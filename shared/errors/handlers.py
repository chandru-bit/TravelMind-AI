from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from shared.logging.structured import request_id_ctx

def create_error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: any = None
) -> JSONResponse:
    """Generates standard JSON error response across all API endpoints."""
    req_id = request_id_ctx.get()
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": req_id
            }
        }
    )

class APIException(Exception):
    """Custom API Exception for controlled service-level error raising."""
    def __init__(self, code: str, message: str, status_code: int = 400, details: any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

async def api_exception_handler(request: Request, exc: APIException):
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }
    code = code_map.get(exc.status_code, "ERROR")
    message = exc.detail if isinstance(exc.detail, str) else "An unexpected error occurred."
    return create_error_response(code=code, message=message, status_code=exc.status_code)

from pydantic import ValidationError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Please check the information you entered.",
        status_code=422,
        details=exc.errors()
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Please check the information you entered.",
        status_code=422,
        details=exc.errors()
    )

async def generic_exception_handler(request: Request, exc: Exception):
    return create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="TravelMind AI encountered a server error. Please try again.",
        status_code=500
    )
