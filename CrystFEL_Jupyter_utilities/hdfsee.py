"""Main module for running code.
Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""
import argparse
import logging
import sys

# Module for parsing geometry file.
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
    range : tuple

        min, max value for contrast.
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
        # Following initialized depending on the execution arguments.
        self.path = path
        self.geomfile = geomfile
        self.streamfile = streamfile
        self.event = event
        # Setting the contrast.
        self.range = range
        # Setting the default colormap.
        self.cmap = 'inferno'
        self.matrix = None
        self.image = None
        self.peaks = []
        self.detectors = []
        self.bad_places = None
        # Created a figure and suplot
        # Used 9.5 because default size is to small in notebook
        self.fig, self.ax = self.creat_figure(path=self.path,
                                              figsize=(9.5, 9.5),
                                              event=self.event)
        # Displaying without laying the panels
        if self.geomfile is None:                                                                
            # Raw data from h5 file without peaks data. 
            data = get_file_data(self.path)
            # Numpy.ndarray with panel data
            self.matrix = np.copy(data)
            # Rotating to get the same image as CrystFEL hdfsee.
            self.matrix = self.matrix[::-1, :]
            # Display data as an image; i.e. on a 2D regular raster.
            self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                        vmin=self.range[0],
                                        vmax=(self.range[0]+self.range[1])/2)
        # When the geometry file was provided:
        else:
            try:
                # Load geometry information.
                # Dictionary with information about the image: panels, bad places.
                self.geom = load_crystfel_geometry(self.geomfile)                                             
            except FileNotFoundError:
                LOGGER.critical("Error while opening geometry file.")
                sys.exit(1)
            # Panels reconstruction:
            self.display_arrangement_view()
        # Position ContrastSlider.
        axes = plt.axes([.90, 0.78, 0.09, 0.075], facecolor='lightyellow')
        # Created ContrastSlider widget to change the contrast.
        self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                        ax=axes, label="Contrast",
                                        vmax=self.range[1],
                                        vmin=self.range[0])
        # Position RadioButton.
        axes2 = plt.axes([.90, 0.65, 0.09, 0.12], facecolor='lightyellow')
        # Created Radio widget to change the colormap.
        self.radio = Radio(fig=self.fig, ax=axes2,
                            labels=('inferno', 'plasma', 'Greys'),
                            cmap=self.cmap, image=self.image)
        # Created PeakButtons widget to switching enable / disable the peaks display.
        self.peak_buttons = PeakButtons(fig=self.fig, peaks=self.peaks,
                                        matrix=self.matrix,
                                        radio=self.radio,
                                        slider=self.slider,
                                        ax=self.ax,
                                        streamfile=streamfile,
                                        panels=self.detectors)
        # Display the image:
        plt.show()

    def creat_figure(self, path, figsize=(10, 10), event=None):
        """Creating new figure object, adds subplot.

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
        `peak reflection` from stream file.

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
        """Display panels data as an image; i.e. on a 2D regular raster.
        Creating the image filled with ones (?) and
        applies bad pixel mask (?). Then adds panels (?).
        """
        # matrix size and shifted layout Oxy.
        columns, rows, center_x, center_y = self.find_image_size(self.geom)
        # Created an 'empty' matrix ready to be filled with pixel data.
        self.matrix = np.ones((rows, columns))
        # Created a detector dictionary with keys as panels name and values
        # as class Panel objects.
        self.detectors, self.peaks = get_file_data(
            file=self.path, geom=self.geom, event=self.event,
            image_size=(rows, columns))
        # With stream file.
        if self.streamfile is not None:
            # Add peaks to panels.
            self.add_stream_peaks(self.detectors, self.streamfile, self.event)
        # Arranging the panels.
        self.arrangement_panels(center_x, center_y)
        # Add mask
        if self.event is None:
            # Created a BadRegion numpy.ndarray (mask).
            self.bad_places = bad_places((rows, columns), self.geom,
                                         center_x, center_y)
            # Arranging the BadRegion.
            self.arrangement_bad_places()
        # Display data as an image; i.e. on a 2D regular raster.
        self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                    vmin=self.range[0],
                                    vmax=(self.range[0]+self.range[1])/2)

    def arrangement_bad_places(self):
        """Iterates through each BadRegion and
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
                            detector.array.shape[1]] = (
                                detector.get_array_rotated(center_x, center_y))
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
        # first panel name
        panel_name = list(geom["panels"].keys())[0]
        # current length and height are from first panel.
        x_min, x_max, y_min, y_max = self.local_range(
            geom["panels"][panel_name])
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


def main(argv=None):
    # Creating arguments for parsing.
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs=1, metavar="name.H5",
                        help='Display this image.')
    parser.add_argument('-g', "--geomfile", nargs=1, metavar='name.GEOM',
                        help='Use geometry from file' +
                        ' to display arrangment panels')
    parser.add_argument('-p', '--peaks', nargs=1, metavar='name.STREAM',
                        help='use to display peaks' +
                        ' from stream is used only witch geom')
    parser.add_argument('-e', '--event', nargs=1, metavar='name.EVENT',
                        help='Event to show from multi-event file.')
    # Parsing command line arguments.
    args = parser.parse_args()
    # Variable for filename.
    path = args.filename[0]
    if args.geomfile:
        # Check if the geometry file was provided.
        geomfile = args.geomfile[0]
        if args.peaks:
            streamfile = args.peaks[0]
        else:
            # Only the geometry file was provided.
            streamfile = None
        if args.event:
            event = args.event[0]
        else:
            event = None
    # Image file without geometry.
    else:
        if args.event:
            LOGGER.warning(
                'Can not use without geometry reconstruction.')
        if args.peaks:
            LOGGER.warning(
                'Displaying panels without geometry reconstruction.')
        streamfile = None
        geomfile = None
        event = None

    IMAGE = Image(path=path, geomfile=geomfile,
                  streamfile=streamfile, event=event)


if __name__ == '__main__':
    main()
