## Context

SEP 2 ("Nomenclature guidelines", Draft, 2021) defers to PEP 8, adds a broader-term-first word-order rule, and canonizes 7 variable names (`frf`, `freq`, `freq_rad`, `natural_freq`, `fs`, `dt`, `freq_upper`/`freq_lower`). It says nothing about class, function, method, parameter, or module names, and SEP 1 nevertheless makes it binding for namespace membership. The 2026-06 API audit of the installed packages found:

- **No `__all__` anywhere** — not in the six first-level packages, not in the backends (pyFRF, pyExSi, pyuff, lvm_read, pyMRAW, pyLump).
- **Shim leaks**: `sdypy.FRF` (= `from pyFRF import *`) exposes `np`, `scipy`, `warnings`; `sdypy.excitation` (= `from pyExSi import *`) exposes `np`, `CubicSpline`, `beta`, `moment`, `signal` (scipy.signal), `signals` (pyExSi internal) alongside its 11 real signal-generation functions.
- **Own-code leaks**: `sdypy.EMA` exposes `np`, `tqdm`, `warnings` (via `from .tools import *`); `sdypy.view` exposes `np`, `pv`, `io`, `platform`, `subprocess`, `pyperclip`, `warnings`, `haspyqt`, `BackgroundPlotter`, `BasePlotter`, `Image`; `sdypy.model` leaks incidental submodule attributes (`beam`, `shell`, `tetrahedron`, `eigenvalue_solution`).
- **Naming anomalies in own code**: `EMA.Model.autoMAC()` (camelCase), `Tetrahedron(Young=, Density=, Poisson=)` and `Beam(Young=)` (CapWords parameters), the FRF acronym spelled four ways (`FRF` class, `FRF_reconstruct`, `add_frf`, `pyfrf=`).
- **Structural inconsistencies** (recorded, not fixed here): `get_*`-method vs `solve()` vs `construct_*` result-access patterns; `Shell` has no `solve()` while `Beam`/`Tetrahedron` do; `nodes`/`elements` vs `org`/`conec` for the same geometry concept; `EMA.Model` vs `pyLump.Model` name reuse (acceptable — namespaces disambiguate); `frf_type='accelerance'` (EMA) vs `form='receptance'` (pyFRF) for the same concept (the naming side is fixed here via the canonical `frf_form`; the differing defaults and semantics remain out of scope).

Constraints: backends are 3rd-level upstream dependencies (their APIs are out of scope); development on ladisk forks; PyPI releases batched and deferred; change #3's `sibling-package-template` spec is still in its change folder (not yet synced to `openspec/specs/`), so this change must not collide with it — it governs packaging files, this change governs the Python API surface; the two are complementary.

## Goals / Non-Goals

**Goals:**
- Every first-level package (and the umbrella) declares its public API with an explicit, curated `__all__`; no third-party/stdlib names in the curated surface.
- SEP 2 amended to actually cover public naming (classes, functions, methods, parameters, modules, acronyms, framework exemptions) and set on the Draft → Accepted path.
- The few PEP 8 violations in own code renamed with non-breaking deprecated aliases and a written deprecation policy.
- Conformance is testable: distribution-layer tests in core CI + a repo-layer checker for clones.

