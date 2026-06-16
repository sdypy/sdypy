SDyPy — Structural Dynamics Scientific Python
=============================================

SDyPy is a scientific Python ecosystem for structural dynamics.
It provides a unified namespace (``sdypy.*``) that aggregates six
independently developed packages covering the full structural-dynamics
workflow — from excitation-signal generation and measurement I/O, through
frequency-response-function estimation and experimental modal analysis, to
3-D visualisation and finite-element modelling.

.. code-block:: bash

   pip install sdypy

.. list-table:: Integrated packages
   :header-rows: 1
   :widths: 20 60 20

   * - Package
     - Description
     - Docs
   * - ``sdypy.EMA``
     - Experimental Modal Analysis — modal parameter identification from FRF data
     - `sdypy-EMA RTD <https://sdypy-ema.readthedocs.io/en/latest/>`_
   * - ``sdypy.io``
     - Measurement I/O — read/write structural-dynamics data formats (UFF, MTS, …)
     - `sdypy-io RTD <https://sdypy-io.readthedocs.io/en/latest/>`_
   * - ``sdypy.FRF``
     - Frequency Response Functions — H1/H2/Hv estimation and signal processing
     - `pyFRF docs <https://pyfrf.readthedocs.io/en/latest/>`_
   * - ``sdypy.excitation``
     - Excitation signals — random, burst-random, chirp, and impact signals
     - `pyExSi docs <https://pyexsi.readthedocs.io/en/latest/>`_
   * - ``sdypy.view``
     - 3-D visualisation — interactive plotting of mode shapes and animations
     - `sdypy-view RTD <https://sdypy-view.readthedocs.io/en/latest/>`_
   * - ``sdypy.model``
     - Finite element models — beam, shell, and tetrahedral elements
     - `sdypy-model RTD <https://sdypy-model.readthedocs.io/en/latest/>`_

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started
   code

.. toctree::
   :maxdepth: 1
   :caption: Packages

   packages

.. toctree::
   :maxdepth: 2
   :caption: SDyPy Enhancement Proposals

   seps/index

.. toctree::
   :maxdepth: 1
   :caption: Development

   dev/contributing
   dev/governance
   dev/code_of_conduct
   dev/pep8
   dev/governance_people
   dev/readme.dev


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
