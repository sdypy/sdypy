## 1. Delta specs

- [x] 1.1 `documentation`: FRF Documentation URL is its own RTD site; `build_index.py` path; residue scenario title no longer calls io/FRF shims (verifier: `check_docs.py`, docs build in `docs.yml`)
- [x] 1.2 `distribution-packaging`: docs extra scenario names `pydata-sphinx-theme`; version scenario is version-agnostic (verifier: `check_docs.py`; docs build)
- [x] 1.3 `sibling-package-template`: distribution-layer checks are the `pypi_artifacts` local gate, not core CI (verifier: `python-package.yml` `-m "not pypi_artifacts"`; `pytest::test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`)
- [x] 1.4 `testing-ci`: current umbrella `__all__` test name; remove the two change-scoped requirements with reasons
- [x] 1.5 `sep005-standard`: alias resolves to `sdypy_sep005.sep005` (verifier: `pytest::test_sep005_alias_resolves_to_standalone_distribution`)

## 2. Verification

- [x] 2.1 `openspec validate reconcile-spec-conflicts --strict` and `openspec validate --all --strict` pass
- [x] 2.2 `pytest -m "not pypi_artifacts"` passes
- [ ] 2.3 CI green on the PR

## 3. Archive

- [ ] 3.1 With the archive: update `REQUIREMENTS.md` rows (drop the two removed `testing-ci` rows and the fork-CI item in § Pending A; fix the *Conformance checking* row and the `build_index.py` path) and hand-edit the `testing-ci` Purpose/Scope line that names the removed fork-CI requirement
