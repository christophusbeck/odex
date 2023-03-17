from django.test import TestCase
from user.models import Users, SecurityQuestions, SecurityAnswers, TANs


class UsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Users.objects.create(username='tester', password='123')

    def test_username_max_length(self):
        user = Users.objects.get(id=1)
        max_length = user._meta.get_field('username').max_length
        self.assertEquals(max_length, 16)

    def test_password_max_length(self):
        user = Users.objects.get(id=1)
        max_length = user._meta.get_field('password').max_length
        self.assertEquals(max_length, 64)

    def test_username_label(self):
        user = Users.objects.get(id=1)
        field_label = user._meta.get_field('username').verbose_name
        self.assertEquals(field_label, 'username')

    def test_password_label(self):
        user = Users.objects.get(id=1)
        field_label = user._meta.get_field('password').verbose_name
        self.assertEquals(field_label, 'password')

    def test_object_name(self):
        user = Users.objects.get(id=1)
        expected_object_name = f'{user.username}'
        self.assertEquals(expected_object_name, str(user.username))

    def test_str_representation(self):
        user = Users.objects.get(id=1)
        self.assertEqual(str(user), 'tester (id:1)')

class SecurityQuestionsTest(TestCase):
    def setUp(self):
        SecurityQuestions.objects.create(question='What is your favorite movie?')

    def test_security_question(self):
        security_question = SecurityQuestions.objects.get(id=1)
        expected_question = 'What is your favorite movie?'
        self.assertEqual(security_question.question, expected_question)
        self.assertLess(len(security_question.question), 1025)


class SecurityAnswersTest(TestCase):
    def setUp(self):
        user = Users.objects.create(username='test_user')
        question = SecurityQuestions.objects.create(question='What is your favorite color?')
        SecurityAnswers.objects.create(user=user, question=question, answer='blue')

    def test_user_field(self):
        security_answer = SecurityAnswers.objects.get(id=1)
        self.assertEqual(security_answer.user.username, 'test_user')

    def test_question_field(self):
        security_answer = SecurityAnswers.objects.get(id=1)
        self.assertEqual(security_answer.question.question, 'What is your favorite color?')

    def test_answer_field(self):
        security_answer = SecurityAnswers.objects.get(id=1)
        self.assertEqual(security_answer.answer, 'blue')
        self.assertLessEqual(len(security_answer.answer), 64)
        self.assertNotEqual(security_answer.answer, 'red')


class TANsTest(TestCase):
    def setUp(self):
        TANs.objects.create(tan='123456', authenticated=False)

    def test_tan_field(self):
        tan_obj = TANs.objects.get(id=1)
        self.assertEqual(tan_obj.tan, '123456')
        self.assertLessEqual(len(tan_obj.tan), 6)
        self.assertNotEqual(tan_obj.tan, 'abcdef')

    def test_authenticated_field(self):
        tan_obj = TANs.objects.get(id=1)
        self.assertFalse(tan_obj.authenticated)
        tan_obj.authenticated = True
        tan_obj.save()
        updated_tan_obj = TANs.objects.get(id=1)
        self.assertTrue(updated_tan_obj.authenticated)
