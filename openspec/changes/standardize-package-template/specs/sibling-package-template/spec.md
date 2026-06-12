## Purpose
The contract that every first-level sdypy namespace package (sdypy-EMA, sdypy-io, sdypy-FRF, sdypy-excitation, sdypy-view, sdypy-model) must satisfy to maintain a uniform, maintainable packaging baseline — single build definition, metadata-derived version, correct namespace layout, clean distributions, standardized CI and release workflows, consistent metadata, and valid repo scaffolding. Established by the `standardize-package-template` change.

## ADDED Requirements

### Requirement: Single build definition
Every first-level sdypy namespace package SHALL define build metadata, runtime dependencies, optional extras, and the package version in `pyproject.toml` only. No secondary build script (`setup.py`, `setup.cfg`), standalone dependency file (`requirements*.txt`), version synchronisation script (`sync_version.py`), or legacy CI configuration file (`.travis.yml`) SHALL exist at the repository root.

#### Scenario: No setup.py present
- **WHEN** the sibling repository working tree is inspected
- **THEN** no `setup.py` file exists at the repository root

#### Scenario: No standalone requirements files present
- **WHEN** the sibling repository working tree is inspected
- **THEN** no `requirements.txt` or `requirements.dev.txt` file exists at the repository root

#### Scenario: No sync_version.py present
- **WHEN** the sibling repository working tree is inspected
- **THEN** no `sync_version.py` file exists at the repository root

#### Scenario: No .travis.yml present
- **WHEN** the sibling repository working tree is inspected
- **THEN** no `.travis.yml` file exists at the repository root

#### Scenario: pip install from pyproject installs runtime deps
- **WHEN** a user runs `pip install .` in a clean virtual environment from a directory that is not the parent `SdyPy/` folder
- **THEN** all runtime dependencies declared in `[project] dependencies` are installed without requiring any separate requirements file

### Requirement: Version single-sourced via installed metadata
Every first-level sdypy namespace package SHALL declare the authoritative version as a literal string in the `[project]` table of `pyproject.toml`. The corresponding `sdypy/<pkg>/__init__.py` SHALL derive `__version__` from installed distribution metadata via `importlib.metadata.version("sdypy-<pkg>")` with a `PackageNotFoundError` fallback of `"0+unknown"`. No `sync_version.py` script and no version-sync step in any workflow SHALL exist.

#### Scenario: pyproject.toml contains literal version
- **WHEN** `pyproject.toml` is inspected
- **THEN** the `[project]` table contains a `version = "X.Y.Z"` literal (not `dynamic = ["version"]`)

#### Scenario: __init__.py derives __version__ from metadata
- **WHEN** `sdypy/<pkg>/__init__.py` is inspected
- **THEN** it contains `importlib.metadata.version("sdypy-<pkg>")` and a `PackageNotFoundError` handler that sets `__version__ = "0+unknown"`

#### Scenario: __version__ matches installed distribution after pip install
- **WHEN** the package is installed with `pip install .` (from a neutral directory, not the parent `SdyPy/` folder) and `import sdypy.<pkg>; print(sdypy.<pkg>.__version__)` is executed
- **THEN** the printed string matches the `version` field in `pyproject.toml`

#### Scenario: __version__ fallback in uninstalled source checkout
- **WHEN** `sdypy/<pkg>/__init__.py` is imported in a Python process where the distribution metadata is not present
- **THEN** `__version__` equals `"0+unknown"` without raising an exception

#### Scenario: Release workflow contains no version-sync step
- **WHEN** `.github/workflows/release-and-publish-to-pypi.yml` is inspected
- **THEN** no step references `sync_version.py` or any other version-synchronisation command

### Requirement: Native namespace portion and wheel contents
Every first-level sdypy namespace package SHALL ship a wheel that contains only the `sdypy/<pkg>/` namespace portion and SHALL NOT include a top-level `sdypy/__init__.py`. Namespace packaging layout requirements are governed by the `namespace-packaging` spec; this requirement applies only to wheel contents and build configuration. The `[tool.hatch.build.targets.wheel]` table SHALL list only `"sdypy"` (the namespace root) as the packages entry — listing `"sdypy/<pkg>"` makes hatchling strip the namespace prefix and ship `<pkg>/` at the wheel top level, breaking `import sdypy.<pkg>`.

#### Scenario: Wheel does not contain sdypy/__init__.py
- **WHEN** `python -m build --wheel` is run and the resulting `.whl` is inspected
- **THEN** the archive contains no entry named `sdypy/__init__.py`

#### Scenario: Wheel contains only the package namespace portion
- **WHEN** the wheel is inspected
- **THEN** all `sdypy/` entries are under `sdypy/<pkg>/` and no other top-level `sdypy/` file is present

