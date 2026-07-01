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
- `tools/check_*.py` — a repo-layer conformance checker (also run in CI).
- `manual` — a human/governance act with no automated gate (tracked in
  [§ Pending requirements](#pending-requirements)).

---

## Canonical sources

| Source | What it governs |
|---|---|
| `openspec/specs/*/spec.md` | Normative requirements (7 capabilities, below) |
| `docs/seps/sep-000*.rst` | SEP governance (SEP 1 levels, 2 API, 3 namespace, 5 sep005) |
| `tools/check_public_api.py` | Executable `public-api` conformance |
| `tools/check_docs.py` | Executable `documentation` conformance |
| `tools/check_sibling_template.py` | Executable `sibling-package-template` conformance |
| `tests/` | Functional + interop + conformance test suite |

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
| Standardised `readthedocs.yaml`; docs conformance CI job | `check_docs.py` in CI |

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

- [ ] Team sign-off on the curated `__all__` lists and the project-lead
      decisions of 2026-06-12 (view helpers public; FEM material parameters
      unified on `young_modulus`/`poisson_ratio`/`density`; SEP 2 table extended
      with `frf_form` + material params; umbrella `__all__` with eager
      star-import). Gate before the Bucket A releases.
- [ ] Flip `docs/seps/sep-0002.rst` (SEP 2, public API) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Flip `docs/seps/sep-0003.rst` (SEP 3, namespace) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Flip `docs/seps/sep-0005.rst` (SEP 5, sep005) `Draft` → `Accepted` + `:Resolution:`.
- [ ] Rebuild the SEP index (`python tools/build_index.py` in `docs/seps/`).
