import redis.asyncio as redis
from app.core.config import settings

async def get_redis():
    client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    try:
        yield client
    finally:
        await client.close()
