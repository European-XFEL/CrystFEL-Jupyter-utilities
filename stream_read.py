"""
Module for parsing indexing stream file produced by CrystFEL indexamajig.
"""
import sys


def diction_crystal_return(file_name):
    """
    Function returns a parsed indexing stream file as a dictionary with keys
    as name of the crystal from which file it comes from and values are lists
    of lines containing crystal details.

    name_flag = False: Check if the file has been already processed.
    begin_crystal_flag = False: Check if the crystal details have begun.
    begin_crystal = []: Lines from the file regarding a given crystal.
    diction_crystal = {}: Output dictionary to be returned.
    <Begin crystal ; End crystal>
    """
    name_flag = False
    begin_crystal_flag = False
    begin_crystal = []
    diction_crystal = {}
    stream_name = None
    suma = 0  # Number of crystals in the histogram.
    chunks_count = 0  # All crystals in the stream file.
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
                    #  Count all crystals.
                    chunks_count += 1
                if line.startswith("--- Begin crystal"):
                    # After this line following lines contain cryst. info.
                    if ((not begin_crystal_flag) and name_flag):
                        begin_crystal_flag = True
                    else:
                        print("Error: duplicate data.")
                elif line.startswith('Reflections measured after indexing'):
                    # Last line with cryst. info.
                    begin_crystal_flag = name_flag = False
                    # If this much lines then it may be error (?).
                    if len(begin_crystal) == 13:
                        check_list_begin_crystal(begin_crystal, name)
                        name = name.strip()  # For multiple names of the same
                        # crystal then such crystal is added with a copy of the
                        # name and a number.
                        copy = 1
                        name_help = name
                        while name_help in diction_crystal:  # It is unknown
                            # how many of the same name crystals are in the
                            # stream so the loops iterates until all names
                            # are processed.
                            name_help = name + '-additional'+str(copy)
                            copy += 1
                        diction_crystal[name_help] = begin_crystal
                        # The whole list of data is put into a dictionary where
                        # key is the crystal name.
                    else:
                        check_list_begin_crystal(begin_crystal, name)
                        print("Not enough" +
                              " data for crystal: {}".format(name.strip()))
                        if "ddunique_axis" in begin_crystal[5]:
                            print("No centernings")
                        else:
                            print("Unknown error in crystal {}".format(name))
                            sys.exit()
                        suma += 1  # Counts crystals which can be histogramed.
                        # To know where it belongs.
                        latice_type = begin_crystal[4].strip()
                        if latice_type == "lattice_type = triclinic" or\
                                          latice_type == "lattice_type" +\
                                          " = monoclinic":

                            print(latice_type, "Will have centering type: P\n")
                            # When no centering is found.
                            begin_crystal.insert(5, 'centering = P\n')
                        else:
                            print("Unknown orientation.")
                            sys.exit()
                        #  In the stream file the crystals of P type (?).
                        name = name.strip()
                        copy = 1  # Multiple names of the same crystal.
                        name_help = name
                        while name_help in diction_crystal:  # Loop ends when
                            # there is no more crystals of the same name.
                            name_help = name + '-additional'+str(copy)
                            copy += 1

                        diction_crystal[name_help] = begin_crystal
                    begin_crystal = []

                elif (begin_crystal_flag and name_flag):
                    # When a crystal is found it is added to the list.
                    # List of lines from 'begin crystal'.
                    begin_crystal.append(line)
    except FileNotFoundError:
        print("File not found or not a indexing stream file.")
        sys.exit()
    print("Loaded {} cells from {} chunks".format(len(diction_crystal.keys()),
                                                  chunks_count))
    return diction_crystal


