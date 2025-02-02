from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_tables, close_db_connection
from app.cache import init_redis_pool, close_redis_connection
from app.routers import auth
from app.middleware.error_handler import error_handler_middleware
from app.middleware.logging import logging_middleware
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Print all environment variables for debugging
print(os.environ)  # This will print all environment variables

# Check if DATABASE_URL is loaded
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")
else:
    print(f"DATABASE_URL: {database_url}")  # Debugging line

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await create_tables()
        await init_redis_pool()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        # Allow the application to start even if database init fails
    yield
    # Shutdown
    try:
        await close_db_connection()
        await close_redis_connection()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.error(f"Application shutdown error: {str(e)}")

app = FastAPI(
    title="Authentication API",
    description="API for user authentication and authorization",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)

# Include routers
app.include_router(auth.router)

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 