"""
File upload and management functionality.
"""
import os
import uuid
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.utils import StandardResponse
from core.exceptions import ValidationError

bearer_security = [{'Bearer': []}]


class FileUploadViewSet(viewsets.GenericViewSet):
    """File upload and management."""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    ALLOWED_EXTENSIONS = {
        'profile_picture': ['.jpg', '.jpeg', '.png', '.gif'],
        'document': ['.pdf', '.doc', '.docx', '.txt'],
        'spreadsheet': ['.xls', '.xlsx', '.csv'],
        'all': ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.csv']
    }
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    
    def validate_file(self, file, file_type='all'):
        """Validate file size and type."""
        # Check file size
        if file.size > self.MAX_FILE_SIZE:
            raise ValidationError(
                f'File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024)}MB'
            )
        
        # Check file extension
        ext = os.path.splitext(file.name)[1].lower()
        allowed_exts = self.ALLOWED_EXTENSIONS.get(file_type, self.ALLOWED_EXTENSIONS['all'])
        
        if ext not in allowed_exts:
            raise ValidationError(
                f'File type {ext} not allowed. Allowed types: {", ".join(allowed_exts)}'
            )
        
        return True
    
    @swagger_auto_schema(
        operation_summary="Upload File",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='File to upload'
            ),
            openapi.Parameter(
                'file_type',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=True,
                description='Type: profile_picture, document, spreadsheet'
            ),
            openapi.Parameter(
                'related_object_type',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description='Related object type'
            ),
            openapi.Parameter(
                'related_object_id',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description='Related object ID'
            ),
        ],
        security=bearer_security
    )
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """Upload a file."""
        file = request.FILES.get('file')
        file_type = request.data.get('file_type', 'all')
        related_object_type = request.data.get('related_object_type')
        related_object_id = request.data.get('related_object_id')
        
        if not file:
            return Response(
                StandardResponse.error(
                    message='No file provided',
                    code='MISSING_FILE'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file
        try:
            self.validate_file(file, file_type)
        except ValidationError as e:
            return Response(
                StandardResponse.error(
                    message=str(e),
                    code='VALIDATION_ERROR'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique filename
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4()}{ext}"
        
        # Determine storage path
        if file_type == 'profile_picture':
            path = f"profile_pictures/{request.user.id}/{filename}"
        elif file_type == 'document':
            path = f"documents/{request.user.id}/{filename}"
        elif file_type == 'spreadsheet':
            path = f"spreadsheets/{request.user.id}/{filename}"
        else:
            path = f"uploads/{request.user.id}/{filename}"
        
        # Save file
        file_path = default_storage.save(path, ContentFile(file.read()))
        file_url = default_storage.url(file_path)
        
        # If profile picture, update user
        if file_type == 'profile_picture' and hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            student.profile_picture = file_url
            student.save()
        
        return Response(
            StandardResponse.success(
                message='File uploaded successfully',
                data={
                    'file_id': str(uuid.uuid4()),  # Could be saved to DB
                    'file_name': file.name,
                    'file_size': file.size,
                    'file_type': file_type,
                    'file_url': file_url,
                    'uploaded_at': None  # Add datetime
                }
            ),
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_summary="Delete File",
        manual_parameters=[
            openapi.Parameter(
                'file_path',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='Path to file to delete'
            ),
        ],
        security=bearer_security
    )
    @action(detail=False, methods=['delete'], url_path='delete')
    def delete_file(self, request):
        """Delete a file."""
        file_path = request.query_params.get('file_path')
        
        if not file_path:
            return Response(
                StandardResponse.error(
                    message='File path is required',
                    code='MISSING_FILE_PATH'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Security check - only allow deletion of user's own files
        if not file_path.startswith(f"profile_pictures/{request.user.id}/") and \
           not file_path.startswith(f"documents/{request.user.id}/") and \
           not file_path.startswith(f"uploads/{request.user.id}/") and \
           request.user.role != 'ADMIN':
            return Response(
                StandardResponse.error(
                    message='Permission denied',
                    code='PERMISSION_DENIED'
                ),
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Delete file
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            
            return Response(
                StandardResponse.success(message='File deleted successfully'),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                StandardResponse.error(
                    message='File not found',
                    code='FILE_NOT_FOUND'
                ),
                status=status.HTTP_404_NOT_FOUND
            )