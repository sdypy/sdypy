## MODIFIED Requirements

### Requirement: Conformance checking
Drift from the template SHALL be detectable mechanically without a manual audit. The core repository SHALL provide two conformance layers: (1) distribution-layer checks in `tests/test_namespace_conformance.py` that verify published PyPI artifacts; they carry the `pypi_artifacts` marker, so they run in a plain local `pytest` as the release-time gate and are deselected on GitHub CI (`testing-ci` *GitHub CI deselects pypi_artifacts and the matrix is green*) (no `setup.py`/`requirements*.txt` in sdists, wheel contains only the namespace portion, version metadata present); (2) a repo-layer checker script `tools/check_sibling_template.py` that audits a sibling working clone by path, covering root-file hygiene, pyproject shape, workflow file names and matrices, and `__init__.py` version derivation pattern.

#### Scenario: Distribution-layer checks detect setup.py in a published sdist
- **WHEN** `tests/test_namespace_conformance.py` is run locally with plain `pytest` and a sibling's latest PyPI sdist contains `setup.py`
- **THEN** the corresponding test for that package fails, signalling a conformance regression

#### Scenario: Distribution-layer checks detect sdypy/__init__.py in a published wheel
- **WHEN** `tests/test_namespace_conformance.py` is run locally with plain `pytest` and a sibling's latest PyPI wheel contains `sdypy/__init__.py`
- **THEN** the corresponding test for that package fails

#### Scenario: Distribution-layer checks do not run on GitHub CI
- **WHEN** the core `python-package.yml` workflow runs `pytest -m "not pypi_artifacts"`
- **THEN** none of the distribution-layer tests in `tests/test_namespace_conformance.py` is collected

#### Scenario: Repo-layer checker detects stale setup.py in a clone
- **WHEN** `python tools/check_sibling_template.py --path packages/sdypy-EMA` is run in the core repo
- **THEN** if `packages/sdypy-EMA/setup.py` exists the script exits non-zero and reports the violation

#### Scenario: Repo-layer checker detects wrong workflow file name
- **WHEN** `python tools/check_sibling_template.py --path packages/sdypy-view` is run and `pytest.yaml` still exists instead of `python-package.yml`
- **THEN** the script exits non-zero and reports the wrong filename
