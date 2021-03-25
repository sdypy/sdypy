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
would like an extension to be implemented, if it is general and not related to structural dynamics.
consider implementing it into the SciPy stack.


Installation
------------

Install this package by:

.. code-block:: console

    pip install sdypy


Package integration in SDyPy
----------------------------

The existing efforts in the field of structural dynamics are included in SDyPy according to
the level of integration (see `SEP 1 <https://github.com/sdypy/sdypy/blob/main/docs/seps/sep-0001.rst>`_).

- **1st level** (part of SDyPy repository):
    - *No packages are currently at 1st level*

- **2nd level** (imported in namespace):
    - *No packages are currently at 2nd level*
   
- **3rd level** (installed by SDyPy):
   - `pyEMA <https://github.com/ladisk/pyEMA>`_ (Experimental Modal Analysis in Python)
   - `pyExSi <https://github.com/ladisk/pyExSi>`_ (Excitation signal generator)
   - `FLife <https://github.com/ladisk/FLife>`_ (Vibration fatigue life in the spectral domain)
   - `pyFBS <https://gitlab.com/pyFBS/pyFBS>`_ (Frequency Based Substructuring and Transfer Path Analysis)
   - `pyIDI <https://github.com/ladisk/pyidi>`_ (Image-Based Displacement Identification)
   
- **4th level** (these packages are developed completely independently but might be useful for 3rd, 2nd and 1st level packages):
   - `pyFRF <https://github.com/openmodal/pyFRF>`_ (Frequency Response Function estimation)
   - `speckle_pattern <https://github.com/ladisk/speckle_pattern>`_ (Speckle pattern generation for DIC)
   - `pyUFF <https://github.com/ladisk/uff_widget>`_ (Universal File Format in Python)
   - `pyNNST <https://github.com/LolloCappo/pyNNST>`_ (Obtaining non-stationary index for time-series)
   - `python-acoustics <https://github.com/python-acoustics/python-acoustics>`_ (Useful tools for acousticians)
   - `pyTrigger <https://github.com/ladisk/pyTrigger>`_ (Software trigger for data acquisition)
   - `AMfe <https://github.com/AppliedMechanics/AMfe>`_ (Finite Element Research Code)




