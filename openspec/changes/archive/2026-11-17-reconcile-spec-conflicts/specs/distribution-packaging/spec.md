## MODIFIED Requirements

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
- **THEN** sphinx, pydata-sphinx-theme, and sphinx-copybutton are installed at their required minimum versions
- **AND** no competing theme (`sphinx-rtd-theme`, `sphinx-book-theme`) is installed by the extra

### Requirement: Version single-sourced everywhere
The package version SHALL appear in exactly one authoritative location (`pyproject.toml`). Every other location that must display the version — including `sdypy.__version__` (established by `namespace-packaging`) and the documentation build — SHALL derive it from installed distribution metadata at runtime, not duplicate it as a hard-coded string.

#### Scenario: docs/source/conf.py derives version from metadata
- **WHEN** the Sphinx configuration (`docs/source/conf.py`) is executed during a docs build
- **THEN** the `release` variable is set to the value of `importlib.metadata.version("sdypy")` rather than a hard-coded string

#### Scenario: docs version matches installed package version
- **WHEN** `sdypy` version `X.Y.Z` is installed and a docs build is run
- **THEN** the generated documentation reports release `X.Y.Z` and version `X.Y` without any manual update to `conf.py`
