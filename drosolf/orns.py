
"""
For loading Hallem & Carlson olfactory receptor neuron responses, in a
pandas.DataFrame.
"""

from __future__ import print_function

import os

import numpy as np
import pandas as pd


_path = os.path.abspath(os.path.dirname(__file__))
# TODO get missing glomeruli (that currently parse to "Unnamed X") to
# parses to NaN? (would then have to change handling that expected "unnamed")
raw_hc = pd.read_csv(os.path.join(_path, 'Hallem_Carlson_2006.csv'))

_SPONTANEOUS_FIRING_RATE_COLUMN = 'spontaneous firing rate'

# TODO compare to data loaded from the text file from Anne's code
# + where is 176 from in olsen?
# (i now know that one row from Anne's version of the data should be wrong. one
# of those acids...)
def orns(add_sfr=True, drop_sfr=True, verbose=False):
    """
    Args:
        add_sfr (bool): (optional, default=True) Whether spontaneous firing rate
            should be added to each measured change, to recover absolute
            odor-evoked firing rates.

        drop_sfr (bool): (optional, default=True) If False, the spontaneous
            firing rates will be returned alongside the odor data.

        verbose (bool) (optional, default=False): Prints extra debugging
            information if True.

    Returns:
        pandas.DataFrame with odors as one column, and olfactory receptors as
        remaining columns. The entries are firing rates above or below baseline,
        with the exception of the "spontaneous firing rate" row, which can be
        added to the rows with odors to recover the absolute firing rate.
    """
    global raw_hc

    # TODO better way to set column index?
    raw_hc.columns = raw_hc.iloc[0].fillna('cas_number')

    # TODO what was the 1: intended to exclude?
    odor_indexed_hc = raw_hc.set_index('odor')[1:]

    # Just to set all values besides cas_numbers to float in one go.
    cas_col = odor_indexed_hc['cas_number']
    odor_indexed_hc = odor_indexed_hc.drop(columns=['cas_number']).astype(float)
    #odor_indexed_hc['cas_number'] = cas_col

    # TODO TODO i think i do want to keep the entries of all columns as floats,
    # so think about whether / where / how I want to provide name translation
    # (or just fn to get float part?) (?)
    def real_valued_part(df):
        return df[df.columns[df.dtypes == 'float64']]

    ret = odor_indexed_hc

    if add_sfr:
        abs_hc = (real_valued_part(odor_indexed_hc) + 
            odor_indexed_hc.loc[_SPONTANEOUS_FIRING_RATE_COLUMN]
        )

        if verbose:
            print(('{} entries negative after adding spontaneous firing ' +
                'rate.').format(
                np.sum(np.sum(real_valued_part(abs_hc).as_matrix() < 0))
            ))

        # TODO TODO float part here too... (?)
        abs_hc[abs_hc < 0] = 0
        ret = abs_hc

    if drop_sfr:
        ret.drop(_SPONTANEOUS_FIRING_RATE_COLUMN, inplace=True)

    # TODO maybe factor chem id conversion natural_odors wraps arong this fn
    # (which uses chemutils) into here, calling if chemutils is found?
    # TODO plus the hallem grouping into chemical classes that
    # natural_odors/odors.py adds

    ret.columns.name = 'receptor'

    return ret


# TODO helper functions with more verbose names wrapping various combinations of
# flags to function above?


def nonpheromone_orns(**kwargs):
    """Wraps orns(), with same kwargs, removing the data from the putatitive
    pheromone receptors exluded in Luo et al. 2010 for their Kenyon cell
    and lateral horn modelling.

    Excluded:
    - Or33b
    - Or47b
    - Or65a
    - Or88a

    Have Luo et al's claims that these receptors are pheromone receptors been
    substantiated? If not, or if the list requires revision, maybe rename this
    to something indicating connection to that paper.
    """
    r_orns = orns(**kwargs)

    pheromone_receptors = {'33b', '47b', '65a', '88a'}
    r_orns.drop(r_orns.columns[r_orns.columns.isin(pheromone_receptors)],
        axis=1, inplace=True
    )

    # TODO maybe assert only decreasing column dimension by size of set
    
    return r_orns


def receptors2glomeruli(as_series=False):
    """Returns dict with receptors as keys, and the glomeruli their ORNs project
    to as values. Some receptors will map to None, as they were not listed with
    a glomerulus in the Hallem and Carlson data.
    """
    # TODO is this correspondence completely described now?
    global raw_hc

    glom2receptor = raw_hc.iloc[0]

    receptor2glom = dict()
    for glom, receptor in raw_hc.iloc[0].dropna()[1:].iteritems():
        if glom.startswith('Unnamed: '):
            receptor2glom[receptor] = None
        else:
            receptor2glom[receptor] = glom

    if as_series:
        series = pd.Series(receptor2glom)
        series.name = 'glomeruli'
        series.index.name = 'receptor'
        return series
    else:
        return receptor2glom


receptor2glomerulus_dict = None
def receptor2glomerulus(receptor):
    """Takes a string receptor name and returns glomerulus that expressing ORNs
    project to. Returns None if this glomerulus is unknown.
    """
    global receptor2glomerulus_dict
    # TODO test this works
    if receptor2glomerulus_dict is None:
        receptor2glomerulus_dict = receptors2glomeruli()

    return receptor2glomerulus_dict[receptor]


# TODO just return melted df w/ two id_vars cols, one for glomeruli and one for
# receptors?
def per_glomerulus():
    """
    """
    raise NotImplementedError
    

# TODO include means of translating between receptors and glomerulus
# or include config file / some configuration setting idiom like (.set_style())
# where user can specify which index they prefer? could add a flag to each
# function, but i'd prefer not to. could also just require user to index their
# own dataframes.

