
"""
Functions to generate model Kenyon cell responses.

Note that this was copied from my luo2010 repo, but I could not seem to
reproduce all the figures in their paper, so there may be an error.
Run luo2010.py in that repository to see the discrepancy yourself.
"""

from __future__ import print_function
from __future__ import division


import numpy as np

from drosolf import pns


checks = True

# TODO best to handle state of PN->KC connectivity matrix through class or is it
# cool to just use global variables for that?

'''
class KCPop:
    def __init__(self):
        checks = 
'''

# think about naming conventions here...
# TODO rewrite to allow for distribution, rather than integer n_pns_per_kc
# input, or make two functions
def pn_to_kc_inputs(n_pns_per_kc=5, n_kcs=n_kcs, verbose=False):
    """
    """
    # from methods: "we chose the n synaptic connections for the KCs randomly
    # and drew their weights, denoted by the vector w, from a uniform
    # distribution between 0 and 1."
    # TODO maybe make this connectivity more accurate, using information from
    # subsequent studies?  some stuff that could help exists, right?

    # TODO w/ replacement or not? need diff function to do w/o replacement?
    nonzero_weights = np.random.randint(n_pns, size=(n_kcs, n_pns_per_kc))
    # w in their equations (transposed?)
    pn_to_kc_weights = np.zeros((n_kcs, n_pns))
    #pn_to_kc_weights[nonzero_weights] = np.random.uniform(
    #    size=nonzero_weights.shape)

    # TODO do different trials of theirs only differ with the activity of the
    # PNs, or do they also re-draw the PN inputs to the KCs?

    # Sampling glomeruli WITH REPLACEMENT. Not obvious whether Luo et al. sample
    # with replacement or not.
    counts = dict()
    # TODO how to vectorize this?
    for k in range(n_kcs):
        distinct_pn_inputs = set()
        for i in range(n_pns_per_kc):
            # so that if we same from the same glomerulus twice, we increase the
            # weight
            pn_to_kc_weights[k, nonzero_weights[k,i]] += np.random.uniform()
            distinct_pn_inputs.add(nonzero_weights[k,i])

        if verbose:
            n_distinct_inputs = len(distinct_pn_inputs)
            if n_distinct_inputs in counts:
                counts[n_distinct_inputs] += 1
            else:
                counts[n_distinct_inputs] = 1

    if verbose:
        print('counts:', counts)

    # same?
    '''
    pn_to_kc_weights2 = np.zeros((n_kcs, n_pns))
    for i in range(n_pns_per_kc):
        pn_to_kc_weights2[:, nonzero_weights[:,i]] = 
    '''
    return pn_to_kc_weights


def kc_activations(pns=None, n=None, pn_to_kc_weights=None, inhibition=True, 
                   checks=False):
    """
    Args:
        pns (np.ndarray): (optional) If passed, model KC responses are computed
            with these PN responses. By default, model PNs responses are
            generated with the function pns.pns(add_noise=True)

            TODO say which dimensions / labels are expected

        n (int): The number of PNs each KC will receive input from, each weight
            drawn from the uniform distribution on [0,1). Only pass either this
            or pn_to_kc_weights. If neither is passed, the function behaves as
            if it had n set to 5, as the parameterization used for most of the
            paper.

        pn_to_kc_weights (np.ndarray): The PN to KC weights to use, if
            predefined. Only pass either this or n.

        inhibition (bool): Whether to include their "global" inhibition term
            False should be able to recapitulate S2, when fed through the rest
            of the analysis.

        checks (bool): Whether to check dimensions and some of the identities in
            the supplement.
    """
    if pns is None:
        pns = pns.pns(add_noise=True)

    if pn_to_kc_weights is None:
        if n is None:
            # the value the paper ultimately settled on for most of the figures
            n = 5
        pn_to_kc_weights = pn_to_kc_inputs(n_pns_per_kc=n)
        
    elif not (n is None or pn_to_kc_weights is None):
        raise ValueError('ambiguous. only pass in either n or pn_to_kc_weights')

    # from SI: (.T to indicate transpose, * for matrix multiplication) "the
    # total KC input in our model is I=W.T * r_pn - v * r_in, with r_in the
    # firing rate of one or more globally acting interneurons connected to each
    # KC through a synapse of strength v and driven by PNs through synapses
    # W_in.T so that r_in = W_in.T * r_pn. Defining r_hat = <r_pn> / |<r_pn>|,
    # where the brackets denote an average across odors, we set v = W.T * r_hat
    # and W_in = r_hat. Then,
    # I = W.T * r_pn - v * r_in = W.T * (r_pn - (r_hat.T * r_pn) * r_hat),
    # which removes the projection of the PN rates along the direction of their
    # mean. Note that if we average over all odors,
    # <I> = W.T * <r_pn> - v * <r_in> = 0"
    # TODO is that last consequence (just above) sensible?
    # TODO is this really subtracting first PC?
    # TODO is this model totally linear? (i guess this is all before some
    # threshold?)

    # TODO TODO vectorize to include a trials dimension for these calculations,
    # if possible

    # TODO TODO check dims of pns consistent across luo code this was copied
    # from and drosolf pns code

    odor_averaged_pn_responses = np.mean(pns, axis=1)
    if checks:
        assert len(odor_averaged_pn_responses.shape) == 1
        assert odor_averaged_pn_responses.shape[0] == n_pns

    odor_averaged_pn_responses = np.expand_dims(odor_averaged_pn_responses,
        axis=1)
    #print(odor_averaged_pn_responses)
    #print(odor_averaged_pn_responses.shape)

    # r_hat in their equations
    # TODO is their denominator definitely this norm? probably?
    normalized_pn_responses = (odor_averaged_pn_responses /
        np.linalg.norm(odor_averaged_pn_responses))
    #print('normalized_pn_responses.shape:', normalized_pn_responses.shape)

    # w_in (transposed?) in their equations
    pn_to_inh_weights = normalized_pn_responses
    #print('pn_to_inh_weights.shape:', pn_to_inh_weights.shape)

    # r_in in their equations
    inhibitory_neurons_activation = np.dot(pn_to_inh_weights.T, pns)
    #print('inhibitory_neurons_activation.shape:',
    #    inhibitory_neurons_activation.shape)

    #print('pn_to_kc_weights.shape:', pn_to_kc_weights.shape)
    # v in their equations
    # TODO correct? scalar or not?
    inhibition_strength = np.dot(pn_to_kc_weights, normalized_pn_responses)
    #print('inhibition_strength.shape:', inhibition_strength.shape)

    kc_activation = (np.dot(pn_to_kc_weights, pns) - 
        np.dot(inhibition_strength, inhibitory_neurons_activation))

    if checks:
        # checking this equals their equivalent form, largely to gaurd against
        # having made dimension mismatch errors
        synonym_kc_activation = np.dot(pn_to_kc_weights, (pns -
            np.dot(np.dot(odor_averaged_pn_responses.T, pns).T,
            odor_averaged_pn_responses.T).T))

        print('kc_activation.shape:', kc_activation.shape)
        '''
        print(synonym_kc_activation.shape)

        print(kc_activation[0,:])
        print(synonym_kc_activation[0,:])

        print(kc_activation[-1,:])
        print(synonym_kc_activation[-1,:])
        # TODO recheck above math. identify errors.
        assert np.allclose(kc_activation, synonym_kc_activation)
        '''
        # TODO if this inhibition is not equivalent to "subtracting first PC"
        # then prove it. compute PCs, calculate with that, show different.

        # my original attempt:
        #np.dot(pn_to_kc_weights, (pns -
        #    np.dot(np.dot(odor_averaged_pn_responses.T, pns),
        #    odor_averaged_pn_responses)))

        odor_averaged_kc_activation = np.mean(kc_activation, axis=1)
        assert len(odor_averaged_kc_activation.shape) == 1
        assert odor_averaged_kc_activation.shape[0] == n_kcs
        # their assertion (do algebra to get this consequence)
        assert np.allclose(odor_averaged_kc_activation, 0.0)

    return kc_activation


