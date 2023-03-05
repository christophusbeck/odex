from django.test import TestCase
from django.urls import reverse, resolve

from user import views, forms, models


class RegistrationViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        self.url = reverse('register')
        self.successful_url = reverse('login')
        self.response_get = self.client.get(self.url)

    def test_fixtures(self):
        tan = models.TANs.objects.get(id=1)
        self.assertEqual(tan.tan, '123')

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


