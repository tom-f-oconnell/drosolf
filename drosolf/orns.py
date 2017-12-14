#!/usr/bin/env python

from __future__ import print_function
import pandas as pd
import numpy as np
import os

# TODO compare to data loaded from the text file from Anne's code
# + where is 176 from in olsen?
def orns(verbose=False):
    # __file__ always work? caller?
    path = os.path.abspath(os.path.dirname(__file__))
    raw_hc = pd.read_csv(os.path.join(path, 'Hallem_Carlson_2006.csv'))
    hc = raw_hc.set_index('odor')[1:].astype(float)

    abs_hc = hc + hc.loc['spontaneous firing rate']

    if verbose:
        print('{} entries negative after adding spontaneous firing rate.'.format(
            np.sum(np.sum(abs_hc.as_matrix() < 0))))

    abs_hc[abs_hc < 0] = 0
    return abs_hc

