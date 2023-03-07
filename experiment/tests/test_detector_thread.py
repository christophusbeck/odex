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
    path_media = "media\\"
    path_input = "input.csv"
    path_gt = "gt.csv"
    path_gen = "gen.csv"

    def setup(self):
        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        odm_handling.write_data_to_csv(self.path_media + self.path_input, training_data)

        gt_list = []
        for row in train_gt:
            gt_list.append([row])

        odm_handling.write_data_to_csv(self.path_media + self.path_gt, gt_list)
        odm_handling.write_data_to_csv(self.path_media + self.path_gen, test_data)

    def tearDown(self):
        models.Experiments.objects.all().delete()
        if os.path.exists(self.path_media + self.path_input):
            os.remove(self.path_media + self.path_input)
        if os.path.exists(self.path_media + self.path_gt):
            os.remove(self.path_media + self.path_gt)
        if os.path.exists(self.path_media + self.path_gen):
            os.remove(self.path_media + self.path_gen)

    def test_run_only_od(self):
        user = models.Users.objects.create(id=0)
        exp = models.PendingExperiments.objects.create(user=user, id=0)
        exp.id = 0
        odm_pick = "ABOD"  # random.choice(list(odm_handling.get_odm_dict().keys()))
        exp.odm = odm_handling.match_odm_by_name(odm_pick)
        exp.set_para(odm_handling.get_def_value_dict(exp.odm).copy())
        exp.operation = "1"

        exp.main_file.name = self.path_input
        exp.save()

        det_thread = detector_thread.DetectorThread(id=0)
        det_thread.run()


if __name__ == '__main__':
    unittest.main()
