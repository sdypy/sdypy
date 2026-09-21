# SDyPy — Requirements (single source of truth)

This file is the top-level, human- and agent-readable roster of the SDyPy core
umbrella's **functional, measurable requirements**. It exists so that both
reviewers and AI agents can see, in one place, *what the package must do* and
*how each requirement is verified*.

It is an **index, not a second copy** of the contracts. The full normative text
of every requirement lives in the canonical capability specs under
`openspec/specs/<capability>/spec.md`; each row below links to that spec and to
the automated check that measures it. When a requirement changes, change it in
the spec (via an OpenSpec change) — then update the corresponding row here.

**Legend — "Verified by"**
- `pytest::<name>` — a test in `tests/` (run `pytest -m "not pypi_artifacts"` in
  CI; `pytest` locally to include the PyPI-artifact gate).
- `tools/check_*.py` — a repo-layer conformance checker. Those that can run at
  the umbrella root (`check_seps.py`, `check_docs.py`) run in `docs.yml`; the
  others audit a **sibling clone** and cannot run here — see § Canonical sources.
- `manual` — a human/governance act with no automated gate (tracked in
  [§ Pending requirements](#pending-requirements)).

---

## Canonical sources

| Source | What it governs |
|---|---|
| `openspec/specs/*/spec.md` | Normative requirements (8 capabilities, below) |
| `docs/seps/sep-000*.rst` | SEP governance (SEP 1 levels, 2 API, 3 namespace, 5 sep005) |
| `tools/check_seps.py` | Executable `sep-governance` (SEP metadata) conformance — **runs in `docs.yml`** |
| `tools/check_docs.py` | Executable `documentation` conformance — **runs in `docs.yml`** |
| `tools/check_public_api.py` | Executable `public-api` (`__all__`) conformance — **audits a sibling clone**, `--path ../sdypy-EMA` |
| `tools/check_nomenclature.py` | Executable SEP 2 nomenclature conformance — **audits a sibling clone**; its own logic is covered by `tests/test_nomenclature.py` in CI |
| `tools/check_sibling_template.py` | Executable `sibling-package-template` conformance — **audits a sibling clone** |
| `tests/` | Functional + interop + conformance test suite |

The three clone-auditing checkers cannot run against this repository: each
resolves exactly one portion under `sdypy/`, and the umbrella provides none (it
ships the facade plus the `sdypy/core` and `sdypy/testing` stubs). They are run
by hand against a sibling checkout, or by that sibling's own CI.

---

## Current requirements

**Scope** — each capability is either **umbrella-local** (governs the `sdypy`
umbrella's own code) or **org-wide** (binds all six first-level sibling
packages). Mixed capabilities tag the exception rows inline. The scope also
appears at the top of each `openspec/specs/<capability>/spec.md`.

### namespace-packaging
Spec: `openspec/specs/namespace-packaging/spec.md` (SEP 3) · Scope: **umbrella-local** (except the native-portions row → **org-wide**)

| Requirement | Verified by |
|---|---|
| Umbrella exposes first-level sub-packages by attribute access | `pytest::test_attribute_access_resolves_subpackage`, `test_from_import_style`, `test_submodule_import_style` |
| Importing the umbrella is lightweight (no heavy backends on bare import) | `pytest::test_bare_import_does_not_pull_heavy_backends` |
| Version is sourced from installed metadata | `pytest::test_version_is_non_empty_string` |
| Sub-packages are native PEP 420 portions (no sibling ships `sdypy/__init__.py`) **(org-wide)** | `pytest::test_sibling_ships_no_namespace_init`, `test_published_wheel_ships_only_own_portion` (`pypi_artifacts`) |

### public-api
Spec: `openspec/specs/public-api/spec.md` (SEP 2) · Checker: `tools/check_public_api.py` · Scope: **org-wide** (except the umbrella `__all__` row → umbrella-local)

| Requirement | Verified by |
|---|---|
| Every first-level package declares a non-empty `__all__` | `pytest::test_subpackage_declares_nonempty_all`; `check_public_api.py` |
| Every `__all__` entry resolves | `pytest::test_every_all_entry_resolves` |
| No leaked third-party/stdlib names in curated surfaces | `pytest::test_no_banned_leak_names_in_all` |
| Module-type entries in `__all__` only where sanctioned | `pytest::test_module_entries_only_where_sanctioned` |
| Curated surface matches the SEP 2 table | `pytest::test_curated_surface_matches_spec` |
| Umbrella `__all__` = the six names (+ `sep005` alias) **(umbrella-local)** | `pytest::test_umbrella_all_is_the_six_subpackages_plus_sep005` |
| Renamed names keep deprecated aliases through v1.x | `pytest::test_shim_drift_check_is_advisory` (advisory) |
| Canonical table wins over the word-order heuristic | `manual` (SEP 2 prose) — checker planned, see `enforce-sep2-nomenclature` |
| Canonical names for modal quantities (`mode_shape`, `damping_ratio`, `n_modes`) | sibling repos' suites; checker planned |
| Canonical names for system matrices (`mass_matrix`, `stiffness_matrix`, `damping_matrix`) | sibling repos' suites; checker planned |
| Canonical names for mesh geometry (`nodes`, `elements`) | sibling repos' suites; checker planned |
| Counts are `n_<plural>`, indices are `<name>_idx` | sibling repos' suites; checker planned |
| SEP 2 declares the extended table + precedence rule | `manual` (docs) — verified by review of `docs/seps/sep-0002.rst` |
| SEP 2 declares the divergent spellings each canonical name replaces ("Instead of" column) | `pytest::test_sep2_instead_of_column_parses`; the two-way mirror tests below |
| Canonical names for element natural coordinates (`xi`, `eta`, `zeta`) | `pytest::test_bare_xi_is_not_enforced_as_a_damping_spelling`, `test_element_coordinates_are_not_reported` |
| `EI` is not a divergent spelling of `stiffness_matrix` | `pytest::test_ei_is_reported_without_a_canonical_name` |
| The checker mirrors SEP 2 in **both** directions | `pytest::test_every_enforced_spelling_appears_in_sep2`, `test_every_sep2_spelling_is_enforced` |
| Evidenced divergences carry deprecated aliases (Bucket C) | sibling repos' suites — see [§ Pending](#c-align-sibling-nomenclature-with-sep-2-org-wide) |
| Nomenclature conformance is mechanically enforced | `tools/check_nomenclature.py`; `pytest::test_conforming_clone_passes` and the rule tests in `tests/test_nomenclature.py` |
| The checker declares its coverage boundary | review of the `check_nomenclature.py` docstring; `pytest::test_every_canonical_name_appears_in_sep2` |
| A bare `xi` is not statically decidable (damping vs element coordinate) | `manual` — declared in the `check_nomenclature.py` docstring; sibling suites own it |
| Sibling nomenclature conformance is a pre-release gate | `pytest::test_installed_package_uses_canonical_names` (`pypi_artifacts`) |
| SEP 2 records its relation to ISO 7626 and every divergence from it | `manual` (docs) — review of the "Relation to ISO 7626" section in `docs/seps/sep-0002.rst` |
| A name for an uncovered quantity satisfies the guidelines and ISO 7626 | `manual` (SEP 2 prose) — human judgement; not mechanically checkable |
| The pull-request author declares new public names | `manual` (process) — no tool detects an undeclared name; see [§ Pending D](#d-pr-template-and-checker-invocation-deferred) |
| Declared names reach the table via a ledger and a triggered amendment | `manual` (process) — a *SEP 2 pending terms* issue, opened on first declaration and closed by the amendment PR; the mirror tests gate the resulting edit |
| The narrative docs carry the worked procedure | `manual` (docs) — review of `docs/source/dev/nomenclature.rst`; `check_docs.py` |

### sep005-standard
Spec: `openspec/specs/sep005-standard/spec.md` (SEP 5) · Scope: **umbrella-local**

| Requirement | Verified by |
|---|---|
| Umbrella exposes `sep005` as a facade alias to the standalone distribution | `pytest::test_sep005_alias_resolves_to_standalone_distribution` |
| `sep005` is listed in the umbrella public surface | `pytest::test_star_import_of_umbrella_yields_subpackages_and_sep005` |
| SEP 5 dict-format contract (data/name/unit/fs-or-time; no timestamp key) | `pytest` interop: `test_valid_sep005_list_accepted`, `test_missing_*_raises`, `test_prohibited_timestamp_key_raises` |
| `sep005` documented as the SEP 5 standard; ratification path recorded | `manual` (docs) — see Pending |

### distribution-packaging
Spec: `openspec/specs/distribution-packaging/spec.md` · Scope: **umbrella-local**

| Requirement | Verified by |
|---|---|
| Single build definition (hatchling, `pyproject.toml`, no `setup.py`) | `check_sibling_template.py`; build in CI (`python -m build`) |
| No dead CI configuration | `check_docs.py` / review |
| No tracked build artefacts | `.gitignore` (bare `_build/`); sdist excludes `docs/**/_build` |
| Version single-sourced everywhere (installed metadata) | `pytest::test_version` |
| sdist contains only source artefacts (explicit allow-list) | `pytest::test_published_sdist_has_no_stale_packaging` (`pypi_artifacts`) |
| Classifiers reflect the tested support matrix (3.12–3.14) | review vs `python-package.yml` matrix |
| Read the Docs install is complete and canonical | `readthedocs.yaml`; `check_docs.py` |

### documentation
Spec: `openspec/specs/documentation/spec.md` · Checker: `tools/check_docs.py` · Scope: **umbrella-local**

| Requirement | Verified by |
|---|---|
| No foreign-project residue; unified pydata Sphinx theme | `check_docs.py` |
| Docs extras/requirements aligned with theme | `check_docs.py`; docs build (`docs.yml`) |
| README standardised as reStructuredText | `check_docs.py` |
| Umbrella landing page + unified toctree; autodoc for own-code | docs build (`docs.yml`) |
| Unified SEP rendering via `build_index.py` | `python tools/build_index.py` (in `docs.yml`) |
| Canonical variable table surfaced in the narrative docs by transclusion (single definition) | `manual` — `docs/source/dev/nomenclature.rst` includes the marker-delimited region of `sep-0002.rst`; verified by docs build |
| Standardised `readthedocs.yaml`; docs conformance CI job | `check_docs.py` in CI |

### sep-governance
Spec: `openspec/specs/sep-governance/spec.md` (SEP 0) · Checker: `tools/check_seps.py` · Scope: **umbrella-local**

| Requirement | Verified by |
|---|---|
| Every SEP declares `:Authors:`, `:Status:`, `:Type:`, `:Created:` (and `:Resolution:` once ratified) | `pytest::test_missing_field_is_reported`, `test_deprecated_author_spelling_is_reported`, `test_accepted_without_resolution_is_reported`, `test_multi_line_authors_is_read_in_full`; `check_seps.py` |
| `:Status:` is one of the nine values `index.rst.tmpl` renders (case-sensitive) | `pytest::test_unknown_status_is_reported`, `test_miscased_status_is_reported`, `test_template_declares_vocabularies`; `check_seps.py` |
| `:Type:` is one of SEP 0's three kinds (`Standards Track`, `Informational`, `Process`) | `pytest::test_out_of_vocabulary_type_is_reported`, `test_template_declares_vocabularies`; `check_seps.py` |
| `:Created:` is an ISO 8601 `yyyy-mm-dd` date | `pytest::test_non_iso_date_is_reported`, `test_other_non_iso_dates_are_reported`; `check_seps.py` |
| SEP metadata conformance is mechanically enforced, ahead of the index generator | `pytest::test_all_seps_conform`; `check_seps.py` in `.github/workflows/docs.yml` |

### sibling-package-template
Spec: `openspec/specs/sibling-package-template/spec.md` · Checker: `tools/check_sibling_template.py` · Scope: **org-wide**

| Requirement | Verified by |
|---|---|
| Single build definition; version single-sourced via metadata | `check_sibling_template.py` |
| Native namespace portion + wheel contents (no `sdypy/__init__.py`) | `check_sibling_template.py`; `pytest::test_published_wheel_ships_only_own_portion` (`pypi_artifacts`) |
| sdist is an explicit allow-list | `check_sibling_template.py` |
| Canonical test + release workflows; metadata consistency; scaffolding | `check_sibling_template.py` |

### testing-ci
Spec: `openspec/specs/testing-ci/spec.md` · Scope: **mixed** (see rows)

| Requirement | Verified by |
|---|---|
| `pypi_artifacts` marker registered and applied to PyPI-dependent tests | `pyproject.toml` `[tool.pytest.ini_options]`; marker usage in `tests/` |
| GitHub CI deselects `pypi_artifacts`; matrix (3.12–3.14) green | `.github/workflows/python-package.yml` |
| Core test + release workflows have the required shape | review of `python-package.yml`, `release-and-publish-to-pypi.yml` |
| Every first-level package has a functional test baseline **(org-wide)** | sibling repos' suites |
| Core interop suite exercises cross-package composition | `pytest tests/test_interop.py` (EMA/FRF/io/excitation/model chains, ±2–5 % tolerances) |
| Every umbrella-runnable checker executes in core CI | `check_seps.py` + `check_docs.py` steps in `.github/workflows/docs.yml`; review of § Canonical sources |
| All seven fork CIs green after pushes **(org-wide)** | `manual` — see Pending |

---

## Pending requirements

Post-merge work that is **not** spec-driven (the target state is already
canonical above, or the act is pure governance), so it is tracked here rather
than as OpenSpec changes. Preserved in full in the archived change tasks under
`openspec/changes/archive/2026-07-01-*/tasks.md`.

### A. Release siblings to PyPI (infra / maintainer)
Acceptance: the `pypi_artifacts`-marked tests flip from red to green from a fresh
`pip install`.

- [ ] Fix the published wheels of **`sdypy-view`** (0.1.6) and **`sdypy-model`**:
      remove the top-level `sdypy/__init__.py` so each is a native PEP 420
      portion; bump patch versions. *(genuine code fix, in the sibling repos)*
- [ ] Publish the coordinated releases: minor releases EMA 0.30.0, io 0.4.0,
      FRF 0.2.0, excitation 0.2.0, view 0.2.0, model 0.2.0 (public-api round) and
      the template patch releases.
- [ ] After releases land: fresh-venv `pip install sdypy` runs the conformance
      tests green (`test_public_api`, `test_namespace_conformance` flip green).
- [ ] Verify GitHub Actions concludes green on all seven ladisk fork repos
      (the four previously-silent forks show their first successful run).
- [ ] Register `sdypy-FRF`, `sdypy-excitation`, `sdypy-view` on Read the Docs;
      rebuild the stale `sdypy-model` RTD site; decide the `sdypy.org` domain.

### B. Ratify SEP status (governance)
Acceptance: SEP 2/3/5 show `:Status: Accepted` with a `:Resolution:` line, after
recorded team sign-off.

These flips are now gated by `tools/check_seps.py` (see § sep-governance): a
`Draft → Accepted` flip that omits `:Resolution:` fails CI, and the checker runs
before the index generator so the error is a named violation rather than a
traceback. The gate makes the flips safe to perform; it does not perform them —
they stay team-gated.

- [ ] Team sign-off on the curated `__all__` lists and the project-lead
      decisions of 2026-06-12 (view helpers public; FEM material parameters
      unified on `young_modulus`/`poisson_ratio`/`density`; SEP 2 table extended
      with `frf_form` + material params; umbrella `__all__` with eager
      star-import). Gate before the Bucket A releases.
- [ ] Flip `docs/seps/sep-0002.rst` (SEP 2, public API) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Flip `docs/seps/sep-0003.rst` (SEP 3, namespace) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Flip `docs/seps/sep-0005.rst` (SEP 5, sep005) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Rebuild the SEP index (`python tools/build_index.py` in `docs/seps/`).

### C. Align sibling nomenclature with SEP 2 (org-wide)
Acceptance: every name below is available under its canonical spelling, the
divergent name still works and emits `DeprecationWarning`, and positional
callers are unaffected. Established by the `extend-sep2-nomenclature` change;
the contract is `openspec/specs/public-api/spec.md`, not this list.

This inventory is **derived from `tools/check_nomenclature.py` output**, not
asserted independently of it — per the `public-api` spec, a name the checker no
longer reports is dropped from the list. Baseline at the
`canonicalize-sep2-migration-map` change, audited against the **installed**
(published) packages: EMA 0.29.1 → 27 findings, model 0.1.5 → 82, view 0.

**Audit the installed package, not a local clone.** The local `../sdypy-model`
checkout is at 0.1.2 and its `acoustic_external` sources are untracked and
absent, so auditing it reports 68 findings and silently misses 16 — including
every `frequency` site. `../sdypy-EMA` is faithful (identical output either
way), but the model discrepancy is why the counts above are taken from the
installed distributions.

All six first-level packages are checked: EMA 0.29.1 → 27, io 0.4.0 → 0,
FRF 0.1.0 → 0, excitation 0.1.1 → 0, view 0.1.6 → 0, model 0.1.5 → 82.

**A zero for a shim package is vacuous.** `sdypy-FRF` and `sdypy-excitation`
contain no code of their own — each is a single `__init__.py` that does
`from pyFRF import *` / `from pyExSi import *`. `sdypy-io` re-exports `pyuff`,
`lvm_read` and `pyMRAW` as module aliases beside its own `sfmov`. The names a
caller actually touches therefore come from the backend distributions, which the
checker cannot reach: it resolves one portion under `sdypy/`, and the backend is
not there.

SEP 2 places backend parameter names out of scope (see the `frf_form` row), so
the backends are not audited here and their names are not pending work. Note
only that a star-import shim republishes whatever the backend exposes. Whether
that is acceptable is a shim-curation question for the `public-api` spec, not a
nomenclature one.

- [ ] `sdypy-EMA` (27 findings): `nat_freq` → `natural_freq` (public attribute of `Model` —
      needs a class-level `__getattr__` shim, not a plain assignment); `nat_xi` and
      `pole_xi` → `damping_ratio` (`Model.select_closest_poles`, `Model.get_poles`);
      `phi` → `mode_shape` (`Model.get_constants` — a genuine mode shape, but the
      checker no longer reports a bare `phi`, so this one is `manual`; `MAC`/`MSF`/`MCF`
      keep `phi_X`/`phi_A`/`phi` as a recorded SEP 2 exception);
      `lower`/`upper`/`f_lower`/`f_upper` → `freq_lower`/`freq_upper` (`Model.__init__`,
      `Model.get_constants`); `frf_type` → `frf_form` (`Model.__init__`,
      `Model.read_uff`, `LSFD`, `LSFD_old`, `LSFD_proportional`);
      `FRF_ind`/`lower_ind`/`upper_ind`/`pole_ind` → the `_idx` spellings.
- [ ] `sdypy-model` (82 findings): `nat_freq` → `natural_freq` (`Beam.solve`,
      `Tetrahedron.solve`); `K`/`M` → `stiffness_matrix`/`mass_matrix` (`Beam.assemble`,
      `Shell.construct_global_matrices`, `solve_eigenvalue`, `lump_mass_matrix`);
      `org`/`conec` → `nodes`/`elements` (`Beam`, `Tetrahedron`, `construct_loce`);
      `n` → `n_modes` (`Beam.solve`); `E`/`Young` → `young_modulus`, `nu`/`Poisson` →
      `poisson_ratio`, `rho`/`ro`/`Density` → `density` (`Shell`, `Tetrahedron`,
      `MITC4_element`, `MITC4_global`, `H_matrix`, `get_constitutive_tensor`,
      `matrices_k_e_timoshenko`); `derivative_E_ind`/`derivative_ro_ind`/`eig_ind` →
      the `_idx` spellings (`Tetrahedron.matrix_derivative`, `Tetrahedron.S_matrix`).
      The bare uppercase parameters `I`, `A`, `J` and `EI` each need a descriptive
      snake_case name of the maintainer's choosing: SEP 2 has no canonical entry for
      them, so the checker reports the snake_case violation without proposing a
      replacement. In particular `EI` (`matrices_k_e`, `Beam`) is a scalar bending
      rigidity (E·I), **not** a stiffness matrix — SEP 2's `stiffness_matrix` row
      explicitly disclaims it.
- [ ] `sdypy-model`, `acoustic_external` and `mesh` (16 further findings, present in the
      published 0.1.5 but absent from the local 0.1.2 checkout): `frequency` → `freq`
      (`AcousticExternalProblem.__init__`, `Body.__init__`, and three more sites);
      `rho` → `density`; `n` → `n_<plural>`; and the bare
      uppercase parameters `N`, `R`, `G`, which need maintainer-chosen descriptive
      names as `I`/`A`/`J` above do.
- [ ] `sdypy-view`: nothing to do — already conformant (`nodes`, `elements`, `mode_shape`,
      `n_frames`). No release needed for this bucket.
- [ ] `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`: nothing to do — all three
      report zero.
- [ ] Core repo follow-up, after EMA and model ship the rename: move
      `tests/test_interop.py` (six reads of `model.nat_freq` / `ema.nat_freq`) to
      `natural_freq`. Not a blocker — the deprecated alias keeps the suite green meanwhile.
- [ ] Every rename keeps its alias through all of v1.x; removal is gated at v2.0 by the
      SEP 2 deprecation policy.

### D. PR template and checker invocation (deferred)
Acceptance: the declaration line exists in a PR template that contributors
actually see, and a decision is recorded on whether `check_nomenclature.py`
runs automatically.

Established by the `add-sep2-term-governance` change, which deliberately left
these out of scope.

- [ ] No PR or issue template exists in the umbrella, in any of the six
      siblings, or in `sdypy_template_project`. The "new public names introduced
      by this PR" declaration line belongs in one. Creating it touches the
      `sibling-package-template` capability (§ *Repository scaffolding*) and all
      six sibling repos.
- [ ] `tools/check_nomenclature.py` is never run automatically: the umbrella
      `docs.yml` excludes it by design, and no sibling CI invokes it. It is run
      by hand against a clone. Decide whether that stays true.
- [ ] The *SEP 2 pending terms* issue convention is documented but untested in
      practice: the first one is opened when a name is actually declared. Watch
      that it is opened rather than skipped.
- [ ] Generating the author's declaration from a public-name diff would automate
      the one step that is currently pure discipline. Revisit once the human
      path has been used a few times.

**Out of scope, tracked elsewhere.** How the rules defined here propagate to the
sibling namespace packages is being solved centrally, not in this repo.
