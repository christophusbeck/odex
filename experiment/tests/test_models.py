import json
import os

import numpy as np
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from datetime import timedelta, datetime
import pytz

from user.models import Users
from experiment.models import Experiments, Experiment_state, PendingExperiments, FinishedExperiments, user_roc_path


class ExperimentsBaseTest(TestCase):
    @classmethod
    def setUp(cls):
        timezone = pytz.timezone('Europe/Berlin')
        cls.data1 = timezone.localize(datetime(
            year=2023,
            month=3,
            day=10,
            hour=22,
            minute=22,
            second=22,
            microsecond=222222
        ))
        cls.data2 = timezone.localize(datetime(
            year=2023,
            month=3,
            day=10,
            hour=23,
            minute=23,
            second=23,
            microsecond=333333
        ))
        cls.delta = timedelta(
            days=0,
            seconds=0,
            microseconds=100,
            milliseconds=290,
            minutes=0,
            hours=0,
            weeks=0
        )

        # create a user to use in the test
        cls.user = Users.objects.create(username='testuser', password='testpass')


class ExperimentsTest(ExperimentsBaseTest):
    @classmethod
    def setUp(cls):
        super().setUp()

        # create an experiment to use in the test
        basic_experiment = Experiments.objects.create(
            user=cls.user,
            run_name='basic testexperiment',
            file_name='basic_testfile.csv',
            state=Experiment_state.editing
        )

        experiment = Experiments.objects.create(
            user=cls.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            created_time=cls.data1,
            start_time=cls.data2,
            duration=cls.delta,
            operation_option='2',
            has_ground_truth=True,
            has_generated_file=True
        )

    def test_basic_experiment_has_user(self):
        basic_experiment = Experiments.objects.get(run_name='basic testexperiment')
        self.assertEqual(basic_experiment.user.username, 'testuser')

    def test_basic_experiment_has_run_name(self):
        basic_experiment = Experiments.objects.get(file_name='basic_testfile.csv')
        self.assertEqual(basic_experiment.run_name, 'basic testexperiment')

    def test_experiment_has_user(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.user.username, 'testuser')

    def test_experiment_has_run_name(self):
        experiment = Experiments.objects.get(file_name='testfile.csv')
        self.assertEqual(experiment.run_name, 'testexperiment')

    def test_experiment_has_state(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.state, 'editing')

    def test_experiment_has_odm(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.odm, 'testodm')

    def test_experiment_has_operation(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.operation, 'testoperation')

    def test_experiment_has_columns(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.get_columns(), {"testcolumn1": "6.433658544295", "testcolumn2": "5.509168303351"})

    def test_experiment_has_parameters(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.get_para(), {"testparam1": 1, "testparam2": 2})

    def test_experiment_has_created_time(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        print(experiment.created_time)
        self.assertEqual(experiment.created_time.strftime('%Y-%m-%d %H:%M:%S.%f'), '2023-03-10 21:22:22.222222')

    def test_experiment_has_start_time(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.start_time.strftime('%Y-%m-%d %H:%M:%S.%f'), '2023-03-10 22:23:23.333333')

    def test_experiment_has_duration(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.duration.microseconds, 290100)

    def test_experiment_has_operation_option(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.operation_option, '2')
        self.assertEqual(experiment.get_operation_option_display(), "All, except")

    def test_experiment_has_ground_truth(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.has_ground_truth, True)

    def test_experiment_has_generated_file(self):
        experiment = Experiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.has_generated_file, True)

    def test_experiment_invalid_state(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state='invalid_state'  # Invalid state value
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_invalid_operation_option(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
            operation_option='invalid_option'  # Invalid operation option value
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_no_user(self):
        with self.assertRaises(IntegrityError):
            Experiments.objects.create(
                # No user provided
                run_name='testexperiment',
                file_name='testfile.csv',
                state=Experiment_state.editing,
            )

    def test_experiment_no_run_name(self):
        experiment = Experiments.objects.create(
            user=self.user,
            # No run_name provided
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_no_file_name(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            # No file_name provided
            state=Experiment_state.editing,
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_no_state(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            # No state provided
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_no_created_time(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.created_time)

    def test_experiment_no_start_time(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.start_time)

    def test_experiment_no_duration(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.duration)

    def test_experiment_no_odm(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.odm)

    def test_experiment_no_operation(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.operation)

    def test_experiment_no_operation_option(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.operation_option)

    def test_experiment_no_has_ground_truth(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertFalse(experiment.has_ground_truth)

    def test_experiment_no_has_generated_file(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertFalse(experiment.has_generated_file)

    def test_experiment_no_columns(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.columns)

    def test_experiment_no_parameters(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
        )
        self.assertIsNone(experiment.parameters)

    def test_experiment_set_columns(self):
        columns = {"testcolumn1": 6.433658544295, "testcolumn2": 5.509168303351}
        experiment = Experiments.objects.get(run_name='testexperiment')
        experiment.set_columns(columns)
        self.assertEqual(experiment.columns, json.dumps(columns))


class PendingExperimentsTest(ExperimentsBaseTest):
    @classmethod
    def setUp(cls):
        super().setUp()

        # create a file to use in the test
        cls.file = SimpleUploadedFile(
            "testfile.csv",
            b"col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n10,11,12",
            content_type="text/csv"
        )
        cls.addfile = SimpleUploadedFile(
            "testaddfile.csv",
            b"col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n10,11,12",
            content_type="text/csv"
        )
        cls.gtfile = SimpleUploadedFile(
            "testgtfile.csv",
            b"gt\n1\n1\n1\n1",
            content_type="text/csv"
        )
        cls.invalid_file = SimpleUploadedFile(
            "testfile.pdf",
            b"col1,col2,col3\n1,2,3\n4,5,6\n7,8,9\n10,11,12",
            content_type="application/pdf"
        )

        # create a PendingExperiments object to use in the test
        pending_experiment = PendingExperiments.objects.create(
            user=cls.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.pending,
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            created_time=cls.data1,
            start_time=cls.data2,
            duration=cls.delta,
            operation_option='2',
            has_ground_truth=True,
            has_generated_file=True,
            main_file=cls.file,
            generated_file=cls.addfile,
            ground_truth=cls.gtfile,
            error="testerror",
        )

    def test_pending_experiment_user(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.user, self.user)

    def test_pending_experiment_run_name(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.run_name, 'testexperiment')

    def test_pending_experiment_file_name(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.file_name, 'testfile.csv')

    def test_pending_experiment_state(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.state, Experiment_state.pending)

    def test_pending_experiment_odm(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.odm, 'testodm')

    def test_pending_experiment_operation(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.operation, 'testoperation')

    def test_pending_experiment_columns(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.get_columns(), {"testcolumn1": "6.433658544295", "testcolumn2": "5.509168303351"})

    def test_pending_experiment_parameters(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.get_para(), {"testparam1": 1, "testparam2": 2})

    def test_pending_experiment_created_time(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.created_time, self.data1)

    def test_pending_experiment_start_time(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.start_time, self.data2)

    def test_pending_experiment_duration(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.duration, self.delta)

    def test_pending_experiment_operation_option(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.operation_option, '2')

    def test_pending_experiment_has_ground_truth(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.has_ground_truth, True)

    def test_pending_experiment_has_generated_file(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.has_generated_file, True)

    def test_pending_experiment_error(self):
        experiment = PendingExperiments.objects.get(id=1)
        self.assertEqual(experiment.error, "testerror")

    def test_pending_experiment_missing_required_fields(self):
        experiment = PendingExperiments(user_id=1)
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_pending_experiment_valid(self):
        experiment = PendingExperiments(
            user_id=1,
            run_name='test experiment',
            file_name='testfile.csv',
            state=Experiment_state.pending,
            main_file=self.file
        )
        experiment.full_clean()  # should pass validation

    def test_pending_experiment_file_extension_validation(self):
        experiment = PendingExperiments(
            user_id=1,
            run_name='test experiment',
            file_name='testfile.pdf',
            state=Experiment_state.pending,
            main_file=self.invalid_file
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_pending_experiment_file_upload(self):
        experiment = PendingExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.main_file)
        self.assertIsNotNone(experiment.generated_file)
        self.assertIsNotNone(experiment.ground_truth)

    def test_pending_experiment_file_deletion(self):
        experiment = PendingExperiments.objects.get(run_name='testexperiment')
        file_path = experiment.main_file.path
        experiment.delete()
        self.assertFalse(os.path.isfile(file_path))

    def test_pending_experiment_str_representation(self):
        experiment = PendingExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(str(experiment), 'testexperiment (pending) (id:1)')

    def test_pending_experiment_columns_and_parameters_json(self):
        experiment = PendingExperiments.objects.get(run_name='testexperiment')
        columns_dict = {'testcolumn1': '6.433658544295', 'testcolumn2': '5.509168303351'}
        parameters_dict = {'testparam1': 1, 'testparam2': 2}
        self.assertDictEqual(experiment.get_columns(), columns_dict)
        self.assertDictEqual(experiment.get_para(), parameters_dict)

    def test_pending_experiment_operation_option_choices(self):
        experiment = PendingExperiments.objects.get(run_name='testexperiment')
        choices = [('1', 'All subspaces'), ('2', 'All, except'), ('3', 'Combination')]
        self.assertEqual(experiment._meta.get_field('operation_option').choices, choices)


class FinishedExperimentsTest(ExperimentsBaseTest):
    @classmethod
    def setUp(cls):
        super().setUp()

        cls.result = SimpleUploadedFile("testresult.csv", b"file_content", content_type="text/csv")
        cls.result_with_addition = SimpleUploadedFile("testresult_with_addition.csv", b"file_content",
                                                      content_type="text/csv")
        cls.metrics_file = SimpleUploadedFile("testmetrics.csv", b"file_content", content_type="text/csv")
        cls.roc = SimpleUploadedFile("testroc.png", b"PNG_FILE_CONTENT", content_type="image/png")
        cls.roc_after_merge = SimpleUploadedFile("test_after_merge.png", b"PNG_FILE_CONTENT", content_type="image/png")
        cls.invalid_file = SimpleUploadedFile("testfile.pdf", b"file_content", content_type="application/pdf")

        # create a FinishedExperiments object to use in the test
        finished_experiment = FinishedExperiments.objects.create(
            user=cls.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.finished,
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            created_time=cls.data1,
            start_time=cls.data2,
            duration=cls.delta,
            operation_option='2',
            has_ground_truth=True,
            has_generated_file=True,
            result=cls.result,
            result_with_addition=cls.result_with_addition,
            metrics='{"testmetric1": 0.75, "testmetric2": 0.92}',
            metrics_file=cls.metrics_file,
            roc_path=user_roc_path(cls.roc.name),
            roc_after_merge_path=user_roc_path(cls.roc_after_merge.name)
        )

    def test_finished_experiment_user(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.user, self.user)

    def test_finished_experiment_run_name(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.run_name, 'testexperiment')

    def test_finished_experiment_file_name(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.file_name, 'testfile.csv')

    def test_finished_experiment_state(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.state, Experiment_state.finished)

    def test_finished_experiment_odm(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.odm, 'testodm')

    def test_finished_experiment_operation(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.operation, 'testoperation')

    def test_finished_experiment_columns(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.columns, '{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}')

    def test_finished_experiment_parameters(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.parameters, '{"testparam1": 1, "testparam2": 2}')

    def test_finished_experiment_created_time(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.created_time, self.data1)

    def test_finished_experiment_start_time(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.start_time, self.data2)

    def test_finished_experiment_duration(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.duration, self.delta)

    def test_finished_experiment_operation_option(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.operation_option, '2')

    def test_finished_experiment_has_ground_truth(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertTrue(experiment.has_ground_truth)

    def test_finished_experiment_has_generated_file(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertTrue(experiment.has_generated_file)

    def test_finished_experiment_result(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.result)

    def test_finished_experiment_result_with_addition(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.result_with_addition)

    def test_finished_experiment_metrics(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertEqual(experiment.get_metrics(), {"testmetric1": 0.75, "testmetric2": 0.92})

    def test_finished_experiment_metrics_file(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.metrics_file)

    def test_finished_experiment_roc_path(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.roc_path)

    def test_finished_experiment_roc_after_merge_path(self):
        experiment = FinishedExperiments.objects.get(run_name='testexperiment')
        self.assertIsNotNone(experiment.roc_after_merge_path)

    def test_roc_path(self):
        filename = 'testfile.csv'
        expected_path = 'testfile_roc.png'
        self.assertEqual(user_roc_path(filename), expected_path)


class NpEncoderTest(ExperimentsBaseTest):

    @classmethod
    def setUp(cls):
        super().setUp()

        experiment = FinishedExperiments.objects.create(
            user=cls.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.finished,
            result='result.csv',
            metrics='{"testmetric": "blank"}',
            metrics_file='metrics.csv'
        )

    def test_integer_encoding(self):
        obj = np.int32(10)
        expected_output = 10
        experiment = FinishedExperiments.objects.get(id=1)
        experiment.set_metrics(obj)
        self.assertEqual(experiment.get_metrics(), expected_output)

    def test_float_encoding(self):
        obj = np.float32(3.14)
        experiment = FinishedExperiments.objects.get(id=1)
        experiment.set_metrics(obj)
        self.assertEqual(experiment.get_metrics(), obj)

    def test_ndarray_encoding(self):
        obj = np.array([1, 2, 3])
        expected_output = [1, 2, 3]
        experiment = FinishedExperiments.objects.get(id=1)
        experiment.set_metrics(obj)
        self.assertEqual(experiment.get_metrics(), expected_output)

    def test_other_object_encoding(self):
        obj = {'a': 1, 'b': 2, 'c': 3}
        experiment = FinishedExperiments.objects.get(id=1)
        experiment.set_metrics(obj)
        self.assertEqual(experiment.get_metrics(), obj)

    # def test_default_method_called(self):
    #     # create a mock object that is not of type np.integer, np.floating, or np.ndarray
    #     obj = {'a': 1, 'b': 2}
    #     # create an instance of NpEncoder
    #     encoder = NpEncoder()
    #     # call the encode method of the encoder with the mock object
    #     result = encoder.encode(obj)
    #     # check if the decoded result is the same as the original object
    #     experiment = FinishedExperiments.objects.get(id=1)
    #     experiment.metrics = result
    #     self.assertEqual(experiment.get_metrics(), obj)

    def test_default_method_called(self):
        # create a dictionary with a numpy array as a value
        obj = set([1, 2, 3])
        # encode the dictionary using NpEncoder
        experiment = FinishedExperiments.objects.get(id=1)
        with self.assertRaises(TypeError):
            experiment.set_metrics(obj)
