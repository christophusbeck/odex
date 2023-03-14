import csv
import json

import pandas as pd
from datetime import datetime, date, time, timedelta

from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone

import tools.odm_handling
from tools.detector_thread import DetectorThread
from experiment.forms import CreateForm, ConfigForm
from experiment import models

from django.http import JsonResponse, FileResponse, Http404
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
        return render(request, self.template_name, {"form": form})
        # return render(request, self.template_name, {"queryset": queryset, "form": form})

    def post(self, request, *args, **kwargs):
        form = CreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = models.Users.objects.get(id=request.session["info"]["id"])
            pending = models.PendingExperiments(user=user)
            pending.run_name = form.cleaned_data['run_name']
            pending.file_name = form.files['main_file'].name
            pending.state = models.Experiment_state.editing
            pending.main_file = form.files['main_file']
            print("form.files['main_file']: ", form.files['main_file'])

            try:
                data = pd.read_csv(pending.main_file)
            except Exception as e:
                form.add_error('main_file', "Unsupported file, this .csv file has errors")
                return JsonResponse({"status": False, 'error': form.errors})

            pending.full_clean()
            pending.save()

            with open(pending.main_file.path, 'r') as f:
                reader = csv.reader(f)
                result = list(reader)
                first_row = result[1]
                columns = {}
                for i in range(len(list(data))):
                    if not result[0][i]:
                        continue
                    columns[list(data)[i]] = first_row[i]
                pending.set_columns(columns)

            pending.created_time = timezone.now()
            pending.full_clean()
            pending.save()
            print("columns: ", pending.columns)
            print("timezone.now().type: ", type(timezone.now()))
            print("pending.created_time.type: ", type(pending.created_time))
            return JsonResponse({"status": True, "id": pending.id})

        return JsonResponse({"status": False, 'error': form.errors})


@method_decorator(csrf_exempt, name='dispatch')
class DeleteView(View):
    def get(self, request, *args, **kwargs):
        models.Experiments.objects.filter(id=request.GET['id']).first().delete()
        return JsonResponse({"status": True})


class ConfigView(View):
    template_name = "Configuration.html"

    def get(self, request, *args, **kwargs):
        exp = models.PendingExperiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()
        form = ConfigForm()
        odms = tools.odm_handling.static_odms_dic()
        id = request.GET['id']

        return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms": odms, "id": id})

    def post(self, request, *args, **kwargs):
        print("request.POST: ", request.POST)
        print("request.GET: ", request.GET)

        form = ConfigForm(data=request.POST, files=request.FILES)
        odms = tools.odm_handling.static_odms_dic()
        exp = models.PendingExperiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()


        if form.is_valid():
            print("form.cleaned_data: ", form.cleaned_data)
            print("form.files: ", form.files)
            # selected_odm = list(odms.keys())[int(request.POST['odms']) - 1]
            # operation = ""

            if form.cleaned_data['operation_model_options'] == '1':
                operation = ""

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

                picks = tools.odm_handling.subspace_exclusion_check(form.cleaned_data['operation_except'],
                                                                    len(columns))
                operation = json.dumps(picks).replace("\"", "").replace("[", "").replace("]", "")

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
            for key, value in parameters.items():
                para = eval('selected_odm') + '_' + eval('key')
                if request.POST.get(para, False):
                    try:
                        parameters[key] = type(value)(request.POST[para])
                    except ValueError as e:
                        form.add_error(None, "Input error by " + para + ": " + str(e))
                        return render(request, self.template_name,
                                      {"exp": exp, "columns": columns, "form": form, "odms": odms})

            exp.odm = selected_odm
            print("parameters: ", parameters)
            print("parameters_type: ",
                  " parameters_type: ".join([str(type(value)) for key, value in parameters.items()]))
            exp.set_para(parameters)
            exp.operation = operation
            exp.state = models.Experiment_state.pending
            exp.operation_option = form.cleaned_data['operation_model_options']
            exp.has_ground_truth = 'ground_truth' in form.files
            exp.has_generated_file = 'generated_file' in form.files

            if 'ground_truth' in form.files:
                exp.ground_truth = form.files['ground_truth']
                print("form.files['ground_truth']: ", form.files['ground_truth'])
            if 'generated_file' in form.files:
                exp.generated_file = form.files['generated_file']
                print("form.files['generated_file']: ", form.files['generated_file'])

            exp.start_time = timezone.now()

            exp.full_clean()
            exp.save()

            DetectorThread(exp.id).start()

            return redirect("/main/")

        return render(request, self.template_name, {"exp": exp, "columns": columns, "form": form, "odms": odms})


