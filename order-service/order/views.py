
# orders/views.py
from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer
from shared.base.views import BaseViewSet
from .services.product_checker import check_product_availability
from rest_framework import status
from rest_framework.response import Response
from shared.utils.messaging import publish_event
from decimal import Decimal, InvalidOperation
import random
import string
# from shared.base.permission import IsAuthenticated, IsAdmin, IsUser

class OrderViewSet(BaseViewSet):
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer_id=self.request.user.sub)

    def perform_create(self, serializer):
        serializer.save(customer_id=self.request.user.sub)

    def perform_update(self, serializer):
        serializer.save(customer_id=self.request.user.sub)
        
    def perform_destroy(self, instance):
        instance.delete()


    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity'))
        print(f"[Product Id] {product_id}")
        print(f"[Quantity] {quantity}")
        
        
        if not product_id or not quantity:
            return Response({'detail': 'product id and quantity are required'},
                            status=status.HTTP_400_BAD_REQUEST)
            
            
        check_product = check_product_availability(product_id=product_id, quantity=quantity)
        
        if not check_product.get('available'):
            return Response({'detail': check_product.get('message', 'Product not available')})
        
        try:
            product_price = Decimal(str(check_product['price'])).quantize(Decimal('0.00'))
            characters = string.ascii_letters + string.digits
            order_number = ''.join(random.choice(characters) for _ in range(15))
            # total_amount = product_price * Decimal(quantity)
        except (ValueError, TypeError, KeyError, InvalidOperation):
            return Response({'detail': 'Invalid product price format'},
                        status=status.HTTP_400_BAD_REQUEST)
        
        order_data = request.data.copy()
        order_data['product_price'] = product_price
        order_data['order_number'] = order_number
        
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            
            # publish order creation event
            publish_event('order.created',{
                'username': request.user.username,
                'email': request.user.email,
                'product_name': check_product['name'],
                'product_price':check_product['price'],
                'customer_phone': request.data.get('customer_phone'),
                'quantity': quantity,
                'order_number': order_number,
            })
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
    