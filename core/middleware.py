"""
Custom middleware for audit logging and request processing.
"""
from django.utils.deprecation import MiddlewareMixin
from core.models import AuditLog
from core.utils import get_client_ip, get_user_agent


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log important actions for audit trail.
    """
    
    # Actions to log
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    EXCLUDED_PATHS = ['/admin/', '/static/', '/media/']
    
    def process_response(self, request, response):
        """Log successful state-changing requests."""
        
        # Skip if not authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Skip if GET request or excluded path
        if request.method not in self.LOGGED_METHODS:
            return response
        
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return response
        
        # Skip if not successful
        if response.status_code not in [200, 201, 204]:
            return response
        
        # Determine action
        action_map = {
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE'
        }
        action = action_map.get(request.method, 'ACCESS')
        
        # Extract model name from path
        path_parts = request.path.strip('/').split('/')
        model_name = path_parts[2] if len(path_parts) > 2 else 'unknown'
        
        # Create audit log
        try:
            AuditLog.objects.create(
                user=request.user,
                action=action,
                model_name=model_name,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Audit logging failed: {str(e)}")
        
        return response