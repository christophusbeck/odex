import os
import shutil
import time
import unittest
import random

import pyod.utils.data
from django.core.files import File
from django.test import TestCase, SimpleTestCase
from django.utils import timezone

from tools import detector_thread
import numpy as np

from experiment import models
from tools import odm_handling


class Test_detector_thread(TestCase):
    path_input = "input.csv"
    path_gt = "gt.csv"
    path_gen = "gen.csv"
    path_outputs = "media/user_0/"

    def setup(self):
        pass

    def tearDown(self):
        self.__try_remove_file(self.path_gt)
        self.__try_remove_file(self.path_gen)
        self.__try_remove_file(self.path_input)
        shutil.rmtree("media/user_0")

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
        self.assertTrue(os.path.exists("media/user_0/"))


        odm_handling.write_data_to_csv(self.path_input, training_data)
        odm_handling.write_data_to_csv(self.path_gt, gt_list)
        odm_handling.write_data_to_csv(self.path_gen, test_data)

        user = models.Users.objects.create(id=0)
        user.save()

        # odm_pick = random.choice(list(odm_handling.get_odm_dict().keys()))
        for odm_pick in list(odm_handling.get_odm_dict().keys()):
            print("odm_pick: ", odm_pick)
            exp = models.PendingExperiments.objects.create(user=user)
            exp.odm = odm_handling.match_odm_by_name(odm_pick)
            exp.set_para({})
            exp.operation = "1"
            if operation_option == "2":
                exp.operation = "1"
            if operation_option == "3":
                exp.operation = "{1,2}|{1,3}&{2,3}"

            exp.operation_option = operation_option
            exp.start_time = timezone.now()
            exp.run_name = "test_exp"

            input = open(self.path_input, 'r', encoding='UTF-8')
            exp.main_file = File(input)
            exp.file_name = self.path_input

            if use_gt:
                gt = open(self.path_gt, 'r', encoding='UTF-8')
                exp.ground_truth = File(gt)
                exp.has_ground_truth = True
            if use_gen:
                gen = open(self.path_gen, 'r', encoding='UTF-8')
                exp.generated_file = File(gen)
                exp.has_generated_file = True
            exp.save()
            input.close()
            if use_gt:
                gt.close()
            if use_gen:
                gen.close()

            det_thread = detector_thread.DetectorThread(id=exp.id)
            det_thread.run()
            time.sleep(1.0)

            ff = models.FinishedExperiments.objects.get(id=exp.id)
            if not use_gen:
                self.assertTrue(os.path.exists(self.path_outputs + str(exp.id) + "/metrics_" + self.path_input))
            self.assertTrue(os.path.exists(self.path_outputs + str(exp.id) + "/result_" + self.path_input))
            path_gen_res = self.path_outputs + str(exp.id) + "/result_" + self.path_input.replace(".csv", "") + "_with_addition.csv"
            if use_gen:
                self.assertTrue(os.path.exists(path_gen_res))

            path_input_roc = self.path_outputs + str(exp.id) + "/main_input_roc.png"
            if use_gt:
                self.assertTrue(os.path.exists(path_input_roc))

            path_gen_roc = self.path_outputs + str(exp.id) + "/additional_gen_roc.png"
            if use_gt and use_gen:
                self.assertTrue(os.path.exists(path_gen_roc))

        for e in models.Experiments.objects.all():
            e.delete()
        for u in models.Users.objects.all():
            u.delete()

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
