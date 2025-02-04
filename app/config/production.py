from pydantic import BaseModel
from typing import List
import os

class ProductionConfig(BaseModel):
    # Server settings
    WORKERS: int = 4
    WORKER_CLASS: str = "uvicorn.workers.UvicornWorker"
    BIND: str = "0.0.0.0:8000"
    
    # Security
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "").split(",")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "INFO" 