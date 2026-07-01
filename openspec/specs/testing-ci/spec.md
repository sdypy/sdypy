# testing-ci Specification

## Purpose
The contract for the SDyPy testing and CI baseline: a registered `pypi_artifacts` marker deselected on GitHub CI, a green core test matrix, canonical core test and release workflows, a real functional test baseline for every first-level package, and a core interop suite exercising cross-package composition. Established by the `establish-testing-ci-baseline` change.

**Scope:** Mixed — umbrella-local for the core test suite, marker, and workflow shape; **org-wide** for the *Every first-level package has a real functional test baseline* and *All seven fork CIs are green* requirements, which bind the six siblings.

## Requirements
### Requirement: pypi_artifacts marker registered and applied to all PyPI-dependent tests
The core `pyproject.toml` SHALL register a pytest marker named `pypi_artifacts` under `[tool.pytest.ini_options]`, and `testpaths` SHALL be set to `["tests"]`. Every core test that fetches published artifacts from PyPI over HTTP (`test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`) or that asserts conformance of installed distributions that come from PyPI in CI (`test_sibling_ships_no_namespace_init` in `test_namespace_conformance.py`; the per-sibling `__all__` tests in `test_public_api.py`: `test_subpackage_declares_nonempty_all`, `test_every_all_entry_resolves`, `test_no_banned_leak_names_in_all`, `test_module_entries_only_where_sanctioned`, `test_curated_surface_matches_spec`) MUST be decorated with `@pytest.mark.pypi_artifacts`. Umbrella-level tests (`test_umbrella_all_is_exactly_the_six_names`, the star-import test, and the drift advisory test) MUST remain unmarked.

#### Scenario: Marker is registered in pyproject.toml
- **WHEN** `pyproject.toml` in the core repo is inspected
- **THEN** `[tool.pytest.ini_options]` contains a `markers` entry that declares `pypi_artifacts: "tests that fetch or assert PyPI-published artifact conformance"` (or equivalent description)
- **AND** `testpaths = ["tests"]` is present in the same section

#### Scenario: PyPI-fetching and per-sibling distribution tests carry the marker
- **WHEN** `tests/test_namespace_conformance.py` and `tests/test_public_api.py` are inspected
- **THEN** `test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`, and `test_sibling_ships_no_namespace_init` are decorated with `@pytest.mark.pypi_artifacts`
- **AND** the five per-sibling parametrized tests in `test_public_api.py` are decorated with `@pytest.mark.pypi_artifacts`

#### Scenario: Umbrella-level tests remain unmarked
- **WHEN** `tests/test_public_api.py` is inspected
- **THEN** `test_umbrella_all_is_exactly_the_six_names`, the star-import test, and the drift advisory test have no `pypi_artifacts` decoration

### Requirement: GitHub CI deselects pypi_artifacts and the matrix is green
The core GitHub CI test workflow SHALL run pytest with `-m "not pypi_artifacts"` to deselect the marked set. A plain local `pytest` invocation (no `-m` flag) SHALL still collect and run all tests, including the marked set. The marked set constitutes the local, release-time gate; it MUST NOT be required to pass on the GitHub server.

#### Scenario: CI command deselects marked tests
- **WHEN** the core `python-package.yml` workflow file is inspected
- **THEN** the pytest step uses the argument `-m "not pypi_artifacts"` (or equivalent quoting)

#### Scenario: Plain local pytest collects all tests including marked set
- **WHEN** `pytest --collect-only` is run locally in the core repo without any `-m` flag
- **THEN** `test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`, and the per-sibling parametrized tests appear in the collected set

#### Scenario: CI matrix is green
- **WHEN** the core `python-package.yml` workflow runs on a push or pull request
- **THEN** all matrix jobs (Python 3.10, 3.11, 3.12) complete with success status

### Requirement: Core test workflow has the required shape
The core `python-package.yml` MUST be triggered on `push`, `pull_request`, and `workflow_dispatch` events. The matrix SHALL cover Python versions `["3.10", "3.11", "3.12"]` with `fail-fast: false`. The workflow MUST use `actions/checkout@v4` and `actions/setup-python@v5`. The install step SHALL run `pip install .` followed by `pip install pytest flake8 build`. The workflow MUST include the existing two-pass flake8 check, the `pytest -m "not pypi_artifacts"` step, and a final `python -m build` validation step.

#### Scenario: Workflow triggers are correct
- **WHEN** `python-package.yml` is inspected
- **THEN** the `on:` section lists `push`, `pull_request`, and `workflow_dispatch`

