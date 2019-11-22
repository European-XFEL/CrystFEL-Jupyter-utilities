import matplotlib.pyplot
import os
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.getcwd())
from GUI_tools import CellExplorer


class Test_CellExplorer(unittest.TestCase):
    @patch('GUI_tools.stream_read')
    @patch('GUI_tools.stats')
    @patch('GUI_tools.CenteringButton')
    @patch('GUI_tools.ButtonBins')
    @patch('GUI_tools.Button')
    @patch('GUI_tools.Span')
    @patch('GUI_tools.np')
    @patch('GUI_tools.Histogram')
    @patch('GUI_tools.crystlib')
    @patch('matplotlib.axes.Axes')
    @patch('GUI_tools.plt')
    def setUp(self, mock_plt, mock_ax, mock_crystlib, mock_histogram,
              mock_numpy, mock_span, mock_button_bins, mock_buton,
              mock_centering_button, mock_stats, mock_stream_read):
        self.mock_plt = mock_plt
        self.mock_crystlib = mock_crystlib
        self.mock_histogram = mock_histogram
        self.mock_numpy = mock_numpy
        self.mock_span = mock_span
        self.mock_button_bins = mock_button_bins
        self.mock_buton = mock_buton
        self.mock_centering_button = mock_centering_button
        self.mock_stats = mock_stats
        self.mock_stream_read = mock_stream_read
        self.figure = mock_plt.figure
        self.mock_ax = mock_ax
        self.mock_plt.subplots.return_value = (self.figure, self.mock_ax)
        self.mock_crystlib.crystals_list.return_value = [1, 2, 3, 4]
        self.mock_stats.norm.fit.return_value = (1, 2)
        self.mock_numpy.linspace.return_value = [0, 1, 2, 3, 4, 5, 6, 7]
        self.mock_stats.norm.pdf.return_value = [1, 2, 2, 4, 2, 2, 1]
        self.cell = CellExplorer("test_file")

    def test_init(self):

        assert self.mock_plt.subplots.called
        assert self.mock_ax.ravel.called
        assert self.mock_plt.show.called
        assert self.mock_crystlib.histograms_data.called
        assert self.mock_stream_read.search_crystals_parameters.called
        self.mock_stream_read.search_crystals_parameters.called_with(
            "test_file")
        self.assertEqual(self.mock_histogram.call_count, 6)
        self.assertEqual(self.mock_span.call_count, 6)
        self.assertEqual(self.mock_centering_button.call_count, 8)
        self.figure.canvas.mpl_connect.called

    def test_gauss_draw(self):

        self.assertEqual(self.mock_histogram().update.call_count, 6)
        self.assertEqual(self.mock_stats.norm.fit.call_count, 6)
        self.mock_stats.norm.pdf.assert_called_with([0, 1, 2, 3, 4, 5, 6, 7],
                                                    1, 2)
        self.mock_histogram().axs.plot.assert_called_with([0, 1, 2, 3, 4, 5,
                                                           6, 7],
                                                          [1, 2, 2, 4, 2, 2,
                                                           1])
        assert self.mock_histogram().axs.get_ylim.called
        assert self.mock_histogram().axs.text.called
        self.mock_numpy.round.assert_called_with(2, 2)

    @patch('matplotlib.backend_bases.MouseEvent')
    def test_rememmber_pos_panel(self, mock_event):
        mock_event.inaxes = self.mock_histogram().axs
        self.cell.rememmber_pos_panel(mock_event)
        assert self.mock_histogram().update_current_xlim.called
        self.assertEqual(
            self.mock_histogram().update_current_xlim.call_count, 6)

    @patch('GUI_tools.ButtonBins')
    def test_home_reset(self, mock_ButtonBins):
        self.mock_histogram.reset_mock()
        self.cell.home_reset()
        assert self.mock_histogram().reset.called
        self.assertEqual(self.mock_histogram().reset.call_count, 6)
        self.assertEqual(mock_ButtonBins.set_bins.call_count, 6)
        mock_ButtonBins.set_bins.assert_called_with(16)
        self.assertEqual(
            self.mock_centering_button().reset_color.call_count, 8)
        self.assertEqual(self.mock_histogram().update.call_count, 6)
        assert self.figure.canvas.draw.called

    def test_was_all_hist_selected(self):
        self.mock_histogram.reset_mock()
        self.mock_histogram().was_clicked_before = False
        self.assertEqual(self.cell.was_all_hist_selected(), False)
        self.mock_histogram().was_clicked_before = True
        self.assertEqual(self.cell.was_all_hist_selected(), True)

    @patch('matplotlib.backend_bases.MouseEvent')
    def test_save_file(self, mock_event):
        self.mock_histogram.reset_mock()
        self.mock_histogram().was_clicked_before = True
        self.cell.save_file(mock_event)
        self.assertEqual(
            self.cell.was_all_hist_selected(), True)
        self.assertEqual(self.mock_stats.norm.fit.call_count, 6)

if __name__ == '__main__':
        unittest.main()
