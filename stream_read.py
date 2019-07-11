"""Module for parsing indexing stream file produced by CrystFEL indexamajig.
"""
import numpy as np
import sys


def cell_parameters(astar, bstar, cstar):
    """Calculates unit cell parameters.

    Parameters
    ----------
    astar : list

        List of float values.
        (A line beginning with `astar`)
    bstar : list

        List of float values.
        (A line beginning with `bstar`)
    cstar : list

        List of float values.
        (A line beginning with `cstar`)

    Returns
    -------
    a, b, c, alfa, beta, gamma : tuple

        Unit cell parameters.
    """

    def angle_between(x1, x2):
        """Auxiliary function for calculating the angle between vectors.

        Parameters
        ----------
        x1 : numpy.ndarray

            First vector.
        x2 : numpy.ndarray

            Second vector.

        Returns
        -------
        Angle in degrees.
        """
        # magnitude of a vector x1
        mod1 = np.linalg.norm(x1)
        # magnitude of a vector x2
        mod2 = np.linalg.norm(x2)
        cosine = (np.sum(x1*x2)) / (mod1*mod2)
        if (cosine > 1.0):
            cosine = 1.0
        if (cosine < -1.0):
            cosine = -1.0

        # angle in degrees
        return np.rad2deg(np.arccos(cosine))

    # Convert reciprocal -> crystallographic.
    # Start by converting reciprocal -> cartesian
    array = np.transpose(np.array([astar, bstar, cstar]))
    # inverse matrix
    array = np.linalg.inv(array)

    # magnitude of a vector
    # Multiplying by 10 for Angstroms.
    a = np.linalg.norm(array[0, :]) * 10
    b = np.linalg.norm(array[1, :]) * 10
    c = np.linalg.norm(array[2, :]) * 10
    # angle between vectors
    alpha = angle_between(array[1, :], array[2, :])
    beta = angle_between(array[0, :], array[2, :])
    gamma = angle_between(array[0, :], array[1, :])

    return a, b, c, alpha, beta, gamma


def search_crystals_parameters(file_name):
    """Searching crystals parameters in indexing stream file.

    The function parses the file.

    Parameters
    ----------
    file_name : Python unicode str (on py3)

        Path to stream file.

    Returns
    -------
    crystals : list

        List of crystals dictionaries
        containing  unit cell details.

    Raises
    ------
    FileNotFoundError
        If no such file.
    IndexError
        If there is no path to the stream file.
    """
    # flags- Check if the line has already been processed.
    flags = {"name": False, "begin_crystal": False,
             "astar": False, "bstar": False, "cstar": False,
             "lattice_type": False, "centering": False,
             "unique_axis": False}

    # crystals: Output list of crystals dictionaries
    # containing  unit cell details.
    crystals = []
    chunks_counter = 0  # All crystals in the stream file.
    # line with the event
    # ( some stream files do not contain these lines)
    event_name = ""

    try:
        with open(file_name) as file:
            for line in file:
                # When the file name is found.
                if "Image filename:" in line:

                    if not flags["name"]:
                        name = line
                        flags["name"] = True
                    else:
                        name = line  # No meaningfull data.
                        flags["name"] = True
                    #  Count all crystals parametrs.
                    chunks_counter += 1
                # When the event name is found.
                if flags["name"] and "Event: " in line:
                    event_name = line
                if "--- Begin crystal" in line:

                    name = name.strip('\n')
                    name += event_name.strip('\n')
                    # After this line following lines contain cryst. info.
                    if ((not flags["begin_crystal"]) and flags["name"]):
                        flags["begin_crystal"] = True
                    else:
                        print("Error: duplicate data.")
                        print(name)
                elif flags["begin_crystal"]:
                    if "astar" in line:
                        # I found a line `astar`
                        flags["astar"] = True
                        # creat list
                        astar = [float(x) for x in line.split(' ')[2:-1]]
                    elif "bstar" in line:
                        # I found a line `bstar`
                        flags["bstar"] = True
                        # creat list
                        bstar = [float(x) for x in line.split(' ')[2:-1]]
                    elif "cstar" in line:
                        # I found a line `bstar`
                        flags["cstar"] = True
                        # creat list
                        cstar = [float(x) for x in line.split(' ')[2:-1]]
                    elif "lattice_type" in line:
                        # I found a line `lattice_type`
                        flags["lattice_type"] = True
                        lattice_type = line.strip().split(' ')[2]
                    elif "centering" in line:
                        # I found a line `centering`
                        flags["centering"] = True
                        centering = line.strip().split(' ')[2]
                    elif "unique_axis" in line:
                        # I found a line `unique_axis`
                        flags["unique_axis"] = True
                        unique_axis = line.strip().split(' ')[2]

                if "--- End crystal" in line:
                        # the end line of cryst. info.
                    # We need `astar`, `bstar` and `cstar`
                    # to calculate unit cell parameters
                    if not(flags["astar"] or flags["bstar"] or flags["cstar"]):
                        print("Image {} has bad cell".format(name))
                    else:
                        a, b, c, alfa, beta, gamma =\
                            cell_parameters(astar, bstar, cstar)
                        if not (flags["lattice_type"] and
                                flags["centering"] and flags["unique_axis"]):

                            # if I do not have `lattice_type` ,`centering`
                            # or `unique_axis`then
                            # I keep the default (`triclinic` `P` , `?`)
                            print("{} keep default triclinic P".format(name))
                            lattice_type = "triclinic"
                            centering = "P"
                            unique_axis = "?"

                        crystal = {'name': name, 'a': a, 'b': b, 'c': c,
                                   'alfa': alfa, 'beta': beta,
                                   'gamma': gamma, 'centering': centering,
                                   'lattice_type': lattice_type,
                                   'unique_axis': unique_axis}
                        crystals.append(crystal)
                        # reset event_name
                        event_name = ""
                        # reset flags
                        for key in flags.keys():
                            flags[key] = False
    except TypeError:
        print("Wrong path to the stream file.")
        sys.exit()
    except IndexError:
        print("Enter path to the stream file.")
        sys.exit()
    except FileNotFoundError:
        print("File not found or not a indexing stream file.")
        sys.exit()
    print("Loaded {} cells from {} chunks".format(len(crystals),
                                                  chunks_counter))
    return crystals


