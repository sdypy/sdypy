## Context

- SPEC 0 dropped Python 3.12 on 2026-10-02. CPython 3.15.0 was released
  2026-10-09; NumPy 2.5.4 (uploaded 2026-10-10) and SciPy 1.18.1 publish cp315
  wheels; `actions/setup-python` lists 3.15.0–3.15.2 as stable (all checked
  2026-11-04).
- The team approved the set for the whole consortium, backends included, and
  chose one PR per repository, opened directly on the canonical repositories.
- `check_docs.py` does not read `readthedocs.yaml`, although `REQUIREMENTS.md`
  names it as the verifier of *Standardised readthedocs.yaml*.

## Decisions

**1. Specs refer to the set; only the checker names it.** The core test matrix
and the Read the Docs Python now say *the supported set* and *its oldest
version*. A future drop edits `SUPPORTED_PYTHON` and the dated note only, plus
the repositories themselves. *Alternative:* keep the numbers in each spec, which
turns every yearly drop into a spec change across three capabilities.

**2. Backends are checked by a mode of the existing checker.** `--python-only`
skips the portion lookup and every template check except the Python points
(floor, classifiers, matrix, docs Python). The matrix is read from all
workflow files, because backends name their test workflow differently.
*Alternative:* a separate script, which would duplicate the set's parsing and
the floor logic.

**3. The docs Python is checked where the set lives.** The template checker
gains the `readthedocs.yaml` check (both modes; skipped when the file is
absent, since some backends have none). It reads the value with a regular
expression, like the workflow checks: the checkers use the standard library
only.

**4. The hub audits itself with the Python-only mode.** A test runs
`--python-only` on the hub root and asserts the core matrix equals the set
exactly, so the hub cannot drift from the set it declares.

## Risks / Trade-offs

- **Users on Python 3.10–3.12** stop receiving new releases of all fourteen
  packages. pip keeps installing the last release that supports their Python.
  pyuff and pyFRF have users outside sdypy; the team accepted this.
- **3.15 may break a dependency not yet checked** (gmsh, pyvistaqt): each
  repository's CI on 3.15 is the gate, in its own PR.
- **Every repository is reported until its own PR lands.** The checker is
  hand-run until `sdypy-devtools`, so nothing fails on its own.