@method_decorator(csrf_exempt, name='dispatch')
class ResultView(View):
    template_name = "result.html"

    def get(self, request, *args, **kwargs):
        """--------------------- only pending and finished exp can access this get function ---------------------"""
        exp = models.Experiments.objects.filter(id=request.GET['id']).first()
        columns = exp.get_columns()
        print("on reslut page, coulums: ", columns)
        paras = exp.get_para()
        print("on result page, paras: ", paras)
        if exp.state == models.Experiment_state.pending:
            exp = models.PendingExperiments.objects.filter(id=request.GET['id']).first()
            return render(request, self.template_name, {"exp": exp, "columns": columns, "paras": paras})
        else:
            exp = models.FinishedExperiments.objects.filter(id=request.GET['id']).first()
            metrics = exp.get_metrics()
            detected_num = metrics['Detected Outliers']
            performance = dict((key, value) for key, value in metrics.items() if key != "Detected Outliers"
                               and key != "Detected Outliers after merging with generated data")

            if exp.has_generated_file:
                detected_additional_num = metrics['Detected Outliers after merging with generated data']
                return render(request, self.template_name,
                              {"exp": exp, "columns": columns, "paras": paras,
                               "outliers": detected_num, "performance": performance,
                               "outliers_generated": detected_additional_num})

            return render(request, self.template_name, {"exp": exp, "columns": columns, "paras": paras,
                                                        "outliers": detected_num, "performance": performance})


@method_decorator(csrf_exempt, name='dispatch')
class ExperimentListView(View):
    def post(self, request, *args, **kwargs):
        uid = request.session["info"]["id"]
        result = models.Experiments.objects.filter(user_id=uid).all().order_by('-id')

        #     .values(
        #     "id", "run_name", "created_time", "state", "odm", "file_name",
        #     "operation", "operation_option", "start_time", "duration"
        # ).order_by('-id')
        total = result.count()

        rows = self.row_generator(result)
        data = {'total': total, 'rows': rows}
        print(data)
        return JsonResponse(data, safe=False)

    def encoder(self, o):
        if isinstance(o, (datetime, date, time)):
            return o.strftime('%m.%d.%Y %H:%M:%S')
        if isinstance(o, timedelta):
            return o.total_seconds()

    def row_generator(self, result):
        rows = []
        selected_records = {"id", "run_name", "created_time", "state", "odm", "file_name",
                            "operation", "start_time", "duration"}
        for item in result:
            item_dict = model_to_dict(item)
            for k, v in item_dict.items():
                if 'time' in k or 'duration' in k:
                    item_dict[k] = self.encoder(v)
                elif k == 'operation':
                    if item_dict[k] is None:
                        item_dict[k] = str(v)
                elif k == 'operation_option':
                    if item_dict[k] is None:
                        item_dict[k] = str(v)
                    else:
                        item_dict[k] = item.get_operation_option_display()
            item_dict['operation'] = item_dict['operation_option'] + item_dict['operation']
            row = {k: v for k, v in item_dict.items() if k in selected_records}
            rows.append(row)
        return rows


# @method_decorator(csrf_exempt, name='dispatch')
# class DownloadView(View):
#     def get(self, request, *args, **kwargs):
#         exp = models.FinishedExperiments.objects.filter(id=request.GET['id']).first()
#         print(exp.id)
#         file_path = exp.result.path
#         if os.path.exists(file_path):
#             try:
#                 response = FileResponse(open(file_path, 'rb'))
#                 response['content_type'] = "application/octet-stream"
#                 response['Content-Disposition'] = 'attachment; filename=' + format(filename)
#                 return response
#             except Exception:
#                 raise Http404
