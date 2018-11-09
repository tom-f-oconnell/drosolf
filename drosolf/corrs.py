#!/usr/bin/env python

import orns
import pns
import matplotlib.pyplot as plt
import seaborn as sns

def get_corrs(*args):
    """
    """
    if len(args) > 1:
        raise \
            ValueError('must pass list of odor names or call with no arguments')

    elif len(args) == 1:
        odor_list = args[0]

    else:
        # TODO provide function in orns to exclude spontaneous
        odor_list = [x for x in orns.orns().index
                     if x != 'spontaneous firing rate']

    R_orn = orns.orns()
    R_pn = pns.pns()
    # transpose so it is odor-odor correlations, not receptor-receptor
    orn_corr = R_orn.T[odor_list].corr()
    pn_corr = R_pn.T[odor_list].corr()
    return orn_corr, pn_corr


def plot_corrs(*args):
    """
    """
    orn_corr, pn_corr = get_corrs(*args)

    fig1 = plt.figure()
    '''
    plt.matshow(orn_corr)
    plt.colorbar()
    '''
    sns.heatmap(orn_corr)
    plt.title('ORNs')

    fig2 = plt.figure()
    '''
    plt.matshow(pn_corr)
    plt.colorbar()
    '''
    sns.heatmap(pn_corr)
    plt.title('PNs')

    #return fig1, fig2
