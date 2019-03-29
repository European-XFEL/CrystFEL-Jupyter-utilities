import unittest
from unittest.mock import patch, Mock
import os
import sys
import matplotlib.pyplot
sys.path.insert(0, os.getcwd())

from widget import Span


class Test_Span(unittest.TestCase):
    @patch('crystlib.Crystal')
    @patch('histogram.Histogram')
    @patch('matplotlib.pyplot')
    def setUp(self, Mock_plt, Mock_hist, Mock_crystal):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.all_crystals_list = [Mock_crystal(), Mock_crystal(),
                                  Mock_crystal(), Mock_crystal(),
                                  Mock_crystal(), Mock_crystal()]
        self.crystals_excluded_list = []
        self.index = 1
        self.name = "test_name"
        self.histogram_list = [Mock_hist(), Mock_hist(), Mock_hist(),
                               Mock_hist(), Mock_hist(), Mock_hist()]
        self.span = Span(fig=self.fig, histogram_list=self.histogram_list,
                         index=self.index, name=self.name,
                         all_crystals_list=self.all_crystals_list,
                         crystals_excluded_list=self.crystals_excluded_list,
                         )

    def test_onselect(self):
        self.span.onselect(20, 100)
        assert self.histogram_list[self.index].set_range_green_space.called
        self.histogram_list[self.index].set_range_green_space.assert_called_once_with(20,100)
        self.histogram_list[self.index].set_was_clicked_before.assert_called_once_with(True)
        assert self.histogram_list[0].bool_crystal_exluded_green_space.called
        assert self.histogram_list[1].bool_crystal_exluded_green_space.called
        assert self.histogram_list[2].bool_crystal_exluded_green_space.called
        assert self.histogram_list[3].bool_crystal_exluded_green_space.called
        assert self.histogram_list[4].bool_crystal_exluded_green_space.called
        assert self.histogram_list[5].bool_crystal_exluded_green_space.called

    @patch('widget.crystlib')
    def test_data_update(self, Mock_crystlib):
        self.span.data_update()

        assert Mock_crystlib.dict_data_histogram.called
        Mock_crystlib.dict_data_histogram.assert_called_once_with(Span.get_crystals_included_list())
        for i in range(0, 5):
            assert self.histogram_list[i].set_data.called
            assert self.histogram_list[i].update.called

if __name__ == '__main__':
        unittest.main()
