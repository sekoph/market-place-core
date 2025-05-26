from .models import Product, ProductCategory
from shared.base.serializers import DynamicFieldModelSerializer
from rest_framework import serializers
from decimal import Decimal



class ProductCategorySerializer(DynamicFieldModelSerializer):
    
    """ Store UUID  for patent category """
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset = ProductCategory.objects.all(),
        source = 'parent',
        write_only = True,
        required = False,
        allow_null = True
    )
    
    parent = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model =  ProductCategory
        fields = ['id', 'name', 'slug', 'description', 'parent', 'parent_id']
        
    def get_parent(self, obj):
        if obj.parent:
            return {
                "id":obj.parent.id,
                "name":obj.parent.name,
                "slug":obj.parent.slug
            }
        return None
    
    
class ProductSerializer(DynamicFieldModelSerializer):
    category = ProductCategorySerializer(read_only = True)
    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = ProductCategory.objects.all(),
        source = 'category',
        write_only = True
    )
    
    price  = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category','category_id', 'price', 'stock_quantity', 'available']