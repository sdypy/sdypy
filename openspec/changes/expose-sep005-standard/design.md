## Context

The 2026-06-16 sep005 audit (facts, verified):
- **Packaging**: `sdypy-sep005` 0.1.1 ships the standalone top-level module `sdypy_sep005/` (`top_level.txt = sdypy_sep005`); it contains no `sdypy/` directory and is **not** a namespace portion. Public API in `sdypy_sep005/sep005.py`: `assert_sep005`, `assert_sep005_channel`, `check_compulsory_fields`, `check_prohibited_fields`, `check_timestamp_iso8601`, and constants `COMPULSORY_FIELDS`/`PROHIBITED_FIELDS`. `assert_sep005` raises `ValueError`/`TypeError` on non-compliance (never returns False). No `__all__`.
- **Blast radius**: `pyFRF.py:10` hard-imports `from sdypy_sep005.sep005 import assert_sep005` (unconditional; pyFRF declares an unpinned `sdypy-sep005` dependency). `sdypy.FRF.assert_sep005` re-exports it. No sibling or core file imports the underscore module directly — all user-facing use goes through `sdypy.FRF.assert_sep005`.
- **Repo control**: no `sdypy/sdypy-sep005` or `ladisk/sdypy-sep005` exists; the only source is `sdypy/sdypy-sep005-compliance` (legacy setup.py, `push: false` for jasasonc, no ladisk fork).
- **SEP classification**: SEP 5 (Draft) defines sep005 as a *data-format standard* and says "a package to test compliance ... is to be developed" (now satisfied by `sdypy-sep005`). SEP 1 doesn't mention sep005; SEP 4's roadmap of eleven `sdypy.*` targets does not include `sdypy.sep005`.
- **Current facade** (`sdypy/__init__.py`): `_SUBPACKAGES = ("EMA","io","FRF","excitation","model","view")`, `__all__ = list(_SUBPACKAGES)`, lazy `__getattr__` over `_SUBPACKAGES`, `__dir__` = globals ∪ `_SUBPACKAGES`. The umbrella test `test_umbrella_all_is_exactly_the_six_names` asserts `sorted(sdypy.__all__) == sorted(_SUBPACKAGES)`.

These facts decided the direction (user-confirmed 2026-06-16): **expose, do not repackage.**

## Goals / Non-Goals

**Goals:**
- `sd.sep005` resolves (lazily) to the `sdypy_sep005` distribution; discoverable via `__all__`/`__dir__`.
- sep005 is documented in the README package table and the docs site as the SEP 5 standard + validator.
- SEP 5 records that its compliance package exists and is put on the Draft→Accepted path.
- Zero backward-compat break; core-repo-only.

