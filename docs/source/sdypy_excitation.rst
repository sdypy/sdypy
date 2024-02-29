sdypy-excitation
----------------

The ``sdypy-excitation`` is a namespace project of the ``sdypy`` framework and is a 
direct link to the `pyExSi <https://github.com/ladisk/pyExSi>`_ package.

To use the ``sdypy-excitation`` functionality, import:

.. code-block:: python

    import sdypy as sd

The ``excitation`` namespace is a direct link to the ``pyExSi`` package. Instead of
calling e.g. ``pyExSi.random_gaussian((N, PSD, fs))`` you can call ``sd.excitation.random_gaussian((N, PSD, fs))``.

For reference, see the `pyExSi documentation <https://pyExSi.readthedocs.io/en/latest/>`_.