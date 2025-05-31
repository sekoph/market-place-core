from .models import Customer
from shared.base.serializers import DynamicFieldModelSerializer

class CustomerSerializer(DynamicFieldModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'keycloak_user_id', 'username', 'email', 'phone']
        read_only_fields = ['id', 'keycloak_user_id', 'username', 'email']
