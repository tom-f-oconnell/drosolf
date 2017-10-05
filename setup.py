
from setuptools import setup

setup(
    # TODO why is this CamelCase in all examples I've seen?
    name='drosolf',
    version='0.1',
    packages=['drosolf'],
    scripts=[],
    install_requires=['numpy', 'pandas'],
    # TODO what does this do?
    package_data={
        'drosolf': ['Hallem_Carlson_2006.txt']
    },
    author="Tom O'Connell",
    author_email='toconnel@caltech.edu',
    license='GPLv3',
    keywords='neuroscience olfaction population coding drosophila',
    url='https://github.com/tom-f-oconnell/drosolf',
    # TODO long + short description
)

