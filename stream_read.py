"""
Module for parsing indexing stream file produced by CrystFEL indexamajig.
"""
import sys


def search_crystals_parameters(file_name):
    """Searching crystals parameters in indexing stream file.

    The function parses the file.

    Parameters
    ----------
    file_name : Python unicode str (on py3)
        Path to stream file

    Returns
    -------
    crystals : dict
        Keys as name of the file from which the crystal
        it comes from and values are lists of lines
        containing crystal details.

    Raises
    ------
    FileNotFoundError
        if no such file
    IndexError
        if there is no path to the stream file
    """

    # name_flag- Check if the file has been already processed.
    name_flag = False
    # begin_crystal_flag- Check if the crystal details have begun.
    begin_crystal_flag = False
    # crystal_parameters- Lines from the file regarding a given crystal.
    # Lines between <Begin crystal ; End crystal>
    crystal_parameters = []
    # crystals- Output dictionary to be returned.

    crystals = {}
    stream_name = None
    crystal_counter = 0  # Number of crystals in the histogram.
    chunks_counter = 0  # All crystals in the stream file.
    try:
        stream_name = file_name
    except IndexError:
        print("Enter path to the stream file.")
        sys.exit()
    try:
        with open(stream_name) as file:
            for line in file:
                # When the file name is found.
                if line.startswith("Image filename:"):

                    if not name_flag:
                        name = line
                        name_flag = True
                    else:
                        name = line  # No meaningfull data.
                        name_flag = True
                    #  Count all crystals parametrs.
                    chunks_counter += 1
                if line.startswith("--- Begin crystal"):
                    # After this line following lines contain cryst. info.
                    if ((not begin_crystal_flag) and name_flag):
                        begin_crystal_flag = True
                    else:
                        print("Error: duplicate data.")
                elif (begin_crystal_flag and
                      line.startswith('Reflections measured after indexing')):

                    # Last line with cryst. info.
                    begin_crystal_flag = name_flag = False
                    # If this much lines then it may be error (?).
                    if (len(crystal_parameters) == 13 or
                            len(crystal_parameters) == 14):

                        check_crystal_parametrs(crystal_parameters, name)
                        name = name.strip()  # For multiple names of the same
                        # crystal then such crystal is added with a copy of the
                        # name and a number.
                        copy = 1
                        helpful_name = name
                        while helpful_name in crystals:
                            # It is unknown
                            # how many of the same name crystals are in the
                            # stream so the loops iterates until all names
                            # are processed.
                            helpful_name = name + '-additional'+str(copy)
                            copy += 1
                        crystals[helpful_name] = crystal_parameters
                        # The whole list of data is put into a dictionary where
                        # key is the crystal name.
                    else:
                        check_crystal_parametrs(crystal_parameters, name)
                        print("Not enough" +
                              " data for crystal: {}".format(name.strip()))
                        if "ddunique_axis" in crystal_parameters[5]:
                            print("No centernings")
                        else:
                            print("Unknown error in crystal {}".format(name))
                            sys.exit()
                        # Counts crystals which can be histogramed.
                        crystal_counter += 1
                        # To know where it belongs.
                        latice_type = crystal_parameters[4].strip()
                        if latice_type == "lattice_type = triclinic" or\
                                          latice_type == "lattice_type" +\
                                          " = monoclinic":

                            print(latice_type, "Will have centering type: P\n")
                            # When no centering is found.
                            crystal_parameters.insert(5, 'centering = P\n')
                        else:
                            print("Unknown orientation.")
                            sys.exit()
                        #  In the stream file the crystals of P type (?).
                        name = name.strip()
                        copy = 1  # Multiple names of the same crystal.
                        helpful_name = name
                        while helpful_name in crystals:
                            # Loop ends when
                            # there is no more crystals of the same name.
                            helpful_name = name + '-additional'+str(copy)
                            copy += 1

                        crystals[helpful_name] = crystal_parameters
                    crystal_parameters = []

                elif (begin_crystal_flag and name_flag):
                    # When a crystal is found it is added to the list.
                    # List of lines from 'begin crystal'.
                    crystal_parameters.append(line)
    except FileNotFoundError:
        print("File not found or not a indexing stream file.")
        sys.exit()
    print("Loaded {} cells from {} chunks".format(len(crystals.keys()),
                                                  chunks_counter))
    return crystals


