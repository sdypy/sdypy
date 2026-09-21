# public-api Specification

## Purpose
The contract for the public API surface of the SDyPy first-level packages: every package declares an explicit, curated `__all__` with no leaked third-party or stdlib names, sanctioned module-type entries only, deprecated aliases kept for renamed names through v1.x, and the umbrella exposing exactly the six first-level names plus the `sep005` alias. Established by the `standardize-public-api` change (SEP 2).

**Scope:** Org-wide — binds all six first-level sibling packages, **except** the *Umbrella `__all__` is the six first-level names plus the sep005 alias* requirement, which is umbrella-local. Governed by SEP 2.
## Requirements
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

### Requirement: Umbrella `__all__` is the six first-level names plus the sep005 alias
`sdypy/__init__.py` SHALL declare an `__all__` whose members are exactly the six first-level sub-package names `EMA`, `io`, `FRF`, `excitation`, `model`, `view` together with the `sep005` alias — seven names, no others. The umbrella's `__dir__` implementation MUST return a list that includes all seven names (consistent with the lazy facade), and the `__all__` content MUST exactly match that set.

`sep005` is not a first-level name and not a `sdypy.*` namespace portion: it is the facade alias to the standalone `sdypy_sep005` distribution (the SEP 5 unified-timeseries standard), surfaced on the umbrella for discoverability. Its presence in `__all__` is therefore governed jointly by this requirement and by the `sep005-standard` capability, which owns the alias's resolution target and its rationale.

#### Scenario: Umbrella `__all__` lists exactly the six first-level names
- **WHEN** `import sdypy` is run and `sdypy.__all__` is inspected
- **THEN** exactly six first-level names are present — `EMA`, `io`, `FRF`, `excitation`, `model`, `view` — and no seventh sub-package name
- **AND** the only further member is the `sep005` alias, so the list equals `["EMA", "io", "FRF", "excitation", "model", "view", "sep005"]` (order may vary)

#### Scenario: `from sdypy import *` imports all six subpackages
- **WHEN** a user runs `from sdypy import *` in a fresh namespace
- **THEN** `EMA`, `io`, `FRF`, `excitation`, `model` and `view` are all present in that namespace
- **AND** `sep005` is present alongside them, because the star-import resolves every member of `__all__` through the lazy `__getattr__`

#### Scenario: Umbrella `__dir__` is consistent with `__all__`
- **WHEN** `dir(sdypy)` is called after `import sdypy`
- **THEN** all seven names `"EMA"`, `"io"`, `"FRF"`, `"excitation"`, `"model"`, `"view"`, `"sep005"` appear in the result

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

### Requirement: The canonical table takes precedence over the word-order heuristic
SEP 2's word-order guideline — that the term with the broader meaning comes first in a compound name — SHALL be treated as a heuristic for coining names, not as a rule that overrides the canonical table. Where the canonical variable table in `docs/seps/sep-0002.rst` has an entry for a quantity, that entry is normative and a name that conforms to it MUST NOT be reported as a word-order violation. The heuristic applies only when a new compound name is coined for a quantity the table does not cover, and it SHALL yield to an established domain term of art.

This precedence is what allows `freq_lower` and `mass_matrix` to be simultaneously canonical: the first follows the heuristic, the second follows established usage, and both are table entries.

#### Scenario: A table entry that contradicts the heuristic is still canonical
- **WHEN** `natural_freq`, `frf_form` or `mass_matrix` is assessed for conformance, each of which places the broader term second and therefore contradicts the word-order heuristic
- **THEN** each is conformant, because the canonical table has an entry for it
- **AND** no word-order violation is reported

#### Scenario: The heuristic governs a name the table does not cover
- **WHEN** a new compound name is coined for a quantity that has no canonical table entry, and no established domain term of art exists for it
- **THEN** the word-order heuristic applies and the broader term is placed first

#### Scenario: An established term of art overrides the heuristic
- **WHEN** a new compound name is coined for a quantity whose established name in the structural-dynamics literature places the broader term second
- **THEN** the established term is used and the heuristic yields
- **AND** the resulting name is added to the canonical table so the decision is recorded rather than re-litigated

