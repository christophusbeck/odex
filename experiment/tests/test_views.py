from django.test import TestCase, Client
from django.urls import reverse
from myapp import models


class ResultViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.exp = models.Experiments.objects.create()  # create an experiment object for testing

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
        models.FinishedExperiments.objects.create(experiment=self.exp)  # create a finished experiment object for testing
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
        models.FinishedExperiments.objects.create(experiment=self.exp)  # create a finished experiment object for testing
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
