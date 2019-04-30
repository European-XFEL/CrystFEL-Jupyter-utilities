"""
Module representing detector.
Creates a detector list from a geometry file (crystfel type) and
matrix size for the image.
"""

import numpy as np

from stream_read import dict_peak_in_name_h5


class Detector:
    """representing a detector.

    Attributes
    ----------

    min_fs : int

        min index in a column
    min_ss : int

    min index in a row
    max_fs : int

        max index in a column
    max_ss : int

        max index in a row
    xfs: double

        fast scan directions, value x
    yfs: double

        fast scan directions, value y
    xss: double

        slow scan directions, value x
    yss: double

        slow scan directions, value y
    corner_x : double

        coordinates of the panel corner from geom file
    corner_y : double

        coordinates of the panel corner from geom file
    array : numpy.array

        detector data
    position : tuple

        panel coordinates on the final image
    peak_list : list

        list of peaks from the stream file
    peak_near_bragg_list : list

        another peak list from the stream file. (peak like the
        check-near-bragg script does)
    """

    def __init__(self, image_size, name, min_fs, min_ss, max_fs, max_ss, xfs,
                 yfs, xss, yss, corner_x, corner_y, data):

        """
        Parameters
        ----------
        image_size : tuple

            image size
        name : str

            the name of the detector
        min_fs : int

            min index in a column
        min_ss : int

        min index in a row
        max_fs : int

            max index in a column
        max_ss : int

            max index in a row
        xfs: double

            fast scan directions, value x
        yfs: double

            fast scan directions, value y
        xss: double

            slow scan directions, value x
        yss: double

            slow scan directions, value y
        corner_x : double

            coordinates of the panel corner from geom file
        corner_y : double

            coordinates of the panel corner from geom file
        data : numpy.array

            data from each panel from part of the data - dataset in h5 file
        """
        self.name = name
        self.min_fs = min_fs
        self.min_ss = min_ss
        self.max_fs = max_fs
        self.max_ss = max_ss
        self.xfs = xfs
        self.yfs = yfs
        self.xss = xss
        self.yss = yss
        self.corner_x = corner_x
        self.corner_y = corner_y
        self.array = np.copy(data[self.min_ss: self.max_ss + 1,
                             self.min_fs: self.max_fs + 1])
        # my position in matrix
        self.position = (0, 0)
        self.peak_list = []
        self.peak_near_bragg_list = []
        self.image_size = image_size

    def get_peak_list(self):
        return self.peak_list

    def get_peak_near_bragg_list(self):
        return self.peak_near_bragg_list

    def get_array_rotated(self):
        """
        Returns array size for each panel after rotation.
        """
        self.with_rotatioon()
        return self.array

    def with_rotatioon(self):
        """By comparing xfs, yfs, xss and yss verifies which kind of rotation
        should be applied.
        """
        if np.abs(self.xfs) < np.abs(self.yfs) and \
                np.abs(self.xss) > np.abs(self.yss):
            if self.yfs > 0 and self.xss < 0:
                self.rot_y_x()
            elif self.yfs < 0 and self.xss > 0:
                self.rot_y_2x()
        elif np.abs(self.xfs) > np.abs(self.yfs) and \
                np.abs(self.xss) < np.abs(self.yss):
            if self.xfs < 0 and self.yss < 0:
                self.rot_y()
            elif self.xfs > 0 and self.yss > 0:
                self.rot_x()
        else:
            print(self.name, "Unknown rotation!")
            exit()

    def rot_x(self):
        """Rotation along x axis, columns stay the same, rows are switched.
        """
        # rotation x
        self.array = self.array[::-1, :]
        # The position of the panel
        # position x
        pos_x = int(np.round(self.image_size[0]/2.0 - self.corner_y -
                    self.array.shape[0], 0))
        # position y
        pos_y = int(np.round(self.image_size[1]/2.0 + self.corner_x, 0))
        # position
        self.position = (pos_x, pos_y)

        # two loop for:
        for peak_stream in self.peak_list:
            # for check peak detection

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            peak_stream.ss_px = self.array.shape[0] - 1 - peak_stream.ss_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)
        for peak_stream in self.peak_near_bragg_list:
            # for script near bragg

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            peak_stream.ss_px = self.array.shape[0] - 1 - peak_stream.ss_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)

    def rot_y(self):
        """Rotation along y axis; columns order is inversed, rows stay the same.
        """
        # rotation y
        self.array = self.array[:, ::-1]
        # The position of the panel
        # position y
        pos_y = int(self.image_size[1]/2) + int(self.corner_x) - \
            int(self.array.shape[1])
        # position x
        pos_x = int(self.image_size[0]/2) - int(self.corner_y)
        # position
        self.position = (pos_x, pos_y)

        # two loop for:
        for peak_stream in self.peak_list:
            # for check peak detection

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            peak_stream.fs_px = self.array.shape[1] - 1 - peak_stream.fs_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)
        for peak_stream in self.peak_near_bragg_list:
            # for script near bragg

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            peak_stream.fs_px = self.array.shape[1] - 1 - peak_stream.fs_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)

    def rot_y_x(self):
        """Rotation along y=x diagonal.
        """
        # rotation y=x digonal
        self.array = np.rot90(self.array)[:, ::-1]
        # The position of the panel
        # position y
        pos_y = int(np.round(self.image_size[1]/2.0 + self.corner_x -
                    self.array.shape[1], 0))

        # position x
        pos_x = int(np.round(self.image_size[0]/2.0 - self.corner_y -
                    self.array.shape[0], 0))
        # position
        self.position = (pos_x, pos_y)

        # two loop for:
        for peak_stream in self.peak_list:
            # for check peak detection

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            old_fs_px = peak_stream.fs_px
            old_ss_px = peak_stream.ss_px
            peak_stream.ss_px = self.array.shape[0] - old_fs_px - 1
            peak_stream.fs_px = self.array.shape[1] - old_ss_px - 1
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)

        for peak_stream in self.peak_near_bragg_list:
            # for script near bragg

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            old_fs_px = peak_stream.fs_px
            old_ss_px = peak_stream.ss_px
            peak_stream.ss_px = self.array.shape[0] - old_fs_px - 1
            peak_stream.fs_px = self.array.shape[1] - old_ss_px - 1
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)

    def rot_y_2x(self):
        """Rotation along y=-x transpose.
        """
        # rotation y=-x transpose
        self.array = np.transpose(self.array)
        # The position of the panel
        # position x
        pos_x = int(np.round(self.image_size[0]/2.0 - self.corner_y, 0))
        # position y
        pos_y = int(np.round(self.image_size[1]/2.0 + self.corner_x, 0))
        # position
        self.position = (pos_x, pos_y)

        # two loop for
        for peak_stream in self.peak_list:
            # for check peak detection

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            old_ss_px = peak_stream.ss_px
            peak_stream.ss_px = peak_stream.fs_px
            peak_stream.fs_px = old_ss_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)

        for peak_stream in self.peak_near_bragg_list:
            # for script near bragg

            # setting the peak relative
            # to the upper left corner of the panel
            # default: upper left corner of the matrix data
            peak_stream.ss_px -= self.min_ss
            peak_stream.fs_px -= self.min_fs

            # setting position after rotation
            old_ss_px = peak_stream.ss_px
            peak_stream.ss_px = peak_stream.fs_px
            peak_stream.fs_px = old_ss_px
            posx = peak_stream.fs_px + self.position[1]
            posy = peak_stream.ss_px + self.position[0]
            # new position of the peak in the panel after rotation
            peak_stream.position = (posx, posy)


