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
    def setUp(self, Mock_axes, Mock_ax, Mock_plt, Mock_radio, Mock_slider,
              Mock_detector, Mock_peak, Mock_button):
        self.Mock_axes = Mock_axes
        self.Mock_ax = Mock_ax
        self.Mock_plt = Mock_plt
        self.Mock_radio = Mock_radio
        self.Mock_slider = Mock_slider
        self.Mock_detector = Mock_detector
        self.Mock_peak = Mock_peak
        self.Mock_button = Mock_button

        self.mock_fig = self.Mock_plt.figure
        self.title = "test.title"
        self.mock_detectors = {"det1": self.Mock_detector, "det2":
                               self.Mock_detector}
        self.mock_peaks = [self.Mock_peak, self.Mock_peak,
                           self.Mock_peak]
        self.matrix = numpy.ones((2, 3))
        self.bttn = PeakButtons(fig=self.mock_fig, ax=self.Mock_ax,
                                matrix=self.matrix, peaks=self.mock_peaks,
                                panels=self.mock_detectors,
                                number_peaks_button=3, title=self.title,
                                radio=self.Mock_radio, slider=self.Mock_slider)

    def test_init(self):
        self.assertEqual(self.Mock_axes.call_count, 3)
        self.assertEqual(self.Mock_button.call_count, 3)
        self.Mock_button.assert_called_with(ax=self.Mock_axes(),
                                            label='peaks_reflections on/off')
        self.assertListEqual(self.bttn.buttons, [self.Mock_button(),
                                                 self.Mock_button(),
                                                 self.Mock_button()])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks_reflection(self, mock_circle):
        self.Mock_detector.get_peaks_reflection.return_value = \
            [{'position': (1, 2)}, {'position': (3, 1)}, {'position': (2, 2)}]

        self.bttn.visual_peaks_reflection()

        self.assertEqual(self.Mock_detector.get_peaks_reflection.call_count, 2)
        mock_circle.assert_called_with((2, 2), color='r', fill=False, radius=5)
        self.Mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.Mock_ax.add_artist.call_count, 6)
        self.assertEqual(self.bttn.list_active_peak, [False, False, True])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks_search(self, mock_circle):
        self.Mock_detector.get_peaks_search.return_value = [{'position': (3, 1)},
                                                            {'position': (8, 9)}]

        self.bttn.visual_peaks_search()
        self.assertEqual(self.Mock_detector.get_peaks_search.call_count, 2)
        mock_circle.assert_called_with((8, 9), color='g', fill=False, radius=5)
        self.Mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.Mock_ax.add_artist.call_count, 4)
        self.assertEqual(self.bttn.list_active_peak, [False, True, False])

    @patch('CrystFEL_Jupyter_utilities.widget.plt.Circle')
    def test_visual_peaks(self, mock_circle):
        self.Mock_peak.get_position.return_value = (1, 2)

        self.bttn.visual_peaks()

        self.assertEqual(self.Mock_peak.get_position.call_count, 3)
        self.assertEqual(self.Mock_ax.add_artist.call_count, 3)
        mock_circle.assert_called_with((1, 2), color='y', fill=False, radius=5)
        self.Mock_ax.add_artist.assert_called_with(mock_circle())
        self.assertEqual(self.Mock_ax.add_artist.call_count, 3)
        self.assertEqual(self.bttn.list_active_peak, [False, False, False])

    @patch('matplotlib.backend_bases.Event')
    def test_peaks_on_of(self, Mock_event):
        self.Mock_radio.get_cmap.return_value = 'inferno'
        self.Mock_slider.get_vmax.return_value = 400
        self.Mock_slider.get_vmin.return_value = 100
        self.bttn.peaks_on_of(Mock_event)

        assert self.Mock_ax.cla.called
        assert self.Mock_radio.get_cmap.called
        assert self.Mock_slider.get_vmax.called
        assert self.Mock_slider.get_vmin.called
        assert self.Mock_ax.imshow.called
        self.Mock_ax.imshow.assert_called_with(self.matrix, animated=True,
                                               cmap='inferno', vmax=400,
                                               vmin=100)
        assert self.mock_fig.canvas.draw.called
        assert self.Mock_ax.set_title.called
        self.Mock_ax.set_title.assert_called_with(self.title)
        assert self.Mock_radio.set_image.called
        assert self.Mock_slider.set_image.called


if __name__ == '__main__':
    unittest.main()
