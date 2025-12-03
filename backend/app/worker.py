import logging
import base64
import httpx
from celery import Celery
from app.core.config import get_settings
from app.db.supabase import get_supabase
from app.services.gemini_service import GeminiService
from app.services.bytedance_service import ByteDanceService
from app.services.fal_service import FalService
from app.utils.credit_calculator import calculate_job_credits, InsufficientCreditsException

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "thumbnail_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.worker.generate_thumbnail_task": "main-queue"
}

@celery_app.task(bind=True)
def generate_thumbnail_task(self, job_id: str):
    """
    Celery task to generate thumbnails.
    Handles all supported models and properly manages credits.
    """
    logger.info(f"Processing Job: {job_id}")
    
    supabase = get_supabase()
    
    # 1. Fetch Job & Project Details
    job_res = supabase.table("jobs").select("*").eq("id", job_id).execute()
    if not job_res.data:
        logger.error(f"Job {job_id} not found")
        return "Job not found"
    job = job_res.data[0]
    
    # Update status to running
    supabase.table("jobs").update({"status": "running"}).eq("id", job_id).execute()
    
    try:
        # Fetch Project & Prompt
        proj_res = supabase.table("projects").select("*").eq("id", job["project_id"]).execute()
        project = proj_res.data[0]
        
        prompt_res = supabase.table("prompts").select("*").eq("project_id", project["id"]).execute()
        prompt_data = prompt_res.data[0]["raw"]
        
        # Check user credits
        user_res = supabase.table("users").select("credits").eq("id", project["user_id"]).execute()
        user_profile = user_res.data[0] if user_res.data else {"credits": 0}
        user_credits = user_profile.get("credits", 0)
        
        # Calculate required credits
        job_info = {
            "quality": job.get("quality", "std"),
            "mode": project.get("mode", "design"),
            "model": job.get("model", "nano_banana")
        }
        required_credits = calculate_job_credits(job_info)
        
        if user_credits < required_credits:
            raise InsufficientCreditsException(f"Need {required_credits} credits but only have {user_credits}")
        
        # Deduct credits
        new_credits = user_credits - required_credits
        supabase.table("users").update({"credits": new_credits}).eq("id", project["user_id"]).execute()
        
        # Log credit deduction
        supabase.table("audit").insert({
            "user_id": project["user_id"],
            "action": "deduct_credits",
            "delta_credits": -required_credits,
            "meta": {"job_id": job_id, "reason": "thumbnail_generation"}
        }).execute()
        
        # Handle References (Download from Supabase Storage -> Bytes)
        ref_images = []
        ref_images_b64 = []  # For models that need base64
        if prompt_data.get("refs"):
            for asset_id in prompt_data["refs"]:
                # Fetch asset path
                asset_res = supabase.table("assets").select("*").eq("id", asset_id).execute()
                if asset_res.data:
                    path = asset_res.data[0]["path"]
                    # Download
                    file_bytes = supabase.storage.from_("assets").download(path)
                    ref_images.append(file_bytes)
                    ref_images_b64.append(base64.b64encode(file_bytes).decode('utf-8'))
        
        # 3. Generate based on model
        images = []
        model = job.get("model", "nano_banana")
        
        logger.info(f"Using model: {model} for job {job_id}")
        
        if "gemini" in model or "nano" in model:
            gemini = GeminiService()
            model_type = "pro" if "pro" in model or "nano_banana_pro" == model else "flash"
            
            if ref_images:
                images = gemini.generate_with_references(
                    prompt=str(prompt_data),
                    reference_images=ref_images,
                    model_type=model_type
                )
            else:
                # Construct proper prompt
                final_prompt = f"""
                Create a {project['platform']} thumbnail.
                Title: {prompt_data.get('headline', '')}
                Subtext: {prompt_data.get('subtext', '')}
                Vibe: {prompt_data.get('vibe', '')}
                """
                
                images = gemini.generate_image(
                    prompt=final_prompt,
                    model_type=model_type
                )
                
        elif "seedream" in model or "bytedance" in model:
            bytedance = ByteDanceService()
            # Construct proper prompt
            final_prompt = f"""
            Create a {project['platform']} thumbnail.
            Title: {prompt_data.get('headline', '')}
            Subtext: {prompt_data.get('subtext', '')}
            Vibe: {prompt_data.get('vibe', '')}
            """
            
            # Run async code in sync context
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            images = loop.run_until_complete(
                bytedance.generate_image(
                    prompt=final_prompt,
                    model="seedream-4.0",
                    width=project.get("width", 1024),
                    height=project.get("height", 1024),
                    reference_images=ref_images_b64 if ref_images_b64 else None
                )
            )
            
        elif "fal" in model:
            fal = FalService()
            # Construct proper prompt
            final_prompt = f"""
            Create a {project['platform']} thumbnail.
            Title: {prompt_data.get('headline', '')}
            Subtext: {prompt_data.get('subtext', '')}
            Vibe: {prompt_data.get('vibe', '')}
            """
            
            # Determine aspect ratio
            width = project.get("width", 16)
            height = project.get("height", 9)
            aspect_ratio = f"{width}:{height}"
            
            images = fal.generate_image(
                prompt=final_prompt,
                model="fal-ai/flux/dev",
                aspect_ratio=aspect_ratio
            )
        
        if not images:
            raise Exception("No images generated")
        
        # 4. Save Results
        for i, img_data in enumerate(images):
            # Handle both base64 strings and URLs
            if isinstance(img_data, str) and img_data.startswith('http'):
                # Download URL
                with httpx.Client() as client:
                    resp = client.get(img_data)
                    img_bytes = resp.content
            else:
                # Assume base64 string
                if isinstance(img_data, str):
                    img_bytes = base64.b64decode(img_data)
                else:
                    img_bytes = img_data
            
            # Upload Render
            file_name = f"renders/{job_id}_{i}.png"
            supabase.storage.from_("renders").upload(
                path=file_name,
                file=img_bytes,
                file_options={"content-type": "image/png"}
            )
            
            # Save to DB
            supabase.table("renders").insert({
                "job_id": job_id,
                "variant": i,
                "thumbnail_path": file_name
            }).execute()
        
        # Update Job Status
        supabase.table("jobs").update({
            "status": "succeeded", 
            "finished_at": "now()",
            "cost_credits": required_credits
        }).eq("id", job_id).execute()
        
        logger.info(f"Job {job_id} completed successfully")
        return "Success"
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        # Update Job Status
        supabase.table("jobs").update({
            "status": "failed",
            "finished_at": "now()"
        }).eq("id", job_id).execute()
        
        # Refund credits on failure
        if 'required_credits' in locals() and 'project' in locals():
            try:
                user_res = supabase.table("users").select("credits").eq("id", project["user_id"]).execute()
                current_credits = user_res.data[0].get("credits", 0) if user_res.data else 0
                refunded_credits = current_credits + required_credits
                
                supabase.table("users").update({"credits": refunded_credits}).eq("id", project["user_id"]).execute()
                
                # Log credit refund
                supabase.table("audit").insert({
                    "user_id": project["user_id"],
                    "action": "refund_credits",
                    "delta_credits": required_credits,
                    "meta": {"job_id": job_id, "reason": "generation_failed"}
                }).execute()
            except Exception as refund_error:
                logger.error(f"Failed to refund credits for job {job_id}: {str(refund_error)}")
        
        return f"Failed: {str(e)}"