import unittest

import CrystFEL_Jupyter_utilities.crystlib as crystlib


class TestCrystlib(unittest.TestCase):
    def setUp(self):
        self.crystals = [{'centering': 'P','a': 10, 'b': 10, 'c': 10,
                          'alfa': 80, 'beta': 80, 'gamma': 80},
                         {'centering': 'C','a': 22, 'b': 22, 'c': 32,
                          'alfa': 89, 'beta': 90, 'gamma': 92},
                         {'centering': 'C','a': 31, 'b': 200, 'c': 120,
                          'alfa': 90, 'beta': 90, 'gamma': 90}]
        
    def test_crystal_search(self):
        test_value = crystlib.crystal_search([], None)
        self.assertEqual(test_value, {})
        test_value = crystlib.crystal_search(self.crystals, 'a')
        self.assertEqual(test_value, {'P': [10], 'C': [22, 31]})
        test_value = crystlib.crystal_search(self.crystals, 'beta')
        self.assertEqual(test_value, {'P': [80], 'C': [90, 90]})

    def test_histograms_data(self):
        test_value = crystlib.histograms_data(self.crystals)
        self.assertEqual(test_value, {'a': {'P': [10], 'C': [22, 31]},
                                      'b': {'P': [10], 'C': [22, 200]},
                                      'c': {'P': [10], 'C': [32, 120]},
                                      'alfa': {'P': [80], 'C': [89, 90]},
                                      'beta': {'P': [80], 'C': [90, 90]},
                                      'gamma': {'P': [80], 'C': [92, 90]}})


if __name__ == '__main__':
    unittest.main()
