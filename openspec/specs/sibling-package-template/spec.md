# sibling-package-template Specification

## Purpose
The contract every first-level sibling distribution must match: a single hatchling build definition, version single-sourced from installed metadata, a native namespace portion (no `sdypy/__init__.py`) with allow-listed sdist and wheel contents, canonical test and release workflows, consistent metadata, and repository scaffolding — verified by `tools/check_sibling_template.py`. Established by the `standardize-package-template` change.

**Scope:** Org-wide — the template every first-level sibling distribution must match. The umbrella's own equivalents live in `distribution-packaging`.
## Requirements
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
Every first-level sdypy namespace package SHALL declare the authoritative version as a literal string in the `[project]` table of `pyproject.toml`. The corresponding `sdypy/<pkg>/__init__.py` SHALL derive `__version__` from installed distribution metadata via `importlib.metadata.version("sdypy-<pkg>")` with a `PackageNotFoundError` fallback of `"0+unknown"`. No `sync_version.py` script SHALL exist, and no workflow SHALL write the version anywhere except the release workflow's bump of `[project] version` in `pyproject.toml`.

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
- **WHEN** the workflows under `.github/workflows/` are inspected
- **THEN** no step references `sync_version.py`, and the only step that writes a version is the release workflow's bump of `[project] version` in `pyproject.toml`

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

### Requirement: Agent instructions link to the hub's org-wide rules
Every first-level sdypy namespace package SHALL provide an `AGENTS.md` at the repository root that contains the hub's link block verbatim. The link block is the region of the hub's `AGENTS.md` delimited by the marker comments `<!-- >>> sdypy hub links -->` and `<!-- <<< sdypy hub links -->`, markers included; the hub's copy is the block's only home, and a sibling MUST NOT edit its copy. Everything outside the markers belongs to the sibling.

#### Scenario: AGENTS.md carries the hub link block
- **WHEN** a sibling clone whose `AGENTS.md` contains the hub's link block unchanged is checked
- **THEN** no on-ramp violation is reported for `AGENTS.md`

#### Scenario: Missing AGENTS.md is reported
- **WHEN** a sibling clone has no `AGENTS.md` at the repository root
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: An edited or missing link block is reported
- **WHEN** a sibling's `AGENTS.md` has no marker-delimited link block, or its block differs from the hub's in any character
- **THEN** the checker reports that the link block does not match the hub's and exits non-zero

### Requirement: Claude Code reads AGENTS.md
Every first-level sdypy namespace package SHALL provide a `CLAUDE.md` at the repository root whose only content is the line `@AGENTS.md`, so that the tool-specific file renders `AGENTS.md` and never becomes a second home for instructions.

#### Scenario: CLAUDE.md is the one-line pointer
- **WHEN** a sibling's `CLAUDE.md` contains exactly `@AGENTS.md` and a trailing newline
- **THEN** no on-ramp violation is reported for `CLAUDE.md`

#### Scenario: A missing or extended CLAUDE.md is reported
- **WHEN** a sibling has no `CLAUDE.md`, or its `CLAUDE.md` contains anything besides the `@AGENTS.md` line
- **THEN** the checker reports it and exits non-zero

### Requirement: OpenSpec configuration carries the hub's shared rules
Every first-level sdypy namespace package other than the backend shim `sdypy-excitation` SHALL provide `openspec/config.yaml` whose `rules` block is the hub's shared rules block verbatim: the region of the hub's `openspec/config.yaml` delimited by the comment lines `# >>> shared rules from the sdypy hub` and `# <<< shared rules`, markers included. The sibling's `context` is its own and is not compared.

#### Scenario: A sibling carries the shared rules unchanged
- **WHEN** a non-shim sibling's `openspec/config.yaml` contains the hub's shared rules block unchanged and a context of its own
- **THEN** no on-ramp violation is reported for `openspec/config.yaml`

#### Scenario: A drifted rules block is reported
- **WHEN** a non-shim sibling's shared rules block differs from the hub's in any character, or has no marker-delimited block
- **THEN** the checker reports that the shared rules do not match the hub's and exits non-zero

