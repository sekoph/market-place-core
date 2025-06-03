from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, ProductViewSet, AveragePriceByCategoryView


router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product_categories', ProductCategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/<slug:slug>/average-price/', AveragePriceByCategoryView.as_view(), name='average-price-by-category'),
]