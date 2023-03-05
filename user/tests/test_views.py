from django.test import TestCase
from django.urls import reverse, resolve

from user import views, forms, models


class RegistrationViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        data = {
            'username': 'tester',
            'password': '123456',
            'repeat_password': '123456',
            'tan': '124',
            'question': 2,
            'answer': 'cat'
        }
        self.url = reverse('register')
        self.successful_url = reverse('login')
        self.response_get = self.client.get(self.url)
        self.response_post = self.client.post(self.url, data, follow=True)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        tan = models.TANs.objects.get(id=1)
        self.assertEqual(tan.tan, '123')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/register/')
        self.assertEqual(view.func.view_class, views.RegistrationView)
        # alternative: self.assertEqual(view.func.__name__, views.RegistrationView.as_view().__name__)

    def test_csrf(self):
        self.assertContains(self.response_get, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response_get.context.get('form')
        self.assertIsInstance(form, forms.RegisterForm)

    '''--------------------------- Successful Registration ---------------------------'''

    def test_redirection(self):
        self.assertRedirects(self.response_post, self.successful_url, status_code=302, target_status_code=200)

    def test_user_creation(self):
        self.assertTrue(models.Users.objects.filter(username='tester').exists())

    def test_tan_authenticated(self):
        tan = models.TANs.objects.filter(tan='124').first()
        self.assertTrue(tan.authenticated)

    def test_security_answer(self):
        user = models.Users.objects.filter(username='tester').first()
        answer = models.SecurityAnswers.objects.filter(user=user).first()
        self.assertEqual(answer.answer, 'cat')

    def test_security_question(self):
        user = models.Users.objects.filter(username='tester').first()
        answer = models.SecurityAnswers.objects.filter(user=user).first()
        question = models.SecurityQuestions.objects.get(id=answer.question.id)
        self.assertEqual(question.id, 2)

    '''--------------------------- Failed Registration ---------------------------'''

    def test_empty_form(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_used_tan(self):
        data = {
            'username': 'new user',
            'password': '123456',
            'repeat_password': '123456',
            'tan': '124',
            'question': 2,
            'answer': 'cat'
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        self.assertEqual(str(form.errors['tan'][0]), "tan is used")

    def test_invalid_tan(self):
        data = {
            'username': 'new user',
            'password': '123456',
            'repeat_password': '123456',
            'tan': '321',
            'question': 2,
            'answer': 'cat'
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        self.assertEqual(str(form.errors['tan'][0]), "invalid tan")


class ResetPasswordViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        self.url = reverse('reset_password')
        self.successful_url = reverse('login')
        self.response = self.client.get(self.url)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/resetpassword/')
        self.assertEqual(view.func.view_class, views.ResetPasswordView)
        # alternative: self.assertEqual(view.func.__name__, views.RegistrationView.as_view().__name__)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_initial_form(self):
        form = self.response.context.get('initial_form')
        self.assertIsInstance(form, forms.InitialResetForm)

