## Why

`tools/check_nomenclature.py` enforces a migration map — divergent spelling →
canonical name — that SEP 2 never ratified. SEP 2's table lists only the
canonical targets; the left-hand side lives solely in the checker's `CANONICAL`
dict, and `tests/test_nomenclature.py::test_every_canonical_name_appears_in_sep2`
pins only the targets. Nothing stops the checker from inventing a rename.

It already has. The blanket entry `xi → damping_ratio` makes the checker report
`shape_functions(xi, eta)` in `sdypy-model/sdypy/model/shell/shell.py:78`, where
`xi`/`eta` are isoparametric element coordinates and the standard term of art in
finite-element work. Obeying the checker there would corrupt the code. Meanwhile
EMA's actual public damping attributes, `nat_xi` and `pole_xi`, are absent from
both the table and the checker, so genuine divergence passes silently.

The 2026-08-26 meeting resolved that SEP 2 is the source of truth for the
migration map, so the map belongs in the SEP with the checker mirroring it — not
the other way round.

## What Changes

- SEP 2's canonical variable table gains an **"Instead of"** column naming the
  divergent spellings each canonical name replaces. The column is normative:
  SEP 2 becomes the source of truth for the migration map.
- SEP 2 gains a canonical entry for **element natural (isoparametric)
  coordinates** — `xi`, `eta`, `zeta`. These are ratified names, not divergences.
- The blanket `xi → damping_ratio` mapping is **removed**. Only damping-context
  spellings map to `damping_ratio`; `nat_xi` and `pole_xi` are added as the
  evidenced EMA divergences.
- `tools/check_nomenclature.py`'s `CANONICAL` dict becomes a pure mirror of the
  "Instead of" column, with no entry the SEP does not carry.
- `tests/test_nomenclature.py` pins **both** directions of the mirror: every
  divergent spelling the checker enforces must appear in SEP 2's "Instead of"
  column, and every column entry must be enforced by the checker.
- The narrative docs surface the SEP 2 canonical table by transclusion —
  `.. include::` of a marker-delimited region of `sep-0002.rst` — so the table
  has one definition and readers do not have to open the whole SEP.
- `REQUIREMENTS.md` Bucket C is refreshed against checker output: the stale
  entries (EMA `xi → damping_ratio`, model `frequency → freq` — neither name
  exists in the code) are dropped, and the unlisted work is added (EMA
  `frf_type`, `pole_ind`; model's `Shell` class, `Density`/`Poisson`/`ro`,
  `I`/`A`/`J`, `derivative_E_ind`/`derivative_ro_ind`/`eig_ind`).

Not breaking: no sibling public API changes here. This change corrects the
contract and its enforcement; the sibling renames stay Bucket C work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: the migration map becomes SEP 2 content rather than checker
  content; `xi` is scoped out of the damping-ratio rule and ratified as an
  element coordinate; the evidenced-divergence inventory is corrected; the
  checker gains a two-way mirror obligation against SEP 2.
- `documentation`: the SEP 2 canonical table is rendered in the narrative docs
  by transclusion from a single definition.

## Impact

- `docs/seps/sep-0002.rst` — new table column, new coordinate entry, marker
  comments delimiting the table region. `:Status:` stays `Draft`; ratification
  remains the separate team-gated act tracked in `REQUIREMENTS.md` § Pending B.
- `tools/check_nomenclature.py` — `CANONICAL` dict rewritten as a SEP mirror;
  module docstring updated where it explains the `xi` and `EI` decisions.
- `tests/test_nomenclature.py` — the mirror test extended to both directions.
- `docs/source/` — a narrative nomenclature page plus its toctree entry.
- `REQUIREMENTS.md` — Bucket C refresh; `public-api` verification rows.
- No change to `sdypy/__init__.py` or any sibling package. Re-running the
  checker after this change is expected to drop the three `shell.py` `xi`
  findings and add `nat_xi`/`pole_xi` findings against `sdypy-EMA`.
