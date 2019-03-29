"""
This module depicts peaks on the panels
gets the poles connection matrix from the h5 file,
all peaks are kept in the list
"""


class Peak:
    """
    Peak representation from the file h5
    (processing/cheetah/peakinfo-assembled)
    posx - the peak position according to the origin system in the center of Ox
    posy - the peak position according to the origin system in the center of Ox
    """
    def __init__(self, posx, posy, intensive, offset):
        self.posx = posx
        self.posy = posy
        self.intensive = intensive
        self.offset = offset

    def get_position(self):
        return (self.posx, self.posy)


def get_list_peaks(matrix, image_size):
    """
    return a list of class Peak form H5
    gets a matrix with data for all peas given
    file h5

    """
    try:
        # array[:,] next rows
        peaks = [Peak(posx=(row[0] + image_size[1]/2.0), posy=(-row[1] +
                 image_size[0]/2.0),
                 intensive=row[2], offset=row[3]) for row in matrix[:, ]]

        return peaks
    except IndexError:
        print("peaks error")