def check_crystal_parametrs(crystal_parameters, name):
    """Checking the data received from indexing stream file.

    Parameters
    ----------
    crystal_parameters : list
        Lines from the file regarding a given crystal
    name : Python unicode str (on py3)
        The name of the file from which the crystal came from
    """

    checks = ["Cell parameters", "astar", "bstar", "cstar", "lattice_type",
              "centering", "unique_axis", "profile_radius",
              "predict_refine/final_residual", "predict_refine/det_shift x",
              "diffraction_resolution_limit", "num_reflections",
              "num_saturated_reflections", "num_implausible_reflections"]
    # do I have enough parameters?
    if len(crystal_parameters) > 14:
        print("Too much data for crystal: {}".format(name))
    elif len(crystal_parameters) >= 13:
        for idx, param in enumerate(crystal_parameters):
            if checks[idx] not in param:
                if checks[idx+1] not in param:
                    print("No {} for {}".format(checks[idx], name))
                    sys.exit()

    elif len(crystal_parameters) == 12:
        if "Cell parameters" not in crystal_parameters[0]:
            print("No Cell parameters for crystal: {}".format(name))
            sys.exit()
        if "astar" not in crystal_parameters[1]:
            print("No astar for crystal: {}".format(name))
            sys.exit()
        if "bstar" not in crystal_parameters[2]:
            print("No bstar for crystal: {}".format(name))
            sys.exit()
        if "cstar" not in crystal_parameters[3]:
            print("No cstar for crystal: {}".format(name))
            sys.exit()
        if "lattice_type" not in crystal_parameters[4]:
            print("No lattice type for crystal: {}".format(name))
            sys.exit()
        index = 7
        if "centering" in crystal_parameters[5]:
            if "unique_axis" not in crystal_parameters[6]:
                print("No unique_axis for crystal: {}".format(name))
                sys.exit()
        elif crystal_parameters[5].startswith("unique_axis"):
            print("No centering for crystal: {}".format(name))
            sys.exit()
        else:
            index = 6
        if "profile_radius" not in crystal_parameters[index]:
            print("No profile_radius for crystal: {}".format(name))
            sys.exit()
        if "predict_refine/det_shift x" not in crystal_parameters[index+1]:
            print("No predict_refine/det_shift x for crystal: {}".format(name))
            sys.exit()
        if "diffraction_resolution_limit" not in crystal_parameters[index+2]:
            print("No diffraction_resolution_limit" +
                  " for crystal: {}".format(name))
            sys.exit()
        if "num_reflections" not in crystal_parameters[index+3]:
            print("No num_reflections for crystal: {}".format(name))
            sys.exit()
        if "num_saturated_reflections" not in crystal_parameters[index+4]:
            print("No num_saturated_reflections for crystal: {}".format(name))
            sys.exit()
        if "num_implausible_reflections" not in crystal_parameters[-1]:
            print("No num_implausible_reflections" +
                  " for crystal: {}".format(name))
            sys.exit()
    else:
        print("Not enough data for crystal: {}".format(name))
        sys.exit()


class PeakSearch:
    """Class for representing a peak  object from the peak search
    in the stream file.

    Attributes
    ----------
    fs_px : double

        fast scan/pixel
    ss_px : double

        slow scan/pixel
    panel_name : str

        the name of the panel to which the peak belongs
    position : tuple

        peak coordinates after panel reconstruction.
    """
    def __init__(self, fs, ss, recip, intesity, panel_name):
        """
        Parameters
        ----------
        fs : double

            fast scan/pixel
        ss : double

            slow scan/pixel
        panel_name : str

            the name of the panel to which the peak belongs
        intesity : double

            Intensity
        recip : double

            value `(1/d)/nm^-1`
        """
        self.fs_px = fs
        self.ss_px = ss
        self.recip = recip
        self.intesity = intesity
        self.panel_name = panel_name
        self.position = None

    def get_position(self):
        """returns peak coordinates
        """
        return self.position


class PeakReflections:
    """Class for representing a peak object from reflections measured
    after indexing in the stream file.

    Attributes
    ----------
    fs_px : double

        fast scan/pixel
    ss_px : double

        slow scan/pixel
    panel_name : str

        the name of the panel to which the peak belongs
    position : tuple

        peak coordinates after panel reconstruction.
    """
    def __init__(self, h, k, l, I, sigmaI, peak, background, fs_px, ss_px,
                 panel_name):
        """
        Parameters
        ----------
        fs_px : double

            fast scan/pixel
        ss_px : double

            slow scan/pixel
        panel_name : str

            the name of the panel to which the peak belongs
        intesity : double

            Intensity
        h : int

            the parameter 'h' of the reflection measured after indexing
        k : int

            the parameter 'k' of the reflection measured after indexing
        l : int

            the parameter 'l' of the reflection measured after indexing
        I : double

            the parameter 'I' of the reflection measured after indexing
        sigmaI : double

            the parameter 'sigma(I)' of the reflection measured
            after indexing
        peak : double

            the parameter 'peak' of the reflection measured
            after indexing
        background : double

            the parameter 'background' of the reflection measured
            after indexing
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
        """
        return self.position


def search_peaks(file_stream, file_h5):
    """Searching peaks in indexing stream file.
    The function parses the file.

    Parameters
    ----------
    file_stream : Python unicode str (on py3)

        Path to stream file
    file_h5 : Python unicode str (on py3)

        Image filename

    Returns
    -------
    peaks_search, peaks_reflection : tuple

        peaks_search and peaks_reflection have
        keys as name of the panel from which the peaks
        belongs from and values are lists of peak object.

    Raises
    ------
    FileNotFoundError
        if no such file
    TypeError
        if the line with the peak parameter contains incomplete data.
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
                    nazwa_h5_z_stream = line3[-1]
                    if nazwa_h5_z_stream in file_h5:
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
