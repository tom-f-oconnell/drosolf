#!/usr/bin/env python

import pandas as pd
import numpy as np

# TODO compare to data loaded from the text file from Anne's code
# + where is 176 from in olsen?
def orns(verbose=False):
    hc = pd.read_csv('Hallem_Carlson_2006.csv').set_index('odor')[1:].astype(float)

    abs_hc = hc + hc.loc['spontaneous firing rate']

    if verbose:
        print '{} entries negative after adding spontaneous firing rate.'.format(
            np.sum(np.sum(abs_hc.as_matrix() < 0)))

    abs_hc[abs_hc < 0] = 0

    return abs_hc

