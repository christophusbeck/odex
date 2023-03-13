import csv
import os
from datetime import timedelta

import requests
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import JsonResponse
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse, resolve
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
        exp = PendingExperiments.objects.filter(run_name='Test Experiment')
        self.assertTrue(exp.exists())
    #     all other attribute should be tested in model_testing

    def test_post_invalid_form(self):
        # except .csv file all other file would be rejected
        data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.txt", b"column1,column2,column3\n1,2,3\n4,5,6\n")
        }
        response_post = self.client.post(self.url, data, follow=True)
        self.assertFalse(Experiments.objects.filter(run_name='Test Experiment').exists())


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
        self.url = reverse('main')

        self.response_post = self.client.post(self.url, data, follow=True)

        self.exp = PendingExperiments.objects.filter(id=1, run_name='Test Experiment').first()

        # os.makedirs('user_1/1/main_test') already create a folder in client post function

        url_exp_id = str(self.response_post.content, encoding='utf8')

        self.url = reverse('delete_exp')

    def test_delete_experiment(self):
        response = self.client.get(self.url, {'id': self.exp.id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experiments.objects.filter(id=self.exp.id).exists())


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

class ConfigurationTestCase(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        user = Users.objects.filter(username="tester1").first()
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        self.url = reverse('configuration')
        self.successful_url = reverse('main')

        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', 'Age', 'Gender'])
            writer.writerow(['John', '25', 'Male'])
            writer.writerow(['Jane', '30', 'Female'])

        with open('test_data.csv', 'rb') as file:
            csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        # create a PendingExperiment object to use in the tests
        self.exp = PendingExperiments.objects.create(
            user=user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.pending,
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            operation_option='2',
            has_ground_truth=True,
            has_generated_file=True,
            main_file=csv_file
        )

        self.data = {'csrfmiddlewaretoken': ['LhESMQhKMlyrTJGAAhmbtB2fcdABFK1nkQiTJusQnnug3q9xwxQkDJTbABjgbMiF'],
                'operation_model_options': ['1'],
                'operation_except': [''],
                'operation_written': [''],
                'ground_truth_options': ['1'],
                'odms': ['1'],
                'ABOD_contamination': [''],
                'ABOD_n_neighbors': [''],
                'ABOD_method': [''],
                'CBLOF_n_clusters': [''],
                'CBLOF_contamination': [''],
                'CBLOF_clustering_estimator': [''],
                'COF_contamination': [''],
                'COF_n_neighbors': [''],
                'COF_method': [''],
                'COPOD_contamination': [''],
                'COPOD_n_jobs': [''],
                'ECOD_contamination': [''],
                'ECOD_n_jobs': [''],
                'FeatureBagging_base_estimator': [''],
                'FeatureBagging_n_estimators': [''],
                'FeatureBagging_contamination': [''],
                'GMM_n_components': [''],
                'GMM_covariance_type': [''],
                'GMM_tol': [''],
                'HBOS_n_bins': [''],
                'HBOS_alpha': [''],
                'HBOS_tol': [''],
                'IForest_n_estimators': [''],
                'IForest_max_samples': [''],
                'IForest_contamination': [''],
                'INNE_n_estimators': [''],
                'INNE_max_samples': [''],
                'INNE_contamination': [''],
                'KDE_contamination': [''],
                'KDE_bandwidth': [''],
                'KDE_algorithm': [''],
                'KPCA_contamination': [''],
                'KPCA_n_components': [''],
                'KPCA_n_selected_components': [''],
                'LMDD_contamination': [''],
                'LMDD_n_iter': [''],
                'LMDD_dis_measure': [''],
                'LODA_contamination': [''],
                'LODA_n_bins': [''],
                'LODA_n_random_cuts': [''],
                'LOF_n_neighbors': [''],
                'LOF_algorithm': [''],
                'LOF_leaf_size': [''],
                'LOCI_contamination': [''],
                'LOCI_alpha': [''],
                'LOCI_k': [''],
                'LUNAR_model_type': [''],
                'LUNAR_n_neighbours': [''],
                'LUNAR_negative_sampling': [''],
                'MAD_threshold': [''],
                'MCD_contamination': [''],
                'MCD_store_precision': [''],
                'MCD_assume_centered': [''],
                'OCSVM_kernel': [''],
                'OCSVM_degree': [''],
                'OCSVM_gamma': [''],
                'PCA_n_components': [''],
                'PCA_n_selected_components': [''],
                'PCA_contamination': [''],
                'RGraph_transition_steps': [''],
                'RGraph_n_nonzero': [''],
                'RGraph_gamma': [''],
                'ROD_contamination': [''],
                'ROD_parallel_execution': [''],
                'Sampling_contamination': [''],
                'Sampling_subset_size': [''],
                'Sampling_metric': [''],
                'x': ['68'],
                'y': ['15']
                }

        self.data = {'csrfmiddlewaretoken': 'LhESMQhKMlyrTJGAAhmbtB2fcdABFK1nkQiTJusQnnug3q9xwxQkDJTbABjgbMiF',
                'operation_model_options': '1',
                'operation_except': '',
                'operation_written': '',
                'ground_truth_options': '1',
                'odms': '1',
                'ABOD_contamination': '',
                'ABOD_n_neighbors': '',
                'ABOD_method': '',
                'CBLOF_n_clusters': '',
                'CBLOF_contamination': '',
                'CBLOF_clustering_estimator': '',
                'COF_contamination': '',
                'COF_n_neighbors': '',
                'COF_method': '',
                'COPOD_contamination': '',
                'COPOD_n_jobs': '',
                'ECOD_contamination': '',
                'ECOD_n_jobs': '',
                'FeatureBagging_base_estimator': '',
                'FeatureBagging_n_estimators': '',
                'FeatureBagging_contamination': '',
                'GMM_n_components': '',
                'GMM_covariance_type': '',
                'GMM_tol': '',
                'HBOS_n_bins': '',
                'HBOS_alpha': '',
                'HBOS_tol': '',
                'IForest_n_estimators': '',
                'IForest_max_samples': '',
                'IForest_contamination': '',
                'INNE_n_estimators': '',
                'INNE_max_samples': '',
                'INNE_contamination': '',
                'KDE_contamination': '',
                'KDE_bandwidth': '',
                'KDE_algorithm': '',
                'KPCA_contamination': '',
                'KPCA_n_components': '',
                'KPCA_n_selected_components': '',
                'LMDD_contamination': '',
                'LMDD_n_iter': '',
                'LMDD_dis_measure': '',
                'LODA_contamination': '',
                'LODA_n_bins': '',
                'LODA_n_random_cuts': '',
                'LOF_n_neighbors': '',
                'LOF_algorithm': '',
                'LOF_leaf_size': '',
                'LOCI_contamination': '',
                'LOCI_alpha': '',
                'LOCI_k': '',
                'LUNAR_model_type': '',
                'LUNAR_n_neighbours': '',
                'LUNAR_negative_sampling': '',
                'MAD_threshold': '',
                'MCD_contamination': '',
                'MCD_store_precision': '',
                'MCD_assume_centered': '',
                'OCSVM_kernel': '',
                'OCSVM_degree': '',
                'OCSVM_gamma': '',
                'PCA_n_components': '',
                'PCA_n_selected_components': '',
                'PCA_contamination': '',
                'RGraph_transition_steps': '',
                'RGraph_n_nonzero': '',
                'RGraph_gamma': '',
                'ROD_contamination': '',
                'ROD_parallel_execution': '',
                'Sampling_contamination': '',
                'Sampling_subset_size': '',
                'Sampling_metric': '',
                'x': '68',
                'y': '15'
                }

        self.response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.response_post = self.client.post(self.url, data= {'id': self.exp.id})

        print(self.response_post.status_code)


    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_page_status_code(self):
        self.assertEqual(self.response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/configuration/')
        self.assertEqual(view.func.view_class, experiment.views.ConfigView)

    def test_csrf(self):
        self.assertContains(self.response_get, 'csrfmiddlewaretoken')


    def test_template_used(self):
        self.assertTemplateUsed(self.response_get, 'Configuration.html')


    def test_not_existed_id(self):
        with self.assertRaises(AttributeError):
            response_get = self.client.get(self.url, data={'id': 1000000})

    def test_session(self):
        user = Users.objects.filter(username="tester1").first()
        print(self.response_get.request['QUERY_STRING'])
        print(self.response_get.context)
        print(self.response_get.client.session['info'])
        print(self.response_post.request['QUERY_STRING'])
        print(self.response_post.context)
        print(self.response_post.client.session['info'])
        self.assertEqual(self.response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_get(self):
        response = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.response_get, 'Configuration.html')

        # check that the context contains the expected objects
        self.assertEqual(self.response_get.context['exp'], self.exp)
        self.assertEqual(self.response_get.context['columns'],
                         {"testcolumn1": "6.433658544295", "testcolumn2": "5.509168303351"})
        self.assertIsNotNone(self.response_get.context['form'])
        self.assertIsNotNone(self.response_get.context['odms'])

    def test_post_valid_form(self):
        file_data = b"file contents here"
        file_name = "test_file.csv"
        file_mock = SimpleUploadedFile(file_name, file_data, content_type="text/csv")



        self.assertRedirects(self.response_post, self.successful_url)

    '''--------------------------- Successful ChangeName ---------------------------'''

    def test_redirection(self):
        self.assertRedirects(self.response_post, self.successful_url, status_code=302, target_status_code=200)

