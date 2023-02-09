import os
import threading

import numpy as np
from django.utils import timezone

from experiment import models
from tools import odm_handling

class DetectorThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        try:
            print("detector thread starts")
            print("exp id:", self.id)
            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            exp_odm = odm_handling.match_odm_by_name(exp.odm)
            exp_para = exp.get_para()

            user_csv = odm_handling.get_data_from_csv(exp.main_file.path)
            user_data = odm_handling.get_array_from_csv_data(user_csv[1:])

            print("exp_odm: ", exp_odm)
            print("exp_para: ", exp_para)

            exp_operation = exp.operation
            exp_operation_option = exp.operation_option

            if exp_operation_option == 1:
                assert(exp_operation, "")
                # TODO: run main file with all subspace, by this time the exp_operation = ""

            elif exp_operation_option == 2:
                # TODO: run main file with all, except, by this time the exp_operation is like 1,2,3...,
                #  that is the excluded columns
                pass

            elif exp_operation_option == 3:
                # TODO: run main file with conbination, by this time the exp_operation is like {1,2}&{1,3}...
                pass

            # TODO: by the way, the checking of" "all,except" is not perfect.
            #  If the file has only 2 column, I enter like 123, It can also run.


            clf = exp_odm(**exp_para)
            clf.fit(user_data)

            outlier_classification = clf.predict(user_data)
            outlier_probability = clf.predict_proba(user_data)

            metrics = {}
            metrics["Detected Outliers"] = sum(outlier_classification)

            ground_truth_array = np.ndarray
            if exp.ground_truth != "":
                ground_truth_csv = odm_handling.get_data_from_csv(exp.ground_truth.path)
                ground_truth_array = odm_handling.get_array_from_csv_data(ground_truth_csv)

                (tp, fp, fn, tn) = odm_handling.calculate_confusion_matrix(outlier_classification, ground_truth_array)
                metrics["True positives"] = tp
                metrics["False positives"] = fp
                metrics["True negatives"] = tn
                metrics["False negatives"] = fn

                metrics["Precision"] = tp / (tp + fp)
                metrics["Accuracy"] = (tp + tn) / (tp + tn + fp + fn)
                metrics["Recall"] = tp / (tp + fn)

            if exp.generated_file != "":
                user_gen_csv = odm_handling.get_data_from_csv(exp.generated_file.path)
                user_gen_data = odm_handling.get_array_from_csv_data(user_gen_csv[1:])
                merged_data = np.concatenate((user_data, user_gen_data))
                clf_merge = exp_odm(**exp_para)
                clf_merge.fit(merged_data)
                outlier_classification_after_merge = clf_merge.predict(merged_data)
                metrics["Detected Outliers after merging with generated data"] = sum(outlier_classification_after_merge)

                if exp.ground_truth != "":
                    ground_truth_gen_array = np.concatenate((ground_truth_array, [[1]] * len(user_gen_data)))
                    (tp_gen, fp_gen, fn_gen, tn_gen) = odm_handling.calculate_confusion_matrix(
                        outlier_classification_after_merge,
                        ground_truth_gen_array)
                    metrics["True positives after merging"] = tp_gen
                    metrics["False positives after merging"] = fp_gen
                    metrics["True negatives after merging"] = tn_gen
                    metrics["False negatives after merging"] = fn_gen

                    metrics["Precision"] = tp_gen / (tp_gen + fp_gen)
                    metrics["Accuracy"] = (tp_gen + tn_gen) / (tp_gen + tn_gen + fp_gen + fn_gen)
                    metrics["Recall"] = tp_gen / (tp_gen + fn_gen)

            result_csv_path = "media/" + models.user_result_path(exp, exp.file_name)
            result_csv = []
            i = 0
            res_headline = user_csv[0]
            res_headline.append("Probability")
            res_headline.append("Classification")
            if exp.ground_truth != "":
                res_headline.append("Ground truth")
            result_csv.append(res_headline)
            for row in user_csv[1:]:
                row.append(outlier_probability[i])
                row.append(outlier_classification[i])
                if exp.ground_truth != "":
                    row.append(str(int(ground_truth_array[i][0])))
                result_csv.append(row)
                i += 1
            odm_handling.write_data_to_csv(result_csv_path, result_csv)

            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            user = exp.user
            models.PendingExperiments.objects.filter(id=self.id).delete()
            finished_exp = models.FinishedExperiments()
            finished_exp.user_id = user.id
            finished_exp.id = self.id
            finished_exp.run_name = exp.run_name
            finished_exp.file_name = exp.file_name
            finished_exp.state = "finished"
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
            finished_exp.set_metrics(metrics)

            duration = timezone.now() - exp.start_time
            finished_exp.duration = duration
            finished_exp.save()
            print("finished_exp.metric: ", finished_exp.metrics)
            os.remove(exp.main_file.path)
            if exp.has_ground_truth:
                os.remove(exp.ground_truth.path)
            if exp.has_generated_file:
                os.remove(exp.generated_file.path)

        except Exception as e:
            print("Error occured")
            print(e)
            print("exp id:", self.id)
            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            exp.state = 'failed'
            exp.save()




