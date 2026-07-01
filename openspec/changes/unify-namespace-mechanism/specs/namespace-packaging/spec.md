## ADDED Requirements

### Requirement: Umbrella exposes first-level sub-packages by attribute access
The `sdypy` umbrella package SHALL expose each first-level sub-package (`EMA`, `io`, `FRF`, `excitation`, `model`, `view`) as an attribute, so that `import sdypy as sd; sd.<name>` resolves to the installed sub-package.

#### Scenario: Attribute access resolves a sub-package
- **WHEN** a user runs `import sdypy as sd` and accesses `sd.EMA`
- **THEN** `sd.EMA` is the `sdypy.EMA` module and no `AttributeError` is raised

#### Scenario: Submodule and from-import styles also work
- **WHEN** a user runs `from sdypy import FRF` or `import sdypy.FRF`
- **THEN** the `sdypy.FRF` sub-package is imported successfully

#### Scenario: Unknown attribute still errors
- **WHEN** a user accesses `sd.does_not_exist`
- **THEN** an `AttributeError` is raised naming the missing attribute

### Requirement: Importing the umbrella is lightweight
Importing `sdypy` SHALL NOT eagerly import its first-level sub-packages or their optional heavy backends. Sub-packages MUST be imported only on first access.

#### Scenario: Bare import pulls no heavy backend
- **WHEN** a fresh interpreter runs `import sdypy`
- **THEN** `sys.modules` contains no entry for `pyvista`, `pyvistaqt`, or `vtk`

#### Scenario: Access triggers the import
- **WHEN** the user subsequently accesses `sdypy.view`
- **THEN** the `sdypy.view` sub-package is imported at that point

### Requirement: Version is sourced from installed metadata
The `sdypy` package SHALL provide `__version__` as a non-empty string derived from the installed distribution metadata, with a defined fallback when metadata is unavailable, and MUST NOT hard-code the version in a second location.

#### Scenario: Version available from metadata
- **WHEN** `sdypy` is installed and a user reads `sdypy.__version__`
- **THEN** the value is a non-empty string equal to the installed distribution version

#### Scenario: Source tree without metadata
- **WHEN** `sdypy` is imported from a source checkout that has no installed distribution metadata
- **THEN** `sdypy.__version__` returns the defined fallback string instead of raising

### Requirement: Sub-packages are native namespace portions
Every first-level package that contributes to the `sdypy` namespace MUST be a PEP 420 native portion and MUST NOT ship a top-level `sdypy/__init__.py`. The umbrella package is the only distribution permitted to provide `sdypy/__init__.py`.

#### Scenario: No sibling ships the namespace __init__
- **WHEN** the installed file lists of `sdypy-EMA`, `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`, `sdypy-view`, and `sdypy-model` are inspected
- **THEN** none of them contains a `sdypy/__init__.py` file

#### Scenario: All first-level packages remain discoverable together
- **WHEN** the umbrella and all six first-level packages are installed in the same environment
- **THEN** each of `sdypy.EMA`, `sdypy.io`, `sdypy.FRF`, `sdypy.excitation`, `sdypy.model`, and `sdypy.view` can be imported in the same interpreter session
