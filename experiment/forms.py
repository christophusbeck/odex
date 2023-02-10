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
        help_text="enter the column indexing above, you can use ',' to to separate your selected columns, like 1,2,3",
        required=False
    )

    operation_written = forms.CharField(
        label="Subspace Combination",
        max_length=64,
        help_text="enter the subspace combination with column indexing above," \
                  " You can use '{}' to denote columns that are executed together, " \
                  "and use '&' and '|' to denote logical operations AND and OR to the result, like {1,2}&{1,3}",
        required=False
    )

    ground_truth_options = fields.ChoiceField(
        choices=[("1", "Detection only"), ("2", "Compare with a ground truth file")],
        widget=widgets.RadioSelect(attrs={
            'id': 'ground_truth',
            'style': 'width:100px; height:20px'
            }),
        initial=1
    )

    #
    # additional_data_option = fields.ChoiceField(
    #     widget=widgets.CheckboxInput(attrs={
    #         'style': 'width:30px; height:20px',
    #     }),
    # )

    operation_model_options = fields.ChoiceField(
        choices=[("1", "All subspaces"), ("2", "All, except"), ("3", "Combination")],  # （value, label）
        widget=widgets.RadioSelect(attrs={
            'id': 'operation_model',
            'style': 'width:100px; height:20px',
        }),
        initial=1
    )



