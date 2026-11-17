## Why

sdypy-EMA PR #29 added the `ModelPoly` class (poly-reference LSCF for MIMO
FRFs) and put it in `sdypy.EMA.__all__`. The public-api spec fixes that list
at eight names, so `check_public_api` now fails on sdypy-EMA main with
"extra: ['ModelPoly']". `ModelPoly` is a user-facing class, like `Model`, and
belongs in the curated surface.

## What Changes

- The curated list for `sdypy.EMA.__all__` gets `ModelPoly`.
- `tools/check_public_api.py` `CURATED["EMA"]` gets the same name.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: the curated `sdypy.EMA.__all__` list adds `ModelPoly`.

## Impact

- `tools/check_public_api.py` passes on sdypy-EMA main again.
- `test_curated_surface_matches_spec[EMA]` (`pypi_artifacts`, not on CI)
  fails until an sdypy-EMA release with `ModelPoly` is on PyPI.