#### Scenario: Matrix and action versions are correct
- **WHEN** `python-package.yml` is inspected
- **THEN** the matrix is `["3.10", "3.11", "3.12"]` with `fail-fast: false`
- **AND** `actions/checkout@v4` and `actions/setup-python@v5` are used (no `@v3`, `@v4` for setup-python, or older versions)

#### Scenario: Workflow includes build validation step
- **WHEN** `python-package.yml` is inspected
- **THEN** a step running `python -m build` is present after the pytest step

### Requirement: Core release workflow has the required shape
The core `release-and-publish-to-pypi.yml` MUST use `actions/checkout@v4`, `actions/setup-python@v5`, build via `pip install --upgrade pip build` then `python -m build`, and publish via `pypa/gh-action-pypi-publish@release/v1` with `password: ${{ secrets.PYPI_API_TOKEN }}` (token auth; trusted publishing is deferred).

#### Scenario: Release workflow uses current action versions and token auth
- **WHEN** `release-and-publish-to-pypi.yml` is inspected
- **THEN** `actions/checkout@v4` and `actions/setup-python@v5` are used
- **AND** the publish step uses `pypa/gh-action-pypi-publish@release/v1` with `password: ${{ secrets.PYPI_API_TOKEN }}`
- **AND** no deprecated `@v2`, `@v1.4.2`, or `@v3`/`@v4` action versions remain

