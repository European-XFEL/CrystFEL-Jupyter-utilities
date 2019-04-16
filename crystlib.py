"""
Module for getting crystals info from input indexing stream file.
"""

from stream_read import search_crystals_parameters


def crystals_list(file_name):
    """Creat a list of all crystal from a stream file.

    Parameters
    ----------

    file_name: Python unicode str (on py3)
        Path to stream file

    Returns
    -------
    crystals: list
        A list of crystal
    """
    diction_crystal = search_crystals_parameters(file_name)
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
        if len(diction_crystal[key]) == 13:
            i = 0
        else:
            i = 1
        diffraction_resolution_limit =\
            float(diction_crystal[key][i+9].split(' ')[-2])
        num_reflections = int(diction_crystal[key][i+10].split(' ')[-1])
        num_saturated_reflections =\
            int(diction_crystal[key][i+11].split(' ')[-1])
        num_implausible_reflections =\
            int(diction_crystal[key][i+12].split(' ')[-1])
        # crystal details as parameters.

        crystal = {'name': name, 'a': a, 'b': b, 'c': c,
                   'alfa': alfa, 'beta': beta, 'gamma': gamma,
                   'astar': astar, 'bstar': bstar,
                   'cstar': cstar, 'lattice_type': lattice_type,
                   'centering': centering, 'num_reflections': num_reflections,
                   'diffraction_resolution_limit': diffraction_resolution_limit,
                   'num_saturated_reflections': num_saturated_reflections,
                   'num_implausible_reflections': num_implausible_reflections}

        crystals.append(crystal)

    return crystals


def crystal_search(crystals, histogram_type):
    """Creating a dictionary of values list ​​divided into centering
    types for a given histogram type

    Parameters
    ----------

        crystals: list
           A list of crystal
        histogram_type:  unicode str (on py3)
            Type of histogram e.g. 'a', 'gamma'

    Returns
    -------
    crystal_dict: dict
        A dict of values lists
        key- type centering
        value - list
    """
    crystal_dict = {}
    for crystal in crystals:
        crystal_dict.setdefault(crystal['centering'],
                                []).append(crystal[histogram_type])
    return crystal_dict


def dict_data_histogram(crystal_list):
    """Creating a dictionary with data for each histogram. Each value is a
    dictionary divided into centering types.

    Parameters
    ----------

        crystals: list
           A list of crystal

    Returns
    -------
    dict_data: dict
        A dict with data
        key- histogram order e.g. 'a', 'beta'
        value - dict

    """
    cryst = crystal_list  # Crystals list
    histogram_order = ['a', 'b', 'c', 'alfa', 'beta', 'gamma']
    dict_data = {key: crystal_search(cryst, key)
                 for key in histogram_order}
    return dict_data
