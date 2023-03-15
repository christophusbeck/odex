import csv
import os
from datetime import timedelta
import time

import requests
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.test import TestCase, Client, RequestFactory, TransactionTestCase
from django.urls import reverse, resolve
from django.utils.http import urlencode
from django.utils.timezone import now

import user
import experiment
from experiment.models import Experiments, PendingExperiments, FinishedExperiments, Experiment_state
from user.models import Users
from experiment.views import ResultView
import json




class Test_MainView(TestCase):
    fixtures = ['user_tests.json']
    '''--------------------------- Session test ---------------------------'''

    def setUp(self):
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        self.url = reverse('main')

    '''--------------------------- logged in ---------------------------'''
    def test_main_GET_without_login(self):
        client = Client()
        # without login and direct request to get into the main page, user would be redirected to the login page
        response = client.get('main/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/', status_code= 302, target_status_code=200, fetch_redirect_response=True)

    def test_main_GET_with_login(self):
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

    def test_main_GET_loggedin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    '''--------------------------- Test Fixture Loading for user ---------------------------'''
    def test_fixtures(self):
        user_test = Users.objects.get(id=1)
        self.assertEqual(user_test.username, 'tester1')

    def test_post_valid_form(self):
        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Age', 'Gender'])
            writer.writerow(['John', '25', 'Male'])
            writer.writerow(['Jane', '30', 'Female'])

        with open('test_data.csv', 'rb') as file:
            csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'Test Experiment',
            'main_file':csv_file,
        }
        response_post = self.client.post(self.url, data, follow=True)
        exp_queryset = PendingExperiments.objects.filter(run_name='Test Experiment')
        self.assertTrue(exp_queryset.exists())
        exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response_post.content, encoding='utf8'), {"status": True, "id": exp.id})

    def test_post_missing_form(self):
        data = {}
        response_post = self.client.post(self.url, data, follow=True)
        print(response_post.json()['error'])
        self.assertFalse(Experiments.objects.filter(run_name='Test Experiment').exists())
        self.assertJSONEqual(str(response_post.content, encoding='utf8'),
                             {"status": False, 'error': response_post.json()['error']})

        self.assertTrue(response_post.json()['error'])
        self.assertIn('This field is required.', response_post.json()['error']['run_name'])
        self.assertIn('This field is required.', response_post.json()['error']['main_file'])


    def test_post_invalid_form_with_non_csv_file(self):
        data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.txt", b"column1,column2,column3\n1,2,3\n4,5,6\n")
        }
        response_post = self.client.post(self.url, data, follow=True)
        self.assertFalse(Experiments.objects.filter(run_name='Test Experiment').exists())
        self.assertJSONEqual(str(response_post.content, encoding='utf8'),
                             {"status": False, 'error': response_post.json()['error']})

        self.assertTrue(response_post.json()['error'])
        self.assertNotIn('run_name', response_post.json()['error'])
        self.assertIn('Unsupported file extension.', response_post.json()['error']['main_file'])

    def test_post_invalid_form_with_fake_csv_file(self):
        data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.csv", b"file_content")
        }
        response_post = self.client.post(self.url, data, follow=True)
        self.assertFalse(Experiments.objects.filter(run_name='Test Experiment').exists())
        self.assertJSONEqual(str(response_post.content, encoding='utf8'),
                             {"status": False, 'error': response_post.json()['error']})

        self.assertTrue(response_post.json()['error'])
        self.assertNotIn('run_name', response_post.json()['error'])
        self.assertIn('Unsupported file, this .csv file has errors.', response_post.json()['error']['main_file'])


