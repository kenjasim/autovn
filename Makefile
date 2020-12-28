# Set any variables needed for building
VENV_NAME?=build_venv
BIN_NAME?=avn
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3

prepare-install:
	python3 -m pip install virtualenv
	make venv

venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate:
	virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install pyinstaller
	${PYTHON} -m pip install -e .
	touch $(VENV_NAME)/bin/activate

install: venv
	make prepare-install

	${PYTHON} -m PyInstaller ${BIN_NAME}.spec -n ${BIN_NAME} --onefile

	mkdir -p bin
	mv dist/${BIN_NAME} ./bin

	make clean

clean: 
	rm -r build/
	rm -r dist/
	rm -r ${BIN_NAME}.egg-info
	rm -r ${VENV_NAME}/


## REFERENCES
# https://blog.horejsek.com/makefile-with-python/