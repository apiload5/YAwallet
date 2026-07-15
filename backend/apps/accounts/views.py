from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import login, logout
from django.db import transaction
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from firebase_admin import auth as firebase_auth
from apps.accounts.models import User, KYCDocument
from apps.accounts.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserSerializer, KYCDocumentSerializer, KYCSubmissionSerializer,
    SetTransactionPinSerializer, VerifyTransactionPinSerializer
)
from apps.core.permissions import IsNotBlocked
from apps.core.exceptions import KYCRequiredError, UserBlockedError
from apps.core.throttling import AuthRateThrottle
from apps.audit.models import AuditLog
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class RegisterView(generics.CreateAPIView):
    """User registration view"""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserRegistrationSerializer,
        responses={201: UserSerializer()}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log audit
        AuditLog.objects.create(
            user=user,
            action='USER_REGISTERED',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class FirebaseLoginView(generics.GenericAPIView):
    """Firebase authentication login view"""
    
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    @swagger_auto_schema(
        operation_description="Login with Firebase ID token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_token': openapi.Schema(type=openapi.TYPE_STRING),
                'device_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={200: UserSerializer()}
    )
    def post(self, request):
        id_token = request.data.get('id_token')
        device_id = request.data.get('device_id')
        
        if not id_token:
            return Response({
                'success': False,
                'error': {'message': 'ID token is required'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify Firebase token
            decoded_token = firebase_auth.verify_id_token(id_token)
            phone = decoded_token.get('phone_number')
            
            if not phone:
                return Response({
                    'success': False,
                    'error': {'message': 'Phone number not found in token'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'full_name': decoded_token.get('display_name', phone),
                    'email': decoded_token.get('email', ''),
                }
            )
            
            if user.is_blocked:
                raise UserBlockedError(f"Account blocked: {user.block_reason}")
            
            if user.is_locked():
                return Response({
                    'success': False,
                    'error': {'message': 'Account is locked. Try again after 15 minutes.'}
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Device management
            if not user.can_add_device(device_id) and device_id not in user.devices:
                return Response({
                    'success': False,
                    'error': {'message': 'Device limit exceeded'}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if device_id not in user.devices:
                user.add_device(device_id)
            
            # Update last login info
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.last_login_device = request.META.get('HTTP_USER_AGENT')
            user.last_login = timezone.now()
            user.save(update_fields=['last_login_ip', 'last_login_device', 'last_login'])
            
            # Log audit
            AuditLog.objects.create(
                user=user,
                action='USER_LOGIN',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response({
                'success': True,
                'message': 'Login successful' if not created else 'User created and logged in',
                'data': {
                    'user': UserSerializer(user).data,
                    'is_new_user': created,
                    'kyc_status': user.kyc_status,
                    'has_transaction_pin': bool(user.transaction_pin),
                }
            })
            
        except firebase_auth.InvalidIdTokenError:
            return Response({
                'success': False,
                'error': {'message': 'Invalid Firebase token'}
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    def get_object(self):
        return self.request.user

class KYCDocumentView(generics.ListCreateAPIView):
    """KYC document management view"""
    
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    def get_queryset(self):
        return KYCDocument.objects.filter(user=self.request.user)
    
    @swagger_auto_schema(
        operation_description="Submit KYC documents",
        request_body=KYCSubmissionSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = KYCSubmissionSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        with transaction.atomic():
            # Create KYC documents
            documents = []
            doc_types = ['CNIC_FRONT', 'CNIC_BACK', 'SELFIE']
            urls = [
                serializer.validated_data['cnic_front'],
                serializer.validated_data['cnic_back'],
                serializer.validated_data['selfie']
            ]
            
            for doc_type, url in zip(doc_types, urls):
                doc = KYCDocument.objects.create(
                    user=user,
                    document_type=doc_type,
                    file_url=url,
                    file_name=f"{user.phone}_{doc_type}.jpg",
                    status='PENDING'
                )
                documents.append(doc)
            
            # Update user KYC status
            user.kyc_status = 'PENDING'
            user.kyc_submitted_at = timezone.now()
            user.save(update_fields=['kyc_status', 'kyc_submitted_at'])
            
            # Log audit
            AuditLog.objects.create(
                user=user,
                action='KYC_SUBMITTED',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
        
        return Response({
            'success': True,
            'message': 'KYC documents submitted successfully',
            'data': KYCDocumentSerializer(documents, many=True).data
        }, status=status.HTTP_201_CREATED)

class SetTransactionPinView(generics.GenericAPIView):
    """Set transaction PIN view"""
    
    serializer_class = SetTransactionPinSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    @swagger_auto_schema(
        operation_description="Set transaction PIN",
        request_body=SetTransactionPinSerializer
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check if PIN is already set
        if user.transaction_pin:
            return Response({
                'success': False,
                'error': {'message': 'Transaction PIN already set'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new PIN
        user.set_transaction_pin(serializer.validated_data['new_pin'])
        
        # Log audit
        AuditLog.objects.create(
            user=user,
            action='TRANSACTION_PIN_SET',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return Response({
            'success': True,
            'message': 'Transaction PIN set successfully'
        })

class VerifyTransactionPinView(generics.GenericAPIView):
    """Verify transaction PIN view"""
    
    serializer_class = VerifyTransactionPinSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    @swagger_auto_schema(
        operation_description="Verify transaction PIN",
        request_body=VerifyTransactionPinSerializer
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='TRANSACTION_PIN_VERIFIED',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return Response({
            'success': True,
            'message': 'PIN verified successfully'
        })

class LogoutView(generics.GenericAPIView):
    """Logout view"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        
        # Log audit
        AuditLog.objects.create(
            user=request.user,
            action='USER_LOGOUT',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        })
