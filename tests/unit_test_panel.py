import unittest
import numpy
import os
import sys
from unittest.mock import patch, Mock

sys.path.insert(0,  os.getcwd())

import panel


class TestPanel(unittest.TestCase):
    def setUp(self):
        self.Raw_data = numpy.ones((1480, 1552), dtype='int32')
        self.size_obraz = (1736, 1742)
        self.detector = panel.Detector(self.size_obraz, 'q0a0', 0, 0, 193, 184,
                                       -0.005902, +0.999983, -0.999983,
                                       -0.005902, 450.549, -26.0936,
                                       self.Raw_data)
        self.bad_place = panel.Bad_places(self.size_obraz, name='bad_thing',
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
                                       "min_y": 820, "max_y": 890}}
                     }

    def test_get_array(self):
        numpy.testing.assert_array_equal(self.detector.get_array_rotated(),
                                         numpy.ones((194, 185), dtype='int32'))
        self.assertTupleEqual(self.detector.get_array_rotated().shape,
                              (185, 194))

    def test_rot_x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_x()
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[::-1, :]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y()
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[:, ::-1]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y_x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y_x()
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.rot90(test_array)[:, ::-1]
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_rot_y_2x(self):
        self.detector.array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        self.detector.rot_y_2x()
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.transpose(test_array)
        numpy.testing.assert_array_equal(self.detector.array, test_array)

    def test_bad_places(self):
        max_x = int(numpy.round(-270 + self.size_obraz[1]/2, 0))
        min_x = int(numpy.round(-390 + self.size_obraz[1]/2, 0))
        min_y = int(numpy.round(-820 + self.size_obraz[0]/2, 0))
        max_y = int(numpy.round(-890 + self.size_obraz[0]/2, 0))
        if min_x < 0:
            min_x = 0
        if max_x > self.size_obraz[0] - 1:
            max_x = self.size_obraz[0] - 1
        if min_y > self.size_obraz[1] - 1:
            min_y = self.size_obraz[1] - 1
        if max_y < 0:
            max_y = 0
        self.assertEqual(self.bad_place.max_x, max_x)
        self.assertEqual(self.bad_place.min_x, min_x)
        self.assertEqual(self.bad_place.max_y, max_y)
        self.assertEqual(self.bad_place.min_y, min_y)

    def test_get_diction_bad_places(self):
        bad = panel.get_diction_bad_places(self.size_obraz, self.geom)
        max_x = -270
        max_x = int(numpy.round(max_x + self.size_obraz[1]/2, 0))
        min_y = 820
        min_y = int(numpy.round(-min_y + self.size_obraz[0]/2, 0))

        self.assertEqual(bad['thing'].max_x, max_x)
        self.assertEqual(bad['thing'].min_y, min_y)

    @patch('panel.dict_peak_in_name_h5',
           return_value=({'q0a0': [1, 2, 3], "q1a1": [1, 1, 1]},
                         {'q0a0': [2, 2, 2], "q1a1": [3, 3, 3]}))
    def test_get_diction_detectors(self, Moc_stream):

        panels = panel.get_diction_detectors(self.Raw_data, None, self.geom,
                                             "1", "N2")
        Moc_stream.assert_called_with("1", "N2")
        self.assertListEqual([1, 2, 3], panels['q0a0'].peak_list)
        self.assertListEqual([3, 3, 3], panels['q1a1'].peak_near_bragg_list)
if __name__ == '__main__':
        unittest.main()