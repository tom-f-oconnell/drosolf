#!/usr/bin/env python3
"""
Parses PDF of Task et al. 2022 ("Chemoreceptor co-expression in Drosophila melanogaster
olfactory neurons") and writes main content of table 3 to `task22_table3.csv`.

Also summarizes glomerulus:receptor mapping.
"""

from pathlib import Path

import pandas as pd
import tabula

# NOTE: data_dir is now something from importlib.resources, and not a simple path, so
# this script might be broken
from drosolf.orns import orns, find_glomeruli, data_dir, task_csv


pdf = data_dir / 'pdfs/task_2022.pdf'

def clean_df(df):
    assert len(df.columns) == 9

    # last column = reference column
    df = df.iloc[:, :8].copy()
    assert len(df.columns) == 8

    df = df.dropna(how='all')

    df.columns = ['glomerulus', 'sensillum', 'receptors', 'orig_coreceptors',
        'orco', 'ir8a', 'ir76b', 'ir25a'
    ]

    df = df.drop(columns=['orig_coreceptors'])

    if df.iloc[0, 0].startswith('Glomerulus'):
        df = df.iloc[1:, :].copy()

    # DL3 has it's row across two lines (?), and two of "Tuning receptor(s)"
    # (Or65a and Or65b) are in first line (which corresponds to a previous row in the
    # DataFrame, NaN elsewhere)
    dl3_rows = df.glomerulus == 'DL3'
    if dl3_rows.any():
        assert dl3_rows.sum() == 1
        df.loc[dl3_rows, 'receptors'] = 'Or65a, Or65b, Or65c'

        len_before = len(df)
        df = df.dropna(subset=[x for x in df.columns if x != 'receptors'], how='all')
        assert len(df) == len_before - 1

    sacculus_rows = df.sensillum.str.contains('chamber')
    if sacculus_rows.any():
        # Most have "Sacculus," on line mostly by itself (preceding line w/ glomerulus
        # name)
        df.sensillum = df.sensillum.str.replace('chamber', 'Sacculus, chamber')

        # VM6l row is an exception, where "Sacculus," is on same line as glomerulus
        # name, and next row has "chamber III"
        vm6l_rows = df.glomerulus == 'VM6l*'
        if vm6l_rows.any():
            assert vm6l_rows.sum() == 1
            df.loc[vm6l_rows, 'sensillum'] = 'Sacculus, chamber III'

            # last row should be one right after VM6l* row (but only contain useless
            # information now and can be dropped. info still corresponds to VM6l*)
            len_before = len(df)
            df = df.iloc[:-1, :].copy()
            assert len(df) == len_before - 1

        df = df.dropna(subset=[x for x in df.columns if x != 'sensillum'], how='all')

    # TODO drop stuff where glomerulus == '(new)' (2nd of two lines in some cases)
    # (and strip any trailing '(new)')

    assert not df.isna().any().any()

    return df


def main():
    # These are the pages that should contain table 3.
    dfs = tabula.read_pdf(pdf, pages=[11, 12, 13])

    assert len(dfs) == 3

    dfs = [clean_df(df) for df in dfs]

    # from counting rows in PDF tables
    assert len(dfs[0]) == 25
    assert len(dfs[1]) == 28
    assert len(dfs[2]) == 7

    df = pd.concat(dfs, ignore_index=True)

    df = df.set_index('glomerulus', verify_integrity=True)

    # example strings this regex would match: 'VM7v (1)', 'VM6l*', etc
    glomerulus_names = df.index.str.replace('(?:\s\(.*\)|\*)', '', regex=True)
    glomerulus_renamed = glomerulus_names != df.index
    if glomerulus_renamed.any():
        verbose = True
        if verbose:
            msg = 'removing parenthetical/* suffix from glomeruli:'
            msg += '\n- '.join( [''] + list(df.index[glomerulus_renamed]) )
            msg += '\n'
            print(msg)

        df.index = glomerulus_names

    # NOTE: should just require pd.read_csv(<path>, index_col='glomerulus') to load
    print(f'writing to {task_csv}\n')
    df.to_csv(task_csv)
    assert df.equals(pd.read_csv(task_csv, index_col='glomerulus'))

    # columns='receptor' should also be the default, but just in case that changes
    hallem_receptors = orns(columns='receptor').columns

    hallem_glomeruli = [find_glomeruli(x, df) for x in hallem_receptors]

    # TODO delete? (just checking find_glomeruli default df loading functions same)
    hallem_glomeruli2 = [find_glomeruli(x) for x in hallem_receptors]
    assert hallem_glomeruli == hallem_glomeruli2
    #

    hallem_no_ambig_glom = [
        find_glomeruli(x, df, include_unclear_receptors=False, verbose=False)
        for x in hallem_receptors
    ]
    assert hallem_no_ambig_glom != hallem_glomeruli

    # TODO delete? (just checking find_glomeruli default df loading functions same)
    hallem_no_ambig_glom2 = [
        find_glomeruli(x, include_unclear_receptors=False, verbose=False)
        for x in hallem_receptors
    ]
    assert hallem_no_ambig_glom == hallem_no_ambig_glom2
    #

    hallem_receptors_with_unclear_glomeruli = set(hallem_receptors[
        [x != y for x, y in zip(hallem_no_ambig_glom, hallem_glomeruli)]
    ])

    hallem_receptor2glomeruli = dict(zip(hallem_receptors,
        # TODO refactor? don't i do similar elsewhere?
        ['+'.join(gs) for gs in hallem_glomeruli]
    ))
    unclear_hallem_glomeruli = {
        hallem_receptor2glomeruli[x] for x in hallem_receptors_with_unclear_glomeruli
    }
    assert unclear_hallem_glomeruli == {'VM5d'}

    # This should be length 23 instead of 24, because one receptor is only DM3+DM5,
    # despite each of those having their own distinct, unique receptor.
    hallem_glomeruli_set = {g for gs in hallem_glomeruli for g in gs}
    assert len(hallem_glomeruli_set) == 23

    print('Hallem receptors and glomeruli:', end='')
    print('\n- '.join([''] + [
        f'{g}: {"+".join(rs)}' for g, rs in zip(hallem_receptors, hallem_glomeruli)
    ]))
    print()

    df = df.reset_index()

    print('Glomerulus -> receptors:')
    # TODO way to groupby() on the index w/o having to reset_index()?
    print(df.groupby('glomerulus').receptors.unique().to_string())

    print()
    print('Glomeruli with multiple receptors:')
    receptor_lists = df.receptors.str.split(', ')
    multiple_receptors = receptor_lists.str.len() > 1
    tdf = df.copy()
    tdf.receptors = receptor_lists
    print(
        tdf.loc[multiple_receptors, ['glomerulus', 'receptors']].to_string(index=False)
    )

    # TODO share code from orns.task_receptor2glomeruli to print out receptors w/
    # multiple glomeruli?


if __name__ == '__main__':
    main()

