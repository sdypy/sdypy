## ADDED Requirements

### Requirement: Canonical name for the FRF estimator
The choice of FRF estimator SHALL be named `frf_estimator` in the public API of every first-level package, including backend objects it re-exports. Its values SHALL be `'H1'`, `'H2'`, `'Hv'` and `'ODS'`. It MUST NOT share a name with the FRF form, which remains `frf_form`.

ISO 7626 does not name this quantity, so the general guidelines govern. SEP 2 SHALL record in its "Relation to ISO 7626" section that ISO 18431-1 calls H1 and H2 the frequency response function "of the first type" and "of the second type", and that SDyPy follows the modal-testing literature's term *estimator* instead, because `type` is ambiguous and shadows a Python built-in.

#### Scenario: The table carries the estimator row
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected
- **THEN** it has an *FRF estimator* row with canonical name `frf_estimator` and the values `'H1'`, `'H2'`, `'Hv'` and `'ODS'`

#### Scenario: The estimator is selected by its canonical name
- **WHEN** user code constructs `sdypy.FRF.FRF(..., frf_estimator='H2')` and calls `get_FRF(frf_estimator='default', frf_form='accelerance')`
- **THEN** no warning is emitted and the H2 accelerance is returned

#### Scenario: The ISO wording is on the record
- **WHEN** the "Relation to ISO 7626" section of SEP 2 is read
- **THEN** it cites ISO 18431-1's "first type" / "second type" wording and gives the reason for `frf_estimator`

### Requirement: SEP 2 binds the signatures of re-exported backend objects
When a first-level package re-exports a class or function from a backend package, the signature and public attributes of that object SHALL be treated as part of the first-level package's public API and SHALL follow SEP 2. Backend names that a first-level package does not re-export remain out of scope.

#### Scenario: A re-exported backend class is in scope
- **WHEN** `sdypy.FRF` re-exports pyFRF's `FRF` class unchanged
- **THEN** the parameter names of `FRF.__init__` and `FRF.get_FRF` and the public attributes of `FRF` instances are assessed against SEP 2

#### Scenario: A backend name that is not re-exported is out of scope
- **WHEN** a backend package exposes a function that no first-level package re-exports
- **THEN** SEP 2 makes no demand on its names

#### Scenario: The table no longer excludes backend names
- **WHEN** the *FRF form* row of the canonical table is read
- **THEN** it does not state that backend parameter names are out of scope

## MODIFIED Requirements

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
instance attribute of `FRF`, re-exported by `sdypy.FRF` from pyFRF);
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

### Requirement: SEP 2 declares the divergent spellings each canonical name replaces
The canonical variable table of `docs/seps/sep-0002.rst` SHALL carry an
"Instead of" column listing, for each canonical name, the divergent spellings it
replaces. That column SHALL be normative: SEP 2 is the single source of truth
for the nomenclature migration map, and no other artefact may introduce a
divergent-spelling mapping the SEP does not carry.

A canonical name that replaces no evidenced divergent spelling SHALL leave the
column empty rather than invent one.

A spelling whose meaning depends on its context (it is canonical, or names a
different quantity, elsewhere) SHALL NOT be listed in the column, because the
checker reports every spelling in the column on sight. Such a spelling SHALL
instead be recorded in the notes below the table, naming the context in which
it diverges and its canonical replacement there. Those notes are part of the
migration map. The bare `xi`, the bare `phi`, the estimator sense of
`frf_type`, and the `get_FRF` parameters `type` and `form` are recorded this
way. Adding a spelling to the column is an
amendment to SEP 2 and follows the same review path as any other SEP amendment.

#### Scenario: The table carries the migration map
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected
- **THEN** it has an "Instead of" column
- **AND** every divergent spelling that first-level packages are required to rename away from appears either in that column against its canonical name or, if its meaning depends on its context, in a note below the table

#### Scenario: A canonical name with no evidenced divergence has an empty cell
- **WHEN** a canonical table entry replaces no divergent spelling found in any first-level package, or replaces only context-dependent spellings recorded in the notes
- **THEN** its "Instead of" cell is empty

#### Scenario: A mapping absent from SEP 2 is not enforceable
- **WHEN** any tooling or roster asserts that a divergent spelling must be renamed to a canonical name
- **AND** that spelling appears neither in SEP 2's "Instead of" column nor in a note below the table
- **THEN** the assertion is a violation of this requirement, and the fix is to amend SEP 2 or drop the assertion

#### Scenario: A context-dependent spelling stays out of the column
- **WHEN** the canonical variable table in `docs/seps/sep-0002.rst` is inspected
- **THEN** `type` and `form` do not appear in any "Instead of" cell, and `frf_type` appears only against `frf_form`
- **AND** a note below the table records `frf_type` (on an FRF estimator), `type` and `form` (on `get_FRF`) with their canonical replacements

### Requirement: Nomenclature conformance is mechanically enforced
The canonical-name contract SHALL be enforced by a standalone conformance checker, `tools/check_nomenclature.py`, following the pattern of the existing repo-layer checkers: it accepts a `--path` argument identifying a first-level package clone, prints one violation per line, exits `0` when the clone conforms and non-zero otherwise, and depends only on the Python standard library. The checker MUST determine public names by static analysis, without importing the audited package, so that packages whose import requires an optional backend (`sdypy.view` and `sdypy.model` require a Qt binding) can be audited in an environment that lacks it.

The checker MUST NOT enforce a divergent spelling whose meaning it cannot
determine statically. Where a spelling is canonical in one domain and divergent
in another, the checker enforces only the unambiguous spellings and records the
ambiguous one as outside its coverage.

A spelling whose second meaning occurs only on re-exported backend objects is
unambiguous within the checker's reach, because the checker audits only the
portion under `sdypy/` and never the backend. Such a spelling SHALL stay
enforced for the meaning the checker can see. `frf_type` is the one case: the
checker enforces it as `frf_form`, and its estimator sense on pyFRF's `FRF` is
left to pyFRF's tests.

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

#### Scenario: Generic backend parameter names are not reported
- **WHEN** the checker audits a public method declaring parameters named `type` or `form`
- **THEN** no `nomenclature` violation is reported for them

### Requirement: The checker declares its coverage boundary
`tools/check_nomenclature.py` SHALL state, in its module docstring, which requirements of the nomenclature contract it does not verify, and `REQUIREMENTS.md` SHALL NOT record a requirement as checker-verified unless the checker actually decides it. The parts that are not statically decidable — whether a coined name corresponds to an established term of art, whether a bare `xi` denotes a damping ratio or an element natural coordinate, whether a deprecated alias emits `DeprecationWarning` and returns the same value as its canonical counterpart, and the names of re-exported backend objects — MUST remain attributed to sibling or backend test suites or to `manual` verification.

#### Scenario: The uncovered requirements are named in the checker
- **WHEN** the module docstring of `tools/check_nomenclature.py` is read
- **THEN** it names the term-of-art judgement, the damping-versus-coordinate reading of a bare `xi`, the deprecated-alias behaviour, and the names of re-exported backend objects as outside the checker's scope

#### Scenario: The requirements roster does not overclaim
- **WHEN** the `public-api` rows of `REQUIREMENTS.md` are inspected after the checker lands
- **THEN** the rows for the rename obligations and the term-of-art rule are attributed to sibling suites or `manual`, not to `check_nomenclature.py`
