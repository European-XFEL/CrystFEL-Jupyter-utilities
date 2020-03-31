# makefile used for testing

install:
	python3 -m pip install .[test]

dev-install:
	python3 -m pip install -U -e .[test]

test:
	coverage run --source CrystFEL_Jupyter_utilities -m unittest discover -s CrystFEL_Jupyter_utilities/tests/ -p 'unit_*' -v
	coverage report -m