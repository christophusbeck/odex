import csv
import os
from datetime import timedelta
import time

import pyod
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse, resolve
from django.utils.http import urlencode
from django.utils.timezone import now

import experiment
from experiment.models import Experiments, PendingExperiments, FinishedExperiments, Experiment_state
from tools import odm_handling
from tools.odm_handling import get_odm_dict
from user.models import Users
from experiment.views import ResultView


class Test_MainView(TestCase):
    fixtures = ['user_tests.json']

    def setUp(self):
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)
        self.url = reverse('main')

    def tearDown(self):
        path = "test_data.csv"
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                pass

        for e in Experiments.objects.all():
            e.delete()
        for u in Users.objects.all():
            u.delete()

    '''--------------------------- Test Fixture Loading for user ---------------------------'''

    def test_fixtures(self):
        user_test = Users.objects.get(id=1)
        self.assertEqual(user_test.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_session(self):
        user = Users.objects.filter(username="tester3").first()
        response_get = self.client.get(self.url)
        self.assertEqual(response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_page_status_code(self):
        response_get = self.client.get(self.url)
        self.assertEqual(response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/main/')
        self.assertEqual(view.func.view_class, experiment.views.MainView)

    def test_template_used(self):
        response_get = self.client.get(self.url)
        self.assertTemplateUsed(response_get, 'main.html')

    '''---------------------------   Basic URL tests for GET    ---------------------------'''

    def test_main_get_without_login(self):
        client = Client()
        # without login and direct request to get into the main page, user would be redirected to the login page
        response = client.get('main/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/', status_code=302, target_status_code=200, fetch_redirect_response=True)

    def test_main_get_with_login(self):
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

    def test_main_get_loggedin(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    '''---------------------------   Basic URL tests for POST with valid form    ---------------------------'''

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
            'main_file': csv_file
        }
        response_post = self.client.post(self.url, data, follow=True)
        self.assertTrue(PendingExperiments.objects.filter(run_name='Test Experiment').exists())
        exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response_post.content, encoding='utf8'), {"status": True, "id": exp.id})

    def test_post_valid_form_with_blank_column(self):
        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Name', '', 'Age', '', 'Gender', '', ''])
            writer.writerow(['John', '', '25', '', 'Male', '', ''])
            writer.writerow(['Jane', '', '30', '', 'Female', '', ''])

        with open('test_data.csv', 'rb') as file:
            csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'Test Experiment',
            'main_file': csv_file
        }
        response_post = self.client.post(self.url, data, follow=True)
        self.assertTrue(PendingExperiments.objects.filter(run_name='Test Experiment').exists())
        exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response_post.content, encoding='utf8'), {"status": True, "id": exp.id})
        self.assertEqual(exp.get_columns(), {"Name": "John", "Age": "25", "Gender": "Male"})

    '''---------------------------   Basic URL tests for POST with invalid form    ---------------------------'''

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
        user = Users.objects.create(username='tester1', password='123')
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
            'main_file': self.csv_file,
        }
        url = reverse('main')
        response_post = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(id=1, run_name='Test Experiment').first()
        self.assertJSONEqual(str(response_post.content, encoding='utf8'), {"status": True, "id": self.exp.id})

        self.url = reverse('delete_exp')

    def tearDown(self):
        path = "test_data.csv"
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                pass

        for e in Experiments.objects.all():
            e.delete()
        for u in Users.objects.all():
            u.delete()


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

    def tearDown(self):
        for e in Experiments.objects.all():
            e.delete()
        for u in Users.objects.all():
            u.delete()


    def test_get(self):
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
    path_input = "input.csv"
    path_gt = "gt.csv"
    path_gen = "gen.csv"

    def setUp(self):
        '''--------------------------- generate files ---------------------------'''
        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        training_data = list(training_data)
        training_data.insert(0, ["x1", "x2", "x3"])
        gt_list = []
        for row in train_gt:
            gt_list.append([row])

        odm_handling.write_data_to_csv(self.path_input, training_data)
        odm_handling.write_data_to_csv(self.path_gt, gt_list)
        odm_handling.write_data_to_csv(self.path_gen, test_data)

        self.file = open(self.path_input, 'r', encoding='UTF-8')
        self.gt = open(self.path_gt, 'r', encoding='UTF-8')
        self.gen = open(self.path_gen, 'r', encoding='UTF-8')

        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123')
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

        '''--------------------------- create a folder and put the csv file in it ---------------------------'''

        self.file = open(self.path_input, 'r', encoding='UTF-8')
        data = {
            'run_name': 'Test Experiment',
            'main_file': self.file,
        }
        url = reverse('main')
        response = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True, "id": self.exp.id})


        '''--------------------------- go into configuration ---------------------------'''

        self.url = reverse('configuration')
        self.successful_url = reverse('main')

        self.data = {'operation_model_options': ['1'], 'operation_except': [''], 'operation_written': [''],
                     'ground_truth_options': ['1'], 'odms': ['1'], 'ABOD_contamination': [''],
                     'ABOD_n_neighbors': [''], 'ABOD_method': [''], 'CBLOF_n_clusters': [''],
                     'CBLOF_contamination': [''], 'CBLOF_clustering_estimator': [''], 'CBLOF_alpha': [''],
                     'CBLOF_beta': [''], 'CBLOF_use_weights': [''], 'CBLOF_check_estimator': [''],
                     'CBLOF_random_state': [''], 'CBLOF_n_jobs': [''], 'COF_contamination': [''],
                     'COF_n_neighbors': [''], 'COF_method': [''], 'COPOD_contamination': [''], 'COPOD_n_jobs': [''],
                     'ECOD_contamination': [''], 'ECOD_n_jobs': [''], 'FeatureBagging_base_estimator': [''],
                     'FeatureBagging_n_estimators': [''], 'FeatureBagging_contamination': [''],
                     'FeatureBagging_max_features': [''], 'FeatureBagging_bootstrap_features': [''],
                     'FeatureBagging_check_detector': [''], 'FeatureBagging_check_estimator': [''],
                     'FeatureBagging_n_jobs': [''], 'FeatureBagging_random_state': [''],
                     'FeatureBagging_combination': [''], 'FeatureBagging_verbose': [''],
                     'FeatureBagging_estimator_params': [''], 'GMM_n_components': [''],
                     'GMM_covariance_type': [''], 'GMM_tol': [''], 'GMM_reg_covar': [''], 'GMM_max_iter': [''],
                     'GMM_n_init': [''], 'GMM_init_params': [''], 'GMM_weights_init': [''], 'GMM_means_init': [''],
                     'GMM_precisions_init': [''], 'GMM_random_state': [''], 'GMM_warm_start': [''],
                     'GMM_contamination': [''], 'HBOS_n_bins': [''], 'HBOS_alpha': [''], 'HBOS_tol': [''],
                     'HBOS_contamination': [''], 'IForest_n_estimators': [''], 'IForest_max_samples': [''],
                     'IForest_contamination': [''], 'IForest_max_features': [''], 'IForest_bootstrap': [''],
                     'IForest_n_jobs': [''], 'IForest_behaviour': [''], 'IForest_random_state': [''],
                     'IForest_verbose': [''], 'INNE_n_estimators': [''], 'INNE_max_samples': [''],
                     'INNE_contamination': [''], 'INNE_random_state': [''], 'KDE_contamination': [''],
                     'KDE_bandwidth': [''], 'KDE_algorithm': [''], 'KDE_leaf_size': [''], 'KDE_metric': [''],
                     'KDE_metric_params': [''], 'KPCA_contamination': [''], 'KPCA_n_components': [''],
                     'KPCA_n_selected_components': [''], 'KPCA_kernel': [''], 'KPCA_gamma': [''], 'KPCA_degree': [''],
                     'KPCA_coef0': [''], 'KPCA_kernel_params': [''], 'KPCA_alpha': [''], 'KPCA_eigen_solver': [''],
                     'KPCA_tol': [''], 'KPCA_max_iter': [''], 'KPCA_remove_zero_eig': [''], 'KPCA_copy_X': [''],
                     'KPCA_n_jobs': [''], 'KPCA_sampling': [''], 'KPCA_subset_size': [''], 'KPCA_random_state': [''],
                     'LMDD_contamination': [''], 'LMDD_n_iter': [''], 'LMDD_dis_measure': [''],
                     'LMDD_random_state': [''], 'LODA_contamination': [''], 'LODA_n_bins': [''],
                     'LODA_n_random_cuts': [''], 'LOF_n_neighbors': [''], 'LOF_algorithm': [''], 'LOF_leaf_size': [''],
                     'LOF_metric': [''], 'LOF_p': [''], 'LOF_metric_params': [''], 'LOF_contamination': [''],
                     'LOF_n_jobs': [''], 'LOF_novelty': [''], 'LOCI_contamination': [''], 'LOCI_alpha': [''],
                     'LOCI_k': [''], 'LUNAR_model_type': [''], 'LUNAR_n_neighbours': [''],
                     'LUNAR_negative_sampling': [''], 'LUNAR_val_size': [''], 'LUNAR_scaler': [''],
                     'LUNAR_epsilon': [''], 'LUNAR_proportion': [''], 'LUNAR_n_epochs': [''], 'LUNAR_lr': [''],
                     'LUNAR_wd': [''], 'LUNAR_verbose': [''], 'MAD_threshold': [''], 'MCD_contamination': [''],
                     'MCD_store_precision': [''], 'MCD_assume_centered': [''], 'MCD_support_fraction': [''],
                     'MCD_random_state': [''], 'OCSVM_kernel': [''], 'OCSVM_degree': [''], 'OCSVM_gamma': [''],
                     'OCSVM_coef0': [''], 'OCSVM_tol': [''], 'OCSVM_nu': [''], 'OCSVM_shrinking': [''],
                     'OCSVM_cache_size': [''], 'OCSVM_verbose': [''], 'OCSVM_max_iter': [''],
                     'OCSVM_contamination': [''], 'PCA_n_components': [''], 'PCA_n_selected_components': [''],
                     'PCA_contamination': [''], 'PCA_copy': [''], 'PCA_whiten': [''], 'PCA_svd_solver': [''],
                     'PCA_tol': [''], 'PCA_iterated_power': [''], 'PCA_random_state': [''], 'PCA_weighted': [''],
                     'PCA_standardization': [''], 'RGraph_transition_steps': [''], 'RGraph_n_nonzero': [''],
                     'RGraph_gamma': [''], 'RGraph_gamma_nz': [''], 'RGraph_algorithm': [''], 'RGraph_tau': [''],
                     'RGraph_maxiter_lasso': [''], 'RGraph_preprocessing': [''], 'RGraph_contamination': [''],
                     'RGraph_blocksize_test_data': [''], 'RGraph_support_init': [''], 'RGraph_maxiter': [''],
                     'RGraph_support_size': [''], 'RGraph_active_support': [''], 'RGraph_fit_intercept_LR': [''],
                     'RGraph_verbose': [''], 'ROD_contamination': [''], 'ROD_parallel_execution': [''],
                     'Sampling_contamination': [''], 'Sampling_subset_size': [''], 'Sampling_metric': [''],
                     'Sampling_metric_params': [''], 'Sampling_random_state': ['']}

    def tearDown(self):
        self.file.close()
        self.gt.close()
        self.gen.close()

        for path in ["test_data.csv", self.path_input, self.path_gt, self.path_gen]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    pass

        for e in Experiments.objects.all():
            e.delete()
        for u in Users.objects.all():
            u.delete()

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def test_session(self):
        user = Users.objects.filter(username="tester3").first()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_page_status_code(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/configuration/')
        self.assertEqual(view.func.view_class, experiment.views.ConfigView)

    def test_csrf(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertContains(response_get, 'csrfmiddlewaretoken')
        print(response_get.context['csrf_token'])

    def test_template_used(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertTemplateUsed(response_get, 'configuration.html')

    '''---------------------------   Basic URL tests for GET    ---------------------------'''

    def test_get_not_existed_id(self):
        response_get = self.client.get(self.url, data={'id': 1000000})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'error404.html')

    def test_get_not_authorized_id(self):
        client = Client()
        user = Users.objects.create(username='tester4', password='123')
        session = client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = client.post('/login/')
        self.assertEqual(response.status_code, 200)

        response_get = client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'error401.html')

    def test_get_editing_experiment(self):
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'configuration.html')

        # check that the context contains the expected objects
        self.assertEqual(response_get.context['exp'], self.exp)
        self.assertIsNotNone(response_get.context['form'])
        self.assertIsNotNone(response_get.context['odms'])

    def test_get_failed_experiment(self):
        data = self.data.copy()
        data['ABOD_contamination'] = '100000'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.failed)
        self.assertIsNotNone(exp.error)

        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'configuration.html')

        # check that the context contains the expected objects
        self.assertEqual(response_get.context['exp'], self.exp)
        self.assertIsNotNone(response_get.context['form'])
        self.assertIsNotNone(response_get.context['odms'])

    '''---------------------------   Basic URL tests for POST with valid form   ---------------------------'''

    def test_post_valid_form_with_subspace_option_1(self):
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=self.data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.operation_option, "1")

    def test_post_valid_form_with_subspace_option_2(self):
        data = self.data.copy()
        data['operation_model_options'] = '2'
        data['operation_except'] = '1'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.operation_option, "2")

    def test_post_valid_form_with_subspace_option_3(self):
        data = self.data.copy()
        data['operation_model_options'] = '3'
        data['operation_written'] = '{1,2}'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.operation_option, "3")

    def test_post_valid_form_with_gt_file(self):
        data = self.data.copy()
        # data["ground_truth"] = SimpleUploadedFile("test_data.csv", b"ground_truth\n1\n0\n")
        data["ground_truth"] = self.gt
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.operation_option, "1")
        self.assertTrue(exp.has_ground_truth)

    def test_post_valid_form_with_add_file(self):
        data = self.data.copy()
        # data["generated_file"] = SimpleUploadedFile("test_data.csv", b"column1,column2,column3\n1,2,3\n4,5,6\n")
        data["generated_file"] = self.gen
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.operation_option, "1")
        self.assertTrue(exp.has_generated_file)

    '''---------------------------   Basic URL tests for POST with invalid form    ---------------------------'''

    def test_post_invalid_form_with_no_data(self):
        data = {}
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(f'{self.url}?{query_string}', data=data)

        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'configuration.html')
        self.assertEqual(response_post.context['exp'], self.exp)
        self.assertIsNotNone(response_post.context['form'])
        self.assertIsNotNone(response_post.context['odms'])
        self.assertTrue(response_post.context['form'].errors)
        self.assertIn('This field is required.', response_post.context['form'].errors['ground_truth_options'])
        self.assertIn('This field is required.', response_post.context['form'].errors['operation_model_options'])

    def test_post_invalid_form_with_subspace_option_2_but_no_operation(self):
        data = self.data.copy()
        data['operation_model_options'] = '2'
        data['operation_except'] = ''
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertTemplateUsed(response_post, "configuration.html")

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        self.assertIsNone(exp.operation_option)
        self.assertTrue(response_post.context['form'].errors)
        self.assertIn('Please enter your excluded subspaces.', response_post.context['form'].errors['operation_except'])

    def test_post_invalid_form_with_subspace_option_2_but_invalid_operation(self):
        data = self.data.copy()
        data['operation_model_options'] = '2'
        data['operation_except'] = 'abc'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertTemplateUsed(response_post, "configuration.html")

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        self.assertIsNone(exp.operation_option)
        self.assertTrue(response_post.context['form'].errors)
        print("response_post.context['form'].errors: ", response_post.context['form'].errors)
        self.assertIn('Please enter your excluded subspaces in correct format.',
                      response_post.context['form'].errors['operation_except'])

    def test_post_invalid_form_with_subspace_option_3_but_no_operation(self):
        data = self.data.copy()
        data['operation_model_options'] = '3'
        data['operation_written'] = ''
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertTemplateUsed(response_post, "configuration.html")

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        self.assertIsNone(exp.operation_option)
        self.assertTrue(response_post.context['form'].errors)
        print("response_post.context['form'].errors: ", response_post.context['form'].errors)
        self.assertIn("Please enter your subspace combination.",
                      response_post.context['form'].errors["operation_written"])

    def test_post_invalid_form_with_subspace_option_3_but_invalid_operation(self):
        data = self.data.copy()
        data['operation_model_options'] = '3'
        data['operation_written'] = 'abc'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertTemplateUsed(response_post, "configuration.html")

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        self.assertIsNone(exp.operation_option)

    def test_post_invalid_form_with_wrong_parameter_type(self):
        data = self.data.copy()
        data['ABOD_n_neighbors'] = 'abc'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertTemplateUsed(response_post, "configuration.html")

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        self.assertIsNone(exp.operation_option)
        self.assertTrue(response_post.context['form'].errors)
        print("response_post.context['form'].errors: ", response_post.context['form'].errors)
        self.assertIn("Input error by ABOD_n_neighbors: invalid literal for int() with base 10: 'abc'",
                      response_post.context['form'].errors['__all__'])

    def test_post_invalid_form_with_invalid_parameter(self):
        data = self.data.copy()
        data['ABOD_contamination'] = '100000'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(0.2)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.failed)
        self.assertEqual(exp.operation_option, "1")
        self.assertTrue(exp.error)
        self.assertIn("contamination must be in (0, 0.5], got: 100000.000000", exp.error)

    '''---------------------------   Basic URL tests for POST with all odms   ---------------------------'''

    def setting_for_all_odms(self, odm_name):
        print("odm_pick: ", odm_name)
        odms = get_odm_dict()
        index = list(odms.keys()).index(odm_name) + 1

        # In order to meet the default parameters of Sampling, the number of data points must be greater than 20.
        with open('test_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['x', 'y', 'z'])
            writer.writerow(['10', '25', '30'])
            writer.writerow(['20', '30', '40'])
            writer.writerow(['30', '35', '50'])
            writer.writerow(['40', '40', '60'])
            writer.writerow(['5', '45', '70'])
            writer.writerow(['6', '50', '80'])
            writer.writerow(['7', '55', '90'])
            writer.writerow(['8', '60', '100'])
            writer.writerow(['10', '2', '30'])
            writer.writerow(['20', '3', '40'])
            writer.writerow(['30', '4', '50'])
            writer.writerow(['40', '5', '60'])
            writer.writerow(['5', '45', '7'])
            writer.writerow(['6', '50', '8'])
            writer.writerow(['7', '55', '9'])
            writer.writerow(['8', '60', '10'])
            writer.writerow(['50', '45', '7'])
            writer.writerow(['60', '50', '8'])
            writer.writerow(['70', '55', '9'])
            writer.writerow(['80', '60', '10'])

        with open('test_data.csv', 'rb') as file:
            csv_file = SimpleUploadedFile(file.name, file.read(), content_type='text/csv')

        data = {
            'run_name': 'New Experiment',
            'main_file': csv_file,
        }
        url = reverse('main')
        response = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(run_name='New Experiment').first()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True, "id": self.exp.id})

        data = self.data.copy()
        data['odms'] = str(index)
        data['operation_model_options'] = '3'
        if odm_name == "MAD":
            data['operation_written'] = '{1}'
        else:
            data['operation_written'] = '{1,2}'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

    def test_post_valid_form_with_all_odms(self):
        for odm in get_odm_dict().keys():
            self.setting_for_all_odms(odm)
            # Wait for the end of the detector thread
            time.sleep(4)
            exp = FinishedExperiments.objects.get(id=self.exp.id)
            self.assertEqual(exp.state, Experiment_state.finished)
            self.assertEqual(exp.odm, odm)

    def test_post_invalid_form_with_LUNAR_but_invalid_scaler(self):
        odms = get_odm_dict()
        index = list(odms.keys()).index("LUNAR") + 1

        data = self.data.copy()
        data['odms'] = str(index)
        data['LUNAR_scaler'] = 'InvalidScaler()'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertEqual(response_post.status_code, 200)
        self.assertTemplateUsed(response_post, 'configuration.html')
        # Wait for the end of the detector thread

        time.sleep(3)
        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.editing)
        error = "Input error by LUNAR_scaler: parameter scaler must be one of StandardScaler() and MinMaxScaler()."
        self.assertIn(error, response_post.context['form'].errors['__all__'])

    def test_post_valid_form_with_LUNAR_using_manual_input_1(self):
        odms = get_odm_dict()
        index = list(odms.keys()).index("LUNAR") + 1

        data = self.data.copy()
        data['odms'] = str(index)
        data['LUNAR_n_neighbours'] = '1'
        data['LUNAR_scaler'] = 'MinMaxScaler()'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(10)

        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.odm, "LUNAR")

    def test_post_valid_form_with_LUNAR_using_manual_input_2(self):
        odms = get_odm_dict()
        index = list(odms.keys()).index("LUNAR") + 1

        data = self.data.copy()
        data['odms'] = str(index)
        data['LUNAR_n_neighbours'] = '1'
        data['LUNAR_scaler'] = 'StandardScaler()'
        query_string = urlencode({'id': self.exp.id})
        response_post = self.client.post(self.url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, self.successful_url, status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(10)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertEqual(exp.odm, "LUNAR")


class ResultViewTest(TransactionTestCase):
    fixtures = ['user_tests.json']
    path_input = "input.csv"
    path_gt = "gt.csv"
    path_gen = "gen.csv"

    def setUp(self):
        '''--------------------------- generate files ---------------------------'''
        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        training_data = list(training_data)
        training_data.insert(0, ["x1", "x2", "x3"])
        gt_list = []
        for row in train_gt:
            gt_list.append([row])

        odm_handling.write_data_to_csv(self.path_input, training_data)
        odm_handling.write_data_to_csv(self.path_gt, gt_list)
        odm_handling.write_data_to_csv(self.path_gen, test_data)

        self.file = open(self.path_input, 'r', encoding='UTF-8')
        self.gt = open(self.path_gt, 'r', encoding='UTF-8')
        self.gen = open(self.path_gen, 'r', encoding='UTF-8')

        '''--------------------------- logged in ---------------------------'''
        user = Users.objects.create(username='tester3', password='123', id=0)
        session = self.client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = self.client.post('/login/')
        self.assertEqual(response.status_code, 200)

        '''--------------------------- create a folder and put the csv file in it ---------------------------'''

        data = {
            'run_name': 'Test Experiment',
            'main_file': self.file,
        }
        url = reverse('main')
        response = self.client.post(url, data, follow=True)
        self.exp = PendingExperiments.objects.filter(run_name='Test Experiment').first()
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"status": True, "id": self.exp.id})

        '''--------------------------- go into configuration ---------------------------'''

        self.data = {'operation_model_options': ['1'], 'operation_except': [''], 'operation_written': [''],
                    'ground_truth_options': ['1'], 'odms': ['1'], 'ABOD_contamination': [''],
                    'ABOD_n_neighbors': [''], 'ABOD_method': [''], 'CBLOF_n_clusters': [''],
                    'CBLOF_contamination': [''], 'CBLOF_clustering_estimator': [''], 'CBLOF_alpha': [''],
                    'CBLOF_beta': [''], 'CBLOF_use_weights': [''], 'CBLOF_check_estimator': [''],
                    'CBLOF_random_state': [''], 'CBLOF_n_jobs': [''], 'COF_contamination': [''],
                    'COF_n_neighbors': [''], 'COF_method': [''], 'COPOD_contamination': [''], 'COPOD_n_jobs': [''],
                    'ECOD_contamination': [''], 'ECOD_n_jobs': [''], 'FeatureBagging_base_estimator': [''],
                    'FeatureBagging_n_estimators': [''], 'FeatureBagging_contamination': [''],
                    'FeatureBagging_max_features': [''], 'FeatureBagging_bootstrap_features': [''],
                    'FeatureBagging_check_detector': [''], 'FeatureBagging_check_estimator': [''],
                    'FeatureBagging_n_jobs': [''], 'FeatureBagging_random_state': [''],
                    'FeatureBagging_combination': [''], 'FeatureBagging_verbose': [''],
                    'FeatureBagging_estimator_params': [''], 'GMM_n_components': [''],
                    'GMM_covariance_type': [''], 'GMM_tol': [''], 'GMM_reg_covar': [''], 'GMM_max_iter': [''],
                    'GMM_n_init': [''], 'GMM_init_params': [''], 'GMM_weights_init': [''], 'GMM_means_init': [''],
                    'GMM_precisions_init': [''], 'GMM_random_state': [''], 'GMM_warm_start': [''],
                    'GMM_contamination': [''], 'HBOS_n_bins': [''], 'HBOS_alpha': [''], 'HBOS_tol': [''],
                    'HBOS_contamination': [''], 'IForest_n_estimators': [''], 'IForest_max_samples': [''],
                    'IForest_contamination': [''], 'IForest_max_features': [''], 'IForest_bootstrap': [''],
                    'IForest_n_jobs': [''], 'IForest_behaviour': [''], 'IForest_random_state': [''],
                    'IForest_verbose': [''], 'INNE_n_estimators': [''], 'INNE_max_samples': [''],
                    'INNE_contamination': [''], 'INNE_random_state': [''], 'KDE_contamination': [''],
                    'KDE_bandwidth': [''], 'KDE_algorithm': [''], 'KDE_leaf_size': [''], 'KDE_metric': [''],
                    'KDE_metric_params': [''], 'KPCA_contamination': [''], 'KPCA_n_components': [''],
                    'KPCA_n_selected_components': [''], 'KPCA_kernel': [''], 'KPCA_gamma': [''], 'KPCA_degree': [''],
                    'KPCA_coef0': [''], 'KPCA_kernel_params': [''], 'KPCA_alpha': [''], 'KPCA_eigen_solver': [''],
                    'KPCA_tol': [''], 'KPCA_max_iter': [''], 'KPCA_remove_zero_eig': [''], 'KPCA_copy_X': [''],
                    'KPCA_n_jobs': [''], 'KPCA_sampling': [''], 'KPCA_subset_size': [''], 'KPCA_random_state': [''],
                    'LMDD_contamination': [''], 'LMDD_n_iter': [''], 'LMDD_dis_measure': [''],
                    'LMDD_random_state': [''], 'LODA_contamination': [''], 'LODA_n_bins': [''],
                    'LODA_n_random_cuts': [''], 'LOF_n_neighbors': [''], 'LOF_algorithm': [''], 'LOF_leaf_size': [''],
                    'LOF_metric': [''], 'LOF_p': [''], 'LOF_metric_params': [''], 'LOF_contamination': [''],
                    'LOF_n_jobs': [''], 'LOF_novelty': [''], 'LOCI_contamination': [''], 'LOCI_alpha': [''],
                    'LOCI_k': [''], 'LUNAR_model_type': [''], 'LUNAR_n_neighbours': [''],
                    'LUNAR_negative_sampling': [''], 'LUNAR_val_size': [''], 'LUNAR_scaler': [''],
                    'LUNAR_epsilon': [''], 'LUNAR_proportion': [''], 'LUNAR_n_epochs': [''], 'LUNAR_lr': [''],
                    'LUNAR_wd': [''], 'LUNAR_verbose': [''], 'MAD_threshold': [''], 'MCD_contamination': [''],
                    'MCD_store_precision': [''], 'MCD_assume_centered': [''], 'MCD_support_fraction': [''],
                    'MCD_random_state': [''], 'OCSVM_kernel': [''], 'OCSVM_degree': [''], 'OCSVM_gamma': [''],
                    'OCSVM_coef0': [''], 'OCSVM_tol': [''], 'OCSVM_nu': [''], 'OCSVM_shrinking': [''],
                    'OCSVM_cache_size': [''], 'OCSVM_verbose': [''], 'OCSVM_max_iter': [''],
                    'OCSVM_contamination': [''], 'PCA_n_components': [''], 'PCA_n_selected_components': [''],
                    'PCA_contamination': [''], 'PCA_copy': [''], 'PCA_whiten': [''], 'PCA_svd_solver': [''],
                    'PCA_tol': [''], 'PCA_iterated_power': [''], 'PCA_random_state': [''], 'PCA_weighted': [''],
                    'PCA_standardization': [''], 'RGraph_transition_steps': [''], 'RGraph_n_nonzero': [''],
                    'RGraph_gamma': [''], 'RGraph_gamma_nz': [''], 'RGraph_algorithm': [''], 'RGraph_tau': [''],
                    'RGraph_maxiter_lasso': [''], 'RGraph_preprocessing': [''], 'RGraph_contamination': [''],
                    'RGraph_blocksize_test_data': [''], 'RGraph_support_init': [''], 'RGraph_maxiter': [''],
                    'RGraph_support_size': [''], 'RGraph_active_support': [''], 'RGraph_fit_intercept_LR': [''],
                    'RGraph_verbose': [''], 'ROD_contamination': [''], 'ROD_parallel_execution': [''],
                    'Sampling_contamination': [''], 'Sampling_subset_size': [''], 'Sampling_metric': [''],
                    'Sampling_metric_params': [''], 'Sampling_random_state': ['']}

        self.url = reverse('result')

    def tearDown(self):
        self.file.close()
        self.gt.close()
        self.gen.close()

        for path in [self.path_input, self.path_gt, self.path_gen]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    pass

        for e in Experiments.objects.all():
            e.delete()
        for u in Users.objects.all():
            u.delete()

    '''--------------------------- Test Fixture Loading ---------------------------'''

    def test_fixtures(self):
        user = Users.objects.get(id=1)
        self.assertEqual(user.username, 'tester1')

    '''---------------------------   Basic URL tests    ---------------------------'''

    def basic_protreatment(self):
        url = reverse('configuration')
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(url + f'?{query_string}', data=self.data)
        self.assertRedirects(response_post, reverse('main'), status_code=302, target_status_code=200)
        time.sleep(2)

    def test_session(self):
        self.basic_protreatment()
        user = Users.objects.filter(username="tester3").first()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.client.session['info'], {'id': user.id, 'username': user.username})

    def test_page_status_code(self):
        self.basic_protreatment()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)

    def test_register_url_resolves_registration_view(self):
        view = resolve('/result/')
        self.assertEqual(view.func.view_class, experiment.views.ResultView)

    def test_csrf(self):
        self.basic_protreatment()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertIsNotNone(response_get.context['csrf_token'])


    def test_template_used(self):
        self.basic_protreatment()
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertTemplateUsed(response_get, 'result.html')

    '''---------------------------   Basic URL tests for GET    ---------------------------'''

    def test_get_pending_experiment(self):
        odms = get_odm_dict()
        index = list(odms.keys()).index("LUNAR") + 1

        data = self.data.copy()
        data['odms'] = str(index)
        data['LUNAR_n_neighbours'] = '1'
        data['LUNAR_scaler'] = 'MinMaxScaler()'
        url = reverse('configuration')
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, reverse('main'), status_code=302, target_status_code=200)

        exp = PendingExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.pending)
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'result.html')
        self.assertContains(response_get, self.exp.id)

        time.sleep(10)

    def test_get_finished_experiment(self):
        self.basic_protreatment()

        # Wait for the end of the detector thread
        time.sleep(3)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'result.html')
        self.assertContains(response_get, self.exp.id)

    def test_get_finished_experiment_with_add(self):
        data = self.data.copy()
        data["generated_file"] = self.gen
        url = reverse('configuration')
        params = {'id': self.exp.id}
        query_string = urlencode(params)
        response_post = self.client.post(url + f'?{query_string}', data=data)
        self.assertRedirects(response_post, reverse('main'), status_code=302, target_status_code=200)

        # Wait for the end of the detector thread
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)
        self.assertTrue(exp.has_generated_file)
        response_get = self.client.get(self.url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'result.html')
        self.assertContains(response_get, self.exp.id)

    def test_get_nonexistent_experiment(self):
        url = reverse('result')
        response_get = self.client.get(url, {'id': 123456})  # use a nonexistent experiment id
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'error404.html')

    def test_get_unarthorized_experiment(self):
        self.basic_protreatment()
        time.sleep(2)
        exp = FinishedExperiments.objects.get(id=self.exp.id)
        self.assertEqual(exp.state, Experiment_state.finished)

        client = Client()
        user = Users.objects.create(username='tester1')
        session = client.session
        session['info'] = {'id': user.id, 'username': user.username}
        session.save()
        response = client.post('/login/')
        self.assertEqual(response.status_code, 200)

        url = reverse('result')
        response_get = client.get(url, data={'id': self.exp.id})
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'error401.html')
