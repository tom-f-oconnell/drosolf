#!/usr/bin/env python

"""
Applies transformation to measured olfactory receptor neuron responses (from
orns), to generate simulated projection neuron responses.

Based on Olsen and Wilson 2010.
"""

import numpy as np

from drosolf import orns

# TODO check eq in Parnas against original Olsen & Wilson

def pns(model='input gain control'):
    """
    Generates projection neuron responses by applying some model to measured
    olfactory receptor neuron responses.

    Args:
        model (str, optional): name of the model you would like to use
            options are:
            -'input gain control'
            -'reponse gain control'
            -'no inhibition'
            but so far, only the first is implemented, as that was claimed to be
            the most realistic, in the Olsen paper.

    Returns:
        a pandas.DataFrame, indexed by odor, with glomerulus (or receptor
        still?) as column name, of the simulated PN responses.
    """
    # TODO convert values that should be convertable in orns.py, and raise error
    # there?
    orn = orns.orns()
    # TODO so this isn't set separately for each channel?
    #Rmax = np.amax(orns, axis=1)

    # spikes / sec
    Rmax = 165
    sigma = 12
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
        R_pn = Rmax * R_orn_pow / (R_orn_pow.T + sigma**exponent + \
            np.power(s, exponent)).T

    elif model == 'response gain control':
        raise NotImplementedError

    elif model == 'no inhibition':
        raise NotImplementedError

    else:
        raise ValueError()

    return R_pn
