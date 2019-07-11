import os
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.getcwd())
from widget import CenteringButton


class Test_CenteringButton(unittest.TestCase):
    @patch('histogram.Histogram')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_axs, Mock_plt, Mock_hist):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.axs = Mock_axs()
        self.label = "test_label"
        self.list_color = ["green", "red", "pink"]
        self.histogram_colors = {"P": "yellow", "A": "yellow"}
        self.histogram_list = [Mock_hist(), Mock_hist(), Mock_hist]
        self.bttn = CenteringButton(fig=self.fig, axs=self.axs,
                                    label=self.label,
                                    list_color=self.list_color,
                                    histogram_list=self.histogram_list,
                                    histogram_colors=self.histogram_colors)

    @patch('matplotlib.backend_bases.Event')
    def test_on_check(self, Mock_event):
        event = Mock_event()
        self.bttn.on_check(event)
        for hist in self.histogram_list:
            assert hist.update_color.called
        assert self.fig.canvas.draw.called
        self.assertEqual("green", self.bttn.color)
        self.bttn.on_check(event)
        self.assertEqual("red", self.bttn.color)


if __name__ == '__main__':
        unittest.main()