#### Scenario: pyproject wheel target declares the namespace root
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[tool.hatch.build.targets.wheel]` contains `packages = ["sdypy"]` and no other package entry

#### Scenario: Wheel ships the portion under the namespace prefix
- **WHEN** the built wheel is inspected
- **THEN** it contains entries under `sdypy/<pkg>/` (not `<pkg>/` at the archive top level), so `import sdypy.<pkg>` resolves after installation

### Requirement: sdist contains only an explicit allow-list
Every first-level sdypy namespace package SHALL publish an sdist that includes source code, tests, documentation source, README, LICENSE, and `pyproject.toml` only. The `[tool.hatch.build.targets.sdist]` table SHALL declare an explicit `include` allow-list. The sdist SHALL NOT contain `_build/` output, deleted packaging artefacts (`setup.py`, `requirements*.txt`, `.travis.yml`, `sync_version.py`), or large binary test data directories (e.g. EMA's `data/`).

#### Scenario: sdist excludes deleted artefacts
- **WHEN** `python -m build --sdist` is run and the resulting `.tar.gz` is inspected
- **THEN** the archive contains no `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`, or `sync_version.py`

#### Scenario: sdist excludes build output
- **WHEN** the sdist is inspected
- **THEN** no path under `_build/` is present in the archive

#### Scenario: sdist excludes large binary data directories
- **WHEN** the sdist for sdypy-EMA is inspected
- **THEN** no path under `data/` is present in the archive

#### Scenario: pyproject sdist target uses an explicit include list
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[tool.hatch.build.targets.sdist]` contains an `include` list that covers the source tree, `tests/`, docs source, README, LICENSE, and `pyproject.toml`

### Requirement: Canonical test workflow
Every first-level sdypy namespace package SHALL provide a GitHub Actions test workflow at `.github/workflows/python-package.yml`. The workflow SHALL trigger on push and pull-request events, run on `ubuntu-latest`, exercise a Python `[3.10, 3.11, 3.12]` matrix, install the package via `pip install .`, run `flake8` and `pytest`, include a `python -m build` validation step, and use non-deprecated action major versions (at minimum `actions/checkout@v4` and `actions/setup-python@v5`).

#### Scenario: Test workflow file is named python-package.yml
- **WHEN** `.github/workflows/` is inspected
- **THEN** a file named `python-package.yml` exists and no file named `pytest.yaml` exists

#### Scenario: Test workflow triggers on push and pull_request
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the `on:` block includes both `push` and `pull_request` triggers

#### Scenario: Test workflow matrix covers Python 3.10, 3.11, and 3.12
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the matrix `python-version` list contains exactly `["3.10", "3.11", "3.12"]`

#### Scenario: Test workflow installs package via pip install dot
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the install step is `pip install .` and no step reads a `requirements*.txt` file

#### Scenario: Test workflow includes build validation step
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** a step runs `python -m build` so a broken sdist or wheel fails CI rather than the next release

#### Scenario: Test workflow uses non-deprecated action versions
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** every `uses:` reference to `actions/checkout` is at `@v4` or later and every reference to `actions/setup-python` is at `@v5` or later

### Requirement: Canonical release workflow
Every first-level sdypy namespace package SHALL provide a GitHub Actions release workflow at `.github/workflows/release-and-publish-to-pypi.yml`. The workflow SHALL trigger on `v*` tag pushes, build both an sdist and a wheel, publish to PyPI, and SHALL NOT contain a version-sync step. No file named with an underscore variant (e.g. `release_and_publish_to_pypi.yml`) SHALL exist.

#### Scenario: Release workflow file is named release-and-publish-to-pypi.yml
- **WHEN** `.github/workflows/` is inspected
- **THEN** a file named `release-and-publish-to-pypi.yml` exists and no underscore-separated variant of that name exists

#### Scenario: Release workflow triggers on v* tag
- **WHEN** `.github/workflows/release-and-publish-to-pypi.yml` is inspected
- **THEN** the `on:` block triggers on `push` with a `tags:` filter matching `v*`

#### Scenario: Release workflow builds sdist and wheel
- **WHEN** `.github/workflows/release-and-publish-to-pypi.yml` is inspected
- **THEN** a step runs `python -m build` (or equivalent) producing both an sdist and a wheel

#### Scenario: Release workflow publishes to PyPI
- **WHEN** `.github/workflows/release-and-publish-to-pypi.yml` is inspected
- **THEN** a step uses `pypa/gh-action-pypi-publish` or equivalent to publish the built distributions

