from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

class LoginSerializer(serializers.Serializer):
    """
    Serializer for handling OAuth2 authorization code flow
    """
    code = serializers.CharField(required=True, help_text="Authorization code from Keycloak")
    redirect_uri = serializers.URLField(required=True, help_text="Redirect URI used in authorization")
    state = serializers.CharField(required=False, help_text="State parameter for security")

class RefreshTokenSerializer(serializers.Serializer):
    """
    Serializer for refreshing access tokens
    """
    refresh_token = serializers.CharField(required=True, help_text="Refresh token")

class AuthUrlSerializer(serializers.Serializer):
    """
    Serializer for generating authorization URL
    """
    redirect_uri = serializers.URLField(required=True, help_text="Redirect URI for OAuth2 flow")
    state = serializers.CharField(required=False, help_text="State parameter for security")

class UserInfoSerializer(serializers.Serializer):
    """
    Serializer for user information response
    """
    sub = serializers.CharField(read_only=True)
    preferred_username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    given_name = serializers.CharField(read_only=True)
    family_name = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    
class TokenResponseSerializer(serializers.Serializer):
    """
    Serializer for token response
    """
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    expires_in = serializers.IntegerField(read_only=True)
    token_type = serializers.CharField(read_only=True, default="Bearer")
    
    
class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration
    """
    username = serializers.CharField(
        min_length=3,
        max_length=50,
        help_text="Username (3-50 characters, alphanumeric and underscores only)"
    )
    email = serializers.EmailField(help_text="Valid email address")
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Password (minimum 8 characters)"
    )
    confirm_password = serializers.CharField(
        min_length=8,
        write_only=True,
        help_text="Confirm password"
    )
    first_name = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="First name (optional)"
    )
    last_name = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="Last name (optional)"
    )
    send_verification_email = serializers.BooleanField(
        default=True,
        help_text="Send email verification after registration"
    )
    assign_default_role = serializers.CharField(
        required=False,
        default="user",
        help_text="Default role to assign (default: 'user')"
    )
    temporary_password = serializers.BooleanField(
        default=False,
        help_text="Whether password should be temporary (user will be forced to change it)"
    )

    def validate_username(self, value):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        return value.lower()  # Convert to lowercase for consistency

    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """Validate password confirmation"""
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        
        return attrs

class UserRegistrationResponseSerializer(serializers.Serializer):
    """
    Serializer for user registration response
    """
    user_id = serializers.CharField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    enabled = serializers.BooleanField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    created_timestamp = serializers.IntegerField(read_only=True)
    message = serializers.CharField(read_only=True)