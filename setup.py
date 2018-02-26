
from setuptools import setup

setup(
    name='drosolf',
    version='0.1.2',
    packages=['drosolf'],
    scripts=[],
    setup_requires=['pytest-runner'],
    install_requires=['numpy', 'pandas'],
    tests_require=['pytest'],
    include_package_data=True,
    author="Tom O'Connell",
    author_email='toconnel@caltech.edu',
    license='GPLv3',
    keywords='neuroscience olfaction population coding drosophila',
    url='https://github.com/tom-f-oconnell/drosolf',
    description='Responses of 1st , 2nd, and soon 3rd order Drosophila ' + \
        'olfactory neurons',
    long_description=open('README.rst').read(),
)