### Requirement: Metadata consistency
Every first-level sdypy namespace package SHALL declare the hatchling build backend, `requires-python = ">=3.10"`, an MIT license, `Programming Language :: Python :: 3.x` classifiers for every Python minor version in the CI matrix (3.10, 3.11, 3.12), `project.urls` whose Homepage and Source entries point at the package's own repository (the Documentation entry SHALL resolve either to the package's own hosted documentation or, for a thin wrapper without hosted docs, to its backend library's documentation), and both `dev` and `docs` optional-dependency extras. The `dev` extra SHALL reference the `docs` extra rather than duplicating its entries.

#### Scenario: hatchling is the declared build backend
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[build-system] build-backend` equals `"hatchling.build"`

#### Scenario: requires-python is at least 3.10
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project] requires-python` is `">=3.10"`

#### Scenario: Python version classifiers match CI matrix
- **WHEN** `pyproject.toml` and `.github/workflows/python-package.yml` are inspected
- **THEN** every Python minor version in the CI matrix has a corresponding `Programming Language :: Python :: 3.x` classifier and no extra classifier appears for a version not in the matrix

#### Scenario: Homepage and Source URLs point at the package's own repository
- **WHEN** `pyproject.toml` is inspected for any first-level sdypy package
- **THEN** the `[project.urls]` Homepage and Source entries resolve to that package's own repository, not a backend library's

#### Scenario: Documentation URL of a thin wrapper resolves to its backend's docs
- **WHEN** `pyproject.toml` is inspected for sdypy-FRF or sdypy-excitation
- **THEN** the `[project.urls]` Documentation entry resolving to pyFRF's or pyExSi's documentation is conformant, because these wrappers have no hosted documentation of their own

#### Scenario: dev and docs extras are declared
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project.optional-dependencies]` contains both a `docs` key and a `dev` key; the `dev` list includes a self-referencing `sdypy-<pkg>[docs]` entry

### Requirement: Repository scaffolding
Every first-level sdypy namespace package SHALL declare the correct README filename in `pyproject.toml` (matching the actual file present in the repository), include a `LICENSE` file, provide a valid `readthedocs.yaml` that installs the package via the `docs` extra, and include a `.gitignore` that covers `dist/`, `_build/`, and `*.egg-info/` build output patterns.

#### Scenario: readme field matches actual README file
- **WHEN** `pyproject.toml` is inspected and the repository root is listed
- **THEN** the value of `[project] readme` equals the filename of the README present in the repository root (e.g. `"README.rst"` when `README.rst` exists, `"README.md"` when `README.md` exists)

#### Scenario: LICENSE file is present
- **WHEN** the repository root is listed
- **THEN** a file named `LICENSE` (with or without extension) exists

#### Scenario: readthedocs.yaml installs via docs extra
- **WHEN** `readthedocs.yaml` is inspected
- **THEN** the `python.install` section uses `method: pip`, `path: .`, and `extra_requirements: [docs]`

#### Scenario: .gitignore covers build output
- **WHEN** `.gitignore` is inspected
- **THEN** patterns matching `dist/`, `_build/`, and `*.egg-info` are present

### Requirement: Conformance checking
Drift from the template SHALL be detectable mechanically without a manual audit. The core repository SHALL provide two conformance layers: (1) distribution-layer checks in `tests/test_namespace_conformance.py` that run in core CI on every push and verify published PyPI artifacts (no `setup.py`/`requirements*.txt` in sdists, wheel contains only the namespace portion, version metadata present); (2) a repo-layer checker script `tools/check_sibling_template.py` that audits a sibling working clone by path, covering root-file hygiene, pyproject shape, workflow file names and matrices, and `__init__.py` version derivation pattern.

#### Scenario: Distribution-layer checks detect setup.py in a published sdist
- **WHEN** `tests/test_namespace_conformance.py` is run in core CI and a sibling's latest PyPI sdist contains `setup.py`
- **THEN** the corresponding test for that package fails, signalling a conformance regression

#### Scenario: Distribution-layer checks detect sdypy/__init__.py in a published wheel
- **WHEN** `tests/test_namespace_conformance.py` is run in core CI and a sibling's latest PyPI wheel contains `sdypy/__init__.py`
- **THEN** the corresponding test for that package fails

#### Scenario: Repo-layer checker detects stale setup.py in a clone
- **WHEN** `python tools/check_sibling_template.py --path packages/sdypy-EMA` is run in the core repo
- **THEN** if `packages/sdypy-EMA/setup.py` exists the script exits non-zero and reports the violation

#### Scenario: Repo-layer checker detects wrong workflow file name
- **WHEN** `python tools/check_sibling_template.py --path packages/sdypy-view` is run and `pytest.yaml` still exists instead of `python-package.yml`
- **THEN** the script exits non-zero and reports the wrong filename
