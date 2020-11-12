=============
SDyPy Roadmap
=============

This is a live snapshot of tasks and features we will be investing resources
in. It may be used to encourage and inspire developers and to search for
funding.


Interoperability
----------------


Extensibility
-------------

We aim to make it much easier to extend SDyPy.


Website and documentation
-------------------------

The SDyPy `documentation <https://www.sdypy.org/devdocs>`__ API documentation should be 
in good shape; tutorials and high-level documentation on topics should not be missing or outdated.

User experience
---------------


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
