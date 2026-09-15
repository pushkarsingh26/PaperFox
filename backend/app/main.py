from contextlib import asynccontextmanager
import logging
import uuid
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import close_mongo_connection, connect_to_mongo, ping_database
from app.core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("paperfox.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PaperFox FastAPI Application...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down PaperFox FastAPI Application...")
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# 1. Security Headers Middleware (outermost response modification)
app.add_middleware(SecurityHeadersMiddleware)

# 2. In-Memory Sliding Window Rate Limiter
app.add_middleware(RateLimitMiddleware)

# 3. Configure CORS
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler for Unhandled Server Errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    logger.error(
        f"Unhandled exception [error_id={error_id}] on {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
        },
    )


# Include API V1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Production health check verifying application and MongoDB connectivity.
    Does not expose sensitive infrastructure details or credentials.
    """
    is_db_connected = await ping_database()
    if is_db_connected:
        return {
            "status": "healthy",
            "database": "connected",
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
        }
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "unhealthy",
            "database": "disconnected",
            "service": settings.PROJECT_NAME,
            "version": "1.0.0",
        },
    )


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs" if settings.ENVIRONMENT == "development" else "protected",
    }