### Requirement: Canonical names for modal quantities
The canonical names for modal quantities across sdypy-org first-level packages SHALL be: `mode_shape` for a mode shape vector or matrix; `damping_ratio` for a viscous damping ratio; `natural_freq` for a natural frequency in Hz; `n_modes` for a count of modes; `poles` for a collection of system poles. A first-level package that exposes any of these quantities in its public API MUST use the canonical name for it.

The arguments of the criterion functions `MAC`, `MSF` and `MCF` are an explicit, narrow exception: they SHALL keep the modal-literature symbols `phi_X` (experimental mode shape) and `phi_A` (analytical mode shape). This exception covers those three functions' arguments only and MUST NOT be generalised to other functions.

The `damping_ratio` rule binds names that expose a damping ratio. It does not
bind the spelling `xi` in every context: `xi`, `eta` and `zeta` are canonical
names for element natural coordinates, so a finite-element routine using them
conforms.

#### Scenario: Mode shape parameters use the canonical name
- **WHEN** a public function or method of a first-level package takes a mode shape as a parameter, other than `MAC`, `MSF` or `MCF`
- **THEN** the parameter is named `mode_shape`, not `phi` or `mode`

#### Scenario: Damping ratio parameters and attributes use the canonical name
- **WHEN** a public function, method or attribute of a first-level package exposes a viscous damping ratio
- **THEN** it is named `damping_ratio`, not `xi`, `nat_xi` or `pole_xi`

#### Scenario: An element coordinate named `xi` is not a damping violation
- **WHEN** a public finite-element routine declares a parameter `xi` that is an element natural coordinate rather than a damping ratio
- **THEN** no violation of the `damping_ratio` name is reported

#### Scenario: Criterion function arguments keep the literature symbols
- **WHEN** the signatures of `sdypy.EMA.MAC`, `sdypy.EMA.MSF` and `sdypy.EMA.MCF` are inspected
- **THEN** their mode shape arguments are named `phi_X` and `phi_A` (and `phi` for the single-argument `MCF`)
- **AND** this is recorded in SEP 2 as an exception, so it is not reported as a violation of the `mode_shape` requirement

#### Scenario: The exception does not extend beyond the criterion functions
- **WHEN** any public function other than `MAC`, `MSF` or `MCF` names a mode shape parameter `phi`, `phi_X` or `phi_A`
- **THEN** it is a violation of the canonical `mode_shape` name

### Requirement: Canonical names for system matrices
The canonical names for the system matrices of a discretised structural model SHALL be `mass_matrix`, `stiffness_matrix` and `damping_matrix`. Public functions, methods and attributes of first-level packages that accept or expose these matrices MUST use these names. Single uppercase letters (`K`, `M`, `C`) and compound abbreviations (`EI`) MUST NOT be used as public parameter names, as they already violate SEP 2's snake_case rule for parameters.

`EI` SHALL NOT be listed as a divergent spelling of `stiffness_matrix`. It is a
scalar bending rigidity (the product E·I), not a stiffness matrix, so renaming it
to `stiffness_matrix` would be wrong. It is a violation only of the snake_case
rule for public parameters, and its replacement is a descriptive snake_case name
chosen by the maintainer of the package that exposes it.

Local variables inside a function body are out of scope: this requirement binds the public surface only, so a numerical routine may still use short symbols internally.

#### Scenario: Eigenvalue solver parameters use the canonical matrix names
- **WHEN** the signature of a public eigenvalue-solving function of a first-level package is inspected
- **THEN** its matrix parameters are named `stiffness_matrix` and `mass_matrix`, not `K` and `M`

#### Scenario: Single uppercase letters are rejected as public parameter names
- **WHEN** a public function of a first-level package declares a parameter named `K`, `M`, `C` or `EI`
- **THEN** it is a violation, both of this requirement and of SEP 2's existing snake_case rule for parameters

#### Scenario: `EI` is reported without a canonical name being invented for it
- **WHEN** the checker audits a public signature declaring a parameter named `EI`
- **THEN** it reports a snake_case violation and states that the canonical table has no entry for it
- **AND** it does not propose `stiffness_matrix` as the replacement

#### Scenario: The stiffness matrix row does not claim `EI`
- **WHEN** the `stiffness_matrix` row of SEP 2's canonical variable table is inspected
- **THEN** neither its description nor its "Instead of" cell lists `EI`

