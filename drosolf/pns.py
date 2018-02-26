#!/usr/bin/env python

# based on Olsen and Wilson 2010

# TODO best syntax for packaging? i kind of thought "import orns" was supposed
# to work?
#from . import orns
from drosolf import orns
import numpy as np

# TODO check eq in Parnas against original Olsen & Wilson

def pns(model='input gain control'):
    # TODO convert values that should be convertable in orns.py, and raise error there?
    orn = orns.orns()
    # TODO so this isn't set separately for each channel?
    #Rmax = np.amax(orns, axis=1)

    # spikes / sec
    Rmax = 165;
    sigma = 12;
    exponent = 1.5

    if model == 'input gain control':
        m_input_gain = 10.63

        # (for at least VM7 and DL5)
        # "input gain model generated better fits than the response gain model"

        # eq 6 from paper
        # sum across receptor types, should be of dimension = # odors sampled

        # TODO units? mV * s^2 / spikes or inverse? that just the 190?
        # s = m * LFP (4)
        # LFP = sum{i=1, # receptor types}(ORNi) / 190
        # 190?
        s = m_input_gain * np.sum(orn, 1) / 190

        R_orn_pow = np.power(orn, exponent)
        R_pn = Rmax * R_orn_pow / (R_orn_pow.T + sigma**exponent + np.power(s, exponent)).T

    elif model == 'response gain control':
        raise NotImplementedError

    elif model == 'no inhibition':
        raise NotImplementedError

    else:
        raise ValueError()

    return R_pn