class PeakSearch:
    """Class for representing a peak  object from the peak search
    in the stream file.

    Attributes
    ----------
    fs_px : double

        Fast scan/pixel.
    ss_px : double

        Slow scan/pixel.
    panel_name : str

        The name of the panel to which the peak belongs.
    position : tuple

        Peak coordinates after panel reconstruction.
    """
    def __init__(self, fs, ss, recip, intesity, panel_name):
        """
        Parameters
        ----------
        fs : double

            Fast scan/pixel.
        ss : double

            Slow scan/pixel.
        panel_name : str

            The name of the panel to which the peak belongs.
        intesity : double

            Intensity.
        recip : double

            Value `(1/d)/nm^-1`.
        """
        self.fs_px = fs
        self.ss_px = ss
        self.recip = recip
        self.intesity = intesity
        self.panel_name = panel_name
        self.position = None

    def get_position(self):
        """Returns peak coordinates.
        Returns
        -------
        position : tuple

            Peak position.
        """
        return self.position


class PeakReflections:
    """Class for representing a peak object from reflections measured
    after indexing in the stream file.

    Attributes
    ----------
    fs_px : double

        Fast scan/pixel.
    ss_px : double

        Slow scan/pixel.
    panel_name : str

        The name of the panel to which the peak belongs.
    position : tuple

        Peak coordinates after panel reconstruction.
    """
    def __init__(self, h, k, l, I, sigmaI, peak, background, fs_px, ss_px,
                 panel_name):
        """
        Parameters
        ----------
        fs_px : double

            Fast scan/pixel.
        ss_px : double

            Slow scan/pixel.
        panel_name : str

            The name of the panel to which the peak belongs.
        h : int

            The parameter 'h' of the reflection measured after indexing.
        k : int

            The parameter 'k' of the reflection measured after indexing.
        l : int

            The parameter 'l' of the reflection measured after indexing.
        I : double

            The parameter 'I' of the reflection measured after indexing.
        sigmaI : double

            Rhe parameter 'sigma(I)' of the reflection measured
            after indexing.
        peak : double

            The parameter 'peak' of the reflection measured
            after indexing.
        background : double

            The parameter 'background' of the reflection measured
            after indexing.
        """
        self.h = h
        self.k = k
        self.l = l
        self.I = I
        self.sigmaI = sigmaI
        self.peak = peak
        self.background = background
        self.fs_px = fs_px
        self.ss_px = ss_px
        self.panel_name = panel_name
        self.position = None

    def get_position(self):
        """returns peak coordinates
        Returns
        -------
        position : tuple

            Peak position.
        """
        return self.position


