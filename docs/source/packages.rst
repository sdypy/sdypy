Packages
========

SDyPy aggregates six independently developed packages under the
``sdypy.*`` namespace.  Each package has its own documentation site
and release cycle; the links below point to the latest stable build.

It also surfaces the SEP 5 unified-timeseries standard as ``sd.sep005``
(see :ref:`the sep005 section below <sep005-standard>`).

sdypy-EMA
---------

Experimental Modal Analysis: modal parameter identification from
frequency-response-function data using LSCF, LSCE, and related methods.

`sdypy-EMA on Read the Docs <https://sdypy-ema.readthedocs.io/en/latest/>`_

sdypy-io
--------

Measurement I/O: read and write common structural-dynamics data formats
including UFF, MTS, and LVM files.

`sdypy-io on Read the Docs <https://sdypy-io.readthedocs.io/en/latest/>`_

sdypy-FRF
---------

Frequency Response Functions: H1, H2, and Hv estimators, coherence, and
signal-conditioning utilities.  Built on the upstream *pyFRF* library.

`pyFRF documentation <https://pyfrf.readthedocs.io/en/latest/>`_

sdypy-excitation
----------------

Excitation signals: generation of random, burst-random, swept-sine (chirp),
and impact waveforms for structural testing.  Built on the upstream *pyExSi*
library.

`pyExSi documentation <https://pyexsi.readthedocs.io/en/latest/>`_

sdypy-view
----------

3-D visualisation: interactive plotting of mode shapes, operating deflection
shapes, and animations using pyvista.

`sdypy-view on Read the Docs <https://sdypy-view.readthedocs.io/en/latest/>`_

sdypy-model
-----------

Finite element modelling: Euler–Bernoulli beam, Kirchhoff–Love shell, and
tetrahedral solid elements with static and eigenvalue solvers.

`sdypy-model on Read the Docs <https://sdypy-model.readthedocs.io/en/latest/>`_

.. _sep005-standard:

sep005 (the unified-timeseries standard)
----------------------------------------

Unlike the six functional sub-packages above, ``sep005`` is not a
``sdypy.*`` namespace package — it is the **SEP 5 unified-timeseries
standard** and its compliance validator, distributed as the standalone
``sdypy-sep005`` package (importable as ``sdypy_sep005``).  SEP 5 defines a
common dictionary/list schema for timeseries data so that input-output
packages across the ecosystem interoperate.

For convenience it is surfaced on the umbrella as ``sd.sep005``::

    import sdypy as sd
    sd.sep005.assert_sep005(timeseries)   # raises on non-compliance

The same validator is also re-exported by ``sdypy.FRF`` as
``sdypy.FRF.assert_sep005``.  See :doc:`SEP 5 <seps/sep-0005>` for the
format specification.

`sdypy-sep005 on PyPI <https://pypi.org/project/sdypy-sep005/>`_
