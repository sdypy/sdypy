## 1. Amend the word-order rule in SEP 2

- [x] 1.1 In `docs/seps/sep-0002.rst` § *General guidelines*, rewrite the second bullet (the
      broader-term-first rule). Keep the rule and its `freq_upper` / `damping_viscous` examples,
      but state explicitly: it is a heuristic for coining names the canonical table does not
      cover; where the table has an entry, the table is normative; and the heuristic yields to
      an established term of art, which is then added to the table. Name the two existing
      entries that follow the other pattern — `natural_freq` and `frf_form` — so the reader
      sees that the precedence is describing the table as it is, not excusing an exception.
- [x] 1.2 Do NOT delete the sentence "it is up to the user to determine what is the more
      broader term" — it is the hedge this precedence formalises; keep it and point at the table
      as the resolution.

## 2. Extend the canonical variable table

- [x] 2.1 Add the modal rows: `mode_shape` (unit —, "Mode shape vector or matrix; see the
      criterion-function exception below"), `damping_ratio` (unit —, "Viscous damping ratio"),
      `n_modes` (unit —, "Number of modes"). Leave the existing `natural_freq` row untouched.
- [x] 2.2 Add the system-matrix rows: `mass_matrix`, `stiffness_matrix`, `damping_matrix`
      (unit — / kg / N/m as appropriate, description noting these replace the single-letter
      `K`, `M`, `C` in public signatures and that local variables inside a routine are unaffected).
- [x] 2.3 Add the mesh rows: `nodes` ("Node coordinate array") and `elements`
      ("Element connectivity array").
- [x] 2.4 Keep the RST grid table well-formed — the existing table uses full-width `+---+` rulers
      and the column widths must be extended consistently, or Sphinx fails the docs build.
      Gate: `python -m sphinx -b html docs/source docs/_build/html` succeeds.

## 3. Add the new prose rules to SEP 2

- [x] 3.1 In § *Naming of public objects*, add the affix conventions: a count is `n_<plural>`
      (`n_modes`, `n_nodes`, `n_elements`, `n_frames`); an index is `<name>_idx` (`node_idx`,
      `elem_idx`); `_ind` is not used, and a bare `n` is not a count in a public signature.
- [x] 3.2 In the same section, extend the criterion-function exception: `MAC`, `MSF`, `MCF` keep
      the bare uppercase acronym as a *name* (already stated) **and** keep the modal-literature
      symbols `phi_X` (experimental) and `phi_A` (analytical) as their *arguments*. State the
      bound explicitly: the exception covers those three functions only; `phi` as a parameter
      name anywhere else is a violation of the canonical `mode_shape`.
- [x] 3.3 Verify the amendment is additive: the PEP 8 reference, the word-order examples, all
      eleven pre-existing table entries, § *Public API surface* and § *Deprecation policy* are
      all still present.
- [x] 3.4 Do NOT touch `:Status: Draft`. The flip to `Accepted` with a `:Resolution:` is a
      team-gated act tracked in `REQUIREMENTS.md` § Pending B, and `tools/check_seps.py` will
      fail the docs build if a flip omits `:Resolution:`.

## 4. Land the spec deltas

- [x] 4.1 `openspec validate extend-sep2-nomenclature --strict` passes.
- [x] 4.2 `openspec archive extend-sep2-nomenclature` folds the seven new requirements into
      `openspec/specs/public-api/spec.md`. Verify the pre-existing requirements of that
      capability are byte-identical afterwards — this change is purely additive at the spec level.
- [x] 4.3 Update the `public-api` section of `REQUIREMENTS.md` with rows for the new
      requirements. Mark the org-wide rename obligations `sibling repos' suites` in the
      "Verified by" column, and the two SEP-document rows `manual` (docs) until
      `enforce-sep2-nomenclature` lands its checker — then they become `check_nomenclature.py`.
      Do not restate the requirement text; the row links to the spec, per the index-not-source rule.

## 5. Record the sibling obligations (no code changes here)

- [x] 5.1 Add the rename inventory to `REQUIREMENTS.md` § Pending as a new bucket (alongside
      A. releases and B. SEP ratification): `nat_freq` → `natural_freq` (EMA `Model`, model
      `Beam`, model `Tetrahedron` — public attributes, so each needs a class-level `__getattr__`
      shim, not a plain assignment); `xi` → `damping_ratio` and `phi` → `mode_shape` (EMA,
      excluding `MAC`/`MSF`/`MCF`); `lower`/`upper`/`f_lower`/`f_upper` → `freq_lower`/`freq_upper`
      (EMA); `frequency` → `freq` (model); `K`/`M`/`EI` → `stiffness_matrix`/`mass_matrix`
      (model); `org`/`conec` → `nodes`/`elements` (model `Beam`); `n` → `n_modes`
      (model `Beam.solve`); `FRF_ind`/`lower_ind`/`upper_ind` → `_idx` spellings (EMA).
- [x] 5.2 State in that bucket that every rename carries a `DeprecationWarning` alias through
      v1.x and that positional callers must be unaffected, and note that `sdypy-view` is already
      conformant (`nodes`, `elements`, `mode_shape`, `n_frames`) so it needs no release.
- [x] 5.3 Note in that bucket that `tests/test_interop.py` in THIS repository reads
      `model.nat_freq` and `ema.nat_freq` in six places, so the EMA/model rename has a
      downstream step here: move the interop suite to `natural_freq` once the siblings ship it.
      The deprecated alias keeps the suite green in the meantime, so this is not a blocker.
- [x] 5.4 Gate: `git diff --stat` for this change touches only `docs/seps/sep-0002.rst`,
      `openspec/` and `REQUIREMENTS.md`. Any change under `sdypy/`, `tests/`, `tools/` or
      `.github/` means the change has overstepped — the renames belong to the sibling repos and
      the checker belongs to `enforce-sep2-nomenclature`.

## 6. Verify

- [x] 6.1 `python tools/check_seps.py --path .` passes — the amendment must not break SEP 2's
      header metadata.
- [x] 6.2 `python tools/build_index.py` in `docs/seps/` regenerates the index without error, and
      SEP 2 still appears in the Draft section.
- [x] 6.3 `pytest -m "not pypi_artifacts"` is no worse than the pre-change baseline. (Requires a
      Qt binding — `pip install PySide6-Essentials` — or the `view`/`model` imports fail for
      reasons unrelated to this change.)
- [x] 6.4 `openspec list` shows `extend-sep2-nomenclature` archived and `enforce-sep2-nomenclature`
      still open, in that order — the checker change depends on this table being final.
