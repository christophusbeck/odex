import os
import time
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
        self.__try_remove_file(self.path_outputs + "metrics_" + self.path_input)
        self.__try_remove_file(self.path_outputs + "result_" + self.path_input)
        self.__try_remove_file(self.path_outputs + "result_" + self.path_input.replace(".csv", "") + "_with_addition.csv")
        self.__try_remove_file(self.path_media + self.path_gt)
        self.__try_remove_file(self.path_media + self.path_gen)
        self.__try_remove_file(self.path_media + "input_roc.jpg")
        self.__try_remove_file(self.path_media + "gen_roc.jpg")
        pass

    def __try_remove_file(self, path):
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
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
        time.sleep(1.0)

        if not use_gen:
            self.assertTrue(os.path.exists(self.path_outputs + "metrics_" + self.path_input))
        self.assertTrue(os.path.exists(self.path_outputs + "result_" + self.path_input))
        path_gen_res = self.path_outputs + "result_" + self.path_input.replace(".csv", "") + "_with_addition.csv"
        if use_gen:
            self.assertTrue(os.path.exists(path_gen_res))

        path_input_roc = self.path_media + "input_roc.jpg"
        if use_gt:
            self.assertTrue(os.path.exists(path_input_roc))

        path_gen_roc = self.path_media + "gen_roc.jpg"
        if use_gt and use_gen:
            self.assertTrue(os.path.exists(path_gen_roc))

        models.Users.objects.all().delete()
        models.PendingExperiments.objects.all().delete()



    def test_run_only_od_1(self):
        self.__run_detector_thread(False, False, "1")

    def test_run_only_od_2(self):
        self.__run_detector_thread(False, False, "2")

    def test_run_only_od_3(self):
        self.__run_detector_thread(False, False, "3")

    def test_run_with_gt_1(self):
        self.__run_detector_thread(True, False, "1")

    def test_run_with_gt_2(self):
        self.__run_detector_thread(True, False, "2")

    def test_run_with_gt_3(self):
        self.__run_detector_thread(True, False, "3")

    def test_run_with_gen_1(self):
        self.__run_detector_thread(False, True, "1")

    def test_run_with_gen_2(self):
        self.__run_detector_thread(False, True, "2")

    def test_run_with_gen_3(self):
        self.__run_detector_thread(False, True, "3")

    def test_run_with_gt_and_gen_1(self):
        self.__run_detector_thread(True, True, "1")

    def test_run_with_gt_and_gen_2(self):
        self.__run_detector_thread(True, True, "2")

    def test_run_with_gt_and_gen_3(self):
        self.__run_detector_thread(True, True, "3")


if __name__ == '__main__':
    unittest.main()
