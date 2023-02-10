import json

import numpy as np
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
    editing = 'editing', _('editing')
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
    user = models.ForeignKey(
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
    operation = models.CharField(
        verbose_name="logical formula",
        max_length=128,
        blank=True,
        null=True
    )
    auxiliary_file_name = models.CharField(
        verbose_name="file",
        max_length=128,
        blank=True,
        null=True
    )
    columns = models.TextField(blank=True, null=True)
    parameters = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(
        verbose_name="created time",
        blank=True,
        null=True)
    start_time = models.DateTimeField(
        verbose_name="start time",
        blank=True,
        null=True)
    duration = models.DurationField(
        verbose_name="duration of run",
        blank=True,
        null=True
    )
    operation_option = models.CharField(
        max_length=2,
        choices=[("1", "All subspaces"), ("2", "All, except"), ("3", "Combination")],
        blank=True,
        null=True
    )
    has_ground_truth = models.BooleanField(
        blank=True,
        null=True
    )
    has_generated_file = models.BooleanField(
        blank=True,
        null=True
    )

    def set_columns(self, x):
        self.columns = json.dumps(x)

    def get_columns(self):
        return json.loads(self.columns)

    def set_para(self, x):
        self.parameters = json.dumps(x)

    def get_para(self):
        return json.loads(self.parameters)


def user_main_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/main_<filename>
    return 'user_{0}/{1}/main_{2}'.format(instance.user_id, instance.id, filename)


def user_generated_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/additional_<filename>
    return 'user_{0}/{1}/additional_{2}'.format(instance.user_id, instance.id, filename)


def user_ground_truth_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/ground_truth_<filename>
    return 'user_{0}/{1}/ground_truth_{2}'.format(instance.user_id, instance.id, filename)


def user_result_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/result_<filename>
    return 'user_{0}/{1}/result_{2}'.format(instance.user_id, instance.id, filename)

def user_roc_path(filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/<filename>_roc.jpg
    return '{0}_roc.jpg'.format(filename.removesuffix('.csv'))


def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class PendingExperiments(Experiments):
    main_file = models.FileField(
        verbose_name="main file path",
        upload_to=user_main_file_path,
        help_text="please upload a file",
        validators=[validate_file_extension],
        blank=True,
        null=True
    )
    generated_file = models.FileField(
        verbose_name="generated file path",
        upload_to=user_generated_file_path,
        help_text="please upload a generated file",
        validators=[validate_file_extension],
        blank=True,
        null=True
    )
    ground_truth = models.FileField(
        verbose_name="ground truth path",
        upload_to=user_ground_truth_path,
        help_text="please upload a ground truth file",
        validators=[validate_file_extension],
        blank=True,
        null=True
    )
    error = models.TextField(blank=True, null=True)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class FinishedExperiments(Experiments):
    result = models.FileField(
        verbose_name="ground truth path",
        upload_to=user_result_path,
        help_text="please upload a ground truth file",
        validators=[validate_file_extension],
        blank=True,
        null=True
    )
    metrics = models.TextField(
        blank=True,
        null=True
    )
    roc_path = models.FileField(
        verbose_name="Roc curve",
        upload_to=user_result_path,
        validators=[validate_file_extension],
        blank=True,
        null=True
    )
    roc_after_merge_path = models.FileField(
        verbose_name="Roc curve with additional file",
        upload_to=user_result_path,
        validators=[validate_file_extension],
        blank=True,
        null=True
    )

    def set_metrics(self, x):
        self.metrics = json.dumps(x, cls=NpEncoder)

    def get_metrics(self):
        return json.loads(self.metrics)



class OutlierDetectionMethods:
    #all_names_of_pyod_method = string

    def __str__(self):
        return "ab"


class Hyperparameters:
    hyperparameters = list
    odm_name = OutlierDetectionMethods

