
from setuptools import setup

setup(
    name='drosolf',
    version='0.1.3',
    packages=['drosolf'],
    scripts=[],
    # TODO replace w/ more modern alternative (move everything to pyproject.toml while
    # at it?)
    setup_requires=['pytest-runner'],
    #
    # importlib.resources is available in stdlib after 3.7, but only has
    # importlib.resources.files I use in >=3.9, so need to use this backport lib
    install_requires=['importlib_resources', 'numpy', 'pandas'],
    tests_require=['pytest'],
    include_package_data=True,
    author="Tom O'Connell",
    author_email='toconnel@caltech.edu',
    license='GPLv3',
    keywords='neuroscience olfaction population coding drosophila',
    url='https://github.com/tom-f-oconnell/drosolf',
    description='Responses of 1st , 2nd, and soon 3rd order Drosophila ' + \
        'olfactory neurons',
    # TODO switch to .md, for consistency w/ other repos, when switching to
    # pyproject.toml
    long_description=open('README.rst').read(),
)
