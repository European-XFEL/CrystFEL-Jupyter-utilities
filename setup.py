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
    match = re.search(r'^__version__ = "(\d+\.\d+\.\d+)"', vers_file, re.M)
    if match is not None:
        return match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='CrystFEL_Jupyter_utilities',
      version=find_version("CrystFEL_Jupyter_utilities", "__init__.py"),
      author="European XFEL GmbH, National Centre for Nuclear Research",
      author_email="da-support@xfel.eu",
      url="https://github.com/European-XFEL/CrystFEL-Jupyter-utilities",
      long_description=read("README.md"),
      long_description_content_type='text/markdown',
      license="BSD-3-Clause",
      packages=find_packages(),
      scripts=['scripts/check-peak-detection'],
      entry_points={
          "console_scripts": [
              "hdfsee_py = CrystFEL_Jupyter_utilities.hdfsee:main",
              "cell_explorer_py = CrystFEL_Jupyter_utilities.GUI_tools:main"
          ],
      },
      install_requires=[
          'cfelpyutils>=0.92',
          'h5py>=2.7.1',
          'matplotlib',
          'numpy',
          'scipy',
      ],
      extras_require={
          'docs': [
              'ipython',
          ],
          'test': [
              'coverage<5',
          ]
      },
      python_requires='>=3.5',
      classifiers=[
          'Development Status :: 1 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Scientific/Engineering :: Physics',
      ])
