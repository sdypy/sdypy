SDyPy — development notes
--------------------------

Setting up a development environment, running the tests and building these
docs are described in
`AGENTS.md <https://github.com/sdypy/sdypy/blob/main/AGENTS.md>`_.


Publishing the project
----------------------

The project is published to PyPI via the ``release-and-publish-to-pypi.yml``
GitHub Actions workflow.  Build and upload are handled by ``hatchling`` /
``twine``; no manual ``python -m build`` step is normally required.

Before tagging a release, check whether a *SEP 2 pending terms* issue is open.
If one is, trigger the canonical-table amendment described in
:doc:`nomenclature`; if there is no such issue, no names are waiting. The
amendment is triggered by hand, not on a schedule — this is the reminder, not a
gate, and a release is not held up by it.

After a release, SDyPy is installable with:

.. code-block:: console

    $ pip install sdypy
