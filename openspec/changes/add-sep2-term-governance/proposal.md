## Why

SEP 2 lists settled names and a word-order heuristic for coining new ones. It
does not say how a name for a quantity the table does not cover gets chosen,
reviewed, or recorded. In practice the name is decided inside a package and SEP 2
learns about it later or not at all — which is how `frf_type` came to mean the
FRF ratio in `sdypy-EMA` and the FRF estimator in `sdypy-FRF` at the same time,
with disjoint value vocabularies, on the flagship interop path.

SEP 2 also has no external terminology anchor: it never mentions ISO 7626. An
audit against the standard (issue #2) found the two agree everywhere they
overlap except one deliberate divergence, `'receptance'` for ISO's *dynamic
compliance*. That has to be on the record before ISO can be cited as a source
for new names.

The 2026-09-01 meeting resolved that a new term follows the general guidelines
*and* the ISO terminology, and that an unclear case goes to a discussion rather
than being settled silently.

## What Changes

- SEP 2 gains two short subsections: **"Relation to ISO 7626"** and
  **"Proposing a new term"**. The SEP states the rule and stays short.
- The rule places responsibility on the **pull-request author**: they declare
  the new public names their PR introduces, and the reviewer assesses them
  against the guidelines and ISO 7626. No tool detects an undeclared name.
- The discussion happens **in that pull request**. A separate SEP amendment PR
  is never required before it can merge.
- Declared names collect on a **`SEP 2 pending terms` issue** — opened when the
  first name since the last amendment is declared, closed by the amendment PR —
  and reach the canonical table through a **manually triggered amendment PR**,
  with a reminder at release time. Recording never gates a feature.
- The operational detail — how to run the checker, what it does and does not
  decide, and the ordered steps for adding a table row — goes to
  `docs/source/dev/nomenclature.rst`, not into the SEP.
- `.claude/` gains a thin command that *executes* the documented process and
  links to it rather than restating it, so the process survives without it.

## Capabilities

### Modified Capabilities

- `public-api`: SEP 2 gains an external terminology reference and a defined path
  from a proposed name to a canonical table entry.

## Out of scope

- **Propagation to the sibling namespace packages.** How rules defined here
  reach the other packages is being solved centrally; this change stays inside
  `sdypy`.
- **PR and issue templates.** None exist in any repo today. The declaration line
  belongs in a PR template, but creating one touches the
  `sibling-package-template` capability and all six siblings, so it is recorded
  in `REQUIREMENTS.md` § Pending instead of built here.
- **Running `check_nomenclature.py` automatically.** It is invoked by hand
  against a clone today; nothing schedules it. Unchanged by this change.

## Impact

- `docs/seps/sep-0002.rst` — two short subsections plus ISO 7626 in the
  references. `:Status:` stays `Draft`; ratification remains team-gated in
  `REQUIREMENTS.md` § Pending B.
- `docs/source/dev/nomenclature.rst` — the worked procedure.
- `AGENTS.md` — one router line pointing at the procedure.
- `REQUIREMENTS.md` — new `public-api` rows, plus a § Pending entry for the PR
  template work.
- `.claude/commands/` — the amendment-drafting command.
- No canonical name changes and no sibling code changes. The `frf_form`
  migration this enables is separate work.
