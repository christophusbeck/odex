from django import forms
from experiment import models
from tools.bootstrap import BootStrapModelForm


class CreateForm(BootStrapModelForm):
    class Meta:
        model = models.Experiments
        fields = ["run_name"]
