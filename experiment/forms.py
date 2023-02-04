from django import forms
from experiment import models
from tools.bootstrap import BootStrapForm, BootStrapModelForm


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}/{2}'.format(instance.user.id, instance.experiment.id, filename)


class CreateForm(BootStrapModelForm):
    run_name = forms.CharField(label="experiment name", max_length=128)

    class Meta:
        model = models.PendingExperiments
        fields = ["main_file"]