#!/usr/bin/env python3

import pandas as pd

from drosolf import orns
from drosolf import pns


def check_dataframe(df):
    """
    Checks object:
    -is a DataFrame
    -is two dimensional
    -neither dimensional is only zero or one
    """
    assert type(df) == pd.DataFrame
    assert len(df.shape) == 2 and df.shape[0] > 1 and df.shape[1] > 1
    # TODO may need to change if i process only the supplemental subset separately?
    # (110 if no SFR, 111 otherwise)
    assert len(df) >= 110, f'{len(df)=}'
    assert df.index.name == 'odor'


def test_orns():
    df = orns.orns()
    check_dataframe(df)
    # TODO add tests where it's glomerulus too?
    assert df.columns.name == 'receptor'


def test_pns():
    df = pns.pns()
    check_dataframe(df)
    assert df.columns.name == 'receptor'


def test_receptor2glomeruli_match_task22():
    # TODO TODO is this complete? run/test more code in scripts/task*?
    # TODO move code into here, to make more explicit? or used elsewhere too?
    orns._check_csv_data()
