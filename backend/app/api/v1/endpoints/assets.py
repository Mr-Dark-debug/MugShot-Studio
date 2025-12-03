from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from app.core.auth import get_current_user
from app.db.supabase import get_supabase
from app.core.config import settings
import uuid
import time
import os

router = APIRouter()

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB

@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    type: str = Form(...), # selfie, ref, copy_target, profile_photo
    user: dict = Depends(get_current_user)
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, WEBP allowed.")
    
    # Read file to check size (be careful with large files in memory, but 8MB is manageable)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 8MB limit.")
    
    # Bucket selection
    bucket_name = "user_assets"
    if type == "profile_photo":
        bucket_name = "profile_photos"
    elif type == "render":
        bucket_name = "renders"
    
    # Naming convention: {user_id}/{asset_type}/{uuid}_{timestamp}.{ext}
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{user['id']}/{type}/{uuid.uuid4()}_{int(time.time())}.{ext}"
    
    supabase = get_supabase()
    
    try:
        # Upload to Storage
        supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=contents,
            file_options={"content-type": file.content_type}
        )
        
        # Get Public URL (or signed URL if private)
        # For now, assuming public for profile photos, private for others?
        # Docs: "All public renders are stored with public-read... Private assets remain private"
        # Let's assume user_assets are private.
        
        storage_path = filename # Store the path relative to bucket
        
        # Create Asset Record
        asset_data = {
            "user_id": user["id"],
            "type": type,
            "storage_path": storage_path,
            "width": 0, # TODO: Extract dimensions using Pillow if needed
            "height": 0,
            "md5": "", # TODO: Calculate MD5
        }
        
        response = supabase.table("assets").insert(asset_data).execute()
        new_asset = response.data[0]
        
        # If profile photo, update user record
        if type == "profile_photo":
            supabase.table("users").update({"profile_photo_asset_id": new_asset["id"]}).eq("id", user["id"]).execute()
            
        return new_asset
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
