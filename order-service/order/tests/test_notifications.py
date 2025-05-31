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
    
    @patch('order.services.mails.mail_sms_handler.')
    def test_sms_sent_successfully(self, mock_sms):
        """Test SMS is sent successfully"""
        # Mock successful SMS response
        mock_sms.send.return_value = {'status': 'success'}
        
        # Send notifications
        result = handle_order_completed(self.test_data)
        
        # Check SMS was called
        mock_sms.send.assert_called_once()
        
        # Check the message and phone number
        call_args = mock_sms.send.call_args
        message = call_args[0][0]
        phone_numbers = call_args[0][1]
        
        self.assertIn('John Doe', message)
        self.assertIn('order #12345', message)
        self.assertEqual(phone_numbers, ['254708123456'])
        self.assertTrue(result['sms_sent'])
    
    @patch('order.services.mails.mail_sms_handler')
    def test_both_notifications_sent(self, mock_sms):
        """Test both SMS and email are sent"""
        # Mock SMS
        mock_sms.send.return_value = {'status': 'success'}
        
        # Clear emails
        mail.outbox.clear()
        
        # Send notifications
        result = handle_order_completed(self.test_data)
        
        # Check both were sent
        self.assertTrue(result['sms_sent'])
        self.assertTrue(result['email_sent'])
        
        # Check SMS was called
        mock_sms.send.assert_called_once()
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
    
    @patch('order.services.mails.mail_sms_handler')
    def test_sms_fails_email_still_sent(self, mock_sms):
        """Test that if SMS fails, email is still sent"""
        # Mock SMS failure
        mock_sms.send.side_effect = Exception("SMS failed")
        
        # Clear emails
        mail.outbox.clear()
        
        # Send notifications
        result = handle_order_completed(self.test_data)
        
        # Check SMS failed but email succeeded
        self.assertFalse(result['sms_sent'])
        self.assertTrue(result['email_sent'])
        self.assertEqual(len(mail.outbox), 1)
    
    def test_email_fails_sms_still_works(self):
        """Test that if email fails, SMS still works"""
        with patch('order.services.mails.mail_sms_handler') as mock_sms:
            mock_sms.send.return_value = {'status': 'success'}
            
            # Mock email failure by breaking settings
            with patch('django.core.mail.send_mail', side_effect=Exception("Email failed")):
                result = handle_order_completed(self.test_data)
                
                # Check SMS succeeded but email failed
                self.assertTrue(result['sms_sent'])
                self.assertFalse(result['email_sent'])
    
    def test_invalid_phone_number(self):
        """Test handling of invalid phone number"""
        invalid_data = self.test_data.copy()
        invalid_data['customer_phone'] = 'invalid'
        
        with patch('order.services.mails.mail_sms_handler') as mock_sms:
            result = handle_order_completed(invalid_data)
            
            # SMS should not be called due to invalid phone
            mock_sms.send.assert_not_called()
            self.assertFalse(result['sms_sent'])
            
            # Email should still be sent
            self.assertTrue(result['email_sent'])
    
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
            self.assertIn('sms_sent', result)
            self.assertIn('email_sent', result)