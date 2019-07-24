"""Main module for running code.

Creates image from a ndarray, arranges the panels,
refreshes (updates) the image and adds widgets.
"""

# Module for parsing command line arguments had to be moved here to
# avoid displaying the same image all over again in jupyter notebook.
import argparse
import matplotlib.pyplot as plt
import numpy as np
import sys
# Module for parsing geometry file and determining size of the
# image after panel arrangement.
import cfelpyutils.crystfel_utils as c
import cfelpyutils.geometry_utils as g

import data
import panel
import peak_h5
from stream_read import search_peaks
from widget import ContrastSlider, PeakButton, Radio


# Creating arguments for parsing.

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
    axis_list : list

        List of matplotlib.pyplot.axes objects for locations of the
        buttons.
    list_active_peak : list

        Flags list showing which type of peaks were selected.
    """
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('filename', nargs=1, metavar="name.H5",
                        help='Display this image.')
    PARSER.add_argument('-g', "--geomfile", nargs=1, metavar='name.GEOM',
                        help='Use geometry from file' +
                        ' to display arrnagmrnt panels')
    PARSER.add_argument('-p', '--peaks', nargs=1, metavar='name.STREAM',
                        help='use to display peaks' +
                        ' from stream is used only witch geom')
    # Parsing command line arguments.
    ARGS = PARSER.parse_args()
    # Variable for running mode.
    WHICH_ARGUMNENT_IS_USED = {'display_only_file': False,
                               'display_arrangment_view': False,
                               'dispaly_with_peaks': False}
    # Variable for filename.
    FILE_H5_NAME = ARGS.filename[0]
    if ARGS.geomfile:
        # Check if the geometry file was provided.
        FILE_GEOM_NAME = ARGS.geomfile[0]
        if ARGS.peaks:
            FILE_STREAM_NAME = ARGS.peaks[0]
            WHICH_ARGUMNENT_IS_USED['dispaly_with_peaks'] = True
            WHICH_ARGUMNENT_IS_USED['display_arrangment_view'] = False
        else:
            # Only the geometry file was provided.
            FILE_STREAM_NAME = None
            WHICH_ARGUMNENT_IS_USED['display_arrangment_view'] = True
    # Image file without geometry.
    else:
        if ARGS.peaks:
            print('Displaying panels without geometry reconstruction.')
        FILE_STREAM_NAME = None
        FILE_GEOM_NAME = None
        WHICH_ARGUMNENT_IS_USED['display_only_file'] = True

    try:
        GEOM = c.load_crystfel_geometry(FILE_GEOM_NAME)
        # Dictionary with information about the image: panels, bad places.
        # Tuple for the minimal images size.
        IMAGE_SIZE = g.compute_min_array_size(g.compute_pix_maps(GEOM))
    except FileNotFoundError:
        print("Error while opening geometry file.")
        sys.exit()
    except TypeError:
        # No geometry file was provided.
        IMAGE_SIZE = None

    def __init__(self):
        """Method for initializing image and checking options how to run code.
        """
        # Dictionary containing panels and peaks info from the h5 file.
        self.dict_witch_data = data.get_diction_data(Image.FILE_H5_NAME)

        # Creating a figure of the right size. (why 10x10?)
        # used 10X10 because default size is to small in notebook
        self.fig = plt.figure(figsize=(10, 10))
        # Adding subplot (?).
        # fiugre doesn't has a subplot and we add one
        self.ax = self.fig.add_subplot(111)
        # Setting the title to filename path.
        self.ax.set_title(Image.FILE_H5_NAME)
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
        self.axis_list = [False, False, False]
        self.list_active_peak = [False, False, False]

        # For displaying the image in the right orientation (?).
        # dispaly without laying the panels
        if Image.WHICH_ARGUMNENT_IS_USED['display_only_file']:
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
            self.axis_list[0] = plt.axes([.90, 0.55, 0.09, 0.08],
                                         facecolor='yellow')
            # Only one button for showing peaks from h5 file.
            self.peakbtn =\
                PeakButton(fig=self.fig, peaks=self.peaks, matrix=self.matrix,
                           title=Image.FILE_H5_NAME, axis_list=self.axis_list,
                           radio=self.radio, slider=self.slider,
                           list_active_peak=self.list_active_peak,
                           axs=self.ax, detectors=self.detectors,
                           ax=self.axis_list[0], label='cheetah peaks on/off')
            # For displaying peaks from stream file.
            if Image.WHICH_ARGUMNENT_IS_USED['dispaly_with_peaks']:
                # Additional buttons for switching on/off
                # peaks from stream file.
                self.axis_list[1] = plt.axes([.90, 0.45, 0.09, 0.08],
                                             facecolor='yellow')
                # Button for peaks from stream (?).
                # we can show peaks as shown near_bragg
                # they are under line 'Reflections measured after indexing'
                # we can show peaks as shown check_peak_detection
                # they are under line 'Peaks from peak search'
                self.peakbtn2 =\
                    PeakButton(fig=self.fig, peaks=self.peaks,
                               matrix=self.matrix, title=Image.FILE_H5_NAME,
                               axis_list=self.axis_list, radio=self.radio,
                               slider=self.slider,
                               list_active_peak=self.list_active_peak,
                               axs=self.ax, detectors=self.detectors,
                               ax=self.axis_list[1],
                               label='CrystFEL_peak on/off')

                self.axis_list[2] = plt.axes([.90, 0.35, 0.09, 0.08],
                                             facecolor='yellow')
                self.peakbtn3 =\
                    PeakButton(fig=self.fig, peaks=self.peaks,
                               matrix=self.matrix, title=Image.FILE_H5_NAME,
                               axis_list=self.axis_list, radio=self.radio,
                               slider=self.slider,
                               list_active_peak=self.list_active_peak,
                               axs=self.ax, detectors=self.detectors,
                               ax=self.axis_list[2],
                               label='CrystFEL_near_bragg_peak on/off')
        # Display the image:
        plt.show()

    def display_arrangment_view(self):
        """Creating the image filled with ones (?) and applies bad pixel mask (?).
        Then adds panels (?).
        """
        # Creating an 'empty' matrix ready to be filled with pixel data.
        self.matrix = np.ones(Image.IMAGE_SIZE)
        # Creates a detector dictionary with keys as panels name and values
        # as class Panel objects.
        peaks_search, peaks_reflections =\
            search_peaks(Image.FILE_STREAM_NAME,
                         Image.FILE_H5_NAME)
        self.detectors =\
            panel.get_detectors(self.dict_witch_data["Panels"],
                                Image.IMAGE_SIZE, Image.GEOM, peaks_search,
                                peaks_reflections)
        # Creating a peak list from the h5 file.
        self.peaks = peak_h5.get_list_peaks(self.dict_witch_data["Peaks"],
                                            Image.IMAGE_SIZE)
        # Creating a bad pixel mask (?).
        self.bad_places = panel.bad_places(Image.IMAGE_SIZE,
                                           Image.GEOM)
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
            print("Wrong panel position: ", end="")
            print(detector.name, end="Position:  ")
            print(detector.position)

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
            print("Wrong position: ", end="")
            print(bad_place.name, bad_place.printer())

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


IMAGE = Image()
