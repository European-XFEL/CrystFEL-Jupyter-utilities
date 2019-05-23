from matplotlib.widgets import Button
import matplotlib.pyplot as plt


class PeakButton(Button):
    """A GUI button used in hadsee to visible others peaks in image

    Attributes
    ----------
    fig : The class:`matplotlib.figure.Figure`.

        The Figure which will be redraw
    axs : The class:`matplotlib.axes.Axes`

        The Axes contains most of the figure elements
    axis_list : list

        position button in figure(object matplotlib.pyplot.axis)
    list_active_peak : list

        flags with peaks are enabled/disabled
    detectors : dict

        object class Panel with peaks
    peaks -  list

        objects Peak (form h5 file)
    title : Python unicode str (on py3)

        title image
    radio : object form widget/Radio

    slider : objet form widget/My_slider

    matrix : numpy.array object

        data with pixels
    """
    def __init__(self, fig, axs, matrix, ax, label, axis_list,
                 list_active_peak, peaks, detectors, title, radio, slider):
        """
        Parameters
        ----------
        fig : The class:`matplotlib.figure.Figure`.

            The Figure which will be redraw
        axs : The class:`matplotlib.axes.Axes`

            The Axes contains most of the figure elements
        matrix : numpy.array object

            data with pixels
        ax : The :class:`matplotlib.axes.Axes`

            instance the button will be placed into.
        label : Python unicode str (on py3)

            button name.
        axis_list : list

            position button in figure(object matplotlib.pyplot.axis)
        list_active_peak : list

            flags with peaks are enabled/disabled
        detectors : dict

            object class Panel with peaks
        peaks -  list

            objects Peak (form h5 file)
        title : Python unicode str (on py3)

            title image
        radio : object form widget/Radio

        slider : objet form widget/My_slider


        """
        self.fig = fig
        self.axs = axs
        self.matrix = matrix

        self.ax = ax
        self.axis_list = axis_list
        self.list_active_peak = list_active_peak
        self.peaks = peaks
        self.detectors = detectors
        self.title = title
        self.radio = radio
        self.slider = slider
        # Initialize parent constructor.
        super(PeakButton, self).__init__(ax=self.ax, label=label)
        # On click reaction.
        super(PeakButton, self).on_clicked(self.peaks_on_of)

    def visual_peaks_reflection(self):
        """Draw peaks reflections measured after indexing
        from stream file. Like as script near_bragg.
        """
        # set flag peaks_near_bragg are enabled
        self.list_active_peak[2] = True
        # loop through all detectors
        for name in self.detectors:
            # loop through all peaks near_bragg
            for peak in self.detectors[name].get_peaks_reflection():
                circle = plt.Circle(peak.get_position(), radius=5, color='r',
                                    fill=False)
                # draw red circle
                self.axs.add_artist(circle)

    def visual_peaks_search(self):
        """
        Draw peaks  form peaks search from stream file.
        Like check_peak_detection script.
        """
        # set flag peaks_list are enabledd
        self.list_active_peak[1] = True
        # loop through all detectors
        for name in self.detectors:
            # loop through all peaks list
            for peak in self.detectors[name].get_peaks_search():
                circle = plt.Circle(peak.get_position(), radius=5, color='g',
                                    fill=False)
                # draw red circle
                self.axs.add_artist(circle)

    def visual_peaks(self):
        """Draw peaks form dataset in h5 file 'cheetah peakinfo-assembled'
        """
        try:
            # loop through all peaks list
            for peak in self.peaks:
                circle = plt.Circle(peak.get_position(), radius=5,
                                    color='y', fill=False)
                # draw yellow circle
                self.axs.add_artist(circle)
        except TypeError:
            # exception when we can find peak in dataset
            return None

    def peaks_on_of(self, event):
        """React at the click of buttons.
        Clear and create clean image. Checks which flags were active
        and changes the flags due to the button being clicked.
        """
        # clear subplot
        self.axs.cla()
        # returned color map last used
        cmap = self.radio.get_cmap()
        # retuned contrast range last used
        vmax = self.slider.get_vmax()
        vmin = self.slider.get_vmin()
        # created new image we have a new reference
        image = self.axs.imshow(self.matrix, cmap=cmap, vmax=vmax,
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

            # other was enabled and draw or diasbled and don't draw
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
                # 'CrystFEL_near_bragg_peak on/off' and change flags was enabled 
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
        self.axs.set_title(self.title)
        # set a new reference in the widgets
        self.radio.set_image(image)
        self.slider.set_image(image)
