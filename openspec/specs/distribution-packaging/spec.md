## Purpose
The contract that the `sdypy` core repository maintains exactly one authoritative build and dependency definition (`pyproject.toml`), carries no stale packaging scripts or dead CI configurations, tracks no generated build artefacts in git, single-sources the package version in all locations it appears (package facade and documentation build), and publishes metadata classifiers that accurately reflect the tested Python support matrix. Established by the `packaging-hygiene-sweep` change.

**Scope:** Umbrella-local — the `sdypy` core distribution's own build, packaging, and metadata. The parallel contract for the six first-level sibling packages is `sibling-package-template`.

## Requirements

### Requirement: Single build definition
The repository SHALL define build metadata, runtime dependencies, optional extras, and the package version in `pyproject.toml` only. No secondary build script (`setup.py`, `setup.cfg`) or standalone dependency file (`requirements*.txt`) SHALL exist at the repository root or under `docs/`.

#### Scenario: No setup.py present
- **WHEN** the repository working tree is inspected
- **THEN** no `setup.py` file exists at the repository root

#### Scenario: No standalone requirements files present
- **WHEN** the repository working tree is inspected
- **THEN** no `requirements.txt`, `requirements.dev.txt`, or `docs/requirements.txt` files exist

#### Scenario: pip install from pyproject installs runtime deps
- **WHEN** a user runs `pip install .` in a clean virtual environment
- **THEN** all runtime dependencies declared in `[project] dependencies` are installed without requiring any separate requirements file

#### Scenario: pip install dev extra installs dev deps
- **WHEN** a user runs `pip install .[dev]` in a clean virtual environment
- **THEN** all development dependencies (test runner, build, linting tools) are installed

#### Scenario: pip install docs extra installs docs deps
- **WHEN** a user runs `pip install .[docs]` in a clean virtual environment
- **THEN** sphinx, sphinx-rtd-theme, and sphinx-copybutton are installed at their required minimum versions

### Requirement: No dead CI configuration
The repository SHALL NOT contain CI configuration files for services that are no longer used. The authoritative CI is GitHub Actions; no `.travis.yml` or other legacy CI file SHALL exist.

#### Scenario: No .travis.yml present
- **WHEN** the repository working tree is inspected
- **THEN** no `.travis.yml` file exists at the repository root

#### Scenario: GitHub Actions CI installs the package from pyproject
- **WHEN** the GitHub Actions test workflow runs
- **THEN** the `sdypy` package and its runtime dependencies are installed via `pip install .` before the test suite executes

#### Scenario: GitHub Actions CI does not reference deleted files
- **WHEN** the GitHub Actions test workflow runs
- **THEN** no step attempts to read `requirements.txt` or any other deleted file

### Requirement: No tracked build artefacts
The repository SHALL NOT track generated build output in git. Sphinx `_build/` directories at any nesting depth SHALL be listed in `.gitignore` and SHALL NOT appear in `git ls-files` output.

#### Scenario: docs/_build not tracked
- **WHEN** `git ls-files docs` is executed
- **THEN** the output contains no path that includes `_build`

#### Scenario: _build pattern in .gitignore
- **WHEN** `.gitignore` is inspected
- **THEN** it contains a pattern that matches `_build/` directories at any depth (e.g. the bare pattern `_build/`)

### Requirement: Version single-sourced everywhere
The package version SHALL appear in exactly one authoritative location (`pyproject.toml`). Every other location that must display the version — including `sdypy.__version__` (established by `namespace-packaging`) and the documentation build — SHALL derive it from installed distribution metadata at runtime, not duplicate it as a hard-coded string.

#### Scenario: docs/source/conf.py derives version from metadata
- **WHEN** the Sphinx configuration (`docs/source/conf.py`) is executed during a docs build
- **THEN** the `release` variable is set to the value of `importlib.metadata.version("sdypy")` rather than a hard-coded string

#### Scenario: docs version matches installed package version
- **WHEN** `sdypy` version 0.6.0 is installed and a docs build is run
- **THEN** the generated documentation reports release `0.6.0` and version `0.6` without any manual update to `conf.py`

### Requirement: sdist contains only source artefacts
The published sdist SHALL contain source code, tests, documentation source, examples, and project metadata files. It SHALL NOT contain generated build output (`_build/`), development workflow files (`openspec/`, `.claude/`), or deleted packaging artefacts.

#### Scenario: sdist excludes build output and dev workflow dirs
- **WHEN** `python -m build --sdist` is run and the resulting `.tar.gz` is inspected
- **THEN** the archive contains no path under `_build/`, `openspec/`, or `.claude/`

#### Scenario: sdist excludes deleted files
- **WHEN** the published sdist is inspected
- **THEN** it contains no `setup.py`, `.travis.yml`, `requirements.txt`, or `requirements.dev.txt`

#### Scenario: wheel contents unchanged
- **WHEN** `python -m build --wheel` is run and the resulting `.whl` is inspected
- **THEN** the wheel contains only the `sdypy/` package files (unchanged from before this sweep)

### Requirement: Classifiers reflect the tested support matrix
`pyproject.toml` SHALL list `Programming Language :: Python :: 3.x` classifiers for every minor Python version exercised by CI, and the `Development Status` classifier SHALL accurately reflect the project's maturity stage.

#### Scenario: Python version classifiers match CI matrix
- **WHEN** the CI test matrix (`.github/workflows/python-package.yml`) and `pyproject.toml` are inspected
- **THEN** every Python minor version tested in CI has a corresponding `Programming Language :: Python :: 3.x` classifier in pyproject

#### Scenario: Development status is Beta before v1.0
- **WHEN** `pyproject.toml` is inspected before the v1.0 release milestone
- **THEN** the `Development Status` classifier reads `4 - Beta`

### Requirement: Read the Docs install is complete and canonical
The Read the Docs build SHALL install `sdypy` and its documentation dependencies via the `docs` extra defined in `pyproject.toml`. No separate `docs/requirements.txt` SHALL be used.

#### Scenario: RTD config uses pip extra
- **WHEN** `readthedocs.yaml` is inspected
- **THEN** the install method is `pip` with `path: .` and `extra_requirements: [docs]`

#### Scenario: RTD build can import all documented sub-packages
- **WHEN** a Read the Docs build runs after `pip install .[docs]`
- **THEN** the Sphinx autodoc extensions can import `sdypy.EMA`, `sdypy.io`, `sdypy.FRF`, `sdypy.excitation`, `sdypy.model`, and `sdypy.view` without import errors (subject to the sub-packages being installed as runtime deps)
