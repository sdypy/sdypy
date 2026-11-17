## MODIFIED Requirements

### Requirement: Shim packages use explicit curated re-exports
`sdypy/excitation/__init__.py` is the only shim: it SHALL NOT contain any `from <backend> import *` star-import, MUST use explicit named imports (`from pyExSi import burst_random, ...`) and MUST declare a matching `__all__`. `sdypy/FRF/__init__.py` is not a shim: it holds its code in its own modules (`sdypy/FRF/frf.py`, `sdypy/FRF/fft_tools.py`), SHALL NOT contain any `import *` and MUST import its curated names explicitly from those modules (`from .frf import FRF, assert_sep005, direction_dict`) and declare a matching `__all__`. `sdypy-FRF` MUST NOT depend on `pyFRF`.

#### Scenario: No star-import in FRF `__init__.py`
- **WHEN** `sdypy/FRF/__init__.py` in the sdypy-FRF repository clone is inspected
- **THEN** the file contains no `import *` form
- **AND** its curated names are imported from the package's own modules, not from `pyFRF`

#### Scenario: No star-import in excitation `__init__.py`
- **WHEN** `sdypy/excitation/__init__.py` in the sdypy-excitation repository clone is inspected
- **THEN** the file contains no line matching `from pyExSi import *` or any `import *` form

#### Scenario: Curated FRF names are importable after explicit re-export
- **WHEN** `sdypy.FRF` is imported in an environment where `sdypy-FRF` is installed
- **THEN** `sdypy.FRF.FRF`, `sdypy.FRF.assert_sep005`, and `sdypy.FRF.direction_dict` are all accessible without error

#### Scenario: Curated excitation names are importable after explicit re-export
- **WHEN** `sdypy.excitation` is imported in an environment where `sdypy-excitation` is installed
- **THEN** all eleven names in `sdypy.excitation.__all__` (`burst_random`, `get_kurtosis`, `get_psd`, `impulse`, `nonstationary_signal`, `normal_random`, `pseudo_random`, `random_gaussian`, `sine_sweep`, `stationary_nongaussian_signal`, `uniform_random`) are accessible without error

### Requirement: Advisory drift check for shims
The conformance tooling SHALL report backend public callables that are absent from the curated `__all__` of `sdypy.excitation`, but this report MUST NOT cause CI to fail. The drift check is advisory only: it surfaces new backend names that may warrant a curation decision without blocking the build.

#### Scenario: Drift check reports uncurated backend names without failing
- **WHEN** `tools/check_public_api.py` is run against the sibling clones and a backend (pyExSi) exposes a public callable not in the shim's `__all__`
- **THEN** the checker prints a report listing the uncurated names
- **AND** the checker exits with code 0 (does not fail CI)

#### Scenario: Drift check passes when curated list is complete
- **WHEN** `tools/check_public_api.py` is run and all backend public callables are already in the shim's curated `__all__`
- **THEN** the checker prints no drift report and exits with code 0

### Requirement: SEP 2 binds the signatures of re-exported backend objects
When a first-level package re-exports a class or function from a backend package, the signature and public attributes of that object SHALL be treated as part of the first-level package's public API and SHALL follow SEP 2. Backend names that a first-level package does not re-export remain out of scope.

#### Scenario: A re-exported backend class is in scope
- **WHEN** `sdypy.excitation` re-exports a pyExSi function unchanged
- **THEN** its parameter names are assessed against SEP 2

#### Scenario: A backend name that is not re-exported is out of scope
- **WHEN** a backend package exposes a function that no first-level package re-exports
- **THEN** SEP 2 makes no demand on its names

#### Scenario: The table no longer excludes backend names
- **WHEN** the *FRF form* row of the canonical table is read
- **THEN** it does not state that backend parameter names are out of scope

