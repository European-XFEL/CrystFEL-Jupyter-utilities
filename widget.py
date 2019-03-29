"""
Module for centering switches and handling mouse events.
"""
import itertools
from matplotlib.widgets import Button, SpanSelector, Slider, RadioButtons
import crystlib


class Bttn_bins(Button):
    """
    Klasa reprezentująca guzik do zmiany ilości
    bins we wszystkich histogrmaach
    """
    __bins = None
    # zmienna używana przez wszystkie objekty tej klasy
    # inicjalizowana przez set_bins

    def __init__(self, fig, histogram_list, ax, label):
        # Initialize parent constructor.
        super(Bttn_bins, self).__init__(ax=ax, label=label)
        self.fig = fig  # For calling canvas draw which refreshes the image.
        self.histogram_list = histogram_list  # List with all histograms
        self.label = label
        super(Bttn_bins, self).on_clicked(self.change_bins)  # Click reaction

    def set_bins(bins):
        """
        Ustawia mi początkową wartość bins dla wszystkich
        histogrmaów
        """
        Bttn_bins.__bins = bins

    def change_bins(self, event):
        """
        Method for keyboard handling.
        """
        # Changing number of bins; Number is a power of 2. Max val. 512.

        if self.label == '+':
            if Bttn_bins.__bins < 512:
                Bttn_bins.__bins *= 2
                for his in self.histogram_list:
                    his.set_bins(Bttn_bins.__bins)
                    his.update()
                    his.draw_green_space()
        elif self.label == '-':
            if Bttn_bins.__bins > 2:
                Bttn_bins.__bins /= 2
                for his in self.histogram_list:
                    his.set_bins(Bttn_bins.__bins)
                    his.update()
                    his.draw_green_space()
        self.fig.canvas.draw()


class Radio(RadioButtons):
    """
    class used in hdfsee
    image - image created by functions imshow()
    fig - object of the Figuge class used to redraw
    cmap - color map used to change color map in image
    """
    def __init__(self, fig, ax, labels, cmap, image):
        self.image = image
        self.fig = fig
        self.cmap = cmap
        # Initialize parent constructor.
        super(Radio, self).__init__(ax=ax, labels=labels, active=0)
        # On click reaction.
        self.on_clicked(self.colorfunc)

    def colorfunc(self, label):
        """
        Calls itself after switching colour.
        Updates the image.
        """
        # change name cmap
        self.cmap = label
        # set cmap
        self.image.set_cmap(cmap=self.cmap)
        # Redraw the current figure.
        self.fig.canvas.draw()

    def set_image(self, image):
        """
        set a new object returned by imshow
        """
        self.image = image

    def get_cmap(self):
        """
        returned last cmap
        """
        return self.cmap


class My_slider(Slider):
    """
    class used in hdfsee
    image - image created by functions imshow()
    fig - object of the Figuge class used to redraw
    vmax and vmin - is used to change contrast
    """
    def __init__(self, image, fig, ax, label, vmin, vmax):
        self.image = image
        self.fig = fig
        self.vmax = vmax
        self.vmin = vmin
        # Initialize parent constructor.
        super(My_slider, self).__init__(ax, label, vmin, 600, valinit=255)
        super(My_slider, self).on_changed(self.on_check)  # On click reaction.

    def on_check(self, event):
        self.vmax = event
        self.image.set_clim(vmax=self.vmax)
        self.fig.canvas.draw()

    def set_image(self, image):
        self.image = image

    def get_vmax(self):
        return self.vmax

    def get_vmin(self):
        return self.vmin


