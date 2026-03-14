"""FastAPI application entry point."""
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.api import auth, tasks, chat
from src.config import settings
from src.database import create_db_and_tables
from src.middleware.error_handler import (
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
# Import all models to register them with SQLModel metadata
from src.models import User, Task, Conversation, Message

# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="RESTful API for multi-user task management with JWT authentication",
    version="1.0.0",
    debug=settings.DEBUG,
)

# Configure CORS middleware
# Parse allowed origins from settings (comma-separated list)
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
origins = [
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use configured origins, not wildcard
    allow_credentials=True,  # False for localStorage JWT (no cookies)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including Authorization
)

# Register exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router)


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
