import json

from django.db import models
from django.utils.translation import gettext_lazy as _

from user.models import Users


# Create your models here.

class CSVFileField(models.FileField):
    #content_types
    max_upload_size = 0
    #super.path

    #def clean():


class Experiment_state(models.TextChoices):
    finished = 'finished', _('finished')
    pending = 'pending', _('pending')
    edited = 'edited', _('edited')
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
    user_id = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        verbose_name="user id",
        help_text="Please enter 3 characters"
    )
    run_name = models.CharField(
        verbose_name="experiment name",
        max_length=128,
        help_text="please enter a name"
    )
    file_name = models.CharField(verbose_name="file", max_length=128)
    state = models.CharField(verbose_name="state", max_length=200, choices=Experiment_state.choices, blank=True, null=True)
    odm = models.CharField(verbose_name="odm", max_length=128, choices=Pyod_methods.choices, blank=True, null=True)
    operation = models.CharField(verbose_name="logical formula", max_length=128, blank=True, null=True)
    auxiliary_file_name = models.CharField(verbose_name="file", max_length=128, blank=True, null=True)
    columns = models.TextField(null=True)

    def set_columns(self, x):
        self.columns = json.dumps(x)

    def get_columns(self):
        return json.loads(self.columns)


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.user_id, instance.id, filename)


class PendingExperiments(Experiments):
    main_file = models.FileField(
        verbose_name="main file path",
        upload_to=user_directory_path,
        help_text="please upload a file",
        blank=True,
        null=True
    )
    generated_file = models.FileField(verbose_name="generated file path", upload_to=user_directory_path, blank=True, null=True)
    ground_truth = models.FileField(verbose_name="ground truth path", upload_to=user_directory_path, blank=True, null=True)


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

