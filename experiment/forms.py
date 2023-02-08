from django import forms
from django.forms import fields, widgets
from django.shortcuts import render, redirect

import tools.odm_handling
from experiment import models
from tools.bootstrap import BootStrapForm, BootStrapModelForm




class CreateForm(BootStrapModelForm):
    class Meta:
        model = models.PendingExperiments
        fields = ["run_name", "main_file"]

class ConfigForm(BootStrapModelForm):

    class Meta:
        model = models.PendingExperiments
        fields = ['odm', 'auxiliary_file_name', 'generated_file', 'ground_truth']
        label = {
            'operation': 'detected subspaces',
            'generated_file': 'upload an additional data file',
            'ground_truth': 'upload a ground truth file'
        }

    operation_except = forms.CharField(
        label="All subspaces, except",
        max_length=64,
        help_text="enter the column indexing above",
        required=False
    )

    operation_written = forms.CharField(
        label="Subspace Combination",
        max_length=64,
        help_text="enter the subspace combination with column indexing above",
        required=False
    )

    # odm_options = fields.ChoiceField(
    #     choices=[(1, "1"), (2, "2"), (3, "3"), ],
    #     initial=2
    # )

    # ground_truth_options = fields.ChoiceField(
    #     choices=[(1, "detection only"), (2, "compare with a grund truth file")],
    #     widget=widgets.RadioSelect(attrs={'style':'width:30px; height:20px'}),
    # )
    #
    # additional_data_option = fields.ChoiceField(
    #     widget=widgets.CheckboxInput(attrs={'style':'width:30px; height:20px'}),
    # )
    #
    # operation_model_options = fields.ChoiceField(
    #     choices=[(1, "All subspaces"), (2, "All, except:"), (3, "Combination:")],
    #     widget=widgets.RadioSelect(attrs={'style':'width:30px; height:20px'}),
    #     initial=1
    # )


# class UpForm(BootStrapForm):
#     operation = forms.CharField(label="detected subspaces")
#     ground_truth = forms.FileField(label= "upload a ground truth file")
#     # still need to check if this is a valid file or not
#     add_data = forms.FileField(label= "upload an addtional data file")
#     # upload all the informations in a table! only for test
#     # parameter = forms.CharField(label="parameters")


