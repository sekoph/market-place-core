from keycloak import KeycloakOpenID, KeycloakAdmin
from django.conf import settings
from dotenv import load_dotenv
import logging
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auth_service.settings')


load_dotenv()


logger = logging.getLogger(__name__)

class KeycloakAuth:
    def __init__(self):
        
        self.keycloak_openid = KeycloakOpenID(
            server_url=os.getenv('KEYCLOAK_SERVER_URL', 'http://keycloak:8080'),
            client_id=os.getenv('KEYCLOAK_CLIENT_ID','django-app'),
            realm_name=os.getenv('KEYCLOAK_REALM', 'master'),
            client_secret_key=os.getenv('KEYCLOAK_CLIENT_SECRET')
        )
        
        self.keycloak_admin = KeycloakAdmin(
            server_url=os.getenv('KEYCLOAK_SERVER_URL','http://keycloak:8080'),
            username=os.getenv('KEYCLOAK_ADMIN_USERNAME','admin'),
            password=os.getenv('KEYCLOAK_ADMIN_PASSWORD','admin'),
            realm_name=os.getenv('KEYCLOAK_REALM','django-app'),
            verify=True
        )
    
    def validate_token(self, token):
        """Validate JWT token with Keycloak"""
        try:
            token_info = self.keycloak_openid.introspect(token)
            print(token_info)
            if token_info.get('active'):
                return token_info
            return None
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def get_user_info(self, token):
        """Get user information from Keycloak"""
        try:
            user_info = self.keycloak_openid.userinfo(token)
            return user_info
        except Exception as e:
            logger.error(f"Get user info error: {str(e)}")
            return None
    
    def has_role(self, token, role_name):
        """Check if user has specific role"""
        try:
            token_info = self.validate_token(token)
            if not token_info:
                return False
            
            # Check realm roles
            realm_roles = token_info.get('realm_access', {}).get('roles', [])
            if role_name in realm_roles:
                return True
            
            # Check client roles
            client_roles = token_info.get('resource_access', {})
            for client, access in client_roles.items():
                if role_name in access.get('roles', []):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Role check error: {str(e)}")
            return False
    
    def get_authorization_url(self, redirect_uri, state=None):
        """Get Keycloak authorization URL for OAuth2 flow"""
        return self.keycloak_openid.auth_url(
            redirect_uri=redirect_uri,
            scope="openid email profile",
            state=state
        )
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token"""
        try:
            token = self.keycloak_openid.token(
                grant_type='authorization_code',
                code=code,
                redirect_uri=redirect_uri
            )
            return token
        except Exception as e:
            logger.error(f"Token exchange error: {str(e)}")
            raise e
    
    def refresh_token(self, refresh_token):
        """Refresh access token"""
        try:
            token = self.keycloak_openid.refresh_token(refresh_token)
            return token
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise e
    
    def logout_user(self, refresh_token):
        """Logout user from Keycloak"""
        try:
            self.keycloak_openid.logout(refresh_token)
            return True
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return False
        
    def create_user(self, user_data):
        """
        Create a new user in Keycloak
        
        Args:
            user_data (dict): User information containing:
                - username (required)
                - email (required)
                - password (required)
                - first_name (optional)
                - last_name (optional)
                - enabled (optional, default True)
                - email_verified (optional, default False)
                - temporary_password (optional, default True)
        
        Returns:
            dict: Created user information with user_id
        """
        try:
            # Prepare user payload for Keycloak
            keycloak_user = {
                "username": user_data['username'],
                "email": user_data['email'],
                "enabled": user_data.get('enabled', True),
                "emailVerified": user_data.get('email_verified', False),
                "firstName": user_data.get('first_name', ''),
                "lastName": user_data.get('last_name', ''),
                "credentials": [{
                    "type": "password",
                    "value": user_data['password'],
                    "temporary": user_data.get('temporary_password', False)
                }]
            }
            
            # Create user in Keycloak
            user_id = self.keycloak_admin.create_user(keycloak_user)
            logger.info(f"User created successfully with ID: {user_id}")
            
            # Get the created user details
            created_user = self.keycloak_admin.get_user(user_id)
            
            return {
                'user_id': user_id,
                'username': created_user['username'],
                'email': created_user['email'],
                'first_name': created_user.get('firstName', ''),
                'last_name': created_user.get('lastName', ''),
                'enabled': created_user['enabled'],
                'email_verified': created_user['emailVerified'],
                'created_timestamp': created_user.get('createdTimestamp')
            }
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")
    
    def assign_role_to_user(self, user_id, role_name):
        """
        Assign a realm role to a user
        
        Args:
            user_id (str): Keycloak user ID
            role_name (str): Role name to assign
        
        Returns:
            bool: True if successful
        """
        try:
            # Get the role
            role = self.keycloak_admin.get_realm_role(role_name)
            
            # Assign role to user
            self.keycloak_admin.assign_realm_roles(user_id, [role])
            logger.info(f"Role '{role_name}' assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Role assignment error: {str(e)}")
            raise Exception(f"Failed to assign role: {str(e)}")
    
    def assign_client_role_to_user(self, user_id, client_id, role_name):
        """
        Assign a client role to a user
        
        Args:
            user_id (str): Keycloak user ID
            client_id (str): Client ID
            role_name (str): Role name to assign
        
        Returns:
            bool: True if successful
        """
        try:
            # Get client
            client = self.keycloak_admin.get_client_id(client_id)
            
            # Get client role
            role = self.keycloak_admin.get_client_role(client, role_name)
            
            # Assign role to user
            self.keycloak_admin.assign_client_role(user_id, client, role)
            logger.info(f"Client role '{role_name}' assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Client role assignment error: {str(e)}")
            raise Exception(f"Failed to assign client role: {str(e)}")
        
        
    def get_user_by_username(self, username):
        """
        Get user by username from Keycloak
        
        Args:
            username (str): Username to search for
            
        Returns:
            dict: User information or None if not found
        """
        try:
            users = self.keycloak_admin.get_users({"username": username})
            if users:
                return users[0]
            return None
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return None
    
    def get_user_by_email(self, email):
        """
        Get user by email from Keycloak
        
        Args:
            email (str): Email to search for
            
        Returns:
            dict: User information or None if not found
        """
        try:
            users = self.keycloak_admin.get_users({"email": email})
            if users:
                return users[0]
            return None
        except Exception as e:
            logger.error(f"Get user by email error: {str(e)}")
            return None
    

# Global instance
keycloak_auth = KeycloakAuth()