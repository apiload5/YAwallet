"""
Authentication classes for YaWallet
"""

from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from django.conf import settings
import firebase_admin
from firebase_admin import auth as firebase_auth
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Firebase Authentication class for DRF
    Authenticates users using Firebase ID tokens
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Firebase ID token
        """
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        # Check if it's a Bearer token
        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        # Verify Firebase token
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token.get('uid')
            phone = decoded_token.get('phone_number')
            
            if not phone:
                raise exceptions.AuthenticationFailed('Phone number not found in token')
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'full_name': decoded_token.get('name', phone),
                    'email': decoded_token.get('email', ''),
                }
            )
            
            # Check if user is blocked
            if user.is_blocked:
                raise exceptions.AuthenticationFailed('User is blocked')
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return (user, decoded_token)
            
        except firebase_auth.InvalidIdTokenError:
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except firebase_auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token expired')
        except firebase_auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed('Firebase token revoked')
        except Exception as e:
            logger.error(f"Firebase authentication error: {str(e)}")
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def authenticate_header(self, request):
        """
        Return the authentication header for 401 responses
        """
        return 'Bearer'


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT Authentication class for DRF
    Uses simple JWT for authentication
    """
    
    def authenticate(self, request):
        """
        Authenticate using JWT token
        """
        from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuth
        
        # Use simple JWT authentication
        auth = SimpleJWTAuth()
        return auth.authenticate(request)
    
    def authenticate_header(self, request):
        """
        Return the authentication header for 401 responses
        """
        return 'Bearer'


class SessionAuthentication(authentication.SessionAuthentication):
    """
    Session authentication with CSRF check disabled for API
    """
    
    def enforce_csrf(self, request):
        """
        Disable CSRF check for API calls
        """
        return
