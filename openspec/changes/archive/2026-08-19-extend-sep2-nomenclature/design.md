## Context

See proposal.md § Why for the motivation and the evidence table. Three constraints shape the design.

**The evidence is an AST inventory, not a guess.** Every divergence named in the specs was read out of the installed sibling sources (`sdypy-EMA` 0.29.1, `sdypy-io` 0.4.0, `sdypy-FRF` 0.1.0, `sdypy-excitation` 0.1.1, `sdypy-view` 0.1.6, `sdypy-model` 0.1.5) by parsing public function, method and class signatures without importing them. That matters for `natural_freq`: the inventory is what showed that the canonical name appears nowhere and `nat_freq` is a *public attribute* on three classes — a fact that changes the cost of the decision from "documentation" to "rename with aliases".

**SEP 2 is on the ratification path.** `REQUIREMENTS.md` § Pending B queues the `Draft → Accepted` flip. Anything this change gets wrong becomes much more expensive to correct afterwards, and anything it leaves wrong gets frozen.

**The previous round set the precedent.** `standardize-public-api` (archived 2026-07-01) already amended SEP 2, already added a rename inventory with `DeprecationWarning` aliases (`autoMAC`, `frf_type`, `E`/`nu`/`rho`, `Young`/`Density`/`Poisson`), and already left the actual sibling releases to `REQUIREMENTS.md` § Pending A. This change follows that shape rather than inventing a new one.

## Goals / Non-Goals

**Goals**
- Make SEP 2 internally consistent: no rule the table contradicts, no table entry the code contradicts without a recorded obligation to fix it.
- Canonise names on evidence of actual divergence, not on completeness for its own sake.
- Leave SEP 2 in a state worth ratifying.

**Non-Goals**
- Writing the conformance checker. It is `enforce-sep2-nomenclature`, and it must come second: a checker encodes the table, so the table has to stop moving first.
- Performing the renames. They live in six other repositories.
- Canonising every domain term someone might want. A name enters the table because two packages disagree about it today, or because one package uses a spelling that violates a rule SEP 2 already states.
- Flipping `:Status:`.

## Decisions

**D1 — Demote the word-order guideline to a heuristic, and say the table wins.** This is the load-bearing decision; without it the extended table is incoherent. The alternative was to enforce the guideline strictly and rename the offenders (`natural_freq` → `freq_natural`, `frf_form` → `form_frf`, and `matrix_mass` instead of `mass_matrix`). Rejected: it renames two names that are already canonical and one that is already ratified vocabulary in the previous round, and it produces `matrix_mass` and `form_frf`, which no practitioner writes. The guideline's own text already hedges ("it is up to the user to determine what is the more broader term"), so this decision formalises the reading the project has been using rather than changing it. Note what this costs: `freq_lower` and `mass_matrix` now follow *different* patterns, and the only way to know which applies to a given quantity is to look it up. That is precisely why the resolution is "the table is normative" — the table is the lookup.

**D2 — `mass_matrix`, not `matrix_mass`.** Follows from D1 plus the observation that "mass matrix" is a term of art in every structural-dynamics text, whereas "lower frequency" is a description rather than a name. *Alternative considered*: `matrix_mass` / `matrix_stiffness` / `matrix_damping`, which sort together in autocomplete and obey the heuristic — rejected on readability and on the term-of-art rule. *Alternative considered*: keep `K`, `M`, `C` as a literature exception alongside `MAC` / `MSF` / `MCF` — rejected: those are *function names*, where the acronym is the identity of the thing; `K` and `M` are *parameters*, which SEP 2 already binds to snake_case, so the exception would have to override an existing rule rather than fill a gap.

