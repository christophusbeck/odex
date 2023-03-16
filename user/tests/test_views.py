from django.test import TestCase
from django.urls import reverse, resolve
from django.utils.http import urlencode

from user import views, forms, models
from user.models import Users
from tools.encrypt import md5
from django.http import JsonResponse


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
        data = {
            'username': 'tester',
            'password': '123456',
            'repeat_password': '123456',
            'tan': '124',
            'question': 2,
            'answer': 'cat'
        }


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

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_initial_form(self):
        form = self.response.context.get('initial_form')
        self.assertIsInstance(form, forms.InitialResetForm)

    '''--------------------------- Username does not exist ---------------------------'''

    def test_not_existed_username(self):
        data = {'username': 'user'}
        response = self.client.get(self.url, data)
        form = response.context.get('initial_form')
        self.assertEqual(str(form.errors['username'][0]), "This user does not exist")

    '''--------------------------- Username exists ---------------------------'''

    def test_existed_username(self):
        data = {'username': 'tester1'}
        response = self.client.get(self.url, data)
        initial_form = response.context.get('initial_form')
        form = response.context.get('form')
        self.assertIsInstance(initial_form, forms.InitialResetForm)
        self.assertIsInstance(form, forms.ResetPasswordForm)

    '''---------------------------   Basic URL tests for POST   ---------------------------'''

    def test_post_empty_form(self):
        data = {}
        query_string = urlencode({'username': 'tester1'})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'reset_password.html')
        self.assertIn('This field is required.', response_post.context['form'].errors['password'])
        self.assertIn('This field is required.', response_post.context['form'].errors['repeat_password'])
        self.assertIn('This field is required.', response_post.context['form'].errors['answer'])

    def test_post_valid_form(self):
        data = {'password': '123123', 'repeat_password': '123123', 'answer': 'cat'}
        query_string = urlencode({'username': 'tester1'})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)
        user = Users.objects.get(id=1)
        self.assertEqual(user.password, md5('123123'))

    def test_post_invalid_form_with_wrong_repeat_password(self):
        data = {'password': '123123', 'repeat_password': '111111', 'answer': 'cat'}
        query_string = urlencode({'username': 'tester1'})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'reset_password.html')
        self.assertIn('Inconsistent password input.', response_post.context['form'].errors['__all__'])

    def test_post_invalid_form_with_wrong_answer(self):
        data = {'password': '123123', 'repeat_password': '123123', 'answer': 'dog'}
        query_string = urlencode({'username': 'tester1'})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'reset_password.html')
        self.assertIn('Your answer is wrong.', response_post.context['form'].errors['answer'])

    def test_post_invalid_form_with_invalid_password(self):
        data = {'password': '123', 'repeat_password': '123', 'answer': 'cat'}
        query_string = urlencode({'username': 'tester1'})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'reset_password.html')
        self.assertIn('Ensure this value has at least 6 characters (it has 3).', response_post.context['form'].errors['password'])


class LoginViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        data = {
            'username': 'tester1',
            'password': '123',
        }
        self.url = reverse('login')
        self.successful_url = reverse('main')
        self.response_get = self.client.get(self.url)
        self.response_post = self.client.post(self.url, data, follow=True)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/login/')
        self.assertEqual(view.func.view_class, views.LoginView)

    def test_csrf(self):
        self.assertContains(self.response_get, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response_get.context.get('form')
        self.assertIsInstance(form, forms.LoginForm)

    '''--------------------------- Successful Login ---------------------------'''

    def test_redirection(self):
        self.assertRedirects(self.response_post, self.successful_url, status_code=302, target_status_code=200)

    '''--------------------------- Failed Login ------------------------------'''

    def test_empty_form(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_not_existed_username(self):
        data = {'username': 'tester', 'password': '123'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

    def test_error_password(self):
        data = {'username': 'tester1', 'password': '123456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertEqual(str(form.errors['password'][0]), "password error")


class ChangeNameViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        self.user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': self.user.id, 'username': self.user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)
        data = {
            'username': 'new_tester',
        }
        self.url = reverse('change_name')
        self.successful_url = reverse('main')
        self.response_get = self.client.get(self.url)
        self.response_post = self.client.post(self.url, data, follow=True)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/changename/')
        self.assertEqual(view.func.view_class, views.ChangeNameView)

    def test_csrf(self):
        self.assertContains(self.response_get, 'csrfmiddlewaretoken')

    def test_contains_initial_form(self):
        form = self.response_get.context.get('form')
        self.assertIsInstance(form, forms.ChangeNameForm)

    '''--------------------------- Successful ChangeName ---------------------------'''

    def test_redirection(self):
        self.assertRedirects(self.response_post, self.successful_url, status_code=302, target_status_code=200)

    def test_user_change_name(self):
        self.assertTrue(models.Users.objects.filter(username='new_tester').exists())
        self.assertFalse(models.Users.objects.filter(username='tester3').exists())

    '''--------------------------- Failed ChangeName ---------------------------'''

    def test_empty_form(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_already_existed_username(self):
        session = self.client.session
        session['info'] = {'id': self.user.id, 'username': 'tester1'}
        session.save()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)


class AboutUsViewTest(TestCase):
    def setUp(self):
        self.url = reverse('aboutus')
        self.response = self.client.get(self.url)

    def test_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/aboutus/')
        self.assertEqual(view.func.view_class, views.AboutUsView)

    def test_correct_template(self):
        self.assertTemplateUsed(self.response, 'aboutus.html')


class ChangePasswordViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        user = models.Users.objects.filter(username="tester1").first()
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        self.url = reverse('change_password')
        self.successful_url = reverse('main')
        self.response_get = self.client.get(self.url)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/changepassword/')
        self.assertEqual(view.func.view_class, views.ChangePasswordView)

    def test_csrf(self):
        self.assertContains(self.response_get, 'csrfmiddlewaretoken')

    def test_contains_initial_form(self):
        form = self.response_get.context.get('initial_form')
        self.assertIsInstance(form, forms.InitialChangePasswordForm)

    '''--------------------------- Failed Changing Password ---------------------------'''

    def test_empty_form(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_wrong_old_password(self):
        data = {'old_password': md5("321")}
        response = self.client.post(self.url, data)
        form = response.context.get('initial_form')
        self.assertEqual(str(form.errors['old_password'][0]), "The password is wrong")

    '''--------------------------- Successful Changing Password ---------------------------'''

    def test_correct_old_password(self):
        data1 = {
            'old_password': md5("123")
        }
        self.client.post(self.url, data1)
        data2 = {
            "new_password": "321",
            "repeat_password": "321"
        }
        self.client.post(self.url, data2)
        user = models.Users.objects.filter(username="tester1").first()
        self.assertEqual(user.password, md5("321"))


class CheckUsernameTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        self.url = reverse('check_username')
        self.response = self.client.get(self.url)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/checkusername/')
        self.assertEqual(view.func.view_class, views.CheckUsername)

    '''--------------------------- Username does not exist ---------------------------'''

    def test_not_existed_username(self):
        data = {'username': 'user'}
        response = self.client.get(self.url, data)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'flag': False})

    '''--------------------------- Username exists ---------------------------'''

    def test_existed_username(self):
        data = {'username': 'tester1'}
        response = self.client.get(self.url, data)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'flag': True})


class LogOutViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        user = models.Users.objects.filter(username="tester1").first()
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        self.url = reverse('logout')
        self.successful_url = reverse('login')
        self.response = self.client.get(self.url, follow=True)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/logout/')
        self.assertEqual(view.func.view_class, views.LogOutView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    '''--------------------------- Successful Log out ---------------------------'''

    def test_redirection(self):
        self.assertRedirects(self.response, self.successful_url, status_code=302, target_status_code=200)


class DeleteAccountViewTest(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        user = models.Users.objects.filter(username="tester1").first()
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        self.url = reverse('delete_user')
        self.successful_url = reverse('login')
        self.response = self.client.get(self.url, follow=True)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = models.Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/user/delete')
        self.assertEqual(view.func.view_class, views.DeleteAccountView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    '''--------------------------- Successful deleting account ---------------------------'''

    def test_user_deleted(self):
        self.assertFalse(models.Users.objects.filter(username="tester1").exists())

    def test_redirection(self):
        self.assertRedirects(self.response, self.successful_url, status_code=302, target_status_code=200)
