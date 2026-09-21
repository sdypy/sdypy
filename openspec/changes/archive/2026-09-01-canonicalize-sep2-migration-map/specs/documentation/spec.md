## ADDED Requirements

### Requirement: The canonical variable table is surfaced in the narrative docs by transclusion
The umbrella documentation SHALL present the SEP 2 canonical variable table on a
narrative page, so that a contributor looking up a name does not have to read the
whole SEP. The table SHALL have exactly one definition — the one in
`docs/seps/sep-0002.rst` — and the narrative page SHALL transclude the
marker-delimited table region rather than restating it.

Restating the table, in whole or in part, in any other file is a violation: a
copy can drift from the SEP, which is the source of truth for the canonical
names and for the divergent spellings they replace.

The narrative page SHALL render only the table region and its surrounding
explanation, not the full SEP text, and SHALL link to SEP 2 for the governance
context, deprecation policy and status.

#### Scenario: The table renders on the narrative page
- **WHEN** the umbrella docs are built and the nomenclature page is opened
- **THEN** the canonical variable table is rendered on it, including the "Instead of" column

#### Scenario: The table has a single definition
- **WHEN** the documentation sources are inspected
- **THEN** the table rows appear literally in `docs/seps/sep-0002.rst` only
- **AND** the narrative page reaches them through an include directive bounded by the region markers, not through a copy

#### Scenario: Editing the SEP updates the narrative page
- **WHEN** a row is added to the canonical variable table in `docs/seps/sep-0002.rst`
- **AND** the docs are rebuilt without any other edit
- **THEN** the new row appears on the narrative page

#### Scenario: The narrative page is not a second copy of the SEP
- **WHEN** the rendered nomenclature page is inspected
- **THEN** it does not reproduce the SEP's header fields, abstract, deprecation policy or status
- **AND** it links to the rendered SEP 2 page for them

#### Scenario: The page is reachable from the documentation tree
- **WHEN** the built umbrella site is navigated from its landing page
- **THEN** the nomenclature page is reachable through the toctree
