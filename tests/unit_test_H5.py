import unittest
import numpy
import h5py 
import os
import sys 
sys.path.insert(0, os.getcwd())
import data
class TestH5(unittest.TestCase):
    def setUp(self):
        if os.path.exists("tests/sample.h5"):
            os.remove("tests/sample.h5")
        else:
            pass 
        self.h5file = h5py.File("tests/sample.h5",'a')
        
        dts_data = self.h5file.create_dataset("/data/data",(10,12),dtype='i')
        dts_data = self.h5file["/data/data"] 
        dts_data[...] = numpy.linspace(0,120,120,endpoint=False).reshape(10,12)
        dts_data2 = self.h5file.create_dataset("/processing/hitfinder/peakinfo-assembled",(3,4),dtype='d')
        dts_data2[...] = numpy.array([[401.771728515625, 138.53125, 409.2867736816406, 3.0],\
            [357.61907958984375, 0.3685567378997803, 1977.989501953125,5.0],\
            [-365.4927673339844, -172.0950164794922, 576.232666015625, 3.0]])
        dts_data = self.h5file.create_dataset("/LCLS/ebeamCharge",(1,),dtype='d')
        dts_data = self.h5file.create_dataset("/LCLS/evt41",(1,),dtype='d')
        dts_data = self.h5file.create_dataset("/processing/cheetah/peakinfo-assembled",(3,4),dtype='d')
        self.dict_test = {'LCLS': {'ebeamCharge': self.h5file["LCLS"]["ebeamCharge"], 'evt41': self.h5file["LCLS"]["evt41"]}, 'data': {'data': self.h5file["data"]["data"]}, \
        'processing': {'cheetah': {'peakinfo-assembled': self.h5file["processing"]["cheetah"]['peakinfo-assembled']}, \
                      'hitfinder': {'peakinfo-assembled': self.h5file["processing"]["hitfinder"]['peakinfo-assembled']}}}    

        self.test_list = [self.h5file["LCLS"]["ebeamCharge"], self.h5file["LCLS"]["evt41"], self.h5file["data"]["data"],\
                          self.h5file["processing"]["cheetah"]['peakinfo-assembled'], \
                          self.h5file["processing"]["hitfinder"]['peakinfo-assembled']]
        
    def tearDown(self):
        self.h5file.close()
        if os.path.exists("tests/sample.h5"):
            os.remove("tests/sample.h5")
        else:
            pass 
    def test_katalog(self):
        diction = {x:self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        self.assertDictEqual(diction, self.dict_test)

    def test_list_datasets(self):
        diction = {x:self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        self.assertListEqual(lista,self.test_list)

    def test_dane_peaks(self):
        diction = {x:self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        data_test = data.get_data_peaks(lista)
        self.assertEqual(data_test, self.h5file["processing"]["hitfinder"]['peakinfo-assembled'])
    def test_dane_obrazu(self):
        diction = {x:self.h5file[x] for x in self.h5file}
        diction = data.catalog(diction)
        lista = []
        data.list_datasets(diction, lista)
        dane_obrazu = data.get_data_image(lista)
        self.assertEqual(dane_obrazu, self.h5file["data"]["data"])
    def test_data(self):
        self.h5file.close()
        data_test = data.get_diction_data('tests/sample.h5')
        data1 = {"Paneles":numpy.linspace(0,120,120,endpoint=False,dtype='int32').reshape(10,12),
        "Peaks": numpy.array([[401.771728515625, 138.53125, 409.2867736816406, 3.0],\
            [357.61907958984375, 0.3685567378997803, 1977.989501953125,5.0],\
            [-365.4927673339844, -172.0950164794922, 576.232666015625, 3.0]])}
        numpy.testing.assert_array_equal(data1["Paneles"],data_test["Paneles"])
        numpy.testing.assert_array_equal(data1["Peaks"],data_test["Peaks"])       
if __name__ == '__main__':
        unittest.main()