**D3 — `natural_freq` stays canonical; `nat_freq` gets a rename obligation.** The cheap option was to codify `nat_freq`, since three packages already agree on it and nothing would need renaming. Rejected on the descriptive-names rule that opens SEP 2: `nat` is an abbreviation that saves four characters and costs clarity, and SEP 2's tolerated abbreviations (`fs`, `dt`, `frf`) are tolerated because they are near-universal in the wider ecosystem, which `nat_freq` is not. This is the one decision that pushes the change beyond "documentation only": it obliges a public-attribute rename in `sdypy-EMA` and `sdypy-model`. The obligation is stated in the spec and executed in the siblings — see D6.

**D4 — `phi_X` / `phi_A` survive as a named exception, scoped to three functions.** `MAC(phi_X, phi_A)` is written that way in the modal-analysis literature, and the criterion functions are already SEP 2's uppercase-acronym exception, so the exception is extended to their arguments rather than invented. It is deliberately written as "these three functions' arguments only", with a scenario asserting that `phi` elsewhere *is* a violation — an unbounded "literature symbols are fine" exception would swallow the `mode_shape` requirement whole.

**D5 — `_idx` over `_ind`.** Both are in the tree; `model` uses `_idx` (`node_idx`, `elem_idx`), EMA uses `_ind` (`FRF_ind`, `lower_ind`, `upper_ind`). `_idx` is the more common spelling in the scientific Python ecosystem, so the tie is broken outward rather than by counting occurrences. The paired `n_<plural>` convention is not a tie at all — `model` and `view` already use `n_nodes`, `n_frames`, `n_modes` consistently, and only `Beam.solve(n)` diverges.

**D6 — State the rename obligations as an org-wide requirement; perform none of them.** The specs bind all six siblings; the work happens in their repositories and is verified by their suites, exactly as the existing org-wide `public-api` requirements are. This keeps the change reviewable in one repo and keeps it off the critical path of the § Pending A releases. The trade-off is real: a requirement with no local test is a requirement that can sit unmet for a long time, which is why `enforce-sep2-nomenclature` follows immediately and why the obligations are enumerated by name rather than left as "packages SHALL conform".

**D7 — Extend `public-api`; do not create a `nomenclature` capability.** `public-api` already owns SEP 2's naming conventions and SEP 2's document content. A separate capability would put two halves of one SEP in two homes and force every future reader to check both.

## Risks / Trade-offs

- [The rename obligations pile onto the already-pending sibling release round (§ Pending A), and neither ships] → the obligations are written to be satisfiable independently and in any order; nothing here blocks the pending releases, and none of the pending releases is invalidated by a later rename. If the maintainer chooses to batch them, that is an optimisation, not a requirement.
- [Some scenarios cannot be checked statically — "an established term of art", "the value is identical to the canonical attribute"] → they are contract text for humans and for the sibling suites, not checker input. `enforce-sep2-nomenclature` will implement the mechanically decidable subset (parameter names against the table, `_ind` usage, single-uppercase parameters) and must say plainly which requirements it does *not* cover, so the gap is visible instead of assumed closed.
- [`nat_freq` → `natural_freq` breaks user code that does `model.nat_freq`] → attribute-level deprecation needs a `__getattr__` shim on the class rather than a simple assignment, which is slightly more work than the keyword-argument shims of the previous round. It is a known pattern and the alias requirement makes it mandatory; the risk is that a sibling implements the rename *without* the shim, which the sibling's own suite must catch.
- [The table grows into a dumping ground for every domain term] → the entry bar is stated in Non-Goals and enforced by the evidence table in the proposal: a name enters because packages disagree today, not because it might be useful.

## Migration Plan

Core repo: docs and specs only, so nothing to deploy; revert is `git revert`. Siblings: each rename is an additive minor release — canonical name added, divergent name kept as a warning-emitting alias — so no coordinated release is needed and any order works. Removal of the aliases is gated at v2.0 by the existing deprecation policy and is out of scope here.

## Open Questions

None. The four contested decisions (matrix word order, `nat_freq` vs `natural_freq`, the `phi_X` / `phi_A` exception, `_idx` vs `_ind`) were put to the project lead and answered before the specs were written; they are recorded as D1–D5 above rather than deferred.