#### Scenario: Internal variables are unaffected
- **WHEN** a function body assigns a local variable `K` while its public parameter is named `stiffness_matrix`
- **THEN** no violation is reported, because the requirement binds the public surface only

### Requirement: Canonical names for mesh and geometry
The canonical names for finite-element mesh data SHALL be `nodes` for the node coordinate array and `elements` for the element connectivity array. Public functions, methods and attributes of first-level packages that accept or expose mesh data MUST use these names.

#### Scenario: Mesh-consuming functions use the canonical names
- **WHEN** a public function or class constructor of a first-level package accepts finite-element mesh data
- **THEN** its parameters are named `nodes` and `elements`

#### Scenario: Connectivity abbreviations are rejected
- **WHEN** a public constructor declares parameters named `org` or `conec` for node coordinates and element connectivity
- **THEN** it is a violation of the canonical `nodes` / `elements` names

### Requirement: Counts and indices follow fixed affix conventions
A public name denoting a count of items SHALL be spelled `n_<plural>` (for example `n_modes`, `n_nodes`, `n_elements`, `n_frames`). A public name denoting an index into a collection SHALL be spelled `<name>_idx` (for example `node_idx`, `elem_idx`). The `_ind` suffix MUST NOT be used for indices, and a bare `n` MUST NOT be used for a count in a public signature.

#### Scenario: A count uses the n_ prefix with a plural noun
- **WHEN** a public method takes the number of modes to compute
- **THEN** the parameter is named `n_modes`, not `n`

#### Scenario: An index uses the _idx suffix
- **WHEN** a public function takes an index into a collection of FRFs or nodes
- **THEN** the parameter is named with the `_idx` suffix (`frf_idx`, `node_idx`), not `_ind`

#### Scenario: Both spellings in one org is the condition being removed
- **WHEN** the public surfaces of all six first-level packages are inspected for index parameters
- **THEN** every one of them uses `_idx`, and no public index parameter uses `_ind`

### Requirement: SEP 2 declares the extended canonical table and the precedence rule
`docs/seps/sep-0002.rst` SHALL be amended so that its canonical variable table contains entries for `mode_shape`, `damping_ratio`, `n_modes`, `mass_matrix`, `stiffness_matrix`, `damping_matrix`, `nodes` and `elements`, each with its unit where one applies and a description. The SEP SHALL additionally state, in prose: the precedence of the canonical table over the word-order heuristic; the `n_<plural>` and `<name>_idx` affix conventions; and the `MAC` / `MSF` / `MCF` argument exception for `phi_X` and `phi_A`. The existing eleven table entries and all existing prose rules SHALL be retained.

#### Scenario: The amended table contains the new canonical entries
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected after amendment
- **THEN** it contains rows for `mode_shape`, `damping_ratio`, `n_modes`, `mass_matrix`, `stiffness_matrix`, `damping_matrix`, `nodes` and `elements`

#### Scenario: The amended SEP states the precedence and affix rules
- **WHEN** the prose of `docs/seps/sep-0002.rst` is inspected after amendment
- **THEN** it states that the canonical table is normative and the word-order guideline is a heuristic for uncovered names that yields to established terms of art
- **AND** it states the `n_<plural>` count convention and the `<name>_idx` index convention
- **AND** it records the `phi_X` / `phi_A` exception for the criterion functions

#### Scenario: The amendment is additive
- **WHEN** `docs/seps/sep-0002.rst` is compared against its pre-amendment content
- **THEN** the PEP 8 reference, the naming-of-public-objects section, the public-API-surface section, the deprecation policy, and all eleven pre-existing table entries are still present
- **AND** the `:Status:` field is unchanged at `Draft`, because ratification is a separate, team-gated act

### Requirement: Evidenced divergences carry deprecated aliases to the canonical names
Every public name in a first-level package that diverges from a canonical table entry SHALL be renamed to the canonical name, with the divergent name retained as an alias that emits `DeprecationWarning`, per SEP 2's existing deprecation policy: aliases remain functional through all of v1.x and are removed no earlier than v2.0. Positional callers MUST be unaffected by keyword renames.

