## 1. Convert the canonical table to `list-table`

- [x] 1.1 Rewrite the canonical variable table in `docs/seps/sep-0002.rst` as a `.. list-table::` with the existing three columns and rows, changing no content; verify by building `sphinx-build -b html docs/source docs/_build/html` and confirming the rendered SEP 2 page shows the same rows as before
- [x] 1.2 Confirm the conversion is content-neutral by checking that every canonical name and description string present before the conversion is still present (`python tools/check_seps.py --path .` passes, and `pytest -m "not pypi_artifacts" tests/test_nomenclature.py` still passes unchanged)
- [x] 1.3 Commit the conversion on its own, so the content commits that follow have a small reviewable diff

## 2. Add the migration map to SEP 2

- [x] 2.1 Add the **"Instead of"** column to the `list-table` and populate it from the current `CANONICAL` dict in `tools/check_nomenclature.py`, minus `xi`; verify the rendered table shows the fourth column
- [x] 2.2 Add `nat_xi` and `pole_xi` to the `damping_ratio` row's "Instead of" cell (the evidenced EMA public attributes, per `sdypy-EMA/sdypy/EMA/EMA.py:660` and `pole_picking.py:43`)
- [x] 2.3 Add a canonical table row for element natural (isoparametric) coordinates — `xi`, `eta`, `zeta` — with an empty "Instead of" cell, and a sentence of prose noting these are a finite-element term of art and are not divergent spellings of `damping_ratio`
- [x] 2.4 Remove `EI` from the `stiffness_matrix` row: strike "and the abbreviation ``EI``" from its description and leave `EI` out of its "Instead of" cell; add a prose note that `EI` is a scalar bending rigidity needing a maintainer-chosen descriptive snake_case name
- [x] 2.5 Add a sentence stating that the "Instead of" column is normative and is the single source of truth for the migration map
- [x] 2.6 Verify `:Status:` is still `Draft` and `python tools/check_seps.py --path .` passes

## 3. Mirror the map in the checker

- [x] 3.1 In `tools/check_nomenclature.py`, remove the `"xi": "damping_ratio"` entry and add `"nat_xi": "damping_ratio"` and `"pole_xi": "damping_ratio"`; verify `python tools/check_nomenclature.py --path ../sdypy-model` no longer reports the two `shell.py` `xi` findings
- [x] 3.2 Verify `python tools/check_nomenclature.py --path ../sdypy-EMA` now reports `nat_xi` and `pole_xi` against `damping_ratio`
- [x] 3.3 Reconcile any remaining difference between the dict and SEP 2's "Instead of" column so the two are set-equal
- [x] 3.4 Update the module docstring: record that a bare `xi` is not statically decidable between a damping ratio and an element coordinate, and that this is outside the checker's coverage; keep the existing `EI` note accurate against the SEP change in 2.4
- [x] 3.5 Verify `python tools/check_nomenclature.py --path ../sdypy-view` still exits `0`

## 4. Pin the mirror in both directions

- [x] 4.1 Add a helper to `tests/test_nomenclature.py` that parses the "Instead of" cells out of the `list-table` in `docs/seps/sep-0002.rst`; verify it returns a non-empty set on the real SEP
- [x] 4.2 Add `test_every_enforced_spelling_appears_in_sep2` — every key of `CANONICAL` appears in the parsed column — and verify it fails when a bogus key is temporarily added to the dict
- [x] 4.3 Add `test_every_sep2_spelling_is_enforced` — every parsed column entry is a key of `CANONICAL` — and verify it fails when a row is temporarily added to the SEP
- [x] 4.4 Keep `test_every_canonical_name_appears_in_sep2` (the target-side pin) passing
- [x] 4.5 Verify the whole suite with `pytest -m "not pypi_artifacts"` in an environment with no first-level package installed

## 5. Surface the table in the narrative docs

- [x] 5.1 Add `.. canonical-table-start` / `.. canonical-table-end` comment markers around the table region in `docs/seps/sep-0002.rst`, with no hyperlink targets or headings inside the region; verify the markers do not appear in the rendered SEP page
- [x] 5.2 Create `docs/source/dev/nomenclature.rst` that explains how to use the table, transcludes the region with `.. include:: ../seps/sep-0002.rst` plus `:start-after:`/`:end-before:`, and links to the rendered SEP 2 for governance, deprecation policy and status
- [x] 5.3 Add `dev/nomenclature` to the Development toctree in `docs/source/index.rst`
- [x] 5.4 Build the docs and verify the table renders on the new page with the "Instead of" column, that the page carries no copy of the SEP's header or policy sections, and that Sphinx emits no duplicate-label or missing-include warning
- [x] 5.5 Verify `python tools/check_docs.py --path .` passes

## 6. Refresh the requirements roster

- [x] 6.1 In `REQUIREMENTS.md` Bucket C, drop EMA `xi → damping_ratio` and model `frequency → freq`; verify neither spelling is reported by the checker against any sibling clone
- [x] 6.2 Add the EMA work the checker reports but the roster omits: `frf_type → frf_form`, `pole_ind → pole_idx`, and `nat_xi`/`pole_xi → damping_ratio`
- [x] 6.3 Add the model work the roster omits: the `Shell` class (`E`, `nu`, `rho`, `K`, `M`), `Tetrahedron`'s `Density`/`Poisson`/`ro`, the bare `I`/`A`/`J` parameters, and `derivative_E_ind`/`derivative_ro_ind`/`eig_ind → _idx`
- [x] 6.4 Correct the `EI` entry to say a maintainer-chosen descriptive name, not `stiffness_matrix`, matching 2.4
- [x] 6.5 Note in Bucket C that `sdypy-io`, `sdypy-FRF` and `sdypy-excitation` are unaudited because no local clone exists, so the inventory is known-incomplete
- [x] 6.6 Update the `public-api` verification rows in `REQUIREMENTS.md` for the new two-way mirror tests and the new documentation requirement

## 7. Validate and hand off for review

- [x] 7.1 Run `openspec validate canonicalize-sep2-migration-map --strict` and confirm it passes
- [x] 7.2 Run the full local gate `pytest` and report which `pypi_artifacts` tests fail and why (they are expected red until Bucket A lands)
- [x] 7.3 Re-run all three sibling audits and record the new finding counts against the pre-change baseline (view 0, EMA 26, model 70) — done, and extended to the *installed* packages after the clone was found stale: view 0, EMA 28, model 84
- [x] 7.4 Review round closed in the 2026-09-01 meeting with Janko and Klemen. The PR intended in `ladisk/sdypy` was never opened — the change reached `main` by direct push through a miscommunication — so the review was held in the meeting instead: the ISO 7626 relation was accepted, and the `frf_form` migration and the handling of future nomenclature proposals were agreed as follow-on work
