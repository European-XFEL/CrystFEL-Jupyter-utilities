import matplotlib.pyplot
import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.GUI_tools import CellExplorer


class TestCellExplorer(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.search_crystals_parameters')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.stats')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.CenteringButton')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.ButtonBins')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.Button')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.Span')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.np')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.Histogram')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.histograms_data')
    @patch('matplotlib.axes.Axes')
    @patch('CrystFEL_Jupyter_utilities.GUI_tools.plt')
    def setUp(self, mock_plt, mock_ax, mock_histograms_data, mock_histogram,
              mock_numpy, mock_span, mock_button_bins, mock_button,
              mock_centering_button, mock_stats,
              mock_search_crystals_parameters):
        self.mock_plt = mock_plt
        self.mock_histograms_data = mock_histograms_data
        self.mock_histogram = mock_histogram
        self.mock_numpy = mock_numpy
        self.mock_span = mock_span
        self.mock_button_bins = mock_button_bins
        self.mock_button = mock_button
        self.mock_centering_button = mock_centering_button
        self.mock_stats = mock_stats
        self.mock_search_crystals_parameters = mock_search_crystals_parameters
        self.figure = mock_plt.figure
        self.mock_ax = mock_ax
        self.mock_plt.subplots.return_value = (self.figure, self.mock_ax)
        self.mock_histograms_data.crystals_list.return_value = [1, 2, 3, 4]
        self.mock_stats.norm.fit.return_value = (1, 2)
        self.mock_numpy.linspace.return_value = [0, 1, 2, 3, 4, 5, 6, 7]
        self.mock_stats.norm.pdf.return_value = [1, 2, 2, 4, 2, 2, 1]
        self.cell = CellExplorer("test_file")

    def test_init(self):
        assert self.mock_plt.subplots.called
        assert self.mock_ax.ravel.called
        assert self.mock_plt.show.called
        assert self.mock_histograms_data.called
        assert self.mock_search_crystals_parameters.called
        self.mock_search_crystals_parameters.called_with("test_file")
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
    def test_remember_pos_panel(self, mock_event):
        mock_event.inaxes = self.mock_histogram().axs
        self.cell.remember_pos_panel(mock_event)
        assert self.mock_histogram().update_current_xlim.called
        self.assertEqual(self.mock_histogram().update_current_xlim.call_count,
                         6)

    @patch('CrystFEL_Jupyter_utilities.GUI_tools.ButtonBins')
    def test_home_reset(self, mock_button_bins):
        self.mock_histogram.reset_mock()
        self.cell.home_reset()
        assert self.mock_histogram().reset.called
        self.assertEqual(self.mock_histogram().reset.call_count, 6)
        self.assertEqual(mock_button_bins.set_bins.call_count, 6)
        mock_button_bins.set_bins.assert_called_with(16)
        self.assertEqual(self.mock_centering_button().reset_color.call_count,
                         8)
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
        self.assertEqual(self.cell.was_all_hist_selected(), True)
        self.assertEqual(self.mock_stats.norm.fit.call_count, 6)


if __name__ == '__main__':
    unittest.main()
