from rest_framework.test import APITestCase
from django.urls import reverse 
from customer.models import Customer


class CustomerApiTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name = "Jane",
            last_name = "Doe",
            username = "OnlyJane",
            email = "jane@example.com",
            phone = "254 792653532"
        )
        
    def test_list_customer(self):
        response = self.client.get(reverse('customer-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data),4)
        
    def test_create_customer(self):
        data = {
            "first_name": "Milton",
            "last_name": "Doe",
            "username" : "OnlyMilton",
            "email" : "milton@example.com",
            "phone" : "254 892653532"
        }
        
        response = self.client.post(reverse('customer-list'), data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.count(), 2)
        
        