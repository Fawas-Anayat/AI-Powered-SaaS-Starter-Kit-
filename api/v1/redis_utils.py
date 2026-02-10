from fastapi import Response
import redis.asyncio as redis
from passlib.context import CryptContext
from datetime import datetime , timedelta
from core.security import settings

# redis_client = redis.Redis(
#     host=settings.REDIS_URL,
#     port=6379,
#     db=0,
#     decode_responses=True
# )

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def save_refresh_token_redis(user_id : int , refresh_token : str):
    hashed_token = pwd_context.hash(refresh_token)

    key = f"refresh_token:{user_id}"
    expiry = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    await redis_client.setex(key,expiry,hashed_token)

async def verify_refresh_token_redis(user_id: int, refresh_token: str) -> bool:
    key = f"refresh_token:{user_id}"
    hashed_token = await redis_client.get(key)

    if not hashed_token:
        return False
    
    return pwd_context.verify(refresh_token, hashed_token)

async def delete_refresh_token_redis(user_id: int):
    key = f"refresh_token:{user_id}"
    await redis_client.delete(key)

