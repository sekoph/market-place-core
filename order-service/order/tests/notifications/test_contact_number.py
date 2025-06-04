import pytest
from unittest.mock import patch
from django.core import mail
from order.services.mails.mail_sms_handler import format_phone_number

class TestFormatPhoneNumber:
    @pytest.mark.parametrize("input_phone,expected", [
        ("254712345678", "+254712345678"),  # Missing +
        ("+254712345678", "+254712345678"),  # Correct format
        ("0712345678", "+254712345678"),     # Local format
        ("712345678", "+254712345678"),      # Missing 0
        ("+254 712 345 678", "+254712345678"),  # With spaces
        ("254-712-345-678", "+254712345678"),   # With dashes
    ])
    def test_valid_phone_numbers(self, input_phone, expected):
        assert format_phone_number(input_phone) == expected

    @pytest.mark.parametrize("invalid_phone", [
        "123456",           # Too short
        "2547123456789",    # Too long
        "+255712345678",    # Wrong country code
        "071234567",        # Invalid length
        "abc123",           # Non-numeric
        None,               # None input
        "",                 # Empty string
    ])
    def test_invalid_phone_numbers(self, invalid_phone):
        assert format_phone_number(invalid_phone) is None