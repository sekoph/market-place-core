from .models import Order
from shared.base.serializers import DynamicFieldModelSerializer
from rest_framework import serializers


class OrderSerializer(DynamicFieldModelSerializer):
    
    product_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        coerce_to_string=False
    )
    total_amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = Order
        fields = ['id', 'customer_id','customer_phone', 'order_number', 'product_id','product_price', 'quantity',  'total_amount']
        read_only_fields = ['order_number', 'customer_id']
