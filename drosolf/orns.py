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
def orns(verbose=False):
    """
    Args:
        verbose (bool) (optional, default=False): prints extra debugging
            information if true

    Returns:
        pandas.DataFrame with odors as one column, and olfactory receptors as
        remaining columns. The entries are firing rates above or below baseline,
        with the exception of the "spontaneous firing rate" row, which can be
        added to the rows with odors to recover the absolute firing rate.
    """
    # __file__ always work? caller?
    path = os.path.abspath(os.path.dirname(__file__))
    raw_hc = pd.read_csv(os.path.join(path, 'Hallem_Carlson_2006.csv'))
    odor_indexed_hc = raw_hc.set_index('odor')[1:].astype(float)

    abs_hc = odor_indexed_hc + odor_indexed_hc.loc['spontaneous firing rate']

    if verbose:
        print('{} entries negative after adding spontaneous firing ' + \
            'rate.'.format(np.sum(np.sum(abs_hc.as_matrix() < 0))))

    abs_hc[abs_hc < 0] = 0
    return abs_hc

