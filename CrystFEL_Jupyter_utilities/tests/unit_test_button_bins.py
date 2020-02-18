import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import ButtonBins


class TestButtonBins(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.histogram.Histogram')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, mock_ax, mock_plt, mock_hist):
        self.fig = mock_plt.figure()
        self.ax = mock_ax
        self.hist = mock_hist
        self.label = "+"
        self.histogram_list = [self.hist, self.hist]
        self.bttn = ButtonBins(fig=self.fig, ax=self.ax,
                               histogram_list=self.histogram_list,
                               label=self.label)

    @patch('matplotlib.backend_bases.Event')
    def test_change_bins(self, mock_event):
        ButtonBins.set_bins(100)
        self.bttn.change_bins(mock_event)
        assert self.fig.canvas.draw.called
        self.assertEqual(self.hist.bins, 200)
        assert self.hist.draw_green_space.called
        assert self.hist.update.called
        self.bttn.label = '-'
        ButtonBins.set_bins(600)
        self.bttn.change_bins(mock_event)
        self.assertEqual(self.hist.bins, 300)


if __name__ == '__main__':
    unittest.main()
