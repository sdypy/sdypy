## ADDED Requirements

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
Every first-level sdypy namespace package other than the two backend shims (`sdypy-FRF`, `sdypy-excitation`) SHALL provide `openspec/config.yaml` whose `rules` block is the hub's shared rules block verbatim: the region of the hub's `openspec/config.yaml` delimited by the comment lines `# >>> shared rules from the sdypy hub` and `# <<< shared rules`, markers included. The sibling's `context` is its own and is not compared.

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
- **WHEN** `sdypy-FRF` or `sdypy-excitation` has no `openspec/` directory
- **THEN** no violation is reported for it

### Requirement: Supported Python versions follow SPEC 0
The Python minor versions a first-level sdypy namespace package supports SHALL follow Scientific Python's SPEC 0: from the oldest minor version released less than three years ago through the newest stable CPython release for which the current NumPy and SciPy releases both publish wheels. The concrete set SHALL be declared in exactly one place, the sibling template checker; every other requirement refers to it as *the supported set*. At the time of this change the supported set is 3.12, 3.13 and 3.14.

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
Every first-level sdypy namespace package SHALL declare the hatchling build backend, a `requires-python` floor equal to the oldest version of the supported set, an MIT license, `Programming Language :: Python :: 3.x` classifiers for every Python minor version in the CI matrix, `project.urls` whose Homepage and Source entries point at the package's own repository (the Documentation entry SHALL resolve either to the package's own hosted documentation or, for a thin wrapper without hosted docs, to its backend library's documentation), and both `dev` and `docs` optional-dependency extras. The `dev` extra SHALL reference the `docs` extra rather than duplicating its entries.

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
- **WHEN** `pyproject.toml` is inspected for sdypy-FRF or sdypy-excitation
- **THEN** the `[project.urls]` Documentation entry resolving to pyFRF's or pyExSi's documentation is conformant, because these wrappers have no hosted documentation of their own

#### Scenario: dev and docs extras are declared
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project.optional-dependencies]` contains both a `docs` key and a `dev` key; the `dev` list includes a self-referencing `sdypy-<pkg>[docs]` entry

## REMOVED Requirements

### Requirement: Canonical test workflow
**Reason**: It names a fixed Python matrix (3.10–3.12) and allows only a bare `pip install .`. Its scenarios carry those facts in their names, and a MODIFIED block cannot rename a scenario, so the requirement is replaced rather than edited.
**Migration**: Replaced by *Canonical test workflow on the supported Python set*, which keeps every other obligation unchanged, refers to *the supported set*, and also allows `pip install .[<extras>]`.

### Requirement: Metadata consistency
**Reason**: It fixes `requires-python = ">=3.10"` and classifiers for 3.10–3.12, including in a scenario name; replaced for the same reason as the test workflow.
**Migration**: Replaced by *Metadata consistency with the supported Python set*, which keeps every other obligation unchanged and takes the floor from *the supported set*.
