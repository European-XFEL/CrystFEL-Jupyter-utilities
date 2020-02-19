import h5py
import numpy
import unittest
import tempfile

import CrystFEL_Jupyter_utilities.data as data


class TestH5(unittest.TestCase):
    def setUp(self):
        self.temporaryfile = tempfile.NamedTemporaryFile(delete=True)
        self.h5file = h5py.File(self.temporaryfile, mode="r+")
        self.peak_data = numpy.array(
            [[401.771728515625, 138.53125, 409.2867736816406, 3.0],
             [357.61907958984375, 0.3685567378997803, 1977.989501953125, 5.0],
             [-365.4927673339844, -172.0950164794922, 576.232666015625, 3.0]])
        self.panel_data = numpy.array([[1, 1, 1, 1], [2, 2, 2, 2],
                                      [3, 3, 3, 3], [4, 4, 4, 4]])
        self.panel_data_2 = numpy.array([[[[1, 1], [1, 1]]]])
        dts_data = self.h5file.create_dataset("/data/data",
                                              (4, 4), dtype='i')
        dts_data_2 = self.h5file.create_dataset("/entry1/data",
                                                (1, 1, 2, 2), dtype='i')
        dts_data[...] = self.panel_data
        dts_data_2[...] = self.panel_data_2
        dts_data2 = self.h5file.create_dataset(
            "/processing/hitfinder/peakinfo-assembled", (3, 4), dtype='d')
        dts_data2[...] = self.peak_data
        dts_data = self.h5file.create_dataset("/LCLS/ebeamCharge", (1,),
                                              dtype='d')
        dts_data = self.h5file.create_dataset("/LCLS/evt41", (1,), dtype='d')
        dts_data = self.h5file.create_dataset(
            "/processing/cheetah/peakinfo-assembled", (3, 4), dtype='d')
        self.test_list = [
            self.h5file["LCLS"]["ebeamCharge"], self.h5file["LCLS"]["evt41"],
            self.h5file["data"]["data"], self.h5file["entry1"]["data"],
            self.h5file["processing"]["cheetah"]['peakinfo-assembled'],
            self.h5file["processing"]["hitfinder"]['peakinfo-assembled']]
        self.geom = {'panels': {'q0a0': {'cnx': 0, 'cny': 10, 'min_fs': 0,
                                         'min_ss': 0, 'max_fs': 2, 'max_ss': 1,
                                         'xfs': 1, 'yfs': 0, 'xss': 1,
                                         'yss': 1, 'data': None,
                                         'dim_structure': ['ss', 'fs']}}}

    def tearDown(self):
        self.h5file.close()

    def test_list_datasets(self):
        list_datasets = []
        data.list_datasets(self.h5file, list_datasets)
        for elem in list_datasets:
            self.assertIn(elem, self.test_list)
        for elem in self.test_list:
            self.assertIn(elem, list_datasets)

    def test_cheetah_peaks_list(self):
        list_datasets = []
        data.list_datasets(self.h5file, list_datasets)
        peaks = data.cheetah_peaks_list(list_datasets, (10, 10))
        self.assertEqual(peaks[0], {'posx': 401.771728515625+5,
                                    'posy': 5-138.53125,
                                    'position': (401.771728515625+5,
                                                 5-138.53125)})
        self.assertEqual(peaks[2], {'posx': -365.4927673339844+5,
                                    'posy': 5+172.0950164794922,
                                    'position': (-365.4927673339844+5,
                                                 5+172.0950164794922)})

    def test_get_peaks_data(self):
        list_datasets = []
        data.list_datasets(self.h5file, list_datasets)
        data_test = data.get_peaks_data(list_datasets)
        numpy.testing.assert_array_equal(data_test, self.peak_data)
        del self.h5file["/processing/hitfinder/peakinfo-assembled"]
        data.list_datasets(self.h5file, list_datasets)
        data_test = data.get_peaks_data(list_datasets)
        numpy.testing.assert_array_equal(data_test, None)

    def test_get_panel_dataset(self):
        list_datasets = []
        data.list_datasets(self.h5file, list_datasets)
        panel_data = data.get_panel_dataset(list_datasets, "/data/data")
        numpy.testing.assert_array_equal(panel_data, self.panel_data)
        panel_data = data.get_panel_dataset(list_datasets, "/entry1/data")
        numpy.testing.assert_array_equal(panel_data, self.panel_data_2[0, 0])
        panel_data = data.get_panel_dataset(list_datasets, "/brak/brak")
        numpy.testing.assert_array_equal(panel_data, self.panel_data)
        panel_data = data.get_panel_dataset(list_datasets, "/brak/brak", 0)
        numpy.testing.assert_array_equal(panel_data, self.panel_data_2[0, 0])

    def test_creat_panels(self):
        list_datasets = []
        data.list_datasets(self.h5file, list_datasets)
        panels = data.creat_panels(list_datasets, self.geom, (0, 0))
        self.assertEqual(list(panels.keys()), ['q0a0'])
        numpy.testing.assert_array_equal(panels['q0a0'].array,
                                         self.panel_data[:2, :3])
        self.geom['panels']['q0a0']['dim_structure'] = ['%', 0, 'ss', 'fs']
        self.geom['panels']['q0a0']['data'] = "/entry1/data"
        self.geom['panels']['q0a0']['max_fs'] = 1
        panels = data.creat_panels(list_datasets, self.geom, (0, 0))
        numpy.testing.assert_array_equal(panels['q0a0'].array,
                                         self.panel_data_2[0, 0, :])


if __name__ == '__main__':
    unittest.main()
