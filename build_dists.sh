#!/usr/bin/env bash

# These two pip commands used to be prefixed with 'sudo -H'
pip install twine
pip install wheel

python setup.py sdist
python setup.py bdist_wheel

# TODO check for pypi information first?
twine upload dist/*