class Test_DeleteView(TestCase):

    def setUp(self):
        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

        '''--------------------------- create a folder and put the csv file in it ---------------------------'''

        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Age', 'Gender'])
            writer.writerow(['John', '25', 'Male'])
            writer.writerow(['Jane', '30', 'Female'])

        with open('test_data.csv', 'rb') as file:
            self.csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')


        data = {
            'run_name': 'Test Experiment',
            'main_file':self.csv_file,
        }
        url = reverse('main')
        response_post = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(id=1, run_name='Test Experiment').first()
        self.assertJSONEqual(str(response_post.content, encoding='utf8'), {"status": True, "id": self.exp.id})

        self.url = reverse('delete_exp')

    def test_delete_experiment(self):
        response = self.client.get(self.url, {'id': self.exp.id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experiments.objects.filter(id=self.exp.id).exists())
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True})


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

        self.experiment = Experiments.objects.create(
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
        rows = experiment.views.ExperimentListView().row_generator(Experiments.objects.all())
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




class ConfigurationTest(TransactionTestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        print("user.id:", user.id)
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

        '''--------------------------- create a folder and put the csv file in it ---------------------------'''

        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['x', 'y', 'z'])
            writer.writerow(['10', '25', '30'])
            writer.writerow(['20', '30', '40'])

        with open('test_data.csv', 'rb') as file:
            self.csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'Test Experiment',
            'main_file': self.csv_file,
        }
        url = reverse('main')
        response = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True, "id": self.exp.id})

        '''--------------------------- go into configuration ---------------------------'''

        self.url = reverse('configuration')
        self.successful_url = reverse('main')

        self.data = {'operation_model_options': '1', 'operation_except': '', 'operation_written': '',
                     'ground_truth_options': '1', 'odms': '1', 'ABOD_contamination': '', 'ABOD_n_neighbors': '',
                     'ABOD_method': '', 'CBLOF_n_clusters': '', 'CBLOF_contamination': '',
                     'CBLOF_clustering_estimator': '', 'COF_contamination': '', 'COF_n_neighbors': '', 'COF_method': '',
                     'COPOD_contamination': '', 'COPOD_n_jobs': '', 'ECOD_contamination': '', 'ECOD_n_jobs': '',
                     'FeatureBagging_base_estimator': '', 'FeatureBagging_n_estimators': '',
                     'FeatureBagging_contamination': '', 'GMM_n_components': '', 'GMM_covariance_type': '',
                     'GMM_tol': '', 'HBOS_n_bins': '', 'HBOS_alpha': '', 'HBOS_tol': '', 'IForest_n_estimators': '',
                     'IForest_max_samples': '', 'IForest_contamination': '', 'INNE_n_estimators': '',
                     'INNE_max_samples': '', 'INNE_contamination': '', 'KDE_contamination': '', 'KDE_bandwidth': '',
                     'KDE_algorithm': '', 'KPCA_contamination': '', 'KPCA_n_components': '',
                     'KPCA_n_selected_components': '', 'LMDD_contamination': '', 'LMDD_n_iter': '',
                     'LMDD_dis_measure': '', 'LODA_contamination': '', 'LODA_n_bins': '', 'LODA_n_random_cuts': '',
                     'LOF_n_neighbors': '', 'LOF_algorithm': '', 'LOF_leaf_size': '', 'LOCI_contamination': '',
                     'LOCI_alpha': '', 'LOCI_k': '', 'LUNAR_model_type': '', 'LUNAR_n_neighbours': '',
                     'LUNAR_negative_sampling': '', 'MAD_threshold': '', 'MCD_contamination': '',
                     'MCD_store_precision': '', 'MCD_assume_centered': '', 'OCSVM_kernel': '', 'OCSVM_degree': '',
                     'OCSVM_gamma': '', 'PCA_n_components': '', 'PCA_n_selected_components': '',
                     'PCA_contamination': '', 'RGraph_transition_steps': '', 'RGraph_n_nonzero': '', 'RGraph_gamma': '',
                     'ROD_contamination': '', 'ROD_parallel_execution': '', 'Sampling_contamination': '',
                     'Sampling_subset_size': '', 'Sampling_metric': '', 'x': '68', 'y': '15'}

        self.wrong_data = {'operation_model_options': '1', 'operation_except': '', 'operation_written': '',
                     'ground_truth_options': '1', 'odms': '1', 'ABOD_contamination': '', 'ABOD_n_neighbors': '',
                     'ABOD_method': '1', 'CBLOF_n_clusters': '', 'CBLOF_contamination': '',
                     'CBLOF_clustering_estimator': '', 'COF_contamination': '', 'COF_n_neighbors': '', 'COF_method': '',
                     'COPOD_contamination': '', 'COPOD_n_jobs': '', 'ECOD_contamination': '', 'ECOD_n_jobs': '',
                     'FeatureBagging_base_estimator': '', 'FeatureBagging_n_estimators': '',
                     'FeatureBagging_contamination': '', 'GMM_n_components': '', 'GMM_covariance_type': '',
                     'GMM_tol': '', 'HBOS_n_bins': '', 'HBOS_alpha': '', 'HBOS_tol': '', 'IForest_n_estimators': '',
                     'IForest_max_samples': '', 'IForest_contamination': '', 'INNE_n_estimators': '',
                     'INNE_max_samples': '', 'INNE_contamination': '', 'KDE_contamination': '', 'KDE_bandwidth': '',
                     'KDE_algorithm': '', 'KPCA_contamination': '', 'KPCA_n_components': '',
                     'KPCA_n_selected_components': '', 'LMDD_contamination': '', 'LMDD_n_iter': '',
                     'LMDD_dis_measure': '', 'LODA_contamination': '', 'LODA_n_bins': '', 'LODA_n_random_cuts': '',
                     'LOF_n_neighbors': '', 'LOF_algorithm': '', 'LOF_leaf_size': '', 'LOCI_contamination': '',
                     'LOCI_alpha': '', 'LOCI_k': '', 'LUNAR_model_type': '', 'LUNAR_n_neighbours': '',
                     'LUNAR_negative_sampling': '', 'MAD_threshold': '', 'MCD_contamination': '',
                     'MCD_store_precision': '', 'MCD_assume_centered': '', 'OCSVM_kernel': '', 'OCSVM_degree': '',
                     'OCSVM_gamma': '', 'PCA_n_components': '', 'PCA_n_selected_components': '',
                     'PCA_contamination': '', 'RGraph_transition_steps': '', 'RGraph_n_nonzero': '', 'RGraph_gamma': '',
                     'ROD_contamination': '', 'ROD_parallel_execution': '', 'Sampling_contamination': '',
                     'Sampling_subset_size': '', 'Sampling_metric': '', 'x': '68', 'y': '15'}

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/configuration/')
        self.assertEqual(view.func.view_class, experiment.views.ConfigView)

    def test_csrf(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertContains(response_get, 'csrfmiddlewaretoken')

    def test_template_used(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertTemplateUsed(response_get, 'Configuration.html')


    def test_not_existed_id(self):
        with self.assertRaises(AttributeError):
            response_get = self.client.get(self.url, data={'id': 1000000})

    def test_session(self):
        user = Users.objects.filter(username="tester3").first()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_get_editing_experiment(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'Configuration.html')

        # check that the context contains the expected objects
        self.assertEqual(response_get.context['exp'], self.exp)
        self.assertEqual(response_get.context['columns'], {'x': '10', 'y': '25', 'z': '30'})
        self.assertIsNotNone(response_get.context['form'])
        self.assertIsNotNone(response_get.context['odms'])

    def test_get_failed_experiment(self):
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(self.url + f'?{query_string}', data=self.wrong_data)
        time.sleep(1)
        print("self.exp.state: ", self.exp.state)
        self.assertEqual(self.exp.state, Experiment_state.failed)
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'Configuration.html')

        # check that the context contains the expected objects
        self.assertEqual(response_get.context['exp'], self.exp)
        self.assertEqual(response_get.context['columns'], {'x': '10', 'y': '25', 'z': '30'})
        self.assertIsNotNone(response_get.context['form'])
        self.assertIsNotNone(response_get.context['odms'])


    def test_post_valid_form(self):
        print("self.exp.state: ", self.exp)
        # in order to get the information /?id=, using urlencode
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(self.url + f'?{query_string}', data=self.data)
        self.assertRedirects(response_post, self.successful_url, status_code= 302, target_status_code= 200, fetch_redirect_response=True)

        time.sleep(1)
        print("self.exp.state: ", self.exp.state)

    def test_post_invalid_form(self):
        data = {}
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(f'{self.url}?{query_string}', data=data)

        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'Configuration.html')
        self.assertEqual(response_post.context['exp'], self.exp)
        self.assertEqual(response_post.context['columns'], {'x': '10', 'y': '25', 'z': '30'})
        self.assertIsNotNone(response_post.context['form'])
        self.assertIsNotNone(response_post.context['odms'])
        self.assertTrue(response_post.context['form'].errors)
        self.assertIn('This field is required.', response_post.context['form'].errors['ground_truth_options'])
        self.assertIn('This field is required.', response_post.context['form'].errors['operation_model_options'])

