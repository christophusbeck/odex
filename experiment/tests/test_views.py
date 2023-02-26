
from unittest.mock import MagicMock

from experiment.models import Users, Experiments, FinishedExperiments
from experiment.forms import CreateForm

from django.test import Client
from django.urls import reverse
from myapp import models

from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from experiment.views import Configuration
from experiment.models import PendingExperiments

class ConfigurationViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_post_with_valid_data(self):
        # Create a PendingExperiments object for the test
        exp = PendingExperiments.objects.create(name="test_exp")
        # Create a valid POST request with the necessary data
        file_data = b"id,name,value\n1,foo,42\n2,bar,7\n"
        uploaded_file = SimpleUploadedFile("data.csv", file_data)
        request = self.factory.post("/configuration?id=%d" % exp.id, {
            "odms": "1",
            "operation_model_options": "2",
            "operation_except": "name",
        }, FILES={
            "ground_truth": uploaded_file,
        })
        # Call the view and check that the PendingExperiments object was updated correctly
        response = Configuration.as_view()(request)
        exp.refresh_from_db()
        self.assertEqual(exp.operation, "name")
        self.assertEqual(exp.odm, "odm1")
        self.assertEqual(exp.has_ground_truth, True)
        self.assertEqual(exp.state, "pending")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/main/")

    def test_invalid_config_error_message(self):
        # create an invalid configuration
        invalid_config = {'option1': 'value1', 'option2': 'value2'}

        # set the session with the invalid configuration
        self.client.session['config'] = invalid_config
        self.client.session.save()

        # make a GET request to the configuration view
        response = self.client.get(reverse('config'))

        # check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # check that the response contains an error message
        self.assertContains(response, 'Invalid configuration')

    def test_valid_config_values_displayed(self):
        # create a valid configuration
        valid_config = {'option1': 'value1', 'option2': 'value2', 'option3': 'value3'}

        # set the session with the valid configuration
        self.client.session['config'] = valid_config
        self.client.session.save()

        # make a GET request to the configuration view
        response = self.client.get(reverse('config'))

        # check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # check that the response contains the correct values for each option
        self.assertContains(response, 'value1')
        self.assertContains(response, 'value2')
        self.assertContains(response, 'value3')
    def test_save_config_changes(self):
        # create a valid configuration
        valid_config = {'option1': 'value1', 'option2': 'value2', 'option3': 'value3'}

        # set the session with the valid configuration
        self.client.session['config'] = valid_config
        self.client.session.save()

        # make a POST request to the configuration view with updated values
        updated_config = {'option1': 'new_value1', 'option2': 'new_value2', 'option3': 'new_value3'}
        response = self.client.post(reverse('config'), data=updated_config)

        # check that the response status code is a redirect (302)
        self.assertEqual(response.status_code, 302)

        # check that the session was updated with the new configuration
        self.assertEqual(self.client.session['config'], updated_config)


    def test_missing_config_option(self):
        # create a configuration with a missing option
        config = {'option1': 'value1', 'option2': 'value2'}

        # set the session with the invalid configuration
        self.client.session['config'] = config
        self.client.session.save()

        # make a GET request to the configuration view
        response = self.client.get(reverse('config'))

        # check that the response status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # check that the missing option is displayed with a default value
        self.assertContains(response, 'value1')
        self.assertContains(response, 'value2')
        self.assertContains(response, 'default_value', 1)


class DeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Users.objects.create(username='test_user')
        self.experiment = Experiments.objects.create(user=self.user)

    def test_delete_experiment(self):
        response = self.client.get(reverse('delete') + f'?id={self.experiment.id}')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Experiments.objects.filter(id=self.experiment.id).exists())

    def tearDown(self):
        self.user.delete()


class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Users.objects.create(username='testuser')
        self.client.force_login(self.user)
        self.form_data = {
            'run_name': 'Test Experiment',
            'main_file': SimpleUploadedFile("test_data.csv", b"file_content"),
        }
        self.url = reverse('main-view')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')
        self.assertIsInstance(response.context['form'], CreateForm)

    def test_post_valid_form(self):
        with MagicMock() as mock_pending_save:
            PendingExperiments.save = mock_pending_save
            response = self.client.post(self.url, data=self.form_data)
            pending_exp = PendingExperiments.objects.get(id=response.json()['id'])
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['status'])
            self.assertEqual(pending_exp.user, self.user)
            self.assertEqual(pending_exp.run_name, self.form_data['run_name'])
            self.assertEqual(pending_exp.file_name, self.form_data['main_file'].name)
            self.assertEqual(pending_exp.state, 'editing')
            self.assertEqual(pending_exp.main_file.read(), b"file_content")
            self.assertEqual(pending_exp.get_columns(), ['file_content'])
            mock_pending_save.assert_called_once()

    def test_post_invalid_form(self):
        invalid_data = self.form_data.copy()
        invalid_data['main_file'] = 'invalid_file.csv'
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['status'])
        self.assertIn('main_file', response.json()['error'])
        self.assertIn('Unsupported file', response.json()['error']['main_file'][0])

class ResultViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.exp = Experiments.objects.create()  # create an experiment object for testing

    def test_get_pending_exp(self):
        self.exp.state = 'pending'
        self.exp.save()
        url = reverse('result_url') + '?id=' + str(self.exp.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        self.assertEqual(response.context['exp'], self.exp)
        self.assertEqual(response.context['columns'], self.exp.get_columns())
        self.assertEqual(response.context['paras'], self.exp.get_para())

    def test_get_finished_exp(self):
        self.exp.state = 'finished'
        self.exp.save()
        FinishedExperiments.objects.create(experiment=self.exp)  # create a finished experiment object for testing
        url = reverse('result_url') + '?id=' + str(self.exp.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        self.assertEqual(response.context['exp'], self.exp)
        self.assertEqual(response.context['columns'], self.exp.get_columns())
        self.assertEqual(response.context['paras'], self.exp.get_para())
        self.assertEqual(response.context['outliers'], self.exp.get_metrics()['Detected Outliers'])
        self.assertEqual(response.context['performance'], dict((key, value) for key, value in self.exp.get_metrics().items() if key != "Detected Outliers" and key != "Detected Outliers after merging with generated data"))

    def test_get_finished_exp_with_generated_file(self):
        self.exp.state = 'finished'
        self.exp.has_generated_file = True
        self.exp.save()
        FinishedExperiments.objects.create(experiment=self.exp)  # create a finished experiment object for testing
        url = reverse('result_url') + '?id=' + str(self.exp.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'result.html')
        self.assertEqual(response.context['exp'], self.exp)
        self.assertEqual(response.context['columns'], self.exp.get_columns())
        self.assertEqual(response.context['paras'], self.exp.get_para())
        self.assertEqual(response.context['outliers'], self.exp.get_metrics()['Detected Outliers'])
        self.assertEqual(response.context['performance'], dict(
            (key, value) for key, value in self.exp.get_metrics().items() if key != "Detected Outliers"))

    def test_redirect_to_configuration(self):
        self.exp.state = 'other_state'
        self.exp.save()
        url = reverse('result_url') + '?id=' + str(self.exp.id)
        response = self.client.get(url)
        self.assertRedirects(response, '/configuration/?id=' + str(self.exp.id), fetch_redirect_response=False)
