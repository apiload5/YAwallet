from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit

class CustomUserRateThrottle(UserRateThrottle):
    """Custom user rate throttle with specific limits"""
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.id
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}

class AuthRateThrottle(UserRateThrottle):
    """Rate throttle for auth endpoints"""
    scope = 'auth'
    rate = '5/hour'

class TransferRateThrottle(UserRateThrottle):
    """Rate throttle for transfer endpoints"""
    scope = 'transfer'
    rate = '10/10min'

class PaymentRateThrottle(UserRateThrottle):
    """Rate throttle for payment endpoints"""
    scope = 'payment'
    rate = '20/hour'

def rate_limit_exceeded(request, exception):
    """Custom response for rate limit exceeded"""
    from rest_framework.response import Response
    return Response(
        {
            'success': False,
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Rate limit exceeded. Please try again later.',
                'status_code': 429
            }
        },
        status=429
    )