**Non-Goals:**
- Renaming or restructuring backend APIs (pyFRF's `get_FRF`/`form`, pyuff's surface, etc.).
- Structural cross-package API unification (FRF-object interop, a common `solve()` protocol, result-access pattern). Recorded as observations for a post-v1.0 change.
- Rendered API documentation pages (change #6); PyPI releases (deferred batch); CI workflow changes (change #5).

## Decisions

### D1: Shims switch from `import *` to curated explicit re-exports

`sdypy/FRF/__init__.py` and `sdypy/excitation/__init__.py` replace the star-import with explicit `from pyFRF import FRF, ...` plus a matching `__all__`.

- Curated `sdypy.FRF` surface: `FRF`, `assert_sep005`, `direction_dict`.
- Curated `sdypy.excitation` surface: `burst_random`, `get_kurtosis`, `get_psd`, `impulse`, `nonstationary_signal`, `normal_random`, `pseudo_random`, `random_gaussian`, `sine_sweep`, `stationary_nongaussian_signal`, `uniform_random`.

*Why not keep `import *`?* Zero-maintenance, but the sdypy-level API then silently equals whatever the backend happens to leak — `from sdypy.excitation import *` currently hands users scipy's `beta` distribution object. A wrapper whose only job is to present the backend under the sdypy namespace should present a deliberate surface. *Why not auto-generate `__all__` by filtering `dir(backend)`?* Hides drift instead of surfacing it; a new backend name should be a conscious curation decision. Drift is handled by an advisory conformance check (D4) that reports backend public names missing from the curated list without failing CI.

### D2: Curated `__all__` for every package and the umbrella

- `sdypy.EMA`: `Model`, `MAC`, `MSF`, `MCF`, `complex_freq_to_freq_and_damp`, plus the deliberately-exposed submodules `stabilization`, `normal_modes`, `pole_picking`. The `from .tools import *` star-import is replaced with explicit imports; `np`, `tqdm`, `warnings` leave the surface. Incidental submodule attributes (`EMA`, `tools`) stay importable but out of `__all__`.
- `sdypy.io`: `uff`, `lvm`, `mraw`, `sfmov` — the module-alias aggregator style is **ratified** as io's API (it wraps whole reader libraries, not individual functions).
- `sdypy.view`: `Plotter3D`, `create_fem_mesh`, `prepare_animation_displacements`, `prepare_animation_field`, `copy_image_to_clipboard` (helper inclusion confirmed by the project lead, 2026-06-12). All stdlib/third-party leaks (`np`, `pv`, `io`, `platform`, `subprocess`, `pyperclip`, `Image`, `BackgroundPlotter`, `BasePlotter`, `haspyqt`, `warnings`) excluded.
- `sdypy.model`: `Beam`, `Shell`, `Tetrahedron`, `solve_eigenvalue`, `lumped` (the pyLump alias), `mesh`.
- Umbrella `sdypy`: `__all__ = ["EMA", "io", "FRF", "excitation", "model", "view"]`, matching the lazy facade's `__getattr__`/`__dir__` (SEP 3 names; `sep005` joins in change #7 if accepted). Note `from sdypy import *` then eagerly imports all six — acceptable, the user explicitly asked for everything (confirmed 2026-06-12).

Names excluded from `__all__` may still exist as module attributes (Python attaches submodules on import; removing them is fragile churn). The contract is: `__all__` **is** the documented public API; everything else is unsupported.

### D3: Naming contract (SEP 2 amendment) and rename-vs-alias policy

SEP 2 keeps its existing content (PEP 8 reference, word-order rule, variable table) and gains:

- **Modules/packages**: snake_case words; established acronym subpackages (`EMA`, `FRF`, future `OMA`) stay uppercase as fixed by SEP 3/4.
- **Classes**: CapWords; acronyms uppercase inside CapWords (`FRF`, not `Frf`).
- **Functions/methods/parameters/variables**: snake_case; acronyms lowercase inside snake_case names (`add_frf`, `frf_type`); exception: established standalone criterion functions may be the bare uppercase acronym (`MAC`, `MSF`, `MCF`).
- **Constants**: ALL_CAPS.
- **Framework exemption**: names mandated by an external framework keep that framework's casing (e.g. Qt's `closeEvent` override in `Plotter3D`).
- **Public-surface rule**: every first-level package declares `__all__`; only curated names are supported API.
- **Deprecation policy**: renames keep the old name as an alias emitting `DeprecationWarning` for all of v1.x; removal no earlier than v2.0; new code uses canonical names only.

**Rename inventory** (own code only, all aliased; decided by the project lead 2026-06-12 — unify all three FEM element classes on descriptive snake_case material parameters):

| Current | Canonical | Mechanism |
|---|---|---|
| `EMA.Model.autoMAC()` | `auto_mac()` | old method kept as deprecated wrapper |
| `EMA.Model(frf_type=)` | `frf_form=` | both accepted; old kwarg warns |
| `Shell(E=, nu=, rho=)` | `young_modulus=, poisson_ratio=, density=` | both accepted; old kwargs warn |
| `Tetrahedron(Young=, Density=, Poisson=)` | `young_modulus=, density=, poisson_ratio=` | both accepted; CapWords kwargs warn |
| `Beam(Young=)` | `young_modulus=` | same dual-accept shim (`density` is already canonical) |

Positional callers are unaffected by the parameter renames; the shims only translate (and warn on) the old keyword spellings. Deliberately **not** renamed: `FRF_reconstruct`, `get_H1/H2/Hv`-style domain names (acronym-in-method tension noted in the SEP for future guidance), `construct_loce` (needs domain input), anything in backends — including pyFRF's `form=`, which stays as-is (3rd-level scope).

**Canonical variable table extension** (decided 2026-06-12): the SEP 2 table gains the evidenced entries `frf_form` (FRF form: receptance / mobility / accelerance — resolves the EMA `frf_type` vs pyFRF `form` conflict at the sdypy level), `young_modulus`, `poisson_ratio`, and `density` (FEM material parameters, treated as fixed compound terms rather than contorted into broader-term-first order). Further table extensions belong to the team's acceptance review.

