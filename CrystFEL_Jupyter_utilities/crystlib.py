"""Module for getting crystals info from input indexing stream file.
"""


def crystal_search(crystals, histogram_type):
    """Creating a dictionary of values list ​​divided into centering
    types for a given histogram type.

    Parameters
    ----------
    crystals : list

        A list of crystal.
    histogram_type :  unicode str (on py3)

        Type of histogram e.g. 'a', 'gamma'.

    Returns
    -------
    crystal_dict : dict

        A dict of values lists
        key- type centering
        value - list
    """
    crystal_dict = {}
    for crystal in crystals:
        crystal_dict.setdefault(crystal['centering'], []).append(
            crystal[histogram_type])
    return crystal_dict


def histograms_data(crystal_list):
    """Creating a dictionary with data for each histogram. Each value is a
    dictionary divided into centering types.

    Parameters
    ----------
    crystal_list : list

        A list of crystal

    Returns
    -------
    dict_data : dict

        A dict with data
        key- histogram order e.g. 'a', 'beta'
        value - dict
    """
    cryst = crystal_list  # Crystals list
    histogram_order = ['a', 'b', 'c', 'alfa', 'beta', 'gamma']
    dict_data = {key: crystal_search(cryst, key) for key in histogram_order}
    return dict_data
