## 1. Spec

- [x] 1.1 Delta for `public-api`: add the model renames to table names; drop `pole_xi` and `EI`
- [x] 1.2 `openspec validate sep2-renames-followup --strict` is clean

## 2. Tests

- [x] 2.1 `tests/test_interop.py`: `nat_freq` → `natural_freq`, `nat_xi` → `damping_ratio`, `lower`/`upper` → `freq_lower`/`freq_upper`
- [x] 2.2 `pytest tests/test_interop.py` and `pytest -m "not pypi_artifacts"` pass
- [x] 2.3 `tools/check_public_api.py` passes against `../sdypy-EMA` and `../sdypy-model`

## 3. Roster

- [ ] 3.1 Archive with the REQUIREMENTS.md roster update
