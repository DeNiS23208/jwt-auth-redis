import redis.asyncio as redis
from app.core.config import settings


redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


async def set_value(key: str, value: str, expire_seconds: int | None = None):
    await redis_client.set(key, value, ex=expire_seconds)
    
async def get_value(key: str) -> str | None:
    return await redis_client.get(key)

async def delete_value(key: str) -> None:
    await redis_client.delete(key)
    
    
def access_key(jti: str) -> str:
    return f"whitelist:access:{jti}"

def refresh_key(jti: str) -> str:
    return f"whitelist:refresh:{jti}"

def blacklist_key(jti: str) -> str:
    return f"blacklist:{jti}"
