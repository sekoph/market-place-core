from shared.base.views import BaseViewSet
from .models import Product, ProductCategory
from .serializers import ProductCategorySerializer, ProductSerializer

class ProductViewSet(BaseViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    

class ProductCategoryViewSet(BaseViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    
    

