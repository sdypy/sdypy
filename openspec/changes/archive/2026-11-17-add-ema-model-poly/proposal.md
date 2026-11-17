## Why

sdypy-EMA adds `ModelPoly`, a class for poly-reference (MIMO) modal
identification (sdypy/sdypy-EMA issue #7; its own OpenSpec change
`add-poly-reference-model` carries the behaviour). The public-api spec lists
`sdypy.EMA.__all__` exactly, so exporting the new class is a change to this
org-wide contract and is proposed here; the code lands in sdypy-EMA.

Change type: **non-trivial** (a spec requirement and a public name change).

## What Changes

- `sdypy.EMA.__all__` gains `ModelPoly`: the curated list in the requirement
  *Every first-level package declares an explicit `__all__`* and the mirror in
  `tools/check_public_api.py` (`CURATED["EMA"]`).
- No other package and no other requirement changes. No **BREAKING** change.

New public name declared for SEP 2: `ModelPoly` (class; follows the existing
`Model`, so that both appear together in auto-completion). Its attribute names
are declared in the sdypy-EMA pull request.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: the curated `sdypy.EMA.__all__` list.

## Impact

- `tools/check_public_api.py`: `CURATED["EMA"]`.
- `tests/test_public_api.py::test_curated_surface_matches_spec[EMA]`
  (`pypi_artifacts`) stays red against the published sdypy-EMA until a release
  that contains `ModelPoly`; the checker run against the sdypy-EMA branch is
  green. Merge this change together with, or after, the sdypy-EMA pull request.
