## Purpose
The contract for SEP document metadata: the header preamble that every `docs/seps/sep-<nnnn>.rst` must declare, the closed `Status` and `Type` vocabularies, the ISO 8601 `Created` format, the `Resolution` field required by ratification, and the standalone checker that enforces all of it in CI. This capability covers the mechanically checkable subset of SEP 0 only; SEP 0's human process (champion, consensus, discussion period) is deliberately out of scope. Established by the `add-sep-governance-checks` change.

## ADDED Requirements

### Requirement: Every SEP declares the required header fields
Every `docs/seps/sep-<nnnn>.rst` file, excluding `sep-template.rst`, SHALL declare the header fields `:Authors:`, `:Status:`, `:Type:` and `:Created:` in its RST field-list preamble. `:Authors:` is the canonical spelling; `:Author:` MUST NOT be used. A field value MAY continue onto following indented lines, and the continuation MUST be treated as part of the value. A SEP whose `:Status:` is `Accepted`, `Rejected` or `Withdrawn` SHALL additionally declare `:Resolution:` with a non-empty value.

#### Scenario: A conforming SEP declares all four required fields
- **WHEN** the checker reads a SEP that declares `:Authors:`, `:Status:`, `:Type:` and `:Created:`
- **THEN** it reports no missing-field violation for that SEP

#### Scenario: A missing required field is reported
- **WHEN** the checker reads a SEP whose preamble omits `:Created:`
- **THEN** it reports a violation naming the file and the missing field
- **AND** the checker exits non-zero

#### Scenario: The deprecated singular spelling is reported
- **WHEN** the checker reads a SEP that declares `:Author:` instead of `:Authors:`
- **THEN** it reports a violation naming the file and the deprecated field spelling

#### Scenario: A multi-line author field is read in full
- **WHEN** the checker reads `sep-0004.rst`, whose `:Authors:` value continues onto two indented lines
- **THEN** the parsed value contains all three authors, not only those on the first line

#### Scenario: Ratification without a Resolution is reported
- **WHEN** the checker reads a SEP whose `:Status:` is `Accepted` and which declares no `:Resolution:`
- **THEN** it reports a violation naming the file
- **AND** the violation is reported by the checker itself, not only as a `build_index.py` traceback

### Requirement: Status is drawn from a closed vocabulary
The `:Status:` value of every SEP SHALL be exactly one of `Draft`, `Active`, `Provisional`, `Accepted`, `Final`, `Deferred`, `Superseded`, `Rejected`, `Withdrawn` — case-sensitive. This vocabulary is exactly the set of values that `docs/seps/index.rst.tmpl` renders into a toctree section; any other value causes the SEP to be omitted from every section of the generated index without error, which this requirement exists to prevent. `sep-template.rst` SHALL declare the same vocabulary.

#### Scenario: An unknown status is reported
- **WHEN** the checker reads a SEP whose `:Status:` is `In progress`
- **THEN** it reports a violation naming the file, the offending value, and the permitted vocabulary
- **AND** the checker exits non-zero

#### Scenario: A mis-cased status is reported
- **WHEN** the checker reads a SEP whose `:Status:` is `draft`
- **THEN** it reports a violation, because the comparison is case-sensitive

#### Scenario: The template declares the same status vocabulary
- **WHEN** `docs/seps/sep-template.rst` is read
- **THEN** its `:Status:` placeholder lists exactly the nine permitted values, including `Provisional`

### Requirement: Type is drawn from a closed vocabulary
The `:Type:` value of every SEP SHALL be exactly one of `Standards Track`, `Informational`, `Process` — the three kinds SEP 0 defines, case-sensitive. `sep-template.rst` SHALL declare the same three values.

#### Scenario: SEP 5's abbreviated type is corrected
- **WHEN** the checker reads `sep-0005.rst` after this change
- **THEN** its `:Type:` is `Standards Track`, not `Standards`
- **AND** the checker reports no type violation

#### Scenario: An out-of-vocabulary type is reported
- **WHEN** the checker reads a SEP whose `:Type:` is `Standards`
- **THEN** it reports a violation naming the file, the offending value, and the three permitted values

#### Scenario: The template declares all three types
- **WHEN** `docs/seps/sep-template.rst` is read
- **THEN** its `:Type:` placeholder lists `Standards Track`, `Informational` and `Process`

### Requirement: Created is an ISO 8601 date
The `:Created:` value of every SEP SHALL be a calendar date in `yyyy-mm-dd` form, as `sep-template.rst` prescribes.

#### Scenario: A non-ISO date is reported
- **WHEN** the checker reads a SEP whose `:Created:` is `2-Nov-2020`
- **THEN** it reports a violation naming the file and the offending value

#### Scenario: SEP 0's creation date is normalised
- **WHEN** `docs/seps/sep-0000.rst` is read after this change
- **THEN** its `:Created:` is `2020-11-02`

### Requirement: SEP metadata conformance is mechanically enforced
SEP metadata conformance SHALL be enforced by `tools/check_seps.py`, a standalone checker following the conventions of the existing repository checkers: it accepts `--path`, prints one line per violation identifying the file and the rule, exits `0` when the SEP set conforms and non-zero otherwise. It SHALL be invoked in the docs CI job before `docs/seps/tools/build_index.py`, so a metadata error surfaces as a named violation rather than a generator traceback. A test in `tests/` SHALL invoke the same checks so that a plain `pytest` run fails on a non-conforming SEP set. The checker SHALL be the conformance authority; the existing `build_index.py` validations are retained as generator preconditions and MUST NOT be the only gate.

#### Scenario: The checker passes on the conforming repository
- **WHEN** `python tools/check_seps.py --path .` is run on the core repository after this change
- **THEN** it prints no violations and exits `0`

#### Scenario: The checker runs ahead of the index generator in CI
- **WHEN** `.github/workflows/docs.yml` is read
- **THEN** it contains a step invoking `tools/check_seps.py` that precedes the `build_index.py` step

#### Scenario: A non-conforming SEP fails the test suite
- **WHEN** a SEP with an out-of-vocabulary `:Status:` is present and `pytest -m "not pypi_artifacts"` is run
- **THEN** the SEP governance test fails and names the offending file
