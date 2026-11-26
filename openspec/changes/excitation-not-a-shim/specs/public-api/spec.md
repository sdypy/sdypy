## REMOVED Requirements

### Requirement: Shim packages use explicit curated re-exports
**Reason**: No package is a shim any more. `sdypy-FRF` and `sdypy-excitation` hold their own code. The rule that still applies to them moves to *First-level packages import their curated names explicitly*.
**Migration**: None for users. The explicit-import rule continues in the new requirement.

### Requirement: Advisory drift check for shims
**Reason**: The drift check compared a shim's curated `__all__` with its backend (pyExSi). `sdypy-excitation` no longer has a backend, so there is nothing to compare.
**Migration**: None. `tools/check_public_api.py` drops the drift report.

## ADDED Requirements

### Requirement: First-level packages import their curated names explicitly
`sdypy/FRF/__init__.py` and `sdypy/excitation/__init__.py` SHALL NOT contain any `import *`, MUST import their curated names explicitly from the package's own modules (`from .frf import FRF, assert_sep005, direction_dict`; `from .signals import burst_random, ...`) and MUST declare a matching `__all__`. `sdypy-FRF` MUST NOT depend on `pyFRF` and `sdypy-excitation` MUST NOT depend on `pyExSi`.

#### Scenario: No star-import in FRF `__init__.py`
- **WHEN** `sdypy/FRF/__init__.py` in the sdypy-FRF repository clone is inspected
- **THEN** the file contains no `import *` form
- **AND** its curated names are imported from the package's own modules, not from `pyFRF`

#### Scenario: No star-import in excitation `__init__.py`
- **WHEN** `sdypy/excitation/__init__.py` in the sdypy-excitation repository clone is inspected
- **THEN** the file contains no `import *` form
- **AND** its curated names are imported from the package's own modules, not from `pyExSi`

#### Scenario: Curated FRF names are importable after explicit import
- **WHEN** `sdypy.FRF` is imported in an environment where `sdypy-FRF` is installed
- **THEN** `sdypy.FRF.FRF`, `sdypy.FRF.assert_sep005`, and `sdypy.FRF.direction_dict` are all accessible without error

#### Scenario: Curated excitation names are importable after explicit import
- **WHEN** `sdypy.excitation` is imported in an environment where `sdypy-excitation` is installed
- **THEN** all eleven names in `sdypy.excitation.__all__` (`burst_random`, `get_kurtosis`, `get_psd`, `impulse`, `nonstationary_signal`, `normal_random`, `pseudo_random`, `random_gaussian`, `sine_sweep`, `stationary_nongaussian_signal`, `uniform_random`) are accessible without error

#### Scenario: Neither package depends on its former backend
- **WHEN** the `dependencies` of `sdypy-FRF` and `sdypy-excitation` are read from their `pyproject.toml`
- **THEN** neither lists `pyFRF` or `pyExSi`

## MODIFIED Requirements

### Requirement: SEP 2 binds the signatures of re-exported backend objects
When a first-level package re-exports a class or function from a backend package, the signature and public attributes of that object SHALL be treated as part of the first-level package's public API and SHALL follow SEP 2. Backend names that a first-level package does not re-export remain out of scope.

#### Scenario: A re-exported backend class is in scope
- **WHEN** a first-level package re-exports a backend function unchanged
- **THEN** its parameter names are assessed against SEP 2

#### Scenario: A backend name that is not re-exported is out of scope
- **WHEN** a backend package exposes a function that no first-level package re-exports
- **THEN** SEP 2 makes no demand on its names

#### Scenario: The table no longer excludes backend names
- **WHEN** the *FRF form* row of the canonical table is read
- **THEN** it does not state that backend parameter names are out of scope