class Bttn(Button):
    """
    Class for button changing crystal type.
    fig - whole image figure called by canvas.draw().
    list_color - list with def. colours.
    histogram_list - list with objects of class histogram.
    dict_color_histogram - dictionary with keys as centering types and value
    is the colour name.
    """
    def __init__(self, fig, axs, label, list_color,
                 histogram_list, dict_color_histogram):
        # Initialize parent constructor.
        super(Bttn, self).__init__(ax=axs, label=label, color=list_color[0])
        self.fig = fig  # For calling canvas draw which refreshes the image.
        # Loop for the colour list of a given button.
        self.colors = itertools.cycle(list_color)
        super(Bttn, self).on_clicked(self.on_check)  # Click reaction
        self.histogram_list = histogram_list  # List with all histograms
        self.dict_color_histogram = dict_color_histogram
        self.list_color = list_color

    def on_check(self, label):
        """
        Change colour of the histogram depending
        on which switch has been clicked.
        """
        self.color = next(self.colors)  # After clicking changes the colour
        # to the next in a loop. For a given button the colour will be set in
        # the histogram.
        # change name color in diction for key PABCFHIR is label button
        self.dict_color_histogram[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.set_cololor(self.dict_color_histogram)  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_color()
        self.fig.canvas.draw()  # Redraw the current figure.

    def reset_color(self):
        self.colors = itertools.cycle(self.list_color)
        self.color = self.list_color[0]
        self.dict_color_histogram[self.label.get_text()] = self.color
        for hist in self.histogram_list:  # Loop for each histogram.
            hist.set_cololor(self.dict_color_histogram)  # Setting new colour
            # in a given histogram.
            # Refresh each histogram (clear image and draw again)
            hist.update_color()


class Span():
    """
    Class for selecting the region of interest.
    which_was_clicked_before - list of flags for showing
        what was selected where.
    dict_witch_range_crystal - original scope under as value (?).
    """
    __which_was_used_last = [False, False, False, False, False, False]
    __crystals_included_list = []
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

    def set_all_false():
        Span.__which_was_used_last = [False, False, False, False, False, False]

    def get_all_used():
        return Span.__which_was_used_last

    def onselect(self, xmin, xmax):
        """
        Method for getting data from a dictionary
        after selecting region of interest.
        """
        Span.set_all_false()
        Span.__which_was_used_last[self.index] = True

        # Always search every crystal and exclude the rest (?).
        # We clear list and search again
        Span.__crystals_included_list.clear()
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
            if self.histogram_list[0].bool_crystal_exluded_green_space(crystal.a):
                self.crystals_excluded_list.append(crystal)
            elif self.histogram_list[1].bool_crystal_exluded_green_space(crystal.b):
                self.crystals_excluded_list.append(crystal)
            elif self.histogram_list[2].bool_crystal_exluded_green_space(crystal.c):
                self.crystals_excluded_list.append(crystal)
            elif self.histogram_list[3].bool_crystal_exluded_green_space(crystal.alfa):
                self.crystals_excluded_list.append(crystal)
            elif self.histogram_list[4].bool_crystal_exluded_green_space(crystal.beta):
                self.crystals_excluded_list.append(crystal)
            elif self.histogram_list[5].bool_crystal_exluded_green_space(crystal.gamma):
                self.crystals_excluded_list.append(crystal)
            else:
                # If the crystal meets all conditions it is added.
                Span.__crystals_included_list.append(crystal)

        print("Selected {} of {} cells".format(len(Span.__crystals_included_list),
              len(self.all_crystals_list)))

        self.data_update()
        for hist in self.histogram_list:
            # Loop for changing the colour to green on the selected part.
            hist.draw_green_space()

    def get_crystals_included_list():
        return Span.__crystals_included_list

    def data_update(self):
        """
        Method for updating data in
        the histograms with regard to the selection.
        """
        dict_data_histogram_included =\
            crystlib.dict_data_histogram(Span.__crystals_included_list)

        data_excluded_a = []
        data_excluded_b = []
        data_excluded_c = []
        data_excluded_alfa = []
        data_excluded_beta = []
        data_excluded_gamma = []

        for crystal in self.crystals_excluded_list:
            # each crystal value is added at the end of the list
            data_excluded_a.append(crystal.a)
            data_excluded_b.append(crystal.b)
            data_excluded_c.append(crystal.c)
            data_excluded_alfa.append(crystal.alfa)
            data_excluded_beta.append(crystal.beta)
            data_excluded_gamma.append(crystal.gamma)
        self.histogram_list[0].set_data(data_to_histogram=dict_data_histogram_included["a"],
                                        data_excluded=data_excluded_a)
        self.histogram_list[1].set_data(data_to_histogram=dict_data_histogram_included["b"],
                                        data_excluded=data_excluded_b)
        self.histogram_list[2].set_data(data_to_histogram=dict_data_histogram_included["c"],
                                        data_excluded=data_excluded_c)

        self.histogram_list[3].set_data(data_to_histogram=dict_data_histogram_included["alfa"],
                                        data_excluded=data_excluded_alfa)

        self.histogram_list[4].set_data(data_to_histogram=dict_data_histogram_included["beta"],
                                        data_excluded=data_excluded_beta)

        self.histogram_list[5].set_data(data_to_histogram=dict_data_histogram_included["gamma"],
                                        data_excluded=data_excluded_gamma)
        self.histogram_list[0].update()
        self.histogram_list[1].update()
        self.histogram_list[2].update()
        self.histogram_list[3].update()
        self.histogram_list[4].update()
        self.histogram_list[5].update()
