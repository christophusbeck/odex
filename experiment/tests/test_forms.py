import csv
import os

from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from experiment.forms import CreateForm, ConfigForm


class CreateFormTest(TestCase):
    def tearDown(self):
        path = "test_data.csv"
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                pass
    def test_form_valid(self):
        file = SimpleUploadedFile(
            "testfile.csv",
            b"col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n10,11,12",
            content_type="text/csv"
        )
        form = CreateForm(data={'run_name': 'testexperiment'}, files={'main_file': file})
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_missing_fields(self):
        form = CreateForm(data={})
        self.assertFalse(form.is_valid())
        print(form.errors)
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
