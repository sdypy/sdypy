## ADDED Requirements

### Requirement: Deprecated aliases are not reported as divergences
The nomenclature checker SHALL NOT report a divergent name that the audited code already treats as deprecated, because *Evidenced divergences carry deprecated aliases to the canonical names* requires such names to remain. A name counts as deprecated when, statically, either the parameter is tested in a conditional whose body calls `warnings.warn` with category `DeprecationWarning`, or the function or method that declares it calls `warnings.warn` with category `DeprecationWarning` unconditionally at the top level of its body, or is decorated with `deprecated`. The same divergent name without such a guard MUST still be reported.

#### Scenario: A warned parameter alias is not reported
- **WHEN** the checker audits a public function declaring `frf_type=None` whose body contains `if frf_type is not None:` followed by `warnings.warn(..., DeprecationWarning)`
- **THEN** no violation is reported for `frf_type`

#### Scenario: Parameters of a deprecated method are not reported
- **WHEN** the checker audits a public method whose body begins by calling `warnings.warn(..., DeprecationWarning)` unconditionally and which declares a parameter `FRF_ind`
- **THEN** no violation is reported for `FRF_ind`

#### Scenario: An unguarded divergent name is still reported
- **WHEN** the checker audits a public function declaring `frf_type` with no deprecation warning guarding it
- **THEN** it reports `frf_type` with the canonical name `frf_form`

#### Scenario: A warning of another category does not exempt a name
- **WHEN** the conditional that tests a divergent parameter calls `warnings.warn` with `UserWarning` or `FutureWarning`
- **THEN** the parameter is still reported

## MODIFIED Requirements

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
- **WHEN** the checker audits a public function declaring a parameter named `phi`, `K`, `conec`, `frf_type` or `frequency` that is not a deprecated alias
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
