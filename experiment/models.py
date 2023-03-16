import json
import os
import shutil

import numpy as np
from sklearn.preprocessing._data import MinMaxScaler, StandardScaler
from django.db import models
from django.utils.translation import gettext_lazy as _

from odex import settings
from user.models import Users



class Experiment_state(models.TextChoices):
    finished = 'finished', 'finished'
    pending = 'pending', 'pending'
    editing = 'editing', 'editing'
    failed = 'failed', 'failed'


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
    file_name = models.CharField(
        verbose_name="file",
        max_length=128
    )
    state = models.CharField(
        verbose_name="state",
        max_length=200,
        choices=Experiment_state.choices
    )
    odm = models.CharField(
        verbose_name="odm",
        max_length=128,
        blank=True,
        null=True
    )
    operation = models.CharField(
        verbose_name="logical formula",
        max_length=128,
        blank=True,
        null=True
    )
    columns = models.TextField(
        blank=True,
        null=True
    )
    parameters = models.TextField(
        blank=True,
        null=True
    )
    created_time = models.DateTimeField(
        verbose_name="created time",
        blank=True,
        null=True
    )
    start_time = models.DateTimeField(
        verbose_name="start time",
        blank=True,
        null=True
    )
    duration = models.DurationField(
        verbose_name="duration of run",
        blank=True,
        null=True
    )
    operation_option = models.CharField(
        verbose_name="operation option",
        max_length=1,
        choices=[("1", "All subspaces"), ("2", "All, except"), ("3", "Combination")],
        blank=True,
        null=True
    )
    has_ground_truth = models.BooleanField(
        verbose_name="if has ground truth",
        blank=True,
        null=True
    )
    has_generated_file = models.BooleanField(
        verbose_name="if has generated file",
        blank=True,
        null=True
    )

    def set_columns(self, x):
        self.columns = json.dumps(x)

    def get_columns(self):
        return json.loads(self.columns)

    def set_para(self, x):
        if self.odm == 'LUNAR' and "scaler" in x:
            if isinstance(x["scaler"], MinMaxScaler):
                x["scaler"] = "MinMaxScaler()"
            elif isinstance(x["scaler"], StandardScaler):
                x["scaler"] = "StandardScaler()"
        self.parameters = json.dumps(x)

    def get_para(self):
        para = json.loads(self.parameters)
        if self.odm == 'LUNAR':
            if para["scaler"] == "MinMaxScaler()":
                para["scaler"] = MinMaxScaler()
            elif para["scaler"] == "StandardScaler()":
                para["scaler"] = StandardScaler()
        return para

    def delete(self, *args, **kwargs):
        # Delete the file before the model
        shutil.rmtree(user_experiment_directory(self))
        super(Experiments, self).delete(*args, **kwargs)

    def __str__(self):
        return self.run_name + " (" + self.state + ")"


def user_experiment_directory(instance):
    # return directory MEDIA_ROOT/user_<id>/<exp_id>
    return '{0}/user_{1}/{2}'.format(settings.MEDIA_ROOT, instance.user_id, instance.id)


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


def user_result_with_addition_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/result_<filename>_with_addition.csv
    return 'user_{0}/{1}/result_{2}_with_addition.csv'.format(instance.user_id, instance.id, filename.removesuffix('.csv'))


def user_metrics_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<exp_id>/metrics_<filename>
    return 'user_{0}/{1}/metrics_{2}'.format(instance.user_id, instance.id, filename)

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
        verbose_name="result",
        upload_to=user_result_path
    )
    result_with_addition = models.FileField(
        verbose_name="result with addition",
        upload_to=user_result_with_addition_path,
        blank=True,
        null=True
    )
    metrics = models.TextField()
    metrics_file = models.FileField(
        verbose_name="metrics",
        upload_to=user_metrics_path
    )
    roc_path = models.TextField(
        verbose_name="Path of roc curve",
        blank=True,
        null=True
    )
    roc_after_merge_path = models.TextField(
        verbose_name="Path of roc curve with additional file",
        blank=True,
        null=True
    )

    def set_metrics(self, x):
        self.metrics = json.dumps(x, cls=NpEncoder)

    def get_metrics(self):
        return json.loads(self.metrics)

