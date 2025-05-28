
# orders/views.py
from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(customer_id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save(customer_id=self.request.user.id)
