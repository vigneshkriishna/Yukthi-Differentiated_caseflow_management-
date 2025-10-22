"""
Global Exception Handler for FastAPI Application
Provides consistent error responses and proper error handling
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging
from typing import Union, Dict, Any
import traceback


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom API error class"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class BusinessLogicError(APIError):
    """Business logic validation error"""
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(message, status_code=400, error_code=error_code)


class ResourceNotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, resource: str, identifier: Union[str, int] = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class DuplicateResourceError(APIError):
    """Duplicate resource error"""
    def __init__(self, resource: str, field: str = None, value: str = None):
        message = f"{resource} already exists"
        if field and value:
            message += f" with {field}: {value}"
        super().__init__(message, status_code=409, error_code="DUPLICATE_RESOURCE")


class InsufficientPermissionsError(APIError):
    """Insufficient permissions error"""
    def __init__(self, action: str = None, resource: str = None):
        message = "Insufficient permissions"
        if action and resource:
            message += f" to {action} {resource}"
        super().__init__(message, status_code=403, error_code="INSUFFICIENT_PERMISSIONS")


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Any = None,
    path: str = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    error_response = {
        "error": True,
        "status_code": status_code,
        "message": message,
        "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow().isoformat() + "Z"
    }
    
    if error_code:
        error_response["error_code"] = error_code
    
    if details:
        error_response["details"] = details
    
    if path:
        error_response["path"] = path
    
    return error_response


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers for FastAPI app"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle custom API errors"""
        logger.warning(f"API Error: {exc.message} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation Error: {exc.errors()} - Path: {request.url.path}")
        
        # Format validation errors consistently
        validation_details = []
        for error in exc.errors():
            validation_details.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
        
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                status_code=422,
                message="Validation failed",
                error_code="VALIDATION_ERROR",
                details=validation_details,
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
        
        # Map status codes to user-friendly messages
        message_map = {
            401: "Authentication required",
            403: "Access forbidden - insufficient permissions",
            404: "Resource not found",
            405: "Method not allowed",
            429: "Too many requests - please try again later",
            500: "Internal server error",
            502: "Bad gateway",
            503: "Service unavailable"
        }
        
        message = message_map.get(exc.status_code, exc.detail)
        error_code = f"HTTP_{exc.status_code}"
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                status_code=exc.status_code,
                message=message,
                error_code=error_code,
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity constraint violations"""
        logger.error(f"Database Integrity Error: {str(exc)} - Path: {request.url.path}")
        
        # Parse common integrity errors
        error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        if "UNIQUE constraint failed" in error_message:
            message = "Resource already exists with this identifier"
            error_code = "DUPLICATE_RESOURCE"
            status_code = 409
        elif "FOREIGN KEY constraint failed" in error_message:
            message = "Referenced resource does not exist"
            error_code = "INVALID_REFERENCE"
            status_code = 400
        elif "NOT NULL constraint failed" in error_message:
            message = "Required field is missing"
            error_code = "MISSING_REQUIRED_FIELD"
            status_code = 400
        else:
            message = "Database constraint violation"
            error_code = "DATABASE_CONSTRAINT_ERROR"
            status_code = 400
        
        return JSONResponse(
            status_code=status_code,
            content=create_error_response(
                status_code=status_code,
                message=message,
                error_code=error_code,
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle general SQLAlchemy database errors"""
        logger.error(f"Database Error: {str(exc)} - Path: {request.url.path}")
        
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                status_code=500,
                message="Database operation failed",
                error_code="DATABASE_ERROR",
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        """Handle Pydantic model validation errors"""
        logger.warning(f"Pydantic Validation Error: {exc.errors()} - Path: {request.url.path}")
        
        validation_details = []
        for error in exc.errors():
            validation_details.append({
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=422,
            content=create_error_response(
                status_code=422,
                message="Model validation failed",
                error_code="MODEL_VALIDATION_ERROR",
                details=validation_details,
                path=str(request.url.path)
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected Error: {str(exc)} - Path: {request.url.path}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Don't expose internal error details in production
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                status_code=500,
                message="An unexpected error occurred",
                error_code="INTERNAL_SERVER_ERROR",
                path=str(request.url.path)
            )
        )


# Utility functions for raising common errors
def raise_not_found(resource: str, identifier: Union[str, int] = None):
    """Raise a standardized not found error"""
    raise ResourceNotFoundError(resource, identifier)


def raise_duplicate(resource: str, field: str = None, value: str = None):
    """Raise a standardized duplicate resource error"""
    raise DuplicateResourceError(resource, field, value)


def raise_business_error(message: str, error_code: str = None):
    """Raise a standardized business logic error"""
    raise BusinessLogicError(message, error_code)


def raise_insufficient_permissions(action: str = None, resource: str = None):
    """Raise a standardized insufficient permissions error"""
    raise InsufficientPermissionsError(action, resource)


# Input validation helpers
def validate_date_range(start_date, end_date):
    """Validate date range inputs"""
    if start_date > end_date:
        raise_business_error("Start date must be before end date")


def validate_positive_integer(value: int, field_name: str):
    """Validate positive integer inputs"""
    if value <= 0:
        raise_business_error(f"{field_name} must be a positive integer")


def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 255):
    """Validate string length"""
    if len(value) < min_length:
        raise_business_error(f"{field_name} must be at least {min_length} characters long")
    if len(value) > max_length:
        raise_business_error(f"{field_name} must be no more than {max_length} characters long")


def validate_enum_value(value: str, enum_class, field_name: str):
    """Validate enum value"""
    valid_values = [e.value for e in enum_class]
    if value not in valid_values:
        raise_business_error(f"{field_name} must be one of: {', '.join(valid_values)}")


# Security validation helpers
def sanitize_string_input(value: str) -> str:
    """Basic string sanitization"""
    if not value:
        return value
    
    # Remove potential XSS characters
    dangerous_chars = ['<', '>', '"', "'", '&']
    for char in dangerous_chars:
        value = value.replace(char, '')
    
    # Limit length to prevent DoS
    if len(value) > 10000:
        value = value[:10000]
    
    return value.strip()


def validate_file_upload(file_size: int, allowed_extensions: list, file_extension: str):
    """Validate file upload parameters"""
    max_size = 10 * 1024 * 1024  # 10MB
    
    if file_size > max_size:
        raise_business_error(f"File size too large. Maximum allowed: {max_size} bytes")
    
    if file_extension.lower() not in allowed_extensions:
        raise_business_error(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")


# Rate limiting helpers (for future implementation)
def check_rate_limit(user_id: str, endpoint: str, limit: int = 100, window: int = 3600):
    """Check rate limiting (placeholder for future implementation)"""
    # This would integrate with Redis or similar for rate limiting
    # For now, just a placeholder
    pass


# Request logging middleware
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring"""
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = 0.1  # Would calculate actual time
    logger.info(f"Response: {response.status_code} - Time: {process_time:.4f}s")
    
    return response
