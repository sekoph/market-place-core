from django.test import TestCase
from customer.models import Customer

class CustomerModelTest(TestCase):
    def test_customer_creation(self):
        customer = Customer.objects.create(
            first_name = "Micah",
            last_name = "Doe",
            username = "OnlyMicah",
            email = "micah@example.com",
            phone = "254 092653532"
        )
        
        self.assertEqual(str(customer), "OnlyMicah")
        self.assertEqual(customer.email, "micah@example.com")
