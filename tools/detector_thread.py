import threading

from experiment import models


class DetectorThread(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)

    def run(self):
        try:
            print("detector thread starts")
            print(self.id)
            exp = models.PendingExperiments.objects.filter(id=self.id).first()
            exp_odm = exp.odm
            exp_para = exp.parameters
            print("exp_odm: ", exp_odm)
            print("exp_para: ", exp_para)
        except Exception as e:
            print(e)




