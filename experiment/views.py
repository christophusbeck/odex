from http.client import HTTPResponse

from django.forms import fields, widgets
from django.shortcuts import render, redirect
from django.views import View

from experiment.forms import CreateForm, ConfigForm, UpForm
from experiment import models

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from tools.bootstrap import BootStrapModelForm


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
        queryset = models.Experiments.objects.all()
        form = CreateForm()
        return render(request, self.template_name, {"queryset": queryset, "form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user_id = models.Users.objects.get(id=request.session["info"]["id"])
            pending = models.PendingExperiments(user_id=user_id)
            pending.run_name = form.cleaned_data['run_name']
            pending.file_name = form.files['main_file'].name
            pending.state = "edited"
            pending.main_file = form.files['main_file']
            pending.save()
            return JsonResponse({"status": True, "id": pending.id})

        return JsonResponse({"status": False, 'error': form.errors})


class DeleteView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET['id'])
        models.Experiments.objects.filter(id=request.GET['id']).delete()
        return redirect("/main/")


class Configuration(View):
    template_name = "Configuration.html"

    def get(self, request, *args, **kwargs):
        exp_Info = models.Experiments.objects.filter(id=request.GET['id'])
        form = ConfigForm()
        upform = UpForm()
        print(request.GET)
        return render(request, self.template_name, {"exp_Info": exp_Info, "form": form, "upform":upform})

    def post(self, request, *args, **kwargs):
        form = UpForm(data=request.POST, files=request.FILES)

        exp_Info = models.Experiments.objects.all()
        upform = UpForm()
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
