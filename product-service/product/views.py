from shared.base.views import BaseViewSet
from .models import Product, ProductCategory
from .serializers import ProductCategorySerializer, ProductSerializer
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from shared.base.permission import IsAuthenticated

class ProductViewSet(BaseViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    

class ProductCategoryViewSet(BaseViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    
class AveragePriceByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        category = get_object_or_404(ProductCategory, slug=slug)
        avg_price = category.products.aggregate(avg_price=Avg('price'))['avg_price']

        return Response({
            'category': category.name,
            'average_price': avg_price
        })
    
    

