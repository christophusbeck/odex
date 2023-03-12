
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils.timezone import now

import experiment.models
import user
from experiment.views import ResultView
from user import models
import json

from user.models import Users


class Test_MainView(TestCase):
    fixtures = ['user_tests.json']
    '''--------------------------- Session test ---------------------------'''
    def test_main_GET_without_login(self):
        client = Client()
        # without login and direct request to get into the main page, user would be redirected to the login page
        response = client.get('main/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/', status_code= 302, target_status_code=200, fetch_redirect_response=True)

    def setUp(self):
        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

    def test_main_GET_loggedin(self):
        self.url = reverse('main')
        response = self.response_get = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    '''--------------------------- Test Fixture Loading for user ---------------------------'''
    def test_fixtures(self):
        user_test = user.models.Users.objects.get(id=1)
        self.assertEqual(user_test.username, 'tester1')

    def test_post_valid_form(self):
        data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.csv", b"file_content"),
        }
        self.url = reverse('main')
        self.response_post = self.client.post(self.url, data, follow=True)
        exp = experiment.models.Experiments.objects.filter(run_name='Test Experiment')
        self.assertTrue(exp.exists())
    #     all other attribute should be tested in model_testing

    def test_post_invalid_form(self):
        # except .csv file all other file would be rejected
        data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.txt", b"file_content"),
        }
        self.url = reverse('main')
        self.response_post = self.client.post(self.url, data, follow=True)
        self.assertFalse(experiment.models.Experiments.objects.filter(run_name='Test Experiment').exists())


class Test_DeleteView(TestCase):

    def setUp(self):
        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)
        self.experiment = experiment.models.Experiments.objects.create(id=1, user_id=1, run_name='Test')
        self.url = reverse('delete_exp')

    def test_delete_experiment(self):
        response = self.client.get(self.url, {'id': self.experiment.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(experiment.models.Experiments.objects.filter(id=self.experiment.id).exists(), False)


class Test_ExperimentlistView(TestCase):
    def setUp(self):
        '''--------------------------- logged in ---------------------------'''
        self.user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': self.user.id, 'username': self.user.username}
        session.save()
        self.client.post('/login/')
        self.url = reverse('main')
        self.response_get = self.client.get(self.url)

        self.experiment = experiment.models.Experiments.objects.create(
            user=self.user, run_name='Test Run', created_time=now(),
            state='pending', file_name='test.csv', operation='filter', start_time=now(),
            duration=timedelta(minutes=10))

    def test_GET(self):
        # not allowed to get explist as url
        response = self.client.get(reverse('explist'))
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        response = self.client.post(reverse('explist'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('total', response.json())
        self.assertIn('rows', response.json())


    def test_row_generator(self):
        rows = experiment.views.ExperimentListView().row_generator(experiment.models.Experiments.objects.all())
        self.assertIsInstance(rows, list)
        self.assertIsInstance(rows[0], dict)
        self.assertIn('id', rows[0])
        self.assertIn('run_name', rows[0])
        self.assertIn('created_time', rows[0])
        self.assertIn('state', rows[0])
        self.assertIn('odm', rows[0])
        self.assertIn('file_name', rows[0])
        self.assertIn('operation', rows[0])
        self.assertIn('start_time', rows[0])
        self.assertIn('duration', rows[0])
