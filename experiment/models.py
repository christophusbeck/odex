from django.db import models
from enum import Enum
import csv


# Create your models here.

class CSVFileField(models.FileField):
    #content_types
    max_upload_size = 0

    #def clean():


class Experiment_state(Enum):
    FAILED = -1
    PENDING = 0
    FINISHED = 1


class Pyod_method_names(Enum):
    # tba
    NULL = 0


class Experiments(models.Model):
    userid = models.IntegerField(verbose_name="user id")
    experiment_name = models.CharField(verbose_name="experiment name", max_length=128)
    # data =
    file_name = models.CharField(verbose_name="file", max_length=128)
    state = Experiment_state
    column_names = list
    pyod_method_name = Pyod_method_names
    logical_formula = models.CharField(verbose_name="logical formula", max_length=128)
    auxiliary_file_name = models.CharField(verbose_name="file", max_length=128)


class PendingExperiments(Experiments):
    experimentID = models.IntegerField(verbose_name="experiment id")
    main_file_path = models.CharField(verbose_name="main file path", max_length=128)
    generated_file_path = models.CharField(verbose_name="generated file path", max_length=128)
    ground_truth_path = models.CharField(verbose_name="ground truth path", max_length=128)


class FinishedExperiment(Experiments):
    experimentID = models.IntegerField(verbose_name="run duration")
    result = list
    run_duration = models.IntegerField(verbose_name="run duration")


class OutlierDetectionMethods:
    all_names_of_pyod_method = string

    def __str__(self):
        return "ab"


class Hyperparameters:
    hyperparameters = list
    odm_name = OutlierDetectionMethods

