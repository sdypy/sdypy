## ADDED Requirements

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

## MODIFIED Requirements

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
