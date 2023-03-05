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
