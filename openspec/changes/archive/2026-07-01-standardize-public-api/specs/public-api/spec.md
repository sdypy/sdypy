## Purpose
The contract governing the public API surface of the `sdypy` umbrella and the six first-level packages — explicit `__all__` declarations, curated re-exports for backend shims, naming conventions for all public names (as codified in the amended SEP 2), the deprecation policy for renamed names, and the conformance checks that enforce all of it. Established by the `standardize-public-api` change.

## ADDED Requirements

### Requirement: Every first-level package declares an explicit `__all__`
Every first-level sdypy namespace package (`sdypy.EMA`, `sdypy.io`, `sdypy.FRF`, `sdypy.excitation`, `sdypy.view`, `sdypy.model`) SHALL declare a non-empty `__all__` list in its `sdypy/<pkg>/__init__.py`. Every name in `__all__` MUST resolve via `getattr` on the module object after import.

#### Scenario: `__all__` present and non-empty in each first-level package
- **WHEN** each of the six first-level packages is imported (`import sdypy.EMA`, `import sdypy.io`, `import sdypy.FRF`, `import sdypy.excitation`, `import sdypy.view`, `import sdypy.model`)
- **THEN** each module has an `__all__` attribute that is a non-empty list

#### Scenario: Every `__all__` entry resolves via getattr
- **WHEN** each of the six first-level packages is imported and `getattr(module, name)` is called for every name in `module.__all__`
- **THEN** no `AttributeError` is raised for any entry in any of the six packages

#### Scenario: Curated names match the design-specified lists
- **WHEN** the `__all__` of each package is inspected after import
- **THEN** `sdypy.EMA.__all__` contains exactly `["Model", "MAC", "MSF", "MCF", "complex_freq_to_freq_and_damp", "stabilization", "normal_modes", "pole_picking"]`
- **AND** `sdypy.io.__all__` contains exactly `["uff", "lvm", "mraw", "sfmov"]`
- **AND** `sdypy.FRF.__all__` contains exactly `["FRF", "assert_sep005", "direction_dict"]`
- **AND** `sdypy.excitation.__all__` contains exactly `["burst_random", "get_kurtosis", "get_psd", "impulse", "nonstationary_signal", "normal_random", "pseudo_random", "random_gaussian", "sine_sweep", "stationary_nongaussian_signal", "uniform_random"]`
- **AND** `sdypy.view.__all__` contains exactly `["Plotter3D", "create_fem_mesh", "prepare_animation_displacements", "prepare_animation_field", "copy_image_to_clipboard"]`
- **AND** `sdypy.model.__all__` contains exactly `["Beam", "Shell", "Tetrahedron", "solve_eigenvalue", "lumped", "mesh"]`

### Requirement: No leaked third-party or stdlib names in curated surfaces
No `__all__` list of any first-level package SHALL contain a name that refers to a third-party library or Python standard library module or object. Banned names include but are not limited to: `np`, `scipy`, `warnings`, `os`, `io`, `platform`, `subprocess`, `pickle`, `tqdm`, `pv`, `CubicSpline`, `beta`, `moment`, `signal`, `signals`, `BackgroundPlotter`, `BasePlotter`, `haspyqt`, `Image`, `pyperclip`.

#### Scenario: No banned leak names in any `__all__`
- **WHEN** the `__all__` of each of the six installed first-level packages is inspected
- **THEN** none of the following names appears in any `__all__`: `np`, `scipy`, `warnings`, `os`, `io`, `platform`, `subprocess`, `pickle`, `tqdm`, `pv`, `CubicSpline`, `beta`, `moment`, `signal`, `signals`, `BackgroundPlotter`, `BasePlotter`, `haspyqt`, `Image`, `pyperclip`

#### Scenario: `from sdypy.excitation import *` does not expose `beta` or `CubicSpline`
- **WHEN** a user runs `from sdypy.excitation import *` in a fresh namespace
- **THEN** the names `beta`, `CubicSpline`, `np`, and `scipy` are not present in that namespace

### Requirement: Shim packages use explicit curated re-exports
`sdypy/FRF/__init__.py` and `sdypy/excitation/__init__.py` SHALL NOT contain any `from <backend> import *` star-import. Both files MUST use explicit named imports (`from pyFRF import FRF, ...` and `from pyExSi import burst_random, ...`) and declare a matching `__all__`.

#### Scenario: No star-import in FRF `__init__.py`
- **WHEN** `sdypy/FRF/__init__.py` in the sdypy-FRF repository clone is inspected
- **THEN** the file contains no line matching `from pyFRF import *` or any `import *` form

#### Scenario: No star-import in excitation `__init__.py`
- **WHEN** `sdypy/excitation/__init__.py` in the sdypy-excitation repository clone is inspected
- **THEN** the file contains no line matching `from pyExSi import *` or any `import *` form

#### Scenario: Curated FRF names are importable after explicit re-export
- **WHEN** `sdypy.FRF` is imported in an environment where `sdypy-FRF` is installed
- **THEN** `sdypy.FRF.FRF`, `sdypy.FRF.assert_sep005`, and `sdypy.FRF.direction_dict` are all accessible without error

