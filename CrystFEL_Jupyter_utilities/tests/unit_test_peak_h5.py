import unittest
import numpy

import CrystFEL_Jupyter_utilities.peak_h5 as peak_h5


class TestPeak(unittest.TestCase):
    def setUp(self):

        self.size_image = (1736, 1742)
        self.array = numpy.array([[368.7373352050781, 148.3291778564453,
                                   431.1397399902344, 3.0],
                                  [-361.62225341796875, 18.792268753051758,
                                   991.7413330078125, 4.0],
                                  [63.85224914550781, -403.03155517578125,
                                   659.25634765625, 3.0]])

    def test_list_peaks(self):
        test_list = peak_h5.get_list_peaks(self.array, self.size_image)
        self.assertEqual(test_list[0].posx,
                         368.7373352050781+self.size_image[1]/2.0)
        self.assertEqual(test_list[1].posy,
                         -18.792268753051758+self.size_image[0]/2.0)
        self.assertEqual(test_list[2].intensive, 659.25634765625)


if __name__ == '__main__':
    unittest.main()
