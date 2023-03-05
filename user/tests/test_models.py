from django.test import TestCase
from user.models import Users,SecurityQuestions

class UsersModelTest(TestCase):
    @classmethod
    def setUp(self):
        Users.objects.create(username='tester', password='123')

    def test_username_max_length(self):
        user = Users.objects.get(id=1)
        max_length = user._meta.get_field('username').max_length
        self.assertEquals(max_length, 16)

    def test_password_max_length(self):
        user = Users.objects.get(id=1)
        max_length = user._meta.get_field('password').max_length
        self.assertEquals(max_length, 64)

    def test_create(self):
        Users.objects.create(username='tester2', password='456')
        user = Users.objects.get(username='tester2')
        self.assertEquals(user.username,'tester2')
        self.assertEquals(user.password, '456')


    def test_delete(self):
        user = Users.objects.get(username='tester')
        user.delete()
        ret = Users.objects.filter(username='tester')
        self.assertEquals(len(ret), 0)

    # def test_update_username(self):
    #     user = Users.objects.get(username='tester')
    #     user.username = 'tester2'
    #     ret = Users.objects.get(username='tester2')
    #     self.assertEquals(ret.username, 'tester2')

    # def test_update_password(self):
    #     user = Users.objects.get(username='tester')
    #     user.password = '123456'
    #     ret = Users.objects.get(username='tester')
    #     self.assertEquals(ret.password, '123456')

class SecurityQuestionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        SecurityQuestions.objects.create(question='What is your favorite movie?')


