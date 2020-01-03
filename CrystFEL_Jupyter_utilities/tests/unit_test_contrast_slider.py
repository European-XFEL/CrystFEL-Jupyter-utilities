import os
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.getcwd())
from CrystFEL_Jupyter_utilities.widget import ContrastSlider


class Test_ContrastSlider(unittest.TestCase):
    @patch('matplotlib.image')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_plt, Mock_image):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.ax = Mock_ax()
        self.image = Mock_image()
        self.vmax = 100
        self.vmin = 400
        self.label = "test_label"
        self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                     ax=self.ax, label=self.label,
                                     vmin=self.vmin, vmax=self.vmax)

    @patch('matplotlib.backend_bases.Event')
    def test_on_check(self, Mock_event):
        event = Mock_event()
        self.slider.on_check(event)
        assert self.image.set_clim.called
        assert self.fig.canvas.draw.called
        self.image.set_clim.assert_called_once_with(vmax=event)
        self.assertEqual(self.slider.vmax, event)

    @patch('matplotlib.image')
    def test_image(self, Mock_image):
        image = Mock_image
        self.assertEqual(self.image, self.slider.image)
        self.slider.set_image(image)
        self.assertEqual(image, self.slider.image)

    def test_vamx_vmin(self):
        self.assertEqual(self.slider.get_vmax(), self.vmax)
        self.assertEqual(self.slider.get_vmin(), self.vmin)


if __name__ == '__main__':
        unittest.main()
