import matplotlib
import matplotlib.pyplot as plt
import numpy
import unittest
from unittest.mock import patch, Mock

import CrystFEL_Jupyter_utilities.histogram as histogram


class TestHistogram(unittest.TestCase):

    @patch('matplotlib.cbook.silent_list')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.axes.Axes')
    def setUp(self, mock_ax, mock_plt, mock_patch):
        self.fig = mock_plt.figure()
        self.fig.add_subplot(1, 1, 1)
        self.mock_ax = mock_ax()
        self.patch = mock_patch()
        self.mock_ax.get_xlim.return_value = "current_xlim"
        self.mock_ax.hist.return_value = [None, None, self.patch]
        self.data = {'P': [1, 2, 3, 4, 5, 10], 'B': [2, 2, 3, 4, 4, 4],
                     'I': [6, 6, 5, 4, 5, 3], 'A': [1, 1, 1, 1]}
        self.dict_color = {'P': 'gray', 'A': 'cyan', 'B': 'darkblue',
                           'C': 'royalblue', 'I': 'lime',
                           'F': "magenta", 'H': "firebrick", 'R': 'olive'}
        self.title = "test_hist"
        self.xlabel = "test_label"
        self.hist = histogram.Histogram(axs=self.mock_ax, xlabel=self.xlabel,
                                        data_to_histogram=self.data,
                                        colors=self.dict_color,
                                        bins=10, name=self.title)

    def tearDown(self):
        self.fig.reset_mock()
        self.mock_ax.reset_mock()
        self.patch.reset_mock()

    def test_plt(self):
        assert self.fig.add_subplot.called
        self.fig.add_subplot.assert_called_with(1, 1, 1)
        self.fig.reset_mock()

    def test_hist(self):
        assert self.mock_ax.hist.called
        self.mock_ax.hist.assert_called_with(
            alpha=0.9, bins=10, density=1,
            color=['gray', 'cyan', 'darkblue', 'royalblue', 'lime',
                   'magenta', 'firebrick', 'olive', 'lightgray'],
            histtype='stepfilled', range=(1, 10),
            stacked=True, x=[[1, 2, 3, 4, 5, 10], [1, 1, 1, 1],
                             [2, 2, 3, 4, 4, 4], [], [6, 6, 5, 4, 5, 3],
                             [], [], [], []])
        self.assertEqual(self.patch, self.hist.patches)
        assert self.mock_ax.get_xlim.called

    def test_bool_crystal_exluded_green_space(self):
        self.assertEqual(self.hist.bool_crystal_exluded_green_space(1111),
                         False)
        self.hist.range_green_space = [0, 2]
        self.assertEqual(self.hist.bool_crystal_exluded_green_space(3), True)
        self.hist.range_green_space = [None, None]

    def test_set_range_green_space(self):
        self.assertEqual(self.hist.range_green_space, [None, None])
        self.hist.range_green_space = 1, 4
        self.assertEqual(self.hist.range_green_space, (1, 4))

    def test_draw_green_space(self):
        self.hist.range_green_space = 1, 3
        self.hist.draw_green_space()
        assert self.mock_ax.axvspan.called
        self.mock_ax.axvspan.assert_called_with(1, 3, facecolor='#2ca02c',
                                                alpha=0.5)

    def test_set_was_clicked_before(self):
        self.assertEqual(self.hist.was_clicked_before, False)
        self.hist.was_clicked_before = True
        self.assertEqual(self.hist.was_clicked_before, True)

    def test_get_was_clicked_before(self):
        self.hist.was_clicked_before = True
        self.assertEqual(self.hist.was_clicked_before, True)

    def test_set_bins(self):
        self.hist.bins = 15
        self.assertEqual(self.hist.bins, 15)
        self.hist.bins = 22
        self.assertEqual(self.hist.bins, 22)

    def test_set_name(self):
        self.hist.name = "New title"
        self.assertEqual(self.hist.name, "New title")

    def test_update(self):
        self.mock_ax.reset_mock()
        self.data = {'P': [2, 3, 4, 5], 'A': [3, 4, 5, 6, 6]}
        self.data_excluded = [1, 1, 2, 3, 2]
        self.hist.update(self.data, self.data_excluded)
        self.assertListEqual(self.hist.list_data[0], [2, 3, 4, 5])
        self.assertListEqual(self.hist.list_data[1], [3, 4, 5, 6, 6])
        self.assertListEqual(self.hist.list_data[-2], [])
        self.assertListEqual(self.hist.data_excluded, [1, 1, 2, 3, 2])
        assert self.mock_ax.clear.called
        assert self.mock_ax.set_title.called
        self.mock_ax.set_title.assert_called_with("Histogram of " +
                                                  self.hist.name)
        assert self.mock_ax.set_xlabel.called
        self.mock_ax.set_xlabel.assert_called_with(self.xlabel)
        assert self.mock_ax.hist.called

    def test_set_color(self):
        self.dict_color = {'P': 'magenta', 'A': 'magenta', 'B': 'magenta',
                           'C': 'olive', 'I': 'olive', 'F': "olive",
                           'H': "magenta", 'R': 'firebrick'}
        self.hist.list_colors = self.dict_color
        list_test = ['magenta', 'magenta', 'magenta', 'olive', 'olive',
                     'olive', 'magenta', 'firebrick', 'lightgray']
        self.assertListEqual(self.hist.list_colors, list_test)

    def test_current_xlim(self):
        self.assertEqual(self.hist.current_xlim, 'current_xlim')
        self.mock_ax.get_xlim.reset_mock()
        self.hist.update_current_xlim()
        assert self.mock_ax.get_xlim.called


if __name__ == '__main__':
    unittest.main()
