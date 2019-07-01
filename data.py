"""Module for creating functions on h5 files.
"""
import h5py
import numpy as np
import sys


def list_datasets(dictionary, list_dataset):
    """Recursively searches all Datasets
    from the h5 file and add at the end of the list.

    Parameters
    ----------
    dictionary : dict

        dictionary in a dictionary with dataset due to a datagroup.
    list_dataset : list

        list with all dataset from h5py.
    """
    for name in dictionary:
        if isinstance(dictionary[name], dict):
            list_datasets(dictionary[name], list_dataset)

        else:
            list_dataset.append(dictionary[name])


def catalog(dictionary):
    """Creat recursively dictionary in dictionary
    datagroup is key and value is diction witch file inside
    if is dataset key is name dataset and value
    is object dataset.

    Parameters
    ----------
    dictionary : dict

        dictionary in dictionary with dataset.

    Returns
    -------
    dictionary : dict

        dictionary in a dictionary with dataset due to a datagroup.
    """
    for key in dictionary.keys():
        # name is instance datagroup
        if isinstance(dictionary[key], h5py.Group):
            dictionary[key] = {z: dictionary[key][z] for z in dictionary[key]}
            # if is I create recursively dictionary with file in that group
            catalog(dictionary[key])
    return dictionary


def get_data_peaks(list_dataset):
    """Returned Dataset with peaks data from 'hitfinder/peakinfo'.


    Parameters
    ----------
    list_dataset : list

        list with dataset from h5py.

    Returns
    -------
    dataset : The class 'h5py._hl.dataset.Dataset'

        Dataset with peaks data.
    """
    # we are looking for the end because in LCLS H5.
    # this datasets is near the end.
    for dataset in list_dataset[::-1]:
        if dataset.name == "/processing/hitfinder/peakinfo-assembled":
            return dataset
    print("lack Dataset /processing/hitfinder/peakinfo-assembled \
containing peaki cheetah")


def get_data_image(list_dataset):
    """Look for a raw data from h5 with a specific name '/data/data'
    if we don't find it we return the first datata with shape = 2.

    Parameters
    ----------
    list_dataset : list

        list with dataset from h5py.

    Returns
    -------
    dataset : The class 'h5py._hl.dataset.Dataset'

        Dataset with panels data.
    """
    for dataset in list_dataset:
        # panel data
        if dataset.name == "/data/data":
            return dataset
    for dataset in list_dataset:
        # we return the first datata with shape = 2
        if len(dataset.shape) == 2:
            return dataset
    print("There is no data representing panels in the h5 file")
    sys.exit()


def get_diction_data(file):
    """Opens the H5 file and creates a dictionary
    with two entries: "Panels" with image data and
    "Peaks" with peaks data.

    Parameters
    ----------
    file : Python unicode str (on py3)

        Path to hdf5 file.

    Returns
    -------
    dictionary : dict

        dictionary with two entries: image data and peaks data.
    """
    # the variable contains all dataset from H5
    list_dataset = []
    try:
        with h5py.File(file, "r") as fileh5:
            dictionary = {x: fileh5[x] for x in fileh5}
            dictionary = catalog(dictionary)
            # create a list of all datasets
            list_datasets(dictionary, list_dataset)
            # copies the necessary matrices data
            data = np.copy(get_data_image(list_dataset))
            peaks = np.copy(get_data_peaks(list_dataset))
            # create a word with dnaymi
            dictionary = {"Panels": data, "Peaks": peaks}
            return dictionary
    except OSError:
        print("Error opening the file H5")
        sys.exit()
