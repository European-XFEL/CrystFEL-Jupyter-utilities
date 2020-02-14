import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import CenteringButton


class TestCenteringButton(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.histogram.Histogram')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, mock_axs, mock_plt, mock_hist):
        self.fig = mock_plt.figure()
        self.mock_axs = mock_axs
        self.mock_hist = mock_hist
        self.label = "test_label"
        self.list_color = ["green", "red", "pink"]
        self.histogram_colors = {"P": "yellow", "A": "yellow"}
        self.histogram_list = [mock_hist, mock_hist, mock_hist]
        self.bttn = CenteringButton(fig=self.fig, axs=self.mock_axs,
                                    label=self.label,
                                    list_color=self.list_color,
                                    histogram_list=self.histogram_list,
                                    histogram_colors=self.histogram_colors)

    @patch('matplotlib.backend_bases.Event')
    def test_on_check(self, mock_event):
        self.bttn.on_check(mock_event)
        self.assertEqual(self.mock_hist.update_colors.call_count, 3)
        assert self.fig.canvas.draw.called
        self.assertEqual("green", self.bttn.color)
        self.bttn.on_check(mock_event)
        self.assertEqual("red", self.bttn.color)

    @patch('CrystFEL_Jupyter_utilities.widget.itertools')
    def test_reset_color(self, mock_itertools):
        self.bttn.reset_color()
        assert mock_itertools.cycle.called
        mock_itertools.cycle.assert_called_once_with(self.list_color)
        self.assertEqual(self.mock_hist.update_colors.call_count, 3)


if __name__ == '__main__':
    unittest.main()
