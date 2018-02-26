#!/usr/bin/env bash

sudo -H pip install twine
sudo -H pip install wheel

python setup.py sdist
python setup.py bdist_wheel

# TODO check for pypi information first?
twine upload dist/*
