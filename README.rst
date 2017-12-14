Installation
~~~~~~~~~~~~

::

    pip install drosolf

If you need elevated permissions to install (if the ``pip install`` line
fails with some sort of permissions error), you can try:

::

    sudo -H pip install drosolf

Examples
~~~~~~~~

To get Hallem and Carlson ORN responses, with the baseline added back
in. Returned as a pandas DataFrame with columns of receptor and row
indices of odor. The transpose (i.e. ``orn_responses.T``) will have
odors as the columns.

::

    from drosolf import orns
    orn_responses = orns.orns()

To get simulated projection neuron responses, using the Olsen input gain
control model and the ORN responses.

::

    from drosolf import pns
    pn_responses = pns.pns()

Get correlation matrices at the ORN and (simulated) PN levels for a list
of odors, named as the columns of the previous DataFrames.

::

    from drosolf import corrs
    orn_correlations, pn_correlations = corrs.get_corrs(list_of_odors)

Generate plots of the same ORN and PN correlation matrices (uses
seaborn).

::

    import matplotlib.pyplot as plt
    from drosolf import corrs

    corrs.plot_corrs(list_of_odors)
    plt.show()

Todo
~~~~

-  DoOR integration
-  KC model(s)
-  sympy description of transformations applied to ORN data
