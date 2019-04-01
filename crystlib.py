"""
Module for getting crystals info from input indexin stream file.
"""

from stream_read import diction_crystal_return
# From the stream file return a dictionary with each crystal as key and
# crystal details as parameters.


class Crystal():
    """
    Object representing a crystall from indexamajig (CrystFEL) output file.
    Includes a, b, c, alpha, beta, gamma values needed for drawing histograms.
    """

    def __init__(self, name, a, b, c, alfa, beta, gamma, astar, bstar,
                 cstar, lattice_type, centering, diffraction_resolution_limit,
                 num_reflections,
                 num_saturated_reflections,
                 num_implausible_reflections):
        self.name = name
        self.a = a
        self.b = b
        self.c = c
        self.alfa = alfa
        self.beta = beta
        self.gamma = gamma
        self.astar = astar
        self.bstar = bstar
        self.cstar = cstar
        self.lattice_type = lattice_type
        self.centering = centering
        self.histogram_order = ['a', 'b', 'c', 'alfa', 'beta', 'gamma']
        self.histogram_data = [a, b, c, alfa, beta, gamma]
        self.crystals_dict = {key_1: key_2 for key_1,
                              key_2 in zip(self.histogram_order, self.histogram_data)}
        # The other parameters may be needed later.

        self.diffraction_resolution_limit = diffraction_resolution_limit
        self.num_reflections = num_reflections
        self.num_saturated_reflections = num_saturated_reflections
        self.num_implausible_reflections = num_implausible_reflections


def crystals_list(file_name):
    """
    Function for creating a list of all crystal objects from a stream file.
    """
    diction_crystal = diction_crystal_return(file_name)
    crystals = []
    for key in diction_crystal:
        name = key.split(' ')[2]
        cell_parameters = diction_crystal[key][0].split(' ')
        a = float(cell_parameters[2])*10  # Multiplying by 10 for Angstroms.
        b = float(cell_parameters[3])*10
        c = float(cell_parameters[4])*10
        alfa = float(cell_parameters[6])
        beta = float(cell_parameters[7])
        gamma = float(cell_parameters[8])
        astar = [float(x) for x in diction_crystal[key][1].split(' ')[2:-1]]
        bstar = [float(x) for x in diction_crystal[key][2].split(' ')[2:-1]]
        cstar = [float(x) for x in diction_crystal[key][3].split(' ')[2:-1]]
        lattice_type = diction_crystal[key][4].split(' ')[2]
        centering = diction_crystal[key][5].strip().split(' ')[2]
        diffraction_resolution_limit =\
            float(diction_crystal[key][9].split(' ')[-2])
        num_reflections = int(diction_crystal[key][10].split(' ')[-1])
        num_saturated_reflections =\
            int(diction_crystal[key][11].split(' ')[-1])
        num_implausible_reflections =\
            int(diction_crystal[key][12].split(' ')[-1])
        # Crystal class constructor.
        crystal = Crystal(name, a, b, c, alfa, beta, gamma, astar, bstar,
                          cstar, lattice_type, centering,
                          diffraction_resolution_limit,
                          num_reflections,
                          num_saturated_reflections,
                          num_implausible_reflections)

        crystals.append(crystal)

    return crystals


def crystal_search(crystals, crystal_type):
    crystal_dict = {}
    for crystal in crystals:
        try:
            crystal_dict[crystal['centering']].append(crystal[crystal_type])
        except KeyError:
            crystal_dict[crystal['centering']] = [crystal[crystal_type]]
    return crystal_dict

def dict_data_histogram(crystal_list):
    """
    Creating a dictionary with data for each histogram. Each value is a
    dictionary divided into centering types.
    """
    cryst = crystal_list  # Crystals list
    histogram_order = ['a', 'b', 'c', 'alfa', 'beta', 'gamma']
    dict_data = {key: crystal_search(cryst, key)
                 for key in histogram_order}
    return dict_data
