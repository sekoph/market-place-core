import pytest
from unittest.mock import patch
from django.core import mail
from order.services.mails.mail_sms_handler import handle_order_completed

class TestHandleOrderCompleted:
    @patch('your_app.messaging.send_admin_email')
    @patch('your_app.messaging.send_user_sms')
    def test_successful_handling(self, mock_send_sms, mock_send_email):
        mock_send_email.return_value = {'status': 'success'}
        mock_send_sms.return_value = {'status': 'Success'}
        print("Mock send email called:", mock_send_email.called)
        test_data = {
            'order_number': 'ORD123',
            'username': 'testuser',
            'customer_phone': '254712345678'
        }
        
        handle_order_completed(test_data)
        
        mock_send_email.assert_called_once_with(test_data)
        mock_send_sms.assert_called_once_with(test_data)

    @patch('your_app.messaging.send_admin_email', side_effect=Exception('Email Error'))
    @patch('your_app.messaging.send_user_sms')
    def test_partial_failure(self, mock_send_sms, mock_send_email):
        test_data = {'order_number': 'ORD123'}
        
        handle_order_completed(test_data)
        
        # Should still attempt to send SMS even if email fails
        mock_send_sms.assert_called_once()