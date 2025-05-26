from django.db import models
from shared.base.models import BaseModel
from django.utils.text import slugify
from django.core.validators import MinLengthValidator


class ProductCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True,related_name='children', on_delete=models.SET_NULL)
    
    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='products')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinLengthValidator(0.01)]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at']),
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



