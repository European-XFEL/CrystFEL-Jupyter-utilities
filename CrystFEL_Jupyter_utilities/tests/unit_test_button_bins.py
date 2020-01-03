import os
import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import ButtonBins


class Test_button_bins(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.histogram.Histogram')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_plt, Mock_hist):

        self.fig = Mock_plt.figure()
        self.ax = Mock_ax
        self.hist = Mock_hist
        self.label = "+"
        self.histogram_list = [self.hist, self.hist]
        self.bttn = ButtonBins(
            fig=self.fig, histogram_list=self.histogram_list,
            ax=self.ax, label=self.label)

    @patch('matplotlib.backend_bases.Event')
    def test_change_bins(self, Mock_event):
        ButtonBins.set_bins(100)
        self.bttn.change_bins(Mock_event)
        assert self.fig.canvas.draw.called
        self.assertEqual(self.hist.bins, 200)
        assert self.hist.draw_green_space.called
        assert self.hist.update.called
        self.bttn.label = '-'
        ButtonBins.set_bins(600)
        self.bttn.change_bins(Mock_event)
        self.assertEqual(self.hist.bins, 300)

if __name__ == '__main__':
        unittest.main()
