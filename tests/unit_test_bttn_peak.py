import unittest
import numpy
from unittest.mock import patch, Mock
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
sys.path.insert(0, os.getcwd())

import bttn_peak


class Test_bttn_peak(unittest.TestCase):
    @patch('stream_read.Peak_stream')
    @patch("stream_read.Peak_Reflections_measured")
    @patch('peak_h5.Peak')
    @patch('panel.Detector')
    @patch('widget.My_slider')
    @patch('widget.Radio')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.axes.Axes')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_axs, Mock_plt, Mock_radio, Mock_slider,
              Mock_detector, Mock_peak, Mock_peak_reflections_measured,
              Mock_peak_stream):

        self.Mock_ax = Mock_ax
        self.Mock_axs = Mock_axs
        self.Mock_plt = Mock_plt
        self.Mock_radio = Mock_radio
        self.Mock_slider = Mock_slider
        self.Mock_detector = Mock_detector
        self.Mock_peak = Mock_peak
        self.Mock_peak_reflections_measured = Mock_peak_reflections_measured
        self.Mock_peak_stream = Mock_peak_stream

        self.stream_mock = self.Mock_peak_stream()
        self.bragg_mock = self.Mock_peak_reflections_measured()
        self.plt_mock = self.Mock_plt()
        self.fig = self.plt_mock.figure()
        self.axs_mock = self.Mock_axs()
        self.ax_mock = self.Mock_ax()
        self.radio_mock = self.Mock_radio()
        self.slider_mock = self.Mock_slider()
        self.detector_mock = self.Mock_detector()
        self.peak_mock = self.Mock_peak()
        self.list_active_peak_mock = [True, True, False]
        self.title = "test.title"
        self.label = "test.label"
        self.detectors_mock = {"det1": self.detector_mock, "det2":
                               self.detector_mock}
        self.peaks_mock = [self.peak_mock, self.peak_mock,
                           self.peak_mock]
        self.axis_list = [self.Mock_ax(), self.Mock_ax(), self.Mock_ax()]
        self.matrix = numpy.ones((2, 3))
        self.bttn = bttn_peak.Bttn_peak(fig=self.fig, axs=self.axs_mock,
                                        matrix=self.matrix,
                                        ax=self.ax_mock, label=self.label,
                                        axis_list=self.axis_list,
                                        list_active_peak=self.list_active_peak_mock,
                                        peaks=self.peaks_mock,
                                        detectors=self.detectors_mock,
                                        title=self.title,
                                        radio=self.radio_mock,
                                        slider=self.slider_mock)

    def test_init(self):
        assert self.plt_mock.figure.called
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

    def test_visual_peaks_near_bragg_from_stream(self):
        self.bragg_mock.get_position.return_value = (1, 2)
        self.detector_mock.get_peak_near_bragg_list.return_value = [self.bragg_mock, self.bragg_mock, self.bragg_mock]

        self.bttn.visual_peaks_near_bragg_from_stream()

        assert self.detector_mock.get_peak_near_bragg_list.called
        assert self.bragg_mock.get_position.called
        assert self.axs_mock.add_artist.called
        self.assertEqual(self.axs_mock.add_artist.call_count, 6)

    def test_visual_peaks_from_stream(self):
        self.stream_mock.get_position.return_value = (1, 3)
        self.detector_mock.get_peak_list.return_value = [self.stream_mock,
                                                         self.stream_mock,
                                                         self.stream_mock,
                                                         self.stream_mock]

        self.bttn.visual_peaks_from_stream()
        assert self.detector_mock.get_peak_list.called
        assert self.stream_mock.get_position.called
        assert self.axs_mock.add_artist.called
        self.assertEqual(self.axs_mock.add_artist.call_count, 8)

    def test_visual_peaks(self):
        self.peak_mock.get_position.return_value = (1, 2)

        self.bttn.visual_peaks()
        assert self.peak_mock.get_position.called
        assert self.axs_mock.add_artist.called
        self.assertEqual(self.axs_mock.add_artist.call_count, 3)

    @patch('matplotlib.backend_bases.Event')
    def test_peaks_on_of(self, Mock_event):
        event = Mock_event()
        self.radio_mock.get_cmap.return_value = 'inferno'
        self.slider_mock.get_vmax.return_value = 400
        self.slider_mock.get_vmin.return_value = 100
        self.bttn.peaks_on_of(event)

        assert self.axs_mock.cla.called
        assert self.radio_mock.get_cmap.called
        assert self.slider_mock.get_vmax.called
        assert self.slider_mock.get_vmin.called
        assert self.axs_mock.imshow.called
        self.axs_mock.imshow.assert_called_with(self.matrix, animated=True,
                                                cmap='inferno', vmax=400,
                                                vmin=100)
        assert self.fig.canvas.draw.called
        assert self.axs_mock.set_title.called
        self.axs_mock.set_title.assert_called_with(self.title)
        assert self.radio_mock.set_image.called
        assert self.slider_mock.set_image.called

if __name__ == '__main__':
        unittest.main()
