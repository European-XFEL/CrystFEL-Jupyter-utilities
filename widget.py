"""
Module for centering switches and handling mouse events.
"""
import itertools
from matplotlib.widgets import Button, SpanSelector, Slider, RadioButtons
import crystlib


class ButtonBins(Button):
    """A GUI button to change the number of bins in all histograms

    Attributes
    ----------
    fig : The :class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    histogram_list : list
        Contains objects the class:`histogram.Histogram`

    label : The :class:`matplotlib.text.Text` instance.
    """
    __bins = None
    # zmienna używana przez wszystkie objekty tej klasy
    # inicjalizowana przez set_bins

    def __init__(self, fig, histogram_list, ax, label):
        """
        Parameters
        ----------
        fig : The :class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The :class:`matplotlib.axes.Axes`

            instance the button will be placed into.
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
        """ Set the value of bins for all histograms

        Parameters
        ----------
        bins : int

            New value of bins
        """
        ButtonBins.__bins = bins

    def change_bins(self, event):
        """
        When the ButtonBins is clicked, call this func with event

        Parameters
        ----------
        event : The class:`matplotlib.backend_bases.Event`
        """
        # Changing number of bins; Number is a power of 2. Max val. 512.
        if self.label == '+':
            if ButtonBins.__bins < 512:
                ButtonBins.__bins *= 2
                for his in self.histogram_list:
                    his.set_bins(ButtonBins.__bins)
                    his.update()
                    his.draw_green_space()
        elif self.label == '-':
            if ButtonBins.__bins > 2:
                ButtonBins.__bins /= 2
                for his in self.histogram_list:
                    his.set_bins(ButtonBins.__bins)
                    his.update()
                    his.draw_green_space()
        self.fig.canvas.draw()


class Radio(RadioButtons):
    """A GUI radio button used in hdfsee

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
    cmap : The class:`matplotlib.colors.Colormap`

        used to change color map in image
    """
    def __init__(self, fig, ax, labels, cmap, image):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            instance the button will be placed into.
        labels : tuple of The :class:`matplotlib.text.Text`

            instance.
        cmap : The class:`matplotlib.colors.Colormap`

            used to change color map in image
        image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
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
        """set a new image

        Parameters
        ----------
        image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
        """
        self.image = image

    def get_cmap(self):
        """returned last cmap
        """
        return self.cmap


class ContrastSlider(Slider):
    """A GUI slider used in hdfsee to change the contrast

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
    vmax : int

        define the data range that the colormap covers.
    vmin : int

        define the data range that the colormap covers.
    """
    def __init__(self, image, fig, ax, label, vmin, vmax):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`

            The Figure which will be redraw.
        ax : The class:`matplotlib.axes.Axes`

            instance the button will be placed into.
        label : The :class:`matplotlib.text.Text` instance.

            instance.
        vmax : int

            define the data range that the colormap covers.
        vmin : int

            define the data range that the colormap covers.
        image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
        """
        self.image = image
        self.fig = fig
        self.vmax = vmax
        self.vmin = vmin
        # Initialize parent constructor.
        super(ContrastSlider, self).__init__(ax, label, vmin, 600, valinit=255)
        # On click reaction.
        super(ContrastSlider, self).on_changed(self.on_check)

    def on_check(self, event):
        self.vmax = event
        self.image.set_clim(vmax=self.vmax)
        self.fig.canvas.draw()

    def set_image(self, image):
        """set a new image

        Parameters
        ----------
        image : The class:`matplotlib.image.AxesImage`

            created by functions imshow()
        """
        self.image = image

    def get_vmax(self):
        """returned  last vmax

        Returns
        -------
        vmax : int
            max range that the colormap covers.
        """
        return self.vmax

    def get_vmin(self):
        """returned  last vmin

        Returns
        -------
        vmin : int
            min range that the colormap covers.
        """
        return self.vmin


