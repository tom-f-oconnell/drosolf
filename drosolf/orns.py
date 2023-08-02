
"""
For loading Hallem & Carlson olfactory receptor neuron responses.
"""

from typing import List, Optional

from pathlib import Path

import numpy as np
import pandas as pd


# TODO delete this note + hc_data.csv (though if it's the only soure of data w/ lower
# conc stuff, maybe just replace Hallem_Carlson_2006.csv with it?
# TODO TODO add support for loading that supplemental data (lowers concs, fruits, etc),
# probably w/ kwarg to enable also loading it
# TODO add kwarg (maybe default to True) for appending ' @ -2' to odor names
# TODO kwarg to drop 33b data? anyting else (2a)

# NOTE on differences between Hallem_Carlson_2006.csv and hc_data.csv:
# Hallem_Carlson_2006.csv:
# - no glomerulus listed for 33b
#   - hc_data.csv lists DM3, w/ "DM3.1" for 47a. this CSV lists "DM3" for 47a.
# - no glomerulus listed for 47b
#   - hc_data.csv lists 'VM5d' for for 85b. both agree on 98a->VM5v
# - doesn't have the lower concentration / fruit data from the other table
# TODO TODO TODO where was that other csv getting VM5d (and what does task 22 say?)

# TODO move to __init__.py or something?
data_dir = Path('../data').resolve()

hallem_csv_name = 'Hallem_Carlson_2006.csv'

_script_dir = Path(__file__).resolve().parent
hallem_csv_path = _script_dir / hallem_csv_name

# TODO or do i also want to define location of this relative to orns.py, rather than
# data_dir? if so, could move data_dir back into task22.py
task_csv = data_dir / 'task22_table3.csv'

n_hallem_receptors = 24
glomerulus2receptor = {
    'DA3': '23a',
    'DA4l': '43a',
    'DA4m': '2a',
    'DC1': '19a',
    'DL1': '10a',
    'DL3': '65a',
    'DL4': '85f',
    'DL5': '7a',
    'DM2': '22a',

    # NOTE: this receptor goes to both DM3 and DM5. Its responses in Hallem are smaller
    # and less specific than either of the other receptors for those glomeruli.
    # Ann/Matt both drop 33b in their modelling. Matt does so inside olfsysm, so any use
    # of Hallem data loaded by olfsysm should handle it. Setting ORN data manually (e.g.
    # to add odors) will need to replicate this.
    'DM3+DM5': '33b',

    'DM3': '47a',
    'DM4': '59b',
    # NOTE: DoOR says this also gets input from 85a
    'DM5': '85a',
    'DM6': '67a',
    'VA1d': '88a',
    'VA1v': '47b',
    'VA5': '49b',
    'VA6': '82a',
    'VC3': '35a',
    'VC4': '67c',
    'VM2': '43b',
    'VM3': '9a',
    'VM5d': '85b',
    'VM5v': '98a',
}
assert len(glomerulus2receptor) == n_hallem_receptors

def _read_hallem_csv(**kwargs):
    # after usecols (1 odor name index column + receptor columns) is a CAS column I
    # don't want
    df = pd.read_csv(hallem_csv_path, index_col='odor',
        usecols=range(1 + n_hallem_receptors), **kwargs
    )
    df.columns.name = 'receptor'
    return df


# TODO where is 176 from in olsen? (?)
_raw_hallem_df = None
def orns(add_sfr: bool = True, drop_sfr: bool  = True, columns: str = 'receptor',
    verbose: bool = False) -> pd.DataFrame:
    """
    Args:
        add_sfr: whether spontaneous firing rate should be added to each measured
            change, to recover absolute odor-evoked firing rates.

        drop_sfr: if False, the spontaneous firing rates will be returned alongside the
            odor-evoked spike rate deltas.

        verbose: prints extra debugging information if True.

    Returns odor X receptors/glomeruli dataframe with int odor-evoked spike rate deltas
    """
    global _raw_hallem_df

    valid_columns_vals = ('receptor', 'glomerulus')
    if columns not in valid_columns_vals:
        raise ValueError(f'columns argument must be one of {valid_columns_vals}')

    if _raw_hallem_df is None:
        # header=1 so that receptor names (2nd row. fully defined.) are used rather than
        # glomeruli names (1st row. 2 missing of 24).
        df = _read_hallem_csv(header=1)

        _raw_hallem_df = df
    else:
        df = _raw_hallem_df

    sfr_row = 'spontaneous firing rate'
    assert sfr_row in df.index

    if add_sfr:
        df = df + df.loc[sfr_row]
        if verbose:
            n_neg_abs = (df < 0).sum().sum()
            print(f'{n_neg_abs} entries negative after adding spontaneous firing rate')

        df[df < 0] = 0

    if drop_sfr:
        df.drop(sfr_row, inplace=True)

    if columns == 'glomerulus':
        df.columns = df.columns.map(receptor2glomerulus)
        df.columns.name = 'glomerulus'
        assert not df.columns.isnull().any()

    return df


