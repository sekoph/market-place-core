from .models import Customer
from shared.base.serializers import DynamicFieldModelSerializer

class CustomerSerializer(DynamicFieldModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone']