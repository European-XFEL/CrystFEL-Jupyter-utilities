import h5py
import numpy
import unittest
import tempfile

import CrystFEL_Jupyter_utilities.data as data


class TestH5(unittest.TestCase):
    def setUp(self):
        self.temporaryfile = tempfile.NamedTemporaryFile(delete=True)
        self.h5file = h5py.File(self.temporaryfile)
        dts_data = self.h5file.create_dataset("/data/data",
                                              (10, 12), dtype='i')
        dts_data = self.h5file["/data/data"]
        dts_data[...] = numpy.linspace(0, 120, 120,
                                       endpoint=False).reshape(10, 12)
        dts_data2 = self.h5file.create_dataset(
            "/processing/hitfinder/peakinfo-assembled", (3, 4), dtype='d')
        dts_data2[...] = numpy.array(
            [[401.771728515625, 138.53125, 409.2867736816406, 3.0],
             [357.61907958984375, 0.3685567378997803, 1977.989501953125, 5.0],
             [-365.4927673339844, -172.0950164794922, 576.232666015625, 3.0]])
        dts_data = self.h5file.create_dataset("/LCLS/ebeamCharge", (1,),
                                              dtype='d')
        dts_data = self.h5file.create_dataset("/LCLS/evt41", (1,), dtype='d')
        dts_data = self.h5file.create_dataset(
            "/processing/cheetah/peakinfo-assembled", (3, 4), dtype='d')
        self.dict_test = {'LCLS': {
            'ebeamCharge': self.h5file["LCLS"]["ebeamCharge"],
            'evt41': self.h5file["LCLS"]["evt41"]},
            'data': {'data': self.h5file["data"]["data"]},
            'processing': {'cheetah': {
                'peakinfo-assembled': self.h5file["processing"]["cheetah"]['peakinfo-assembled']},
            'hitfinder': {
                'peakinfo-assembled': self.h5file["processing"]["hitfinder"]['peakinfo-assembled']}}}
        self.test_list = \
            [self.h5file["LCLS"]["ebeamCharge"], self.h5file["LCLS"]["evt41"],
             self.h5file["data"]["data"],
             self.h5file["processing"]["cheetah"]['peakinfo-assembled'],
             self.h5file["processing"]["hitfinder"]['peakinfo-assembled']]

    def tearDown(self):
        self.h5file.close()

    def test_catalog(self):
        diction = {x: self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        self.assertDictEqual(diction, self.dict_test)

    def test_list_datasets(self):
        diction = {x: self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        for elem in lista:
            self.assertIn(elem, self.test_list)
        for elem in self.test_list:
            self.assertIn(elem, lista)

    def test_get_data_peaks(self):
        diction = {x: self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        data_test = data.get_data_peaks(lista)
        self.assertEqual(data_test, self.h5file["processing"]["hitfinder"]['peakinfo-assembled'])

    def test_get_data_image(self):
        diction = {x: self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        image_data = data.get_data_image(lista)
        self.assertEqual(image_data, self.h5file["data"]["data"])

    def test_get_diction_data(self):
        self.h5file.close()
        data_test = data.get_diction_data(self.temporaryfile.name)
        data1 = {"Panels": numpy.linspace(0, 120, 120, endpoint=False,
                                          dtype='int32').reshape(10, 12),
                 "Peaks": numpy.array([[401.771728515625, 138.53125,
                                        409.2867736816406, 3.0],
                                       [357.61907958984375, 0.3685567378997803,
                                        1977.989501953125, 5.0],
                                       [-365.4927673339844, -172.0950164794922,
                                        576.232666015625, 3.0]])}
        numpy.testing.assert_array_equal(data1["Panels"],
                                         data_test["Panels"])
        numpy.testing.assert_array_equal(data1["Peaks"], data_test["Peaks"])


if __name__ == '__main__':
    unittest.main()
