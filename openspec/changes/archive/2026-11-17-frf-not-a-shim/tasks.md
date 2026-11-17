## 1. Checkers

- [x] 1.1 `tools/check_public_api.py`: `SHIM_BACKENDS = {"excitation": "pyExSi"}`; update the module docstring
- [x] 1.2 `tools/check_sibling_template.py`: `SHIM_PACKAGES = {"excitation"}`; update the comment
- [x] 1.3 `tools/check_docs.py`: drop `sdypy-FRF` from `UPSTREAM_DOC_TARGET`

## 2. Tests

- [x] 2.1 `tests/test_sibling_template.py`: shim examples use excitation; add a test that FRF is not exempt
- [x] 2.2 `tests/test_public_api.py`: the drift test runs over the remaining shim

## 3. Verification and roster

- [x] 3.1 `openspec validate frf-not-a-shim --strict` is clean
- [x] 3.2 `pytest -m "not pypi_artifacts"` adds no failure to the baseline
- [x] 3.3 In the archive commit, update REQUIREMENTS.md: the shim rows and the 'A zero for a shim package is vacuous' note (FRF is no longer a shim)
