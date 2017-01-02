VERSION=`./setup.py --version`
FILE_EXISTS:=$(wildcard install.record)
ifeq ($(strip $(FILE_EXISTS)),)
    UNINSTALL_FILES:=
else
    UNINSTALL_FILES:=$(shell cat install.record)
endif
 

help:
	@echo "Local Build"
	@echo "  build     : build the python package."
	@echo "  install   : install the python package into /usr/local."
	@echo "  uninstall : uninstall the python package from /usr/local."
	@echo "Pypi package"
	@echo "  register  : register the package with PyPI."
	@echo "  distro    : build the distribution tarball."
	@echo "  pypi      : upload the package to PyPI."
	@echo "Deb package"
	@echo "  deb_deps  : install the package builder dependencies (stdeb)."
	@echo "  source_deb: source packaging (for ppas)"
	@echo "  deb       : build the deb."
	@echo "Other"
	@echo "  clean     : clean build/dist directories."

build:
	python setup.py build

deb_deps:
	echo "Downloading dependencies"
	sudo apt-get install python-stdeb

clean_dist:
	-rm -f MANIFEST
	-rm -rf build dist
	-rm -rf deb_dist
	-rm -rf debian
	-rm -rf ../*.build
	-rm -rf *.tar.gz

source_package:
	python setup.py sdist

# Another install method that might be better:
#       sudo checkinstall python setup.py install
install: source_package
	python setup.py install --record install.record

uninstall:
	rm -f ${UNINSTALL_FILES}

source_deb:
	rm -rf dist deb_dist
	python setup.py --command-packages=stdeb.command sdist_dsc

deb:
	rm -rf dist deb_dist
	python setup.py --command-packages=stdeb.command bdist_deb

register:
	python setup.py register

pypi: 
	python setup.py sdist upload

clean:  clean_dist
	-sudo rm -f install.record
	-sudo rm -rf build
	-sudo rm -rf ckx_tools.egg-info

