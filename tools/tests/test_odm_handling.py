import os
import random
import re
import unittest
from unittest import TestCase

from tools import odm_handling
import numpy as np


class Test_odm_handling(TestCase):

    def setup(self):
        pass


    def test_get_array_from_csv_data(self):
        data = np.random.random((50, 50))

        listify = []
        for row in data:
            listify.append(list(row))

        self.assertTrue((data == odm_handling.get_array_from_csv_data(listify)).all())

    def test_subspace_exclusion_check(self):
        max_col = random.randint(2, 10)

        empty_string = odm_handling.subspace_exclusion_check("", max_col)
        nonsensical_string = odm_handling.subspace_exclusion_check("not a valid input", max_col)
        exclude_negative = odm_handling.subspace_exclusion_check("-1", max_col)
        exclude_beyond_max = odm_handling.subspace_exclusion_check(str(max_col + 1), max_col)
        valid_picks_list = odm_handling.subspace_exclusion_check(str(max_col - 1), max_col)
        exclude_more_than_possible = odm_handling.subspace_exclusion_check("1,2,3", 0)

        self.assertFalse(empty_string)
        self.assertFalse(nonsensical_string)
        self.assertFalse(exclude_negative)
        self.assertFalse(exclude_beyond_max)
        self.assertTrue(len(valid_picks_list) > 0)
        self.assertFalse(exclude_more_than_possible)

    def test_subspace_combination_check(self):
        max_col = random.randint(2, 10)

        empty_string = odm_handling.subspace_combination_check("", max_col)
        nonsensical_string = odm_handling.subspace_combination_check("not a valid input", max_col)
        include_negative = odm_handling.subspace_combination_check("{-1}", max_col)
        include_beyond_max = odm_handling.subspace_combination_check("{" + str(max_col + 1) + "}", max_col)

        valid_input = odm_handling.subspace_combination_check("{1,2}", max_col)
        valid_input_and = odm_handling.subspace_combination_check("{1,2}&{1}", max_col)
        valid_input_or = odm_handling.subspace_combination_check("{1,2}|{1}", max_col)
        valid_input_and_or = odm_handling.subspace_combination_check("{1,2}&{1}|{1,2}", max_col)

        self.assertFalse(empty_string)
        self.assertFalse(nonsensical_string)
        self.assertFalse(include_negative)
        self.assertFalse(include_beyond_max)

        self.assertTrue(valid_input)
        self.assertTrue(valid_input_and)
        self.assertTrue(valid_input_or)
        self.assertTrue(valid_input_and_or)

    def test_subspace_selection_parser(self):
        pass

    def test_get_head_indexing(self):

        data = np.random.randint(-1000, 1000, (100, 100))
        indexing = odm_handling.get_head_indexing(data)
        headrow = data[0, :]

        for index_tuple in indexing:
            (val, i) = index_tuple
            self.assertEqual(index_tuple, [headrow[int(i)], str(i)])

    def test_get_def_value_dict(self):
        def foo(self, param_1 = 1, param_2 = 2):
            pass
        foo_dict = {"param_1" : 1, "param_2" : 2}
        self.assertEqual(odm_handling.get_def_value_dict(foo), foo_dict)

    def test_get_odm_dict(self):
        odm_dict = odm_handling.get_odm_dict()
        self.assertTrue(len(odm_dict) > 0)

    def test_match_odm_by_name(self):
        odm_dict = odm_handling.get_odm_dict()
        pick = random.choice(list(odm_dict.values()))

        odm_name = str(pick)
        odm_name = odm_name.replace("<class '", "")
        odm_name = odm_name.replace("'>", "")
        odm_name = odm_name.split(".")[3]

        self.assertEqual(pick, odm_dict[odm_name])

    def test_calculate_confusion_matrix(self):
        pred = np.random.randint(0, 1, 100)
        actual = pred = np.random.randint(0, 1, 100)

        (tp_test, fn_test, fp_test, tn_test) = odm_handling.calculate_confusion_matrix(pred, actual)

        tp = 0
        fp = 0
        tn = 0
        fn = 0
        i = 0
        for datapoint in pred:
            if pred[i] and actual[i]:
                tp += 1
            elif pred[i] and (not actual[i]):
                fp += 1
            elif (not pred[i]) and (not actual[i]):
                tn += 1
            elif (not pred[i]) and actual[i]:
                fn += 1
            i += 1

        self.assertEqual(tp, tp_test)
        self.assertEqual(fp, fp_test)
        self.assertEqual(tn, tn_test)
        self.assertEqual(fn, fn_test)

    def test_col_subset(self):
        data = np.random.randint(-1000, 1000, (100, 100))
        selected_col = np.random.randint(0, 99)

        subset = odm_handling.col_subset(data, [selected_col])

        i = 0
        for orig_val in data[:, selected_col]:
            self.assertEqual([orig_val], subset[i])
            i += 1


    def test_operate_and_on_arrays(self):
        pass

    def test_operate_or_on_arrays(self):
        #or_array_1 = np.random.random_integers(0, 2, 100)
        #or_array_2 = np.random.random_integers(0, 2, 100)
        #proba_1 = [[0], [0]] * 100
        #proba_2 = [[0], [0]] * 100
        #(or_array_result, new_proba) = odm_handling.operate_or_on_arrays(or_array_1, proba_1, or_array_2, proba_2)

        #for (a, b, c) in (or_array_1, or_array_2, or_array_result):
            #self.assertEqual(c, a or b)
        pass

    def test_csv_write_and_read(self):
        path = "unit_test_csv.csv"
        write_data = np.random.randint(-1000, 1000, (100, 100))
        odm_handling.write_data_to_csv(path, write_data)
        read_data = odm_handling.get_data_from_csv(path)
        write_data_str = []
        for row in write_data:
            new_row = []
            for val in row:
                new_row.append(str(val))
            write_data_str.append(new_row)

        self.assertEqual(write_data_str, read_data)
        os.remove(path)


if __name__ == '__main__':
    unittest.main()
