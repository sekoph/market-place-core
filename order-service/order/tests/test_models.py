from django.test import TestCase
from order.models import Order
from decimal import Decimal
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import uuid

class OrderModelTestCase(TestCase):
    def setUp(self):
        self.order_data = {
            'customer_id': uuid.uuid4(),
            'order_number': 'ORD' + ''.join([str(i) for i in range(1, 16)]),
            'customer_phone': '+254708063310',
            'product_id': uuid.uuid4(),
            'product_price': Decimal('19.99'),
            'quantity': 5
        }

    def test_create_order_successfully(self):
        order = Order.objects.create(**self.order_data)
        
        self.assertEqual(order.customer_id, self.order_data['customer_id'])
        self.assertEqual(order.order_number, self.order_data['order_number'])
        self.assertEqual(order.customer_phone, self.order_data['customer_phone'])
        self.assertEqual(order.product_id, self.order_data['product_id'])
        self.assertEqual(order.product_price, self.order_data['product_price'])
        self.assertEqual(order.quantity, self.order_data['quantity'])
        
        # Test auto-calculated total_amount
        expected_total = Decimal('19.99') * 5
        self.assertEqual(order.total_amount, expected_total)
        self.assertEqual(str(order), f"Order #{self.order_data['order_number']}")

    def test_required_fields(self):
        required_fields = ['customer_id', 'order_number', 'customer_phone',
                         'product_id', 'product_price', 'quantity']
        
        for field in required_fields:
            data = self.order_data.copy()
            data[field] = None
            
            with self.assertRaises(Exception):  
                Order.objects.create(**data)

    def test_decimal_fields(self):
        # Test different decimal values
        test_cases = [
            ('0.01', 1, '0.01'),
            ('999999.99', 1, '999999.99'),  # Max allowed with 10,2
            ('100.00', 3, '300.00')
        ]
        
        for price, quantity, expected_total in test_cases:
            data = self.order_data.copy()
            data['product_price'] = Decimal(price)
            data['quantity'] = quantity
            
            order = Order.objects.create(**data)
            self.assertEqual(order.total_amount, Decimal(expected_total))

    def test_meta_options(self):
        # Test ordering and indexes
        self.assertEqual(Order._meta.ordering, ['-created_at'])
        
        index_fields = {index.fields[0] for index in Order._meta.indexes}
        self.assertIn('customer_id', index_fields)
        self.assertIn('order_number', index_fields)

    def test_string_representation(self):
        order = Order.objects.create(**self.order_data)
        self.assertEqual(str(order), f"Order #{self.order_data['order_number']}")

    def test_save_method(self):
        # Test that save() properly calculates total_amount
        order = Order(**self.order_data)
        order.save()
        
        expected_total = self.order_data['product_price'] * self.order_data['quantity']
        self.assertEqual(order.total_amount, expected_total)
        
        # Test update scenario
        order.quantity = 10
        order.save()
        self.assertEqual(order.total_amount, self.order_data['product_price'] * 10)
        
        
    def test_create_order_without_customer_id(self):
        with self.assertRaises(IntegrityError):
            Order.objects.create(
                order_number= 'ORD' + ''.join([str(i) for i in range(1, 16)]),
                customer_phone= '+254708063310',
                product_id= uuid.uuid4(),
                product_price= Decimal(19.99),
                quantity=3
            )