## MODIFIED Requirements

### Requirement: Metadata consistency with the supported Python set
Every first-level sdypy namespace package SHALL declare the hatchling build backend, a `requires-python` floor equal to the oldest version of the supported set, an MIT license (declared either by the SPDX expression `license = "MIT"`, which needs no license classifier, or by the legacy table `license = {text = "MIT"}` together with the `License :: OSI Approved :: MIT License` classifier; in both forms any `License ::` classifier present SHALL be that one), `Programming Language :: Python :: 3.x` classifiers for every Python minor version in the CI matrix, `project.urls` whose Homepage and Source entries point at the package's own repository (the Documentation entry SHALL resolve either to the package's own hosted documentation or, for the shim `sdypy-excitation`, which has no hosted docs, to its backend library's documentation), and both `dev` and `docs` optional-dependency extras. The `dev` extra SHALL reference the `docs` extra rather than duplicating its entries.

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

#### Scenario: An SPDX expression declares MIT without a classifier
- **WHEN** `pyproject.toml` declares `license = "MIT"` and no `License ::` classifier
- **THEN** no license violation is reported

#### Scenario: An SPDX expression with the MIT classifier is accepted
- **WHEN** `pyproject.toml` declares `license = "MIT"` and the `License :: OSI Approved :: MIT License` classifier
- **THEN** no license violation is reported

#### Scenario: An SPDX expression contradicted by another license classifier is reported
- **WHEN** `pyproject.toml` declares `license = "MIT"` and a `License ::` classifier other than `License :: OSI Approved :: MIT License`
- **THEN** the checker reports the contradicting classifier and exits non-zero

#### Scenario: The legacy table with the MIT classifier is accepted
- **WHEN** `pyproject.toml` declares `license = {text = "MIT"}` and the `License :: OSI Approved :: MIT License` classifier
- **THEN** no license violation is reported

#### Scenario: The legacy table without the MIT classifier is reported
- **WHEN** `pyproject.toml` declares `license = {text = "MIT"}` and no `License :: OSI Approved :: MIT License` classifier
- **THEN** the checker reports the missing classifier and exits non-zero

#### Scenario: The legacy table contradicted by another license classifier is reported
- **WHEN** `pyproject.toml` declares `license = {text = "MIT"}` and a `License ::` classifier other than `License :: OSI Approved :: MIT License`
- **THEN** the checker reports the contradicting classifier and exits non-zero

#### Scenario: A license other than MIT is reported
- **WHEN** `pyproject.toml` declares a `license` expression other than exactly `MIT` (for example `"GPL-3.0-only"` or `"MIT OR Apache-2.0"`), a table `{text = "<not MIT>"}` or `{file = ...}`, or no `license` at all
- **THEN** the checker reports the license and exits non-zero, whatever classifiers are present
