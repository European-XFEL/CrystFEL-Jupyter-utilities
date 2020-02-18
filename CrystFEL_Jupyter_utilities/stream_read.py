"""Module for parsing indexing stream file produced by CrystFEL indexamajig.
"""
import logging
import sys

import numpy as np

# remove all the handlers.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
LOGGER = logging.getLogger(__name__)
# create console handler with a higher log level
ch = logging.StreamHandler()
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(levelname)s | %(filename)s | %(funcName)s | %(lineno)d | %(message)s\n')
ch.setFormatter(formatter)
# add the handlers to logger
LOGGER.addHandler(ch)
LOGGER.setLevel("INFO")


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
        # Clip (limit) the value.
        cosine = np.clip(cosine, -1, 1)
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
                    if (not flags["begin_crystal"]) and flags["name"]:
                        flags["begin_crystal"] = True
                    else:
                        LOGGER.warning(
                            "Error: duplicate data {}.".format(name))
                elif flags["begin_crystal"]:
                    if "astar" in line:
                        # I found a line `astar`
                        flags["astar"] = True
                        # create list
                        astar = [float(x) for x in line.split(' ')[2:-1]]
                    elif "bstar" in line:
                        # I found a line `bstar`
                        flags["bstar"] = True
                        # creat list
                        bstar = [float(x) for x in line.split(' ')[2:-1]]
                    elif "cstar" in line:
                        # I found a line `bstar`
                        flags["cstar"] = True
                        # create list
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
                        LOGGER.warning("Image {} has bad cell".format(name))
                    else:
                        a, b, c, alfa, beta, gamma = cell_parameters(
                            astar, bstar, cstar)
                        if not (flags["lattice_type"] and
                                flags["centering"] and flags["unique_axis"]):
                            # if I do not have `lattice_type` ,`centering`
                            # or `unique_axis`then
                            # I keep the default (`triclinic` `P` , `?`)
                            LOGGER.warning(
                                "{} keep default triclinic P".format(name))
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
        LOGGER.critical("Wrong path to the stream file.")
        sys.exit(1)
    except IndexError:
        LOGGER.critical("Enter path to the stream file.")
        sys.exit(1)
    except FileNotFoundError:
        LOGGER.critical("File not found or not a indexing stream file.")
        sys.exit(1)
    LOGGER.info(
        "Loaded {} cells from {} chunks".format(len(crystals), chunks_counter))
    return crystals


def search_peaks(file_stream, file_h5):
    """Searching peaks in indexing stream file.
    The function parses the file.

    Parameters
    ----------
    file_stream : Python unicode str (on py3)

        Path to stream file.
    file_h5 : Python unicode str (on py3)

        Image filename.

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
                if line.startswith("Image filename:"):
                    # a h5 filename.
                    line = line.strip()  # Remove whitespace.
                    line2 = line.split(' ')
                    # Parsing to have Image and filename.
                    line3 = line2[2].split('/')
                    # Parsing to leave only the filename.
                    name_h5_stream = line3[-1]
                    if name_h5_stream in file_h5:
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
                    fs_px = float(line2[0])  # Fast scan/pixel.
                    ss_px = float(line2[1])  # Slow scan/pixel.
                    recip = float(line2[2])  # Value `(1/d)/nm^-1`.
                    intensity = float(line2[3])  # Intensity
                    # The name of the panel to which the peak belongs.
                    panel_name = line2[4]
                    # dictionary representing peak data
                    # from the peak search in the stream file.
                    peak = {'fs_px': fs_px, 'ss_px': ss_px, 'recip': recip,
                            'intensity': intensity, 'panel_name': panel_name,
                            'position': None}
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
                    # The parameter 'h'
                    # of the reflection measured after indexing.
                    h = int(line2[0])
                    # The parameter 'k'
                    # of the reflection measured after indexing.
                    k = int(line2[1])
                    # The parameter 'l'
                    # of the reflection measured after indexing.
                    l_ = int(line2[2])
                    # The parameter 'I'
                    # of the reflection measured after indexing.
                    I_ = float(line2[3])
                    # The parameter 'sigma(I)'
                    # of the reflection measured after indexing.
                    sigmaI = float(line2[4])
                    # The parameter 'peak'
                    # of the reflection measured after indexing.
                    peak = float(line2[5])
                    # The parameter 'background'
                    # of the reflection measured after indexing.
                    background = float(line2[6])
                    fs_px = float(line2[7])  # Fast scan/pixel.
                    ss_px = float(line2[8])  # Slow scan/pixel.
                    # The name of the panel to which the peak belongs.
                    panel_name = line2[9]
                    # dictionary representing peak data from the reflections
                    # measured after indexing in the stream file.
                    peak = {'h': h, 'k': k, 'l': l_, 'I': I_, 'sigmaI': sigmaI,
                            'peak': peak, 'background': background,
                            'fs_px': fs_px, 'ss_px': ss_px,
                            'panel_name': panel_name, 'position': None}
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
        LOGGER.warning('Error while opening stream file.')
        peaks_reflection = {}
        peaks_search = {}
        return peaks_search, peaks_reflection
    except TypeError:
        peaks_reflection = {}
        peaks_search = {}
        return peaks_search, peaks_reflection
    if not found_h5_in_stream:
        LOGGER.warning("No peaks for file in the stream file.")
    return peaks_search, peaks_reflection
    # In case of error the dictionary is returned empty.
