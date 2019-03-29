import unittest
from unittest.mock import patch, Mock
import os
import sys
import matplotlib.pyplot
sys.path.insert(0, os.getcwd())

from GUI_tools import CellExplorer


class Test_CellExplorer(unittest.TestCase):
    @patch('GUI_tools.stats')
    @patch('GUI_tools.Bttn')
    @patch('GUI_tools.Span')
    @patch('GUI_tools.np')
    @patch('GUI_tools.Histogram')
    @patch('GUI_tools.crystlib')
    @patch('matplotlib.axes.Axes')
    @patch('GUI_tools.plt')
    def setUp(self, mock_plt, mock_ax, mock_crystal, mock_histogram,
              mock_numpy, mock_span, mock_bttn, mock_stats):
        self.mock_plt = mock_plt
        self.mock_crystal = mock_crystal
        self.mock_histogram = mock_histogram
        self.mock_numpy = mock_numpy
        self.mock_span = mock_span
        self.mock_bttn = mock_bttn
        self.mock_stats = mock_stats
        self.figure = mock_plt.figure()
        self.mock_ax = mock_ax()
        self.mock_plt.subplots.return_value = (self.figure, self.mock_ax)
        self.mock_crystal.crystals_list.return_value = [1, 2, 3, 4]
        self.mock_stats.norm.fit.return_value = (1, 2)
        self.mock_numpy.linspace.return_value = [0, 1, 2, 3, 4, 5, 6, 7]
        self.mock_stats.norm.pdf.return_value = [1, 2, 2, 4, 2, 2, 1]
        self.cell = CellExplorer("test_file")
        # mock_plt.subplots.return_value = (self.figure, self.ax)

    def test_init(self):

        assert self.mock_plt.subplots.called
        assert self.mock_ax.ravel.called
        assert self.mock_plt.show.called
        assert self.mock_crystal.crystals_list.called
        self.mock_crystal.crystals_list.assert_called_with("test_file")
        self.assertEqual(self.mock_histogram.call_count, 6)
        self.assertEqual(self.mock_span.call_count, 6)
        self.assertEqual(self.mock_bttn.call_count, 8)
        self.figure.canvas.mpl_connect.called

    def test_gauss_draw(self):
        self.assertEqual(self.mock_stats.norm.fit.call_count, 6)
        self.mock_stats.norm.pdf.assert_called_with([0, 1, 2, 3, 4, 5, 6, 7],
                                                    1, 2)
        self.mock_histogram().axs.plot.assert_called_with([0, 1, 2, 3, 4, 5,
                                                           6, 7],
                                                          [1, 2, 2, 4, 2, 2,
                                                           1])
        assert self.mock_histogram().get_current_ylim.called
        assert self.mock_histogram().axs.text.called

    @patch('matplotlib.backend_bases.MouseEvent')
    def test_rememmber_pos_panel(self, mock_event):
        mock_event.inaxes = self.mock_histogram().axs
        self.cell.rememmber_pos_panel(mock_event)
        assert self.mock_histogram().set_current_xlim.called

    def test_home_reset(self):
        self.cell.home_reset()
        assert self.mock_histogram().reset.called
        self.assertEqual(self.mock_histogram().reset.call_count, 6)
        self.assertEqual(self.mock_bttn().reset_color.call_count, 8)

        assert self.figure.canvas.draw.called

    @patch('matplotlib.backend_bases.MouseEvent')
    def test_save_file(self, mock_event):
        self.cell.save_file(mock_event)
        self.assertEqual(
            self.mock_histogram().get_was_clicked_before.call_count, 6)
        self.assertEqual(self.mock_stats.norm.fit.call_count, 6)

if __name__ == '__main__':
        unittest.main()
