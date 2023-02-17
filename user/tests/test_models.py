from django.test import TestCase
from user.models import Users

class UsersModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Users.objects.create(username='tester', password='123')

    def test_username_max_length(self):
        user = Users.objects.get(id=1)
        max_length = user._meta.get_field('username').max_length
        self.assertEquals(max_length, 16)
