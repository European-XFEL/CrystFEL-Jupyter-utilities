"""Main module for running code.

Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""

import logging
import re
import sys
# Module for parsing geometry file and determining size of the
# image after panel arrangement.
from cfelpyutils.crystfel_utils import load_crystfel_geometry
import matplotlib.pyplot as plt
import numpy as np

from .data import get_file_data
from .panel import bad_places
from .stream_read import search_peaks
from .widget import ContrastSlider, PeakButtons, Radio

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
LOGGER.setLevel("INFO")

__all__ = ['Image']


class Image:
    """Class for the main image.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    ax : The class:`matplotlib.axes.Axes`

            The Axes contains most of the figure elements
    vmax : int

        max value for contrast.
    vmin : int

        min value for contrast.
    cmap : Python unicode str (on py3).

        Colormap name used to map scalar data to colors.
    matrix : numpy.array

        The image data filled with data from the panels.
    image : The class `matplotlib.image.AxesImage`

        The image module supports basic rescaling and display operations.
        Returned by matplotlib imshow.
    peaks : list

        Containing peak objects from 'peak_h5' module.
    detectors : dict

        Containing Detector object from 'panel' module.
    bad_places : list

        Containing BadRegion object from 'panel' module.
    """

    def __init__(self, path, range=(0, 600), geomfile=None,
                 streamfile=None, event=None):
        """Method for initializing image and checking options how to run code.

        Parameters
        ----------
        path : Python unicode str (on py3).

            Path to h5 file.
        range : tuple

            min, max value for contrast.
       geomfile : Python unicode str (on py3)

            Path to geometry file.
        streamfile : Python unicode str (on py3)

            Path to stream file.
        event : int

            Event to show from multi-event file.
        """
        self.path = path
        self.geomfile = geomfile
        self.streamfile = streamfile
        self.event = event
        # Dictionary containing panels and peaks info from the h5 file.
        # Creating a figure and suplot
        # used 10X10 because default size is to small in notebook
        self.fig, self.ax = self.__creat_figure(path=self.path,
                                                figsize=(9.5, 9.5),
                                                event=self.event)
        # Setting the contrast.
        self.range = range
        # Setting the default colour map.
        self.cmap = 'inferno'
        # Following initialized depending on the execution arguments.
        self.matrix = None
        self.image = None
        self.peaks = None
        self.detectors = None
        self.bad_places = None
        # For displaying the image in the right orientation (?).
        # display without laying the panels
        if self.geomfile is None:
            # Just the image from file with no buttons or reconstruction.
            data = get_file_data(self.path)
            self.matrix = np.copy(data)
            # Rotating to get the same image as CrystFEL hdfsee.
            self.matrix = self.matrix[::-1, :]
            # Creating the image with imshow().
            self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                        vmin=self.range[0],
                                        vmax=(self.range[0]+self.range[1])/2)
            # Slider position.
            axes = plt.axes([.90, 0.78, 0.09, 0.075], facecolor='lightyellow')
            self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                         ax=axes, label="Contrast",
                                         vmax=self.range[1],
                                         vmin=self.range[0])
            # Radio (?) position.
            # Position RadioButton
            axes2 = plt.axes([.90, 0.65, 0.09, 0.12], facecolor='lightyellow')
            # created button radio
            self.radio = Radio(fig=self.fig, ax=axes2,
                               labels=('inferno', 'plasma', 'Greys'),
                               cmap=self.cmap, image=self.image)
        # When the geometry file was provided:
        else:
            try:
                self.geom = load_crystfel_geometry(self.geomfile)
            # Dictionary with information about the image: panels, bad places.
            except FileNotFoundError:
                LOGGER.critical("Error while opening geometry file.")
                sys.exit(1)
            # Panels reconstruction:
            self.display_arrangement_view()
            # Slider position.
            axes = plt.axes([.90, 0.78, 0.09, 0.075], facecolor='lightyellow')
            self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                         ax=axes, label="Contrast",
                                         vmax=self.range[1],
                                         vmin=self.range[0])
            # Radio position.
            axes2 = plt.axes([.90, 0.65, 0.09, 0.12], facecolor='lightyellow')
            # Radio button.
            self.radio = Radio(fig=self.fig, ax=axes2,
                               labels=('inferno', 'plasma', 'Greys'),
                               cmap=self.cmap, image=self.image)
            # Positioning buttons for switching on/off displaying peaks from
            # h5 file in path /processing/hitfinder/peakinfo-assembled.
            # Position has to be saved to be able to
            # determine what has been clicked.
            # For displaying peaks from stream file.
            if self.streamfile is not None:
                # Additional buttons for switching on/off
                # peaks from stream file.
                self.peak_buttons = PeakButtons(fig=self.fig, peaks=self.peaks,
                                                number_peaks_button=3,
                                                matrix=self.matrix,
                                                title=self.ax.get_title(),
                                                radio=self.radio,
                                                slider=self.slider,
                                                ax=self.ax,
                                                panels=self.detectors)
            else:
                # Only one button for showing peaks from h5 file.
                self.peak_buttons = PeakButtons(fig=self.fig, peaks=self.peaks,
                                                number_peaks_button=1,
                                                matrix=self.matrix,
                                                title=self.ax.get_title(),
                                                radio=self.radio,
                                                slider=self.slider,
                                                ax=self.ax,
                                                panels=self.detectors)
        # Display the image:
        plt.show()

    def __creat_figure(self, path, figsize=(10, 10), event=None):
        """Creats new figure object, adds subplot.

        Parameters
        ----------
        path : Python unicode str (on py3).

            Path to the image data file.
        figsize : tuple

            Figure size (default = (10, 10)).
        event : Python unicode str (on py3)

            Event to show from multi-event file.

        Returns
        -------
        fig : The class:`matplotlib.figure.Figure`.

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            The Axes contains most of the figure elements.
        """
        fig, ax = plt.subplots(figsize=figsize)
        event_name = " Event " + str(event)
        if event is None:
            event_name = ""
        # Setting the title to filename path.
        ax.set_title(path + event_name)
        return fig, ax

    def add_stream_peaks(self, panels, streamfile, event=None):
        """Search for peaks `peak search` and
        `peak reflection` from streamfile.

       Parameters
        ----------
        streamfile : Python unicode str (on py3)

            Path to stream file.
        panels : list

            List of panels object.
        event : Python unicode str (on py3)

            Event to show from multi-event file.
        """
        if event is None:
            line_name = self.path.strip().split('/')[-1]
            peaks_search, peaks_reflection =\
                search_peaks(streamfile, line_name, 'Image filename:')
        else:
            peaks_search, peaks_reflection = \
                search_peaks(streamfile, str(event), 'Event')
        # add peaks to each panel,not everyone can have them.
        for name in panels:
            # peaks_search doesn't have the key panel.name
            try:
                panels[name].peaks_search = peaks_search[name]
            except KeyError:
                pass
            # peaks_reflection doesn't have the key panel.name
            try:
                panels[name].peaks_reflection = peaks_reflection[name]
            except KeyError:
                pass

    def display_arrangement_view(self):
        """Creating the image filled with ones (?) and
        applies bad pixel mask (?). Then adds panels (?).
        """
        columns, rows, center_x, center_y = self.find_image_size(self.geom)
        # Creating an 'empty' matrix ready to be filled with pixel data.
        self.matrix = np.ones((rows, columns))
        # Creates a detector dictionary with keys as panels name and values
        # as class Panel objects.
        self.detectors, self.peaks = get_file_data(
            file=self.path, geom=self.geom, event=self.event,
            image_size=(rows, columns))
        if self.streamfile is not None:
            self.add_stream_peaks(self.detectors, self.streamfile, self.event)
        # Arranging the panels.
        self.arrangement_panels(center_x, center_y)
        # Add mask
        if self.event is None:
            # Creating a bad pixel mask (?).
            self.bad_places = bad_places((rows, columns), self.geom,
                                         center_x, center_y)
            # Masking the bad pixels (?).
            self.arrangement_bad_places()
        # Displaying the image.
        self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                    vmin=self.range[0],
                                    vmax=(self.range[0]+self.range[1])/2)

    def arrangement_bad_places(self):
        """Iterates through each mask and
           sets them in the right place in the image.

        Raises
        ------
        ValueError
            If wrong bad_place position.
        """
        for name_bad_place in self.bad_places:
            bad_place = self.bad_places[name_bad_place]
            try:
                self.matrix[bad_place.max_y: bad_place.max_y +
                            bad_place.shape[0],
                            bad_place.min_x: bad_place.min_x +
                            bad_place.array.shape[1]] = bad_place.get_array()
            except ValueError:
                LOGGER.critical(
                    "Wrong mask position: {}".format(bad_place.name))
                sys.exit(1)

    def arrangement_panels(self, center_x, center_y):
        """Iterates through each detector and
           sets them in the right place in the image.
        Parameters
        ----------
        center_x : int

            Displacement of centre x-axis.
        center_y : int

            Displacement of centre y-axis.
        """
        for key in self.detectors:
            detector = self.detectors[key]
        # Trying to reposition the panels.
            try:
                self.matrix[detector.position[0]: detector.position[0] +
                            detector.array.shape[0],
                            detector.position[1]: detector.position[1] +
                            detector.array.shape[1]] = \
                                detector.get_array_rotated(center_x, center_y)
            except ValueError:
                text = " ".join(["Wrong panel position",
                                "{}, Position: {}".format(detector.name,
                                                          detector.position)])
                LOGGER.critical(text)
                sys.exit(1)

    def local_range(self, panel):
        """Calculates the location of the two extreme corners of the panel.

        Parameters
        ----------
        panel : dict

            A CrystFEL geometry data for panel.

        Returns
        -------
        (local_xmin, local_xmax, local_ymin, local_ymax) : tuple

            The location of the two extreme corners of the panel.
        """
        if (np.abs(panel['xfs']) < np.abs(panel['xss']) and
                np.abs(panel['yfs']) > np.abs(panel['yss'])):
            if panel['xss'] > 0 and panel['yfs'] < 0:
                # After rotation along y=x
                local_xmax = panel['cnx']
                local_ymin = panel['cny']
                local_xmin = (panel['cnx'] - panel['max_ss'] +
                              panel['min_ss'] - 1)
                local_ymax = (panel['cny'] + panel['max_fs'] -
                              panel['min_fs'] + 1)
            elif panel['xss'] < 0 and panel['yfs'] > 0:
                # After rotation along y=-x
                local_xmin = panel['cnx']
                local_ymax = panel['cny']
                local_xmax = (panel['cnx'] + panel['max_ss'] -
                              panel['min_ss'] + 1)
                local_ymin = (panel['cny'] - panel['max_fs'] +
                              panel['min_fs'] - 1)
        elif (np.abs(panel['xfs']) > np.abs(panel['xss']) and
              np.abs(panel['yfs']) < np.abs(panel['yss'])):
            if panel['xfs'] < 0 and panel['yss'] < 0:
                # After rotation along y-axis
                local_xmax = panel['cnx']
                local_ymax = panel['cny']
                local_xmin = (panel['cnx'] - panel['max_fs'] +
                              panel['min_fs'] - 1)
                local_ymin = (panel['cny'] - panel['max_ss'] +
                              panel['min_ss'] - 1)
            elif panel['xfs'] > 0 and panel['yss'] > 0:
                # After rotation along x-axis
                local_xmin = panel['cnx']
                local_ymin = panel['cny']
                local_xmax = (panel['cnx'] + panel['max_fs'] -
                              panel['min_fs'] + 1)
                local_ymax = (panel['cny'] + panel['max_ss'] -
                              panel['min_ss'] + 1)
        return local_xmin, local_xmax, local_ymin, local_ymax

    def find_image_size(self, geom):
        """Finds a matrix size that allows you to hold all the panels.

        Parameters
        ----------
        geom : dict

            Dictionary with the geometry information loaded from the geomfile.

        Returns
        -------
        (columns, rows,  center_x, center_y) : tuple

            columns, rows : Matrix size used in imshow.
            center_x, center_y : Displacement of centre.
        """
        # current length and height.
        x_min = x_max = y_min = y_max = 0
        # I am looking for the most remote panel points.
        for name in geom["panels"]:
            local_xmin, local_xmax, local_ymin, local_ymax = self.local_range(
                geom["panels"][name])
            if local_xmax > x_max:
                x_max = local_xmax
            elif local_xmin < x_min:
                x_min = local_xmin
            if local_ymax > y_max:
                y_max = local_ymax
            elif local_ymin < y_min:
                y_min = local_ymin
        # The number of columns.
        columns = x_max - x_min
        # The number of rows.
        rows = y_max - y_min
        # Displacement of centre.
        center_y = -int(x_max - columns/2)
        center_x = int(y_max - rows/2)
        # conversion to integer.
        rows = int(np.ceil(rows))
        columns = int(np.ceil(columns))
        return columns, rows, center_x, center_y
