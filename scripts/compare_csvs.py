#!/usr/bin/env python3

import numpy as np
import pandas as pd


def main():
    # TODO probably move this one out, and replace it w/ hc_data.csv
    ha = pd.read_csv('../drosolf/Hallem_Carlson_2006.csv')
    hc = pd.read_csv('../data/hc_data.csv')

    a_rec = ha.iloc[0][1:-1]
    c_rec = hc.iloc[0][2:]
    assert np.array_equal(a_rec, c_rec)

    a_glom = ha.columns[1:-1]
    c_glom = hc.columns[2:]
    neq = a_glom != c_glom

    print('receptors for mismatched glomeruli:')
    print(a_rec[neq].values)
    print('hc_data.csv glomeruli:')
    print(a_glom[neq].values)
    print('Hallem_Carlson_2006.csv glomeruli:')
    print(c_glom[neq].values)

    # Firing rate deltas for all non-(concentration series | fruit | SFR) data is the
    # same.
    assert np.array_equal(ha.iloc[1:111, 1:-1].values, hc.iloc[1:111, 2:].values)

    # Odor names are equal, ignoring (concentration series | fruit | SFR) names
    a_odors = ha.iloc[1:111, 0]
    c_odors = hc.iloc[1:111, 1]
    assert np.array_equal(a_odors, c_odors)

    # SFRs are also the same.
    a_sfr = ha.iloc[-1, 1:-1]
    c_sfr = hc.iloc[-1, 2:]
    assert np.array_equal(a_sfr, c_sfr)


    # ha doesn't have concentration series / fruit data, but we will just check that he
    # hc -2 data from the other table matches the main table data (which was also at -2;
    # it should have come from exactly the same data)

    # the iloc call here is removing the 'class' column, that is placed there after
    # changing index
    hc = hc.set_index('odor').iloc[:, 1:]

    c_minus2 = hc.iloc[111:(111 + 10)]
    for odor, row in c_minus2.iterrows():
        odor = odor[:-len(' -2')]
        assert np.array_equal(hc.loc[odor], row)


if __name__ == '__main__':
    main()

