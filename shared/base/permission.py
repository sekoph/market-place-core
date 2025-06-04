from rest_framework.permissions import BasePermission
from shared.utils.auth_utils import keycloak_auth
import logging

logger = logging.getLogger(__name__)

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class HasRole(BasePermission):
    """
    Base permission class to check if user has specific role in Keycloak
    """
    def __init__(self, role):
        self.role = role
        
    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        try:
            #  Properly split the Authorization header
            token = auth_header.split(' ')[1]
            return keycloak_auth.has_role(token, self.role)
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False

class HasAnyRole(BasePermission):
    """
    Permission class to check if user has any of the specified roles
    """
    def __init__(self, roles):
        self.roles = roles if isinstance(roles, list) else [roles]
        
    def has_permission(self, request, view):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        try:
            token = auth_header.split(' ')[1]
            return any(keycloak_auth.has_role(token, role) for role in self.roles)
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False

class IsAdmin(HasRole):
    """
    Permission class for admin role
    """
    def __init__(self):
        super().__init__('admin')

class IsUser(HasRole):
    """
    Permission class for user role
    """
    def __init__(self):
        super().__init__('user')

class IsManager(HasRole):
    """
    Permission class for manager role
    """
    def __init__(self):
        super().__init__('manager')