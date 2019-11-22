"""Module to run the program from the console.
Parse a command line.
"""
# !/usr/bin/env python
import argparse
from CrystFEL_Jupyter_utilities.GUI_tools import CellExplorer

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('filename', nargs=1, metavar="name.stream",
                        help="Download data from this file")
    ARGS = PARSER.parse_args()
    streamfile = ARGS.filename[0]
    Run = CellExplorer(streamfile)
