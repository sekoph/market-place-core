from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from shared.utils.auth_utils import keycloak_auth
from .serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    AuthUrlSerializer,
    UserInfoSerializer,
    TokenResponseSerializer,
    UserRegistrationResponseSerializer,
    UserRegistrationSerializer
)
from shared.base.permission import IsAuthenticated, IsAdmin, IsUser
from django.contrib.auth.models import User
from keycloak import KeycloakOpenID,KeycloakAdmin
from dotenv import load_dotenv
import os

import logging

logger = logging.getLogger(__name__)
load_dotenv()


# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#         email = request.data.get("email")

#         if not username or not password or not email:
#             return Response({"error": "username, password, and email are required"}, status=400)

#         try:
#             keycloak_admin = KeycloakAdmin(
#                 server_url=os.getenv("KEYCLOAK_SERVER_URL"),
#                 username=os.getenv("KEYCLOAK_ADMIN_USER"),
#                 password=os.getenv("KEYCLOAK_ADMIN_PASSWORD"),
#                 realm_name=os.getenv("KEYCLOAK_REALM"),
#                 client_id="admin-cli",
#                 verify=True
#             )

#             # Create user
#             user_id = keycloak_admin.create_user({
#                 "email": email,
#                 "username": username,
#                 "enabled": True,
#                 "credentials": [{"value": password, "type": "password",}],
#             })

#             return Response({"message": "User created", "user_id": user_id}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

class KeyCloakLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, " and", password)

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            keycloak_openid = KeycloakOpenID(
                server_url=os.getenv("KEYCLOAK_SERVER_URL"),
                client_id=os.getenv("KEYCLOAK_CLIENT_ID"),
                realm_name=os.getenv("KEYCLOAK_REALM"),
                client_secret_key=os.getenv("KEYCLOAK_CLIENT_SECRET")
            )

            token = keycloak_openid.token(username, password)
            userinfo = keycloak_openid.userinfo(token['access_token'])

            return Response({
                "access_token": token["access_token"],
                "refresh_token": token["refresh_token"],
                "user": userinfo
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Authentication failed",
                "details": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class AuthUrlView(APIView):
    """
    Get Keycloak authorization URL for OAuth2 flow
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AuthUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        redirect_uri = serializer.validated_data.get('redirect_uri')
        state = serializer.validated_data.get('state')
        
        try:
            auth_url = keycloak_auth.get_authorization_url(redirect_uri, state)
            return Response({
                'auth_url': auth_url
            })
        except Exception as e:
            logger.error(f"Auth URL generation error: {str(e)}")
            return Response(
                {'error': 'Failed to generate authorization URL'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    """
    Handle OAuth2 authorization code exchange for tokens
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data.get('code')
        redirect_uri = serializer.validated_data.get('redirect_uri')
        
        try:
            # Exchange authorization code for tokens
            token = keycloak_auth.exchange_code_for_token(code, redirect_uri)
            
            # Get user info
            user_info = keycloak_auth.get_user_info(token['access_token'])
            
            response_data = {
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
                'expires_in': token['expires_in'],
                'token_type': token.get('token_type', 'Bearer'),
                'user_info': user_info
            }
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserInfoView(APIView):
    """
    Get current user information
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # User info is available from the authentication process
            if hasattr(request.user, 'keycloak_user_info'):
                user_info = request.user.keycloak_user_info
            else:
                # Fallback: get user info from token
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                token = auth_header.split(' ')[1]
                user_info = keycloak_auth.get_user_info(token)
            
            if not user_info:
                return Response(
                    {'error': 'Could not retrieve user information'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(user_info)
            
        except Exception as e:
            logger.error(f"User info error: {str(e)}")
            return Response(
                {'error': 'Failed to get user information'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LogoutView(APIView):
    """
    Logout user from Keycloak
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                success = keycloak_auth.logout_user(refresh_token)
                if success:
                    return Response({'message': 'Successfully logged out'})
                else:
                    return Response(
                        {'error': 'Logout failed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {'error': 'refresh_token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {'error': 'Logout failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RefreshTokenView(APIView):
    """
    Refresh access token using refresh token
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data.get('refresh_token')
        
        try:
            token = keycloak_auth.refresh_token(refresh_token)
            response_data = {
                'access_token': token['access_token'],
                'refresh_token': token['refresh_token'],
                'expires_in': token['expires_in'],
                'token_type': token.get('token_type', 'Bearer')
            }
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

# Example protected views
class AdminOnlyView(APIView):
    """
    Example view that requires admin role
    """
    permission_classes = [IsAdmin]
    
    def get(self, request):
        return Response({'message': 'Hello Admin! This is admin-only content.'})

class UserView(APIView):
    """
    Example view that requires user role
    """
    permission_classes = [IsUser]
    
    def get(self, request):
        return Response({'message': 'Hello User! This is user content.'})

class PublicView(APIView):
    """
    Example public view
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'message': 'This is public content, no authentication required.'})

class AuthenticatedView(APIView):
    """
    Example view that requires any authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'message': f'Hello {request.user.username}! You are authenticated.',
            'user_id': request.user.id,
            'email': request.user.email
        })
        
        
class UserRegistrationView(APIView):
    """
    Register a new user in Keycloak and Django
    """
    permission_classes = [AllowAny]  # Allow anyone to register
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Check if user already exists in Keycloak
            existing_user_by_username = keycloak_auth.get_user_by_username(
                serializer.validated_data['username']
            )
            if existing_user_by_username:
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            existing_user_by_email = keycloak_auth.get_user_by_email(
                serializer.validated_data['email']
            )
            if existing_user_by_email:
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare user data for Keycloak
            user_data = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password'],
                'first_name': serializer.validated_data.get('first_name', ''),
                'last_name': serializer.validated_data.get('last_name', ''),
                'enabled': True,
                'email_verified': False,
                'temporary_password': serializer.validated_data.get('temporary_password', False)
            }
            
            # Create user in Keycloak
            created_user = keycloak_auth.create_user(user_data)
            
            # Assign default role if specified
            # default_role = serializer.validated_data.get('assign_default_role')
            default_role = 'user'
            if default_role:
                try:
                    keycloak_auth.assign_role_to_user(created_user['user_id'], default_role)
                except Exception as role_error:
                    logger.warning(f"Failed to assign default role '{default_role}': {str(role_error)}")
            
            # Send verification email if requested
            if serializer.validated_data.get('send_verification_email', True):
                try:
                    keycloak_auth.send_verify_email(created_user['user_id'])
                except Exception as email_error:
                    logger.warning(f"Failed to send verification email: {str(email_error)}")
            
            # Create corresponding Django user
            django_user, django_created = User.objects.get_or_create(
                username=created_user['username'],
                defaults={
                    'email': created_user['email'],
                    'first_name': created_user['first_name'],
                    'last_name': created_user['last_name'],
                }
            )
            
            # Prepare response
            response_data = {
                'user_id': created_user['user_id'],
                'username': created_user['username'],
                'email': created_user['email'],
                'first_name': created_user['first_name'],
                'last_name': created_user['last_name'],
                'enabled': created_user['enabled'],
                'email_verified': created_user['email_verified'],
                'created_timestamp': created_user.get('created_timestamp'),
                'message': 'User registered successfully'
            }
            
            if serializer.validated_data.get('send_verification_email', True):
                response_data['message'] += '. Verification email sent.'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"User registration error: {str(e)}")
            return Response(
                {'error': f'Registration failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )