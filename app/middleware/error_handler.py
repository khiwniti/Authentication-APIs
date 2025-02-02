from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging
from typing import Callable

logger = logging.getLogger(__name__)

async def error_handler_middleware(
    request: Request,
    call_next: Callable
) -> Response:
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        ) 