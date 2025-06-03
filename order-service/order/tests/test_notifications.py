import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core import mail
from django.conf import settings

# Import your notification functions
from order.services.mails.mail_sms_handler import handle_order_completed, send_admin_email, format_phone_number


class NotificationTestCase(TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_data = {
            'customer_phone': '0708123456',
            'username': 'John Doe',
            'order_number': '12345',
            'total_amount': '1500.00'
        }
    
    def test_phone_number_formatting(self):
        """Test phone number formatting function"""
        # Test valid formats
        self.assertEqual(format_phone_number('0708123456'), '+254708123456')
        self.assertEqual(format_phone_number('254708123456'), '+254708123456')
        self.assertEqual(format_phone_number('2547 08123456'), '+254708123456')
        self.assertEqual(format_phone_number('708123456'), '+254708123456')
        
        # Test invalid formats
        self.assertIsNone(format_phone_number('invalid'))
        self.assertIsNone(format_phone_number(''))
        self.assertIsNone(format_phone_number(None))
    
    def test_admin_email_sent(self):
        """Test that admin email is sent correctly"""
        # Clear any existing emails
        mail.outbox.clear()
        
        # Send admin email
        result = send_admin_email(self.test_data)
        
        # Check email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check email content
        email = mail.outbox[0]
        self.assertIn('Order #12345', email.subject)
        self.assertIn('John Doe', email.body)
        self.assertIn('0708123456', email.body)
        self.assertIn('1500.00', email.body)
    

    def test_missing_data_fields(self):
        """Test handling of missing data fields"""
        incomplete_data = {
            'order_number': '12345'
            # Missing other fields
        }
        
        with patch('order.services.mails.mail_sms_handler') as mock_sms:
            result = handle_order_completed(incomplete_data)
            
            # Should handle gracefully
            self.assertIsInstance(result, dict)
            self.assertIn('email status', result)
            self.assertEqual(result['email status'], 'success')