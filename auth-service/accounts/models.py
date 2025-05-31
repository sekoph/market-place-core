from django.db import models
from django.contrib.auth.models import User

# You can extend the User model if needed
class UserProfile(models.Model):
    """
    Extended user profile to store additional Keycloak information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    keycloak_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Profile"
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"