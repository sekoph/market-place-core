# tests/test_orders/test_views.py
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status
from unittest.mock import patch, MagicMock
from decimal import Decimal
from order.models import Order
from order.views import OrderViewSet
from shared.utils.messaging import publish_event
from order.services.product_checker import check_product_availability
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = OrderViewSet.as_view({'post': 'create'})
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            sub='user123'
        )
        self.valid_payload = {
            "customer_phone": "+254708063310",
            "quantity": 5,
            "product_id": "4cc96b33-c7fc-45de-bfed-1679bd543209"
        }

    @patch('orders.services.product_checker.check_product_availability')
    @patch('shared.utils.messaging.publish_event')
    def test_create_order_successfully(self, mock_publish, mock_check_product):
        # Mock product availability check
        mock_check_product.return_value = {
            'available': True,
            'price': '19.99',
            'name': 'Test Product'
        }

        # Mock event publishing
        mock_publish.return_value = None

        request = self.factory.post('/orders/', self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(customer_id=self.user.sub).exists())
        
        # Verify product check was called
        mock_check_product.assert_called_once_with(
            product_id=self.valid_payload['product_id'],
            quantity=self.valid_payload['quantity']
        )
        
        # Verify event was published
        mock_publish.assert_called_once_with('order.created', {
            'username': self.user.username,
            'email': self.user.email,
            'product_name': 'Test Product',
            'product_price': '19.99',
            'customer_phone': self.valid_payload['customer_phone'],
            'quantity': self.valid_payload['quantity'],
            'order_number': Order.objects.first().order_number
        })

    def test_create_order_missing_required_fields(self):
        test_cases = [
            ({'quantity': 5, 'product_id': '123'}, 'customer_phone'),
            ({'customer_phone': '+254...', 'product_id': '123'}, 'quantity'),
            ({'customer_phone': '+254...', 'quantity': 5}, 'product_id'),
        ]

        for payload, missing_field in test_cases:
            request = self.factory.post('/orders/', payload, format='json')
            force_authenticate(request, user=self.user)
            response = self.view(request)
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(missing_field, str(response.data['detail']).lower())

    @patch('orders.services.product_checker.check_product_availability')
    def test_create_order_product_unavailable(self, mock_check_product):
        mock_check_product.return_value = {
            'available': False,
            'message': 'Out of stock'
        }

        request = self.factory.post('/orders/', self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Out of stock')

    @patch('orders.services.product_checker.check_product_availability')
    def test_create_order_invalid_price_format(self, mock_check_product):
        mock_check_product.return_value = {
            'available': True,
            'price': 'invalid_price',
            'name': 'Test Product'
        }

        request = self.factory.post('/orders/', self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid product price format')

    @patch('orders.services.product_checker.check_product_availability')
    @patch('shared.utils.messaging.publish_event')
    def test_create_order_serializer_error(self, mock_publish, mock_check_product):
        mock_check_product.return_value = {
            'available': True,
            'price': '19.99',
            'name': 'Test Product'
        }

        # Create invalid payload (missing required fields from serializer)
        invalid_payload = self.valid_payload.copy()
        invalid_payload.pop('customer_phone')

        request = self.factory.post('/orders/', invalid_payload, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_publish.assert_not_called()

    @patch('orders.services.product_checker.check_product_availability')
    @patch('shared.utils.messaging.publish_event')
    def test_create_order_exception_handling(self, mock_publish, mock_check_product):
        mock_check_product.return_value = {
            'available': True,
            'price': '19.99',
            'name': 'Test Product'
        }
        mock_publish.side_effect = Exception("Publishing failed")

        request = self.factory.post('/orders/', self.valid_payload, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Publishing failed')