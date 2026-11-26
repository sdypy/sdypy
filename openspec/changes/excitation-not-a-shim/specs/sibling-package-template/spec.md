## MODIFIED Requirements

### Requirement: OpenSpec configuration carries the hub's shared rules
Every first-level sdypy namespace package SHALL provide `openspec/config.yaml` whose `rules` block is the hub's shared rules block verbatim: the region of the hub's `openspec/config.yaml` delimited by the comment lines `# >>> shared rules from the sdypy hub` and `# <<< shared rules`, markers included. The sibling's `context` is its own and is not compared.

#### Scenario: A sibling carries the shared rules unchanged
- **WHEN** a sibling's `openspec/config.yaml` contains the hub's shared rules block unchanged and a context of its own
- **THEN** no on-ramp violation is reported for `openspec/config.yaml`

#### Scenario: A drifted rules block is reported
- **WHEN** a sibling's shared rules block differs from the hub's in any character, or has no marker-delimited block
- **THEN** the checker reports that the shared rules do not match the hub's and exits non-zero

#### Scenario: A missing configuration is reported for a non-shim sibling
- **WHEN** a sibling (none is a shim) has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: A shim is not required to carry OpenSpec configuration
- **WHEN** a package that was once a shim, such as `sdypy-excitation`, has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero, because no package is a shim any more

#### Scenario: sdypy-FRF is not exempt
- **WHEN** `sdypy-FRF` has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: sdypy-excitation is not exempt
- **WHEN** `sdypy-excitation` has no `openspec/config.yaml`
- **THEN** the checker reports the missing file and exits non-zero

### Requirement: Metadata consistency with the supported Python set
Every first-level sdypy namespace package SHALL declare the hatchling build backend, a `requires-python` floor equal to the oldest version of the supported set, an MIT license, `Programming Language :: Python :: 3.x` classifiers for every Python minor version in the CI matrix, `project.urls` whose Homepage and Source entries point at the package's own repository and whose Documentation entry resolves to the package's own hosted documentation, and both `dev` and `docs` optional-dependency extras. The `dev` extra SHALL reference the `docs` extra rather than duplicating its entries.

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
- **WHEN** `pyproject.toml` is inspected for sdypy-excitation, or for any package, and its Documentation entry resolves to a backend library's documentation (for example pyExSi's)
- **THEN** the checker reports it and exits non-zero, because no package is a thin wrapper any more

#### Scenario: sdypy-FRF documentation must be its own
- **WHEN** `pyproject.toml` is inspected for sdypy-FRF
- **THEN** the `[project.urls]` Documentation entry must be its own readthedocs.io site, because `sdypy-FRF` is a regular package

#### Scenario: sdypy-excitation documentation must be its own
- **WHEN** `pyproject.toml` is inspected for sdypy-excitation
- **THEN** the `[project.urls]` Documentation entry must be its own readthedocs.io site, because `sdypy-excitation` is a regular package

#### Scenario: dev and docs extras are declared
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project.optional-dependencies]` contains both a `docs` key and a `dev` key; the `dev` list includes a self-referencing `sdypy-<pkg>[docs]` entry
