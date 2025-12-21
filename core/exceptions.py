"""
Custom exceptions and exception handler for the API.
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from core.utils import StandardResponse


class InvalidCredentialsError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid credentials'
    default_code = 'INVALID_CREDENTIALS'


class InvalidTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired token'
    default_code = 'INVALID_TOKEN'


class InvalidOTPError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid or expired OTP code'
    default_code = 'INVALID_OTP'


class PermissionDeniedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied'
    default_code = 'PERMISSION_DENIED'


class ResourceNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'RESOURCE_NOT_FOUND'


class DuplicateEntryError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource already exists'
    default_code = 'DUPLICATE_ENTRY'


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation failed'
    default_code = 'VALIDATION_ERROR'


class ClassFullError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Class is full'
    default_code = 'CLASS_FULL'


class PrerequisitesNotMetError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Prerequisites not met'
    default_code = 'PREREQUISITES_NOT_MET'


class ScheduleConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Schedule conflict detected'
    default_code = 'SCHEDULE_CONFLICT'


class InvalidOperationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Operation not allowed'
    default_code = 'INVALID_OPERATION'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Get error code
        error_code = getattr(exc, 'default_code', 'ERROR')
        
        # Format error message
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                error_message = str(response.data['detail'])
                errors = None
            else:
                error_message = 'Validation failed'
                errors = response.data
        else:
            error_message = str(response.data)
            errors = None
        
        # Create standardized error response
        response.data = StandardResponse.error(
            message=error_message,
            code=error_code,
            errors=errors
        )
    
    return response