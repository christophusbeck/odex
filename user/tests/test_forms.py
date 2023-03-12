from django.test import TestCase
from user.models import Users, SecurityQuestions,SecurityAnswers,TANs
from user.forms import LoginForm, QuestionForm, RegisterForm,InitialResetForm
from tools.encrypt import md5

class LoginFormTest(TestCase):
    def test_login_form_valid(self):
        data = {'username': 'testuser', 'password': 'testpassword'}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        data = {'username': 'testuser', 'password': ''}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())


class QuestionFormTest(TestCase):
    def test_valid_question_form(self):
        form = QuestionForm(data={
            "question": "Test question"
        })
        self.assertTrue(form.is_valid())

    def test_invalid_question_form(self):
        form = QuestionForm(data={})
        self.assertFalse(form.is_valid())


class RegisterFormTest(TestCase):
    def test_register_form_valid(self):
        security_question = SecurityQuestions.objects.create(
            question='What is your favorite color?'
        )
        form_data = {
            'username': 'tester',
            'password': '123',
            'repeat_password': '123',
            'tan': '123',
            'question': security_question.id,
            'answer': 'blue'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form_inconsistent_password(self):
        security_question = SecurityQuestions.objects.create(
            question='What is your favorite color?'
        )
        form_data = {
            'username': 'tester',
            'password': '123',
            'repeat_password': '456',
            'tan': '123',
            'question': security_question.id,
            'answer': 'blue'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(str(form.errors['__all__'][0]),'Inconsistent password input')

    def test_register_form_clean_repeat_password(self):
        security_question = SecurityQuestions.objects.create(
            question='What is your favorite color?'
        )
        form_data = {
            'username': 'tester1',
            'password': '123',
            'repeat_password': '123',
            'tan': '123',
            'question': security_question.id,
            'answer': 'blue'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['repeat_password'], '7088966d4c03aeb6a66c390ec6462589')

    def test_register_form_clean_password(self):
        security_question = SecurityQuestions.objects.create(
            question='What is your favorite color?'
        )
        form_data = {
            'username': 'tester1',
            'password': '123',
            'repeat_password': '123',
            'tan': '123',
            'question': security_question.id,
            'answer': 'blue'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['password'], '7088966d4c03aeb6a66c390ec6462589')
