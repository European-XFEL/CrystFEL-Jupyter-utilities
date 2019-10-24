"""Module for creating functions on h5 files.
"""
import logging
import sys

import h5py
import numpy as np

# remove all the handlers.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
LOGGER = logging.getLogger(__name__)
# create console handler with a higher log level
ch = logging.StreamHandler()
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(levelname)s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s\n')
ch.setFormatter(formatter)
# add the handlers to logger
LOGGER.addHandler(ch)


def list_datasets(fileh5, list_dataset):
    """Recursively searches all Datasets
    from the h5 file and add at the end of the list.

    Parameters
    ----------
    fileh5 : class h5py._hl.files.File

        H5py file with image data.
    list_dataset : list

        List with all dataset from h5py.
    """
    for name in fileh5:
        if isinstance(fileh5[name], h5py.Group):
            list_datasets(fileh5[name], list_dataset)
        else:
            list_dataset.append(fileh5[name])

def get_data_peaks(list_dataset):
    """Returned Dataset with peaks data from 'hitfinder/peakinfo'.

    Parameters
    ----------
    list_dataset : list

        List with dataset from h5py.

    Returns
    -------
    dataset[...] : The class 'numpy.ndarray'

        Peaks data.
    """
    # we are looking for the end because in LCLS H5.
    # this datasets is near the end.
    for dataset in list_dataset[::-1]:
        if dataset.name == "/processing/hitfinder/peakinfo-assembled":
            return dataset[...]
    LOGGER.warning("Missing Dataset /processing/hitfinder/peakinfo-assembled \
        containing peaki cheetah")


def get_data_image(list_dataset):
    """Look for a raw data from h5 with a specific name '/data/data'
    if we don't find it we return the first datata with shape = 2.

    Parameters
    ----------
    list_dataset : list

        List with dataset from h5py.

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
    raise Exception("There is no data representing panels in the h5 file")


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

        Dictionary with two entries: image data and peaks data.
    """
    # the variable contains all dataset from H5
    list_dataset = []
    try:
        with h5py.File(file, "r") as fileh5:
            # create a list of all datasets
            list_datasets(fileh5, list_dataset)
            # copies the necessary matrices data
            data = np.copy(get_data_image(list_dataset))
            peaks = np.copy(get_data_peaks(list_dataset))
            # create a word with dnaymi
            dictionary = {"Panels": data, "Peaks": peaks}
            return dictionary
    except OSError:
        LOGGER.critical("Error opening the file H5")
        sys.exit(1)
    except Exception:
        exc_value = sys.exc_info()[1]
        LOGGER.critical(str(exc_value))
        sys.exit(1)
