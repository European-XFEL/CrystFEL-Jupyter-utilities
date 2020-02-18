import numpy
import unittest
from unittest.mock import patch, Mock

import CrystFEL_Jupyter_utilities.panel as panel


class TestPanel(unittest.TestCase):
    def setUp(self):
        self.peaks_search = {'q0a0': [1, 2, 3], "q1a1": [1, 1, 1]}
        self.peaks_reflections = {'q0a0': [2, 2, 2], "q1a1": [3, 3, 3]}
        self.Raw_data = numpy.ones((1480, 1552), dtype='int32')
        self.size_image = (1736, 1742)
        self.detector = panel.Detector(self.size_image, 'q0a0', 0, 0, 193, 184,
                                       -0.005902, +0.999983, -0.999983,
                                       -0.005902, 450.549, -26.0936,
                                       self.Raw_data)
        self.bad_place = panel.BadRegion(self.size_image, name='bad_thing',
                                         min_x=-390, max_x=-270, min_y=820,
                                         max_y=890)
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

    def test_get_array(self):
        numpy.testing.assert_array_equal(self.detector.get_array_rotated(0, 0),
                                         numpy.ones((194, 185), dtype='int32'))
        self.assertTupleEqual(self.detector.get_array_rotated(0, 0).shape,
                              (185, 194))

    def test_rot_x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_x(0, 0)
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[::-1, :]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y(0, 0)
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[:, ::-1]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y_x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y_x(0, 0)
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.rot90(test_array)[:, ::-1]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y_2x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y_2x(0, 0)
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.transpose(test_array)
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_bad_region(self):
        max_x = int(numpy.round(-270 + self.size_image[1]/2, 0))
        min_x = int(numpy.round(-390 + self.size_image[1]/2, 0))
        min_y = int(numpy.round(-820 + self.size_image[0]/2, 0))
        max_y = int(numpy.round(-890 + self.size_image[0]/2, 0))
        if min_x < 0:
            min_x = 0
        if max_x > self.size_image[0] - 1:
            max_x = self.size_image[0] - 1
        if min_y > self.size_image[1] - 1:
            min_y = self.size_image[1] - 1
        if max_y < 0:
            max_y = 0
        self.assertEqual(self.bad_place.max_x, max_x)
        self.assertEqual(self.bad_place.min_x, min_x)
        self.assertEqual(self.bad_place.max_y, max_y)
        self.assertEqual(self.bad_place.min_y, min_y)

    def test_bad_places(self):
        bad = panel.bad_places(self.size_image, self.geom)
        max_x = -270
        max_x = int(numpy.round(max_x + self.size_image[1]/2, 0))
        min_y = 820
        min_y = int(numpy.round(-min_y + self.size_image[0]/2, 0))
        self.assertEqual(bad['thing'].max_x, max_x)
        self.assertEqual(bad['thing'].min_y, min_y)

    def test_get_detectors(self):
        panels = panel.get_detectors(self.Raw_data, self.size_image, self.geom,
                                     self.peaks_search, self.peaks_reflections)
        self.assertListEqual([1, 2, 3], panels['q0a0'].peaks_search)
        self.assertListEqual([3, 3, 3], panels['q1a1'].peaks_reflection)


if __name__ == '__main__':
    unittest.main()