def search_peaks(file_stream, line_name, look_for):
    """Searching peaks in indexing stream file.
    The function parses the file.

    Parameters
    ----------
    file_stream : Python unicode str (on py3)

        Path to stream file.
    line_name : Python unicode str (on py3)

        The name I am looking for:
        `Image filename` or `Event number`.
    look_for : Python unicode str (on py3)

        The line in which I am looking.
        `Image filename: ` or `Event:`
    Returns
    -------
    peaks_search, peaks_reflection : tuple

        Peaks_search and peaks_reflection have
        keys as name of the panel from which the peaks
        belongs from and values are lists of peak object.

    Raises
    ------
    FileNotFoundError
        If no such file.
    TypeError
        If the line with the peak parameter contains incomplete data.
    """
    name_h5_flag = False  # Check if already filename was processed.
    found_h5_in_stream = False  # Check if h5 file was
    # processed by indexamajig.
    peaks_from_peak_search = False
    peaks_search = {}
    peaks_reflection = {}
    reflections_measured_after_indexing_flag = False  # If this line was found
    # with data for near bragg

    try:
        with open(file_stream) as file:
            for line in file:
                
                # Check if line contains
                if line.startswith(look_for):
                    # a h5 filename.
                    line = line.strip()  # Remove whitespace.
                    # Parsing to have Image and filename.
                    line2 = line.split('/')
                    # Parsing to leave only the filename.
                    name_found_line = line2[-1]
                    if name_found_line == line_name:
                        name_h5_flag = True  # If it is a name witha filename.
                        found_h5_in_stream = True
                    else:
                        name_h5_flag = False
                if name_h5_flag and line.startswith('End of peak list'):
                    #  Last line with the peaks.
                    peaks_from_peak_search = False
                elif peaks_from_peak_search:
                    # Check if lines still contain peak info.
                    line2 = line.strip().split(' ')  # Dividing to columns.
                    while '' in line2:
                        line2.remove('')  # Remove empty chars.
                    fs_px = float(line2[0])  # Get data for peaks.
                    ss_px = float(line2[1])
                    recip = float(line2[2])
                    intesity = float(line2[3])
                    panel_name = line2[4]
                    peak = PeakSearch(fs_px, ss_px, recip, intesity,
                                      panel_name)
                    # Create an object with peak information.
                    if panel_name not in peaks_search.keys():
                        peaks_search[panel_name] = list()
                        peaks_search[panel_name].append(peak)
                    else:
                        peaks_search[panel_name].append(peak)
                if name_h5_flag and line.startswith('  fs/px   ss/px' +
                                                    ' (1/d)/nm^-1   ' +
                                                    'Intensity  Panel'):
                    # Check for the peak beginning line.
                    peaks_from_peak_search = True

                if name_h5_flag and line.startswith('End of reflections'):
                    # Check for the last line.
                    reflections_measured_after_indexing_flag = False
                elif reflections_measured_after_indexing_flag:
                    line2 = line.strip().split(' ')  # Splitting to columns.
                    while '' in line2:
                        line2.remove('')  # Remove empty chars.
                    h = int(line2[0])
                    k = int(line2[1])
                    l = int(line2[2])
                    I = float(line2[3])
                    sigmaI = float(line2[4])
                    peak = float(line2[5])
                    background = float(line2[6])
                    fs_px = float(line2[7])
                    ss_px = float(line2[8])
                    panel_name = line2[9]
                    peak = PeakReflections(h, k, l, I, sigmaI, peak,
                                           background, fs_px,
                                           ss_px, panel_name)
                    # Create an object.
                    if panel_name not in peaks_reflection.keys():
                        peaks_reflection[panel_name] = list()
                        # Dictionary with a panel name as key and near_bragg
                        # peaks as value.
                        peaks_reflection[panel_name].append(peak)
                    else:
                        peaks_reflection[panel_name].append(peak)
                if name_h5_flag and line.startswith('   h    k    l  '):
                    # Check for the near_bragg info.
                    reflections_measured_after_indexing_flag = True

    except FileNotFoundError:
        print('Error while opening stream file.')
        peaks_reflection = {}
        peaks_search = {}
        return (peaks_search, peaks_reflection)
    except TypeError:
        peaks_reflection = {}
        peaks_search = {}
        return (peaks_search, peaks_reflection)
    if not found_h5_in_stream:
        print("No peaks for file in the stream file.")

    return (peaks_search, peaks_reflection)
    # In case of error the dictionary is returned empty.
