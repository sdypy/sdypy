|pytest| |documentation|

SDyPy - Structural Dynamics Python
----------------------------------

This package has the goal to defragment the open source effort in the scientific field 
of structural dynamics. Our goal is to speed-up the development and implementation of scientific
methods. This an open and free initiative, we stand up for:

- free MIT license,
- open development,
- open accepting of contributions,
- open decision making,
- multi-institutional engagement.

SDyPy depends on core SciPy stack packages, please use those packages where possible. If you 
would like an extension to be implemented, if it is general and not related to structural dynamics,
consider implementing it into the SciPy stack.


Installation and basic usage
----------------------------

Install this package by:

.. code-block:: console

    pip install sdypy

The `sdypy` offers a convenient way to access the functionality of the namespace packages.

First import the `sdypy` package:

.. code-block:: python

    import sdypy as sd

Access the `EMA` module:

.. code-block:: python

    model = sd.EMA.Model(FRF_matrix, freq_array)

or the `io` module:

.. code-block:: python

	uff_obj = sd.io.uff.UFF('file.uff')

or the `FRF` module:

.. code-block:: python

	frf_obj = sd.FRF.FRF(sampling_freq, excitation, response)

or the `excitation` module:

.. code-block:: python

    gausian_signal = sd.excitation.random_gaussian((N, PSD, fs))


Package integration in SDyPy
----------------------------

The existing efforts in the field of structural dynamics are included in SDyPy according to
the level of integration (see `SEP 1 <https://github.com/sdypy/sdypy/blob/main/docs/seps/sep-0001.rst>`_).

- **1st level** (part of SDyPy repository or organization):
   - `sdypy-EMA <https://github.com/sdypy/sdypy-EMA>`_ (Experimental Modal Analysis in Python)
   - `sdypy-io <https://github.com/sdypy/sdypy-io>`_ (Input/Output for Structural Dynamics)
   - `sdypy-FRF <https://github.com/sdypy/sdypy-FRF>`_ (Frequency Response Function estimation)
   - `sdypy-excitation <https://github.com/sdypy/sdypy-excitation>`_ (Excitation signals as used in structural dynamics and vibration fatigue)

- **2nd level** (namespace package in independent repository):
   
- **3rd level** (packages that correspond to the SDyPy template):
   - `pyExSi <https://github.com/ladisk/pyExSi>`_ (Excitation signal generator)
   - `FLife <https://github.com/ladisk/FLife>`_ (Vibration fatigue life in the spectral domain)
   - `pyIDI <https://github.com/ladisk/pyidi>`_ (Image-Based Displacement Identification)
   
- **4th level** (these packages are developed completely independently but might be useful for 3rd, 2nd and 1st level packages):
   - `pyFRF <https://github.com/openmodal/pyFRF>`_ (Frequency Response Function estimation)
   - `pyFBS <https://gitlab.com/pyFBS/pyFBS>`_ (Frequency Based Substructuring and Transfer Path Analysis)
   - `speckle_pattern <https://github.com/ladisk/speckle_pattern>`_ (Speckle pattern generation for DIC)
   - `pyUFF <https://github.com/ladisk/pyuff>`_ (Universal File Format in Python)
   - `pyNNST <https://github.com/LolloCappo/pyNNST>`_ (Obtaining non-stationary index for time-series)
   - `python-acoustics <https://github.com/python-acoustics/python-acoustics>`_ (Useful tools for acousticians)
   - `pyTrigger <https://github.com/ladisk/pyTrigger>`_ (Software trigger for data acquisition)
   - `AMfe <https://github.com/AppliedMechanics/AMfe>`_ (Finite Element Research Code)


..  |documentation| image:: https://readthedocs.org/projects/sdypy/badge/?version=latest
    :target: https://sdypy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |pytest| image:: https://github.com/sdypy/sdypy/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/sdypy/sdypy/actions
