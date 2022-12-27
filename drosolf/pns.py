
"""
Applies transformation to measured olfactory receptor neuron responses (from
orns), to generate simulated projection neuron responses.

Based on Olsen and Wilson 2010.
"""

from __future__ import division

import numpy as np

from drosolf import orns


# TODO check eq in Parnas against original Olsen & Wilson

# TODO default to returning version with noise added?
# maybe separate function called mean_pns?
# should probably rename to pns.responses or something...
# and at that point, maybe make a class for a cell population and start
# providing a more consistent interface to these things?

def pns(orn=None, model='input gain control', add_noise=False, **kwargs):
    """
    Generates projection neuron responses by applying some model to measured
    olfactory receptor neuron responses.

    Args:
        orn (array-like): (optional) If passed, this array is treated as ORN
        input, instead of the Hallem data returned by drosolf.orns.orns()
        TODO specify the expected dimensions / labels

        model (str, optional): name of the model you would like to use
            options are:
            -'input gain control'
            -'reponse gain control'
            -'no inhibition'
            but so far, only the first is implemented, as that was claimed to be
            the most realistic, in the Olsen paper.

        kwargs: passed thru to drosolf.orns.orns

    Returns:
        a pandas.DataFrame, indexed by odor, with glomerulus (or receptor
        still?) as column name, of the simulated PN responses.
    """
    # TODO convert values that should be convertable in orns.py, and raise error
    # there?
    if orn is None:
        orn = orns.orns(**kwargs)

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
        # TODO check index name on axis 1 matches our expectation / size
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

    # TODO may want to leave to another fn? or only take a # trials?
    # s.t. noise can be included efficiently in many trial case
    if add_noise:
        # Parameters used in Luo 2010, for their (simple) model of Kenyon cell
        # responses.
        # TODO need to check there isn't a better estimate of PN noise
        # properties
        alpha_noise_hz = 0.025
        sigma_noise_hz = 10

        R_pn = R_pn + (sigma_noise_hz * np.tanh(alpha_noise_hz * R_pn) *
            np.random.normal(loc=0.0, scale=1.0, size=R_pn.shape)
        )

    return R_pn


# will this name be an issue once ultrastructural data becomes available?
# what would be most useful for simulations then?
def per_glomerulus():
    """
    """
    raise NotImplementedError

# TODO also functions to subdivide by cholinergic / not?
