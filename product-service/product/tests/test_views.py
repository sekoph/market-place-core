from rest_framework.test import APITestCase, APIRequestFactory
from django.urls import reverse
from product.models import Product, ProductCategory
from decimal import Decimal
import uuid
from shared.utils.auth_utils import KeycloakAuth
from unittest.mock import patch, ANY

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
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_list_products(self, mock_validate_token, mock_get_user_info):
        response = self.client.get(reverse('product-list'), HTTP_AUTHORIZATION='Bearer mock-valid-token')
        self.assertEqual(response.status_code, 200)
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_create_product(self, mock_validate_token, mock_get_user_info):
        data = {
            "name":"Shirts",
            "slug":"shirt",
            "description": "top weareable",
            "category_id": self.category.id,
            "price":Decimal("245.04"),
            "stock_quantity":10,
            "available":True
        }
        
        response = self.client.post(reverse('product-list'), data, HTTP_AUTHORIZATION='Bearer mock-valid-token')
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
    
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_list_products_without_parent_id(self, mock_validate_token, mock_get_user_info):
        response = self.client.get(reverse('category-list'), HTTP_AUTHORIZATION='Bearer mock-valid-token')
        self.assertEqual(response.status_code, 200)
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_list_products_with_parent_id(self, mock_validate_token, mock_get_user_info):
        response = self.client.get(reverse('category-list'),HTTP_AUTHORIZATION='Bearer mock-valid-token')
        self.assertEqual(response.status_code, 200)
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_create_product_without_parent_id(self, mock_validate_token, mock_get_user_info):
        data = {
            "name":"SUV",
            "slug":"suv",
            "description": "motor for transportation",
        }
        
        response = self.client.post(reverse('category-list'), data, HTTP_AUTHORIZATION='Bearer mock-valid-token')
        self.assertEqual(response.status_code, 201)
    
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })    
    def test_create_product_with_parent_id(self, mock_validate_token, mock_get_user_info):
        data = {
            "name":"Four Wheel",
            "slug":"four-wheel",
            "description": "motor for transportation",
            "parent_id":self.parent_category.id
        }
        
        response = self.client.post(reverse('category-list'), data, HTTP_AUTHORIZATION='Bearer mock-valid-token')
        self.assertEqual(response.status_code, 201)
        
        
class AveragePriceByCategoryViewTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        
        # Create test data
        self.category = ProductCategory.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        # Create products with prices
        Product.objects.bulk_create([
            Product(name="Laptop",
                slug="laptop",
                description= "bottom long pants",
                category=self.category,
                price=Decimal("245.04"),
                stock_quantity=10,
                available=True),
            
            Product(name="Phone",
                slug="phone",
                description= "bottom long pants",
                category=self.category,
                price=Decimal("500.04"),
                stock_quantity=10,
                available=True),
            
            Product(name="Tablet",
                slug="tablet",
                description= "bottom long pants",
                category=self.category,
                price=Decimal("800.04"),
                stock_quantity=10,
                available=True),
        ])


    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_correct_average_calculation(self, mock_validate_token, mock_get_user_info):
        """Test the average price calculation is correct"""
        response = self.client.get(
            reverse('average-price-by-category', kwargs={'slug': 'electronics'}),
            HTTP_AUTHORIZATION='Bearer mock-valid-token'
        )
        
        # (1000 + 500 + 300) / 3 = 600
        expected_avg = Decimal((245.04 + 500.04 + 800.04) / 3)
        self.assertAlmostEqual(response.data['average_price'], expected_avg)
        self.assertEqual(response.data['category'], 'Electronics')
