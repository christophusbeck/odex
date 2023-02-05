from django import forms
from experiment import models
from tools.bootstrap import BootStrapForm, BootStrapModelForm




class CreateForm(BootStrapModelForm):
    run_name = forms.CharField(label="experiment name", max_length=128, help_text="please enter a name")

    class Meta:
        model = models.PendingExperiments
        fields = ["main_file"]