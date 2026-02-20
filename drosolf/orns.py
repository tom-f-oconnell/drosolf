"""
For loading Hallem & Carlson olfactory receptor neuron responses.
"""

from typing import List, Dict, Optional
# i thought it was importlib.resources after 3.7?
from importlib_resources import files

from pathlib import Path
from pprint import pprint

import numpy as np
import pandas as pd

import drosolf


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

data_dir = files('drosolf.data')

task_csv = data_dir.joinpath('task22_table3.csv')
hallem_csv = data_dir.joinpath('Hallem_Carlson_2006.csv')

# TODO or do i also want to define location of this relative to orns.py, rather than
# data_dir? if so, could move data_dir back into task22.py
# path to this seems broken when at least one pip install 2025-04-11, w/ pip==22.3.1
# (same as in al_analysis venv) (run from w/in ~/src/model_test/al_analysis)
# [via `git+https://github.com/tom-f-oconnell/drosolf` line in requirements.txt]

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
receptor2glomerulus = {r: g for g, r in glomerulus2receptor.items()}
assert len(receptor2glomerulus) == len(glomerulus2receptor)


def _read_hallem_csv(**kwargs):
    # after usecols (1 odor name index column + receptor columns) is a CAS column I
    # don't want
    df = pd.read_csv(hallem_csv, index_col='odor',
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

        _raw_hallem_df = df.copy()
    else:
        # TODO .copy()? didn't seem to fix an issue
        df = _raw_hallem_df.copy()

    sfr_row = 'spontaneous firing rate'
    assert sfr_row in df.index

    if add_sfr:
        df = df + df.loc[sfr_row]
        if verbose:
            n_neg_abs = (df < 0).sum().sum()
            print(f'{n_neg_abs} entries negative after adding spontaneous firing rate')

        df[df < 0] = 0

    if drop_sfr:
        df = df.drop(sfr_row)

    if columns == 'glomerulus':
        df.columns = df.columns.map(receptor2glomerulus)
        df.columns.name = 'glomerulus'
        assert not df.columns.isnull().any()

    return df


def _task_add_receptor_lists(df: pd.DataFrame) -> None:
    """Modify `df` to add 'receptor_list' column, from splitting str 'receptors' column.
    """
    if 'receptor_lists' in df:
        return

    # TODO maybe sort receptors here?
    # TODO need to strip any whitespace after (doesn't seem so)? always one space (seems
    # so)? check set of receptor names this gives us for any whitespace
    receptor_lists = df.receptors.str.split(', ')
    assert (receptor_lists.str.len() >= 1).all()
    df['receptor_lists'] = receptor_lists


_task_df = None
def _read_task_csv(**kwargs):
    global _task_df
    if _task_df is None:
        df = pd.read_csv(task_csv, index_col='glomerulus', **kwargs)
        assert not df.index.duplicated().any(), 'should be one row per glomerulus'

        _task_add_receptor_lists(df)

        _task_df = df

    return _task_df


def format_glomeruli(glomeruli: List[str], *, delim: str = '+') -> str:
    return delim.join(sorted(glomeruli))


_receptors_with_unclear_glomeruli = set()
# TODO option to pass output thru format_glomeruli?
# TODO rename?
# TODO TODO warn if any glomeruli found also have other receptors? at least if verbose?
# TODO set verbose default to False
def find_glomeruli(receptor: str, _df: Optional[pd.DataFrame] = None, *,
    include_unclear_receptors: bool = True, verbose: bool = True
    ) -> Optional[List[str]]:
    """
    Args:
        receptor: receptor name (from ORs, IRs, or a few other special values).
            'Or' prefix optional for ORs.
    """
    if _df is None:
        df = _read_task_csv()
    else:
        df = _df.copy()
        _task_add_receptor_lists(df)

    receptor_lists = df['receptor_lists']

    has_receptor = receptor_lists.apply(lambda rs: receptor in rs)

    unclear_receptor = receptor_lists.apply(lambda rs: f'{receptor}?' in rs)
    if unclear_receptor.sum() > 0:
        if verbose:
            print(f'found unclear receptors matching {receptor=}')
            print(df.loc[unclear_receptor, 'receptors'].to_string())
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
            return find_glomeruli(f'Or{receptor}', _df=df,
                include_unclear_receptors=include_unclear_receptors,
                verbose=verbose
            )
        else:
            # NOTE: if include_unclear_receptors were False, this would trigger
            # on Hallem Or85b (VM5d: "Or85b?, Or98b?")
            #raise KeyError(f'no glomeruli found with input from {receptor=}')
            return None

    glomeruli = df.loc[has_receptor].index
    return sorted(glomeruli)


# TODO TODO in either pns.py or a new file, add fns for getting full hemibrain
# (+ fafb) PN->KC data, ideally w/ glomeruli all in same terms as task 22 data here

def task_glomerulus2receptors(verbose: bool = False) -> Dict[str, List[str]]:
    df = _read_task_csv()

    assert df.index.name == 'glomerulus'
    receptor_lists = df.receptor_lists

    # TODO sort in a way that splits into 'Or'(/prefix) <number> <letter> parts?
    # not that important...
    glomerulus2receptors = {g: sorted(rs) for g, rs in receptor_lists.to_dict().items()}
    assert len(glomerulus2receptors) == len(df)

    # TODO if verbose, print which glomerulus->receptors map for those w/ multiple
    # receptors (as in task22.py)
    if verbose:
        multiple_receptors = {
            g: rs for g, rs in glomerulus2receptors.items() if len(rs) > 1
        }
        if len(multiple_receptors) > 0:
            print('glomeruli with multiple receptors:')
            pprint(multiple_receptors)

    # TODO process receptors w/ '?' suffix (to remove it)?

    return glomerulus2receptors


# TODO or should i format List[str] to just a str? flag to do so at least?
# TODO also add option to convert any values that would have multiple to a single NaN?
def task_receptor2glomeruli(verbose: bool = False, **kwargs) -> Dict[str, List[str]]:
    """
    Args:
        **kwargs: passed thru to `find_glomeruli`
    """
    df = _read_task_csv()
    receptor_lists = df.receptor_lists

    receptors = set()
    for rs in receptor_lists:
        receptors.update(rs)

    for receptor in receptors:
        # TODO move these first two checks to _task_add_receptor_lists?
        assert receptor == receptor.strip()
        assert ',' not in receptor

        # NOTE: this also implies that if any receptors have '?' as a suffix, that same
        # receptor isn't listed anywhere without this uncertainty.
        assert not any(x.startswith(receptor) for x in receptors - {receptor})

    receptor2glomeruli = {
        r: find_glomeruli(r, verbose=verbose, **kwargs) for r in sorted(receptors)
    }

    if verbose:
        glomerulus2receptors = task_glomerulus2receptors(verbose=verbose)
        multiple_glomeruli = {
            r: [f'{g} ({"+".join(glomerulus2receptors[g])})' for g in gs]
            for r, gs in receptor2glomeruli.items() if len(gs) > 1
        }
        if len(multiple_glomeruli) > 0:
            print()
            print('receptors with multiple glomeruli:')
            pprint(multiple_glomeruli)

    # TODO process receptors w/ '?' suffix (to remove it)?

    return receptor2glomeruli


def _check_csv_data():
    df = _read_hallem_csv()

    # TODO validate all receptor names match <1-2 digits><lowercase letter a-f>?

    assert len(glomerulus2receptor) == n_hallem_receptors
    assert len(set(glomerulus2receptor.values())) == len(glomerulus2receptor)

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

    # TODO replace all receptor2glomerulus/glomerulus2receptor stuff w/ task_*
    # counterparts?
    receptor2task_glomeruli = {
        r: format_glomeruli(find_glomeruli(r)) for r in csv_receptors
    }
    assert receptor2glomerulus == receptor2task_glomeruli

    receptor2glomeruli = task_receptor2glomeruli()
    # TODO move this to an option in task_receptor2glomeruli?
    receptor2glomeruli = {r.strip('?'): gs for r, gs in receptor2glomeruli.items()}

    assert not any(x.startswith('Or') for x in csv_receptors)

    hallem_receptor2glomeruli = {
        r: '+'.join(receptor2glomeruli[f'Or{r}']) for r in csv_receptors
    }
    assert hallem_receptor2glomeruli == receptor2glomerulus

