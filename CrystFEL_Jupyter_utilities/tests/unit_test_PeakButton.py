import matplotlib
import matplotlib.pyplot as plt
import numpy
import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import PeakButtons


class TestPeakButtons(unittest.TestCase):
    @patch('CrystFEL_Jupyter_utilities.widget.Button')
    @patch('CrystFEL_Jupyter_utilities.peak_h5.Peak')
    @patch('CrystFEL_Jupyter_utilities.panel.Detector')
    @patch('CrystFEL_Jupyter_utilities.widget.ContrastSlider')
    @patch('CrystFEL_Jupyter_utilities.widget.Radio')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.axes.Axes')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, mock_axes, mock_ax, mock_plt, mock_radio, mock_slider,
              mock_detector, mock_peak, mock_button):
        self.mock_axes = mock_axes
        self.mock_ax = mock_ax
        self.mock_plt = mock_plt
        self.mock_radio = mock_radio
        self.mock_slider = mock_slider
        self.mock_detector = mock_detector
        self.mock_peak = mock_peak
        self.mock_button = mock_button
        self.mock_fig = self.mock_plt.figure
        self.title = "test.title"
        self.mock_detectors = {"det1": self.mock_detector, "det2":
                               self.mock_detector}
        self.mock_peaks = [self.mock_peak, self.mock_peak,
                           self.mock_peak]
        self.matrix = numpy.ones((2, 3))
        self.bttn = PeakButtons(fig=self.mock_fig, ax=self.mock_ax,
                                matrix=self.matrix, peaks=self.mock_peaks,
                                panels=self.mock_detectors,
                                number_peaks_button=3, title=self.title,
                                radio=self.mock_radio, slider=self.mock_slider)

    def test_init(self):
        self.assertEqual(self.mock_axes.call_count, 3)
        self.assertEqual(self.mock_button.call_count, 3)
        self.mock_button.assert_called_with(ax=self.mock_axes(),
                                            label='peaks_reflections on/off')
        self.assertListEqual(self.bttn.buttons, [self.mock_button(),
                                                 self.mock_button(),
                                                 self.mock_button()])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks_reflection(self, mock_circle):
        self.mock_detector.get_peaks_reflection.return_value = \
            [{'position': (1, 2)}, {'position': (3, 1)}, {'position': (2, 2)}]
        self.bttn.visual_peaks_reflection()
        self.assertEqual(self.mock_detector.get_peaks_reflection.call_count, 2)
        mock_circle.assert_called_with((2, 2), color='r', fill=False, radius=5)
        self.mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.mock_ax.add_artist.call_count, 6)
        self.assertEqual(self.bttn.list_active_peak, [False, False, True])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks_search(self, mock_circle):
        self.mock_detector.get_peaks_search.return_value = [{'position': (3, 1)},
                                                            {'position': (8, 9)}]
        self.bttn.visual_peaks_search()
        self.assertEqual(self.mock_detector.get_peaks_search.call_count, 2)
        mock_circle.assert_called_with((8, 9), color='g', fill=False, radius=5)
        self.mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.mock_ax.add_artist.call_count, 4)
        self.assertEqual(self.bttn.list_active_peak, [False, True, False])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks(self, mock_circle):
        self.mock_peak.get_position.return_value = (1, 2)
        self.bttn.visual_peaks()
        self.assertEqual(self.mock_peak.get_position.call_count, 3)
        self.assertEqual(self.mock_ax.add_artist.call_count, 3)
        mock_circle.assert_called_with((1, 2), color='y', fill=False, radius=5)
        self.mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.mock_ax.add_artist.call_count, 3)
        self.assertEqual(self.bttn.list_active_peak, [False, False, False])

    @patch('matplotlib.backend_bases.Event')
    def test_peaks_on_of(self, mock_event):
        self.mock_radio.get_cmap.return_value = 'inferno'
        self.mock_slider.get_vmax.return_value = 400
        self.mock_slider.get_vmin.return_value = 100
        self.bttn.peaks_on_of(mock_event)
        assert self.mock_ax.cla.called
        assert self.mock_radio.get_cmap.called
        assert self.mock_slider.get_vmax.called
        assert self.mock_slider.get_vmin.called
        assert self.mock_ax.imshow.called
        self.mock_ax.imshow.assert_called_with(self.matrix, animated=True,
                                               cmap='inferno', vmax=400,
                                               vmin=100)
        assert self.mock_fig.canvas.draw.called
        assert self.mock_ax.set_title.called
        self.mock_ax.set_title.assert_called_with(self.title)
        assert self.mock_radio.set_image.called
        assert self.mock_slider.set_image.called


if __name__ == '__main__':
    unittest.main()
