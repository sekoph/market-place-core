from django.test import TestCase
from django.db import IntegrityError
from customer.models import Customer
import uuid


class CustomerModelTest(TestCase):
    def setUp(self):
        Customer.objects.create(
            keycloak_user_id=str(uuid.uuid4()),
            username="testuser",
            email="testuser@gmail.com",
            phone = "254 092653532",
        )
        
    def test_customer_creation(self):
        customer = Customer.objects.create(
            keycloak_user_id=str(uuid.uuid4()),
            username="testuser2",
            email="testuser2@gmail.com",
            phone = "254 092653532",
        )
        
        self.assertEqual(str(customer), "testuser2")
    
    
    def test_duplicate_username_creation(self):
        # Attempt to create duplicate - should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                keycloak_user_id=str(uuid.uuid4()),
                username="testuser",  # Same username
                email="testuser3@gmail.com",
                phone="254092653533"
            )
            
    def test_duplicated_keycloak_user_id_creation(self):
            # Attempt to create duplicate - should raise IntegrityError
        Customer.objects.create(
            keycloak_user_id="f70100d4-bfd8-4593-a941-bf072df5b373",
            username="testuser3",
            email="testuser4@gmail.com",
            phone="254092653532"
        )
        
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
            keycloak_user_id="f70100d4-bfd8-4593-a941-bf072df5b373", # same keycloak_user-id
            username="testuser4",
            email="testuser5@gmail.com",
            phone="254092653532"
        )
            
    def test_duplicated_email_creation(self):
            # Attempt to create duplicate - should raise IntegrityError
        Customer.objects.create(
            keycloak_user_id=str(uuid.uuid4()),
            username="testuser5",
            email="testuser6@gmail.com",
            phone="254092653532"
        )
        
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
            keycloak_user_id=str(uuid.uuid4()),
            username="testuser6",
            email="testuser6@gmail.com", # same email
            phone="254092653532"
        )
            
    def test_customer_creation_without_keycloak_user(self):
        # cant create user without keycloak_user_id
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
            username="testuser5",
            email="testuser6@gmail.com",
            phone="254092653532"
        )