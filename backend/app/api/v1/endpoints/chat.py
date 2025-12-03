from fastapi import APIRouter, HTTPException, Depends
from app.core.auth import get_current_user
from app.db.supabase import get_supabase
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter()

class ChatCreate(BaseModel):
    session_name: Optional[str] = None

class MessageCreate(BaseModel):
    content: str
    sender: str = "user" # user, system, ai

@router.post("/new")
async def create_chat(payload: ChatCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    
    chat_id = str(uuid.uuid4())
    chat_data = {
        "id": chat_id,
        "user_id": user["id"],
        "session_name": payload.session_name or "New Chat"
    }
    
    try:
        supabase.table("chats").insert(chat_data).execute()
        return {
            "chat_id": chat_id,
            "url": f"https://localhost/c/{chat_id}" # In prod, use env var for base URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{chat_id}")
async def get_chat(chat_id: str, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    
    res = supabase.table("chats").select("*").eq("id", chat_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat = res.data[0]
    if chat["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
        
    return chat

@router.get("/{chat_id}/messages")
async def get_messages(chat_id: str, user: dict = Depends(get_current_user)):
    # Verify access first
    await get_chat(chat_id, user)
    
    supabase = get_supabase()
    res = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
    return res.data

@router.post("/{chat_id}/messages")
async def send_message(chat_id: str, payload: MessageCreate, user: dict = Depends(get_current_user)):
    # Verify access
    await get_chat(chat_id, user)
    
    supabase = get_supabase()
    msg_data = {
        "chat_id": chat_id,
        "sender": payload.sender,
        "content": payload.content
    }
    
    try:
        res = supabase.table("messages").insert(msg_data).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
