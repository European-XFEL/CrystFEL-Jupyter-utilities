import matplotlib.pyplot
import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import Span


class TestSpan(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.histogram.Histogram')
    @patch('matplotlib.pyplot')
    def setUp(self, mock_plt, mock_hist):
        self.fig = mock_plt.figure()
        self.all_crystals_list = [{'name': 'Image filename: db.h5',
                                   'a': 1, 'b': 1,
                                   'c': 1, 'alfa': 90,
                                   'beta': 90, 'gamma': 90,
                                   'lattice_type': "monoclinic",
                                   'centering': "C", "unique_axis": "b"},
                                  {'name': 'Image filename: db2.cxi',
                                   'a': 40, 'b': 40,
                                   'c': 40, 'alfa': 120,
                                   'beta': 120, 'gamma': 120,
                                   'lattice_type': "triclinic",
                                   'centering': "P", "unique_axis": "b"}]
        self.crystals_excluded = []
        self.index = 1
        self.name = "test_name"
        self.mock_hist = mock_hist
        self.mock_hist.name = 'a'
        self.histogram_list = [self.mock_hist, self.mock_hist, self.mock_hist,
                               self.mock_hist, self.mock_hist, self.mock_hist]
        self.span = Span(fig=self.fig, histogram_list=self.histogram_list,
                         index=self.index, name=self.name,
                         all_crystals_list=self.all_crystals_list,
                         crystals_excluded=self.crystals_excluded)

    def test_onselect(self):
        self.span.onselect(20, 100)
        self.assertEqual(
            self.mock_hist.was_clicked_before, True)
        self.assertEqual(self.mock_hist.range_green_space, (20, 100))
        self.assertEqual(len(self.crystals_excluded), 2)
        self.span.onselect(20, 20)
        self.assertEqual(self.mock_hist.was_clicked_before, False)
        self.assertEqual(self.mock_hist.range_green_space, (None, None))

    @patch('CrystFEL_Jupyter_utilities.widget.histograms_data')
    def test_data_update(self, mock_histograms_data):
        self.mock_hist.reset_mock()
        self.span.data_update()
        assert mock_histograms_data.called
        mock_histograms_data.assert_called_once_with(
            Span.get_crystals_included_list())
        self.assertEqual(self.mock_hist.update.call_count, 6)

    def test_is_exluded(self):
        crystal = {'name': 'Image filename: db2.cxi',
                   'a': 40, 'b': 40,
                   'c': 40, 'alfa': 120,
                   'beta': 120, 'gamma': 120,
                   'lattice_type': "triclinic",
                   'centering': "P", "unique_axis": "b"}
        self.mock_hist.reset_mock()
        self.mock_hist.bool_crystal_exluded_green_space.return_value = False
        self.span.is_exluded(crystal)
        self.assertEqual(
            self.mock_hist.bool_crystal_exluded_green_space.call_count, 6)
        self.mock_hist.bool_crystal_exluded_green_space.return_value = True
        self.assertEqual(self.span.is_exluded(crystal), True)


if __name__ == '__main__':
    unittest.main()
