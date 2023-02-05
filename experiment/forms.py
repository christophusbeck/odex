from django import forms
from django.shortcuts import render, redirect

from experiment import models
from tools.bootstrap import BootStrapForm, BootStrapModelForm




class CreateForm(BootStrapModelForm):
    run_name = forms.CharField(label="experiment name", max_length=128, help_text="please enter a name")

    class Meta:
        model = models.PendingExperiments
        fields = ["main_file"]


class ConfigForm():
    dbfile_name = forms.FileField(label="dbfile")
    ground_truth_file_path = forms.FileField(label="gtfile")
    addtional_data_file_path = forms.FileField(label="addfile")
    operation = forms.CharField(label="operation")

    def upload_form(request):
        form = ConfigForm()
        return redirect('main.html')

    def is_valid(self):
        pass

    def save(self):
        pass


