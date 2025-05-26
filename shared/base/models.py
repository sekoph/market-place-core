import uuid
from django.db import models

""" model providing created_at and updated fields.
    It is inherited by our models"""

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        
        

"""Abstact model adding soft delete functionality.
    Set its to false without actually deleting it"""
class SoftDeleteModel(models.Model):
    
    is_active = models.BooleanField(default=True)
    
    def delete(self, *args, **kwargs):
        """ overides default delete to soft delete"""
        
        self.is_active = False
        self.save()
        
    class Meta:
        abstract = True
        
 
"""Abstract class that provides a UUID primary key"""
class UUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    class Meta:
        abstract = True
        
        
""" Unified Abstract class that includes all the abstract classes to be inherited """
class BaseModel(UUIDModel, SoftDeleteModel, TimeStampModel):
    
    class Meta:
        abstract = True