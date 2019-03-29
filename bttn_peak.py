from matplotlib.widgets import Button
import matplotlib.pyplot as plt


class Bttn_peak(Button):
    """
    class used in hadsee to visible others peaks in image
    fig - object of the Figuge class used to redraw
    axs - is object subplot(Axes objects)
    axis - position button in figure(object matplotlib.pyplot.axis)
    label - the name of the button
    axis_list - list all position button used to peaks
                (list object matplotlib.pyplot.axis)
    list_active_peak - list flags with peaks are enabled/disabled
    detectors - diction all panels with peaks
    peaks - peaks form h5 file
    title - title image
    radio - object form widget/Radio
    slider - objet form widget/My_slider
    matrix - data with pixels
    """
    def __init__(self, fig, axs, matrix, ax, label, axis_list,
                 list_active_peak, peaks, detectors, title, radio, slider):
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
        super(Bttn_peak, self).__init__(ax=self.ax, label=label)
        # On click reaction.
        super(Bttn_peak, self).on_clicked(self.peaks_on_of)

    def visual_peaks_near_bragg_from_stream(self):
        """
        draw peaks like as script near_bragg from stream
        under line  'Reflections measured after indexing'
        """
        # set flag peaks_near_bragg are enabled
        self.list_active_peak[2] = True
        # loop through all detectors
        for name in self.detectors:
            # loop through all peaks near_bragg
            for peak in self.detectors[name].get_peak_near_bragg_list():
                circle = plt.Circle(peak.get_position(), radius=5, color='r',
                                    fill=False)
                # draw red circle
                self.axs.add_artist(circle)

    def visual_peaks_from_stream(self):
        """
        Draw peaks like check_peak_detection script
        from stream file under line Peaks 'from peak search'
        """
        # set flag peaks_list are enabledd
        self.list_active_peak[1] = True
        # loop through all detectors
        for name in self.detectors:
            # loop through all peaks list
            for peak in self.detectors[name].get_peak_list():
                circle = plt.Circle(peak.get_position(), radius=5, color='g',
                                    fill=False)
                # draw red circle
                self.axs.add_artist(circle)

    def visual_peaks(self):
        """
        draw peaks form dataset in h5 file 'cheetah peakinfo-assembled'
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
        """
        clear and create clean image
        checks which flags were active
        and changes the flags due to the button being pressed
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
                self.visual_peaks_from_stream()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_near_bragg_from_stream()

        # when we clicked button 'CrystFEL_peak on/off'
        if event.inaxes == self.axis_list[1]:
            if self.list_active_peak[0]:
                # 'cheetah peaks on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_near_bragg_from_stream()
            if self.list_active_peak[1]:
                # 'CrystFEL_peak on/off' was enabled and change flags
                # we don't draw
                self.list_active_peak[1] = False
            else:
                # 'CrystFEL_peak on/off' was disabled and change flags
                # we draw
                self.list_active_peak[1] = True
                self.visual_peaks_from_stream()

        # when we clicked button 'CrystFEL_near_bragg_peak on/off'
        if event.inaxes == self.axis_list[2]:
            if self.list_active_peak[0]:
                # 'cheetah peaks on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks()
            if self.list_active_peak[1]:
                # 'CrystFEL_peak on/off' was enabled
                # and draw we don't change flags
                self.visual_peaks_from_stream()
            if self.list_active_peak[2]:
                # 'CrystFEL_near_bragg_peak on/off' and change flags was enabled 
                # we don't draw
                self.list_active_peak[2] = False
            else:
                # 'CrystFEL_near_bragg_peak on/off' was disabled 
                # and change flags
                # we don't draw
                self.list_active_peak[2] = True
                self.visual_peaks_near_bragg_from_stream()
        # Redraw the current figure.
        self.fig.canvas.draw()
        # set title because we clear subplot axs
        self.axs.set_title(self.title)
        # set a new reference in the widgets
        self.radio.set_image(image)
        self.slider.set_image(image)
