from django.test import TestCase
from faker import Faker

# Create your tests here.
from Site_User.models import User

class testUser(TestCase):
    userName = Faker().first_name()
    def setUp(self):
        User.objects.create(username=self.userName,password=Faker().password())
        print(User.objects.filter(username=self.userName))
        print(User.objects.filter(username=self.userName))
        print(User.objects.filter(username=self.userName))
        print(User.objects.filter(username=self.userName))

    def test_Created_User(self):
        qs = User.objects.filter(username=self.userName).first()
        print(self.userName)
        self.assertIsNotNone(qs)


        # if User.objects.filter(username=self.userName).first():
        #     print("yes")
        # else:
        #     print("no")



