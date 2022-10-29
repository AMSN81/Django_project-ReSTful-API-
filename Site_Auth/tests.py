import json
from faker import Faker
from django.contrib import messages
from django.http import HttpResponse
from django.test import TestCase
from rest_framework.test import APIRequestFactory,APITestCase,APIClient

# Create your tests here.
from Site_User.models import User


class testAPI(APITestCase):
    def testRegisterAPI(self):
        client=APIClient()
        username=Faker().first_name()
        request=client.post(
            '/api/v1/auth/register',
            json.dumps({"username": username,
            "email": "asdad54ada@gmail.com",
            "first_name": "mmmmmmmmm",
            "last_name": "nnnnnnnnnn",
            "password": "ddada5564sfg54g5",
            "password2":"ddada5564sfg54g5"}),
            content_type="application/json")
        self.assertIsNotNone(User.objects.filter(username=username).first())


