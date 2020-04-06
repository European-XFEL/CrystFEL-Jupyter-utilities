import numpy as np
import unittest
from unittest.mock import mock_open, patch

import CrystFEL_Jupyter_utilities.stream_read as stream_read


class TestStreamRead(unittest.TestCase):
    def setUp(self):
        self.astar = [+0.1628118, -0.0234613, +0.0047666]
        self.bstar = [+0.0115679, +0.0777724, -0.0235210]
        self.cstar = [+0.0019407, +0.0171354, +0.0576783]
        array = np.transpose(np.array([[+0.1628118, -0.0234613, +0.0047666],
                                       [+0.0115679, +0.0777724, -0.0235210],
                                       [+0.0019407, +0.0171354, +0.0576783]]))
        array = np.linalg.inv(array)
        self.a = np.linalg.norm(array[0, :])*10
        self.b = np.linalg.norm(array[1, :])*10
        self.c = np.linalg.norm(array[2, :])*10
        mod1 = np.linalg.norm(array[0, :])
        mod2 = np.linalg.norm(array[1, :])
        mod3 = np.linalg.norm(array[2, :])
        cosine1 = (np.sum(array[1, :]*array[2, :])) / (mod2*mod3)
        cosine2 = (np.sum(array[0, :]*array[2, :])) / (mod1*mod3)
        cosine3 = (np.sum(array[0, :]*array[1, :])) / (mod1*mod2)
        self.alfa = np.rad2deg(np.arccos(cosine1))
        self.beta = np.rad2deg(np.arccos(cosine2))
        self.gamma = np.rad2deg(np.arccos(cosine3))
        self.file_name = "test_name"
        self.file_cont = \
            '\n'.join(["Image filename: some_name",
                       "Image filename: some/dir/db.h5",
                       "Peaks from peak search",
                       "  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel",
                       " 248.50  103.17       2.20     1440.39   q0a1",
                       " 519.07   72.50       2.08      878.44   q1a0",
                       "  52.50  265.35       0.86     2837.75   q0a2",
                       " 182.55  305.79       1.05     7230.42   q0a2",
                       " 172.41  337.50       0.91     2752.75   q0a2",
                       "End of peak list",
                       "--- Begin crystal",
                       "Cell parameters \
                        6.07787 12.18471 16.61399 nm, \
                        89.98647 91.09241 89.77393 deg",
                       "astar = +0.1628118 -0.0234613 +0.0047666 nm^-1",
                       "bstar = +0.0115679 +0.0777724 -0.0235210 nm^-1",
                       "cstar = +0.0019407 +0.0171354 +0.0576783 nm^-1",
                       "lattice_type = monoclinic", "centering = C",
                       "unique_axis = b", "profile_radius = 0.00135 nm^-1",
                       "predict_refine/det_shift x = -0.149 y = -0.264 mm",
                       "diffraction_resolution_limit = 1.92 nm^-1 or 5.20",
                       "num_reflections = 81", "num_saturated_reflections = 0",
                       "num_implausible_reflections = 0",
                       "Reflections measured after indexing",
                       "   h    k    l          I   sigma(I)\
                                  peak background  fs/px  ss/px panel",
                       " -24   -2  -18     -27.69      46.98      37.00\
                                 16.47  802.3  734.6 q2a6",
                       " -23   -5  -18     -36.17      48.68      55.00\
                                 16.83  838.4  680.9 q2a6",
                       " -22  -16  -24      14.58      29.55      27.00\
                                 14.08  833.1  500.2 q2a4",
                       " -22    2  -13      15.25      32.18      28.00\
                                 11.75  730.3 1145.9 q1a13",
                       "End of reflections",
                       "--- End crystal"
                       "----- End chunk -----"])
        self.file_wrong = \
            '\n'.join(["Image filename: some_name",
                       "Image filename: some/dir/db.h5",
                       "Peaks from peak search",
                       "  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel",
                       " 248.50  103.17       2.20     1440.39   q0a1",
                       " 519.07   72.50       2.08      878.44   q1a0",
                       "  52.50  265.35       0.86     2837.75   q0a2",
                       " 182.55  305.79       1.05     7230.42   q0a2",
                       " 172.41  337.50       0.91     2752.75   q0a2",
                       "End of peak list",
                       "--- Begin crystal",
                       "Cell parameters \
                        6.07787 12.18471 16.61399 nm, \
                        89.98647 91.09241 89.77393 deg",
                       "astar = +0.1628118 -0.0234613 +0.0047666 nm^-1",
                       "bstar = +0.0115679 +0.0777724 -0.0235210 nm^-1",
                       "cstar = +0.0019407 +0.0171354 +0.0576783 nm^-1",
                       "profile_radius = 0.00135 nm^-1",
                       "predict_refine/det_shift x = -0.149 y = -0.264 mm",
                       "diffraction_resolution_limit = 1.92 nm^-1 or 5.20",
                       "num_reflections = 81", "num_saturated_reflections = 0",
                       "num_implausible_reflections = 0",
                       "Reflections measured after indexing",
                       "   h    k    l          I   sigma(I)\
                                  peak background  fs/px  ss/px panel",
                       " -24   -2  -18     -27.69      46.98      37.00\
                                 16.47  802.3  734.6 q2a6",
                       " -23   -5  -18     -36.17      48.68      55.00\
                                 16.83  838.4  680.9 q2a6",
                       " -22  -16  -24      14.58      29.55      27.00\
                                 14.08  833.1  500.2 q2a4",
                       " -22    2  -13      15.25      32.18      28.00\
                                 11.75  730.3 1145.9 q1a13",
                       "End of reflections",
                       "--- End crystal"
                       "----- End chunk -----"])
        self.image = [{'name': 'Image filename: some/dir/db.h5',
                       'a': 60.7786850462726, 'b': 121.8471175709961,
                       'c': 166.1400763997097, 'alfa': 89.9864517320275,
                       'beta': 91.0923794044879, 'gamma': 89.7739024004247,
                       'centering': 'C', 'lattice_type': 'monoclinic',
                       'unique_axis': 'b'}]
        self.image_2 = [{'name': 'Image filename: some/dir/db.h5',
                         'a': 60.7786850462726, 'b': 121.8471175709961,
                         'c': 166.1400763997097, 'alfa': 89.9864517320275,
                         'beta': 91.0923794044879, 'gamma': 89.7739024004247,
                         'centering': 'C', 'lattice_type': 'monoclinic',
                         'centering': 'P', 'lattice_type': 'triclinic',
                         'unique_axis': '?'}]
        self.peak_list = ['q0a1', 'q1a0', 'q0a2']
        self.peak_reflections_list = ['q2a6', 'q2a4', 'q1a13']

    def test_cell_parameters(self):
        a, b, c, alfa, beta, gamma =\
            stream_read.cell_parameters(self.astar, self.bstar, self.cstar)
        self.assertEqual(a, self.a)
        self.assertEqual(b, self.b)
        self.assertEqual(c, self.c)
        self.assertEqual(gamma, self.gamma)

    def test_search_crystals_parameters(self):
        with patch('builtins.open', mock_open(read_data=self.file_cont),
                   create=True) as m:
            m.return_value.__iter__.return_value = self.file_cont.splitlines()
            s = stream_read.search_crystals_parameters(self.file_name)
            assert m.called
            m.assert_called_once_with(self.file_name)
            self.assertEqual(s[0]['name'], self.image[0]['name'])
            self.assertEqual(np.round(s[0]['a'], 13), self.image[0]['a'])
            self.assertEqual(np.round(s[0]['b'], 13), self.image[0]['b'])
            self.assertEqual(np.round(s[0]['c'], 13), self.image[0]['c'])
            self.assertEqual(np.round(s[0]['alfa'], 13), self.image[0]['alfa'])
            self.assertEqual(np.round(s[0]['beta'], 13), self.image[0]['beta'])
            self.assertEqual(np.round(s[0]['gamma'], 13),
                             self.image[0]['gamma'])
            self.assertEqual(s[0]['centering'], self.image[0]['centering'])
            self.assertEqual(s[0]['lattice_type'],
                             self.image[0]['lattice_type'])
            self.assertEqual(s[0]['unique_axis'], self.image[0]['unique_axis'])

        with patch('builtins.open', mock_open(read_data=self.file_wrong),
                   create=True) as m:
            m.return_value.__iter__.return_value = self.file_wrong.splitlines()
            s = stream_read.search_crystals_parameters(self.file_name)
            assert m.called
            m.assert_called_once_with(self.file_name)
            self.assertEqual(s[0]['name'], self.image_2[0]['name'])
            self.assertEqual(np.round(s[0]['a'], 13), self.image_2[0]['a'])
            self.assertEqual(np.round(s[0]['b'], 13), self.image_2[0]['b'])
            self.assertEqual(np.round(s[0]['c'], 13), self.image_2[0]['c'])
            self.assertEqual(np.round(s[0]['alfa'], 13),
                             self.image_2[0]['alfa'])
            self.assertEqual(np.round(s[0]['beta'], 13),
                             self.image_2[0]['beta'])
            self.assertEqual(np.round(s[0]['gamma'], 13),
                             self.image_2[0]['gamma'])
            self.assertEqual(s[0]['centering'], self.image_2[0]['centering'])
            self.assertEqual(s[0]['lattice_type'],
                             self.image_2[0]['lattice_type'])
            self.assertEqual(s[0]['unique_axis'],
                             self.image_2[0]['unique_axis'])

    def test_search_peaks(self):
        with patch('builtins.open', mock_open(read_data=self.file_cont),
                   create=True) as m:
            m.return_value.__iter__.return_value = self.file_cont.splitlines()
            s = stream_read.search_peaks(self.file_name, "db.h5",
                                         'Image filename:')
            assert m.called
            m.assert_called_once_with(self.file_name)
            result_peak_list = list(s[0].keys())
            result_peak_list.sort()
            self.peak_list.sort()
            self.assertEqual(result_peak_list, self.peak_list)
            result_peak_reflections_list = list(s[1].keys())
            result_peak_reflections_list.sort()
            self.peak_reflections_list.sort()
            self.assertEqual(result_peak_reflections_list,
                             self.peak_reflections_list)
            s = stream_read.search_peaks(self.file_name, "None",
                                         'Image filename:')
            self.assertEqual(s, ({}, {}))

    def test_fille_error(self):
        s = stream_read.search_peaks(self.file_name, "db.h5",
                                     'Image filename:')
        self.assertEqual(s, ({}, {}))
        s = stream_read.search_peaks(None, "db.h5",
                                     'Image filename:')
        self.assertEqual(s, ({}, {}))
        with self.assertRaises(SystemExit) as cm:
            s = stream_read.search_crystals_parameters("None")
        self.assertEqual(cm.exception.code, 1)
        with self.assertRaises(SystemExit) as cm:
            s = stream_read.search_crystals_parameters(None)
        self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
