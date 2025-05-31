from django.db import models
from shared.base.models import BaseModel

class Customer(BaseModel):
    keycloak_user_id = models.UUIDField(null=False, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    class Meta:
        verbose_name_plural = "customers"
    
    def __str__(self):
        return f"{self.username}"

