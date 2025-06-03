from django.db import models
from shared.base.models import BaseModel
import random
import string
from decimal import Decimal

class Order(BaseModel):
    
    customer_id = models.UUIDField(null=False) # Reference to customer service
    order_number = models.CharField(max_length=50, unique=False)
    customer_phone = models.CharField(max_length=50, null=False)
    product_id = models.UUIDField()  # Reference to product service
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.product_price * Decimal(self.quantity)
        super().save(*args, **kwargs)
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['order_number']),
        ]
        
        
    def __str__(self):
        return f"Order #{self.order_number}"

