## Why

The supported Python set is out of date by its own rule. *Supported Python
versions follow SPEC 0* asks for every minor version released less than three
years ago, through the newest one for which the current NumPy and SciPy both
publish wheels. SPEC 0 dropped 3.12 on 2026-10-02 (3.12.0 released 2023-10-02),
CPython 3.15.0 was released on 2026-10-09, and NumPy 2.5.4 and SciPy 1.18.1 both
publish 3.15 wheels. The set is therefore 3.13, 3.14 and 3.15; the checker still
says 3.12, 3.13 and 3.14.

The team approved applying the set to every package the consortium maintains:
the hub, the six first-level packages, the template project, and the seven
backend libraries the packages wrap or depend on (pyFRF, pyExSi, pyEMA, pyuff,
pyLump, lvm_read, pyMRAW). Today only the first-level packages are bound by the
rule.

Three hub specs also write the versions out instead of referring to the set:
the core test matrix (`testing-ci`) and the Read the Docs Python
(`documentation`, pinned to 3.12 for all seven repositories). Each yearly
drop would then need a spec change, and the Read the Docs pin would break every
docs build once a package's floor rises past it.

Non-trivial: it changes spec requirements.

## What Changes

- The supported set becomes **3.13, 3.14, 3.15** (one declaration, the sibling
  template checker). **BREAKING** for users: packages released under the new
  set no longer install on Python 3.10–3.12; earlier releases stay installable.
- **New requirement:** the seven backend libraries support the same set
  (Python floor, classifiers, CI matrix, and the docs build where they have
  one). The checker gains a `--python-only` mode that audits just these points
  in any repository, since a backend has no `sdypy/` portion for the full
  template check.
- The core test matrix and the Read the Docs Python refer to the supported set
  (the matrix is the set; the docs build runs on its oldest version) instead of
  naming versions. The next yearly drop becomes a one-line edit of the checker.
- The template checker also checks the `readthedocs.yaml` Python, so the
  docs-build requirement gets a mechanical verifier (today `check_docs.py`
  does not read `readthedocs.yaml` at all).
- The hub follows the new set: `pyproject.toml`, the test matrix, the docs and
  release jobs, `readthedocs.yaml`, and the `AGENTS.md` development line.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sibling-package-template`: MODIFIED *Supported Python versions follow SPEC 0*
  (dated note 3.13–3.15); ADDED *Backend libraries support the supported Python
  set*.
- `testing-ci`: MODIFIED *GitHub CI deselects pypi_artifacts and the matrix is
  green*, MODIFIED *Core test workflow has the required shape* (matrix by
  reference).
- `documentation`: REMOVED *Standardised readthedocs.yaml*, ADDED *Standardised
  readthedocs.yaml on the oldest supported Python* (same shape, Python by
  reference; replaced because a scenario name carries "3.12").

## Impact

- Hub: `tools/check_sibling_template.py`, `tests/test_sibling_template.py`,
  `pyproject.toml`, `.github/workflows/{python-package,docs,release-and-publish-to-pypi}.yml`,
  `readthedocs.yaml`, `AGENTS.md`, `REQUIREMENTS.md` (at archive).
- Every sibling and backend is reported by the checker until its own PR moves
  it to the new set; those PRs live in each repository, not in this change.
