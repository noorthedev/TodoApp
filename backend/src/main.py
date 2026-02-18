"""FastAPI application entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, tasks
from src.config import settings
from src.database import create_db_and_tables
from src.middleware.error_handler import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from src.models.user import User
from src.models.task import Task

# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="RESTful API for multi-user task management with JWT authentication",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS middleware
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Task Management API is running",
        "version": "1.0.0",
    }


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    pass
