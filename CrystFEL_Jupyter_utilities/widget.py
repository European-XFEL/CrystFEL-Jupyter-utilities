"""Module for centering switches and handling mouse events.
"""
import logging
import itertools

from matplotlib.widgets import Button, RadioButtons, SpanSelector, Slider
import matplotlib.pyplot as plt

from .crystlib import histograms_data

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


class PeakButtons:
    """A GUI buttons used to visible others peaks in image

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    ax : The class:`matplotlib.axes.Axes`

        The Axes contains most of the figure elements.
    axis_list : list

        Position button in figure (object matplotlib.pyplot.axis).
    list_active_peak : list

        Flags with peaks are enabled/disabled.
    panels : dict

        Object class Panel with peaks.
    peaks -  list

        Objects Peak (form h5 file).
    title : Python unicode str (on py3)

        Title image.
    radio : object form widget/Radio

    slider : objet form widget/My_slider

    matrix : numpy.array object

        Data with pixels.
    number_peaks_button : int

        Number of buttons.
        1- Only button for peaks from hdf5.
        2- Only two buttons for peaks from stream.
        3- three buttons for all peaks.
    """

    def __init__(self, fig, ax, matrix, peaks, number_peaks_button, panels,
                 title, radio, slider):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`.

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            The Axes contains most of the figure elements.
        matrix : numpy.array object

            Data with pixels.
        panels : dict

            Objects class Detector with peaks.
        peaks -  list

            Objects class Peak form h5 file.
        number_peaks_button : int

            Number of buttons.
        title : Python unicode str (on py3)

            Title image.
        radio : object form widget/Radio

        slider : object form widget/ContrastSlider
        """
        self.fig = fig
        self.ax = ax
        self.matrix = matrix
        self.axis_list = [None, None, None]
        self.list_active_peak = [False, False, False]
        self.peaks = peaks
        self.panels = panels
        self.title = title
        self.radio = radio
        self.slider = slider
        self.buttons = []
        if number_peaks_button != 2:
            self.axis_list[0] = plt.axes([.90, 0.55, 0.09, 0.08],
                                         facecolor='yellow')
            button = Button(ax=self.axis_list[0],
                            label='peaks_cheetah on/off')
            button.on_clicked(self.peaks_on_of)
            self.buttons.append(button)
            # On click reaction.
        if number_peaks_button != 1:
            self.axis_list[1] = (plt.axes([.90, 0.45, 0.09, 0.08],
                                          facecolor='yellow'))
            # Create button object.
            button = Button(ax=self.axis_list[1],
                            label='peaks_search   on/off')
            # On click reaction.
            button.on_clicked(self.peaks_on_of)
            # Add to list of buttons.
            self.buttons.append(button)
            self.axis_list[2] = (plt.axes([.90, 0.35, 0.09, 0.08],
                                          facecolor='yellow'))
            button = Button(ax=self.axis_list[2],
                            label='peaks_reflections on/off')
            # On click reaction.
            button.on_clicked(self.peaks_on_of)
            # Add to list of buttons.
            self.buttons.append(button)
        for button in self.buttons:
            button.label.set_fontsize(8)
            button.label.set_wrap(True)
            button.label.set_fontstretch(200)
            button.label.set_linespacing(2)

    def visual_peaks_reflection(self):
        """Draw peaks from line `reflections measured after indexing`
        from stream file. Like as script near_bragg.
        """
        # set flag peaks_near_bragg are enabled
        self.list_active_peak[2] = True
        # loop through all panels
        for name in self.panels:
            # loop through all peaks near_bragg
            for peak in self.panels[name].get_peaks_reflection():
                circle = plt.Circle(peak['position'], radius=5,
                                    color='r', fill=False)
                # draw red circle
                self.ax.add_artist(circle)

    def visual_peaks_search(self):
        """Draw peaks from `peaks search` from stream file.
        Like check_peak_detection script.
        """
        # set flag peaks_list are enabled
        self.list_active_peak[1] = True
        # loop through all panels
        for name in self.panels:
            # loop through all peaks list
            for peak in self.panels[name].get_peaks_search():
                circle = plt.Circle(peak['position'], radius=5,
                                    color='g', fill=False)
                # draw red circle
                self.ax.add_artist(circle)

    def visual_peaks(self):
        """Draw peaks form dataset in h5 file 'cheetah peakinfo-assembled'.
        """
        try:
            # loop through all peaks list
            for peak in self.peaks:
                circle = plt.Circle(peak.get_position(), radius=5,
                                    color='y', fill=False)
                # draw yellow circle
                self.ax.add_artist(circle)
        except TypeError:
            # exception when we can find peak in dataset
            return None

    def peaks_on_of(self, event):
        """React at the click of buttons.
        Clear and create clean image. Checks which flags were active
        and changes the flags due to the button being clicked.

        Parameters
        ----------
        event : The class:`matplotlib.backend_bases.Event`.
        """
        # clear subplot
        self.ax.cla()
        # returned color map last used
        cmap = self.radio.get_cmap()
        # returned contrast range last used
        vmax = self.slider.get_vmax()
        vmin = self.slider.get_vmin()
        # created new image we have a new reference
        image = self.ax.imshow(self.matrix, cmap=cmap, vmax=vmax,
                               vmin=vmin, animated=True)
        # when we clicked button 'cheetah peaks on/off'
        if event.inaxes == self.axis_list[0]:
            # 'cheetah peaks on/off' was enabled
            if self.list_active_peak[0]:
                # then is disabled. We change flags and don't draw
                self.list_active_peak[0] = False
            # when we want enabled
            else:
                # We change flags and draw
                self.list_active_peak[0] = True
                self.visual_peaks()
            # other was enabled and draw or disabled and don't draw
            if self.list_active_peak[1]:
                # 'CrystFEL_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_search()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_reflection()
        # when we clicked button 'CrystFEL_peak on/off'
        if event.inaxes == self.axis_list[1]:
            if self.list_active_peak[0]:
                # 'cheetah peaks on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_reflection()
            if self.list_active_peak[1]:
                # 'CrystFEL_peak on/off' was enabled and change flags
                # we don't draw
                self.list_active_peak[1] = False
            else:
                # 'CrystFEL_peak on/off' was disabled and change flags
                # we draw
                self.list_active_peak[1] = True
                self.visual_peaks_search()
        # when we clicked button 'CrystFEL_near_bragg_peak on/off'
        if event.inaxes == self.axis_list[2]:
            if self.list_active_peak[0]:
                # 'cheetah peaks on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks()
            if self.list_active_peak[1]:
                # 'CrystFEL_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_search()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off'
                # and change flags was enabled
                # we don't draw
                self.list_active_peak[2] = False
            else:
                # 'CrystFEL_near_bragg_peak on/off' was disabled
                # and change flags
                # we don't draw
                self.list_active_peak[2] = True
                self.visual_peaks_reflection()
        # Redraw the current figure.
        self.fig.canvas.draw()
        # set title because we clear subplot axs
        self.ax.set_title(self.title)
        # set a new reference in the widgets
        self.radio.set_image(image)
        self.slider.set_image(image)


class ButtonBins(Button):
    """A GUI button to change the number of bins in all histograms

    Attributes
    ----------
    fig : The :class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    histogram_list : list

        Contains objects the class:`histogram.Histogram`.
    label : The :class:`matplotlib.text.Text` instance.
    """
    __bins = None
    # variable used by all objects in this class
    # initialized by set_bins

    def __init__(self, fig, histogram_list, ax, label):
        """
        Parameters
        ----------
        fig : The :class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The :class:`matplotlib.axes.Axes`

            Instance the button will be placed into.
        histogram_list : list

            Contains objects the class:`histogram.Histogram`
        label : The :class:`matplotlib.text.Text` instance.
        """
        # Initialize parent constructor.
        super(ButtonBins, self).__init__(ax=ax, label=label)
        self.fig = fig  # For calling canvas draw which refreshes the image.
        self.histogram_list = histogram_list  # List with all histograms
        self.label = label
        super(ButtonBins, self).on_clicked(self.change_bins)  # Click reaction

    @staticmethod
    def set_bins(bins):
        """Set the value of bins for all histograms

        Parameters
        ----------
        bins : int

            New value of bins.
        """
        ButtonBins.__bins = bins

    def change_bins(self, event):
        """When the ButtonBins is clicked, call this func with event

        Parameters
        ----------
        event : The class:`matplotlib.backend_bases.Event`.
        """
        # Changing number of bins; Number is a power of 2. Max val. 512.
        if self.label == '+':
            if ButtonBins.__bins < 512:
                ButtonBins.__bins *= 2
                for his in self.histogram_list:
                    his.bins = ButtonBins.__bins
                    his.update()
                    his.draw_green_space()
        elif self.label == '-':
            if ButtonBins.__bins > 2:
                ButtonBins.__bins /= 2
                for his in self.histogram_list:
                    his.bins = ButtonBins.__bins
                    his.update()
                    his.draw_green_space()
        self.fig.canvas.draw()


class Radio(RadioButtons):
    """A GUI radio button used in hdfsee.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
    cmap : The class:`matplotlib.colors.Colormap`

        Used to change color map in image.
    """

    def __init__(self, fig, ax, labels, cmap, image):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            Instance the button will be placed into.
        labels : tuple of The :class:`matplotlib.text.Text` instance.
        cmap : The class:`matplotlib.colors.Colormap`

            Used to change color map in image.
        image : The class:`matplotlib.image.AxesImage`

            Created by functions imshow().
        """
        self.image = image
        self.fig = fig
        self.cmap = cmap
        # Initialize parent constructor.
        super(Radio, self).__init__(ax=ax, labels=labels, active=0)
        # On click reaction.
        self.on_clicked(self.colorfunc)

    def colorfunc(self, label):
        """When the button is clicked, call this func with button label
        Updates the image.
        """
        # change name cmap
        self.cmap = label
        # set cmap
        self.image.set_cmap(cmap=self.cmap)
        # Redraw the current figure.
        self.fig.canvas.draw()

    def set_image(self, image):
        """Set a new image.

        Parameters
        ----------
        image : The class:`matplotlib.image.AxesImage`

            Created by functions imshow().
        """
        self.image = image

    def get_cmap(self):
        """Returns last cmap.
        """
        return self.cmap


class ContrastSlider(Slider):
    """A GUI slider used in hdfsee to change the contrast.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    image : The class:`matplotlib.image.AxesImage`

            Created by functions imshow().
    vmax : int

        Define the data range that the colormap covers.
    vmin : int

        Define the data range that the colormap covers.
    """

    def __init__(self, image, fig, ax, label, vmin, vmax):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            Instance the button will be placed into.
        label : The :class:`matplotlib.text.Text` instance.
        vmax : int

            Define the data range that the colormap covers.
        vmin : int

            Define the data range that the colormap covers.
        image : The class:`matplotlib.image.AxesImage`

            Created by functions imshow().
        """
        self.image = image
        self.fig = fig
        self.vmax = vmax
        self.vmin = vmin
        # Initialize parent constructor.
        super(ContrastSlider, self).__init__(ax, label, self.vmin, self.vmax,
                                             valinit=(self.vmin + self.vmax)/2)
        # On click reaction.
        super(ContrastSlider, self).on_changed(self.on_check)
        # Set position `Contrast` label
        # get positoin x Slider.
        pos_x = self.ax.get_position().get_points()[0][0]
        # get position y Slider.
        pos_y = self.ax.get_position().get_points()[1][0]
        # set label position.
        self.label.set_position((pos_x, pos_y + 0.1))
        # Disabled value text.
        self.valtext.set_visible(False)

    def on_check(self, event):
        """When the button is clicked, call this func with event
        Updates the image contrast.

        Parameters
        ----------
        event : The class:`matplotlib.backend_bases.Event`.
        """
        self.vmax = event
        self.image.set_clim(vmax=self.vmax)
        self.fig.canvas.draw()

    def set_image(self, image):
        """set a new image

        Parameters
        ----------
        image : The class:`matplotlib.image.AxesImage`

            Created by functions imshow().
        """
        self.image = image

    def get_vmax(self):
        """Returns last vmax.

        Returns
        -------
        vmax : int

            Max range that the colormap covers.
        """
        return self.vmax

    def get_vmin(self):
        """Returns  last vmin.

        Returns
        -------
        vmin : int

            Min range that the colormap covers.
        """
        return self.vmin


class CenteringButton(Button):
    """A GUI button for changing
    the color of the histogram bar for proper centering.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    colors : itertools.cycle list

        Contains a list of colors.
    histogram_list : list

        Contains objects the class:`histogram.Histogram`.
    list_color : list

        Colors of changing the bars in the histogram.
    histogram_list : list

        Contains objects the class:`histogram.Histogram`.
    histogram_colors : dict

        key - type centering, value - list with colors.
    """

    def __init__(self, fig, axs, label, list_color,
                 histogram_list, histogram_colors):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        axs : The class:`matplotlib.axes.Axes`

            Instance the button will be placed into.
        label : The :class:`matplotlib.text.Text` instance.
        list_color : list

            Colors of changing the bars in the histogram.
        histogram_list : list

            Contains objects the class:`histogram.Histogram`.
        histogram_colors : dict

            key - type centering, value - list with colors.
        """
        # Initialize parent constructor.
        super(CenteringButton, self).__init__(ax=axs, label=label,
                                              color=list_color[0])
        self.fig = fig  # For calling canvas draw which refreshes the image.
        # Loop for the colour list of a given button.
        self.colors = itertools.cycle(list_color)
        # Click reaction
        super(CenteringButton, self).on_clicked(self.on_check)
        self.histogram_list = histogram_list  # List with all histograms
        self.histogram_colors = histogram_colors
        self.list_color = list_color

    def on_check(self, label):
        """Change colour of the histogram depending
        on which switch has been clicked.

        Parameters
        ----------
        label : The :class:`matplotlib.text.Text` instance.
        """
        self.color = next(self.colors)  # After clicking changes the colour
        # to the next in a loop. For a given button the colour will be set in
        # the histogram.
        # change name color in diction for key PABCFHIR is label button
        self.histogram_colors[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.list_colors = self.histogram_colors  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_colors()
        self.fig.canvas.draw()  # Redraw the current figure.

    def reset_color(self):
        """Restore the initial settings.
        """
        self.colors = itertools.cycle(self.list_color)
        self.color = self.list_color[0]
        self.histogram_colors[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.list_colors = self.histogram_colors  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_colors()


class Span:
    """Visually select the region of interest on a single histogram.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw.
    crystals_excluded : list

        Crystals excluded.
    all_crystals_list : list

        All crystals.
    histogram_list : list

        Contains objects the class:`histogram.Histogram`.
    index : int

        Index number in the histogram_list.
    name : str

        Name of the histogram.
    """
    # list of flags for showing what was selected last, where.
    __which_was_used_last = [False, False, False, False, False, False]
    __crystals_included = []
    # crystals in green space

    def __init__(self, fig, crystals_excluded,
                 all_crystals_list, histogram_list, name, index):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`.

            The Figure which will be redraw.
        crystals_excluded : list

            Crystals excluded.
        all_crystals_list : list

            All crystals.
        histogram_list : list

            Contains objects the class:`histogram.Histogram`.
        name : str

            Name of the histogram.
        index : int

            Index number in the histogram_list.
        """
        self.fig = fig
        # Excluded crystals.
        self.crystals_excluded = crystals_excluded
        # all crystals found in stream file
        self.all_crystals_list = all_crystals_list
        self.index = index  # Which histogram is used.
        self.name = name  # Histogram name.
        self.histogram_list = histogram_list  # List with all histograms. Works
        # as a active surface for selecting.
        self.span = SpanSelector(self.histogram_list[index].axs, self.onselect,
                                 'horizontal', useblit=True,
                                 rectprops=dict(alpha=0.5, facecolor='red'))

    @staticmethod
    def set_all_false():
        """List of flags to show what was selected were set to false.
        """
        Span.__which_was_used_last = [False, False, False, False, False, False]

    @staticmethod
    def get_all_used():
        """Get a list of flags to show what was selected were.
        """
        return Span.__which_was_used_last

    def onselect(self, xmin, xmax):
        """Selects the list of crystals whose parameter
        is in the region of interest (xmin, xmax),
        sets new data for histograms and draws the region of interest

        One click reset clear the region of interest.
        """
        Span.set_all_false()
        Span.__which_was_used_last[self.index] = True

        # Always search every crystal whose parameter
        # is in the region of interest and exclude the rest.
        # We clear list and search again
        Span.__crystals_included.clear()
        self.crystals_excluded.clear()
        left_posx = min(xmin, xmax)  # Left selection point.
        right_posx = max(xmin, xmax)  # Right selection point.
        if left_posx == right_posx:  # Clicking resets the selection.
            # set flags
            self.histogram_list[self.index].was_clicked_before = False
            self.histogram_list[self.index].range_green_space = None, None
        else:
            # set flags this histogram was clicked
            self.histogram_list[self.index].was_clicked_before = True
            # set range green space
            self.histogram_list[self.index].range_green_space = (left_posx,
                                                                 right_posx)
        for crystal in self.all_crystals_list:
            # Loop for each histogram checking if it belongs to the selection.
            if not self.is_exluded(crystal):
                # If the crystal meets all conditions it is added.
                Span.__crystals_included.append(crystal)
        LOGGER.info(
            "Selected {} of {} cells".format(len(Span.__crystals_included),
                                             len(self.all_crystals_list)))

        self.data_update()
        for hist in self.histogram_list:
            # Loop for changing the colour to green on the selected part.
            hist.draw_green_space()

    def is_exluded(self, crystal):
        """Checks whether a given crystal is in the region of interest.

        Parameters
        ----------

        crystal : dict

            Crystal details.

        Returns
        -------
        True : if crystal is in the region of interest.
        """
        for hist in self.histogram_list:
            if hist.bool_crystal_exluded_green_space(crystal[hist.name]):
                self.crystals_excluded.append(crystal)
                return True

    @staticmethod
    def get_crystals_included_list():
        """ Returns all crystals found in the region of interest.
        """
        return Span.__crystals_included

    def data_update(self):
        """Method for updating data in
        the histograms with regard to the selection.
        """
        data_included = histograms_data(Span.__crystals_included)
        data_excluded = {'a': [], 'b': [], 'c': [],
                         'alfa': [], 'beta': [], 'gamma': []}
        for crystal in self.crystals_excluded:
            for hist in self.histogram_list:
                data_excluded[hist.name].append(crystal[hist.name])
        # set data and refresh hist
        for hist in self.histogram_list:
            hist.update(data_excluded=data_excluded[hist.name],
                        data_to_histogram=data_included[hist.name])