def get_detectors(raw_data_from_h5, image_size, geom,
                  file_stream, file_h5):
    """Creates a dictionary with detector class objects as items and panel names
    as in the geometry file as keys. Function reads 'raw' data
    for each panel from the h5 file.

    Parameters
    ----------
    raw_data_from_h5 : numpy.array

        data from h5 for all detectors
    image_size : tuple

        image size
    geom : dict

        dictionary with the geometry information loaded from the geomfile.

    file_stream : path

        file stream path
    file_h5 : path

        file h5 path

    Returns
    -------
    panels : dict

        dictionary with class Detector object
            """
    panels = {panel_name: Detector(name=panel_name, image_size=image_size,
                                   corner_x=geom["panels"][panel_name]["cnx"],
                                   corner_y=geom["panels"][panel_name]["cny"],
                                   min_fs=geom["panels"][panel_name]["min_fs"],
                                   min_ss=geom["panels"][panel_name]["min_ss"],
                                   max_fs=geom["panels"][panel_name]["max_fs"],
                                   max_ss=geom["panels"][panel_name]["max_ss"],
                                   xfs=geom["panels"][panel_name]["xfs"],
                                   yfs=geom["panels"][panel_name]["xss"],
                                   xss=geom["panels"][panel_name]["yfs"],
                                   yss=geom["panels"][panel_name]["yss"],
                                   data=raw_data_from_h5)
              for panel_name in geom["panels"]}

    dict_witch_peak_list, dict_witch_peak_reflections_list =\
        dict_peak_in_name_h5(file_stream, file_h5)
    # complete all panels  with a list of peaks they have.
    # peaks which `cheack peak detection` shows
    # and peaks which  `near bragg` shows.
    for panel_name in dict_witch_peak_list:
        panels[panel_name].peak_list = dict_witch_peak_list[panel_name]

    for panel_name in dict_witch_peak_reflections_list:
        panels[panel_name].peak_near_bragg_list =\
            dict_witch_peak_reflections_list[panel_name]

    return panels


class Bad_places():
    """
    Class for mapping bad pixel regions on the image. Regions are read from the
    geometry file.

    name - bad region name from geom file
    image_size - whole image size
    min_x, min_y, max_x, max_y - corner coordinates on the image.
    """
    def __init__(self, image_size, name, min_x, max_x, min_y, max_y):
        self.name = name
        self.image_size = image_size

        self.min_x = int(np.round(min_x + self.image_size[1]/2, 0))
        self.max_x = int(np.round(max_x + self.image_size[1]/2, 0))
        self.min_y = int(np.round(-min_y + self.image_size[0]/2, 0))
        self.max_y = int(np.round(-max_y + self.image_size[0]/2, 0))

        # sprawdzam czy wspolzedne nie sa po za moim obrazem
        if self.min_x < 0:
            self.min_x = 0
        if self.max_x > self.image_size[0] - 1:
            self.max_x = self.image_size[0] - 1
        if self.min_y > self.image_size[1] - 1:
            self.min_y = self.image_size[1] - 1
        if self.max_y < 0:
            self.max_y = 0

        self.shape = (self.min_y - self.max_y, self.max_x - self.min_x)
        self.array = np.zeros(self.shape)
        # te obszary były zle!!

    def get_array(self):
        """
        Array with bad pixel regions which will cover the area on the image.
        """
        return self.array


def get_diction_bad_places(image_size, geom):
    """
    Creates a dictionary with bad pixel regions from geom file.
    """

    dict_witch_bad_places = {bad_name: Bad_places(image_size, bad_name,
                             geom['bad'][bad_name]['min_x'],
                             geom['bad'][bad_name]['max_x'],
                             geom['bad'][bad_name]['min_y'],
                             geom['bad'][bad_name]['max_y'])

                             for bad_name in geom['bad']}

    return dict_witch_bad_places