**Non-Goals:**
- Repackaging `sdypy_sep005` → `sdypy/sep005/` (breaks pyFRF, needs a repo we can't push, contradicts SEP 1/4/5). Documented as a rejected option below.
- Editing pyFRF or the `sdypy-sep005` package.
- Making io/FRF readers emit/consume the sep005 dict format (future adoption work).
- A new sibling-style `__all__`/docs-theme/CI treatment of `sdypy_sep005` (not our repo).

## Decisions

### D1: `sd.sep005` is a facade alias, not a namespace portion

Add an explicit alias map to `sdypy/__init__.py`:

```python
# Aliases exposed on the umbrella that are NOT sdypy.* namespace portions.
# sep005 ships as the standalone distribution `sdypy_sep005` (SEP 5 standard +
# validator); the backends depend on it directly, so it stays a leaf package and
# is surfaced here only for discoverability.
_ALIASES = {"sep005": "sdypy_sep005"}
```

Extend `__getattr__` to resolve `_ALIASES` (import the aliased module, cache into `globals()`), and keep `_SUBPACKAGES` untouched (sep005 is deliberately not a first-level portion). `__getattr__` returns `import_module("sdypy_sep005")` for `sep005`; unknown names still raise `AttributeError`.

*Why an alias map and not adding "sep005" to `_SUBPACKAGES`?* `_SUBPACKAGES` entries are resolved as `import_module("sdypy." + name)` — there is no `sdypy.sep005` module, so that path would fail. The alias map makes the indirection explicit and self-documents that sep005 is a re-exposed leaf, preserving the SEP 5 framing and the clean layering (backends → sep005 leaf).

### D2: `__all__` and `__dir__` include sep005

`__all__ = list(_SUBPACKAGES) + list(_ALIASES)` and `__dir__` returns `globals() ∪ _SUBPACKAGES ∪ _ALIASES`. Bare `import sdypy` stays lightweight (sep005 is lazy like the rest; `sdypy_sep005` is tiny and pulls no heavy backend). `from sdypy import *` now also binds `sep005`.

### D3: Update the umbrella `__all__` conformance test

`tests/test_public_api.py::test_umbrella_all_is_exactly_the_six_names` currently asserts `sorted(sdypy.__all__) == sorted(_SUBPACKAGES)`. Update it (and its name/intent) to assert `sorted(sdypy.__all__) == sorted(list(_SUBPACKAGES) + list(_ALIASES))`, and add a test that `sd.sep005 is import_module("sdypy_sep005")` and `callable(sd.sep005.assert_sep005)`. These are environment-local (the `sdypy-sep005` dep is installed) and stay **unmarked** (not `pypi_artifacts`) so they run in CI. The per-sibling public-api tests are unaffected (sep005 is not a sibling).

### D4: Documentation

- **README package table**: add a `sep005` row — "Unified-timeseries standard (SEP 5) and compliance validator; `sd.sep005` → `sdypy_sep005`."
- **docs `packages.rst`** (from change #6): add a sep005 entry distinguished from the six sub-packages (it's a standard/validator, linked to the `sdypy-sep005` PyPI page and SEP 5), noting access via `sd.sep005` and that `sdypy.FRF.assert_sep005` re-exports the validator.

### D5: SEP 5 ratification

Edit `docs/seps/sep-0005.rst`: replace "A package to test compliance with the standard is to be developed" with a note that it now exists (`sdypy-sep005`, exposed as `sd.sep005`); add a brief "Reference implementation / access" subsection. Put SEP 5 on the Draft→Accepted path. The actual `:Status:` flip + `:Resolution:` is a **gated team act** (consistent with SEP 2/3) and may remain an open task at archive — do not flip it in this change.

### D6: No conformance-tooling or version changes

`tools/check_public_api.py` checks the six siblings' `__all__`, not the umbrella, so it needs no change. `tools/check_docs.py` checks per-repo invariants, unaffected. No version bump: this is core docs/test/facade work that folds into the umbrella's next release (same no-bump rule as #5/#6).

## Rejected: full repackaging into `sdypy.sep005`

Moving `sdypy_sep005/` → `sdypy/sep005/` would require: forking `sdypy/sdypy-sep005-compliance` to ladisk (we lack push), restructuring + migrating its legacy setup.py to pyproject, shipping a `sdypy_sep005` compat shim, **and** coordinating an upstream pyFRF release (its hard import would otherwise break), **and** amending SEP 1/4/5 to admit sep005 as a first-level member. That is multi-repo, partly outside our control, and contradicts the current SEPs' treatment of sep005 as a standard. Disproportionate for v1.0; not pursued.

## Risks / Trade-offs

- [Users expect `sd.sep005` to be a full sub-package like the six] → docs explicitly frame it as the standard/validator alias; `__dir__` lists it; the API (`assert_sep005` etc.) is what they need.
- [Alias map drifts from reality if `sdypy_sep005` is renamed upstream] → the new resolve-test fails loudly if `import sdypy_sep005` breaks.
- [SEP 5 acceptance stalls] → the exposure + docs stand alone; the status flip is independent and gated, like SEP 2/3.

## Migration Plan

1. Core: alias map + `__all__`/`__dir__` in `sdypy/__init__.py`; update + extend `tests/test_public_api.py`; README table; `packages.rst`; SEP 5 edit; new `sep005-standard` spec.
2. Gate: `pytest -m "not pypi_artifacts"` green (incl. the new sep005 tests); core docs build still succeeds; `openspec validate --strict` green.
3. Push to ladisk/sdypy (core only) on the user's word.
4. Rollback: revert the `sdypy/__init__.py` alias block and the doc/test edits (self-contained).

## Open Questions

Resolved by the project lead (2026-06-16): expose via facade alias, do not repackage. SEP 5 Draft→Accepted flip deferred to the team at the final review.
