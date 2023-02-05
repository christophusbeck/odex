from django import forms
from django.forms import fields, widgets
from django.shortcuts import render, redirect

from experiment import models
from tools.bootstrap import BootStrapForm, BootStrapModelForm




class CreateForm(BootStrapModelForm):
    class Meta:
        model = models.PendingExperiments
        fields = ["run_name", "main_file"]

class ConfigForm(forms.Form):


    odm = fields.ChoiceField(
        choices=[(1,"1"),(2,"2"),(3,"3"),],
        initial=2
    )

    ground_truth = fields.CharField(
        widget= widgets.RadioSelect(choices= [(1, "detection only"), (2, "compare with a grund truth file"),]),
    )

    addtional_data = fields.CharField(
        widget=widgets.CheckboxInput(),
    )

    operation_model = fields.CharField(
        widget= widgets.RadioSelect(choices= [(1, "All subspaces"), (2, "All, except:"),(3, "Combination:"),]),
        initial = 1
    )


class UpForm(BootStrapForm):
    operation = forms.CharField(label="detected subspaces")
    ground_truth = forms.FileField(label= "upload a ground truth file")
    add_data = forms.FileField(label= "upload an addtional data file")
    # upload all the informations in a table! only for test
    # parameter = forms.CharField(label="parameters")


class BootStrapForm(forms.Form):

    bootstrap_exclude_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name in self.bootstrap_exclude_fields:
                continue
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
            else:
                field.widget.attrs = {
                    "class": "form-control",
                }
