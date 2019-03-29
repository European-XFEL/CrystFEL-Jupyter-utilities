"""
Module for displaying a single module in a subplot.
"""


class Histogram():
    """
    Class for representing a single subplot for displaying a histogram.
    axs     - a subplot object.
    title   - histogram title.
    xlabel  - distanse or angle unit
    facecolor - histogram colour
    bins    - number of bins
    was_clicked_before - flag for checking is something was selected on a hist.
    range_green_space - range of the 'green' surface
    data_included - data not excluded during selection
    data_excluded - data in the range which was not selected
    """
    def __init__(self, axs, title, xlabel, data_to_histogram,
                 data_excluded, colors, bins):
        self.title = title
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
            self.data_included+=self.list_data[k]
        
        try:
            self.data_excluded = data_excluded
        except KeyError:
            self.data_excluded = []
        
        self.list_data.append(self.data_excluded)

        self.max = max(self.data_included + self.data_excluded)
        self.min = min(self.data_included + self.data_excluded)

        self.color_exclude = 'lightgray'

        self.list_colors = [colors[color] for color in self.cryst_list]
        self.list_colors.append(self.color_exclude)

        self.axs.set_title(self.title)
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
        self.was_clicked_before = False
        self.range_green_space = [None, None]
        self.current_xlim = self.xlim

    def bool_crystal_exluded_green_space(self, data):
        """
        Function for checking if data is in the selection and if the
        cristal will be included in the selection or not.
        """
        if self.range_green_space[0] is None or\
           self.range_green_space[1] is None:
            return False
        elif data < self.range_green_space[0] or\
                data > self.range_green_space[1]:
            return True

        return False

    def set_range_green_space(self, minimum, maximum):
        """
        Setting the range of selection.
        """
        self.range_green_space = [minimum, maximum]

    def draw_green_space(self):
        """
        Changing colour to green in the selection.
        """
        if self.range_green_space[0] is not None or\
           self.range_green_space[1] is not None:
            self.axs.axvspan(self.range_green_space[0],
                             self.range_green_space[1],
                             facecolor='#2ca02c', alpha=0.5)

    def set_was_clicked_before(self, true_false):
        """
        Check if range was selected.
        """
        self.was_clicked_before = true_false

    def get_was_clicked_before(self):
        """
        Return bool value.
        """
        return self.was_clicked_before

    def set_bins(self, bins):
        """
        Changing number of bins.
        """
        self.bins = int(bins)
        # Dividing by 2 may give float number.

    def get_bins(self):
        return self.bins

    def set_title(self, title):
        """
        Change the histogram title.
        """
        self.title = title

    def set_data(self, data_to_histogram, data_excluded):
        """
        Method for updating data during the selection with Span.
        Finds excluded crystals (?).
        Try/Except needed for none crystals in selection.
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
        """
        For updating colours.
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
        self.axs.set_title(self.title)
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
        self.current_xlim = xlim

    def get_current_xlim(self):
        return self.axs.get_xlim()

    def get_current_ylim(self):
        return self.axs.get_ylim()
