#!/usr/bin/env python

import orns
import pns
import matplotlib.pyplot as plt
import seaborn as sns

def get_corrs(odor_list):
    """
    """
    R_orn = orns.orns()
    R_pn = pns.pns()
    # transpose so it is odor-odor correlations, not receptor-receptor
    orn_corr = R_orn.T[odor_list].corr()
    pn_corr = R_pn.T[odor_list].corr()
    return orn_corr, pn_corr


def plot_corrs(odor_list):
    """
    """
    orn_corr, pn_corr = get_corrs(odor_list)

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
