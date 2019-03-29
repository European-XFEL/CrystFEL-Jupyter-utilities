"""
modules for creating functions on h5 files
"""
import h5py

import numpy as np

import sys


def list_datasets(diction, list_dataset):
    """
    recursively searches all Datasets
    from the h5 file and add at the end of the list
    """
    for name in diction:
        if isinstance(diction[name], dict):
            list_datasets(diction[name], list_dataset)

        else:
            list_dataset.append(diction[name])


def catalog(diction):
    """
    creat diction in diction
    datagroup is key and value is diction witch file inside
    if is dataset key is name dataset and value
    is object dataset

    """
    for key in diction.keys():
        # name is instance datagroup
        if isinstance(diction[key], h5py.Group):
            diction[key] = {z: diction[key][z] for z in diction[key]}
            # if is I create recursively diction with file in that group
            catalog(diction[key])
    return diction


def get_data_peaks(list_dataset):
    """
    returned matrix from dataset
    hitfinder/peakinfo are later in the file
    we are looking for the end because in LCLS H5
    this datasets is near the end
    """
    for dataset in list_dataset[::-1]:
        if dataset.name == "/processing/hitfinder/peakinfo-assembled":
            return dataset
    print("lack Dataset /processing/hitfinder/peakinfo-assembled \
containing peaki cheetah")


def get_data_image(list_dataset):
    """
    returns matrix
    we look for a raw data from h5 with a specific name '/data/data'
    if we don't find it we return the first datata with shape = 2
    TODO: check if we are actually getting image data.
    """
    for dataset in list_dataset:
        # panel data
        if dataset.name == "/data/data":
            return dataset
    for dataset in list_dataset:
        if len(dataset.shape) == 2:
            return dataset
    print("There is no data representing panels in the h5 file")
    sys.exit()


def get_diction_data(file):
    """
    opens the H5 file and creates a data dictionary
    where under the key "Paneles" there is data for everyone panels
    and under peaks "Peaks" are data for peaks from h5
    """
    # the variable contains all dataset from H5
    list_dataset = []
    try:
        with h5py.File(file, "r") as fileh5:
            diction = {x: fileh5[x] for x in fileh5}
            diction = catalog(diction)
            # create a list of all datasets
            list_datasets(diction, list_dataset)
            # copies the necessary matrices data
            data = np.copy(get_data_image(list_dataset))
            peaks = np.copy(get_data_peaks(list_dataset))
            # create a word with dnaymi
            diction = {"Paneles": data, "Peaks": peaks}
            return diction
    except OSError:
        print("Error opening the file H5")
        sys.exit()
