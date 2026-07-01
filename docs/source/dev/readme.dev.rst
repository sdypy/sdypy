SDyPy — development notes
--------------------------

To download the source code:

.. code-block:: console

    $ git clone https://github.com/sdypy/sdypy

To begin development, install the package and its development dependencies
with:

.. code-block:: console

    $ pip install -e ".[dev]"

Consider adding unit-tests in ``tests/``. The provided test file structure
is set up to work with `pytest <https://docs.pytest.org/en/latest/>`_.

To build the Sphinx documentation locally:

.. code-block:: console

    $ python docs/seps/tools/build_index.py
    $ python -m sphinx -b html docs/source docs/_build/html

The built files appear under ``docs/_build/html/``.


File structure
--------------

pyproject.toml
    Project metadata, build system configuration, and optional-dependency
    extras (``pip install .[docs]``, ``pip install .[dev]``).

README.rst
    The main project description shown on PyPI and GitHub.

CONTRIBUTING.rst
    Information for contributors.

License
    The project licence (MIT).

.gitignore
    Files excluded from version control.

tests/
    Unit tests — run with ``pytest``.

sdypy/
    The umbrella package source code: a lightweight lazy facade that
    re-exports the six first-level sub-packages.

docs/
    Sphinx documentation sources (``docs/source/``) and the standalone
    SEP project (``docs/seps/``).

examples/
    Notebooks and scripts that showcase SDyPy workflows.


Publishing the project
----------------------

The project is published to PyPI via the ``release-and-publish-to-pypi.yml``
GitHub Actions workflow.  Build and upload are handled by ``hatchling`` /
``twine``; no manual ``python -m build`` step is normally required.

After a release, SDyPy is installable with:

.. code-block:: console

    $ pip install sdypy
