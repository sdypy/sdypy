## 1. Amend SEP 2 and the hub (hub, branch `sep2-frf-estimator`)

- [x] 1.1 Add the *FRF estimator* row to the canonical table in `docs/seps/sep-0002.rst`: `frf_estimator`, empty **Instead of**, values `'H1'`, `'H2'`, `'Hv'`, `'ODS'`, with a remark that `'ODS'` is an operational deflection shape, not an H-estimator. Verify: `pytest tests/test_nomenclature.py` passes (the new row adds no spelling to the column, so the two-way pin still holds)
- [x] 1.2 In the *FRF form* row, replace "Backend parameter names are out of scope." with a pointer to the re-exported-objects rule (task 1.4). Verify: the row no longer says backend names are out of scope
- [x] 1.3 Change "Two entries need a word of explanation." to three, and add the note: `frf_type` diverges from `frf_form` for the FRF form and from `frf_estimator` for the estimator choice; on `get_FRF`, `type` diverges from `frf_estimator` and `form` from `frf_form`; the checker enforces only `frf_type` → `frf_form`, and pyFRF's tests verify the rest. Verify: the note sits before `.. canonical-table-end`, so `docs/source/dev/nomenclature.rst` shows it
- [x] 1.4 Add a short "Re-exported backend objects" paragraph after the *Public API surface* section: a class or function that a first-level package re-exports is part of its public API and follows SEP 2; backend names not re-exported are out of scope. Verify: `python tools/check_seps.py --path .` exits 0
- [x] 1.5 In "Relation to ISO 7626", add two sentences: ISO 7626 does not name the estimator choice; ISO 18431-1 says "frequency response function of the first type / second type", and SDyPy uses `frf_estimator` because `type` is ambiguous and shadows a Python built-in. Add ISO 18431-1 to the references. Verify: `sphinx-build -W -b html docs/source docs/_build/html` succeeds
- [x] 1.6 Add to the coverage-boundary list in the `tools/check_nomenclature.py` docstring: names of re-exported backend objects (pyFRF's `FRF`) are not audited; their renames are verified by the backend's tests. Verify: `pytest tests/test_nomenclature.py` passes
- [x] 1.7 Add tests to `tests/test_nomenclature.py`: `type` and `form` are not keys of `CANONICAL`; a clone with `pkg="FRF"` and a class with a public method `get_FRF(self, type=None, form=None)` reports no `nomenclature` fault; SEP 2's notes below the table mention `frf_estimator`, `type` and `form`. Verify: `pytest -m "not pypi_artifacts"` passes
- [x] 1.8 Change `tests/test_interop.py:184` from `get_FRF(type="H1")` to the positional `get_FRF("H1")`, which works on pyFRF 1.4 and 1.5 without a warning. Verify: `pytest tests/test_interop.py` passes
- [ ] 1.9 In the archive commit (task 6.3, per AGENTS.md), update `REQUIREMENTS.md`: add `public-api` rows for the new and changed requirements, naming the verifiers (`tests/test_nomenclature.py` for the column and notes; pyFRF `tests/test_deprecations.py` for the backend renames; the hub PR reviewer for the scope rule); rewrite the pending-roster paragraph that calls backend names out of scope; add a pyFRF entry to the roster. Verify: every requirement in the delta spec has a row
- [x] 1.10 Open the hub PR on `ladisk/sdypy` with the OpenSpec artifacts in the first commit and the implementation after, linking PR #6 and PR #7. Declare `frf_estimator` as a new public name in the PR body (SEP 2 "Proposing a new term"). Verify: CI green

## 2. pyFRF (ladisk/pyFRF, branch `frf-estimator`)

- [x] 2.1 Rename the `FRF.__init__` parameter `frf_type` to `frf_estimator` in the same position; add keyword-only `frf_type=None` that emits `DeprecationWarning` and wins when passed. Verify: tests in the new file `tests/test_deprecations.py`
- [x] 2.2 Store the choice as `self.frf_estimator`; add a `frf_type` property with getter and setter over it, both emitting `DeprecationWarning`; add `__setstate__` that moves a pickled `frf_type` to `frf_estimator`. Verify: tests read and set `frf.frf_type` under `pytest.warns(DeprecationWarning)`, and unpickle an object whose state dict holds `frf_type`
- [x] 2.3 Change `get_FRF` to `get_FRF(self, frf_estimator='default', frf_form='receptance', *, type=None, form=None)` with the same warn-and-win behaviour. Update docstrings and error messages to the new names. Leave the private constants `_FRF_TYPES` and `_FRF_FORM` as they are. Verify: tests that `get_FRF('H1', 'accelerance')`, `get_FRF(frf_estimator='H1', frf_form='accelerance')` and `get_FRF(type='H1', form='accelerance')` return equal arrays, and only the last warns
- [x] 2.4 Update `readme.rst`, `docs/source/tutorial.rst`, `Showcase.ipynb` and `tests/test_pyFRF.py:794` to the new names, noting "since 1.5.0" in the README. Verify: `grep -rnE "frf_type|type=|form=" readme.rst docs Showcase.ipynb` finds only the deprecation note
- [x] 2.5 Run the suite with `-W error::DeprecationWarning` to prove that no internal call uses an old name. If a third-party warning fails the run, add a targeted `filterwarnings` entry for it only. Verify: `pytest -W error::DeprecationWarning` passes
- [ ] 2.6 Set version 1.5.0 and add a release note. Open the PR linking the hub PR. Verify: CI green; release after merge (maintainer)

## 3. sdypy-FRF (ladisk/sdypy-FRF)

- [x] 3.1 Set `pyFRF >= 1.5` in `pyproject.toml` and version 0.3.0. Verify: `python ../../sdypy/tools/check_sibling_template.py --path .` exits 0
- [x] 3.2 Update `README.rst` and `tests/test_frf.py` to `frf_estimator=` and `frf_form=`. Verify: `pytest -W error::DeprecationWarning` passes against pyFRF 1.5.0
- [ ] 3.3 Open the PR linking the hub PR, after pyFRF 1.5.0 is on PyPI. Verify: CI green

## 4. sdypy-EMA (ladisk/sdypy-EMA)

- [x] 4.1 Change `Model.add_frf()` from `get_FRF(form='receptance')` to `get_FRF('default', 'receptance')`, and add a test for `add_frf` with a small pyFRF object (none exists today). Verify: the test passes with pyFRF 1.4.0 and with 1.5.0 under `-W error::DeprecationWarning`
- [x] 4.2 Rename the `frf_type` parameter of the public `LSFD`, `LSFD_proportional` and `LSFD_old` functions to `frf_form` in the same position, with a keyword-only deprecated `frf_type` (design D4). Verify: tests that the old keyword warns and gives the same result, and that positional calls do not warn
- [x] 4.3 Update `docs/source/tutorial.rst` to `frf_form=` and add the missing changelog entries (0.28 to 0.31), including the `frf_type` → `frf_form` renames. Verify: `grep -rn frf_type docs/source` finds only changelog lines; the docs build
- [x] 4.4 Set version 0.31.0. Open the PR linking the hub PR. Verify: CI green; `python ../../sdypy/tools/check_nomenclature.py --path . | grep frf_type` lists only the `Model.__init__` and `LSFD*` deprecated-alias parameters

## 5. pyEMA (ladisk/pyEMA)

- [x] 5.1 Update `docs/source/tutorial.rst` to `frf_form=`. Verify: `grep -rn frf_type docs` is empty
- [x] 5.2 Align pyEMA's version with sdypy-EMA: set `__version__` to 0.31.0 and the dependency to `sdypy-EMA>=0.31`. Verify: `python -c "import pyEMA; print(pyEMA.__version__)"` prints 0.31.0
- [ ] 5.3 Open the PR linking the hub PR, after sdypy-EMA 0.31.0 is on PyPI. Verify: `pytest` passes

## 6. Close out

- [ ] 6.1 Cross-package check: in a fresh `uv venv` with all merged branches installed, run the hub `pytest -m "not pypi_artifacts" -W error::DeprecationWarning`. Verify: green, or every failure traced to a third-party warning
- [x] 6.2 PR #6 merged on 2026-09-28; its note is replaced by the `frf_estimator` note in the merge commit
- [ ] 6.3 After the last package PR merges, run `openspec archive canonicalize-frf-estimator` as the final hub commit, carrying the REQUIREMENTS.md update. Verify: `openspec validate --all --strict` passes
