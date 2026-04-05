from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("firstfintech")


class AppException(Exception):
    """Base application exception."""
    def __init__(self, status_code: int = 400, message: str = "An error occurred"):
        self.status_code = status_code
        self.message = message


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Invalid or expired authentication credentials"):
        super().__init__(status_code=401, message=message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(status_code=422, message=message)


class ExternalServiceException(AppException):
    def __init__(self, message: str = "External service error"):
        super().__init__(status_code=502, message=message)


async def app_exception_handler(request: Request, exc: AppException):
    """Global handler for all AppException subclasses."""
    logger.warning(f"AppException: {exc.status_code} - {exc.message} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    logger.error(f"Unhandled exception: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error. Please try again later."},
    )
