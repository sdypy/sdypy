## 1. Umbrella facade alias

- [x] 1.1 In `sdypy/__init__.py`, add an `_ALIASES = {"sep005": "sdypy_sep005"}` mapping with an explanatory comment (sep005 is the SEP 5 standard/validator leaf, exposed for discoverability, NOT a `sdypy.sep005` namespace portion). Keep `_SUBPACKAGES` unchanged.
- [x] 1.2 Extend `__getattr__` to resolve `_ALIASES`: if `name in _ALIASES`, `import_module(_ALIASES[name])`, cache into `globals()[name]`, and return it. Keep the existing `_SUBPACKAGES` branch and the final `AttributeError`.
- [x] 1.3 Set `__all__ = list(_SUBPACKAGES) + list(_ALIASES)` and update `__dir__` to return `sorted(set(globals()) | set(_SUBPACKAGES) | set(_ALIASES))`.

## 2. Tests

- [x] 2.1 In `tests/test_public_api.py`, update `test_umbrella_all_is_exactly_the_six_names` (rename to reflect six + sep005): assert `sorted(sdypy.__all__) == sorted(list(_SUBPACKAGES) + ["sep005"])`, and that `"sep005"` is in `dir(sdypy)`. Import `_ALIASES` from `sdypy` if convenient, or hard-code `["sep005"]`.
- [x] 2.2 Add a test `test_sep005_alias_resolves`: assert `sdypy.sep005 is importlib.import_module("sdypy_sep005")` and `callable(sdypy.sep005.assert_sep005)`. No `pypi_artifacts` marker (the dep is installed; runs in CI).
- [x] 2.3 Update `test_star_import_of_umbrella_yields_six_subpackages` to also expect `sep005` in the star-imported namespace (rename/adjust the assertion to six + sep005).
- [x] 2.4 Gate: from the core repo run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest tests/test_public_api.py -q` and confirm green; then `-m "not pypi_artifacts"` over the full suite stays green.

## 3. Documentation

- [x] 3.1 Add a `sep005` row to the README package table in `README.rst`: "Unified-timeseries standard (SEP 5) + compliance validator; reachable as `sd.sep005` (→ `sdypy_sep005`)."
- [x] 3.2 Add a sep005 entry to `docs/source/packages.rst`, distinguished from the six sub-packages (it is the SEP 5 standard/validator), linking the `sdypy-sep005` distribution and SEP 5, and noting `sdypy.FRF.assert_sep005` re-exports the validator.
- [x] 3.3 Gate: rebuild the core docs (`python docs/seps/tools/build_index.py` then `sphinx-build -b html docs/source docs/_build/html`) and confirm it still succeeds; `python tools/check_docs.py --path .` exits 0.

## 4. SEP 5 ratification

- [x] 4.1 Edit `docs/seps/sep-0005.rst`: replace the "A package to test compliance with the standard is to be developed" wording with a note that it exists (`sdypy-sep005`, exposed as `sd.sep005`); add a short "Reference implementation / access" subsection. Do NOT change `:Status: Draft` — the flip to Accepted is a gated team act (task 5.3).

## 5. Verification

- [x] 5.1 Run the full core suite from the core repo: `python -m pytest -m "not pypi_artifacts"` — all green (including the new/updated sep005 tests). Confirm the full run's only reds remain the known `pypi_artifacts`-marked PyPI-artifact tests.
- [x] 5.2 Run `openspec validate expose-sep005-standard --strict` and confirm no errors.
- [ ] 5.3 (Deferred, team-gated — NOT done here) Flip `docs/seps/sep-0005.rst` `:Status: Draft` → `Accepted` with a `:Resolution:` at the final review, alongside the SEP 2/3 flips.
