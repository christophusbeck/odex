import csv
import os
import threading

import numpy as np
from django.db import OperationalError
from django.utils import timezone

from experiment import models
from tools import odm_handling


class DetectorThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        try:
            # print("detector thread starts")
            # print("exp id:", self.id)
            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            user = exp.user
            exp_odm = odm_handling.match_odm_by_name(exp.odm)
            exp_para = exp.get_para()

            user_csv = odm_handling.get_data_from_csv(exp.main_file.path)
            user_data = odm_handling.get_array_from_csv_data(user_csv[1:])
            # print("user_csv: ", len(user_csv))
            # print("user_data: ", len(user_data))

            exp_operation = exp.operation
            exp_operation_option = exp.operation_option

            included_cols = self.included_columns(exp)
            subspace_combination = []

            if exp_operation_option == "1":
                pass

            elif exp_operation_option == "2":
                excluded_cols = exp_operation.split(",")
                # included_cols = list(range(0, len(user_csv[1:])))

                for excl_col in excluded_cols:
                    included_cols.remove(int(excl_col) - 1)

            elif exp_operation_option == "3":
                subspace_combination = odm_handling.subspace_selection_parser(exp_operation)
                # print("subspace_combination : ", subspace_combination)

            clf = exp_odm(**exp_para)
            outlier_classification = []
            # Here is none, has no outlier_probability.
            outlier_probability = []

            if exp_operation_option == "3":
                or_prediction = list([0] * len(user_data))
                or_probability = list([[1, 0]] * len(user_data))
                for or_selection in subspace_combination:
                    and_prediction = list([1] * len(user_data))
                    and_probability = list([[0, 1]] * len(user_data))
                    for and_selection in or_selection:
                        subspace = odm_handling.get_array_from_csv_data(odm_handling.col_subset(user_csv[1:],
                                                                                                and_selection))
                        clf.fit(subspace)
                        subspace_pred = clf.predict(subspace)
                        subspace_proba = clf.predict_proba(subspace)
                        and_prediction, and_probability = odm_handling.operate_and_on_arrays(and_prediction,
                                                                                             and_probability,
                                                                                             subspace_pred,
                                                                                             subspace_proba)
                    or_prediction, or_probability = odm_handling.operate_or_on_arrays(or_prediction, or_probability,
                                                                                      and_prediction, and_probability)
                outlier_classification = or_prediction
                outlier_probability = or_probability

            else:

                # print("included_cols 1: ", included_cols)
                user_data = odm_handling.get_array_from_csv_data(odm_handling.col_subset(user_csv[1:], included_cols))

                clf.fit(user_data)

                outlier_classification = clf.predict(user_data)
                outlier_probability = clf.predict_proba(user_data)

            metrics = {}
            metrics["Number of entities"] = len(user_data)
            metrics["Detected Outliers"] = sum(outlier_classification)

            ground_truth_array = np.ndarray
            if exp.ground_truth != "":
                ground_truth_csv = odm_handling.get_data_from_csv(exp.ground_truth.path)
                ground_truth_array = odm_handling.get_array_from_csv_data(ground_truth_csv)

                if ground_truth_array.sum() == 0 or ground_truth_array.sum() == len(ground_truth_array):
                    raise Exception(
                        "No meaningful calculation of metrics is possible with the uploaded ground truth file.")

                tp, fn, fp, tn = odm_handling.calculate_confusion_matrix(outlier_classification, ground_truth_array)
                print("tp, fn, fp, tn:", tp, fn, fp, tn)
                metrics["True positives"] = tp
                metrics["False positives"] = fp
                metrics["True negatives"] = tn
                metrics["False negatives"] = fn

                metrics["Precision"] = '{:.5%}'.format(tp / (tp + fp))
                metrics["Accuracy"] = (tp + tn) / (tp + tn + fp + fn)
                metrics["Recall"] = '{:.5%}'.format(tp / (tp + fn))

                roc_path = "media/" + models.user_roc_path(exp.main_file.name)
                odm_handling.picture_ROC_curve(ground_truth_array, outlier_probability, roc_path)

            if exp.generated_file != "":
                user_gen_csv = odm_handling.get_data_from_csv(exp.generated_file.path)
                user_gen_data = odm_handling.get_array_from_csv_data(
                    odm_handling.col_subset(user_csv[1:], included_cols))
                merged_data = np.concatenate((user_data, user_gen_data))
                clf_merge = exp_odm(**exp_para)
                metrics["Number of additional rows"] = len(user_gen_data)
                metrics["Number of entities after merging"] = len(merged_data)

                if exp_operation_option == "3":
                    or_prediction = list([0] * len(user_data))
                    or_probability = list([[1, 0]] * len(user_data))
                    for or_selection in subspace_combination:
                        and_prediction = list([1] * len(user_data))
                        and_probability = list([[0, 1]] * len(user_data))
                        for and_selection in or_selection:
                            subspace = odm_handling.get_array_from_csv_data(odm_handling.col_subset(merged_data[0:],
                                                                                                    and_selection))
                            clf_merge.fit(subspace)
                            subspace_pred = clf.predict(subspace)
                            subspace_proba = clf.predict_proba(subspace)
                            and_prediction, and_probability = odm_handling.operate_and_on_arrays(and_prediction,
                                                                                                 and_probability,
                                                                                                 subspace_pred,
                                                                                                 subspace_proba)
                        or_prediction, or_probability = odm_handling.operate_or_on_arrays(or_prediction, or_probability,
                                                                                          and_prediction,
                                                                                          and_probability)
                    outlier_classification_after_merge = or_prediction
                    outlier_probability_after_merge = or_probability

                else:

                    clf_merge.fit(merged_data)
                    outlier_classification_after_merge = clf_merge.predict(merged_data)
                    outlier_probability_after_merge = clf_merge.predict_proba(merged_data)

                metrics["Detected Outliers after merging with generated data"] = sum(
                    outlier_classification_after_merge)

                if exp.ground_truth != "":
                    ground_truth_gen_array = np.concatenate((ground_truth_array, [[1]] * len(user_gen_data)))
                    (tp_gen, fp_gen, fn_gen, tn_gen) = odm_handling.calculate_confusion_matrix(
                        outlier_classification_after_merge,
                        ground_truth_gen_array)
                    metrics["True positives after merging"] = tp_gen
                    metrics["False positives after merging"] = fp_gen
                    metrics["True negatives after merging"] = tn_gen
                    metrics["False negatives after merging"] = fn_gen

                    metrics["Precision after merging"] = '{:.5%}'.format(tp_gen / (tp_gen + fp_gen))
                    metrics["Accuracy after merging"] = (tp_gen + tn_gen) / (tp_gen + tn_gen + fp_gen + fn_gen)
                    metrics["Recall after merging"] = '{:.5%}'.format(tp_gen / (tp_gen + fn_gen))

                    metrics["Delta accuracy (merged - original)"] = metrics["Accuracy after merging"] - metrics[
                        "Accuracy"]
                    metrics["Delta accuracy (merged - original)"] = '{:.5%}'.format(
                        metrics["Delta accuracy (merged - original)"])
                    metrics["Accuracy after merging"] = '{:.5%}'.format(metrics["Accuracy after merging"])

                    roc_after_merge_path = "media/" + models.user_roc_path(exp.generated_file.name)
                    odm_handling.picture_ROC_curve(ground_truth_array, outlier_probability_after_merge,
                                                   roc_after_merge_path)

            if "Accuracy" in metrics.keys():
                metrics["Accuracy"] = '{:.5%}'.format(metrics["Accuracy"])

            result_csv_path = "media/" + models.user_result_path(exp, exp.file_name)
            result_with_addition_path = "media/" + models.user_result_with_addition_path(exp, exp.file_name)
            result_csv = []
            result_with_addition = []
            res_headline = []
            i = 0

            # res_headline = user_csv[0]
            # print("res_headline: ",res_headline)
            # print("res_headline type : ", type(res_headline))
            res_headline.append("Id")
            res_headline.append("Probability")
            res_headline.append("Classification")
            if exp.ground_truth != "":
                res_headline.append("Ground truth")
            result_csv.append(res_headline)
            if exp.generated_file != "":
                result_with_addition.append(res_headline)

            for row in user_csv[1:]:
                result_row = []
                result_row.append(i + 1)
                result_row.append(outlier_probability[i])
                result_row.append(outlier_classification[i])
                if exp.ground_truth != "":
                    result_row.append(str(int(ground_truth_array[i][0])))
                result_csv.append(result_row)
                if exp.generated_file != "":
                    result_with_addition_row = []
                    result_with_addition_row.append(i + 1)
                    result_with_addition_row.append(outlier_probability_after_merge[i])
                    result_with_addition_row.append(outlier_classification_after_merge[i])
                    if exp.ground_truth != "":
                        result_with_addition_row.append(str(int(ground_truth_array[i][0])))
                    result_with_addition.append(result_with_addition_row)
                i += 1
            odm_handling.write_data_to_csv(result_csv_path, result_csv)
            odm_handling.write_data_to_csv(result_with_addition_path, result_with_addition)

            # exp = models.PendingExperiments.objects.filter(id=self.id).first()
            # user = exp.user
            models.PendingExperiments.objects.filter(id=self.id).delete()
            finished_exp = models.FinishedExperiments()
            finished_exp.user_id = user.id
            finished_exp.id = self.id
            finished_exp.run_name = exp.run_name
            finished_exp.file_name = exp.file_name
            finished_exp.state = models.Experiment_state.finished
            finished_exp.columns = exp.columns
            finished_exp.created_time = exp.created_time
            finished_exp.start_time = exp.start_time
            finished_exp.operation = exp.operation
            finished_exp.odm = exp.odm
            finished_exp.parameters = exp.parameters
            finished_exp.operation_option = exp.operation_option
            finished_exp.has_ground_truth = exp.has_ground_truth
            finished_exp.has_generated_file = exp.has_generated_file
            finished_exp.result = models.user_result_path(exp, exp.file_name)
            finished_exp.result_with_addition = models.user_result_with_addition_path(exp, exp.file_name)
            finished_exp.set_metrics(metrics)
            finished_exp.metrics_file = models.user_metrics_path(exp, exp.file_name)

            if exp.has_ground_truth:
                # print("models.user_roc_path(exp, exp.main_file): ", models.user_roc_path(exp.main_file.name) )
                finished_exp.roc_path = models.user_roc_path(exp.main_file.name)

                if finished_exp.has_generated_file:
                    # print("models.user_roc_path(exp, exp.generated_file.name): ", models.user_roc_path(exp.generated_file.name))
                    finished_exp.roc_after_merge_path = models.user_roc_path(exp.generated_file.name)

            duration = timezone.now() - exp.start_time

            # print("timezone.now(): ", timezone.now())
            # print("exp.start_time: ", exp.start_time)
            # print("duration: ", duration)
            # print("duration.type: ", type(duration))
            # print("start_time.type: ", type(exp.start_time))

            finished_exp.duration = duration
            finished_exp.full_clean()
            finished_exp.save()

            os.remove(exp.main_file.path)
            if exp.has_ground_truth:
                os.remove(exp.ground_truth.path)
            if exp.has_generated_file:
                os.remove(exp.generated_file.path)

            # print("metrics: ", metrics)

            metrics_path = "media/" + models.user_metrics_path(finished_exp, finished_exp.file_name)
            odm_handling.write_data_to_csv(metrics_path, self.metrics_to_csv(finished_exp, metrics))

        except OperationalError as e:
            print("Error occured")
            print(e)

        except Exception as e:
            try:
                # print("exp id:", self.id)
                exp = models.PendingExperiments.objects.filter(experiments_ptr_id=self.id).first()
                exp.state = models.Experiment_state.failed
                exp.error = "There are some error related to your entered hyperparameters of odm you seleted. The error message is: \n\n" + \
                            str(e) + ".\n\n This error message will help you adjust the hyperparameters. " \
                                     "In some cases, it is also possible that there is an error in the file you uploaded or your seleted subspaces. " \
                                     "Please check the column you want to execute to ensure that there are no null values or uncalculated values. "
                exp.full_clean()
                exp.save()
            except Exception as ee:
                print("Error occured by setting failed")
                print(ee)

    # maybe there are some columns without value
    def included_columns(self, exp):
        included_cols = []
        with open(exp.main_file.path, 'r') as f:
            reader = csv.reader(f)
            result = list(reader)
            for i in range(len(result[0])):
                if not result[0][i]:
                    continue
                included_cols.append(i)
        return included_cols

    def metrics_to_csv(self, exp, metrics):
        headers = []
        values = []

        headers.append("file name")
        values.append(exp.file_name)

        headers.append("start time")
        values.append(exp.start_time)

        headers.append("duration")
        values.append(exp.duration)

        headers.append("selected subspaces")
        values.append(exp.get_operation_option_display() + exp.operation)

        headers.append("selected odm")
        values.append(exp.odm)

        headers.append("hyper parameters")
        values.append(exp.parameters)

        for header, value in metrics.items():
            headers.append(header)
            values.append(value)
        data = [headers, values]
        return data
