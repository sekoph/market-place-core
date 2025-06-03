from django.contrib.auth import get_user_model
from shared.utils.auth_utils import keycloak_auth
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from shared.utils.auth_helper import KeycloakUser
from dotenv import load_dotenv
import logging
import os
import django
from django.conf import settings

load_dotenv()



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')
django.setup()


logger = logging.getLogger(__name__)
User = get_user_model()

class KeycloakAuthentication(BaseAuthentication):
    """
    Custom authentication class for Keycloak JWT tokens
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        # print(f"[token header] token before spliting {auth_header}")
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        try:
            # Fix: Properly split the Authorization header
            token = auth_header.split(' ')[1]
            logger.debug(f"[Auth Debug] Stripped Token: {token}")
            # print(f"[Auth Debug] stripped Token: {token}")
            # Validate token with Keycloak
            token_info = keycloak_auth.validate_token(token)

            if not token_info:
                # print(f"[Keycloak] Token validation failed for token: {token[:30]}...")
                raise AuthenticationFailed('Invalid token')
            
            # Get user info from Keycloak
            user_info = keycloak_auth.get_user_info(token)
            if not user_info:
                raise AuthenticationFailed('Could not get user info')
            
            # Create or update Django user
            print(user_info)
            
            user = self._get_or_create_user(user_info, token_info, token)
            
            
            # Store token info in user object for later use
            # user.keycloak_token = token
            # user.keycloak_user_info = user_info

            return (user, token)
        
        except Exception as e:
            
            # logger.error(f"Authentication error: {str(e)}")
            print(f"[Keycloak] Exception during token validation: {str(e)}")
            raise AuthenticationFailed('Invalid token')

            # return None
    def _get_or_create_user(self,user_info, token_info, token):
        """ get or create user based on service configuration """
        
        if self._is_auth_service():
            return self._handle_django_user(user_info, token_info, token)
        else:
            return self._handle_keycloak_user(user_info, token_info, token)
        
    def _is_auth_service(self):
        """ check if auth service is django or keycloak """
        if os.getenv('SERVICE_NAME') == 'auth-service':
            return True
        else:
            return False
        
    def _handle_django_user(self, user_info, token_info, token):
        """ handle django user """
        user, created = User.objects.get_or_create(
            username=user_info.get('preferred_username', user_info.get('sub')),
            defaults={
                'email': user_info.get('email', ''),
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
            }
        )

        # Update user info if not created
        if not created:
            user.email = user_info.get('email', user.email)
            user.first_name = user_info.get('given_name', user.first_name)
            user.last_name = user_info.get('family_name', user.last_name)
            user.save()

        # Store token info in user object for later use
        user.keycloak_token = token
        user.keycloak_user_info = user_info
        
        return (user)
    
    def _handle_keycloak_user(self, user_info, token_info, token):
        """ handle keycloak user """
        # Get user info from Keycloak
        user = KeycloakUser(user_info)
        
        return (user)
    
        

    def authenticate_header(self, request):
        return 'Bearer'