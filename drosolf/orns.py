#!/usr/bin/env python

"""
For loading Hallem & Carlson olfactory receptor neuron responses, in a
pandas.DataFrame.
"""

from __future__ import print_function

import os

import numpy as np
import pandas as pd

# TODO compare to data loaded from the text file from Anne's code
# + where is 176 from in olsen?
def orns(add_spontaneous=True, return_spontaneous=False, verbose=False):
    """
    Args:
        add_spontaneous (bool): (optional, default=True) whether spontaneous
            firing rate should be added to each measured change, to recover true
            firing rates.
        return_spontaneous (bool): (optional, default=False)
        verbose (bool) (optional, default=False): prints extra debugging
            information if true

    Returns:
        pandas.DataFrame with odors as one column, and olfactory receptors as
        remaining columns. The entries are firing rates above or below baseline,
        with the exception of the "spontaneous firing rate" row, which can be
        added to the rows with odors to recover the absolute firing rate.

        If add_spontaneous is return
    """
    # __file__ always work? caller?
    path = os.path.abspath(os.path.dirname(__file__))
    raw_hc = pd.read_csv(os.path.join(path, 'Hallem_Carlson_2006.csv'))
    odor_indexed_hc = raw_hc.set_index('odor')[1:].astype(float)

    if add_spontaneous:
        abs_hc = (odor_indexed_hc + 
                  odor_indexed_hc.loc['spontaneous firing rate'])

        if verbose:
            print('{} entries negative after adding spontaneous firing ' + \
                'rate.'.format(np.sum(np.sum(abs_hc.as_matrix() < 0))))

        abs_hc[abs_hc < 0] = 0
        return abs_hc

    else:
        return odor_indexed_hc

# helper functions with more verbose names wrapping various combinations of
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
    # TODO 
    
    return orn_responses