### Requirement: Evidenced divergences carry deprecated aliases to the canonical names
Every public name in a first-level package that diverges from a canonical table entry SHALL be renamed to the canonical name, with the divergent name retained as an alias that emits `DeprecationWarning`, per SEP 2's existing deprecation policy: aliases remain functional through all of v1.x and are removed no earlier than v2.0. Positional callers MUST be unaffected by keyword renames.

The inventory of evidenced divergences SHALL be derived from the output of
`tools/check_nomenclature.py` against the sibling clones, not asserted
independently of it. A name that no longer appears in any first-level package
MUST NOT be carried in the inventory. The exception is a context-dependent
spelling on a re-exported backend object, which the checker cannot see: it is
carried in the inventory on the strength of the SEP 2 note that records it, and
the owning package's tests verify the rename.

The inventory of evidenced divergences covered by this requirement is:
`nat_freq` → `natural_freq` (public attribute of `EMA.Model`, `model.Beam`,
`model.Tetrahedron`); `nat_xi`, `pole_xi` → `damping_ratio` and `phi` →
`mode_shape` in EMA public signatures other than the criterion functions;
`lower`, `upper`, `f_lower`, `f_upper` → `freq_lower` and `freq_upper` (EMA);
`frf_type` → `frf_form` (EMA); `K`, `M`, `EI` → `stiffness_matrix`,
`mass_matrix` (model); `E`, `Young` → `young_modulus`, `nu`, `Poisson` →
`poisson_ratio`, `rho`, `ro`, `Density` → `density` (model); `org`, `conec` →
`nodes`, `elements` (`model.Beam`, `model.Tetrahedron`); `n` → `n_modes`
(`model.Beam.solve`); `FRF_ind`, `lower_ind`, `upper_ind`, `pole_ind` (EMA) and
`derivative_E_ind`, `derivative_ro_ind`, `eig_ind` (model) → the corresponding
`_idx` spellings; `frf_type` → `frf_estimator` (constructor parameter and
instance attribute of `FRF`, defined in `sdypy.FRF`);
`type` → `frf_estimator` and `form` → `frf_form` (parameters of
`FRF.get_FRF`).

#### Scenario: A renamed attribute keeps a working deprecated alias
- **WHEN** user code reads `EMA.Model.nat_freq` after the rename to `natural_freq`
- **THEN** a `DeprecationWarning` is emitted
- **AND** the value returned is identical to `EMA.Model.natural_freq`

#### Scenario: The canonical name works without a warning
- **WHEN** user code reads `EMA.Model.natural_freq`
- **THEN** no `DeprecationWarning` is emitted and the value is correct

#### Scenario: Positional callers survive a keyword rename
- **WHEN** existing user code calls a renamed public function using positional arguments only
- **THEN** the call behaves exactly as before the rename, with no warning and no signature error

#### Scenario: An alias removal before v2.0 is a violation
- **WHEN** a first-level package releases a v1.x version in which one of the inventoried deprecated aliases has been removed
- **THEN** it violates this requirement, regardless of how long the alias has existed

#### Scenario: A name absent from every sibling is not carried as pending work
- **WHEN** the inventory names a divergent spelling that `tools/check_nomenclature.py` no longer reports against any sibling clone
- **AND** the spelling is not a context-dependent spelling on a re-exported backend object, which the checker never audits
- **THEN** that entry is removed from the inventory and from the `REQUIREMENTS.md` pending roster

#### Scenario: A renamed backend keyword keeps a working deprecated alias
- **WHEN** user code calls `sdypy.FRF.FRF(..., frf_type='H2')` or `frf.get_FRF(type='H1', form='mobility')`
- **THEN** a `DeprecationWarning` is emitted for each old keyword
- **AND** the object and the returned array are identical to those from `frf_estimator=` and `frf_form=`

#### Scenario: A positional `get_FRF` call is unaffected
- **WHEN** user code calls `frf.get_FRF('H1', 'accelerance')`
- **THEN** it returns the H1 accelerance with no warning, before and after the rename
