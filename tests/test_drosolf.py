#!/usr/bin/env python3

import pandas
from drosolf import orns
from drosolf import pns

def check_dataframe(df):
    """
    Checks object:
    -is a DataFrame
    -is two dimensional
    -neither dimensional is only zero or one
    """
    assert type(df) == pandas.DataFrame
    assert len(df.shape) == 2 and df.shape[0] > 1 and df.shape[1] > 1

def test_orns():
    orn_responses = orns.orns()
    check_dataframe(orn_responses)

def test_pns():
    pn_responses = pns.pns()
    check_dataframe(pn_responses)