### Requirement: Every first-level package has a real functional test baseline
Every first-level package (`sdypy-FRF`, `sdypy-excitation`, `sdypy-io`, `sdypy-view`, `sdypy-model`, `sdypy-EMA`) MUST have at least one real functional test (i.e., a test that exercises the package's own code and asserts a non-trivial behavioral property, not a bare `assert True`). Tests MUST be seeded, require no network access, and require no display. The minimum per-package baselines are: FRF — H1 estimation peak, axis length, and `assert_sep005` valid/invalid paths; excitation — shape/dtype and statistical properties for the eleven curated functions; io — `uff` write→read round-trip, `lvm` parse of a generated file, `sfmov` if hand-constructable (else document-and-skip); view — pure helper shapes and `Plotter3D` `ImportError` path (Qt-free); model — `Beam.solve()` vs analytical frequencies (rtol ≤ 5%), `solve_eigenvalue` on analytic 2-DOF, `lumped` 1-DOF eigenfrequency, `Shell`/`Tetrahedron` matrix properties; EMA — existing accuracy assertions pass unchanged after `pol_order_high` reduction.

#### Scenario: sdypy-FRF has functional H1 and sep005 tests
- **WHEN** the sdypy-FRF test suite is run
- **THEN** a test constructs a synthetic SDOF response, computes H1 via `sdypy.FRF.FRF`, and asserts the magnitude peaks near the resonance frequency
- **AND** a test asserts that `assert_sep005` accepts a valid minimal sep005 dict and raises on an invalid one

#### Scenario: sdypy-excitation has statistical sanity tests for all eleven functions
- **WHEN** the sdypy-excitation test suite is run
- **THEN** tests cover all eleven curated functions: output shape and dtype are verified; `uniform_random` output is within its bounds; `normal_random` mean and standard deviation are within expected tolerances; `sine_sweep` instantaneous-frequency endpoints match the specified range; `get_psd` and `get_kurtosis` return known values on deterministic inputs

#### Scenario: sdypy-io has a uff write→read round-trip test
- **WHEN** the sdypy-io test suite is run
- **THEN** a test constructs FRF data, passes it through `sdypy.io.uff.prepare_58`, writes it to a temporary file, reads it back, and asserts numeric equality with the original data

#### Scenario: sdypy-view tests pure helpers without PyQt6
- **WHEN** the sdypy-view test suite is run in an environment where PyQt6 is absent
- **THEN** `create_fem_mesh` returns a valid mesh object for a toy quad element, `prepare_animation_displacements` and `prepare_animation_field` return arrays with the expected shapes, and instantiating `Plotter3D` raises `ImportError` mentioning `PyQt6`

#### Scenario: sdypy-model Beam frequencies match analytical values
- **WHEN** the sdypy-model test suite is run
- **THEN** `Beam.solve()` for a cantilever beam returns first natural frequencies within 5% rtol of the analytical Euler–Bernoulli values
- **AND** `solve_eigenvalue` on an analytic 2-DOF K/M system returns eigenfrequencies matching the hand-computed values
- **AND** `Shell.construct_global_matrices` and `Tetrahedron.assemble_matrices` produce symmetric stiffness and mass matrices with non-negative eigenvalues on minimal elements

#### Scenario: sdypy-EMA runtime cut preserves accuracy
- **WHEN** the sdypy-EMA test suite is run after reducing `pol_order_high` from 60 to 30 in heavy fixtures
- **THEN** all existing accuracy assertions pass unchanged (identified natural frequencies and damping ratios remain within the original tolerance bounds)

### Requirement: Core interop suite exercises cross-package composition
The core repo SHALL contain `tests/test_interop.py` with four test areas: (1) `sdypy.model.lumped` → `sdypy.EMA` pole identification; (2) `sdypy.excitation` signal → `sdypy.model.lumped` response → `sdypy.FRF` H1 estimate → `sdypy.EMA` identification (end-to-end flagship chain); (3) `sdypy.io.uff` FRF data round-trip; (4) `sdypy.FRF.assert_sep005` smoke. All imports MUST use the `sdypy.*` namespace only (not backend packages directly). All tests MUST be seeded, use tolerance-based assertions (rtol 2–5%), and carry no `pypi_artifacts` marker (they MUST run in CI).

#### Scenario: lumped→EMA identification is accurate
- **WHEN** `test_interop.py` runs the lumped→EMA test with a fixed seed
- **THEN** a 2-DOF `sdypy.model.lumped.Model` produces an FRF matrix, `sdypy.EMA.Model` identifies poles, and the identified natural frequencies and damping ratios are within 2% rtol of the values returned by `sdypy.model.lumped.Model.get_eig_freq()` and `get_damping_ratios()`

#### Scenario: Flagship end-to-end chain identifies correct frequencies
- **WHEN** `test_interop.py` runs the excitation→lumped→FRF→EMA chain with a fixed seed
- **THEN** `sdypy.excitation.pseudo_random` generates an excitation signal; `sdypy.model.lumped` computes a response; `sdypy.FRF.FRF` produces an H1 estimate; `sdypy.EMA` identifies natural frequencies within 5% rtol of the lumped model's analytic frequencies

#### Scenario: io uff round-trip preserves FRF data
- **WHEN** `test_interop.py` runs the io round-trip test
- **THEN** FRF data prepared via `sdypy.io.uff.prepare_58`, written to a temporary file, and read back is numerically equal to the original data

#### Scenario: sep005 smoke test passes and fails correctly
- **WHEN** `test_interop.py` runs the sep005 smoke tests
- **THEN** `sdypy.FRF.assert_sep005` accepts a minimal valid sep005 timeseries dict without raising
- **AND** `sdypy.FRF.assert_sep005` raises when given an invalid dict

#### Scenario: Interop tests run in CI (no pypi_artifacts marker)
- **WHEN** `pytest --collect-only -m "not pypi_artifacts"` is run in the core repo
- **THEN** all tests from `test_interop.py` appear in the collected set

### Requirement: Sibling workflow files are not modified by this change
The workflow files (`.github/workflows/`) in all six sibling repositories (`sdypy-EMA`, `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`, `sdypy-view`, `sdypy-model`) MUST remain byte-identical after this change's commits. Only test files (in `tests/`) are added or modified in sibling repositories; no version bumps and no packaging changes are introduced.

#### Scenario: Sibling workflow files unchanged after this change
- **WHEN** the diff for each sibling repository produced by this change is inspected
- **THEN** no `.github/workflows/` file appears in the diff for any sibling repo

#### Scenario: Sibling test additions fold into pending unreleased versions
- **WHEN** the sdist of any sibling package that gained new tests is built from the pending unreleased version
- **THEN** the built sdist includes the new test files (via the existing template allow-list) and the package version number is unchanged from the pending release version

### Requirement: All seven fork CIs are green after this change's pushes
After the test-suite commits are pushed to all sibling forks and the core workflow rewrite is pushed to the core fork, the latest GitHub Actions workflow run on each of the seven `ladisk` fork repositories (sdypy, sdypy-EMA, sdypy-io, sdypy-FRF, sdypy-excitation, sdypy-view, sdypy-model) SHALL conclude with a success status. Forks that have never had a workflow run (EMA, io, FRF, excitation) SHALL receive their first successful run from the pushes in this change.

#### Scenario: All seven fork CI runs conclude success
- **WHEN** the pushes from this change have been made to all seven ladisk forks
- **THEN** the latest workflow run on each of the seven ladisk fork repositories shows a success conclusion
- **AND** the four previously-silent forks (sdypy-EMA, sdypy-io, sdypy-FRF, sdypy-excitation) show their first-ever successful run

