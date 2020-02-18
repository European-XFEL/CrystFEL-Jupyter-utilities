"""Module for displaying a single module in a subplot.
"""


class Histogram:
    """ Represents a histogram on a single subplot.

    Attributes
    ----------

    axs : The class:`matplotlib.axes.Axes`

        The Axes contains most of the figure elements.
    name : str

        Histogram name used in title.
    xlabel : str

        Distanse or angle unit.
    bins : int

        Number of bins.
    was_clicked_before : boolean

        Flag for checking is something was selected on a hist.
    range_green_space : list

        Range of the 'green' surface.
    data_included : list

        Data not excluded during selection.
    data_excluded : list

        Data in the range which was not selected.
    color_exclude : str

        The name of the color to the exclude histogram bar.

    current_xlim : tuple

            Current x limits of the histogram.
    patches : list

        Individual patches used to create the histogram.
    """

    def __init__(self, axs, name, xlabel, data_to_histogram, colors, bins):
        """
            Attributes
            ----------

            axs : The class:`matplotlib.axes.Axes`

                The Axes contains most of the figure elements.
            name : str

                Histogram name used in title.
            xlabel : str

                Distance or angle unit.
            bins : int

                Number of bins.
            colors : dict

                Colors of changing the bars in the histogram.
            data_to_histogram : dict

                Data for the histogram.
        """
        self.name = name
        self.axs = axs
        self.__bins = bins
        self.xlabel = xlabel
        self.__was_clicked_before = False
        self.__range_green_space = [None, None]
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
        self.__list_colors = [
            colors[centering] for centering in self.cryst_list]
        self.__list_colors.append(self.color_exclude)
        self.axs.set_title("Histogram of " + self.name)
        self.axs.set_xlabel(self.xlabel)
        _, _, self.patches = self.axs.hist(x=self.list_data, bins=self.bins,
                                           density=1, stacked=True, alpha=0.9,
                                           range=(self.min, self.max),
                                           color=self.__list_colors,
                                           histtype='stepfilled')
        # Draw the histogram
        # histtype = 'stepfilled' because for the default type refreshing is
        # very slow.
        # patches is a list of 8 Polygons containing matrix N2 where
        # y height is in the second column.
        # Drawing the grid:
        self.axs.grid(True)
        self.__xlim = self.axs.get_xlim()
        self.__current_xlim = self.axs.get_xlim()

    def reset(self):
        """Restore the initial settings.
        """
        self.__was_clicked_before = False
        self.__range_green_space = None, None
        self.__current_xlim = self.__xlim

    def bool_crystal_exluded_green_space(self, data):
        """Method for checking if data is in the selection and if the
        cristal will be included in the selection or not.

        Parametetrs
        -----------

        data : double

            The value given to check if it belongs to the range of ​​interest.

        Returns
        -------

        Boolean value.
        """
        if (self.__range_green_space[0] is None or
                self.__range_green_space[1] is None):
            return False
        elif (data < self.__range_green_space[0] or
                data > self.__range_green_space[1]):
            return True
        return False

    @property
    def range_green_space(self):
        return self.__range_green_space

    @range_green_space.setter
    def range_green_space(self, left_right):
        """Setting the range of selection.

        Parameters
        ----------

        left_right : tuple

            Left and right position the range of ​​interest.
        """
        self.__range_green_space = left_right

    def draw_green_space(self):
        """Draw the range of ​​interest ('green')
        """
        if (self.__range_green_space[0] is not None or
                self.__range_green_space[1] is not None):
            self.axs.axvspan(self.__range_green_space[0],
                             self.__range_green_space[1],
                             facecolor='#2ca02c', alpha=0.5)

    @property
    def was_clicked_before(self):
        """Get a boolean value that specifies
        if the histogram had the range selected.
        """
        return self.__was_clicked_before

    @was_clicked_before.setter
    def was_clicked_before(self, true_false):
        """Set flag was_clicked_before.

        Parameters
        -----------
        true_false : boolean

           value changing the flag was_clicked_before
        """
        self.__was_clicked_before = true_false

    @property
    def bins(self):
        """Get bins.
        """
        return self.__bins

    @bins.setter
    def bins(self, bins):
        """Changing number of bins.

        Parameters
        ----------
        bins : int

            Number of bins.
        """
        self.__bins = int(bins)
        # Dividing by 2 may give float number.

    @property
    def list_colors(self):
        """Get list of colors of the histogram.

        Returns
        -------
        list_colors : list

            The list with colors for each centering
            in the histogram.
        """
        return self.__list_colors

    @list_colors.setter
    def list_colors(self, colors):
        """Set colors.

        Parameters
        ----------

        colors : dict

            Colors of changing the bars in the histogram.
        """
        self.__list_colors = [
            colors[centering] for centering in self.cryst_list]
        self.__list_colors.append(self.color_exclude)

    def update_colors(self):
        """Loop for each bin and updating colour for the next in colour loop.
        """

        for patch_index in range(9):
            for box in self.patches[patch_index]:
                box.set_facecolor(self.__list_colors[patch_index])

    def update(self, data_to_histogram=None, data_excluded=None):
        """Updates a single histogram.

        Parameters
        ----------

        data_to_histogram : dict

            Data for the histogram.
            Default : None when we only refresh histogram.
        data_excluded : list

            Data excluded for the histogram.
            Default is None when we only refresh histogram.
        """
        # update new data to the histogram when selecting the range.
        if data_to_histogram is not None and data_excluded is not None:
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

        # Refresh histogram
        # Clear subplot
        self.axs.clear()
        self.axs.set_title("Histogram of " + self.name)
        self.axs.set_xlabel(self.xlabel)
        # Draw histogram
        _, _, self.patches = self.axs.hist(x=self.list_data, bins=self.bins,
                                           density=1, stacked=True, alpha=0.9,
                                           range=(self.min, self.max),
                                           color=self.__list_colors,
                                           histtype='stepfilled')
        # Draw mesh
        self.axs.grid(True)
        self.axs.set_xlim(self.__current_xlim)

    @property
    def current_xlim(self):
        """Get current x-axis limits of the histogram.

        Returns
        -------
        xlim : tuple

            The x-axis limits of the histogram.
        """
        return self.__current_xlim

    def update_current_xlim(self):
        """Update the histogram position by moving it with the move button
        """
        self.__current_xlim = self.axs.get_xlim()
