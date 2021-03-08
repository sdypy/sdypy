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

SDyPy depends on core SciPy stack packages, please use those packages where posible. If you 
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
the level of integration (see SEP 1):

- **4th level** (related projects):
   - `pyFRF <https://github.com/openmodal/pyFRF>`_ (Frequency Response Function estimation)
   - `pyExSi <https://github.com/ladisk/pyExSi>`_ (Excitation signal generator)
   - `pyFBS <https://gitlab.com/pyFBS/pyFBS>`_ (Frequency Based Substructuring and Transfer Path Analysis)
   - `FLife <https://github.com/ladisk/FLife>`_ (Vibration fatigue life in the spectral domain)
   - `pyUFF <https://github.com/ladisk/uff_widget>`_ (Universal File Format in Python)
   - `pyIDI <https://github.com/ladisk/pyidi>`_ (Image-Based Displacement Identification)
   - `speckle_pattern <https://github.com/ladisk/speckle_pattern>`_ (Speckle pattern generation for DIC)
   
- **3rd level** (installed by SDyPy):
   - `pyEMA <https://github.com/ladisk/pyEMA>`_ (Experimental Modal Analysis in Python)
   
- **2nd level** (imported in namespace):
    - *No packages are currently at 2nd level*

- **1st level** (part of SDyPy repository):
    - *No packages are currently at 1st level*


