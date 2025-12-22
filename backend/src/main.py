"""FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .config import settings
from .db import create_db_and_tables
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .api.chat import router as chat_router
from .api.ai_actions import router as ai_actions_router
from .api.ai_preferences import router as ai_preferences_router  # Phase 7: AI preferences
from .api.ai_quota import router as ai_quota_router  # Phase 8: AI quota
from .api.ai_health import router as ai_health_router  # Phase 8: AI health check

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Full-stack todo application with multi-user authentication",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router)  # Phase 3: AI chat endpoints
app.include_router(ai_actions_router)  # Phase 3: AI action confirmation endpoints
app.include_router(ai_preferences_router)  # Phase 7: AI preferences
app.include_router(ai_quota_router)  # Phase 8: AI quota
app.include_router(ai_health_router)  # Phase 8: AI health check


# Global exception handlers for consistent error responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with consistent format."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with consistent format."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.environment == "development" else "An unexpected error occurred"
        }
    )


@app.on_event("startup")
def on_startup():
    """Initialize database on application startup."""
    create_db_and_tables()


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Todo API is running",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/health")
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.environment,
    }