#### Scenario: A missing configuration is reported for a non-shim sibling
- **WHEN** a non-shim sibling has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: A shim is not required to carry OpenSpec configuration
- **WHEN** `sdypy-excitation` has no `openspec/` directory
- **THEN** no violation is reported for it

#### Scenario: sdypy-FRF is not exempt
- **WHEN** `sdypy-FRF` has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero

### Requirement: Supported Python versions follow SPEC 0
The Python minor versions a first-level sdypy namespace package supports SHALL follow Scientific Python's SPEC 0: from the oldest minor version released less than three years ago through the newest stable CPython release for which the current NumPy and SciPy releases both publish wheels. The concrete set SHALL be declared in exactly one place, the sibling template checker; every other requirement refers to it as *the supported set*. At the time of this change (2026-11-04) the supported set is 3.13, 3.14 and 3.15.

#### Scenario: The declared set matches SPEC 0
- **WHEN** the supported set declared in the checker is compared with the SPEC 0 drop schedule, the CPython release list and the wheels published by the current NumPy and SciPy releases
- **THEN** it contains every stable minor version released less than three years ago for which both publish wheels, and no older one

#### Scenario: The set has a single declaration
- **WHEN** the hub's tools, tests and specs are searched for the supported Python versions of a sibling
- **THEN** the concrete versions appear only in the checker's declaration and in this requirement's dated note

### Requirement: Canonical test workflow on the supported Python set
Every first-level sdypy namespace package SHALL provide a GitHub Actions test workflow at `.github/workflows/python-package.yml`. The workflow SHALL trigger on push and pull-request events, run on `ubuntu-latest`, exercise a Python matrix that covers the supported set, install the package via `pip install .` or `pip install .[<extras>]`, run `flake8` and `pytest`, include a `python -m build` validation step, and use non-deprecated action major versions (at minimum `actions/checkout@v4` and `actions/setup-python@v5`).

#### Scenario: Test workflow file is named python-package.yml
- **WHEN** `.github/workflows/` is inspected
- **THEN** a file named `python-package.yml` exists and no file named `pytest.yaml` exists

#### Scenario: Test workflow triggers on push and pull_request
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the `on:` block includes both `push` and `pull_request` triggers

#### Scenario: Test workflow matrix covers the supported set
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the matrix `python-version` list contains every version of the supported set

#### Scenario: Test workflow installs the package from pyproject
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the install step is `pip install .` or `pip install .[<extras>]` (quoted or not) and no step reads a `requirements*.txt` file

#### Scenario: Test workflow includes build validation step
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** a step runs `python -m build` so a broken sdist or wheel fails CI rather than the next release

#### Scenario: Test workflow uses non-deprecated action versions
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** every `uses:` reference to `actions/checkout` is at `@v4` or later and every reference to `actions/setup-python` is at `@v5` or later

### Requirement: Metadata consistency with the supported Python set
Every first-level sdypy namespace package SHALL declare the hatchling build backend, a `requires-python` floor equal to the oldest version of the supported set, an MIT license, `Programming Language :: Python :: 3.x` classifiers for every Python minor version in the CI matrix, `project.urls` whose Homepage and Source entries point at the package's own repository (the Documentation entry SHALL resolve either to the package's own hosted documentation or, for the shim `sdypy-excitation`, which has no hosted docs, to its backend library's documentation), and both `dev` and `docs` optional-dependency extras. The `dev` extra SHALL reference the `docs` extra rather than duplicating its entries.

#### Scenario: hatchling is the declared build backend
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[build-system] build-backend` equals `"hatchling.build"`

#### Scenario: requires-python floor is the oldest supported version
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project] requires-python` is `">=3.X"` where `3.X` is the oldest version of the supported set

#### Scenario: Python version classifiers match CI matrix
- **WHEN** `pyproject.toml` and `.github/workflows/python-package.yml` are inspected
- **THEN** every Python minor version in the CI matrix has a corresponding `Programming Language :: Python :: 3.x` classifier and no extra classifier appears for a version not in the matrix

#### Scenario: Homepage and Source URLs point at the package's own repository
- **WHEN** `pyproject.toml` is inspected for any first-level sdypy package
- **THEN** the `[project.urls]` Homepage and Source entries resolve to that package's own repository, not a backend library's

