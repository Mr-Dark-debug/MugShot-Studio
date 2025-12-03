from fastapi import HTTPException, Request, Depends
from app.core.redis import get_redis
from redis.asyncio import Redis
import time

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request, redis: Redis = Depends(get_redis)):
        # Determine key based on user if authenticated, else IP
        user = getattr(request.state, "user", None)
        if user:
            key = f"rate_limit:{user['id']}:{request.url.path}"
        else:
            ip = request.client.host
            key = f"rate_limit:{ip}:{request.url.path}"

        # Use a sliding window or simple counter with expiry
        # Simple counter: key expires after seconds
        # But for sliding window, we need sorted sets or list.
        # Let's use simple fixed window for now: key = prefix + timestamp // seconds
        # Or just increment and expire.
        
        # Using simple increment with expiry on first set
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, self.seconds)
            
        if current > self.times:
            raise HTTPException(status_code=429, detail="Too many requests")
