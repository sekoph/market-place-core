from rest_framework.test import APITestCase
from django.urls import reverse
from product.models import Product, ProductCategory
from decimal import Decimal

class ProductAPITest(APITestCase):
    
    def setUp(self):
        self.category = ProductCategory.objects.create(
            name='Cloths',
            slug='cloths',
            description='covering to keep body warm'
        )
        
        
        self.product = Product.objects.create(
            name="Trousers",
            slug="trousers",
            description= "bottom long pants",
            category=self.category,
            price=Decimal("245.04"),
            stock_quantity=10,
            available=True
        )
        
    def test_list_products(self):
        response = self.client.get(reverse('product-list'))
        self.assertEqual(response.status_code, 200)
        
        
    def test_create_product(self):
        data = {
            "name":"Shirts",
            "slug":"shirt",
            "description": "top weareable",
            "category_id": self.category.id,
            "price":Decimal("245.04"),
            "stock_quantity":10,
            "available":True
        }
        
        response = self.client.post(reverse('product-list'), data)
        self.assertEqual(response.status_code, 201)
            

class ProductCategoryAPITest(APITestCase):
    
    def setUp(self):
        self.parent_category = ProductCategory.objects.create(
            name='Vehicle',
            slug='vehicle',
            description='motor for transportation'
        )
        
        self.child_category = ProductCategory.objects.create(
            name='Buses',
            slug='buses',
            description='motor for transportation',
            parent_id=self.parent_category.id
        )
        
    def test_list_products_without_parent_id(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, 200)
        
    def test_list_products_with_parent_id(self):
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, 200)
        
        
    def test_create_product_without_parent_id(self):
        data = {
            "name":"SUV",
            "slug":"suv",
            "description": "motor for transportation",
        }
        
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, 201)
        
    def test_create_product_with_parent_id(self):
        data = {
            "name":"Four Wheel",
            "slug":"four-wheel",
            "description": "motor for transportation",
            "parent_id":self.parent_category.id
        }
        
        response = self.client.post(reverse('category-list'), data)
        self.assertEqual(response.status_code, 201)