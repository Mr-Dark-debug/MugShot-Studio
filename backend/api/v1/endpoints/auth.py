from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from db.supabase import get_supabase
from core.auth import get_password_hash, verify_password, create_access_token
from core.redis import get_redis
from core.ratelimit import RateLimiter
from datetime import date
import secrets
import random
from typing import Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.capitalize() for x in components[1:])

class UserSignup(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr
    password: str
    confirm_password: str
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9._-]+$")
    full_name: str
    dob: date
    newsletter_opt_in: bool = False

class UserSignin(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr
    password: str

class AuthStart(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr

class ForgotPassword(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr

class ResetPassword(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    token: str
    new_password: str
    confirm_password: str

class ResendConfirmation(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr

class VerifyOTP(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    email: EmailStr
    code: str

@router.post("/start")
async def auth_start(payload: AuthStart):
    supabase = get_supabase()
    response = supabase.table("users").select("id, password_hash").eq("email", payload.email).execute()
    if response.data:
        user = response.data[0]
        if user.get("password_hash"):
            return {"exists": True, "next": "password"}
        else:
            return {"exists": True, "next": "social_login"}
    return {"exists": False, "next": "create_account"}

@router.post("/signup", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def signup(payload: UserSignup, background_tasks: BackgroundTasks, redis: Any = Depends(get_redis)):
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    supabase = get_supabase()
    # Check username uniqueness
    user_check = supabase.table("users").select("id").eq("username", payload.username).execute()
    if user_check.data:
        raise HTTPException(status_code=409, detail="Username already taken")

    # Create user
    hashed_password = get_password_hash(payload.password)
    user_data = {
        "email": payload.email,
        "password_hash": hashed_password,
        "username": payload.username,
        "full_name": payload.full_name,
        "dob": payload.dob.isoformat(),
        "email_confirmed": False,  # Require email confirmation
        "credits": 100,  # Give new users 100 credits to start with
        "newsletter_opt_in": payload.newsletter_opt_in
    }
    
    try:
        response = supabase.table("users").insert(user_data).execute()
        new_user = response.data[0]
        
        # Generate 6-digit OTP code
        otp_code = str(random.randint(100000, 999999))
        
        # Store OTP in Redis with 10-minute expiration
        await redis.setex(f"otp_confirm:{payload.email}", 600, otp_code)
        
        # Send OTP email in background
        from utils.email_utils import send_otp_email
        background_tasks.add_task(send_otp_email, payload.email, otp_code)
        
        # Audit Log
        supabase.table("audit").insert({
            "user_id": new_user["id"],
            "action": "user_signup",
            "delta_credits": 0,
            "meta": {"email": payload.email}
        }).execute()
        
        # Return response indicating email confirmation is needed
        return {
            "user_id": new_user["id"], 
            "message": "User created successfully. Please check your email for confirmation code.",
            "next": "confirm_email"
        }
    except Exception as e:
        # Log the actual error for debugging
        print(f"Signup error: {str(e)}")
        # Check if it's a row-level security error
        if "row-level security policy" in str(e).lower():
            raise HTTPException(
                status_code=500, 
                detail="Database permission error. Please contact support."
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signin", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def signin(payload: UserSignin):
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("email", payload.email).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = response.data[0]
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/confirm")
async def confirm_email(token: str, redis: Any = Depends(get_redis)):
    user_id = await redis.get(f"confirm_email:{token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    supabase = get_supabase()
    supabase.table("users").update({"email_confirmed": True}).eq("id", user_id).execute()
    
    await redis.delete(f"confirm_email:{token}")
    return {"message": "Email confirmed successfully"}

@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTP, redis: Any = Depends(get_redis)):
    # Get stored OTP from Redis
    stored_otp = await redis.get(f"otp_confirm:{payload.email}")
    
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP expired or not found")
    
    if stored_otp != payload.code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    # Update user as email confirmed
    supabase = get_supabase()
    response = supabase.table("users").select("id").eq("email", payload.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=400, detail="User not found")
    
    user_id = response.data[0]["id"]
    supabase.table("users").update({"email_confirmed": True}).eq("id", user_id).execute()
    
    # Remove OTP from Redis
    await redis.delete(f"otp_confirm:{payload.email}")
    
    # Create access token for immediate login
    access_token = create_access_token(data={"sub": user_id})
    
    # Get user data for response
    user_response = supabase.table("users").select("*").eq("id", user_id).execute()
    user = user_response.data[0]
    
    return {
        "user_id": user_id, 
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user,
        "message": "Email verified successfully"
    }

@router.post("/resend-confirmation", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def resend_confirmation(payload: ResendConfirmation, background_tasks: BackgroundTasks, redis: Any = Depends(get_redis)):
    supabase = get_supabase()
    response = supabase.table("users").select("id, email_confirmed").eq("email", payload.email).execute()
    
    if not response.data:
        # Return 200 to avoid user enumeration
        return {"message": "If account exists, confirmation email sent"}
        
    user = response.data[0]
    if user["email_confirmed"]:
        return {"message": "Email already confirmed"}
        
    # Generate 6-digit OTP code
    otp_code = str(random.randint(100000, 999999))
    
    # Store OTP in Redis with 10-minute expiration
    await redis.setex(f"otp_confirm:{payload.email}", 600, otp_code)
    
    # Send OTP email in background
    from utils.email_utils import send_otp_email
    background_tasks.add_task(send_otp_email, payload.email, otp_code)
    
    print(f"DEBUG: Resent OTP code: {otp_code}")
    return {"message": "If account exists, confirmation email sent"}

@router.post("/forgot-password", dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def forgot_password(payload: ForgotPassword, redis: Any = Depends(get_redis)):
    supabase = get_supabase()
    response = supabase.table("users").select("id").eq("email", payload.email).execute()
    
    if response.data:
        user = response.data[0]
        token = secrets.token_urlsafe(32)
        await redis.setex(f"reset_password:{token}", 600, user["id"])
        print(f"DEBUG: Reset Password Link: /auth/reset-password?token={token}")
    
    return {"message": "If account exists, reset instructions sent"}

@router.post("/reset-password")
async def reset_password(payload: ResetPassword, redis: Any = Depends(get_redis)):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    user_id = await redis.get(f"reset_password:{payload.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    hashed_password = get_password_hash(payload.new_password)
    supabase = get_supabase()
    supabase.table("users").update({"password_hash": hashed_password}).eq("id", user_id).execute()
    
    # Audit Log
    supabase.table("audit").insert({
        "user_id": user_id,
        "action": "password_reset",
        "delta_credits": 0,
        "meta": {}
    }).execute()
    
    await redis.delete(f"reset_password:{payload.token}")
    return {"message": "Password reset successfully"}

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    Check if a username is available.
    
    Args:
        username (str): Username to check
        
    Returns:
        dict: {"available": bool}
    """
    supabase = get_supabase()
    response = supabase.table("users").select("id").eq("username", username).execute()
    
    if response.data:
        # Username taken
        raise HTTPException(status_code=409, detail="Username already taken")
    else:
        # Username available
        return {"available": True}
