import unittest
from tools import odm_handling
import numpy as np

class Test_odm_handling(unittest.TestCase):


    def setup(self):
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


if __name__ == '__main__':
    unittest.main()
