from .models import Order
from shared.base.serializers import DynamicFieldModelSerializer
from rest_framework import serializers


class OrderSerializer(DynamicFieldModelSerializer):
    
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'order_number','product_id','product_price','quantity', 'status', 'total_amount', 'payment_status']
        read_only_fields = ['total_amount']
