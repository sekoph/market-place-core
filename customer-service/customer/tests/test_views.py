from unittest.mock import patch
from rest_framework.test import APITestCase
from django.urls import reverse
import uuid
from shared.utils.auth_utils import KeycloakAuth
from customer.models import Customer

class CustomerApiTest(APITestCase):
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_authorized_create_customer(self, mock_get_user_info, mock_validate):
        """Test customer creation with mocked Keycloak authentication"""
        
        response = self.client.post(
            reverse('customer-list'),
            {'phone': '07898787264'},
            HTTP_AUTHORIZATION='Bearer mock-valid-token'
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 201)
        
        # Verify the mocks were called
        mock_validate.assert_called_once()
        mock_get_user_info.assert_called_once()
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=False)
    def test_unauthorized_create_customer(self, mock_validate):
        """Test that customer creation fails with invalid token"""
        
        test_data = {'phone': '07898787264'}
        
        
        response = self.client.post(
            reverse('customer-list'),
            test_data,
            HTTP_AUTHORIZATION='Bearer invalid-token'
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 401)
        
        self.assertEqual(response.data['detail'], 'Invalid token')
        
        # Verify the mock was called with our token
        mock_validate.assert_called_once_with('invalid-token')
        
        # Verify no customer was created
        self.assertEqual(Customer.objects.count(), 0)
        
        
    @patch.object(KeycloakAuth, 'validate_token', return_value=True)
    @patch.object(KeycloakAuth, 'get_user_info', return_value={
        'sub': str(uuid.uuid4()),
        'email': 'test@example.com',
        'preferred_username': 'testuser'
    })
    def test_prevent_duplicate_customer_profile(self, mock_get_user_info, mock_validate):
        """Test that duplicate customer profiles cannot be created"""
        result = KeycloakAuth().get_user_info()
        
        # Create initial customer
        Customer.objects.create(
            keycloak_user_id=result['sub'],
            username=result['preferred_username'],
            email=result['email'],
            phone='07898787264'
        )
        
        # Try to create duplicate
        response = self.client.post(
            reverse('customer-list'),
            {'phone': '07898787264'},
            HTTP_AUTHORIZATION='Bearer valid-token'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Customer profile already exists.')
        self.assertEqual(Customer.objects.count(), 1)