def check_list_begin_crystal(crystals, name):
    """
    Checking the data received from indexing stream file.
    """
    if len(crystals) > 13:
        print("Too much data for crystal: {}".format(name))
    elif len(crystals) == 13:
        if "Cell parameters" not in crystals[0]:
            print("No cell parameters for crystal: {}".format(name))
            sys.exit()
        if "astar" not in crystals[1]:
            print("No astar in crystal: {}".format(name))
            sys.exit()
        if "bstar" not in crystals[2]:
            print("No bstar in crystal: {}".format(name))
            sys.exit()
        if "cstar" not in crystals[3]:
            print("No cstar in crystal: {}".format(name))
            sys.exit()
        if "lattice_type" not in crystals[4]:
            print("lattice type for crystal: {}".format(name))
            sys.exit()
        if "centering" not in crystals[5]:
            print("No centerings for crystal: {}".format(name))
            sys.exit()
        if "unique_axis" not in crystals[6]:
            print("No unique axis for crystal: {}".format(name))
            sys.exit()
        if "profile_radius" not in crystals[7]:
            print("No profile radius for crystal: {}".format(name))
            sys.exit()
        if "predict_refine/det_shift x" not in crystals[8]:
            print("No predict_refine/det_shift x for crystal: {}".format(name))
            sys.exit()
        if "diffraction_resolution_limit" not in crystals[9]:
            print("No diffraction_resolution_limit" +
                  " for crystal: {}".format(name))
            sys.exit()
        if "num_reflections" not in crystals[10]:
            print("No diffraction_resolution_limit" +
                  " for crystal: {}".format(name))
            sys.exit()
        if "num_saturated_reflections" not in crystals[11]:
            print("No num_saturated_reflections for crystal: {}".format(name))
            sys.exit()
        if "num_implausible_reflections" not in crystals[12]:
            print("No num_implausible_reflections" +
                  " for crystal: {}".format(name))
            sys.exit()
    elif len(crystals) == 12:
        if "Cell parameters" not in crystals[0]:
            print("No Cell parameters for crystal: {}".format(name))
            sys.exit()
        if "astar" not in crystals[1]:
            print("No astar for crystal: {}".format(name))
            sys.exit()
        if "bstar" not in crystals[2]:
            print("No bstar for crystal: {}".format(name))
            sys.exit()
        if "cstar" not in crystals[3]:
            print("No cstar for crystal: {}".format(name))
            sys.exit()
        if "lattice_type" not in crystals[4]:
            print("No lattice type for crystal: {}".format(name))
            sys.exit()
        index = 7
        if "centering" in crystals[5]:
            if "unique_axis" not in crystals[6]:
                print("No unique_axis for crystal: {}".format(name))
                sys.exit()
        elif crystals[5].startswith("unique_axis"):
            print("No centering for crystal: {}".format(name))
            sys.exit()
        else:
            index = 6
        if "profile_radius" not in crystals[index]:
            print("No profile_radius for crystal: {}".format(name))
            sys.exit()
        if "predict_refine/det_shift x" not in crystals[index+1]:
            print("No predict_refine/det_shift x for crystal: {}".format(name))
            sys.exit()
        if "diffraction_resolution_limit" not in crystals[index+2]:
            print("No diffraction_resolution_limit" +
                  " for crystal: {}".format(name))
            sys.exit()
        if "num_reflections" not in crystals[index+3]:
            print("No num_reflections for crystal: {}".format(name))
            sys.exit()
        if "num_saturated_reflections" not in crystals[index+4]:
            print("No num_saturated_reflections for crystal: {}".format(name))
            sys.exit()
        if "num_implausible_reflections" not in crystals[-1]:
            print("No num_implausible_reflections" +
                  " for crystal: {}".format(name))
            sys.exit()
    else:
        print("Not enough data for crystal: {}".format(name))
        sys.exit()


class Peak_stream():
    """
    Class for representing a peak object from the indexing stream file.
    fs_px/ss_px - column and row positions in the matrix.
    panel_name - panel to which the peak belongs.
    position - peak coordinates after panel reconstruction.
    """
    def __init__(self, fs, ss, recip, intesity, panel_name):
        self.fs_px = fs
        self.ss_px = ss
        self.recip = recip
        self.intesity = intesity
        self.panel_name = panel_name
        self.position = None

    def get_position(self):
        return self.position

    def printer(self):
        """
        Display peak info.
        """
        print("Peak: ", self.panel_name, self.recip, self.intesity)


class Peak_Reflections_measured:
    """
    Class for representing a reflection peak (?) from the indexing lines:
    "Reflections measured after indexing".
    """
    def __init__(self, h, k, l, I, sigmaI, peak, background, fs_px, ss_px,
                 panel_name):
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

    def printer(self):
        """
        Display peak info.
        """
        print("Peak_reflection", self.panel_name, self.background)

    def get_position(self):
        return self.position


def dict_peak_in_name_h5(file_stream, file_h5):
    """
    Function creates a dictionary with keys as panel names and values as
    lists with peaks in a key panel.
    """
    name_h5_flag = False  # Check if already filename was processed.
    found_h5_in_stream = False  # Check if h5 file was
    # processed by indexamajig.
    peaks_from_peak_search = False
    dict_witch_peak_list = {}
    dict_peak_reflections_list = {}
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
                    peak = Peak_stream(fs_px, ss_px, recip, intesity,
                                       panel_name)
                    # Create an object with peak information.
                    if panel_name not in dict_witch_peak_list.keys():
                        dict_witch_peak_list[panel_name] = list()
                        dict_witch_peak_list[panel_name].append(peak)
                    else:
                        dict_witch_peak_list[panel_name].append(peak)
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
                    peak = Peak_Reflections_measured(h, k, l, I, sigmaI, peak,
                                                     background, fs_px,
                                                     ss_px, panel_name)
                    # Create an object.
                    if panel_name not in dict_peak_reflections_list.keys():
                        dict_peak_reflections_list[panel_name] = list()
                        # Dictionary with a panel name as key and near_bragg
                        # peaks as value.
                        dict_peak_reflections_list[panel_name].append(peak)
                    else:
                        dict_peak_reflections_list[panel_name].append(peak)
                if name_h5_flag and line.startswith('   h    k    l  '):
                    # Check for the near_bragg info.
                    reflections_measured_after_indexing_flag = True

    except FileNotFoundError:
        print('Error while opening stream file.')
        dict_peak_reflections_list = {}
        dict_witch_peak_list = {}
        return (dict_witch_peak_list, dict_peak_reflections_list)
    except TypeError:
        dict_peak_reflections_list = {}
        dict_witch_peak_list = {}
        return (dict_witch_peak_list, dict_peak_reflections_list)
    if not found_h5_in_stream:
        print("No peaks for file in the stream file.")

    return (dict_witch_peak_list, dict_peak_reflections_list)
    # In case of error the dictionary is returned empty.
