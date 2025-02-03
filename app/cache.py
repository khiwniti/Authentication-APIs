from redis.asyncio import Redis
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

redis_client: Optional[Redis] = None

async def init_redis_pool() -> Redis:
    global redis_client
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is not set")
            
        redis_client = Redis.from_url(
            redis_url,
            decode_responses=True
        )
        # Test the connection
        await redis_client.ping()
        logger.info("Successfully connected to Redis")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise

async def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client

async def close_redis_connection():
    if redis_client:
        await redis_client.aclose()  # Use aclose() for async closing
        logger.info("Redis connection closed") 