import csv
import inspect
import numpy as np
import re

from pyod.models.abod import ABOD
#from pyod.models.auto_encoder import AutoEncoder
from pyod.models.cblof import CBLOF
from pyod.models.cof import COF
from pyod.models.copod import COPOD
from pyod.models.ecod import ECOD
from pyod.models.feature_bagging import FeatureBagging
from pyod.models.gmm import GMM
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.inne import INNE
from pyod.models.kde import KDE
from pyod.models.kpca import KPCA
from pyod.models.lmdd import LMDD
from pyod.models.loda import LODA
from pyod.models.lof import LOF
from pyod.models.loci import LOCI
from pyod.models.lunar import LUNAR
from pyod.models.mad import MAD
from pyod.models.mcd import MCD
from pyod.models.ocsvm import OCSVM
from pyod.models.rgraph import RGraph
from pyod.models.pca import PCA
from pyod.models.rod import ROD
from pyod.models.sampling import Sampling
#from pyod.models.vae import VAE


def write_data_to_csv(path: str, data):
    writefile = open(path, 'w', newline='')
    writer = csv.writer(writefile, delimiter=',')
    for row in data:
        writer.writerow(row)
    writefile.close()
    pass


def get_data_from_csv(path: str) -> list[list[str]]:
    results = []
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            results.append(row)

    return results


def get_array_from_csv_data(data: list[list[str]]):
    results = []
    for row in data:
        floatrow = []
        for item in row:
            floatrow.append(float(item))
        results.append(floatrow)
    return np.array(results)

def subspace_combination_check(user_choice: str, max_col):
    user_choice = user_choice.replace(" ", "")
    combination_regex = '((\\{)((([0-9]+)\\,)*)([0-9]+)\\})([&|](\\{)((([0-9]+)\\,)*)([0-9]+)\\})*'
    if re.match(combination_regex, user_choice):
        user_choice = user_choice.replace("&", ",")
        user_choice = user_choice.replace("|", ",")
        user_choice = user_choice.replace("{", "")
        user_choice = user_choice.replace("}", "")
        picks = user_choice.split(",")
        for pick in picks:
            if int(pick) > max_col:
                return False
        return True
    return False


def subspace_selection_parser(user_choice: str):
    pass


def get_head_indexing(data: list[list[str]]):
    headrow = data[0]
    index = 0
    results = []
    for item in headrow:
        results.append([item, str(index)])
        index += 1
    return results


def get_def_value_dict(constructor):
    d = {}
    for (i, key) in enumerate(inspect.getfullargspec(constructor).args):
        if key != "self":
            d[key] = inspect.getfullargspec(constructor).defaults[i - 1]
    return d


def get_list_of_odm():
    odm_dict = get_odm_dict()
    return odm_dict.keys()


def get_odm_dict():
    odm_dict = {
        "ABOD": ABOD,
        #"AutoEncoder": AutoEncoder,
        "CBLOF": CBLOF,
        "COF": COF,
        "COPOD": COPOD,
        "ECOD": ECOD,
        "FeatureBagging": FeatureBagging,
        "GMM": GMM,
        "HBOS": HBOS,
        "IForest": IForest,
        "INNE": INNE,
        "KDE": KDE,
        "KPCA": KPCA,
        "LMDD": LMDD,
        "LODA": LODA,
        "LOF": LOF,
        "LOCI": LOCI,
        "LUNAR": LUNAR,
        "MAD": MAD,
        "MCD": MCD,
        "OCSVM": OCSVM,
        "PCA": PCA,
        "RGraph": RGraph,
        "ROD": ROD,
        "Sampling": Sampling,
        #"VAE": VAE,
    }
    return odm_dict

def match_odm_by_name(name:str):
    odm_dict = get_odm_dict()
    if odm_dict.keys().__contains__(name):
        return odm_dict[name]
    return ABOD  # arbitrary default option

def calculate_confusion_matrix(prediction, actual):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for (datapoint, i) in prediction:
        if prediction[i] and actual[i]:
            tp += 1
        elif prediction[i] and (not actual[i]):
            fp += 1
        elif (not prediction[i]) and (not actual[i]):
            tn +=1
        elif (not prediction[i]) and actual[i]:
            fn += 1
    return tp, fn, fp, tn


def static_odms_dic():
    odms = {}
    for d in get_odm_dict():
        odm_para = get_def_value_dict(match_odm_by_name(d))
        odms[d] = odm_para
    return odms