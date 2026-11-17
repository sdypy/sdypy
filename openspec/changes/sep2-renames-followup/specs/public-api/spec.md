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
`model.Tetrahedron`); `nat_xi` → `damping_ratio` and `phi` → `mode_shape` in
EMA public signatures other than the criterion functions;
`lower`, `upper`, `f_lower`, `f_upper` → `freq_lower` and `freq_upper` (EMA);
`frf_type` → `frf_form` (EMA); `K`, `M` → `stiffness_matrix`,
`mass_matrix` (model); `E`, `Young` → `young_modulus`, `nu`, `Poisson` →
`poisson_ratio`, `rho`, `ro`, `Density` → `density` (model); `org`, `conec` →
`nodes`, `elements` (`model.Beam`, `model.Tetrahedron`); `n` → `n_modes`
(`model.Beam.solve`); `A` → `mode_shape` (eigenvector attribute), `A` →
`area` (cross-section) and `frequency` → `freq` (model); `FRF_ind`, `lower_ind`, `upper_ind`, `pole_ind` (EMA) and
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
