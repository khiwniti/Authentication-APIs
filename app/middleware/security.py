from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Callable
import time
from ..cache import get_redis

async def rate_limit_middleware(
    request: Request,
    call_next: Callable
) -> JSONResponse:
    redis = await get_redis()
    client_ip = request.client.host
    endpoint = request.url.path
    
    # Create a rate limit key for this IP and endpoint
    rate_key = f"rate_limit:{client_ip}:{endpoint}"
    
    # Check if rate limit is exceeded
    requests = await redis.incr(rate_key)
    if requests == 1:
        await redis.expire(rate_key, 60)  # Reset after 60 seconds
        
    if requests > 100:  # 100 requests per minute
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
        
    response = await call_next(request)
    return response 