def _read_task_csv(**kwargs):
    return pd.read_csv(task_csv, index_col='glomerulus', **kwargs)


def format_glomeruli(glomeruli: List[str], *, delim: str = '+') -> str:
    return delim.join(sorted(glomeruli))


_task_df = None
_receptors_with_unclear_glomeruli = set()
# TODO option to pass output thru format_glomeruli?
def find_glomeruli(receptor: str, _df: Optional[pd.DataFrame] = None, *,
    include_unclear_receptors: bool = True, verbose: bool = True
    ) -> Optional[List[str]]:
    """
    Args:
        receptor: receptor name (from ORs, IRs, or a few other special values).
            'Or' prefix optional for ORs.
    """
    global _task_df

    if _df is None:
        if _task_df is None:
            _task_df = _read_task_csv()

        _df = _task_df

    receptor_lists = _df.receptors.str.split(', ')

    has_receptor = receptor_lists.apply(lambda rs: receptor in rs)

    unclear_receptor = receptor_lists.apply(lambda rs: f'{receptor}?' in rs)
    if unclear_receptor.sum() > 0:
        if verbose:
            print(f'found unclear receptors matching {receptor=}')
            print(_df.loc[unclear_receptor, 'receptors'].to_string())
            print()

        _receptors_with_unclear_glomeruli.add(receptor)

    if include_unclear_receptors:
        has_receptor |= unclear_receptor

    # TODO TODO are any cases of multiple receptor per glomerulus (from distinct ORN
    # types, each w/ their own receptor) vs single input cell classes expressing
    # multiple receptors? distinguish?

    if has_receptor.sum() == 0:
        if not receptor.startswith('Or'):
            # TODO could first check receptor matches <1-2 digits>[a-f]
            return find_glomeruli(f'Or{receptor}', _df=_df,
                include_unclear_receptors=include_unclear_receptors,
                verbose=verbose
            )
        else:
            # NOTE: if include_unclear_receptors were False, this would trigger
            # on Hallem Or85b (VM5d: "Or85b?, Or98b?")
            #raise KeyError(f'no glomeruli found with input from {receptor=}')
            return None

    glomeruli = _df.loc[has_receptor].index
    return list(glomeruli)


def _check_csv_data():
    df = _read_hallem_csv()

    # TODO validate all receptor names match <1-2 digits><lowercase letter a-f>?

    # between these two, that should imply 1:1
    assert len(glomerulus2receptor) == n_hallem_receptors
    assert len(set(glomerulus2receptor.values())) == len(glomerulus2receptor)
    # and if 1:1, we can safely do this (note the order is swapped)
    receptor2glomerulus = {r: g for g, r in glomerulus2receptor.items()}
    assert len(receptor2glomerulus) == len(glomerulus2receptor)

    csv_glomeruli = df.columns
    csv_receptors = df.iloc[0]
    assert len(csv_glomeruli) == n_hallem_receptors
    assert len(csv_receptors) == n_hallem_receptors

    common_glom = set(csv_glomeruli) & set(glomerulus2receptor)
    assert set(glomerulus2receptor) - set(csv_glomeruli) == {
        'DM3+DM5', 'VM5d'
    }
    # (total 24 - 2 w/o glomerulus defined in CSV)
    assert len(common_glom) == 22

    csv_map = {k: v for k, v in zip(csv_glomeruli, csv_receptors) if k in common_glom}
    assert csv_map == {k: v for k, v in glomerulus2receptor.items() if k in common_glom}


    assert set(csv_receptors) == set(glomerulus2receptor.values())

    receptor2task_glomeruli = {
        r: format_glomeruli(find_glomeruli(r)) for r in csv_receptors
    }
    assert receptor2glomerulus == receptor2task_glomeruli

