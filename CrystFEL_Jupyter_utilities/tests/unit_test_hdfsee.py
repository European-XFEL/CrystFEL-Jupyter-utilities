import h5py
import numpy
import unittest
import tempfile
from unittest.mock import patch

import CrystFEL_Jupyter_utilities.hdfsee as hdfsee


class TestHdfsee(unittest.TestCase):
    def setUp(self):
        self.image = None
        self.path = "/home/file.h5"
        self.geomfile = "/home/geomfile.geom"
        self.streamfile = "/home/streamfile.stream"
        self.range = (300, 900)
        self.event = 333
        self.geom = {"panels": {'q0a0': {"cnx": 450.549, "cny": -26.0936,
                                         "min_fs": 0, "min_ss": 0,
                                         "max_fs": 193, "max_ss": 184,
                                         "xfs": -0.005902, "xss":  0.999993,
                                         "yfs": -0.999993, "yss": -0.005902},
                                'q1a1': {"cnx": 150.549, "cny": -100.0936,
                                         "min_fs": 194, "min_ss": 185,
                                         "max_fs": 387, "max_ss": 369,
                                         "xfs": -0.005902, "xss":  0.999993,
                                         "yfs": -0.999993, "yss": -0.005902}
                                },
                     "bad": {"thing": {"min_x": -390, "max_x": -270,
                                       "min_y": 820, "max_y": 890}}}
        self.peak_search = {
            'q0a0': [{'fs_px': 58.74, 'ss_px': 11.17, 'recip': 2.35,
                      'intensity': 3388.67, 'panel_name': 'q0a0',
                      'position': None},
                     {'fs_px': 138.85, 'ss_px': 33.64, 'recip': 2.3,
                      'intensity': 2672.5, 'panel_name': 'q0a0',
                      'position': None}],
            'q0a1': {'fs_px': 107.94, 'ss_px': 38.73, 'recip': 2.24,
                     'intensity': 4392.78, 'panel_name': 'q0a1',
                     'position': None}}
        self.peaks_reflection = {
            'q0a1': [{'h': -24, 'k': 6, 'l': 20, 'I': -7.53, 'sigmaI': 35.36,
                      'peak': 44.0, 'background': 19.64, 'fs_px': 30.7,
                      'ss_px': 659.4, 'panel_name': 'q0a1', 'position': None},
                     {'h': -24, 'k': 8, 'l': 21, 'I': -70.89, 'sigmaI': 43.05,
                      'peak': 36.0, 'background': 20.44, 'fs_px': 22.8,
                      'ss_px': 623.0, 'panel_name': 'q0a1', 'position': None},
                     {'h': -24, 'k': 10, 'l': 22, 'I': 109.0, 'sigmaI': 43.67,
                      'peak': 52.0, 'background': 19.0, 'fs_px': 14.8,
                      'ss_px': 586.2, 'panel_name': 'q0a1', 'position': None}],
            'q0a0': [{'h': -23, 'k': 5, 'l': 18, 'I': -44.81, 'sigmaI': 42.85,
                      'peak': 39.0, 'background': 22.03, 'fs_px': 79.9,
                      'ss_px': 677.2, 'panel_name': 'q0a0', 'position': None}]}
        self.peaks = [{'position': (1, 2)}, {'position': (3, 1)},
                      {'position': (2, 2)}]

    @patch('CrystFEL_Jupyter_utilities.hdfsee.load_crystfel_geometry')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.search_peaks')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.ContrastSlider')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.PeakButtons')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.Radio')
    @patch('matplotlib.axes.Axes')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.plt')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.get_file_data')
    def test_init(self, mock_get_file_data, mock_plt, mock_ax,
                  mock_radio, mock_peak_buttons, mock_slider,
                  mock_search_peaks, mock_load_geometry):
        mock_plt.subplots.return_value = (mock_plt.figure, mock_ax)
        mock_get_file_data.return_value = [[1, 4], [2, 3]]
        self.image = hdfsee.Image(self.path, event=self.event,
                                  range=self.range)
        assert mock_plt.subplots.called
        assert mock_ax.set_title.called
        self.assertEqual(self.image.fig, mock_plt.figure)
        self.assertEqual(self.image.ax, mock_ax)
        mock_ax.set_title.assert_called_with('/home/file.h5 Event 333')
        self.assertEqual(self.image.range, self.range)
        self.assertEqual(mock_plt.axes.call_count, 2)
        mock_get_file_data.assert_called_with(self.path)
        self.assertTrue((self.image.matrix == [[2, 3], [1, 4]]).all())
        mock_slider.assert_called_with(ax=mock_plt.axes(), vmin=300, vmax=900,
                                       fig=mock_plt.figure, label='Contrast',
                                       image=mock_ax.imshow())
        mock_radio.assert_called_with(ax=mock_plt.axes(), cmap='inferno',
                                      fig=mock_plt.figure,
                                      image=mock_ax.imshow(),
                                      labels=('inferno', 'plasma', 'Greys'))

    @patch('CrystFEL_Jupyter_utilities.hdfsee.load_crystfel_geometry')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.bad_places')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.search_peaks')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.ContrastSlider')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.PeakButtons')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.Radio')
    @patch('matplotlib.axes.Axes')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.plt')
    @patch('CrystFEL_Jupyter_utilities.panel.Detector')
    @patch('CrystFEL_Jupyter_utilities.hdfsee.get_file_data')
    def test_init_geom(self, mock_get_file_data, mock_dectector, mock_plt,
                       mock_ax, mock_radio, mock_peak_buttons, mock_slider,
                       mock_search_peaks, mock_bad_places, mock_load_geometry):
        mock_plt.subplots.return_value = (mock_plt.figure, mock_ax)
        mock_load_geometry.return_value = self.geom
        mock_search_peaks.return_value = (self.peak_search,
                                          self.peaks_reflection)
        mock_get_file_data.return_value = ([mock_dectector, mock_dectector],
                                           self.peaks)

        self.image = hdfsee.Image(self.path, event=self.event,
                                  range=self.range,
                                  streamfile=self.streamfile,
                                  geomfile=self.geomfile)

        assert mock_plt.subplots.called
        assert mock_ax.set_title.called
        self.assertEqual(self.image.fig, mock_plt.figure)
        self.assertEqual(self.image.ax, mock_ax)
        mock_ax.set_title.assert_called_with('/home/file.h5 Event 333')
        self.assertEqual(self.image.range, self.range)
        self.assertEqual(mock_plt.axes.call_count, 2)
        mock_get_file_data.assert_called_with(geom=self.geom, event=self.event,
                                              file=self.path,
                                              image_size=(268, 485))
        self.assertTrue(
            (self.image.matrix == hdfsee.np.ones(((268, 485)))).all())
        mock_slider.assert_called_with(ax=mock_plt.axes(), vmin=300, vmax=900,
                                       fig=mock_plt.figure, label='Contrast',
                                       image=mock_ax.imshow())
        mock_radio.assert_called_with(ax=mock_plt.axes(), cmap='inferno',
                                      fig=mock_plt.figure,
                                      image=mock_ax.imshow(),
                                      labels=('inferno', 'plasma', 'Greys'))
        mock_search_peaks.assert_called_with(self.streamfile, str(self.event),
                                             'Event')
        self.image.event = 100
        mock_search_peaks.return_value = (self.peak_search,
                                          self.peaks_reflection)
        self.image.add_stream_peaks(self.image.detectors,
                                    self.image.streamfile,
                                    self.image.event)
        mock_search_peaks.assert_called_with(self.streamfile,
                                             str(100),
                                             'Event')
        self.image.event = None
        self.image.add_stream_peaks(self.image.detectors,
                                    self.image.streamfile)
        mock_search_peaks.assert_called_with(self.streamfile, 'file.h5',
                                             'Image filename:')
        self.image.display_arrangement_view()
        assert mock_bad_places.called
        mock_bad_places.assert_called_with((268, 485), self.geom, 33, -208)


if __name__ == '__main__':
    unittest.main()