#### Scenario: Curated excitation names are importable after explicit re-export
- **WHEN** `sdypy.excitation` is imported in an environment where `sdypy-excitation` is installed
- **THEN** all eleven names in `sdypy.excitation.__all__` (`burst_random`, `get_kurtosis`, `get_psd`, `impulse`, `nonstationary_signal`, `normal_random`, `pseudo_random`, `random_gaussian`, `sine_sweep`, `stationary_nongaussian_signal`, `uniform_random`) are accessible without error

### Requirement: Module-type entries in `__all__` only where sanctioned
A name in any first-level package's `__all__` MUST NOT resolve to a Python module object unless it belongs to the sanctioned set. The sanctioned module-type entries are: `sdypy.io`'s `uff`, `lvm`, `mraw`, `sfmov`; `sdypy.EMA`'s `stabilization`, `normal_modes`, `pole_picking`; `sdypy.model`'s `lumped`, `mesh`.

#### Scenario: `sdypy.io` `__all__` entries are module objects
- **WHEN** `sdypy.io` is imported and each of `uff`, `lvm`, `mraw`, `sfmov` is retrieved via `getattr(sdypy.io, name)`
- **THEN** each resolves to a module object (i.e. `inspect.ismodule(obj)` is `True`)

#### Scenario: `sdypy.view` and `sdypy.FRF` `__all__` entries are not module objects
- **WHEN** `sdypy.view` and `sdypy.FRF` are imported and every entry in their `__all__` is inspected
- **THEN** none of the entries resolves to a module object

#### Scenario: EMA submodule entries are module objects
- **WHEN** `sdypy.EMA` is imported and `stabilization`, `normal_modes`, and `pole_picking` are retrieved
- **THEN** each resolves to a module object and is accessible as `sdypy.EMA.stabilization`, `sdypy.EMA.normal_modes`, `sdypy.EMA.pole_picking`

### Requirement: Umbrella `__all__` matches the six first-level names
`sdypy/__init__.py` SHALL declare `__all__ = ["EMA", "io", "FRF", "excitation", "model", "view"]`. The umbrella's `__dir__` implementation MUST return a list that includes all six names (consistent with the lazy facade), and the `__all__` content MUST exactly match those six names.

#### Scenario: Umbrella `__all__` lists exactly the six first-level names
- **WHEN** `import sdypy` is run and `sdypy.__all__` is inspected
- **THEN** it equals `["EMA", "io", "FRF", "excitation", "model", "view"]` (order may vary but all six names present and no others)

#### Scenario: `from sdypy import *` imports all six subpackages
- **WHEN** a user runs `from sdypy import *` in a fresh namespace
- **THEN** `EMA`, `io`, `FRF`, `excitation`, `model`, and `view` are all present in that namespace

#### Scenario: Umbrella `__dir__` is consistent with `__all__`
- **WHEN** `dir(sdypy)` is called after `import sdypy`
- **THEN** all six names `"EMA"`, `"io"`, `"FRF"`, `"excitation"`, `"model"`, `"view"` appear in the result

### Requirement: Public naming conventions for sdypy-org first-level packages
New and renamed public names introduced by sdypy-org first-level packages SHALL follow the naming conventions specified in the amended SEP 2: classes use CapWords with uppercase acronyms (e.g. `FRF`, not `Frf`); functions, methods, and parameters use snake_case with lowercase acronyms (e.g. `add_frf`, `frf_type`); standalone established criterion functions may be the bare uppercase acronym (`MAC`, `MSF`, `MCF`); constants use ALL_CAPS; names mandated by an external framework keep that framework's casing. These conventions apply to new and renamed names introduced in this change; retroactive renaming of everything is out of scope.

#### Scenario: Canonical auto_mac name follows snake_case convention
- **WHEN** `sdypy.EMA.Model` is instantiated and its public methods are inspected
- **THEN** a method named `auto_mac` is present and callable (snake_case with lowercase acronym)

#### Scenario: Canonical FEM constructor parameters are unified and snake_case
- **WHEN** `sdypy.model.Shell`, `sdypy.model.Beam`, and `sdypy.model.Tetrahedron` are inspected for their constructor signatures
- **THEN** all three element classes accept the unified canonical material parameters `young_modulus`, `poisson_ratio`, and `density` (snake_case, descriptive)

#### Scenario: Criterion functions MAC, MSF, MCF retain uppercase acronym form
- **WHEN** `sdypy.EMA` is imported and its `__all__` is inspected
- **THEN** `MAC`, `MSF`, and `MCF` are present — bare uppercase acronym form is the established exception for criterion functions

