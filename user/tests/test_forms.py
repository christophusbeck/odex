from django.test import TestCase
from user.models import Users, SecurityQuestions, SecurityAnswers, TANs
from user.forms import LoginForm, QuestionForm, RegisterForm, ResetPasswordForm, ChangePasswordForm, InitialResetForm, \
    ChangeNameForm, InitialChangePasswordForm


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
        self.assertEqual(str(form.errors['__all__'][0]), 'Inconsistent password input')

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


class ResetPasswordFormTest(TestCase):
    def test_resetpassword_form_valid_data(self):
        form_data = {
            'password': '123',
            'repeat_password': '123',
            'answer': 'mysecurityanswer'
        }
        form = ResetPasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_resetpassword_form_invalid_passwords(self):
        form_data = {
            'password': '123',
            'repeat_password': '456',
            'answer': 'mysecurityanswer'
        }
        form = ResetPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_resetpassword_form_invalid_answer(self):
        form_data = {
            'password': '123',
            'repeat_password': '123',
            'answer': ''
        }
        form = ResetPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())


class ChangePasswordFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'new_password': '123',
            'repeat_password': '123',
        }
        self.invalid_data = {
            'new_password': '123',
            'repeat_password': '456',
        }

    def test_valid_data(self):
        form = ChangePasswordForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = ChangePasswordForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(str(form.errors['__all__'][0]), 'Inconsistent password input')

    def test_clean_repeat_password(self):
        form = ChangePasswordForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['repeat_password'], '7088966d4c03aeb6a66c390ec6462589')

    def test_clean_new_password(self):
        form = ChangePasswordForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['new_password'], '7088966d4c03aeb6a66c390ec6462589')


class InitialResetFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'validusername'
        }
        form = InitialResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_blank_data(self):
        form_data = {
            'username': ''
        }
        form = InitialResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], ['This field is required.'])

    def test_invalid_length(self):
        form_data = {
            'username': 'thisusernameistoolong'
        }
        form = InitialResetForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['username'], [
            'Ensure this value has at most 16 characters (it has ' + str(len('thisusernameistoolong')) + ').'])


class ChangeNameFormTest(TestCase):
    def test_valid_form(self):
        form_data = {'username': 'testuser'}
        form = ChangeNameForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {'username': ''}
        form = ChangeNameForm(data=form_data)
        self.assertFalse(form.is_valid())


class InitialChangePasswordFormTest(TestCase):
    def test_valid_password(self):
        form_data = {'old_password': 'testpassword'}
        form = InitialChangePasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_password(self):
        form_data = {'old_password': ''}
        form = InitialChangePasswordForm(data=form_data)
        self.assertFalse(form.is_valid())
