from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from datetime import timedelta, datetime
import pytz

from user.models import Users
from experiment.models import Experiments, Experiment_state, PendingExperiments, FinishedExperiments


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
        self.assertEqual(experiment.get_columns(), {"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"})

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
            state='invalid_state',  # Invalid state value
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            created_time=self.data1,
            start_time=self.data2,
            duration=self.delta,
            operation_option='2',
            has_ground_truth=True,
            has_generated_file=True
        )
        self.assertRaises(ValidationError, experiment.full_clean)

    def test_experiment_invalid_operation_option(self):
        experiment = Experiments.objects.create(
            user=self.user,
            run_name='testexperiment',
            file_name='testfile.csv',
            state=Experiment_state.editing,
            odm='testodm',
            operation='testoperation',
            columns='{"testcolumn1": "6.433658544295",  "testcolumn2": "5.509168303351"}',
            parameters='{"testparam1": 1, "testparam2": 2}',
            created_time=self.data1,
            start_time=self.data2,
            duration=self.delta,
            operation_option='invalid_option',  # Invalid operation option value
            has_ground_truth=True,
            has_generated_file=True
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


class PendingExperimentsTest(ExperimentsBaseTest):
    @classmethod
    def setUp(cls):
        super().setUp()

        # create a file to use in the test
        cls.file = SimpleUploadedFile("testfile.csv", b"file_content", content_type="text/csv")
        cls.invalid_file = SimpleUploadedFile("testfile.pdf", b"file_content", content_type="application/pdf")

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
            generated_file=cls.file,
            ground_truth=cls.file,
            error="testerror",
        )

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


class FinishedExperimentsTest(ExperimentsBaseTest):
    @classmethod
    def setUp(cls):
        super().setUp()

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
            result='result.csv',
            result_with_addition='result_with_addition.csv',
            metrics='{"testmetric1": 0.75, "testmetric2": 0.92}',
            metrics_file='metrics.csv',
            roc_path='roc.png',
            roc_after_merge_path='roc_after_merge.png'
        )







