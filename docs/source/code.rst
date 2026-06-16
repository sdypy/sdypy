API Reference
=============

The ``sdypy`` umbrella package is a lightweight lazy facade over six
independently developed sub-packages.  Importing ``sdypy`` is cheap — heavy
optional backends (pyvista, Qt) are only loaded when you actually access the
corresponding sub-package attribute.

.. automodule:: sdypy
   :members:
   :undoc-members:

Sub-package public APIs
-----------------------

Each sub-package is documented at its own site (links in :doc:`packages`).
The names exposed directly under ``sdypy`` are:

* ``sdypy.EMA`` — Experimental Modal Analysis
* ``sdypy.io`` — Measurement I/O
* ``sdypy.FRF`` — Frequency Response Functions
* ``sdypy.excitation`` — Excitation signal generation
* ``sdypy.view`` — 3-D visualisation
* ``sdypy.model`` — Finite element modelling
