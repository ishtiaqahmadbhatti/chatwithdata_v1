from fastapi import HTTPException
from typing import Any, Dict, Optional


class SmartConvertException(Exception):
    """Base exception for Smart Convert API."""
    pass


class FileProcessingError(SmartConvertException):
    """Raised when file processing fails."""
    pass


class UnsupportedFileTypeError(SmartConvertException):
    """Raised when an unsupported file type is uploaded."""
    pass


class FileSizeExceededError(SmartConvertException):
    """Raised when uploaded file exceeds size limit."""
    pass


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> HTTPException:
    """Create a standardized error response."""
    error_data = {
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }
    return HTTPException(status_code=status_code, detail=error_data)
