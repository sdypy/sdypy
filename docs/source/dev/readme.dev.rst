SDyPy — development notes
--------------------------

Setting up a development environment, running the tests and building these
docs are described in
`AGENTS.md <https://github.com/sdypy/sdypy/blob/main/AGENTS.md>`_.


Publishing the project
----------------------

The project is published to PyPI by the ``release-and-publish-to-pypi.yml``
GitHub Actions workflow, run by hand with the new version. It is the only way
to release; the steps, including the check for an open *SEP 2 pending terms*
issue (see :doc:`nomenclature`), are in
`AGENTS.md § Releasing <https://github.com/sdypy/sdypy/blob/main/AGENTS.md#releasing>`_.

After a release, SDyPy is installable with:

.. code-block:: console

    $ pip install sdypy
