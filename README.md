# Description:
H5see is a project with graphical tools from CrystFEL implemented in Python.
The project is intended to work as a wrapper for CrystFEL tools when it is not
possible to use a graphical environment but graphical (interactive) features
are needed. The tools were written to resemble original CrystFEL tools while
at the same time feature some of the requests from CrystFEL users.
In particular following tools are available:

* hdfsee
* check-peak-detection.sh (script)
* cell_explorer

Is is recommended to cite the original CrystFEL papers if one is planning to refer to the h5see package:

* T. A. White, V. Mariani, W. Brehm, O. Yefanov, A. Barty, K. R. Beyerlein, F. Chervinskii, L. Galli, C. Gati, T. Nakane, A. Tolstikova, K. Yamashita, C. H. Yoon, K. Diederichs and H. N. Chapman. "Recent developments in CrystFEL". J. Applied Crystallography 49 (2016) p680-689.
* O. Yefanov, V. Mariani, C. Gati, T. A. White, H. N. Chapman and A. Barty. "Accurate determination of segmented X-ray detector geometry". Optics Express 23 (2015) p28459-28470.
* T. A. White. "Post-refinement method for snapshot serial crystallography". Phil. Trans. Roy. Soc. B 369 (2014) 20130330.
* T. A. White, A. Barty, F. Stellato, J. M. Holton, R. A. Kirian, N. A. Zatsepin and H. N. Chapman. "Crystallographic data processing for free-electron laser sources". Acta Cryst. D69 (2013), p1231–1240.
* T. A. White, R. A. Kirian, A. V. Martin, A. Aquila, K. Nass, A. Barty and H. N. Chapman. "CrystFEL: a software suite for snapshot serial crystallography". J. Appl. Cryst. 45 (2012), p335–341.
* R. A. Kirian, X. Wang, U. Weierstall, K. E. Schmidt, J. C. H. Spence, M. Hunter, P. Fromme, T. White, H. N. Chapman and J. Holton. "Femtosecond protein nanocrystallography - data analysis methods". Optics Express 18 (2010) p5713.

## Tools
* hdfsee.py - for displaying a diffraction image from a h5 file.  
* GUI_tools.py - displaying histograms from a indexing.stream file (produced by indexamajig) and fitting gaussian curves.

## Dependencies
`cfelpyutils`  
`h5py`  
`jupyter notebook`  
`matplotlib`  
`numpy`  
`Python >= 3.5`  
`scipy`
## Installing
`git clone` <https://github.com/European-XFEL/CrystFEL-Jupyter-utilities.git>  
`python setup.py install`

## Tests
`python -m unittest discover -s CrystFEL_Jupyter_utilities/tests/ -p 'unit_*' -v`  
or  
`python setup.py test`

## hdfsee.py usage
The tool is designed to work with h5 files (hdf5). Tested only with LCLS specific data structure <http://www.cxidb.org/data/21/cxidb-21-run0130.tar>
Features buttons for changing contrast and colour space, displaying diffraction peaks from indexing.stream file or peaks embedded in the h5 file.

### Example usage
1. Basic displaynig of the data as it is:  
   `python hdfsee_run.py <filename>`
2. Displaying the image with geometry reconstruction:  
    `python hdfsee_run.py <filename> -g <geometry file>`  
3. Displaying the image with geometry reconstruction and peaks written in the indexing.stream file produced by indexamajig:  
    `python hdfsee_run.py <filename> -g <geometry file> -p <stream file>`
4. Run from code cell in jupyter-notebook:  
   ```
   from CrystFEL_Jupyter_utilities.hdfsee import Image
   %matplotlib notebook
   RUN = Image(path=<hdf5 file>, geomfile=<geometry file>, streamfile=<stream file>)
   ```
## check-peak-detection.sh
`./check-peak-detection.sh <stream file> <geometry file>`

**Instructions for running on maxwell cluster**  
#####TODO#####

## GUI_tools.py usage
GUI_tools.py is a `cell_explorer` tool from CrystFEL ported to Python.
To select a range of intrerest for gaussian fitting press and hold left mouse button,
release the button after the selection is ready. To deselect click left mouse button
anywhere on the plot. Pressing '+' or '-' changes the binning size by a factor
of 2 (128 -> 64). Pressing 'g' key fitts the gaussian curve to the selected range
and displays fitting parameters.

### Example
1. Run from the command line:  
   `python cell_explorer_run.py <stream file>`
2. Run from code cell in jupyter-notebook:  
   ```
   from CrystFEL_Jupyter_utilities.GUI_tools import CellExplorer
   %matplotlib notebook
   RUN = CellExplorer(<stream file>)
   ```
### Example in jupyter notebook
`magic-cell_explorer_and_hdfsee.ipynb`
