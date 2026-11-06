## ADDED Requirements

### Requirement: SEP 2 records its relation to ISO 7626
SEP 2 SHALL name ISO 7626 (*Mechanical vibration and shock — Experimental determination of mechanical mobility*) as the external terminology reference for the quantities that standard defines, and SHALL record every place where a canonical SDyPy name diverges from the ISO-preferred term.

A divergence is permitted, but it MUST be deliberate and reasoned on the record. An undocumented divergence is a defect in SEP 2, not in the package that follows the table.

At the time of writing there is exactly one: the `frf_form` value `'receptance'` against ISO 7626-1's preferred *dynamic compliance*. ISO recognises *receptance* as a synonym; SEP 2 keeps it because it is the entrenched term in the modal-testing literature and the existing API string in `sdypy-EMA` and the pyFRF backend.

#### Scenario: The ISO relation is stated in the SEP
- **WHEN** `docs/seps/sep-0002.rst` is read
- **THEN** it names ISO 7626 as the terminology reference for the quantities that standard defines
- **AND** it records `'receptance'` as a deliberate divergence, with the reason

#### Scenario: A new divergence must be recorded
- **WHEN** a canonical name is adopted that differs from the ISO-preferred term for the same quantity
- **THEN** SEP 2 records the divergence and the reason in the same amendment that adopts the name

### Requirement: A name for an uncovered quantity satisfies the guidelines and ISO 7626
A public name coined for a quantity that the canonical table does not cover SHALL satisfy both the SEP 2 general guidelines and the ISO 7626 terminology, where ISO defines that quantity. Where ISO defines no term for it, the general guidelines and the existing precedence rule govern alone, and ISO's silence is not itself a violation.

This composes with the existing precedence requirement rather than replacing it: a canonical table entry still wins over everything, and an established domain term of art still overrides the word-order heuristic.

#### Scenario: ISO defines the quantity
- **WHEN** a public name is coined for a quantity that ISO 7626 defines, and the canonical table has no entry for it
- **THEN** the ISO-preferred term is used, adapted to the `snake_case` conventions of SEP 2

#### Scenario: ISO is silent on the quantity
- **WHEN** a public name is coined for a quantity that ISO 7626 does not define
- **THEN** the general guidelines and the precedence rule govern, and the absence of an ISO term is not a violation

### Requirement: The pull-request author declares new public names
The author of a pull request that introduces a public name for a quantity the canonical table does not cover SHALL declare that name in the pull request, and the reviewer SHALL assess it against the general guidelines and ISO 7626. Conformance to SEP 2 is the author's responsibility: no tool detects an undeclared new name.

The discussion happens in that pull request. A separate SEP amendment pull request MUST NOT be required before it can merge, and an uncontested name merges with its feature.

A name is escalated only when the pull request cannot settle it — the guidelines and ISO conflict, ISO is silent where a term was expected, or the reviewers disagree. Escalation is an issue on `sdypy` followed by a pull request amending SEP 2, and it blocks the contested name alone, not the rest of the feature.

#### Scenario: An uncontested declared name lands with its feature
- **WHEN** an author declares a new public name in a feature pull request and the reviewer accepts it against the guidelines and ISO 7626
- **THEN** the name merges with the feature
- **AND** no separate SEP amendment pull request is opened before the merge

#### Scenario: A contested name escalates alone
- **WHEN** a declared name cannot be settled in the pull request because the guidelines and ISO conflict, or the reviewers disagree
- **THEN** the question goes to an issue on `sdypy` and a pull request amending SEP 2
- **AND** the rest of the feature is not blocked

### Requirement: Declared names reach the table through a ledger and a triggered amendment
Declared names SHALL be collected on a *SEP 2 pending terms* issue and MUST reach the canonical table through an amendment pull request that a maintainer triggers, not through an edit made by the declaring author in passing.

The issue is not permanent. One is opened when the first name since the last amendment is declared, and the amendment pull request closes it. An open issue is therefore itself the signal that an amendment is due, and no empty issue sits around between rounds.

The amendment is triggered manually, with a reminder at release time. It is not scheduled: term churn is low, and a periodic trigger would mostly produce empty pull requests.

The amendment is largely mechanical transcription, because the naming dilemmas were settled in the pull requests that introduced the names. A human reviews and merges it regardless. Recording never gates a feature pull request.

#### Scenario: A declared name is recorded later, in batch
- **WHEN** names have been declared and merged since the last SEP 2 amendment
- **THEN** a *SEP 2 pending terms* issue is open and lists them
- **AND** a triggered amendment pull request adds the agreed ones to the canonical table
- **AND** no feature pull request was blocked waiting for it

#### Scenario: The amendment is reviewed by a human
- **WHEN** an amendment pull request is opened from the ledger
- **THEN** a maintainer reviews and merges it, rather than it landing automatically

### Requirement: The narrative docs carry the worked procedure, not the SEP
The umbrella narrative documentation SHALL carry the operational detail of the naming procedure — how to check a proposed name, what the checker does and does not decide, and how a settled name reaches the canonical table — so that SEP 2 states the rule and stays short.

The checking section MUST state that `tools/check_nomenclature.py` is not run automatically against any package: the umbrella CI excludes it by design, and nothing else invokes it, so it is run by hand against a clone. It MUST state the four faults the checker decides, and that a clean run means no known fault rather than a good name.

The recording section MUST give the ordered steps: the `list-table` row in `docs/seps/sep-0002.rst`, the `CANONICAL` entry in `tools/check_nomenclature.py` for any evidenced divergent spelling, then the test run. The existing two-way mirror tests are the gate: a table row whose divergent spellings are absent from the map, or a map entry absent from the table, MUST fail the suite rather than merge silently.

#### Scenario: A contributor checks a proposed name
- **WHEN** a contributor consults the narrative nomenclature page before proposing a public name
- **THEN** it tells them how to run the checker by hand, that nothing runs it for them, and what it does and does not decide

#### Scenario: A contributor records a settled name
- **WHEN** a contributor follows the documented steps to add a settled name to the canonical table
- **THEN** the steps cover the SEP table row, the checker map, and the test run
- **AND** omitting the checker map for a name that replaces a divergent spelling fails the mirror tests
