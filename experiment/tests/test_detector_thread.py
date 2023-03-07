import unittest
import random

import django.db.models
import pyod.utils.data
from django.test import TestCase
from django.db.models.fields.files import FileField
from tools import detector_thread
import numpy as np

from experiment import models
from experiment.models import PendingExperiments
from tools import odm_handling


class Test_detector_thread(TestCase):

    def setup(self):
        pass

    def test_run(self):
        path_input = "input.csv"
        user = models.Users.objects.create(id=0)

        #exp = PendingExperiments()
        exp = models.PendingExperiments.objects.create(user_id=0, id=0)
        exp.id = 0
        odm_pick = "ABOD" #random.choice(list(odm_handling.get_odm_dict().keys()))
        exp.odm = odm_handling.match_odm_by_name(odm_pick)
        exp.set_para(odm_handling.get_def_value_dict(exp.odm).copy())
        print(exp.get_para())
        exp.operation = "1"

        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        odm_handling.write_data_to_csv(path_input, training_data)
        exp.main_file = FileField(upload_to=path_input)

        det_thread = detector_thread.DetectorThread(id=0)
        det_thread.run()








if __name__ == '__main__':
    unittest.main()
