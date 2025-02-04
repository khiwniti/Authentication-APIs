from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os

class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip HTTPS redirect in test environment
        if os.getenv("TESTING") == "true":
            return await call_next(request)
            
        if request.url.scheme != "https":
            url = request.url.replace(scheme="https", netloc=request.url.netloc)
            return Response(status_code=301, headers={"Location": str(url)})
        return await call_next(request) 