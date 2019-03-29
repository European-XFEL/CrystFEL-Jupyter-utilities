import unittest
from unittest.mock import patch, Mock
import os
import sys

sys.path.insert(0, os.getcwd())

from widget import Bttn_bins


class Test_bttn_bins(unittest.TestCase):
    @patch('histogram.Histogram')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_plt, Mock_hist):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.ax = Mock_ax()
        self.hist = Mock_hist()
        self.label = "+"
        self.histogram_list = [self.hist, self.hist]
        self.bttn = Bttn_bins(fig=self.fig, histogram_list=self.histogram_list,
                              ax=self.ax, label=self.label)

    @patch('matplotlib.backend_bases.Event')
    def test_change_bins(self, Mock_event):
        Bttn_bins.set_bins(100)
        event = Mock_event
        self.bttn.change_bins(event)
        assert self.fig.canvas.draw.called
        assert self.hist.set_bins.called
        assert self.hist.draw_green_space.called
        assert self.hist.update.called
        self.hist.set_bins.assert_called_with(200)
        self.bttn.label = '-'
        Bttn_bins.set_bins(600)
        self.bttn.change_bins(event)
        self.hist.set_bins.assert_called_with(300)
if __name__ == '__main__':
        unittest.main()
