import unittest
from unittest.mock import patch, Mock

from CrystFEL_Jupyter_utilities.widget import Radio


class Test_Radio(unittest.TestCase):
    @patch('matplotlib.image')
    @patch('matplotlib.pyplot')
    @patch('matplotlib.pyplot.axes')
    def setUp(self, Mock_ax, Mock_plt, Mock_image):
        self.plt_mock = Mock_plt()
        self.fig = self.plt_mock.figure()
        self.ax = Mock_ax()
        self.image = Mock_image()
        self.labels = ("plasma", "yellow", "orange")
        self.cmap = "plasma"
        self.ax.get_facecolor.return_value = [0.5, 0.5, 0.5]
        self.radio = Radio(fig=self.fig, ax=self.ax, labels=self.labels,
                           cmap=self.cmap, image=self.image)

    def test_colorfunc(self):
        self.radio.colorfunc("green")
        self.assertEqual(self.radio.get_cmap(), "green")

    @patch('matplotlib.image')
    def test_image(self, Mock_image):
        image = Mock_image
        self.assertEqual(self.image, self.radio.image)
        self.radio.set_image(image)
        self.assertEqual(image, self.radio.image)


if __name__ == '__main__':
    unittest.main()
