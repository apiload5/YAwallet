from django.utils.deprecation import MiddlewareMixin
from apps.audit.models import AuditLog
import json

class AuditMiddleware(MiddlewareMixin):
    """Middleware to audit user actions"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip for certain views
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
        
        # Log API calls
        if request.user.is_authenticated:
            # Don't log every GET request to avoid excessive logs
            if request.method != 'GET':
                audit_data = {
                    'user': request.user,
                    'action': f'{request.method}_{view_func.__name__}',
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'metadata': {
                        'path': request.path,
                        'method': request.method,
                        'data': getattr(request, 'data', {}),
                        'query_params': request.GET.dict(),
                    }
                }
                AuditLog.objects.create(**audit_data)
        
        return None
