
.. image:: https://travis-ci.org/tom-f-oconnell/drosolf.svg?branch=master
    :target: https://travis-ci.org/tom-f-oconnell/drosolf

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

Todo
~~~~

-  DoOR integration
-  KC model(s)
-  sympy description of transformations applied to ORN data
