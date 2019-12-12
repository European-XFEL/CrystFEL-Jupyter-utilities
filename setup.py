import os.path as osp
from setuptools import setup, find_packages
import sys
import re


def get_script_path():
    return osp.dirname(osp.realpath(sys.argv[0]))


def read(*parts):
    return open(osp.join(get_script_path(), *parts)).read()


def find_version(*parts):
    vers_file = read(*parts)
    match = re.search(r'^__version__ = "(\d+\.\d+)"', vers_file, re.M)
    if match is not None:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name='CrystFEL_Jupyter_utilities',
      version=find_version("CrystFEL_Jupyter_utilities","__init__.py"),
      url="https://github.com/European-XFEL/CrystFEL-Jupyter-utilities",
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      license="BSD-3-Clause",
      packages=find_packages(),
      scripts=['scripts/cell_explorer_run.py', 'scripts/hdfsee_run.py', 'scripts/check-peak-detection.sh'],
      install_requires=[
          'cfelpyutils>=0.92',
          'h5py>=2.7.1',
          'matplotlib',
          'numpy',
          'scipy',
      ],

      python_requires='>=3.5',
)