class CenteringButton(Button):
    """A GUI button for changing
    the color of the histogram bar for proper centering.

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    colors : itertools.cycle list

        contains a list of colors
    histogram_list : list

        Contains objects the class:`histogram.Histogram`
    list_color : list

        Colors of changing the bars in the histogram
    histogram_list : list

        Contains objects the class:`histogram.Histogram`
    histogram_colors : dict

        key - type centering, value - list with colors
    """
    def __init__(self, fig, axs, label, list_color,
                 histogram_list, histogram_colors):
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

            instance.
        """
        self.color = next(self.colors)  # After clicking changes the colour
        # to the next in a loop. For a given button the colour will be set in
        # the histogram.
        # change name color in diction for key PABCFHIR is label button
        self.histogram_colors[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.set_colour(self.histogram_colors)  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_color()
        self.fig.canvas.draw()  # Redraw the current figure.

    def reset_color(self):
        """Restore the initial settings
        """
        self.colors = itertools.cycle(self.list_color)
        self.color = self.list_color[0]
        self.histogram_colors[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.set_colour(self.histogram_colors)  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_color()


class Span():
    """Visually select the region of interest on a single histogram

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    crystals_excluded_list : list

        Crystals excluded
    all_crystals_list : list

        all crystals
    histogram_list : list

        Contains objects the class:`histogram.Histogram`
    index : int

        index number in the histgram_list
    name : str

        name of the histrgam
    """
    # list of flags for showing what was selected last, where.
    __which_was_used_last = [False, False, False, False, False, False]
    __crystals_included = []
    # crystals in green space

    def __init__(self, fig, crystals_excluded_list,
                 all_crystals_list, histogram_list, name, index):

        self.fig = fig
        # Excluded crystals.
        self.crystals_excluded_list = crystals_excluded_list
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
        """list of flags to show what was selected were set to false
        """
        Span.__which_was_used_last = [False, False, False, False, False, False]

    @staticmethod
    def get_all_used():
        """get a list of flags to show what was selected were.
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
        # is in the region of interes and exclude the rest.
        # We clear list and search again
        Span.__crystals_included.clear()
        self.crystals_excluded_list.clear()
        left_posx = min(xmin, xmax)  # Left selection point.
        right_posx = max(xmin, xmax)  # Right selection point.

        if left_posx == right_posx:  # Clicking resets the selection.
            # set flags
            self.histogram_list[self.index].set_was_clicked_before(False)
            self.histogram_list[self.index].set_range_green_space(None, None)

        else:
            # set flags this histogram was clicked
            self.histogram_list[self.index].set_was_clicked_before(True)
            # set range green space
            self.histogram_list[self.index].set_range_green_space(left_posx,
                                                                  right_posx)
        for crystal in self.all_crystals_list:
            # Loop for each histogram checking if it belongs to the selection.
            if not self.is_exluded(crystal):
                # If the crystal meets all conditions it is added.
                Span.__crystals_included.append(crystal)

        print("Selected {} of {} cells".format(len(Span.__crystals_included),
              len(self.all_crystals_list)))

        self.data_update()
        for hist in self.histogram_list:
            # Loop for changing the colour to green on the selected part.
            hist.draw_green_space()

    def is_exluded(self, crystal):
        """checks whether a given crystal is in the region of interest.

        Parameters
        ----------

        crystal : dict
            crystal details.

        Returns
        -------

        True : if crystal is in the region of interest.
        """
        for hist in self.histogram_list:
            if hist.bool_crystal_exluded_green_space(crystal[hist.name]):
                self.crystals_excluded_list.append(crystal)
                return True

    @staticmethod
    def get_crystals_included_list():
        """ Returns all crystals found in the region of interest
        """
        return Span.__crystals_included

    def data_update(self):
        """Method for updating data in
        the histograms with regard to the selection.
        """
        data_included =\
            crystlib.dict_data_histogram(Span.__crystals_included)

        data_excluded = {'a': [], 'b': [], 'c': [],
                         'alfa': [], 'beta': [], 'gamma': []}

        for crystal in self.crystals_excluded_list:
            for hist in self.histogram_list:
                data_excluded[hist.name].append(crystal[hist.name])

        # set data and refresh hist
        for hist in self.histogram_list:
            hist.set_data(data_excluded=data_excluded[hist.name],
                          data_to_histogram=data_included[hist.name])
            hist.update()
