"""Main module for running code.

Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""

# Module for parsing command line arguments had to be moved here to
# avoid displaying the same image all over again in jupyter notebook.
import argparse
import logging
import sys
# Module for parsing geometry file and determining size of the
# image after panel arrangement.
from cfelpyutils import crystfel_utils, geometry_utils
import matplotlib.pyplot as plt
import numpy as np

import data
import panel
import peak_h5
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
            # Tuple for the minimal images size.
            Image.image_size = geometry_utils.compute_min_array_size(
                geometry_utils.compute_pix_maps(Image.geom))
        except FileNotFoundError:
            LOGGER.critical("Error while opening geometry file.")
            sys.exit(1)
        except TypeError:
            # No geometry file was provided.
            Image.image_size = None

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
        self.fig = plt.figure(figsize=(10, 10))
        # Adding subplot (?).
        # fiugre doesn't has a subplot and we add one
        self.ax = self.fig.add_subplot(111)
        # Setting the title to filename path.
        self.ax.set_title(Image.file_h5_name)
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
                                         ax=axes, label="Kontrast",
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
                                         ax=axes, label="Kontrast",
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

    def display_arrangment_view(self):
        """Creating the image filled with ones (?) and applies bad pixel mask (?).
        Then adds panels (?).
        """
        # Creating an 'empty' matrix ready to be filled with pixel data.
        self.matrix = np.ones(Image.image_size)
        # Creates a detector dictionary with keys as panels name and values
        # as class Panel objects.
        peaks_search, peaks_reflections =\
            search_peaks(Image.file_stream_name,
                         Image.file_h5_name)
        self.detectors =\
            panel.get_detectors(self.dict_witch_data["Panels"],
                                Image.image_size, Image.geom, peaks_search,
                                peaks_reflections)
        # Creating a peak list from the h5 file.
        self.peaks = peak_h5.get_list_peaks(self.dict_witch_data["Peaks"],
                                            Image.image_size)
        # Creating a bad pixel mask (?).
        self.bad_places = panel.bad_places(Image.image_size,
                                           Image.geom)
        # Arranging the panels.
        self.arrangement_panels()
        # Masking the bad pixels (?).
        self.arrangment_bad_places()
        # Displaying the image.
        self.image = plt.imshow(self.matrix, cmap=self.cmap, vmax=self.vmax,
                                vmin=self.vmin, animated=True)

    def set_panel_in_view(self, detector):
        """Positions (?) the detector in the right place on the matrix.
        Changes the 1 values to the correct pixel value.

        Parameters
        ----------
        detector : The: class Detectror object

            Detector which has been set in the image.

        Raises
        ------
        ValueError
            If wrong panel position.
        """
        # Trying to reposition the panels.
        try:
            self.matrix[detector.position[0]: detector.position[0] +
                        detector.array.shape[0],
                        detector.position[1]: detector.position[1] +
                        detector.array.shape[1]] = detector.get_array_rotated()
        except ValueError:
            text = " ".join(["Wrong panel position",
                             "{}, Position: {}".format(detector.name,
                                                       detector.position)])
            LOGGER.critical(text)
            sys.exit(1)

    def set_bad_place_in_view(self, bad_place):
        """Copying the bad pixel ranges to the image.

        Parameters
        ----------
        bad_place : The: class BadRegion object

            BadRegion which has been set in the image.

        Raises
        ------
        ValueError
            If wrong bad_place position.
        """
        try:
            self.matrix[bad_place.max_y: bad_place.max_y + bad_place.shape[0],
                        bad_place.min_x: bad_place.min_x +
                        bad_place.array.shape[1]] = bad_place.get_array()
        except ValueError:
            LOGGER.critical("Wrong mask position: {}".format(bad_place.name))
            sys.exit(1)

    def arrangment_bad_places(self):
        """Iterates through each bad pixel (?) region and positions it to the
        correct place on the image.
        """
        for name_bad_place in self.bad_places:
            bad_place = self.bad_places[name_bad_place]
            self.set_bad_place_in_view(bad_place)

    def arrangement_panels(self):
        """Iterates through each detector (?) and positions them.
        """
        for key in self.detectors:
            detector = self.detectors[key]
            self.set_panel_in_view(detector)
