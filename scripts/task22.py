#!/usr/bin/env python3

from pprint import pprint

import pandas as pd
import tabula

from drosolf.orns import orns


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

    # DL3 has two it's row across two lines, and two of "Tuning receptor(s)"
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
    pdf = '../data/pdfs/task_2022.pdf'
    dfs = tabula.read_pdf(pdf, pages=[11, 12, 13])

    assert len(dfs) == 3

    dfs = [clean_df(df) for df in dfs]

    # from counting rows in PDF tables
    assert len(dfs[0]) == 25
    assert len(dfs[1]) == 28
    assert len(dfs[2]) == 7

    df = pd.concat(dfs, ignore_index=True)

    #df = df.set_index('glomerulus', verify_integrity=True)

    # columns='receptor' should also be the default, but just in case that changes
    orn_df = orns(columns='receptor')

    def find_glomerulus(hallem_receptor):
        """
        Args:
            hallem_receptor: should not start with 'Or'
                (all receptors in Hallem were ORs anyway)
        """
        receptor = f'Or{hallem_receptor}'
        has_receptor = df.receptors.str.split(', ').apply(lambda task_receptors:
            # TODO warn if using '?' stuff. prob do in separate step.
            receptor in task_receptors or f'{receptor}?' in task_receptors
        )
        glomeruli = df.loc[has_receptor, 'glomerulus']
        return '+'.join(glomeruli)

    # TODO also ensure that any glomeruli w/ multiple receptors get called out
    # (ideally including stuff where 1 from Hallem and >=1 from outside Hallem, if
    # there are any such cases)

    hallem_glomeruli = [find_glomerulus(x) for x in orn_df.columns]

    print('Hallem receptors and glomeruli:')
    pprint([tuple(x) for x in zip(orn_df.columns, hallem_glomeruli)])

    print()
    print('Glomerulus -> receptors:')
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
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()

