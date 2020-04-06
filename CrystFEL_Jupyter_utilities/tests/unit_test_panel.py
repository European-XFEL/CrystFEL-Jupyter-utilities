import numpy
import unittest
from unittest.mock import patch, Mock

import CrystFEL_Jupyter_utilities.panel as panel


class TestPanel(unittest.TestCase):
    def setUp(self):
        self.peaks_search = {'q0a0': {'fs_px': 12, 'ss_px': 13,
                                      'panel_name': 'q0a0',
                                      'position': None},
                             'q1a1': {'fs_px': 12, 'ss_px': 13,
                                      'panel_name': 'q1a1',
                                      'position': None},
                             'q2a3': {'fs_px': 12, 'ss_px': 13,
                                      'panel_name': 'q2a3',
                                      'position': None},
                             'q3a15': {'fs_px': 12, 'ss_px': 13,
                                       'panel_name': 'q3a15',
                                       'position': None}}
        self.peaks_reflections = {'q0a0': {'fs_px': 11, 'ss_px': 22,
                                           'panel_name': 'q0a0',
                                           'position': None},
                                  'q1a1': {'fs_px': 11, 'ss_px': 22,
                                           'panel_name': 'q1a1',
                                           'position': None},
                                  'q2a3': {'fs_px': 11, 'ss_px': 22,
                                           'panel_name': 'q2a3',
                                           'position': None},
                                  'q3a15': {'fs_px': 11, 'ss_px': 22,
                                            'panel_name': 'q3a15',
                                            'position': None}}
        self.geom = {"panels": {'q0a0': {"cnx": 450.549, "cny": -26.0936,
                                         "min_fs": 0, "min_ss": 0,
                                         "max_fs": 193, "max_ss": 184,
                                         "xfs": -0.005902, "xss":  0.999993,
                                         "yfs": -0.999993, "yss": -0.005902},
                                'q1a1': {"cnx": 150.549, "cny": -100.0936,
                                         "min_fs": 194, "min_ss": 185,
                                         "max_fs": 387, "max_ss": 369,
                                         "xfs": -0.005902, "xss": -0.999993,
                                         "yfs": 0.999993, "yss": -0.005902},
                                'q2a3': {"cnx": -226.16, "cny": -166.028,
                                         "min_fs": 970, "min_ss": 185,
                                         "max_fs": 1163, "max_ss": 369,
                                         "xfs": -0.999993, "xss": 0.005902,
                                         "yfs": -0.005902, "yss": -0.999993},
                                'q3a15': {"cnx": 559.766, "cny": -238.613,
                                          "min_fs": 1358, "min_ss": 1295,
                                          "max_fs": 1551, "max_ss": 1479,
                                          "xfs": 0.999993, "xss": -0.005902,
                                          "yfs": -0.005902, "yss": 0.999993}
                                },
                     "bad": {"thing": {"min_x": -390, "max_x": -270,
                                       "min_y": 820, "max_y": 890},
                             "over": {"min_x": -880, "max_x": 910,
                                      "min_y": -910, "max_y": 1024}}}

        self.Raw_data = numpy.ones((1480, 1552), dtype='int32')
        self.image_size = (1736, 1742)
        self.detectors = {}
        for name in self.geom['panels']:
            detector = panel.Detector(
                name=name, image_size=self.image_size,
                corner_x=self.geom["panels"][name]["cnx"],
                corner_y=self.geom["panels"][name]["cny"],
                min_fs=self.geom["panels"][name]["min_fs"],
                min_ss=self.geom["panels"][name]["min_ss"],
                max_fs=self.geom["panels"][name]["max_fs"],
                max_ss=self.geom["panels"][name]["max_ss"],
                xfs=self.geom["panels"][name]["xfs"],
                yfs=self.geom["panels"][name]["yfs"],
                xss=self.geom["panels"][name]["xss"],
                yss=self.geom["panels"][name]["yss"],
                data=self.Raw_data)
            detector.peaks_search = [self.peaks_search[name]]
            detector.peaks_reflection = [self.peaks_reflections[name]]

            self.detectors[name] = detector
        self.bad_place = panel.BadRegion(image_size=self.image_size,
                                         name='bad_thing', min_x=-390,
                                         max_x=-270, min_y=820, max_y=890,
                                         center_x=0, center_y=0)
        self.bad_places = panel.bad_places(self.image_size, self.geom, 0, 0)

    def test_array(self):
        numpy.testing.assert_array_equal(self.detectors['q0a0'].array,
                                         numpy.ones((185, 194), dtype='int32'))
        self.assertTupleEqual(self.detectors['q2a3'].array.shape, (185, 194))

    def test_rot_x(self):
        self.detectors['q3a15'].array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[::-1, :]
        numpy.testing.assert_array_equal(
            self.detectors['q3a15'].get_array_rotated(-3, 2), test_array)
        self.assertEqual(
            self.detectors['q3a15'].peaks_search[0]['position'], (87, 2385))
        self.assertEqual(
            self.detectors['q3a15'].peaks_reflection[0]['position'],
            (86, 2376))

    def test_rot_y(self):
        self.detectors['q2a3'].array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = test_array[:, ::-1]
        numpy.testing.assert_array_equal(
            self.detectors['q2a3'].get_array_rotated(5, 10), test_array)
        self.assertEqual(
            self.detectors['q2a3'].peaks_search[0]['position'], (1612, 867))
        self.assertEqual(
            self.detectors['q2a3'].peaks_reflection[0]['position'],
            (1613, 876))

    def test_rot_y_x(self):
        self.detectors['q0a0'].array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.rot90(test_array)[:, ::-1]
        numpy.testing.assert_array_equal(
            self.detectors['q0a0'].get_array_rotated(11, 21), test_array)
        self.assertEqual(
            self.detectors['q0a0'].peaks_search[0]['position'], (1329, 892))
        self.assertEqual(
            self.detectors['q0a0'].peaks_reflection[0]['position'],
            (1320, 893))

    def test_rot_y_2x(self):
        self.detectors['q1a1'].array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.ones((185, 194), dtype='int32')
        test_array[:5, :5] = numpy.array([2, 3, 4, 5, 6])
        test_array = numpy.transpose(test_array)
        numpy.testing.assert_array_equal(
            self.detectors['q1a1'].get_array_rotated(1, -3), test_array)
        self.assertEqual(
            self.detectors['q1a1'].peaks_search[0]['position'], (847, 787))
        self.assertEqual(
            self.detectors['q1a1'].peaks_reflection[0]['position'],
            (856, 786))

    def test_get_peaks_search(self):
        self.assertListEqual([self.peaks_search['q1a1']],
                             self.detectors['q1a1'].get_peaks_search())

    def test_get_peaks_reflection(self):
        self.assertListEqual([self.peaks_reflections['q1a1']],
                             self.detectors['q1a1'].get_peaks_reflection())

    def test_bad_region(self):
        max_x = int(numpy.round(-270 + self.image_size[1]/2, 0))
        min_x = int(numpy.round(-390 + self.image_size[1]/2, 0))
        min_y = int(numpy.round(-820 + self.image_size[0]/2, 0))
        max_y = int(numpy.round(-890 + self.image_size[0]/2, 0))
        if min_x < 0:
            min_x = 0
        if max_x > self.image_size[0] - 1:
            max_x = self.image_size[0] - 1
        if min_y > self.image_size[1] - 1:
            min_y = self.image_size[1] - 1
        if max_y < 0:
            max_y = 0
        self.assertEqual(self.bad_place.max_x, max_x)
        self.assertEqual(self.bad_place.min_x, min_x)
        self.assertEqual(self.bad_place.max_y, max_y)
        self.assertEqual(self.bad_place.min_y, min_y)

    def test_bad_places(self):
        max_x = -270
        max_x = int(numpy.round(max_x + self.image_size[1]/2, 0))
        min_y = 820
        min_y = int(numpy.round(-min_y + self.image_size[0]/2, 0))
        self.assertEqual(self.bad_places['thing'].max_x, max_x)
        self.assertEqual(self.bad_places['thing'].min_y, min_y)
        max_x = 1735
        min_y = 1741
        self.assertEqual(self.bad_places['over'].max_x, max_x)
        self.assertEqual(self.bad_places['over'].min_y, min_y)

    def test_bad_get_array(self):
        test_array = numpy.zeros((48, 120), dtype='int32')
        numpy.testing.assert_array_equal(
            self.bad_places['thing'].get_array(), test_array)


if __name__ == '__main__':
    unittest.main()