The inventory of evidenced divergences SHALL be derived from the output of
`tools/check_nomenclature.py` against the sibling clones, not asserted
independently of it. A name that no longer appears in any first-level package
MUST NOT be carried in the inventory.

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
`_idx` spellings.

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
- **THEN** that entry is removed from the inventory and from the `REQUIREMENTS.md` pending roster

### Requirement: Nomenclature conformance is mechanically enforced
The canonical-name contract SHALL be enforced by a standalone conformance checker, `tools/check_nomenclature.py`, following the pattern of the existing repo-layer checkers: it accepts a `--path` argument identifying a first-level package clone, prints one violation per line, exits `0` when the clone conforms and non-zero otherwise, and depends only on the Python standard library. The checker MUST determine public names by static analysis, without importing the audited package, so that packages whose import requires an optional backend (`sdypy.view` and `sdypy.model` require a Qt binding) can be audited in an environment that lacks it.

The checker MUST NOT enforce a divergent spelling whose meaning it cannot
determine statically. Where a spelling is canonical in one domain and divergent
in another, the checker enforces only the unambiguous spellings and records the
ambiguous one as outside its coverage.

#### Scenario: A conforming clone passes
- **WHEN** the checker is run against a first-level package clone whose public signatures use only canonical names
- **THEN** it prints no violation and exits `0`

#### Scenario: A non-canonical parameter name is reported
- **WHEN** the checker audits a public function declaring a parameter named `phi`, `K`, `conec`, `frf_type` or `frequency`
- **THEN** it reports a violation naming the file, the function, the offending parameter, and the canonical name it should use
- **AND** the checker exits non-zero

#### Scenario: An element natural coordinate is not reported
- **WHEN** the checker audits a public function declaring parameters `xi`, `eta` or `zeta`
- **THEN** no violation is reported for them

#### Scenario: The evidenced damping spellings are reported
- **WHEN** the checker audits a public attribute or parameter named `nat_xi` or `pole_xi`
- **THEN** it reports a violation naming `damping_ratio` as the canonical name

#### Scenario: The affix conventions are enforced
- **WHEN** the checker audits a public signature declaring an index parameter spelled with the `_ind` suffix, or a bare `n` used as a count
- **THEN** it reports a violation naming the required `_idx` or `n_<plural>` spelling

#### Scenario: The criterion-function exception is applied to exactly three names
- **WHEN** the checker audits `MAC`, `MSF` and `MCF` declaring `phi_X`, `phi_A` or `phi` arguments
- **THEN** no violation is reported for those three functions
- **AND** the same argument names in any other public function are reported as violations

#### Scenario: Auditing does not require the package to be importable
- **WHEN** the checker is run against a clone of `sdypy-view` or `sdypy-model` in an environment with no Qt binding installed
- **THEN** it completes and reports its findings, rather than failing with an import error

### Requirement: The checker declares its coverage boundary
`tools/check_nomenclature.py` SHALL state, in its module docstring, which requirements of the nomenclature contract it does not verify, and `REQUIREMENTS.md` SHALL NOT record a requirement as checker-verified unless the checker actually decides it. The parts that are not statically decidable — whether a coined name corresponds to an established term of art, whether a bare `xi` denotes a damping ratio or an element natural coordinate, and whether a deprecated alias emits `DeprecationWarning` and returns the same value as its canonical counterpart — MUST remain attributed to sibling test suites or to `manual` verification.

#### Scenario: The uncovered requirements are named in the checker
- **WHEN** the module docstring of `tools/check_nomenclature.py` is read
- **THEN** it names the term-of-art judgement, the damping-versus-coordinate reading of a bare `xi`, and the deprecated-alias behaviour as outside the checker's scope

#### Scenario: The requirements roster does not overclaim
- **WHEN** the `public-api` rows of `REQUIREMENTS.md` are inspected after the checker lands
- **THEN** the rows for the rename obligations and the term-of-art rule are attributed to sibling suites or `manual`, not to `check_nomenclature.py`

### Requirement: Sibling nomenclature conformance is a pre-release gate
The core test suite SHALL verify the nomenclature contract against the installed first-level packages, and those tests SHALL carry the `pypi_artifacts` marker so they are deselected on GitHub CI and run locally as the pre-release gate. The checker's own logic SHALL additionally be covered by unmarked unit tests that run in core CI against synthetic fixtures and require no sibling package to be installed.

