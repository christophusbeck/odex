import json
import time

import pandas as pd
from http.client import HTTPResponse

from django.forms import fields, widgets
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone

import tools.odm_handling
from tools.detector_thread import DetectorThread
from experiment.forms import CreateForm, ConfigForm
from experiment import models

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe


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

        page = int(request.GET.get('page', 1))
        page_size = 10
        start = (page - 1) * page_size
        end = page * page_size


        total_count = models.Experiments.objects.filter(user_id=request.session["info"]["id"]).count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        # according to current page show the pages before that and after that
        plus = 5

        if total_page_count <= 2 * plus + 1:
            # to check if there's more than 11 pages, than only show that page
            start_page = 1
            end_page = total_page_count
        else:
            # current page < 5
            if page <= plus:
                start_page = 1
                end_page = 2 * plus + 1
            else:
                if (page + plus) > total_page_count:
                    start_page = total_page_count - 2 * plus
                    end_page = total_page_count
                else:
                    start_page = page - plus
                    end_page = page + plus


        page_str_list = []

        # prev page
        if page > 1:
            prev = '<li><a href ="?page={}">last page</a></li>'.format(page - 1)
        else:
            prev = '<li><a href ="?page={}">last page</a></li>'.format(1)
        page_str_list.append(prev)

        for i in range(start_page,end_page + 1):
            if i == page:
                ele = '<li><a href ="?page={}">{}</a></li>'.format(i,i)
            else:
                ele = '<li><a href ="?page={}">{}</a></li>'.format(i, i)
            page_str_list.append(ele)


        # next page
        if page < total_page_count:
            next = '<li><a href ="?page={}">next page</a></li>'.format(page + 1)
        else:
            next = '<li><a href ="?page={}">next page</a></li>'.format(total_page_count)
        page_str_list.append(next)

        page_string = mark_safe("".join(page_str_list))

        queryset = models.Experiments.objects.filter(user_id=request.session["info"]["id"])[start:end]

        order = "asc"
        tag = "id"
        if request.GET.get('order', False) == "des" and request.GET.get('tag', False) == "id":
            print("herr")
            queryset = models.Experiments.objects.order_by('-id')
            order = "des"
            tag = "id"
        elif request.GET.get('order', False) == "asc" and request.GET.get('tag', False) == "file":
            queryset = models.Experiments.objects.order_by('file_name')
            order = "asc"
            tag = "file"
        elif request.GET.get('order', False) == "des" and request.GET.get('tag', False) == "file":
            queryset = models.Experiments.objects.order_by('-file_name')
            order = "des"
            tag = "file"
        form = CreateForm()
        return render(request, self.template_name, {"queryset": queryset, "form": form, "order": order, "tag": tag, "page_string":page_string})

    def post(self, request, *args, **kwargs):
        form = CreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = models.Users.objects.get(id=request.session["info"]["id"])
            pending = models.PendingExperiments(user=user)
            pending.run_name = form.cleaned_data['run_name']
            pending.file_name = form.files['main_file'].name
            pending.state = "editing"
            pending.main_file = form.files['main_file']
            try:
                data = pd.read_csv(pending.main_file)
            except Exception as e:
                form.add_error('main_file', "Unsupported file, this .csv file has errors")
                return JsonResponse({"status": False, 'error': form.errors})
            pending.set_columns(list(data))
            pending.created_time = timezone.now()
            pending.save()
            return JsonResponse({"status": True, "id": pending.id})

        return JsonResponse({"status": False, 'error': form.errors})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteView(View):
    def get(self, request, *args, **kwargs):
        print(request.GET['id'])
        print(models.Users.objects.all())
        models.Experiments.objects.filter(id=request.GET['id']).delete()
        print(models.Users.objects.all())
        return JsonResponse({"status": True})


