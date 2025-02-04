from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables, close_db_connection
from app.cache import init_redis_pool, close_redis_connection
from app.routers import auth, web_service
from app.middleware.error_handler import error_handler_middleware
from app.middleware.logging import logging_middleware
from app.middleware.security import rate_limit_middleware
from app.config import get_settings
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.force_https import ForceHTTPSMiddleware
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
IS_DEVELOPMENT = os.getenv("ENVIRONMENT", "development") == "development"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await create_tables()
        await init_redis_pool()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
    yield
    # Shutdown
    try:
        await close_db_connection()
        await close_redis_connection()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Application shutdown error: {str(e)}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Secure API for user authentication and authorization",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if IS_DEVELOPMENT else ["https://bitebase.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)

# Add the Force HTTPS middleware only in production
if not IS_DEVELOPMENT:
    app.add_middleware(ForceHTTPSMiddleware)

# Include routers
app.include_router(
    auth.router,
    prefix="/api/v1"
)
app.include_router(
    web_service.router,
    prefix="/api/v1"
)

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        await db.execute("SELECT 1")
        # Check Redis connection
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": "production",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 