### Requirement: Renamed names keep deprecated aliases through v1.x
Every public name renamed in this change SHALL be kept as a deprecated alias that emits `DeprecationWarning` when used. Aliases MUST remain functional through all v1.x releases; positional callers MUST be unaffected by parameter renames. The rename inventory covered by this policy is: `EMA.Model.autoMAC()` renamed to `auto_mac()`; `EMA.Model` constructor parameter `frf_type=` renamed to `frf_form=`; `Shell` constructor parameters `E=`, `nu=`, `rho=` renamed to `young_modulus=`, `poisson_ratio=`, `density=`; `Tetrahedron` constructor parameters `Young=`, `Density=`, `Poisson=` renamed to `young_modulus=`, `density=`, `poisson_ratio=`; `Beam` constructor parameter `Young=` renamed to `young_modulus=`.

#### Scenario: Calling `autoMAC` emits DeprecationWarning and still works
- **WHEN** an `EMA.Model` instance's `autoMAC()` method is called
- **THEN** a `DeprecationWarning` is emitted
- **AND** the method executes and returns the same result as calling `auto_mac()`

#### Scenario: Calling `auto_mac` works without any warning
- **WHEN** an `EMA.Model` instance's `auto_mac()` method is called
- **THEN** no `DeprecationWarning` is emitted and the method executes correctly

#### Scenario: Deprecated kwargs for Tetrahedron emit DeprecationWarning
- **WHEN** `sdypy.model.Tetrahedron` is instantiated with `Young=`, `Density=`, or `Poisson=` keyword arguments
- **THEN** a `DeprecationWarning` is emitted naming the deprecated parameter
- **AND** the object is constructed correctly (identical to using the canonical names)

#### Scenario: Canonical kwargs for Tetrahedron work without warning
- **WHEN** `sdypy.model.Tetrahedron` is instantiated using `young_modulus=`, `density=`, `poisson_ratio=` keyword arguments
- **THEN** no `DeprecationWarning` is emitted and the object is constructed correctly

#### Scenario: Deprecated symbol kwargs for Shell emit DeprecationWarning
- **WHEN** `sdypy.model.Shell` is instantiated with `E=`, `nu=`, or `rho=` keyword arguments
- **THEN** a `DeprecationWarning` is emitted naming the deprecated parameter
- **AND** the object is constructed identically to using `young_modulus=`, `poisson_ratio=`, `density=`

#### Scenario: Deprecated frf_type kwarg for EMA.Model emits DeprecationWarning
- **WHEN** `sdypy.EMA.Model` is instantiated with the `frf_type=` keyword argument
- **THEN** a `DeprecationWarning` is emitted
- **AND** the object is constructed identically to using `frf_form=`

### Requirement: Advisory drift check for shims
The conformance tooling SHALL report backend public callables that are absent from the curated `__all__` of `sdypy.FRF` and `sdypy.excitation`, but this report MUST NOT cause CI to fail. The drift check is advisory only: it surfaces new backend names that may warrant a curation decision without blocking the build.

#### Scenario: Drift check reports uncurated backend names without failing
- **WHEN** `tools/check_public_api.py` is run against the sibling clones and a backend (pyFRF or pyExSi) exposes a public callable not in the corresponding shim's `__all__`
- **THEN** the checker prints a report listing the uncurated names
- **AND** the checker exits with code 0 (does not fail CI)

#### Scenario: Drift check passes when curated list is complete
- **WHEN** `tools/check_public_api.py` is run and all backend public callables are already in the shim's curated `__all__`
- **THEN** the checker prints no drift report and exits with code 0

### Requirement: SEP 2 contains the amended naming rules
`docs/seps/sep-0002.rst` SHALL be amended to include naming rules for modules/packages, classes, functions/methods/parameters, acronym casing, constants, framework exemptions, the public-surface rule (every first-level package declares `__all__`), and the deprecation policy for renames. The amended SEP 2 text MUST cover all of: module/package snake_case convention; class CapWords with uppercase acronyms; function/method/parameter snake_case with lowercase acronyms; criterion-function exception (`MAC`, `MSF`, `MCF`); framework exemption; ALL_CAPS constants; `__all__` requirement; deprecation policy including the minimum v1.x alias period and v2.0 removal gate. The canonical variable table SHALL be extended with the entries `frf_form` (FRF form: receptance / mobility / accelerance), `young_modulus`, `poisson_ratio`, and `density`.

#### Scenario: Amended SEP 2 file contains the required rule sections
- **WHEN** `docs/seps/sep-0002.rst` is inspected after amendment
- **THEN** the file contains text covering class naming (CapWords), function/method naming (snake_case), parameter naming (snake_case), acronym casing rules (uppercase in CapWords, lowercase in snake_case), the criterion-function exception, the `__all__` requirement, and the deprecation policy

#### Scenario: Amended SEP 2 table contains the new canonical entries
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected after amendment
- **THEN** it contains rows for `frf_form`, `young_modulus`, `poisson_ratio`, and `density` in addition to the original seven entries

#### Scenario: Amended SEP 2 retains original content
- **WHEN** `docs/seps/sep-0002.rst` is inspected after amendment
- **THEN** the original PEP 8 reference, word-order rule, and canonical variable table are all still present
