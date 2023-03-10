import os
import unittest
import random


import pyod.utils.data
from django.test import TestCase
from django.utils import timezone

from tools import detector_thread
import numpy as np

from experiment import models
from tools import odm_handling


class Test_detector_thread(TestCase):
    path_media = "media\\"
    path_input = "input.csv"
    path_gt = "gt.csv"
    path_gen = "gen.csv"
    path_outputs = "media/user_0/0/"

    def setup(self):
        pass

    def tearDown(self):
        pass

    def __run_detector_thread(self, use_gt=False, use_gen=False, operation_option="1"):
        training_data, test_data, train_gt, test_gt = pyod.utils.data.generate_data(400, 100, 3, 0.1)
        training_data = list(training_data)
        training_data.insert(0, ["x1", "x2", "x3"])
        gt_list = []
        for row in train_gt:
            gt_list.append([row])

        if not os.path.exists("media/"):
            os.mkdir("media/")
        if not os.path.exists("media/user_0/"):
            os.mkdir("media/user_0/")
        if not os.path.exists("media/user_0/0/"):
            os.mkdir("media/user_0/0/")

        odm_handling.write_data_to_csv(self.path_media + self.path_input, training_data)
        odm_handling.write_data_to_csv(self.path_media + self.path_gt, gt_list)
        odm_handling.write_data_to_csv(self.path_media + self.path_gen, test_data)


        user = models.Users.objects.create(id=0)
        exp = models.PendingExperiments.objects.create(user=user, id=0)
        exp.id = 0
        odm_pick = random.choice(list(odm_handling.get_odm_dict().keys()))
        print("odm_pick = ", odm_pick)
        exp.odm = odm_handling.match_odm_by_name(odm_pick)
        print(exp.odm)
        exp.set_para({})
        exp.operation = "1"
        if operation_option == "2":
            exp.operation = "1"
        if operation_option == "3":
            exp.operation = "{1,2}|{1,3}&{2,3}"

        exp.operation_option = operation_option
        exp.start_time = timezone.now()
        exp.run_name = "test_exp"

        exp.main_file.name = self.path_input
        exp.file_name = self.path_input

        if use_gt:
            exp.ground_truth = self.path_gt
            exp.has_ground_truth = True
        if use_gen:
            exp.generated_file = self.path_gen
            exp.has_generated_file = True
        exp.save()

        det_thread = detector_thread.DetectorThread(id=0)
        det_thread.run()

        if not use_gen:
            self.assertTrue(os.path.exists(self.path_outputs + "metrics_" + self.path_input))
        self.assertTrue(os.path.exists(self.path_outputs + "result_" + self.path_input))
        path_gen_res = self.path_outputs + "result_" + self.path_input.replace(".csv", "") + "_with_addition.csv"
        if use_gen:
            self.assertTrue(os.path.exists(path_gen_res))

        if use_gt:
            path_input_roc = self.path_media + "input_roc.jpg"
            self.assertTrue(os.path.exists(path_input_roc))
        if use_gt and use_gen:
            path_geb_roc = self.path_media + "gen_roc.jpg"
            self.assertTrue(os.path.exists(path_geb_roc))

        models.Users.objects.all().delete()
        models.PendingExperiments.objects.all().delete()

        try:
            os.remove(self.path_outputs + "metrics_" + self.path_input)
            os.remove(self.path_outputs + "result_" + self.path_input)
            os.remove(path_gen_res)
            os.remove(self.path_media + self.path_gt)
            os.remove(self.path_media + self.path_gen)
        except Exception as e:
            pass

    def test_run_only_od(self):
        self.__run_detector_thread(False, False, "1")
        self.__run_detector_thread(False, False, "2")
        self.__run_detector_thread(False, False, "3")
        pass

    def test_run_with_gt(self):
        self.__run_detector_thread(True, False, "1")
        self.__run_detector_thread(True, False, "2")
        self.__run_detector_thread(True, False, "3")
        pass

    def test_run_with_gen(self):
        self.__run_detector_thread(False, True, "1")
        self.__run_detector_thread(False, True, "2")
        self.__run_detector_thread(False, True, "3")
        pass

    def test_run_with_gt_and_gen(self):
        self.__run_detector_thread(True, True, "1")
        self.__run_detector_thread(True, True, "2")
        self.__run_detector_thread(True, True, "3")
        pass


if __name__ == '__main__':
    unittest.main()
