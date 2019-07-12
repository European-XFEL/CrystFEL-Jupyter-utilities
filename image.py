"""Module for image cxi.

Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
# Module for parsing geometry file
import cfelpyutils.crystfel_utils as c

from stream_read import search_peaks
from panel import Detector
from widget import ContrastSlider, PeakButtons, Radio


class ImageCxi:
    """Class for the display cxi image.

    Attributes
    ----------
    path : Python unicode str (on py3).

        Path to cxi file.
    streamfile : Python unicode str (on py3)

        Path to stream file.
    geomfile : Python unicode str (on py3)

        Path to geom file.
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    ax : The class:`matplotlib.axes.Axes`

        The Axes contains most of the figure elements.
    range : tuple

        min, max value for contrast.
    cmap : Python unicode str (on py3).

        Colormap name used to map scalar data to colors.
    matrix : numpy.array

        Data with pixels.
    raw_data : numpy.array

        Data from hdf5 file used in panles.
    image : The class `matplotlib.image.AxesImage`

        The image module supports basic rescaling and display operations.
        Returned by matplotlib imshow.
    panels : dict

        Containing Detector object from 'panel' module.
    event : int

            Event to show from multi-event file.
    """
    def __init__(self, path, geomfile, range=(0, 200), event=0, **kwargs):
        """
        Parameters
        ----------
        path : Python unicode str (on py3).

            Path to cxi file.
        range : tuple

            min, max value for contrast.
        streamfile : Python unicode str (on py3)

            Path to stream file.
       geomfile : Python unicode str (on py3)

            Path to geomfile file.
        event : int

            Event to show from multi-event file.
        """
        self.path = path
        self.geomfile = geomfile
        self.event = event
        self.streamfile = kwargs.get('streamfile')
        self.range = range
        self.cmap = 'inferno'

        self.raw_data = self.__open_file(self.path)
        self.__creat_figure()
        self.draw_image()
    def __creat_figure(self, figsize=(10,10)):
        """Creats new figure object, adds subplot.

        Parameters
        ----------
        figsize : tuple

            Figure size (default = (10, 10)).
        """
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(self.path + " Event " + str(self.event))

    def __panels_create(self, geom, image_size):
        """Creates panels adds peaks to the panels if they are in the sreamfile.

        Parameters
        ----------
        geom : dict

            Dictionary with the geometry information loaded from the geomfile.
        image_size : touple

            numpy.array shape storing the minimum array size used in image.
        """
        self.panels = {}
        peaks = self.__peak_search(self.streamfile, str(self.event))
        for name in geom['panels']:
            idx = int(re.findall('\d+', name)[0])
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
                                data=self.raw_data[idx])
                # some panels haven't peaks
            try:
                panel.peaks_search = peaks[0][name]
            except:
                pass
            try:
                panel.peaks_reflection = peaks[1][name]
            except:
                pass
            self.panels[name] = panel

    def __arrangement_panels(self):
        """Arranging panels in the image.
        """
        for name in self.panels:
            panel = self.panels[name]
            try:
                self.matrix[panel.position[0]: panel.position[0] +
                            panel.array.shape[0],
                            panel.position[1]: panel.position[1] +
                            panel.array.shape[1]] = \
                                panel.get_array_rotated()
            except:
                print("Wrong panel position: {}".format(panel.name))

    def draw_image(self):
        """Draw image.
        """
        # I need good geomfile.
        try:
            self.geom = c.load_crystfel_geometry(self.geomfile)
        except FileNotFoundError:
                print("Wrong geomfile!!!")
                sys.exit()
        # creat panels
        self.__panels_create(geom=self.geom, image_size=(1260, 1099))
        # creat numpy array for imshow
        # all pixel are np.nan
        self.matrix = np.empty((1260, 1099))*np.nan
        # I arrange the panels on the image
        self.__arrangement_panels()
        # creat imshow image with pixel array
        self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                    vmin=self.range[0], vmax=self.range[1])
        # add widget button peaks for `peak search`
        # and `peaks reflections measured after indexing`
        self.__add_widgets(number_peaks_button=2)

    def __add_widgets(self, number_peaks_button=0):
        """Adds widget to figure.
        """
        # widget to change contrast.
        axes = plt.axes([.90, 0.75, 0.05, 0.03], facecolor='lightyellow')
        self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                     ax=axes, label="Kontrast",
                                     vmin=self.range[0],
                                     vmax=self.range[1])
        # widget to change color map.
        axes = plt.axes([.90, 0.62, 0.09, 0.12], facecolor='lightyellow')
        self.radio = Radio(fig=self.fig, ax=axes,
                           labels=('inferno', 'plasma', 'Greys'),
                           cmap=self.cmap, image=self.image)
        # widgets to show peaks.
        self.peak_buttons =\
            PeakButtons(fig=self.fig, peaks=[],
                        number_peaks_button=number_peaks_button,
                        matrix=self.matrix, title=self.ax.get_title(),
                        radio=self.radio, slider=self.slider,
                        ax=self.ax, panels=self.panels)

    def __peak_search(self, streamfile, event):
        """Search for peaks `peak search` and `peak reflection` from streamfile.

       Parameters
        ----------
        streamfile : Python unicode str (on py3)

            Path to stream file.
        event : Python unicode str (on py3)

            Event to show from multi-event file.
        """
        peak_search, peaks_reflections = search_peaks(streamfile, event, 'Event')
        return (peak_search, peaks_reflections)

    def __open_file(self, path):
        """Opens cxi file and gets data for event.

        Parameters
        ----------
        path : Python unicode str (on py3).

            Path to hdf5 file.
        """
        try:
            with h5py.File(path, 'r') as file:
                raw_data = file["/entry_1/data_1/data"][self.event]
                return raw_data
        except OSError:
            print("Error opening the file ")
            sys.exit()