# TODO make another fn called kc_responses that chains the above with this?
def calc_response_prob(trial_fn=lambda: kc_activations(),
                       simulated_trials=simulated_trials,
                       response_threshold=None):
    """
    Args:
        trial_fn (callable): Each call should return an independent simulated
                             trial. If trial_fn_parameter is None
        simulated_trials (int): number of trials to generate
                                -maybe rename?
        response_threshold (number): 

    Returns:
        
    """
    # was it reasonable to not generate the pn_to_kc_weights here?
    # seems to go hand-in-hand with not being able to control the checks arg
    # here...
    trials = []
    for t in range(simulated_trials):
        if t == 0:
            checks = True
        else:
            checks = False
        trials.append(trial_fn())
    trials = np.stack(trials)

    if response_threshold is None:
        threshold_percentile = 0.95
        # TODO allow suppression
        print('determining inverse-CDF of {} for response threshold...'.format(
            threshold_percentile))
        response_threshold = np.sort(trials.flatten())[
            int(round(threshold_percentile * trials.size))]

        assert np.isclose(np.sum(trials < response_threshold) 
            / trials.size, threshold_percentile)
        assert np.isclose(np.sum(trials >= response_threshold) 
            / trials.size, 1 - threshold_percentile)
        return_none = False

    else:
        # Want to return None for response threshold in this case, to not give
        # the false impression it was calculated in here.
        return_none = True

    response_probability = np.mean(trials > response_threshold, axis=0)
    return response_probability, None if return_none else response_threshold


def responders(response_probability):
    """
    """
    # not measuring the same thing as kc_response_threshold above
    response_criteria = 0.50
    # "we define a neuron as responding if it receives an above-threshold input
    # in at least 50% of trials." "fairly stringent"

    # TODO why was this working with kc_response_probability (a typo), when that
    # variable is not defined until below? true, that variable should exist by
    # the time this function is called... so i guess i misunderstood how
    # Python's scoping works?
    responses_above_criteria = response_probability >= response_criteria
    return responses_above_criteria


def responses_along_axis(responses, axis, expected_size):
    """
    Args:
        responses (array-like): a boolean type array to be checked

        axis (int): axis along which to check for a complete lack of responses

        expected_size (int): for checking result it expected size. somewhat
        tautological / equivalent to checking dimensions of responses.
    """
    assert responses.dtype == np.dtype('bool')
    no_responses = np.logical_not(np.any(responses, axis=axis))
    assert no_responses.size == expected_size
    return np.sum(no_responses)


def missed_odors(responses):
    """
    """
    # TODO use variable for the odor / kc axis?
    return responses_along_axis(responses, 0, n_odors)


def silent_kcs(responses):
    """
    Args:
        responses 
    """
    return responses_along_axis(responses, 1, n_kcs)

