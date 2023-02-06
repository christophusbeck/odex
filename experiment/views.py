import json

import pandas as pd
from http.client import HTTPResponse

from django.forms import fields, widgets
from django.shortcuts import render, redirect
from django.views import View

import tools.odm_handling
from experiment.forms import CreateForm, ConfigForm
from experiment import models

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator




# Create your views here.
# To render the pages of configuration and details: we need following parameters
#
# Conf: {
# execution_title,
# #detected subspaces of the database from user,
# a <K,V> map: < subspaces on .csv, indexing(automatic incremental ids : 1,2,3...)>
# }
# A static file which describe the odms that we have AND
# a <parameters,values> map of those odms
#
# For the form of Conf:
# we have to check in the formlist: if detected parameters are valid or not
# example: All, except(x10), x10 as input, we have to check if subspaces contains id == 10
#          Combination: X10&&x12 and x15||x45 if the syntax is correct and subspaces contains
#           ids of 10,12,15,45
# we also have to check the grund truth file and addtional data file from user
# are they really .csv file (or we can just report the error of odms if they are not valid)


# PendingExp:
# {
# execution_title,
# #detected subspaces of the database from user,
# a <K,V> map: < subspaces on .csv, indexing(automatic incremental ids : 1,2,3...)>
# }
# In order to show Configuration we need
# {
# selected odm,
# <Paramater, value> of the odm,
# detecting subspaces user choose in the configuration:
# in form of “(all, except x10)” or “all",
# }


# FinishedExp: {
# execution_title,
# #detected subspaces of the database from user,
# a <K,V> map: < subspaces on .csv, indexing(automatic incremental ids : 1,2,3...)>
# }
# In order to show Configuration we need
# {
#   selected odm,
#   <Paramater, value> of the odm,
#   detecting subspaces user choose in the configuration:
#   in form of “(all, except x10)” or “all",
# }

# In order to show the result we need:
# {
#     amount of detected outliers,
#     detected outliers as .csv file
# }
#
# if with grund truth file:
#     {<Metric, Result>}
#
# if with addtional data:
#     {
#         amount of detected outliers after merging with generated data,
#         download detected outliers as .csv file(include addtional data),
#         (and if possible)
#         an ROC curve image: which shows the diff between with and without addtional data
#     }


@method_decorator(csrf_exempt, name='dispatch')
class MainView(View):
    template_name = "main.html"

    def get(self, request, *args, **kwargs):
        queryset = models.Experiments.objects.filter(user_id=request.session["info"]["id"])
        form = CreateForm()
        return render(request, self.template_name, {"queryset": queryset, "form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = models.Users.objects.get(id=request.session["info"]["id"])
            pending = models.PendingExperiments(user=user)
            pending.run_name = form.cleaned_data['run_name']
            pending.file_name = form.files['main_file'].name
            pending.state = "edited"
            pending.main_file = form.files['main_file']
            data = pd.read_csv(pending.main_file)
            pending.set_columns(list(data))
            pending.save()
            return JsonResponse({"status": True, "id": pending.id})

        return JsonResponse({"status": False, 'error': form.errors})


class DeleteView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET['id'])
        print(models.Users.objects.all())
        models.Experiments.objects.filter(id=request.GET['id']).delete()
        print(models.Users.objects.all())
        return redirect("/main/")


class Configuration(View):
    template_name = "Configuration.html"

    def get(self, request, *args, **kwargs):

        # only for test
        # exp_Info = models.Experiments.objects.all()
        exp = models.Experiments.objects.filter(id=request.GET['id'])
        columns = exp[0].get_columns()
        form = ConfigForm()
        odms = tools.odm_handling.get_odm_dict().keys()
        print("here is odems: ", dict(tools.odm_handling.get_def_value_dict(tools.odm_handling.match_odm_by_name("ABOD"))).keys())
        return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms":odms})

    def post(self, request, *args, **kwargs):
        form = ConfigForm(data=request.POST, files=request.FILES)

        exp_Info = models.Experiments.objects.all()
        formConf = ConfigForm()

        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponse("true")
        return redirect("main/")


class FinishedDetailView(View):
    template_name = "FinishedDetail.html"

    def get(self, request, *args, **kwargs):
        form = CreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm()
        if form.is_valid():
            form.save()
            return redirect('/main/')
        return render(request, self.template_name, {"form": form})


class PendingDetailView(View):
    template_name = "PendingDetail.html"

    def get(self, request, *args, **kwargs):
        form = CreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm()
        if form.is_valid():
            form.save()
            return redirect('/main/')
        return render(request, self.template_name, {"form": form})
