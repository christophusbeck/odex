import json

from django.db import models
from django.utils.translation import gettext_lazy as _



# Create your models here.

class CSVFileField(models.FileField):
    #content_types
    max_upload_size = 0

    #def clean():


class Experiment_state(models.TextChoices):
    finished = 'finished', _('finished')
    pending = 'pending', _('pending')
    failed = 'failed', _('failed')

class Pyod_methods(models.TextChoices):
    abod = 'ABOD', _('Angle-based Outlier Detector')
    knn = 'KNN', _('k-Nearest Neighbors Detector')
    '''
    detection_name  = models.CharField(verbose_name = "detection name", max_length=128)
    contamination = models.FloatField(verbose_name = "contamination")
    n_neighbors = models.IntegerField(verbose_name="neighbors")
    method = models.CharField(verbose_name="experiment name", max_length=128)
    '''


class Experiments(models.Model):
    # TODO:store in the main page, once user triggers a new run and successfully uploaded database and exe_title,
    # TODO:write exp_id and user_id of the corresponding user and exp

    # allow blank only for test
    experiment_id = models.IntegerField(verbose_name="experiment id", blank=True, null=True)
    user_id = models.IntegerField(verbose_name="user id", blank=True, null=True)
    run_name = models.CharField(verbose_name="experiment name", max_length=128, blank=True, null=True)

    # TODO: state should be automatic be Pending untill change
    state = models.CharField(verbose_name="state", max_length=200, choices=Experiment_state.choices, blank=True, null=True)


    # write in the same dataset according to user_id and exp_id, which should be post via uid behind http request
    # TODO:redundant in the pendingexp for the first time, solve it later
    dbfile_name = models.FileField(verbose_name="file", max_length=128, blank=True, null=True)
    ground_truth_file_path = models.FileField(verbose_name="file", max_length=128, blank=True, null=True)
    addtional_data_file_path = models.FileField(verbose_name="file", max_length=128, blank=True, null=True)
    operation = models.CharField(verbose_name="logical formula", max_length=128, blank=True, null=True)

    #  TODO: why use choices here, i don't get it, we don't need to store them
    odm = models.CharField(verbose_name="odm", max_length=128, choices=Pyod_methods.choices, blank=True, null=True)

    # auxiliary_file_name = models.CharField(verbose_name="file", max_length=128, blank=True, null=True)

    # TODO: the following set should be wrote in the NewRun Form, detecting following data and write in the same set
    columns = models.TextField(null=True)
    amount_detected_subspace = models.IntegerField(verbose_name="amount of detected subspaces", blank=True, null=True)


    def set_columns(self, x):
        self.columns = json.dumps(x)

    def get_columns(self):
        return json.loads(self.columns)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.user.id, instance.experiment.id, filename)


# it would be much complex if we divide them into different tables but i'll try through
class PendingExperiments(Experiments):
    main_file = models.FileField(verbose_name="main file path", upload_to=user_directory_path)
    generated_file = models.FileField(verbose_name="generated file path", upload_to=user_directory_path)
    ground_truth = models.FileField(verbose_name="ground truth path", upload_to=user_directory_path)


class FinishedExperiments(Experiments):
    result_path = models.CharField(verbose_name="result path", max_length=128)
    start_time = models.TimeField(verbose_name="start time", auto_now=False, auto_now_add=True)
    duration = models.IntegerField(verbose_name="run duration")


class OutlierDetectionMethods:
    #all_names_of_pyod_method = string

    def __str__(self):
        return "ab"


class Hyperparameters:
    hyperparameters = list
    odm_name = OutlierDetectionMethods

