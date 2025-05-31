from django.contrib.auth.models import AnonymousUser

class KeycloakUser:
    def __init__(self, data):
        self.id = data.get('id')
        self.sub = data.get('sub')
        self.username = data.get('preferred_username')
        self.email = data.get('email')
        self.first_name = data.get('first_name', '')
        self.last_name = data.get('last_name', '')
        self.keycloak_token = data.get('keycloak_token')
        self.keycloak_user_info = data.get('keycloak_user_info')
        self.keycloak_token_info = data.get('keycloak_token_info')
        self.is_authenticated = True  # ✅ critical for DRF permission checks

    def __str__(self):
        return self.username or self.email or "KeycloakUser"
