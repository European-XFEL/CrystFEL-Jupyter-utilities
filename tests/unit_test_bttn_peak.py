import matplotlib
import matplotlib.pyplot as plt
import numpy
import os
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.getcwd())
import bttn_peak


class Test_bttn_peak(unittest.TestCase):
    @patch('stream_read.PeakSearch')
    @patch("stream_read.PeakReflections")
    @patch('peak_h5.Peak')
    @patch('panel.Detector')
    @patch('widget.ContrastSlider')
    @patch('widget.Radio')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.axes.Axes')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_axs, Mock_plt, Mock_radio, Mock_slider,
              Mock_detector, Mock_peak, Mock_peak_reflections,
              Mock_peak_search):

        self.Mock_ax = Mock_ax
        self.Mock_axs = Mock_axs
        self.Mock_plt = Mock_plt
        self.Mock_radio = Mock_radio
        self.Mock_slider = Mock_slider
        self.Mock_detector = Mock_detector
        self.Mock_peak = Mock_peak
        self.Mock_peak_reflections = Mock_peak_reflections
        self.Mock_peak_search = Mock_peak_search

        self.mock_peak_search = self.Mock_peak_search()
        self.mock_peak_reflections = self.Mock_peak_reflections()
        self.mock_plt = self.Mock_plt()
        self.mock_fig = self.mock_plt.figure()
        self.mock_axs = self.Mock_axs()
        self.mock_ax = self.Mock_ax()
        self.mock_radio = self.Mock_radio()
        self.mock_slider = self.Mock_slider()
        self.mock_detector = self.Mock_detector()
        self.mock_peak = self.Mock_peak()
        self.list_active_mock_peak = [True, True, False]
        self.title = "test.title"
        self.label = "test.label"
        self.mock_detectors = {"det1": self.mock_detector, "det2":
                               self.mock_detector}
        self.mock_peaks = [self.mock_peak, self.mock_peak,
                           self.mock_peak]
        self.axis_list = [self.Mock_ax(), self.Mock_ax(), self.Mock_ax()]
        self.matrix = numpy.ones((2, 3))
        self.bttn = bttn_peak.PeakButton(
            fig=self.mock_fig, axs=self.mock_axs, matrix=self.matrix,
            ax=self.mock_ax, label=self.label, axis_list=self.axis_list,
            list_active_peak=self.list_active_mock_peak,
            peaks=self.mock_peaks, detectors=self.mock_detectors,
            title=self.title, radio=self.mock_radio, slider=self.mock_slider)

    def test_init(self):
        assert self.mock_plt.figure.called
        assert self.Mock_plt.called
        assert self.Mock_ax.called
        assert self.Mock_axs.called
        assert self.Mock_radio
        assert self.Mock_slider
        assert self.Mock_detector
        assert self.Mock_peak
        self.assertEqual(self.Mock_ax.call_count, 4)
        self.assertEqual(self.Mock_radio.call_count, 1)
        self.assertEqual(self.Mock_peak.call_count, 1)

    def visual_peaks_reflection(self):
        self.mock_peak_reflections.get_position.return_value = (1, 2)
        self.mock_detector.get_peaks_reflection.return_value = \
            [self.mock_peak_reflections, self.mock_peak_reflections,
             self.mock_peak_reflections]

        self.bttn.visual_peaks_reflection()

        assert self.mock_detector.get_peaks_reflection.called
        assert self.mock_peak_reflections.get_position.called
        assert self.mock_axs.add_artist.called
        self.assertEqual(self.mock_axs.add_artist.call_count, 6)

    def test_visual_peaks_search(self):
        self.mock_peak_search.get_position.return_value = (1, 3)
        self.mock_detector.get_peaks_search.return_value = \
            [self.mock_peak_search, self.mock_peak_search,
             self.mock_peak_search, self.mock_peak_search]

        self.bttn.visual_peaks_search()
        assert self.mock_detector.get_peaks_search.called
        assert self.mock_peak_search.get_position.called
        assert self.mock_axs.add_artist.called
        self.assertEqual(self.mock_axs.add_artist.call_count, 8)

    def test_visual_peaks(self):
        self.mock_peak.get_position.return_value = (1, 2)

        self.bttn.visual_peaks()
        assert self.mock_peak.get_position.called
        assert self.mock_axs.add_artist.called
        self.assertEqual(self.mock_axs.add_artist.call_count, 3)

    @patch('matplotlib.backend_bases.Event')
    def test_peaks_on_of(self, Mock_event):
        event = Mock_event()
        self.mock_radio.get_cmap.return_value = 'inferno'
        self.mock_slider.get_vmax.return_value = 400
        self.mock_slider.get_vmin.return_value = 100
        self.bttn.peaks_on_of(event)

        assert self.mock_axs.cla.called
        assert self.mock_radio.get_cmap.called
        assert self.mock_slider.get_vmax.called
        assert self.mock_slider.get_vmin.called
        assert self.mock_axs.imshow.called
        self.mock_axs.imshow.assert_called_with(self.matrix, animated=True,
                                                cmap='inferno', vmax=400,
                                                vmin=100)
        assert self.mock_fig.canvas.draw.called
        assert self.mock_axs.set_title.called
        self.mock_axs.set_title.assert_called_with(self.title)
        assert self.mock_radio.set_image.called
        assert self.mock_slider.set_image.called

if __name__ == '__main__':
        unittest.main()
