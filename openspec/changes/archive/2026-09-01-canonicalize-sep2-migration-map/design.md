## Context

See `proposal.md` § Why for the motivation. The design-relevant facts:

- The canonical table in `docs/seps/sep-0002.rst` is an RST **grid table** whose
  rows are single physical lines already 200–260 characters wide. Adding a
  fourth column pushes them past 350.
- `tools/check_nomenclature.py` depends only on the standard library and must
  stay that way; it is run by hand and by sibling CI against a clone.
- `tests/test_nomenclature.py:184` asserts only that the checker's canonical
  *targets* appear somewhere in the SEP text, by naive substring search.
- `docs/source/conf.py:122-141` copies `docs/seps/*.rst` into `docs/source/seps/`
  at configuration time, before Sphinx reads the source tree.
- `sdypy-io`, `sdypy-FRF` and `sdypy-excitation` are not cloned locally, so the
  evidenced-divergence inventory is built from `EMA`, `model` and `view` only.

## Goals / Non-Goals

**Goals:**

- One definition of the migration map, in SEP 2, mechanically pinned to the
  checker in both directions.
- A table that stays editable by hand after gaining a column.
- The narrative docs render the table without a second copy of it.

**Non-Goals:**

- Renaming anything in a sibling package. That is Bucket C, unchanged by this.
- Ratifying SEP 2. `:Status:` stays `Draft`; the flip is team-gated work in
  `REQUIREMENTS.md` § Pending B.
- Teaching the checker to disambiguate a bare `xi` by context. It cannot, and
  the spec now records that as a coverage boundary.
- Auditing the three uncloned siblings.

## Decisions

### Convert the canonical table from a grid table to `list-table`

The table gains an "Instead of" column. As a grid table that means editing
350-character lines with hand-aligned `+---+` rules — unmaintainable, and the
source of the drift this change is trying to end. A `.. list-table::` renders
identically, puts each cell on its own line, and can be parsed by the mirror
test with a few lines of stdlib code instead of a grid-cell parser.

*Alternative considered:* keep the grid table and parse it. Rejected — a grid
parser has to handle continuation rows and column-width alignment, which is more
test machinery than the thing it is testing. *Alternative considered:* keep the
grid table and add a separate machine-readable block (YAML/CSV) beside it.
Rejected — that is two definitions again, exactly what the change removes.

### The checker keeps a hand-written dict; the test enforces the mirror

`CANONICAL` stays a literal dict in `check_nomenclature.py`. It is not generated
from the SEP at import time.

The checker must run standalone against a sibling clone, where `docs/seps/` is
not present. Parsing the SEP at import would make the checker depend on the
umbrella's docs tree and turn a docs-formatting slip into a checker crash in
someone else's CI. Keeping the dict literal and pinning it in the umbrella's own
test suite puts the failure where it belongs: on the person editing the SEP or
the checker, in a repo where both files exist.

*Alternative considered:* generate the dict into the checker at build time.
Rejected — introduces a codegen step into a stdlib-only script and leaves a
generated file to review.

### The mirror test compares two sets, both directions

The test parses the `Instead of` cells out of the SEP's `list-table` and
compares set-equality against `CANONICAL`'s keys, reporting each direction
separately so the failure message says which side is stale. The existing
target-side assertion (`test_every_canonical_name_appears_in_sep2`) is kept.

This is what makes the change stick: it is the missing assertion that let
`xi → damping_ratio` in without SEP backing.

### Transclusion by comment markers, not by literalinclude

`docs/source/dev/nomenclature.rst` (next to `dev/pep8.rst`, same contributor
audience) pulls the table in with:

```rst
.. include:: ../seps/sep-0002.rst
   :start-after: .. canonical-table-start
   :end-before: .. canonical-table-end
```

The markers are RST comments, invisible in the rendered SEP. `include` is used
rather than `literalinclude` because the table must render as a table, not as a
code block. The path resolves against the copy `conf.py` already drops in
`docs/source/seps/`, so no new build step is needed.

The transcluded region must contain no explicit hyperlink targets or section
headings, or Sphinx reports duplicate labels when both the SEP page and the
narrative page render it. The region is the table plus its immediate lead-in
sentence only.

### `xi` is removed from the map, not exempted by a special case

`xi` becomes a ratified canonical name for element natural coordinates, so the
checker simply stops carrying it as a divergent spelling. No context-sniffing,
no per-module exemption list. The two evidenced damping spellings that *are*
unambiguous — `nat_xi`, `pole_xi` — take its place.

The cost is stated honestly rather than engineered around: a public parameter
named `xi` that really is a damping ratio will no longer be caught. The spec
records it as a coverage boundary and the sibling suites own it.

### `EI` comes off the `stiffness_matrix` row

SEP 2's `stiffness_matrix` description currently says it replaces `EI`, while
the checker deliberately excludes `EI` with a comment explaining why. The
two-way mirror turns that latent contradiction into a test failure the moment it
is written, so it is resolved here: `EI` is a scalar bending rigidity, it is not
a stiffness matrix, and it leaves the migration map entirely. It stays a
snake_case violation, which the checker already reports without proposing a
canonical name.

## Risks / Trade-offs

- **Converting the table churns the SEP diff** → The conversion is mechanical
  and the rendered output is unchanged; reviewers can check the rendered page
  rather than the diff. Content edits (the new column, the coordinate row, the
  `EI` removal) are separate commits from the format conversion, so the
  conversion diff is verifiable as a no-op.
- **A `list-table` is easier to break than a grid table** (a missing `-` item
  silently shifts a column) → the mirror test parses the same structure, so a
  shifted column fails the suite rather than shipping.
- **Losing `xi` coverage for damping ratios** → accepted and recorded in the
  spec as a coverage boundary; `nat_xi` and `pole_xi` are the spellings actually
  present in EMA today.
- **Transclusion couples the docs build to marker comments in the SEP** →
  deleting a marker breaks the docs build loudly, not silently; `check_docs.py`
  is the place to add a marker-presence assertion if that proves too subtle.
- **The inventory is built from three siblings** → `io`, `FRF` and `excitation`
  are unaudited, so the inventory may be incomplete. The spec requires the
  inventory to be derived from checker output, so cloning and auditing those
  three later extends it without contradicting anything written now.

## Migration Plan

No runtime migration — no shipped code changes. Order of work is format
conversion, then content, then enforcement, so that each step is reviewable:
convert the table, add the column and rows, update the checker, extend the test,
add the docs page, refresh `REQUIREMENTS.md`. Rollback is a revert; nothing is
published by this change.

## Open Questions

- Whether the three uncloned siblings (`io`, `FRF`, `excitation`) should be
  cloned and audited before the inventory is considered complete, or left for a
  follow-up. Deferrable: the spec ties the inventory to checker output, so
  extending it later is an amendment, not a redesign.
