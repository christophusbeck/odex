from django.test import TestCase
from user.models import Users, SecurityQuestions
from user.forms import LoginForm, QuestionForm, RegisterForm


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
            'username': 'testuser',
            'password': 'testpassword',
            'repeat_password': 'testpassword',
            'tan': '123',
            'question': security_question.id,
            'answer': 'blue'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