class ResultViewTest(TransactionTestCase):
    fixtures = ['user_tests.json']

    def setUp(cls):
        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        session = cls.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = cls.client.post('/login/')
        cls.assertEqual(response.status_code, 200)

        '''--------------------------- create a folder and put the csv file in it ---------------------------'''

        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['x', 'y', 'z'])
            writer.writerow(['10', '25', '30'])
            writer.writerow(['20', '30', '40'])

        with open('test_data.csv', 'rb') as file:
            cls.csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'Test Experiment',
            'main_file': cls.csv_file,
        }
        url = reverse('main')
        response = cls.client.post(url, data, follow=True)
        cls.exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        cls.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True, "id": cls.exp.id})

        '''--------------------------- go into configuration ---------------------------'''

        cls.data = {'csrfmiddlewaretoken': 'LhESMQhKMlyrTJGAAhmbtB2fcdABFK1nkQiTJusQnnug3q9xwxQkDJTbABjgbMiF',
                     'operation_model_options': '1', 'operation_except': '', 'operation_written': '',
                     'ground_truth_options': '1', 'odms': '1', 'ABOD_contamination': '', 'ABOD_n_neighbors': '',
                     'ABOD_method': '', 'CBLOF_n_clusters': '', 'CBLOF_contamination': '',
                     'CBLOF_clustering_estimator': '', 'COF_contamination': '', 'COF_n_neighbors': '', 'COF_method': '',
                     'COPOD_contamination': '', 'COPOD_n_jobs': '', 'ECOD_contamination': '', 'ECOD_n_jobs': '',
                     'FeatureBagging_base_estimator': '', 'FeatureBagging_n_estimators': '',
                     'FeatureBagging_contamination': '', 'GMM_n_components': '', 'GMM_covariance_type': '',
                     'GMM_tol': '', 'HBOS_n_bins': '', 'HBOS_alpha': '', 'HBOS_tol': '', 'IForest_n_estimators': '',
                     'IForest_max_samples': '', 'IForest_contamination': '', 'INNE_n_estimators': '',
                     'INNE_max_samples': '', 'INNE_contamination': '', 'KDE_contamination': '', 'KDE_bandwidth': '',
                     'KDE_algorithm': '', 'KPCA_contamination': '', 'KPCA_n_components': '',
                     'KPCA_n_selected_components': '', 'LMDD_contamination': '', 'LMDD_n_iter': '',
                     'LMDD_dis_measure': '', 'LODA_contamination': '', 'LODA_n_bins': '', 'LODA_n_random_cuts': '',
                     'LOF_n_neighbors': '', 'LOF_algorithm': '', 'LOF_leaf_size': '', 'LOCI_contamination': '',
                     'LOCI_alpha': '', 'LOCI_k': '', 'LUNAR_model_type': '', 'LUNAR_n_neighbours': '',
                     'LUNAR_negative_sampling': '', 'MAD_threshold': '', 'MCD_contamination': '',
                     'MCD_store_precision': '', 'MCD_assume_centered': '', 'OCSVM_kernel': '', 'OCSVM_degree': '',
                     'OCSVM_gamma': '', 'PCA_n_components': '', 'PCA_n_selected_components': '',
                     'PCA_contamination': '', 'RGraph_transition_steps': '', 'RGraph_n_nonzero': '', 'RGraph_gamma': '',
                     'ROD_contamination': '', 'ROD_parallel_execution': '', 'Sampling_contamination': '',
                     'Sampling_subset_size': '', 'Sampling_metric': '', 'x': '68', 'y': '15'}

        # in order to get the information /?id=, using urlencode
        url = reverse('configuration')
        params = {'id': cls.exp.id}
        query_string = urlencode(params)
        response_post = cls.client.post(url + f'?{query_string}', data=cls.data)

        cls.url = reverse('result')
        cls.successful_url = reverse('main')

        # self.response_get = self.client.get(self.url, data={'id': self.exp.id})
        # self.response_post = self.client.post(self.url + f'?{query_string}', data=self.data)

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/result/')
        self.assertEqual(view.func.view_class, experiment.views.ResultView)

    def test_csrf(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertContains(response_get, 'csrfmiddlewaretoken')

    def test_template_used(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertTemplateUsed(response_get, 'result.html')

    def test_not_existed_id(self):
        with self.assertRaises(AttributeError):
            response_get = self.client.get(self.url, data={'id': 1000000})

    def test_session(self):
        user = Users.objects.filter(username="tester3").first()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_get_finished_experiment(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'result.html')
        self.assertContains(response_get, self.exp.id)

    def test_get_nonexistent_experiment(self):
        with open('test_file.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['a', 'b', 'c'])
            writer.writerow(['10', '25', '30'])
            writer.writerow(['20', '30', '40'])

        with open('test_file.csv', 'rb') as file:
            test_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'Pending Experiment',
            'main_file': test_file
        }

        url = reverse('main')
        main_response = self.client.post(url, data, follow=True)
        exp = PendingExperiments.objects.get(run_name='Pending Experiment')
        self.assertJSONEqual(str(main_response.content, encoding='utf8'), {"status": True, "id": exp.id})

        print("self.url: ", self.url, "exp.id: ", exp.id)
        response = self.client.get(self.url, data={'id': exp.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/configuration/?id=' + str(exp.id))








