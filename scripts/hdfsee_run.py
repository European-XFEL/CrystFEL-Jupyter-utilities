#!/usr/bin/env python
"""Module for running code from the console.
"""
# Module for parsing command line arguments had to be moved here to
# avoid displaying the same image all over again in jupyter notebook.
import argparse

from CrystFEL_Jupyter_utilities.hdfsee import Image, LOGGER

if __name__ == "__main__":

    # Creating arguments for parsing.
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs=1, metavar="name.H5",
                        help='Display this image.')
    parser.add_argument('-g', "--geomfile", nargs=1, metavar='name.GEOM',
                        help='Use geometry from file' +
                        ' to display arrangment panels')
    parser.add_argument('-p', '--peaks', nargs=1, metavar='name.STREAM',
                        help='use to display peaks' +
                        ' from stream is used only witch geom')
    # Parsing command line arguments.
    args = parser.parse_args()
    # Variable for running mode.
    # Variable for filename.
    path = args.filename[0]
    if args.geomfile:
        # Check if the geometry file was provided.
        geomfile = args.geomfile[0]
        if args.peaks:
            streamfile = args.peaks[0]
        else:
            # Only the geometry file was provided.
            streamfile = None
    # Image file without geometry.
    else:
        if args.peaks:
            LOGGER.warning(
                'Displaying panels without geometry reconstruction.')
        streamfile = None
        geomfile = None

    IMAGE = Image(path=path, geomfile=geomfile, streamfile=streamfile)
