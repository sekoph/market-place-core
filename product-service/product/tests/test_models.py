from django.test import TestCase
from product.models import Product, ProductCategory
from decimal import Decimal
from django.db import IntegrityError



class ProductCategoryModel(TestCase):
    
    def setUp(self):
        self.parent_category = ProductCategory.objects.create(
            name='Furniture',
            slug='Furniture',
            description='Household items made of wood'
        )
        
    
    
    def test_create_product_category_without_parent(self):
        product_category = ProductCategory.objects.create(
            name='Mobile Phones',
            slug='mobile-phones',
            description='Smartphones and accessories'
        )
        
        self.assertEqual(product_category.name, 'Mobile Phones')
        
    def test_create_product_category_with_parent(self):
        
        child_category = ProductCategory.objects.create(
            name='Table',
            slug='table',
            description='use to hold items',
            parent_id=self.parent_category.id
        )
        self.assertEqual(child_category.parent.id, self.parent_category.id)
        
        
    def test_string_representation(self):
        self.assertEqual(str(self.parent_category), "Furniture")

class ProductModelTest(TestCase):
    
    def setUp(self):
        self.product_category = ProductCategory.objects.create(
            name="Bread",
            slug="bread",
            description="a product of a food from a backery"
        )
    
    
    def test_create_product(self):
        product = Product.objects.create(
            name="Cookies",
            slug="cookies",
            description= "baked likes bread but harder",
            category=self.product_category,
            price=Decimal("245.04"),
            stock_quantity=10,
            available=True
        )
        
        self.assertEqual(product.name, "Cookies")
        self.assertEqual(self.product_category.name, 'Bread')
        self.assertIsNotNone(product.created_at)
        
        
    def test_product_requires_category(self):
        with self.assertRaises(IntegrityError):
            Product.objects.create(
            name="Unnamed Gadget",
            slug="unnamed-gadget",
            description="baked like bread but harder",
            category_id=None,
            price=Decimal("245.04"),
            stock_quantity=10,
            available=True
        )