=============
SDyPy Roadmap
=============

This is a live snapshot of tasks and features we will be investing resources
in. It may be used to encourage and inspire developers and to search for
funding.


Interoperability
----------------

SDyPy packages share a common namespace (``sdypy.*``) and a unified
distribution entry point, so that data structures and results can flow
seamlessly between the EMA, io, FRF, excitation, view, and model sub-packages.
Future work aims to standardise array layouts and physical-unit conventions
across all packages, reducing friction for users who combine multiple modules
in a single analysis workflow.


Extensibility
-------------

We aim to make it much easier to extend SDyPy.


Website and documentation
-------------------------

The SDyPy API documentation and tutorials are hosted at
`sdypy.readthedocs.io <https://sdypy.readthedocs.io>`_.
Documentation should be kept up to date; tutorials and high-level
documentation on topics should not be missing or outdated.

User experience
---------------

Ease of use is a core SDyPy value: common structural-dynamics workflows should
require as few lines of code as possible.  Effort is ongoing to harmonise
function signatures and return types across packages, improve error messages,
and add more worked examples.  Feedback from users encountered in the issue
tracker directly shapes this work.

Type annotations
````````````````
We aim to add type annotations for all SDyPy functionality (this is also the goal of NumPy),
so users can use tools like `mypy`_ to type check their code and IDEs can improve their support
for SDyPy and NumPy.

Platform support
````````````````
We aim to increase our support for different hardware architectures. This
includes adding CI coverage when CI services are available, providing wheels on
PyPI for ARM64 (``aarch64``).


Maintenance
-----------

.. _`mypy`: https://mypy.readthedocs.io
