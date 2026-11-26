## 1. Checkers

- [x] 1.1 `tools/check_public_api.py`: remove `SHIM_BACKENDS`, `drift_report` and the `importlib` import; fix the module docstring and the star-import message
- [x] 1.2 `tools/check_sibling_template.py`: remove `SHIM_PACKAGES` and the exemption in `check_openspec_config`
- [x] 1.3 `tools/check_docs.py`: remove `UPSTREAM_DOC_TARGET`; every package must point at its own readthedocs.io site

## 2. Tests

- [x] 2.1 `tests/test_sibling_template.py`: remove the shim-exemption tests; add a test that excitation is not exempt
- [x] 2.2 `tests/test_public_api.py`: remove the drift test and the `SHIM_BACKENDS` import

## 3. Verification and roster

- [x] 3.1 `openspec validate excitation-not-a-shim --strict` is clean
- [x] 3.2 `pytest -m "not pypi_artifacts"` adds no failure to the baseline
- [ ] 3.3 In the archive commit, update REQUIREMENTS.md: remove the shim rows, add the new public-api row, and drop the 'A zero for a shim package is vacuous' note (no package is a shim)
