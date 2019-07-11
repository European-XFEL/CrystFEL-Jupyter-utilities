import matplotlib.pyplot
import os
import sys

import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.getcwd())
from widget import Span


class Test_Span(unittest.TestCase):
    @patch('histogram.Histogram')
    @patch('matplotlib.pyplot')
    def setUp(self, Mock_plt, Mock_hist):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.all_crystals_list = [{'name': 'Image filename: db.h5',
                                   'a': 1, 'b': 1,
                                   'c': 1, 'alfa': 90,
                                   'beta': 90, 'gamma': 90,
                                   'lattice_type': "monoclinic",
                                   'centering': "C", "unique_axis": "b"},
                                  {'name': 'Image filename: db2.cxi',
                                   'a': 40, 'b': 40,
                                   'c': 40, 'alfa': 120,
                                   'beta': 120, 'gamma': 120,
                                   'lattice_type': "triclinic",
                                   'centering': "P", "unique_axis": "b"}]
        self.crystals_excluded = []
        self.index = 1
        self.name = "test_name"
        self.mock_hist = Mock_hist
        self.mock_hist.name = 'a'
        self.histogram_list = [self.mock_hist, self.mock_hist, self.mock_hist,
                               self.mock_hist, self.mock_hist, self.mock_hist]
        self.span = Span(fig=self.fig, histogram_list=self.histogram_list,
                         index=self.index, name=self.name,
                         all_crystals_list=self.all_crystals_list,
                         crystals_excluded=self.crystals_excluded,
                         )

    def test_onselect(self):
        self.span.onselect(20, 100)
        self.assertEqual(
            self.mock_hist.bool_crystal_exluded_green_space.call_count, 2)
        assert self.histogram_list[self.index].set_range_green_space.called
        self.histogram_list[
            self.index].set_range_green_space.assert_called_once_with(
                20, 100)
        self.histogram_list[
            self.index].set_was_clicked_before.assert_called_once_with(True)
        self.assertEqual(len(self.crystals_excluded), 2)

    @patch('widget.crystlib')
    def test_data_update(self, Mock_crystlib):
        self.span.data_update()

        assert Mock_crystlib.histograms_data.called
        Mock_crystlib.histograms_data.assert_called_once_with(
            Span.get_crystals_included_list())
        for i in range(5):
            assert self.histogram_list[i].set_data.called
            assert self.histogram_list[i].update.called
if __name__ == '__main__':
        unittest.main()
