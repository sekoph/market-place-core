import pytest
from unittest.mock import patch
from django.core import mail
from order.services.mails.mail_sms_handler import send_user_sms


class TestSendUserSMS:
    @patch('africastalking.SMS.send')
    def test_successful_sms_send(self, mock_sms_send):
        mock_sms_send.return_value = {'status': 'success'}
        
        test_data = {
            'customer_phone': '254712345678',
            'username': 'testuser',
            'order_number': 'ORD123'
        }
        
        result = send_user_sms(test_data)
        
        assert result['status'] == 'Success'
        mock_sms_send.assert_called_once()
        assert 'ORD123' in mock_sms_send.call_args[0][0]

    @patch('africastalking.SMS.send', side_effect=Exception('API Error'))
    def test_sms_send_failure(self, mock_sms_send):
        result = send_user_sms({
            'customer_phone': '254712345678',
            'username': 'testuser'
        })
        assert result['status'] == 'failed'