#### Scenario: Documentation URL of a thin wrapper resolves to its backend's docs
- **WHEN** `pyproject.toml` is inspected for sdypy-excitation
- **THEN** the `[project.urls]` Documentation entry resolving to pyExSi's documentation is conformant, because the shim has no hosted documentation of its own

#### Scenario: sdypy-FRF documentation must be its own
- **WHEN** `pyproject.toml` is inspected for sdypy-FRF
- **THEN** the `[project.urls]` Documentation entry must be its own readthedocs.io site, because `sdypy-FRF` is a regular package

#### Scenario: dev and docs extras are declared
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project.optional-dependencies]` contains both a `docs` key and a `dev` key; the `dev` list includes a self-referencing `sdypy-<pkg>[docs]` entry

### Requirement: Backend libraries support the supported Python set
The backend libraries the consortium maintains and the first-level packages wrap or depend on (pyFRF, pyExSi, pyEMA, pyuff, pyLump, lvm_read and pyMRAW) SHALL support the supported set: a `requires-python` floor equal to its oldest version, a `Programming Language :: Python :: 3.x` classifier for every version of the set and for no other version, a CI test matrix that covers the set, and, where the library has a `readthedocs.yaml`, a docs build on the set's oldest version. Running the sibling template checker with `--python-only` on a clone SHALL check exactly these points, without requiring an `sdypy/` portion, and exit non-zero on any mismatch.

#### Scenario: A conforming backend passes the Python-only check
- **WHEN** `python tools/check_sibling_template.py --python-only --path <backend-clone>` is run on a clone whose floor, classifiers, workflow matrix and docs Python follow the supported set
- **THEN** the checker exits 0

#### Scenario: An old floor is reported
- **WHEN** the Python-only check runs on a clone declaring `requires-python = ">=3.10"`
- **THEN** the checker reports the floor and exits non-zero

#### Scenario: A matrix missing a supported version is reported
- **WHEN** the Python-only check runs on a clone whose workflows do not test every version of the supported set
- **THEN** the checker reports the matrix and exits non-zero

#### Scenario: Only the Python points are checked
- **WHEN** the Python-only check runs on a clone that has no `sdypy/` portion, no `AGENTS.md` and no release workflow
- **THEN** none of these is reported

### Requirement: Release workflow is the hub's file, copied verbatim
Every first-level sdypy namespace package SHALL provide `.github/workflows/release-and-publish-to-pypi.yml` whose content is the hub's file of the same name, character for character apart from line endings. The hub's copy is the file's only home; a sibling MUST NOT edit its copy. No file named with an underscore variant (e.g. `release_and_publish_to_pypi.yml`) SHALL exist.

#### Scenario: A verbatim copy conforms
- **WHEN** a sibling's release workflow equals the hub's, or differs from it only in line endings
- **THEN** no release-workflow violation is reported

#### Scenario: A drifted copy is reported
- **WHEN** a sibling's release workflow differs from the hub's in any other character, including the old tag-triggered workflow
- **THEN** the checker reports that it differs from the hub's release workflow and exits non-zero

#### Scenario: A missing release workflow is reported
- **WHEN** a sibling has no `.github/workflows/release-and-publish-to-pypi.yml`
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: An underscore-named variant is reported
- **WHEN** `.github/workflows/` contains a file such as `release_and_publish_to_pypi.yml`
- **THEN** the checker reports the underscore-named release workflow

#### Scenario: An unreadable hub copy is reported, not passed
- **WHEN** the checker cannot read the hub's release workflow
- **THEN** it reports the sibling's copy as unchecked instead of passing it

### Requirement: Releases start only by hand from the default branch
The canonical release workflow SHALL be triggered only by `workflow_dispatch` with a required `version` input and MUST NOT trigger on a tag push or any other event. Run from any ref other than the repository's default branch, it SHALL fail before checking out, changing or publishing anything.

#### Scenario: The workflow is started by hand with a version
- **WHEN** the workflow's `on:` block is inspected
- **THEN** it holds only `workflow_dispatch`, with a required `version` input

#### Scenario: A hand-pushed tag publishes nothing
- **WHEN** a maintainer pushes a `v*` tag by hand
- **THEN** no workflow run starts, because no trigger of the release workflow matches a tag push

#### Scenario: A run off the default branch fails
- **WHEN** the workflow is started on a branch other than the default branch
- **THEN** its first step fails with an error naming the default branch, before the checkout

### Requirement: The release workflow writes the version into pyproject.toml
The release workflow SHALL write the requested version into the `version` line of the `[project]` table of `pyproject.toml`, and into no other line, and SHALL confirm by re-parsing the file that `[project] version` now equals the requested version.

#### Scenario: Only the project version changes
- **WHEN** the bump step runs with a valid new version on a `pyproject.toml` that also has a `version` key in a `[tool.*]` table
- **THEN** `[project] version` equals the new version, the `[tool.*]` value is unchanged, and no other byte of the file changes

### Requirement: The release tag sits on the version commit
The release workflow SHALL commit the bumped `pyproject.toml` as *Release X.Y.Z* and SHALL create the annotated tag `vX.Y.Z` on that commit, before building the distributions.

#### Scenario: Commit, tag, then build
- **WHEN** the workflow's steps are inspected
- **THEN** the bump precedes the commit, the commit precedes the tag, and the tag precedes `python -m build`

### Requirement: The release is pushed atomically before it is published
The release workflow SHALL push the release commit to the default branch and the tag in one `git push --atomic`, after the distributions are built and checked and before the publish job runs. Release runs SHALL be serialised, so two runs never race.

#### Scenario: Push after the checks, before publishing
- **WHEN** the workflow is inspected
- **THEN** the atomic push of `HEAD:refs/heads/<default branch>` and `refs/tags/v<version>` follows the distribution check, and the publish job `needs` the job that pushes

#### Scenario: A moved default branch stops the release
- **WHEN** the default branch gained a commit after the run started
- **THEN** the atomic push is rejected as non-fast-forward, neither ref is pushed and nothing is published

#### Scenario: Releases are serialised
- **WHEN** the workflow is inspected
- **THEN** it declares `concurrency` group `release` with `cancel-in-progress: false`

### Requirement: The release workflow refuses an inconsistent version
The release workflow SHALL fail before pushing or publishing anything when the requested version is not `X.Y.Z` optionally followed by `aN`, `bN` or `rcN`, when the tag `v<version>` already exists, when the version is not newer than the current `[project] version`, when `pyproject.toml` has no literal `[project] version`, or when the built distributions are not exactly one wheel and one sdist carrying the requested version.

#### Scenario: A malformed version is refused
- **WHEN** the bump step runs with `1.3`, `v1.3.0`, `1.3.0.dev1`, an empty string, or a version with surrounding whitespace
- **THEN** it fails with an error saying the version is not `X.Y.Z` and leaves `pyproject.toml` unchanged

#### Scenario: An existing tag is refused
- **WHEN** the bump step runs with a version whose `v` tag already exists
- **THEN** it fails with an error naming the existing tag and leaves `pyproject.toml` unchanged

#### Scenario: A version not newer than the current one is refused
- **WHEN** the bump step runs with a version equal to or older than the current `[project] version`, including a pre-release of it
- **THEN** it fails with an error naming the current version

#### Scenario: A dynamic version is refused
- **WHEN** `pyproject.toml` declares `dynamic = ["version"]` instead of a literal version
- **THEN** the bump step fails with an error saying there is no literal `[project]` version

#### Scenario: Distributions carrying another version are refused
- **WHEN** the distribution check runs and a wheel or sdist carries a version other than the requested one, or one of them is missing
- **THEN** it fails before the push

### Requirement: Releasing is documented once, in the hub
The hub's `AGENTS.md` SHALL have a `## Releasing` section that names the canonical release workflow as the only way to release, and the hub link block SHALL link to that section, so every sibling's `AGENTS.md` reaches it through its verbatim copy of the block.

#### Scenario: The hub documents releasing
- **WHEN** the hub's `AGENTS.md` is inspected
- **THEN** it has a `## Releasing` section that names `release-and-publish-to-pypi.yml`

#### Scenario: The link block reaches the section
- **WHEN** the hub link block is extracted
- **THEN** it contains a link to `https://github.com/sdypy/sdypy/blob/main/AGENTS.md#releasing`

