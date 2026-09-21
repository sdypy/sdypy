## Why

SEP 2 canonises eleven names. The six first-level packages use far more domain vocabulary than that, and where the SEP is silent they have each invented their own. An AST inventory of the installed siblings shows the result:

| Quantity | What the code says today | SEP 2 table |
|---|---|---|
| Mode shape | `phi`, `phi_X`, `phi_A`, `mode` (EMA); `mode_shape` (view) | — |
| Damping ratio | `xi`, `xi_temp` (EMA); `complex_freq_to_freq_and_damp` | — |
| Stiffness / mass matrix | `solve_eigenvalue(K, M, …)`, `matrices_k_e`, `EI` (model) | — |
| Mesh | `nodes`, `elements` (model, view) vs `org`, `conec` (`Beam`) | — |
| Mode count | `n_modes` (model) vs `n` (`Beam.solve`) | — |
| Natural frequency | `nat_freq` — a **public attribute** of `EMA.Model`, `model.Beam`, `model.Tetrahedron` | `natural_freq` |
| Frequency band | `lower`, `upper`, `f_lower`, `f_upper`, `lower_ind`, `upper_ind` (EMA) | `freq_lower`, `freq_upper` |
| Frequency | `freq` (EMA) vs `frequency` (model) | `freq` |
| Index suffix | `elem_idx`, `node_idx` (model) vs `FRF_ind`, `lower_ind` (EMA) | — |

Two things are wrong here, and only one of them is "the table is too short".

The second is that **SEP 2's word-order rule is already contradicted by SEP 2's own table**. The rule says the broader term goes first, which yields `freq_lower`, `freq_upper`, `freq_rad`, `damping_viscous`. But `natural_freq` puts the broader term last, and `frf_form` names a *form* while leading with `frf`. So the rule is not, and has never been, a rule — it is a heuristic that yields to established domain usage, and the table is what actually binds. Extending the table without saying so would make the contradiction worse: `mass_matrix` (established usage) sits beside `freq_lower` (heuristic) and a reader has no way to tell which pattern to follow for the next name.

The timing is deliberate. `REQUIREMENTS.md` § Pending B queues SEP 2's `Draft → Accepted` flip, and `natural_freq` is about to be ratified as canonical while three packages ship `nat_freq` and nothing in CI notices. Ratifying a table that the code contradicts and a rule that the table contradicts would freeze both defects into an Accepted governance document.

## What Changes

- **Demote the word-order guideline to an explicit heuristic** and state the precedence that already operates in practice: the canonical table is normative; the heuristic applies only when coining a *new* compound name the table does not cover; and it yields to an established domain term. This is the change that makes `freq_lower` and `mass_matrix` coexist without one of them being a violation.
- **Extend the canonical table** with the four evidenced groups:
  - *Modal quantities*: `mode_shape`, `damping_ratio`, `n_modes`. `natural_freq` and `poles` stay as they are.
  - *System matrices*: `mass_matrix`, `stiffness_matrix`, `damping_matrix` — replacing the single-uppercase-letter parameters `K`, `M` (and `EI`), which violate the existing snake_case-for-parameters rule that SEP 2 already states.
  - *Mesh and geometry*: `nodes`, `elements`, `n_nodes`, `n_elements` — codifying what `model` and `view` already agree on, against which `Beam`'s `org` / `conec` are the outlier.
  - *Counts and indices*: the affix conventions `n_<plural>` for a count and `<name>_idx` for an index, chosen because `model` already uses `n_nodes`, `n_frames`, `elem_idx`, `node_idx`; EMA's `_ind` spelling is the divergence.
- **Add one narrow, named exception**: the arguments of the criterion functions `MAC`, `MSF`, `MCF` keep the modal-literature symbols `phi_X` (experimental) and `phi_A` (analytical). These functions are already SEP 2's uppercase-acronym exception; the exception is now written down for their arguments too, rather than being tolerated silently.
- **Record the rename obligations** for the evidenced divergences as an org-wide requirement: each divergent name is renamed to the canonical one and the old name kept as a `DeprecationWarning`-emitting alias through v1.x, per SEP 2's existing deprecation policy. **This change performs none of those renames** — they live in the sibling repositories and are verified by their suites. It writes the contract; the siblings satisfy it when they next touch those signatures.
- **Not in scope**: mechanical enforcement. A checker that measures conformance to this table, and its CI wiring, is a separate change (`enforce-sep2-nomenclature`) that depends on this one — a checker cannot be written against a table that is still being decided.
- **Not in scope**: the `:Status: Draft → Accepted` flip. It stays team-gated in `REQUIREMENTS.md` § Pending B; this change makes the document worth ratifying, it does not ratify it.

## Capabilities

### New Capabilities
<!-- none. `public-api` already owns SEP 2's naming conventions (§ *Public naming conventions for sdypy-org first-level packages*) and SEP 2's document content (§ *SEP 2 contains the amended naming rules*). Adding a second capability for "nomenclature" would split one contract across two homes. -->

### Modified Capabilities
- `public-api`: gains the canonical-name requirements for modal quantities, system matrices, and mesh geometry; the count/index affix conventions; the precedence of the canonical table over the word-order heuristic; the SEP 2 document-content requirement for the extended table; and the rename obligations for the evidenced divergences.

## Impact

- **Core repo**: `docs/seps/sep-0002.rst` — an extended canonical table and a rewritten word-order paragraph; `openspec/specs/public-api/spec.md` — seven new requirements at archive time; a `public-api` row block in `REQUIREMENTS.md`. No shipped code, no packaging change.
- **Core test suite (downstream consumer, not changed here)**: `tests/test_interop.py` reads `model.nat_freq` and `ema.nat_freq` in six places. When the siblings ship `natural_freq`, this suite must move to the canonical name; until then the deprecated alias keeps it working. This is the one place where a sibling rename obligation reaches back into the umbrella repository.
- **Sibling repos** (the org-wide part, **not done here**): `sdypy-EMA` (`nat_freq`, `xi`, `phi`, `lower`/`upper`/`f_lower`/`f_upper`, `FRF_ind`/`lower_ind`/`upper_ind`), `sdypy-model` (`K`/`M`/`EI`, `org`/`conec`, `nat_freq`, `frequency`, `n`), `sdypy-view` (already conformant on `nodes`/`elements`/`mode_shape`/`n_frames`; nothing to do).
- **Users**: no break. Every rename obligation carries a deprecated alias through all of v1.x, and positional callers are unaffected by keyword renames — the policy SEP 2 already sets and the previous round already implemented for `autoMAC` / `frf_type` / `E` / `nu` / `rho`.
- **Interaction with `REQUIREMENTS.md` § Pending A**: the queued sibling releases (EMA 0.30.0, model 0.2.0, …) are *not* blocked by this change. The obligations here are satisfiable in a later release; batching them into the pending round is a maintainer's call, not a precondition.
- **Interaction with SEP 2 ratification (§ Pending B)**: this change is a prerequisite in substance though not in process — ratifying the current text would freeze a table the code contradicts.
- **Unchanged / out of scope**: the eleven existing table entries except `natural_freq`, which keeps its spelling and instead gains a rename obligation on the three packages that ship `nat_freq`; the curated `__all__` lists; the acronym-casing, constant, and framework-exemption rules; the deprecation policy itself; SEP 1, 3, 4 and 5.
