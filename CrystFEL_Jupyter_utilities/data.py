"""Module for creating functions on h5 files.
"""
import logging
import sys

import h5py

from .panel import Detector

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

        List of all datasets from h5py.
    """
    for name in fileh5:
        if isinstance(fileh5[name], h5py.Group):
            list_datasets(fileh5[name], list_dataset)
        else:
            list_dataset.append(fileh5[name])


def get_peaks_data(list_dataset):
    """Returned numpy.ndarray with
    peaks data from '/processing/hitfinder/peakinfo-assembled'

    Parameters
    ----------
    list_dataset : list

        List of all datasets from h5py.

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


def get_panel_dataset(list_dataset, dataset_name, event=None, idx=0):
    """Returned numpy.ndarray with panel data.

    Parameters
    ----------
    list_dataset : list

        List of all datasets from h5py.
    dataset_name : Python unicode str (on py3)

        Dataset name.
    event : int

        Event to show from multi-event file.
    idx : int

        Index ndarray.
    Returns
    -------
    dataset[...] : The class 'numpy.ndarray'

        Peaks data.
    """
    for dataset in list_dataset:
        # when I find corect dataset
        if dataset.name == dataset_name:
            # if dataset has an array[event,idx,fs,ss]
            if dataset.ndim == 4:
                if event is None:
                    event = 0
                return dataset[int(event)][idx]
            else:
                return dataset[...]
    # when we need to find the first set of data with appropriate dimensions
    for dataset in list_dataset:
        # we return the first data with shape = 2 or 3(cxi)
        if event is None:
            if dataset.ndim == 2:
                return dataset[...]
        else:
            if dataset.ndim == 4:
                return dataset[int(event)][idx]
    raise Exception("There is no data representing panels in the h5 file")


def creat_panels(list_dataset, geom, image_size, event=None):
    """Create panels from raw data from the h5 file.
    The dataset name should be in the geometry file.
    Default is specific name '/data/data'.

    Parameters
    ----------
    list_dataset : list

       List of all datasets from h5py.
    geom : dict

        Dictionary with the geometry information loaded from the geomfile.
    image_size : touple

        numpy.array shape storing the minimum array size used in image.
    event : int

        Event to show from multi-event file.
    Returns
    -------
    panels : Dict

        Dictionary with panels object.
    """
    panels = {}
    dataset_name = "/data/data"

    for name in geom['panels']:
        dim_structure = geom['panels'][name]['dim_structure']
        panel_dataset_name = geom['panels'][name]['data']

        if ((len(dim_structure) == 4 and type(dim_structure[1]) is not int)
                or dim_structure[-2:] != ['ss', 'fs']):
            raise Exception("Unknown dimension structure")

        if dataset_name != panel_dataset_name:
            dataset_name = panel_dataset_name
            panel_data = get_panel_dataset(list_dataset, dataset_name,
                                           event, dim_structure[1])
        elif len(dim_structure) == 4 and type(dim_structure[1]) is int:
            panel_data = get_panel_dataset(list_dataset, dataset_name,
                                           event, dim_structure[1])

        panel = Detector(name=name, image_size=image_size,
                         corner_x=geom["panels"][name]["cnx"],
                         corner_y=geom["panels"][name]["cny"],
                         min_fs=geom["panels"][name]["min_fs"],
                         min_ss=geom["panels"][name]["min_ss"],
                         max_fs=geom["panels"][name]["max_fs"],
                         max_ss=geom["panels"][name]["max_ss"],
                         xfs=geom["panels"][name]["xfs"],
                         yfs=geom["panels"][name]["yfs"],
                         xss=geom["panels"][name]["xss"],
                         yss=geom["panels"][name]["yss"],
                         data=panel_data)

        panels[name] = panel

    return panels

    def cheetah_peaks_list(list_dataset, image_size):
        """Return a list of cheetah peaks form H5
        gets a peaks_data with data for all peaks given
        file h5.

        Parameters
        ----------
        peaks_data : numpy.array

            Data for cheetah peaks from h5 file.
        image_size : touple

            numpy.array shape storing the minimum array size used in image.
        Returns
        -------
        peaks : list

            List of class Peak object.
        """
        peaks = []
        peaks_data = get_peaks_data(list_dataset)
        try:
            # peaks_data[:,] next rows
            for row in peaks_data[:, ]:
                posx = row[0] + image_size[1]/2.0
                posy = -row[1] + image_size[0]/2.0
                peak = {"posx": posx, "posy": posy, "position": (posx, posy)}
                peaks.append(peak)
        except Exception:
            LOGGER.warning("Problem with peaks from the h5 file.")
        finally:
            return peaks


def get_file_data(file, event=None, geom=None, image_size=None):
    """Opens the H5 file and creates a tuple
    with two entries: panels and peaks.

    Parameters
    ----------
    file : Python unicode str (on py3)

        Path to hdf5 file.
    event : int

        Event to show from multi-event file.
    geom : dict

        Dictionary with the geometry information loaded from the geomfile.
    image_size : touple

        numpy.array shape storing the minimum array size used in image.
    Returns
    -------
    all_data : dict

        Dictionary with two entries: panels data and peaks data.
    """
    # the variable contains all dataset from H5
    list_dataset = []
    try:
        with h5py.File(file, "r") as fileh5:
            # create a list of all datasets
            list_datasets(fileh5, list_dataset)
            if geom is None:
                data = get_panel_dataset(list_dataset, "/data/data")
                return data
            else:
                panels = creat_panels(list_dataset, geom, image_size, event)
                peaks = cheetah_peaks_list(list_dataset, image_size)
                return panels, peaks
    except OSError:
        LOGGER.critical("Error opening the file H5")
        sys.exit(1)
    except Exception:
        exc_value = sys.exc_info()[1]
        LOGGER.critical(str(exc_value))
        sys.exit(1)
