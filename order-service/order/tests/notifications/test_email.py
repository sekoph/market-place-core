import pytest
from unittest.mock import patch
from django.core import mail
from order.services.mails.mail_sms_handler import  send_admin_email

class TestSendAdminEmail:
    @patch('django.core.mail.send_mail')
    @patch('django.conf.settings', 
           EMAIL_HOST_USER='test@example.com',
           EMAIL_HOST_PASSWORD='password',
           DEFAULT_FROM_EMAIL='noreply@example.com',
           ADMIN_EMAIL='admin@example.com')
    def test_successful_email_send(self, mock_send_mail):
        test_data = {
            'order_number': 'ORD123',
            'username': 'testuser',
            'customer_phone': '254712345678',
            'product_name': 'Test Product',
            'product_price': '19.99',
            'quantity': 2
        }
        
        result = send_admin_email(test_data)
        
        assert result['status'] == 'success'
        mock_send_mail.assert_called_once()
        assert 'New Order #ORD123 Received' in mock_send_mail.call_args[0][0]

    @patch('django.conf.settings', EMAIL_HOST_USER=None)
    def test_missing_email_config(self):
        result = send_admin_email({})
        assert result['status'] == 'failed'
        assert 'Email configuration incomplete' in result['reason']

    @patch('django.core.mail.send_mail', side_effect=Exception('SMTP Error'))
    @patch('django.conf.settings', 
           EMAIL_HOST_USER='test@example.com',
           DEFAULT_FROM_EMAIL='noreply@example.com',
           ADMIN_EMAIL='admin@example.com')
    def test_email_send_failure(self, mock_send_mail):
        result = send_admin_email({'order_number': 'ORD123'})
        assert result['status'] == 'failed'
        assert 'SMTP Error' in result['reason']