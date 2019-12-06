"""Main module for running code.

Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""

# Module for parsing command line arguments had to be moved here to
# avoid displaying the same image all over again in jupyter notebook.
import argparse
import logging
import re
import sys
# Module for parsing geometry file and determining size of the
# image after panel arrangement.
from cfelpyutils import crystfel_utils, geometry_utils
import matplotlib.pyplot as plt
import numpy as np

import data
from panel import Detector, bad_places
from stream_read import search_peaks
from widget import ContrastSlider, PeakButtons, Radio


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
    @staticmethod
    def argparsing():
        """Creating arguments for parsing and parsing command line arguments.
        """
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
        # Parsing command line arguments.
        args = parser.parse_args()
        # Variable for running mode.
        Image.which_argument_is_used = {'display_only_file': False,
                                        'display_arrangment_view': False,
                                        'dispaly_with_peaks': False}
        # Variable for filename.
        Image.file_h5_name = args.filename[0]
        if args.geomfile:
            # Check if the geometry file was provided.
            Image.file_geom_name = args.geomfile[0]
            if args.peaks:
                Image.file_stream_name = args.peaks[0]
                Image.which_argument_is_used['dispaly_with_peaks'] = True
                Image.which_argument_is_used['display_arrangment_view'] = False
            else:
                # Only the geometry file was provided.
                Image.file_stream_name = None
                Image.which_argument_is_used['display_arrangment_view'] = True
        # Image file without geometry.
        else:
            if args.peaks:
                LOGGER.warning(
                    'Displaying panels without geometry reconstruction.')
            Image.file_stream_name = None
            Image.file_geom_name = None
            Image.which_argument_is_used['display_only_file'] = True

        try:
            Image.geom = crystfel_utils.load_crystfel_geometry(
                Image.file_geom_name)
            # Dictionary with information about the image: panels, bad places.
        except FileNotFoundError:
            LOGGER.critical("Error while opening geometry file.")
            sys.exit(1)
        except TypeError:
            # No geometry file was provided.
            Image.geom = None

    def __init__(self):
        """Method for initializing image and checking options how to run code.
        """
        # method for parsing command line arguments had to be moved here to.
        # avoid displaying the same image all over again in jupyter notebook.
        Image.argparsing()

        # Dictionary containing panels and peaks info from the h5 file.
        self.dict_witch_data = data.get_diction_data(Image.file_h5_name)

        # Creating a figure of the right size. (why 10x10?)
        # used 10X10 because default size is to small in notebook
        self.fig, self.ax = self.__creat_figure(path=Image.file_h5_name,
                                                figsize=(10, 10))

        # Setting the contrast.
        self.vmax = 600
        self.vmin = 0
        # Setting the default colour map.
        self.cmap = 'inferno'
        # Following initialized depending on the execution arguments.
        self.matrix = None
        self.image = None
        self.peaks = None
        self.detectors = None
        self.bad_places = None

        # For displaying the image in the right orientation (?).
        # dispaly without laying the panels
        if Image.which_argument_is_used['display_only_file']:
            # Just the image from file with no buttons or reconstruction.
            self.matrix = np.copy(self.dict_witch_data["Panels"])
            # Rotating to get the same image as CrystFEL hdfsee.
            self.matrix = self.matrix[::-1, :]
            # Creating the image with imshow().
            self.image = self.ax.imshow(self.matrix, cmap=self.cmap,
                                        vmax=self.vmax, vmin=self.vmin)
            # Slider position.
            axes = plt.axes([.90, 0.75, 0.09, 0.075], facecolor='lightyellow')
            self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                         ax=axes, label="Contrast",
                                         vmin=self.vmin, vmax=self.vmax)
            # Radio (?) position.
            # Position RadioButton
            axes2 = plt.axes([.90, 0.65, 0.09, 0.12], facecolor='lightyellow')
            # created button radio
            self.radio = Radio(fig=self.fig, ax=axes2,
                               labels=('inferno', 'plasma', 'Greys'),
                               cmap=self.cmap, image=self.image)
        # When the geometry file was provided:
        else:
            # Panels reconstruction:
            self.display_arrangment_view()
            # Slider position.
            axes = plt.axes([.90, 0.75, 0.09, 0.075], facecolor='lightyellow')
            self.slider = ContrastSlider(image=self.image, fig=self.fig,
                                         ax=axes, label="Contrast",
                                         vmin=self.vmin, vmax=self.vmax)
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
            if Image.which_argument_is_used['dispaly_with_peaks']:
                # Additional buttons for switching on/off
                # peaks from stream file.
                self.peak_buttons =\
                    PeakButtons(fig=self.fig, peaks=self.peaks,
                                number_peaks_button=3,
                                matrix=self.matrix, title=self.ax.get_title(),
                                radio=self.radio, slider=self.slider,
                                ax=self.ax, panels=self.detectors)
            else:
                # Only one button for showing peaks from h5 file.
                self.peak_buttons =\
                    PeakButtons(fig=self.fig, peaks=self.peaks,
                                number_peaks_button=1,
                                matrix=self.matrix, title=self.ax.get_title(),
                                radio=self.radio, slider=self.slider,
                                ax=self.ax, panels=self.detectors)

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

    def __panels_create(self, geom, image_size, event=None):
        """Creates a dictionary of panels with panels objects as items
    and panel names as in the geometry file as keys.

        Parameters
        ----------
        geom : dict

            Dictionary with the geometry information loaded from the geomfile.
        image_size : touple

            numpy.array shape storing the minimum array size used in image.
        event : Python unicode str (on py3)

            Event to show from multi-event file.

        Returns
        -------
        panels : Dict

        Dictionary with panels object.
        """
        panels = {}

        for name in geom['panels']:
            if event is None:
                panel_data = self.dict_witch_data["Panels"]
            else:
                idx = int(re.findall('\d+', name)[0])
                panel_data = self.dict_witch_data["Panels"][idx]

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

    def add_stream_peaks(self, panels, streamfile, event=None):
        """Search for peaks `peak search` and `peak reflection` from streamfile.

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
            line_name = Image.file_h5_name.strip().split('/')[-1]
            peaks_search, peaks_reflection =\
                search_peaks(streamfile, line_name, 'Image filename:')
            print(len(peaks_search), len(peaks_reflection))
        else:
            peaks_search, peaks_reflection = \
                search_peaks(streamfile, event, 'Event')
        # add peaks to each panel,not everyone can have them.
        for name in panels:
            # peaks_search doesn't have the key panel.name
            try:
                panels[name].peaks_search = peaks_search[name]
            except:
                pass
            # peaks_reflection doesn't have the key panel.name
            try:
                panels[name].peaks_reflection = peaks_reflection[name]
            except:
                pass

    def cheetah_peaks_list(self, peaks_data, image_size):
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
        try:
            peaks = []
            # peaks_data[:,] next rows
            for row in peaks_data[:, ]:
                posx = row[0] + image_size[1]/2.0
                posy = -row[1] + image_size[0]/2.0
                peak = {"posx": posx, "posy": posy, "position": (posx, posy)}
                peaks.append(peak)
            return peaks
        except IndexError:
            LOGGER.warning("Problem with peaks from the h5 file.")

    def display_arrangment_view(self):
        """Creating the image filled with ones (?) and applies bad pixel mask (?).
        Then adds panels (?).
        """
        columns, rows, center_x, center_y = self.find_image_size(Image.geom)
        # Creating an 'empty' matrix ready to be filled with pixel data.
        self.matrix = np.ones((columns, rows))
        # Creates a detector dictionary with keys as panels name and values
        # as class Panel objects.

        self.detectors = self.__panels_create(geom=Image.geom,
                                              image_size=(columns, rows))
        if Image.which_argument_is_used['dispaly_with_peaks']:
            self.add_stream_peaks(self.detectors, Image.file_stream_name)
        # Creating a peak list from the h5 file.
        self.peaks = self.cheetah_peaks_list(self.dict_witch_data["Peaks"],
                                             (columns, rows))
        # Creating a bad pixel mask (?).
        self.bad_places = bad_places((columns, rows), Image.geom)
        # Arranging the panels.
        self.arrangement_panels(center_x, center_y)
        # Masking the bad pixels (?).
        self.arrangment_bad_places()
        # Displaying the image.
        self.image = plt.imshow(self.matrix, cmap=self.cmap, vmax=self.vmax,
                                vmin=self.vmin, animated=True)

    def arrangment_bad_places(self):
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
                self.matrix[bad_place.max_y: bad_place.max_y + bad_place.shape[0],
                            bad_place.min_x: bad_place.min_x +
                            bad_place.array.shape[1]] = bad_place.get_array()
            except ValueError:
                LOGGER.critical("Wrong mask position: {}".format(bad_place.name))
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
                local_xmin = \
                    panel['cnx'] - panel['max_ss'] + panel['min_ss'] - 1
                local_ymax = \
                    panel['cny'] + panel['max_fs'] - panel['min_fs'] + 1

            elif panel['xss'] < 0 and panel['yfs'] > 0:

                # After rotation along y=-x
                local_xmin = panel['cnx']
                local_ymax = panel['cny']
                local_xmax = \
                    panel['cnx'] + panel['max_ss'] - panel['min_ss'] + 1
                local_ymin = \
                    panel['cny'] - panel['max_fs'] + panel['min_fs'] - 1
        elif np.abs(panel['xfs']) > np.abs(panel['xss']) and \
                np.abs(panel['yfs']) < np.abs(panel['yss']):
            if panel['xfs'] < 0 and panel['yss'] < 0:

                # After rotation along y-axis
                local_xmax = panel['cnx']
                local_ymax = panel['cny']
                local_xmin = \
                    panel['cnx'] - panel['max_fs'] + panel['min_fs'] - 1
                local_ymin = \
                    panel['cny'] - panel['max_ss'] + panel['min_ss'] - 1

            elif panel['xfs'] > 0 and panel['yss'] > 0:

                # After rotation along x-axis
                local_xmin = panel['cnx']
                local_ymin = panel['cny']
                local_xmax = \
                    panel['cnx'] + panel['max_fs'] - panel['min_fs'] + 1
                local_ymax = \
                    panel['cny'] + panel['max_ss'] - panel['min_ss'] + 1

        return (local_xmin, local_xmax, local_ymin, local_ymax)

    def find_image_size(self, geom):
        """Finds a matrix size that allows you to hold all the panels.

        Parameters
        ----------
        geom : dict

            Dictionary with the geometry information loaded from the geomfile.

        Returns
        -------
        (kolumns, rows,  center_x, center_y) : tuple

            kolumns, rows : Matrix size used in imshow.
            center_x, center_y : Displacement of centre.
        """
        # current lenght and height.
        x_min = x_max = y_min = y_max = 0

        # I am looking for the most remote panel points.
        for name in geom["panels"]:
            local_xmin, local_xmax, local_ymin, local_ymax = \
                self.local_range(geom["panels"][name])
            if local_xmax > x_max:
                x_max = local_xmax
            elif local_xmin < x_min:
                x_min = local_xmin
            if local_ymax > y_max:
                y_max = local_ymax
            elif local_ymin < y_min:
                y_min = local_ymin

        # The number of columns.
        kolumns = x_max - x_min
        # The number of rows.
        rows = y_max - y_min

        # Displacement of centre.
        center_y = -int(x_max-kolumns/2)
        center_x = int(y_max-rows/2)
        # conversion to integer.
        rows = int(np.ceil(rows))
        kolumns = int(np.ceil(kolumns))

        return(kolumns, rows, center_x, center_y)
