import logging
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import ValidationError
from typing import Union

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def database_exception_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "detail": exc.message
        }
    )


async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, ResponseValidationError, ValidationError]):
    """Handle validation errors from request, response, or general Pydantic models"""

    errors = []
    if hasattr(exc, "errors"):
        errors = exc.errors()

    # Log detailed error for debugging
    logger.error(f"Validation error: {errors}")

    error_type = "Request Validation Error"
    if isinstance(exc, ResponseValidationError):
        error_type = "Response Validation Error"

    # Simplify the error messages for the client
    simplified_errors = []
    for error in errors:
        location = ".".join(str(loc) for loc in error.get("loc", []))
        simplified_errors.append({
            "field": location,
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "unknown")
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": error_type,
            "detail": simplified_errors
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions"""
    logger.exception(f"Unhandled exception occurred: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if str(exc) else "An unexpected error occurred"
        }
    )


def register_exception_handlers(app):
    """Register all exception handlers to the FastAPI app"""
    app.add_exception_handler(DatabaseError, database_exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)
    app.add_exception_handler(ResponseValidationError,
                              validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
