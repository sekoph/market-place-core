from django.db import models
from shared.base.models import BaseModel

class Order(BaseModel):
    PROCESSING = "Processing"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    
    
    STATUS_CHOICES = [
        (PROCESSING, 'Processing'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]
    
    customer_id = models.UUIDField(null=False) # Reference to customer service
    order_number = models.CharField(max_length=50, unique=True)
    product_id = models.UUIDField()  # Reference to product service
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PROCESSING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_status = models.CharField(max_length=50)
    
    def save(self, *args, **kwargs):
        self.total_amount = self.product_price * self.quantity
        super().save(*args, **kwargs)
    
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
        
        
    def __str__(self):
        return f"Order #{self.order_number}"