#### Scenario: Checker unit tests run in core CI
- **WHEN** `pytest -m "not pypi_artifacts"` is run in an environment with no first-level package installed
- **THEN** the checker's unit tests execute and pass

#### Scenario: Sibling conformance runs only as the local gate
- **WHEN** `pytest -m "not pypi_artifacts"` is run
- **THEN** the tests that audit the installed sibling packages are deselected
- **AND** a plain `pytest` run selects them, so a divergent published release is caught before the next release

#### Scenario: Recorded divergences do not redden core CI
- **WHEN** core CI runs while the installed siblings still ship names the canonical table has renamed
- **THEN** the CI job passes, because those assertions are `pypi_artifacts`-marked

### Requirement: SEP 2 declares the divergent spellings each canonical name replaces
The canonical variable table of `docs/seps/sep-0002.rst` SHALL carry an
"Instead of" column listing, for each canonical name, the divergent spellings it
replaces. That column SHALL be normative: SEP 2 is the single source of truth
for the nomenclature migration map, and no other artefact may introduce a
divergent-spelling mapping the SEP does not carry.

A canonical name that replaces no evidenced divergent spelling SHALL leave the
column empty rather than invent one. Adding a spelling to the column is an
amendment to SEP 2 and follows the same review path as any other SEP amendment.

#### Scenario: The table carries the migration map
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected
- **THEN** it has an "Instead of" column
- **AND** the divergent spellings that first-level packages are required to rename away from appear in that column against their canonical name

#### Scenario: A canonical name with no evidenced divergence has an empty cell
- **WHEN** a canonical table entry replaces no divergent spelling found in any first-level package
- **THEN** its "Instead of" cell is empty

#### Scenario: A mapping absent from SEP 2 is not enforceable
- **WHEN** any tooling or roster asserts that a divergent spelling must be renamed to a canonical name
- **AND** that spelling does not appear in SEP 2's "Instead of" column
- **THEN** the assertion is a violation of this requirement, and the fix is to amend SEP 2 or drop the assertion

### Requirement: Canonical names for element natural coordinates
The natural (isoparametric) coordinates of a finite element SHALL be named
`xi`, `eta` and `zeta`. These are ratified names of an established term of art
in finite-element analysis, not divergent spellings.
Public functions, methods and attributes of first-level packages that accept or
expose element natural coordinates MUST use them, and MUST NOT be required to
rename them to any other spelling.

This requirement scopes the `damping_ratio` rule: a bare `xi` in a
finite-element context is an element coordinate and conforms; a damping ratio
must still use `damping_ratio` wherever it is exposed.

#### Scenario: Shape functions keep the isoparametric coordinate names
- **WHEN** a public shape-function or element-integration routine of a first-level package takes element natural coordinates as parameters
- **THEN** they are named `xi`, `eta` and `zeta`
- **AND** no nomenclature violation is reported for them

#### Scenario: The coordinate entry does not license `xi` for damping
- **WHEN** a public name exposes a viscous damping ratio under the spelling `xi`
- **THEN** it is a violation of the canonical `damping_ratio` name, because the coordinate entry covers element geometry only

### Requirement: The nomenclature checker mirrors SEP 2 in both directions
The migration map embedded in `tools/check_nomenclature.py` SHALL be a faithful
mirror of SEP 2's "Instead of" column, and the core test suite SHALL pin the
correspondence in **both** directions: every divergent spelling the checker
enforces MUST appear in SEP 2's column, and every spelling in SEP 2's column
MUST be enforced by the checker. Pinning only the canonical targets is
insufficient, because it permits the checker to enforce a rename the SEP has
never ratified.

#### Scenario: A checker-only divergent spelling fails the suite
- **WHEN** a divergent spelling is added to the checker's migration map without a corresponding entry in SEP 2's "Instead of" column
- **THEN** the core test suite fails, naming the unratified spelling

#### Scenario: A SEP entry the checker ignores fails the suite
- **WHEN** a divergent spelling is added to SEP 2's "Instead of" column and the checker's map is not updated
- **THEN** the core test suite fails, naming the unenforced spelling

#### Scenario: The two-way pin runs without a sibling installed
- **WHEN** `pytest -m "not pypi_artifacts"` is run in an environment with no first-level package installed
- **THEN** the two-way mirror tests execute and pass

