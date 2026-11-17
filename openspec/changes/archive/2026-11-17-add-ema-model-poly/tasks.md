# Tasks

## 1. Contract

- [x] 1.1 Add `ModelPoly` to the curated `sdypy.EMA.__all__` list in the `public-api` delta spec
- [x] 1.2 Mirror it in `tools/check_public_api.py` (`CURATED["EMA"]`)

## 2. Verification

- [x] 2.1 `python tools/check_public_api.py --path ../sdypy-EMA` passes against the sdypy-EMA branch `poly-reference` (verifier of the modified requirement, together with `tests/test_public_api.py::test_curated_surface_matches_spec`)
- [x] 2.2 `tests/test_public_api.py::test_curated_surface_matches_spec[EMA]` passes against a published sdypy-EMA release with `ModelPoly`

## 3. Coordination

- [x] 3.1 Land together with, or after, the sdypy-EMA pull request that adds `ModelPoly`
