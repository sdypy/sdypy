## Why

SEP 1 makes SEP 2 (nomenclature) compliance a binding condition for namespace membership, yet SEP 2 is a thin Draft (PEP 8 by reference, one word-order rule, a 7-row variable table) and no first-level package actually has a deliberate public API: none of the six defines `__all__`, the `FRF`/`excitation` shims re-export their backends via bare `import *` (leaking `np`, `scipy`, `warnings`, `CubicSpline`, `beta`, `moment`, internal submodules into the user-visible surface), and naming styles drift inside our own code (`autoMAC` camelCase, `Tetrahedron(Young=, Density=, Poisson=)` CapWords parameters, the FRF acronym spelled four ways). A "solid, consistent v1.0" requires a documented, curated, conformance-checked public API and a ratified nomenclature SEP.

## What Changes

- **Amend SEP 2** (`docs/seps/sep-0002.rst`): keep the existing rules and variable table; add the rules it currently lacks — acronym casing (uppercase in class names and established initialisms such as `MAC`, lowercase in variable/parameter/function names such as `frf`, `fs`), class/function/method naming (CapWords / snake_case, including parameters), the requirement that every first-level package declares its public API via `__all__`, and the deprecation policy for renames; extend the canonical variable table with the evidenced entries `frf_form`, `young_modulus`, `poisson_ratio`, `density`. Put SEP 2 on the Draft → Accepted path (team review + `:Resolution:`).
- **Curate every first-level package's public surface with an explicit `__all__`:**
  - `sdypy.FRF` and `sdypy.excitation` replace `from pyFRF/pyExSi import *` with explicit, curated re-exports — **BREAKING** for code that picked up leaked names (e.g. `from sdypy.excitation import np, CubicSpline`); the backends remain directly importable for anything not curated.
  - `sdypy.EMA` drops the `from .tools import *` star-import for explicit imports; `np`, `tqdm`, `warnings` leave the curated surface.
  - `sdypy.io` ratifies its module-alias style (`uff`, `lvm`, `mraw`, `sfmov`) with a matching `__all__`.
  - `sdypy.view` and `sdypy.model` curate own classes/functions and stop exporting stdlib/third-party imports and incidental submodules.
- **Rename the non-conforming own-code names** with deprecated aliases kept through v1.x — no silent breaks: `EMA.Model.autoMAC` → `auto_mac`, `frf_type=` → `frf_form=`, and unified FEM material parameters (`young_modulus`, `poisson_ratio`, `density`) across `Shell`, `Beam`, `Tetrahedron`; full inventory in design.md. Cross-package *structural* API redesign (FRF object interop, unified `solve()` patterns, `EMA.Model` vs `pyLump.Model` name reuse) is explicitly out of scope — documented as observations for a post-v1.0 change.
- **Add a conformance layer** following the change #3 two-layer pattern: core distribution-layer tests asserting each installed first-level package defines `__all__` and that it contains no leaked third-party/stdlib names, plus a repo-layer checker for the sibling clones.
- **No backend changes**: pyFRF, pyExSi, pyuff, lvm_read, pyMRAW, pyLump are 3rd-level upstream dependencies and keep their APIs; only what the sdypy-* wrappers re-export changes.

## Capabilities

### New Capabilities
- `public-api`: the contract governing the public API surface of the umbrella and the six first-level packages — explicit `__all__` declarations, curated re-exports for backend shims, naming conventions for public names (per amended SEP 2), the deprecation policy for renamed names, and the conformance checks that enforce all of it.

### Modified Capabilities

<!-- none: namespace-packaging (attribute exposure, lazy facade) and distribution-packaging (artifact contents) requirements are untouched. The sibling-package-template capability from change #3 is not yet in openspec/specs/; coordination is noted in design.md. -->

## Impact

- **Core repo**: `docs/seps/sep-0002.rst` (amendment + status path), new conformance tests (extending the `tests/test_namespace_conformance.py` pattern), a repo-layer checker in `tools/`, new `openspec/specs/public-api/spec.md`.
- **All six sibling clones** (ladisk forks): `sdypy/<name>/__init__.py` rewritten to curated explicit exports + `__all__`; deprecated aliases where names change; version bumps (minor, since the visible surface changes — exact numbers in design.md, folding into the still-unreleased change #1/#3 versions where those have not shipped to PyPI).
- **Users**: `import sdypy.<pkg>` behavior unchanged; `from sdypy.FRF import *` / `from sdypy.excitation import *` narrows to the curated names (**BREAKING** only for reliance on leaked backend internals); renamed methods keep working via aliases that emit `DeprecationWarning`.
- **Out of scope**: backend (3rd-level) package APIs, structural cross-package API unification, full docs build-out (change #6), PyPI releases (deferred batch).
