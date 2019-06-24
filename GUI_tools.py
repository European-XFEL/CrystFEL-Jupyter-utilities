"""
Module can be executed in a notebook.
Joins work of other moules together.
"""
# !/usr/bin/env python

import matplotlib.pyplot as plt
# In there we have refereces on to 'home' button
from matplotlib.backend_bases import NavigationToolbar2
import numpy as np
from scipy import stats

import crystlib
from histogram import Histogram
import stream_read
from widget import Span, CenteringButton, ButtonBins, Button
from zoompan import ZoomOnWheel


class CellExplorer:
    """
    Displaying the 6 subplots, each containing a histogram with data from
    'indexing stream' file. Each centering type is displayed as a different
    colour and can be switched after clicking on it as in the cell_explorer.
    """

    def __init__(self, streamfile, **args):
        NavigationToolbar2.home = self.home_reset
        # "Home" button has references to our function
        self.args = args
        self.stream_name = streamfile
        self.fig, self.axs_list = plt.subplots(2, 3)
        # Windows for histograms
        self.axs_list = self.axs_list.ravel()
        # Reshaping matrix to vector: [1][1] to [4]
        # all crystals find in file
        self.all_crystals_list = \
            stream_read.search_crystals_parameters(self.stream_name)
        # Crystals selected by Spanselector (with their colours)
        self.dict_data_histogram =\
            crystlib.dict_data_histogram(self.all_crystals_list)
        # Dictionary with a, b, c, alpha, beta, gamma as keys,
        # ABCFHIR with list of data as values
        self.crystals_excluded_list = []
        # Excluded cristals

        # Colours for each centering type during initialization
        self.dict_color_histogram = {'P': 'gray', 'A': 'cyan', 'B': 'darkblue',
                                     'C': 'royalblue', 'H': "firebrick",
                                     'F': "magenta", 'I': 'lime', 'R': 'olive'}
        self.histogram_order = ['a', 'b', 'c', 'alfa', 'beta', 'gamma']
        self.cryst_list = ['P', 'A', 'B', 'C', 'I', 'F', 'H', 'R']
        self.bins = 16
        # Starting with 2 after pressing +/- keys.
        # Pressing + or - chages the binning by factor of 2.
        # The histograms:
        self.histogram_list = []
        for hist_indx, hist_name in enumerate(self.histogram_order):
            temp_label = 'Angstrem[Å]'
            if hist_indx > 2:
                temp_label = 'deg'
            self.histogram_list.append(Histogram(axs=self.axs_list[hist_indx], name=hist_name,
                                                 xlabel=temp_label,
                                                 data_to_histogram=self.dict_data_histogram[hist_name],
                                                 colors=self.dict_color_histogram, bins=self.bins))

        plt.subplots_adjust(hspace=0.5)
        plt.subplots_adjust(wspace=0.1)
        # Histograms list
        # Buttons below; string list is the colour to which the button
        # and hist. changes after clicking.
        # Using intertool for looping to change color
        # list_color is our cyclic list


        # Buttols list:
        # All Spans include reference for crystals list which were refused
        # or not included (?) changes in 1 Span is visible by others.
        # all_crystals_list has all crystals that are finded
        # crystals_excluded_list has all crystal that has not set they are gray
        # index is used to locate which histogram applies

        button_x_pos = [0.95,0.935,0.92,0.905,0.89,0.875,0.86,0.845]
        self.buttons_list = []
        for cryst_indx, cryst_symb in enumerate(self.cryst_list):
            self.buttons_list.append(CenteringButton(axs=plt.axes([button_x_pos[-1-cryst_indx], 0.95, 0.015, 0.045]), fig=self.fig,
                                            label=cryst_symb, list_color=[
                                                self.dict_color_histogram[cryst_symb], 'gray', 'lightgrey'],
                                            histogram_list=self.histogram_list,
                                            histogram_colors=self.dict_color_histogram))

        self.span_list = []
        for hist_indx, hist_name in enumerate(self.histogram_order):
            self.span_list.append(Span(crystals_excluded_list=self.crystals_excluded_list,
                                       fig=self.fig, index=hist_indx, name=hist_name,
                                       all_crystals_list=self.all_crystals_list,
                                       histogram_list=self.histogram_list))

        # self.span_list = (span1, span2, span3, span4, span5, span6)
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        self.fig.canvas.mpl_connect('button_release_event',
                                    self.rememmber_pos_panel)
        # Listening for key events.

        self.fig.pan_zoom = ZoomOnWheel(self.fig, scale_factor=2.0)
        # For zooming in using mouse wheel
        ButtonBins.set_bins(self.bins)
        self.btt_p = ButtonBins(fig=self.fig, label='+',
                               histogram_list=self.histogram_list,
                               ax=plt.axes([0.91, 0.90, 0.025, 0.025]),)
        self.btt_m = ButtonBins(fig=self.fig, label='-',
                               histogram_list=self.histogram_list,
                               ax=plt.axes([0.935, 0.90, 0.025, 0.025]),)
        self.bttn_save = Button(ax=plt.axes([0.91, 0.875, 0.050, 0.025]),
                                label="Save")
        self.bttn_save.on_clicked(self.save_file)
        self.parametres_used()
        self.gauss_draw()
        plt.show()

    def lattice_type(self, gauss_parametrs):
        """
        return lattice type and unique_axis
        gauss_parametrs = [a,b,c,alfa,beta,gamma]
        """
        def tolerance(a, b, percent):
            if abs(a-b) < abs(a)*(percent/100):
                return True
            return False

        def is_close(a, b): return abs(a-b) < 0.3

        if(is_close(gauss_parametrs[3], 90) and
           is_close(gauss_parametrs[4], 90) and
           is_close(gauss_parametrs[5], 90)):
            # I check if the parameters(alfa,beta,gamma) are close 90 deg
            if(tolerance(gauss_parametrs[0], gauss_parametrs[1], 1.0) and
               tolerance(gauss_parametrs[1], gauss_parametrs[2], 1.0)):
                lt = "CUBIC"
                ua = '*'
            elif(tolerance(gauss_parametrs[0], gauss_parametrs[1], 1.0)):
                lt = 'TETRAGONAL'
                ua = 'c'
            elif(tolerance(gauss_parametrs[0], gauss_parametrs[2], 1.0)):
                lt = 'TETRAGONAL'
                ua = 'b'
            elif(tolerance(gauss_parametrs[1], gauss_parametrs[2], 1.0)):
                lt = 'TETRAGONAL'
                ua = 'a'
            else:
                lt = 'ORTHORHOMBIC'
                ua = '*'

        elif(is_close(gauss_parametrs[3], 90) and
             is_close(gauss_parametrs[4], 90) and
             is_close(gauss_parametrs[5], 120)):
            # I check if the parameters(alfa,beta) are close 90 deg
            # and gamma are close 120 deg
                lt = 'HEXAGONAL'
                ua = 'c'
        elif(is_close(gauss_parametrs[3], 90) and
             is_close(gauss_parametrs[4], 120) and
             is_close(gauss_parametrs[5], 90)):
            # I check if the parameters(alfa,gamma) are close 90 deg
            # and beta are close 120 deg
                lt = 'HEXAGONAL'
                ua = 'b'

        elif(is_close(gauss_parametrs[3], 120) and
             is_close(gauss_parametrs[4], 90) and
             is_close(gauss_parametrs[5], 90)):
            # I check if the parameters(gamma,beta) are close 90 deg
            # and alfa are close 120 deg
                lt = 'HEXAGONAL'
                ua = 'a'
        elif(is_close(gauss_parametrs[3], 90) and
             is_close(gauss_parametrs[4], 90)):
            # I check if the parameters(alfa,beta) are close 90 deg

                lt = 'MONOCLINIC'
                ua = 'c'
        elif(is_close(gauss_parametrs[3], 90) and
             is_close(gauss_parametrs[5], 90)):
            # I check if the parameters(alfa,gamma) are close 90 deg

                lt = 'MONOCLINIC'
                ua = 'b'

        elif(is_close(gauss_parametrs[4], 90) and
             is_close(gauss_parametrs[5], 90)):
            # I check if the parameters(gamma,beta) are close 90 deg

                lt = 'MONOCLINIC'
                ua = 'a'
        elif((is_close(gauss_parametrs[3], gauss_parametrs[4]) and
             is_close(gauss_parametrs[4], gauss_parametrs[5])) and
             (tolerance(gauss_parametrs[0], gauss_parametrs[1], 1.0) and
             tolerance(gauss_parametrs[1], gauss_parametrs[2], 1.0))):

                lt = 'RHOMBOHEDRAL'
                ua = '*'
        else:
                lt = "TRICLINIC"
                ua = '*'
        return (lt, ua)

    def group_centering(self):
        """
        returned maximum centering group from crystal included list
        """
        include_crystal = Span.get_crystals_included_list()
        max_group = 0
        # remmember maximum group
        centering = None
        # type of centering
        counter_group_centering = dict(zip(self.cryst_list, [0]*(len(self.cryst_list))))
        # counter for each centering
        for crystal in include_crystal:
            # search maximum group and this centring
            # Which centering is most common?
            counter_group_centering[crystal.centering] += 1
            if max_group < counter_group_centering[crystal.centering]:
                max_group = counter_group_centering[crystal.centering]
                centering = crystal.centering
        if max_group < len(include_crystal)*0.8:
            # does it constitute 80% of included crystals?
            # why 80% I don't know that was in orginal soft
            return None
        return centering

    def was_all_hist_selected(self):
        """
        check all histogrmas and return true if all
        were selected
        """
        for hist in self.histogram_list:
            if not hist.get_was_clicked_before():
                return False
        return True

    def save_file(self, event):
        """
        writes the crystallography parameters to the file
        if are some problems return Warnig message
        """
        # all must be marked
        if not self.was_all_hist_selected():
            print("Fit all six parameters first.")
            return
        gauss_parametrs = []
        # centering is most common
        centering = self.group_centering()
        if centering is None:
            print("Centering could not be determined unambiguously." +
                  "Select the unit cells more decisively.")
            return
        # determination of  Gauss parameters
        for hist in self.histogram_list:
            m, s = stats.norm.fit(hist.data_included)
            gauss_parametrs.append(np.round(m, 2))
        # start dialog winodw were we selected directory paths
        # and file name
        lattice_type, unique_axis = self.lattice_type(gauss_parametrs)
        output = "CrystFEL unit cell file version 1.0" + \
            "\nlattice_type = {}".format(lattice_type) + \
            "\nunique_axis = {}".format(unique_axis) + \
            "\ncentering = {}".format(centering) + \
            "\na = {} A".format(gauss_parametrs[0]) + \
            "\nb = {} A".format(gauss_parametrs[1]) + \
            "\nc = {} A".format(gauss_parametrs[2]) + \
            "\nal = {} deg".format(gauss_parametrs[3]) + \
            "\nbe = {} deg".format(gauss_parametrs[4]) + \
            "\nga = {} deg".format(gauss_parametrs[5])
        filename = "CrystFEL_unit_cell_file"
        # the name of the file where the parameters will be saved
        with open(filename, 'w') as file:
            file.write(output)
            # open file and save parametrs
        return

    def home_reset(self, *args, **kwargs):
        """
        method used to set the initial
        state of all histograms with a button
        NavigationToolbar2.home
        """
        for hist in self.histogram_list:
            hist.reset()
            hist.set_bins(self.bins)
            ButtonBins.set_bins(self.bins)
        for bttn in self.buttons_list:
            bttn.reset_color()

        if len(self.args) == 0:
            self.crystals_excluded_list.clear()
            for hist_indx, hist_name in enumerate(self.histogram_order):
                self.histogram_list[hist_indx].set_data(self.dict_data_histogram[hist_name],
                                                        self.crystals_excluded_list)
            for hist in self.histogram_list:
                hist.update()
        else:
            self.parametres_used()

        self.fig.canvas.draw()

    def parametres_used(self):

        for hist_indx, hist_name in enumerate(self.histogram_order):
            try:
                self.span_list[hist_indx].onselect(*self.args[hist_name])
            except:
                pass

    def rememmber_pos_panel(self, event):
        for hist in self.histogram_list:
            if hist.axs == event.inaxes:
                hist.set_current_xlim(hist.get_current_xlim())

    def press(self, event):
        """
        Method for keyboard handling.
        """
        # Changing number of bins; Number is a power of 2. Max val. 512.
        if event.key == '+':
            for index, boolean in enumerate(Span.get_all_used()):
                if boolean:
                    bins = self.histogram_list[index].get_bins()
                    if bins < 512:
                        bins *= 2
                        self.histogram_list[index].set_bins(bins)
                        self.histogram_list[index].update()
                        self.histogram_list[index].draw_green_space()
        elif event.key == '-':
            for index, boolean in enumerate(Span.get_all_used()):
                if boolean:
                    bins = self.histogram_list[index].get_bins()
                    if bins > 2:
                        bins /= 2
                        self.histogram_list[index].set_bins(bins)
                        self.histogram_list[index].update()
                        self.histogram_list[index].draw_green_space()

        # Fitting selected range:
        if event.key == 'g':
            self.gauss_draw()
        self.fig.canvas.draw()

    def gauss_draw(self):
        for hist in self.histogram_list:
            hist.update()
            hist.draw_green_space()
            m, s = stats.norm.fit(hist.data_included)
            # Computing mu and sigma
            lnspc = np.linspace(hist.get_current_xlim()[0],
                                hist.get_current_xlim()[1], 80)
            # Table 80 argumnets x by equal distances [0,1,2]
            pdf_g = stats.norm.pdf(lnspc, m, s)
            # Theoretical value for our argumnets
            hist.axs.plot(lnspc, pdf_g)
            # Setting for relative 3/4 of the height;
            # each histogram has other y axis scale
            # and maximum value.
            position_y_text = 0.75*hist.get_current_ylim()[1]
            # Each text will begin with each histogram:
            position_x_text = hist.get_current_xlim()[0]

            hist.axs.text(position_x_text, position_y_text,
                          r"$\mu = {}\ \sigma = {}$".format(np.round(m, 2),
                                                            np.round(s, 2)),
                          fontsize=10)
            hist.axs.grid(True)
if __name__ == "__main__":
    streamfile = '/home/tsachanowski/Dokumenty/Process.stream'
    RUN = CellExplorer(streamfile)
    RUN = CellExplorer(streamfile, alfa=(80, 90),
                       beta=(80, 90), gamma=(80, 90))
