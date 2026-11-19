## MODIFIED Requirements

### Requirement: pypi_artifacts marker registered and applied to all PyPI-dependent tests
The core `pyproject.toml` SHALL register a pytest marker named `pypi_artifacts` under `[tool.pytest.ini_options]`, and `testpaths` SHALL be set to `["tests"]`. Every core test that fetches published artifacts from PyPI over HTTP (`test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`) or that asserts conformance of installed distributions that come from PyPI in CI (`test_sibling_ships_no_namespace_init` in `test_namespace_conformance.py`; the per-sibling `__all__` tests in `test_public_api.py`: `test_subpackage_declares_nonempty_all`, `test_every_all_entry_resolves`, `test_no_banned_leak_names_in_all`, `test_module_entries_only_where_sanctioned`, `test_curated_surface_matches_spec`) MUST be decorated with `@pytest.mark.pypi_artifacts`. Umbrella-level tests (`test_umbrella_all_is_the_six_subpackages_plus_sep005`, the star-import test, and the drift advisory test) MUST remain unmarked.

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
- **THEN** `test_umbrella_all_is_the_six_subpackages_plus_sep005`, the star-import test, and the drift advisory test have no `pypi_artifacts` decoration

## REMOVED Requirements

### Requirement: Sibling workflow files are not modified by this change
**Reason**: A one-off constraint on the diffs of the archived `establish-testing-ci-baseline` change, written as a standing rule. Read as standing, it contradicts the newer `one-step-release` change (archived 2026-11-17), whose `sibling-package-template` requirement *Release workflow is the hub's file, copied verbatim* has every sibling replace its release workflow. The constraint was met when that change landed and has nothing left to verify.
**Migration**: None. Which sibling workflow files must exist and what they contain is governed by `sibling-package-template` (*Canonical test workflow on the supported Python set*, *Release workflow is the hub's file, copied verbatim*).

### Requirement: All seven fork CIs are green after this change's pushes
**Reason**: A one-off acceptance check on the `ladisk` fork repositories for the pushes of the archived `establish-testing-ci-baseline` change. Development now lands through PRs on the `sdypy` organisation repositories, and a green core CI is already required by *GitHub CI deselects pypi_artifacts and the matrix is green*; the fork check carries no live rule.
**Migration**: None. The matching item in `REQUIREMENTS.md` § Pending A is dropped with the roster update at archive.
