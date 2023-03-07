import os
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
        path_media = "media\\"
        path_input = "input.csv"
        path_gt = "gr.csv"
        path_gen = "gen.csv"
        user = models.Users.objects.create(id=0)

        #exp = PendingExperiments()
        exp = models.PendingExperiments.objects.create(user=user, id=0)
        exp.id = 0
        odm_pick = "ABOD" #random.choice(list(odm_handling.get_odm_dict().keys()))
        exp.odm = odm_handling.match_odm_by_name(odm_pick)
        exp.set_para(odm_handling.get_def_value_dict(exp.odm).copy())
        #print(exp.get_para())
        exp.operation = "1"

        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        odm_handling.write_data_to_csv(path_media + path_input, training_data)
        odm_handling.write_data_to_csv(path_media + path_gt, train_gt)
        odm_handling.write_data_to_csv(path_media + path_gen, test_data)

        exp.main_file.name = path_input
        exp.save()

        det_thread = detector_thread.DetectorThread(id=0)
        det_thread.run()

        os.remove(path_media + path_input)
        os.remove(path_media + path_gt)
        os.remove(path_media + path_gen)








if __name__ == '__main__':
    unittest.main()
