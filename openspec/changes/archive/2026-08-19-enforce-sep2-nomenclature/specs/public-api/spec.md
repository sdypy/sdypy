## ADDED Requirements

### Requirement: Nomenclature conformance is mechanically enforced
The canonical-name contract SHALL be enforced by a standalone conformance checker, `tools/check_nomenclature.py`, following the pattern of the existing repo-layer checkers: it accepts a `--path` argument identifying a first-level package clone, prints one violation per line, exits `0` when the clone conforms and non-zero otherwise, and depends only on the Python standard library. The checker MUST determine public names by static analysis, without importing the audited package, so that packages whose import requires an optional backend (`sdypy.view` and `sdypy.model` require a Qt binding) can be audited in an environment that lacks it.

#### Scenario: A conforming clone passes
- **WHEN** the checker is run against a first-level package clone whose public signatures use only canonical names
- **THEN** it prints no violation and exits `0`

#### Scenario: A non-canonical parameter name is reported
- **WHEN** the checker audits a public function declaring a parameter named `xi`, `phi`, `K`, `conec` or `frequency`
- **THEN** it reports a violation naming the file, the function, the offending parameter, and the canonical name it should use
- **AND** the checker exits non-zero

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
`tools/check_nomenclature.py` SHALL state, in its module docstring, which requirements of the nomenclature contract it does not verify, and `REQUIREMENTS.md` SHALL NOT record a requirement as checker-verified unless the checker actually decides it. The parts that are not statically decidable — whether a coined name corresponds to an established term of art, and whether a deprecated alias emits `DeprecationWarning` and returns the same value as its canonical counterpart — MUST remain attributed to sibling test suites or to `manual` verification.

#### Scenario: The uncovered requirements are named in the checker
- **WHEN** the module docstring of `tools/check_nomenclature.py` is read
- **THEN** it names the term-of-art judgement and the deprecated-alias behaviour as outside the checker's scope

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
