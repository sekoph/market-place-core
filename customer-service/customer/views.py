from .models import Customer
from .serializers import CustomerSerializer
from shared.base.views import BaseViewSet

class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer