"""
Error handling utilities for the EvolSynth API
"""

from typing import Dict, Any, Optional
from api.models.responses import ErrorResponse


def create_error_response(
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create a standardized error response"""
    return ErrorResponse(
        error=error,
        message=message,
        details=details
    ) 