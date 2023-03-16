from django.test import TestCase
from experiment.forms import CreateForm, ConfigForm


class CreateFormTest(TestCase):
    def test_form_valid(self):
        form = CreateForm(data={'run_name': 'testexperiment'})
        self.assertTrue(form.is_valid())

    def test_form_missing_fields(self):
        form = CreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('run_name', form.errors.keys())
        self.assertIn('main_file', form.errors.keys())


class ConfigFormTest(TestCase):
    def test_form_valid(self):
        form = ConfigForm(data={
            'operation_except': '1,2,3',
            'operation_written': '{1,2}&{1,3}',
            'ground_truth_options': '1',
            'operation_model_options': '1',
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_fields(self):
        form = ConfigForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('ground_truth_options', form.errors.keys())
        self.assertIn('operation_model_options', form.errors.keys())

    def test_form_invalid_fields(self):
        form = ConfigForm(data={
            'operation_except': '1,2,3',
            'operation_written': '{1,2}&{1,3}',
            'ground_truth_options': '3',  # invalid value
            'operation_model_options': '4',  # invalid value
        })
        self.assertFalse(form.is_valid())
        self.assertIn('ground_truth_options', form.errors.keys())
        self.assertIn('operation_model_options', form.errors.keys())
