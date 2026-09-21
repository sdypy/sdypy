## ADDED Requirements

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

#### Scenario: Mode shape parameters use the canonical name
- **WHEN** a public function or method of a first-level package takes a mode shape as a parameter, other than `MAC`, `MSF` or `MCF`
- **THEN** the parameter is named `mode_shape`, not `phi` or `mode`

#### Scenario: Damping ratio parameters and attributes use the canonical name
- **WHEN** a public function, method or attribute of a first-level package exposes a viscous damping ratio
- **THEN** it is named `damping_ratio`, not `xi`

#### Scenario: Criterion function arguments keep the literature symbols
- **WHEN** the signatures of `sdypy.EMA.MAC`, `sdypy.EMA.MSF` and `sdypy.EMA.MCF` are inspected
- **THEN** their mode shape arguments are named `phi_X` and `phi_A` (and `phi` for the single-argument `MCF`)
- **AND** this is recorded in SEP 2 as an exception, so it is not reported as a violation of the `mode_shape` requirement

#### Scenario: The exception does not extend beyond the criterion functions
- **WHEN** any public function other than `MAC`, `MSF` or `MCF` names a mode shape parameter `phi`, `phi_X` or `phi_A`
- **THEN** it is a violation of the canonical `mode_shape` name

### Requirement: Canonical names for system matrices
The canonical names for the system matrices of a discretised structural model SHALL be `mass_matrix`, `stiffness_matrix` and `damping_matrix`. Public functions, methods and attributes of first-level packages that accept or expose these matrices MUST use these names. Single uppercase letters (`K`, `M`, `C`) and compound abbreviations (`EI`) MUST NOT be used as public parameter names, as they already violate SEP 2's snake_case rule for parameters.

Local variables inside a function body are out of scope: this requirement binds the public surface only, so a numerical routine may still use short symbols internally.

#### Scenario: Eigenvalue solver parameters use the canonical matrix names
- **WHEN** the signature of a public eigenvalue-solving function of a first-level package is inspected
- **THEN** its matrix parameters are named `stiffness_matrix` and `mass_matrix`, not `K` and `M`

#### Scenario: Single uppercase letters are rejected as public parameter names
- **WHEN** a public function of a first-level package declares a parameter named `K`, `M`, `C` or `EI`
- **THEN** it is a violation, both of this requirement and of SEP 2's existing snake_case rule for parameters

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

The inventory of evidenced divergences covered by this requirement is: `nat_freq` → `natural_freq` (public attribute of `EMA.Model`, `model.Beam`, `model.Tetrahedron`); `xi` → `damping_ratio` and `phi` → `mode_shape` in EMA public signatures other than the criterion functions; `lower`, `upper`, `f_lower`, `f_upper` → `freq_lower` and `freq_upper` (EMA); `frequency` → `freq` (model); `K`, `M`, `EI` → `stiffness_matrix`, `mass_matrix` (model); `org`, `conec` → `nodes`, `elements` (`model.Beam`); `n` → `n_modes` (`model.Beam.solve`); `FRF_ind`, `lower_ind`, `upper_ind` → the corresponding `_idx` spellings (EMA).

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
