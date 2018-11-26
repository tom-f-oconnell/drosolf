#!/usr/bin/env python3

"""
Extracts data from the tables in Grabe et al. 2017, and formats them as CSVs for
the Python package.
"""

from __future__ import print_function
from __future__ import division


import numpy as np
import tabula


# TODO get rid of header rows before calling this?
def split_females_males(column):
    def split(s, female=True):
        print(s)
        if s == 'GH146 negative':
            return np.nan

        try:
            parts = s.split()
        except AttributeError:
            return np.nan

        print(parts)
        # TODO just set a slice object as the kwarg?
        # what's the syntax for that?
        if female:
            return ' '.join(parts[:2])
        else:
            return ' '.join(parts[2:])

    def female_data(s):
        return split(s)

    def male_data(s):
        return split(s, female=False)

    female_col = column.apply(female_data)
    male_col = column.apply(male_data)
    
    # TODO possible to insert columns by index?
    # TODO maybe return a dict w/ col names?
    return female_col, male_col


def fillnan(df):
    nanvalues = {'-', 'GH146 negative'}
    # TODO better way?
    # TODO need to strip whitespace first?
    df.loc[df.isin(nanvalues)] = np.nan
    

def split_mean_sd(df, columns):
    # TODO find all columns that are a mean +/- sd
    # could do from
    def mean(x):
        return float(x.split()[0])
    
    def sd(x):
        # TODO maybe just use regex to get part in parens
        return float(x.split()[1].replace('(','').replace(')',''))

    for c in columns:
        df['mean_' + c] = df[c].apply(mean)
        df['sd_' + c] = df[c].apply(sd)

    df.drop(columns=columns, inplace=True)


# TODO under table s2, they save see excel file... is all of this data in a
# spreadsheet already?
pdf = '../data/pdfs/grabe_et_al_2016.pdf'

# TODO maybe force this to start a little lower on the screen, so it gets 10
# columns instead of 7? (or give it other priors on # of cols, etc)
s1_a = tabula.read_pdf(pdf, pages=17)
s1_b = tabula.read_pdf(pdf, pages=18)

joined_male_female_cols = \
    ['Unnamed: 3', 'In vivo glomerular volume', 'Unnamed: 5']

for c in joined_male_female_cols:
    fc, mc = split_females_males(s1_a[c])

# TODO maybe make m/f another column?
# TODO maybe just rename the columns that wont be split here?
s1_columns = [
    'glomerulus', 'sensillum', 'receptor',
    'mean_n_orns_females', 'sd_n_orns_females',
    'mean_n_orns_males', 'sd_n_orns_males',
    'mean_glomerular_vol_females', 'sd_glomerular_vol_females',
    'mean_glomerular_vol_males', 'sd_glomerular_vol_males',
    'mean_n_pns_females', 'sd_n_pns_females',
    'mean_n_pns_males', 'sd_n_pns_males',
    'lifetime_sparseness'
]

# TODO how to handle those 15^a things in the middle of the OSN columns?
# what are those?

# s1_a.iloc[0:4] are all header info / nan


# TODO need to push columns of s1_b down into data before changing cols

import ipdb; ipdb.set_trace()

s2 = tabula.read_pdf(pdf, pages=18)

