import threading
from django.utils import timezone

from experiment import models
from tools import odm_handling

class DetectorThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        # try:
            print("detector thread starts")
            print(self.id)
            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            exp_odm = odm_handling.match_odm_by_name(exp.odm)
            exp_para = exp.get_para()
            exp_op = exp.operation

            print("exp_odm: ", exp_odm)
            print("exp_parameters: ", exp_para)
            print("exp_operation: ", exp_op)

            user_csv = odm_handling.get_data_from_csv(exp.main_file)
            user_data = odm_handling.get_array_from_csv_data(user_csv[1:])

            print("open file successfully")

            clf = exp_odm(**exp_para)
            clf.fit(self, user_data)

            outlier_classification = clf.predict(self, user_data)

            print("outlier classification: ", outlier_classification)

            metrics = {}
            metrics["Detected Outliers"] = sum(outlier_classification)


            result_csv = []
            result_csv.append(user_csv[1])
            for (row, i) in user_data:
                if outlier_classification[i]:
                    result_csv.append(row)
            result_csv_path = exp.user_id + "/" + exp.id + "/results_" + exp.file_name
            odm_handling.write_data_to_csv(result_csv_path, result_csv)

            if exp.ground_truth != "":
                ground_truth_csv = odm_handling.get_data_from_csv(exp.ground_truth)
                ground_truth_array = odm_handling.get_array_from_csv_data(ground_truth_csv)

                (tp, fp, fn, tn) = odm_handling.calculate_confusion_matrix(outlier_classification, ground_truth_array)
                metrics["True positives"] = tp
                metrics["False positives"] = fp
                metrics["True negatives"] = tn
                metrics["False positives"] = fn

                metrics["Precision"] = tp / (tp + fp)
                metrics["Recall"] = tp / (tp + fn)

            if exp.generated_file != "":
                user_gen_csv = odm_handling.get_data_from_csv(exp.generated_file)
                user_gen_data = odm_handling.get_array_from_csv_data(user_gen_csv[1:])
                merged_data = user_data + user_gen_data
                clf_merge = exp_odm(**exp_para)
                clf_merge.fit(self, merged_data)
                outlier_classification_after_merge = clf_merge.predict(self, merged_data)
                metrics["Detected Outliers after merging with generated data"] = sum(outlier_classification_after_merge)

            duration = exp.start_time - timezone.now()
            print(metrics)

            f_exp = models.FinishedExperiments(exp, metrics, result_csv_path, duration)
            print("detector finished")




        # except Exception as e:
        #     print("Error occur")
        #     print(e)