class Configuration(View):
    template_name = "Configuration.html"

    def get(self, request, *args, **kwargs):

        exp = models.Experiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()
        form = ConfigForm()
        odms = tools.odm_handling.static_odms_dic()
        print(exp.state)

        return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms": odms})

    def post(self, request, *args, **kwargs):
        form = ConfigForm(data=request.POST, files=request.FILES)
        odms = tools.odm_handling.static_odms_dic()
        exp = models.PendingExperiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()

        print("request.POST: ", request.POST)
        print("request.GET: ", request.GET)

        if form.is_valid():
            print("form.cleaned_data: ", form.cleaned_data)
            print("form.files: ", form.files)
            selected_odm = list(odms.keys())[int(request.POST['odms']) - 1]
            operation = ""

            if form.cleaned_data['operation_model_options'] == '1':
                operation = "all"

            elif form.cleaned_data['operation_model_options'] == '2':
                if not form.cleaned_data['operation_except']:
                    form.add_error('operation_except', "Please enter your excluded subspaces")
                    return render(request, self.template_name,
                                  {"exp": exp, "columns": columns, "form": form, "odms": odms})
                # here parser the subspaces input
                elif not tools.odm_handling.subspace_exclusion_check(form.cleaned_data['operation_except'],
                                                                     len(columns)):
                    print("Please enter correct excluded subspaces")
                    form.add_error('operation_except', "Please enter your excluded subspaces in correct format")
                    return render(request, self.template_name,
                                  {"exp": exp, "columns": columns, "form": form, "odms": odms})
                operation = form.cleaned_data['operation_except']

            elif form.cleaned_data['operation_model_options'] == '3':
                if not form.cleaned_data['operation_written']:
                    form.add_error('operation_written', "Please enter your subspace combination")
                    return render(request, self.template_name,
                                  {"exp": exp, "columns": columns, "form": form, "odms": odms})
                # here parser the subspaces input
                elif not tools.odm_handling.subspace_combination_check(form.cleaned_data['operation_written'],
                                                                       len(columns)):
                    print("Please enter your subspaces")
                    form.add_error('operation_written', "Please enter your subspace combination in correct format")
                    return render(request, self.template_name,
                                  {"exp": exp, "columns": columns, "form": form, "odms": odms})
                operation = form.cleaned_data['operation_written']

            else:
                return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms": odms})

            print("form.cleaned_data: ", form.cleaned_data)
            print("form.files: ", form.files)
            selected_odm = list(odms.keys())[int(request.POST['odms']) - 1]

            # this is specified parameters by user
            parameters = odms[selected_odm].copy()
            for key in parameters.keys():
                para = eval('selected_odm') + '_' + eval('key')
                if request.POST[para]:
                    parameters[key] = request.POST[para]

            exp.odm = form.cleaned_data['odm'] = selected_odm
            exp.set_para(parameters)
            exp.operation = operation
            exp.state = "pending"
            exp.operation_option = form.cleaned_data['operation_model_options']
            exp.has_ground_truth = 'ground_truth' in form.files
            exp.has_generated_file = 'generated_file' in form.files

            if 'ground_truth' in form.files:
                exp.ground_truth = form.files['ground_truth']
            if 'generated_file' in form.files:
                exp.generated_file = form.files['generated_file']

            exp.start_time = timezone.now()

            exp.save()

            DetectorThread(exp.id).start()

            return redirect("/main/")

        return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms": odms})


@method_decorator(csrf_exempt, name='dispatch')
class ResultView(View):
    template_name = "result.html"

    def get(self, request, *args, **kwargs):
        exp = models.FinishedExperiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()
        paras = exp.get_para()
        if exp.state == "pending":
            detected_num = None
        else:
            exp = models.FinishedExperiments.objects.filter(id=request.GET['id']).first()
            detected_num = exp.get_metrics()['Detected Outliers']
        return render(request, self.template_name,
                      {"exp": exp, "columns": columns, "outliers": detected_num, "paras": paras})

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name)


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
