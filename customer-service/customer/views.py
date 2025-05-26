from .models import Customer
from .serializers import CustomerSerializer
from shared.base.views import BaseViewSet

class CustomerViewSet(BaseViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """   Simplified endpoint for current user   """
        serializer = self.get_serializer(request.user.customer)
        return Response(serializer.data)