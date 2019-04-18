"""
Module for displaying a single module in a subplot.
"""


class Histogram():
    """ Represents a histogram on a single subplot

    Attributes
    ----------

    axs : The class:`matplotlib.axes.Axes`

        The Axes contains most of the figure elements
    name : str

        histogram name used in title.
    xlabel : str

        distanse or angle unit
    bins : int

        number of bins
    was_clicked_before : boolean

        flag for checking is something was selected on a hist.
    range_green_space : list

        range of the 'green' surface
    data_included : list

        data not excluded during selection
    data_excluded : list

        data in the range which was not selected
    color_exclude : str

        the name of the color to the exclude histogram bar

    current_xlim : tuple

            current x limits of the histogram.
    patches : list

        individual patches used to create the histogram
    """
    def __init__(self, axs, name, xlabel, data_to_histogram, colors, bins):
        """
            Attributes
            ----------

            axs : The class:`matplotlib.axes.Axes`

                The Axes contains most of the figure elements
            name : str

                histogram name used in title.
            xlabel : str

                distanse or angle unit
            bins : int

                number of bins
            colors : dict

                Colors of changing the bars in the histogram
            data_to_histogram : dict

                Data for the histogram
    """
        self.name = name
        self.axs = axs
        self.bins = bins
        self.xlabel = xlabel
        self.was_clicked_before = False
        self.range_green_space = [None, None]
        # Try/except necessary - not all histograms contain values depending
        # on centering type.
        self.cryst_list = ['P', 'A', 'B', 'C', 'I', 'F', 'H', 'R']
        self.list_data = []
        self.data_included = []
        for k, a_cryst in enumerate(self.cryst_list):
            try:
                self.list_data.append(data_to_histogram[a_cryst])
            except KeyError:
                self.list_data.append([])
            self.data_included += self.list_data[k]

        try:
            self.data_excluded = []
        except KeyError:
            self.data_excluded = []

        self.list_data.append(self.data_excluded)

        self.max = max(self.data_included + self.data_excluded)
        self.min = min(self.data_included + self.data_excluded)

        self.color_exclude = 'lightgray'

        self.list_colors = [colors[color] for color in self.cryst_list]
        self.list_colors.append(self.color_exclude)

        self.axs.set_title("Histogram of " + self.name)
        self.axs.set_xlabel(self.xlabel)

        _, _, self.patches = self.axs.hist(x=self.list_data, bins=self.bins,
                                           density=1, stacked=True, alpha=0.9,
                                           range=(self.min, self.max),
                                           color=self.list_colors,
                                           histtype='stepfilled')
        # Draw the histogram
        # histtype = 'stepfilled' because for the default type refreshing is
        # very slow.
        # patches is a list of 8 Polygons containing matrix N2 where
        # y height is in the second column.
        # Drawing the grid:
        self.axs.grid(True)
        self.xlim = self.axs.get_xlim()
        self.current_xlim = self.axs.get_xlim()

    def reset(self):
        """Restore the initial settings
        """
        self.was_clicked_before = False
        self.range_green_space = [None, None]
        self.current_xlim = self.xlim

    def bool_crystal_exluded_green_space(self, data):
        """
        Method for checking if data is in the selection and if the
        cristal will be included in the selection or not.

        Parametetrs
        -----------

        data : double

            the value given to check if it belongs to the range of ​​interest

        Returns
        -------

        bolean value
        """
        if self.range_green_space[0] is None or\
           self.range_green_space[1] is None:
            return False
        elif data < self.range_green_space[0] or\
                data > self.range_green_space[1]:
            return True

        return False

    def set_range_green_space(self, minimum, maximum):
        """Setting the range of selection.

        Parameters
        ----------

        minimum : double

        left position the range of ​​interest
        maximum : double

        right position the range of ​​interest
        """
        self.range_green_space = [minimum, maximum]

    def draw_green_space(self):
        """Draw the range of ​​interest ('green')
        """
        if self.range_green_space[0] is not None or\
           self.range_green_space[1] is not None:
            self.axs.axvspan(self.range_green_space[0],
                             self.range_green_space[1],
                             facecolor='#2ca02c', alpha=0.5)

    def set_was_clicked_before(self, true_false):
        """set flag was_clicked_before.
        """
        self.was_clicked_before = true_false

    def get_was_clicked_before(self):
        """Return flag was_clicked_before.
        """
        return self.was_clicked_before

    def set_bins(self, bins):
        """Changing number of bins.

        Parameters
        ----------
        bins : int

            number of bins
        """
        self.bins = int(bins)
        # Dividing by 2 may give float number.

    def get_bins(self):
        """get bins.
        """
        return self.bins

    def set_name(self, name):
        """Changing the histogram name.
        """
        self.name = name

    def set_data(self, data_to_histogram, data_excluded):
        """Updating the data.

        Parameters
        ----------

        data_to_histogram : dict

            Data for the histogram
        data_excluded : list

            Data excluded for the histogram.
        """
        try:
            self.data_excluded = data_excluded
        except KeyError:
            self.data_excluded = []

        self.list_data = []
        self.data_included = []
        for k, a_cryst in enumerate(self.cryst_list):
            try:
                self.list_data.append(data_to_histogram[a_cryst])
            except KeyError:
                self.list_data.append([])
            self.data_included += self.list_data[k]
        self.list_data.append(self.data_excluded)

    def set_colour(self, colors):
        """Set colors.

        Parameters
        ----------

        colors : dict

            Colors of changing the bars in the histogram
        """
        self.list_colors = [colors[color] for color in self.cryst_list]
        self.list_colors.append(self.color_exclude)

    def update_color(self):
        """
        Loop for each bin and updating colour for the next in colour loop.
        """

        for patch_index in range(9):
            for box in self.patches[patch_index]:
                box.set_facecolor(self.list_colors[patch_index])

    def update(self):
        """
        Updates a single histogram.
        """
        # Clear subplot
        self.axs.clear()
        self.axs.set_title("Histogram of " + self.name)
        self.axs.set_xlabel(self.xlabel)
        # Draw histogram
        _, _, self.patches = self.axs.hist(x=self.list_data, bins=self.bins,
                                           density=1, stacked=True, alpha=0.9,
                                           range=(self.min, self.max),
                                           color=self.list_colors,
                                           histtype='stepfilled')
        # Draw mesh
        self.axs.grid(True)
        self.axs.set_xlim(self.current_xlim)

    def set_current_xlim(self, xlim):
        """ set current x limits of the histogram.
        """
        self.current_xlim = xlim

    def get_current_xlim(self):
        """get current x limits of the histogram.
        """
        return self.axs.get_xlim()

    def get_current_ylim(self):
        """get current y limits of the histogram.
        """
        return self.axs.get_ylim()
