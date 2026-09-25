import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("sih26191.exceptions")


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handler for custom application exceptions."""
    logger.error(
        f"Application error: {exc.message} | Path: {request.url.path} | Details: {exc.details}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details,
            },
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handler for standard HTTP exceptions."""
    logger.warning(
        f"HTTP error {exc.status_code}: {exc.detail} | Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": str(exc.detail),
                "type": "HTTPException",
                "details": {},
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic request validation errors."""
    logger.warning(
        f"Validation error on {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "message": "Request validation failed",
                "type": "ValidationError",
                "details": exc.errors(),
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled internal exceptions."""
    logger.exception(
        f"Unhandled server error on {request.url.path}: {str(exc)}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "An internal server error occurred.",
                "type": "InternalServerError",
                "details": {},
            },
        },
    )
