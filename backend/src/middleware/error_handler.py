"""Custom exception handlers for standardized error responses."""
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException with standardized error response.
    
    Args:
        request: The incoming request
        exc: The HTTPException raised
        
    Returns:
        JSONResponse with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "http_error",
                "status_code": exc.status_code,
                "message": exc.detail,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle RequestValidationError with detailed field errors.
    
    Args:
        request: The incoming request
        exc: The RequestValidationError raised
        
    Returns:
        JSONResponse with validation error details
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "type": "validation_error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation failed",
                "details": errors,
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with generic error response.
    
    Args:
        request: The incoming request
        exc: The exception raised
        
    Returns:
        JSONResponse with generic error message (no internal details exposed)
    """
    # Log the actual exception for debugging (in production, use proper logging)
    print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "type": "internal_error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )
