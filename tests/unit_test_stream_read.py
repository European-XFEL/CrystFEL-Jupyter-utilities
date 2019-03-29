import unittest
from unittest.mock import mock_open, patch
import os
import sys
sys.path.insert(0, os.getcwd())
import stream_read


class Test_Stream_read(unittest.TestCase):

    def setUp(self):
        self.file_name = "test_name"
        self.file_content = '\n'.join(["Image filename: db.h5",
"Peaks from peak search",
"  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel",
" 248.50  103.17       2.20     1440.39   q0a1",
" 519.07   72.50       2.08      878.44   q1a0",
"  52.50  265.35       0.86     2837.75   q0a2",
" 182.55  305.79       1.05     7230.42   q0a2",
" 172.41  337.50       0.91     2752.75   q0a2",
"End of peak list",
"--- Begin crystal",
"Cell parameters 6.07787 12.18471 16.61399 nm, 89.98647 91.09241 89.77393 deg",
"astar = +0.1628118 -0.0234613 +0.0047666 nm^-1",
"bstar = +0.0115679 +0.0777724 -0.0235210 nm^-1",
"cstar = +0.0019407 +0.0171354 +0.0576783 nm^-1",
"lattice_type = monoclinic", "centering = C",
"unique_axis = b", "profile_radius = 0.00135 nm^-1",
"predict_refine/det_shift x = -0.149 y = -0.264 mm",
"diffraction_resolution_limit = 1.92 nm^-1 or 5.20",
"num_reflections = 81", "num_saturated_reflections = 0",
"num_implausible_reflections = 0", "Reflections measured after indexing",
"   h    k    l          I   sigma(I)       peak background  fs/px  ss/px panel",
" -24   -2  -18     -27.69      46.98      37.00      16.47  802.3  734.6 q2a6",
" -23   -5  -18     -36.17      48.68      55.00      16.83  838.4  680.9 q2a6",
" -22  -16  -24      14.58      29.55      27.00      14.08  833.1  500.2 q2a4",
" -22    2  -13      15.25      32.18      28.00      11.75  730.3 1145.9 q1a13",
"End of reflections"])
        self.image = {'Image filename: db.h5':
                      ['Cell parameters 6.07787 12.18471 16.61399 nm, 89.98647 91.09241 89.77393 deg',
                       'astar = +0.1628118 -0.0234613 +0.0047666 nm^-1',
                       'bstar = +0.0115679 +0.0777724 -0.0235210 nm^-1',
                       'cstar = +0.0019407 +0.0171354 +0.0576783 nm^-1',
                       'lattice_type = monoclinic', 'centering = C',
                       'unique_axis = b',
                       'profile_radius = 0.00135 nm^-1',
                       'predict_refine/det_shift x = -0.149 y = -0.264 mm',
                       'diffraction_resolution_limit = 1.92 nm^-1 or 5.20',
                       'num_reflections = 81', 'num_saturated_reflections = 0',
                       'num_implausible_reflections = 0']}
        # # Instantiate the object where the data is file_content
        # self.mock_open = mock_open(read_data=file_content)
        # # And add the omitted __iter__ &amp;amp;amp; __next__ methods
        # self.mock_open.return_value.__iter__ = lambda self: self
        # self.mock_open.return_value.__next__ = lambda self: self.readline()
        self.peak_list = ['q0a1', 'q1a0', 'q0a2']
        self.peak_reflections_list = ['q2a6', 'q2a4', 'q1a13']
    def test_diction_crystal_return(self):
        with patch('builtins.open', mock_open(read_data=self.file_content),
                   create=True) as m:
            m.return_value.__iter__.return_value = self.file_content.splitlines()
            s = stream_read.diction_crystal_return(self.file_name)
            assert m.called
            m.assert_called_once_with(self.file_name)
            self.assertEqual(s, self.image)

    def test_dict_peak_in_name_h5(self):
        with patch('builtins.open', mock_open(read_data=self.file_content),
                   create=True) as m:
            m.return_value.__iter__.return_value = self.file_content.splitlines()
            s = stream_read.dict_peak_in_name_h5(self.file_name, "db.h5")
            assert m.called
            m.assert_called_once_with(self.file_name)
            self.assertEqual(list(s[0].keys()), self.peak_list)
            self.assertEqual(list(s[1].keys()), self.peak_reflections_list)

if __name__ == '__main__':
        unittest.main()
