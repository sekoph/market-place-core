from unittest.mock import patch, ANY, Mock
from rest_framework.test import APITestCase
from django.urls import reverse
import uuid
from shared.utils.auth_utils import KeycloakAuth
from decimal import Decimal
from order.models import Order
from order.services import product_checker
import shared.utils.messaging




class OrderApiTest(APITestCase):
    @patch.object(KeycloakAuth, 'validate_token', return_value=False)
    def test_unauthorized_order_creation(self,mock_validate):
        test_data = {
            'customer_id': uuid.uuid4(),
            'order_number': 'ORD' + ''.join([str(i) for i in range(1, 16)]),
            'customer_phone': '+254708063310',
            'product_id': uuid.uuid4(),
            'product_price': Decimal('19.99'),
            'quantity': 5
        }
        
        response = self.client.post(
            reverse('order-list'),
            test_data,
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        
        
        # Verify the response
        self.assertEqual(response.status_code, 401)
        
        self.assertEqual(response.data['detail'], 'Invalid token')
        
        # Verify the mock was called with our token
        mock_validate.assert_called_once_with('invalid-token')
        
        # Verify no customer was created
        self.assertEqual(Order.objects.count(), 0)
        
        
        
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    # @patch.object(product_checker, 'check_product_availability', return_value={'available': False, 'message': 'Product is not available'})
    @patch('order.services.product_checker.RPCClient')
    def test_create_order_with_unavailable_product(self, mock_rpc_client, mock_validate, mock_get_user_info):
        
        mock_client_instance = Mock()
        
        mock_client_instance.call.return_value = {'available': False, 'message': 'Product is not available'}
        
        mock_rpc_client.return_value = mock_client_instance
        
        test_data = {
            'customer_id': uuid.uuid4(),
            'order_number': 'ORD' + ''.join([str(i) for i in range(1, 16)]),
            'customer_phone': '+254708063310',
            'product_id': uuid.uuid4(),
            'product_price': Decimal('19.99'),
            'quantity': 5
        }
        
        response = self.client.post(
            reverse('order-list'),
            test_data,
            HTTP_AUTHORIZATION='Bearer mock-valid-token'
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Product is not available')
        self.assertEqual(Order.objects.count(), 0)
        mock_rpc_client.assert_called_once_with(queue_name='product_availability_queue')
        mock_client_instance.call.assert_called_once()