from fastapi import Request, Response
import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)

async def logging_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Status: {response.status_code} "
        f"Duration: {process_time:.3f}s"
    )
    
    return response 