### D4: Contract lives in `openspec/specs/public-api/spec.md`; two-layer conformance

Same pattern as change #3 (D2 there):

- **Distribution layer**: new `tests/test_public_api.py` in the core repo, run against the installed packages. Asserts per package: `__all__` exists; every `__all__` entry resolves via `getattr`; no banned leak names (`np`, `scipy`, `warnings`, `os`, `io`, `platform`, `subprocess`, `pickle`, `tqdm`, `pv` …) in `__all__`; module-type entries in `__all__` only where sanctioned (io's four aliases, EMA's three submodules, model's `lumped`/`mesh`). Plus an **advisory** drift check for the two shims: backend public callables absent from the curated list are reported (not failed) so new backend features get a conscious curation decision.
- **Repo layer**: new `tools/check_public_api.py` auditing the six clones' `__init__.py` files (has `__all__`, no `import *`, curated list matches the spec). Kept separate from `tools/check_sibling_template.py` so #3's checker stays stable; both are clone-CI candidates in change #5.

As with #3, the distribution-layer tests will be red against current PyPI artifacts until the batched releases ship — expected reds, flipping green per publish.

### D5: Version bumps are minor

The visible surface narrows (star-import users) and names are added — more than a patch: **EMA 0.30.0, io 0.4.0, FRF 0.2.0, excitation 0.2.0, view 0.2.0, model 0.2.0**. The still-unreleased change #1/#3 versions (0.29.2 / 0.3.2 / 0.1.1 / 0.1.2 / 0.1.7 / 0.1.5) have not shipped to PyPI; if that is still true when #4 is implemented, a single release per package carries #1+#3+#4 and the minor bump supersedes the pending patch numbers.

### D6: SEP 2 Draft → Accepted is a gated team act

This change authors the amended SEP 2 text and proposes acceptance; flipping `:Status: Draft` to `Accepted` and adding `:Resolution:` happens only after team sign-off (review on the fork's `main` per the program's review model). The status flip is an explicit task that may remain open at archive time, like #3's maintainer-publish note.

## Risks / Trade-offs

- [Narrowed star-imports break downstream code that used leaked names] → minor version bump + changelog note; the backends remain directly importable (`import pyExSi`), so any lost name has a one-line fix.
- [Backend adds a public name and the shim hides it] → advisory drift check in core CI surfaces it; curation review at each release.
- [Typos in hand-written `__all__`] → conformance test resolves every entry via `getattr`.
- [Dual-accept kwargs shims (Young/young) introduce subtle bugs] → tiny wrappers with unit tests per alias; warn-and-forward only, no logic.
- [SEP 2 acceptance stalls in team review] → the API curation stands on its own (the spec is the enforceable contract); the SEP status flip can lag without blocking v1.0 work.
- [Curation judgment wrong (a "leak" was someone's API)] → deprecation policy only covers renames; for dropped star-import names we accept the minor-version break, documented in changelogs.

## Migration Plan

1. Core repo: amend SEP 2, add `public-api` spec, add `tests/test_public_api.py` (expected-red vs PyPI) and `tools/check_public_api.py`, add umbrella `__all__`.
2. Six sibling clones: rewrite `__init__.py` to curated explicit exports, add aliases/shims per rename inventory, bump versions — each gated on `tools/check_public_api.py` + build + fresh-venv import (same gates as #3).
3. Releases: deferred to the batched PyPI release; core CI reds flip green per publish.
4. Rollback: per-package revert of `__init__.py` (no data or layout migration involved).

## Open Questions

All resolved by the project lead on 2026-06-12 (the team can still revisit during the SEP 2 acceptance review):

- **Q1** — `sdypy.view` helpers: **keep all five names** in `__all__` (`Plotter3D` + the four helpers); demotion, if ever, is a later deprecation.
- **Q2** — FEM constructor parameters: **unify all three element classes** on PEP 8-compliant descriptive names — `young_modulus`, `poisson_ratio`, `density` — with dual-accept shims for `Shell`'s `E`/`nu`/`rho` and `Tetrahedron`/`Beam`'s CapWords names.
- **Q3** — SEP 2 canonical table: **extend now** with the evidenced entries (`frf_form`, `young_modulus`, `poisson_ratio`, `density`); `frf_form` is canonical over EMA's `frf_type` (renamed with shim) — pyFRF's `form` is backend scope and untouched.
- **Q4** — Umbrella `__all__`: **add it**; eager import on explicit `from sdypy import *` is accepted behavior.
