from django.test.client import Client
from django.test import TestCase
from user.models import Users


class UserTestCase(TestCase):

    password = None
    username = None
    user = None

    @classmethod
    def setUpClass(cls):
        print("Set up")
        cls.username = "tester1"
        cls.password = "123"
        cls.user = Users.objects.create(username=cls.username, password=cls.password)
        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')
        cls.user.delete()

    def test_login(self):
        path = '/login/'
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(path, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_checkusername(self):
        path = '/checkusername/'
        data = {
            'username': self.username
        }

        response = self.client.get(path, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
