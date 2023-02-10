from django.test import TestCase
from experiment.models import Experiments
from user.models import Users


class ExperimentTestCase(TestCase):
    user = None
    exp1 = None

    @classmethod
    def setUpClass(cls):
        print("Set up")
        cls.user = Users.objects.create(username='tester', password='123')
        cls.exp1 = Experiments.objects.create(user=cls.user, run_name='1', file_name='test.csv', state='editing',
                                              odm='ABOD', operation='AND', auxiliary_file_name='other.csv',
                                              columns={'x': 1},
                                              parameters='', created_time=None, start_time=None,
                                              duration=None,
                                              operation_option='1', has_ground_truth=True, has_generated_file=True)

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass')
        cls.user.delete()
        cls.exp1.delete()

    def test_create(self):
        exp = Experiments.objects.create(user=self.user, run_name='1', file_name='test.csv', state='editing',
                                         odm='ABOD', operation='AND', auxiliary_file_name='other.csv',
                                         columns={'x': 1},
                                         parameters='', created_time=None, start_time=None,
                                         duration=None,
                                         operation_option='1', has_ground_truth=True, has_generated_file=True)
        self.assertTrue(exp is not None)
        self.assertEqual(Experiments.objects.count(), 1)
        self.assertNotEqual(Experiments.objects.count(), 10)