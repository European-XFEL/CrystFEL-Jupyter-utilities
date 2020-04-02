[![Build Status](https://travis-ci.org/European-XFEL/CrystFEL-Jupyter-utilities.svg?branch=master)](https://travis-ci.org/github/European-XFEL/CrystFEL-Jupyter-utilities)
[![codecov](https://codecov.io/gh/European-XFEL/CrystFEL-Jupyter-utilities/branch/master/graph/badge.svg)](https://codecov.io/gh/European-XFEL/CrystFEL-Jupyter-utilities)
# Description:
CrystFEL-Jupyter-utilities is a project with graphical tools from CrystFEL
implemented in Python. The project is intended to work as a wrapper for
CrystFEL tools when it is not possible to use a graphical environment but
graphical (interactive) features are needed. The tools were written to resemble
original CrystFEL tools while at the same time feature some of the requests
from CrystFEL users. In particular following tools are available:

* hdfsee
* check-peak-detection (script)
* cell_explorer

It is recommended to cite the original CrystFEL papers if one is planning to
refer to the CrystFEL-Jupyter-utilities package:

* T. A. White, V. Mariani, W. Brehm, O. Yefanov, A. Barty, K. R. Beyerlein, F. Chervinskii, L. Galli, C. Gati, T. Nakane, A. Tolstikova, K. Yamashita, C. H. Yoon, K. Diederichs and H. N. Chapman. "Recent developments in CrystFEL". J. Applied Crystallography 49 (2016) p680-689.
* O. Yefanov, V. Mariani, C. Gati, T. A. White, H. N. Chapman and A. Barty. "Accurate determination of segmented X-ray detector geometry". Optics Express 23 (2015) p28459-28470.
* T. A. White. "Post-refinement method for snapshot serial crystallography". Phil. Trans. Roy. Soc. B 369 (2014) 20130330.
* T. A. White, A. Barty, F. Stellato, J. M. Holton, R. A. Kirian, N. A. Zatsepin and H. N. Chapman. "Crystallographic data processing for free-electron laser sources". Acta Cryst. D69 (2013), p1231–1240.
* T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, A. Barty and H. N. Chapman. "CrystFEL: a software suite for snapshot serial crystallography". J. Appl. Cryst. 45 (2012), p335–341.
* R. A. Kirian, X. Wang, U. Weierstall, K. E. Schmidt, J. C. H. Spence, M. Hunter, P. Fromme, T. White, H. N. Chapman and J. Holton. "Femtosecond protein nanocrystallography - data analysis methods". Optics Express 18 (2010) p5713.

## Tools
* Displaying a diffraction image from a h5 file.
* Displaying a diffraction image from a Virtual CXI data file.
* Displaying series of diffraction images with detected peaks using CrystFEL indexing output file.
* Examining the distributions of unit cell parameters in CrystFEL indexing output file.

## Dependencies
`cfelpyutils`  
`h5py`  
`jupyter notebook`  
`matplotlib`  
`numpy`  
`Python >= 3.5`  
`scipy`
## Installing
`git clone <https://github.com/European-XFEL/CrystFEL-Jupyter-utilities.git>`  
`pip install .`  
or  
`python setup.py install`

## Tests
`python -m unittest discover -s CrystFEL_Jupyter_utilities/tests/ -p 'unit_*' -v`  
or  
`python setup.py test`

## Displaying the image
1. Basic displaying of the data as it is:  
   `hdfsee_py <filename>`
2. Displaying the image with geometry reconstruction:  
    `hdfsee_py <filename> -g <geometry file>`  
3. Displaying the image with geometry reconstruction and peaks written in the CrystFEL indexing output file:  
    `hdfsee_py <filename> -g <geometry file> -p <stream file>`
4. Run from code cell in jupyter-notebook:  
   ```
   from CrystFEL_Jupyter_utilities.hdfsee import Image
   %matplotlib notebook
   Image_run = Image(path=<filename>, geomfile=<geometry file>, streamfile=<stream file>)
   ```
## Iterate through images
To display images from the CrystFEL indexing output file:  
`check-peak-detection <stream file> <geometry file>`

**Instructions for running on maxwell cluster**  
#####TODO#####

## Examining the distributions of unit cell parameters
`cell_explorer` tool from CrystFEL has been ported to Python in a form of `CellExplorer` 
class which can be used directly in a Jupyter Notebook and executed with the `cell_explorer_py` 
script.
To select a range of intrerest for gaussian fitting press and hold left mouse button,
release the button after the selection is ready. To deselect click left mouse button
anywhere on the plot. Pressing '+' or '-' changes the binning size by a factor
of 2 (128 -> 64). Pressing 'g' key fitts the gaussian curve to the selected range
and displays fitting parameters.

### Example
1. Run from the command line:  
   `cell_explorer_py <stream file>`
2. Run from code cell in jupyter-notebook:  
   ```
   from CrystFEL_Jupyter_utilities.GUI_tools import CellExplorer
   %matplotlib notebook
   RUN = CellExplorer(<stream file>)
   ```
### Example in jupyter notebook
`CellExplorer_and_H5see_usage.ipynb`
