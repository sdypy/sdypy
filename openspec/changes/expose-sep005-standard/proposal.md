## Why

`sdypy-sep005` — the validator for SEP 5's unified-timeseries format — is a declared dependency of the core umbrella, yet it is invisible from the namespace: it is not reachable as `sd.sep005`, not in the README package table, and not in the docs. It is the last open item (#4) in the 2026-06 core audit. The 2026-06 sep005 audit established three facts that rule out folding it into the namespace as a seventh sub-package: (1) it ships as the standalone top-level module `sdypy_sep005`, not a `sdypy/` portion; (2) the upstream backend pyFRF hard-imports `from sdypy_sep005.sep005 import assert_sep005`, so renaming the module would break `import pyFRF`; (3) its only source repo is `sdypy/sdypy-sep005-compliance`, on which we have no push access, and SEP 1/4/5 classify sep005 as a *data-format standard* (a leaf the backends themselves depend on), not a first-level namespace member. So the right move is to **expose and document** sep005 as a facade alias over the existing leaf package — not to repackage it.

## What Changes

- **Expose `sd.sep005`** through the umbrella's lazy facade as an explicit alias to the installed `sdypy_sep005` distribution (a new alias map in `sdypy/__init__.py`'s `__getattr__`, kept separate from `_SUBPACKAGES` because sep005 is **not** a `sdypy.sep005` namespace portion). `import sdypy as sd; sd.sep005.assert_sep005(...)` resolves to `sdypy_sep005`.
- **List `sep005` in the umbrella `__all__` and `__dir__`** so it is discoverable, and update the umbrella `__all__` conformance test (which currently asserts exactly the six sub-package names) to include the sep005 alias.
- **Document sep005**: add it to the README package table and the docs `packages.rst` page as "the SEP 5 unified-timeseries standard + compliance validator", linking the `sdypy-sep005` distribution and SEP 5.
- **Ratify SEP 5**: update `docs/seps/sep-0005.rst` to record that the compliance package now exists (`sdypy-sep005`, exposed as `sd.sep005`) — the SEP's own "a package to test compliance is to be developed" is now satisfied — and put SEP 5 on the Draft → Accepted path (the status flip is a gated team act, like SEP 2/3).
- **No repackaging, no backward-compat break**: `sdypy_sep005` stays as-is, pyFRF and `sdypy.FRF.assert_sep005` keep working unchanged. This is a core-repo-only change.

## Capabilities

### New Capabilities
- `sep005-standard`: the contract for how the SEP 5 unified-timeseries standard is surfaced in SDyPy — the umbrella facade alias `sd.sep005` over the standalone `sdypy_sep005` distribution (explicitly not a namespace portion), its presence in the umbrella `__all__`/`__dir__`, its documentation in the README/site, and the SEP 5 ratification path.

### Modified Capabilities

<!-- none formally: the public-api capability's "umbrella __all__ = exactly six" requirement lives in the not-yet-synced standardize-public-api change folder (no main spec to delta). The new sep005-standard capability states the umbrella now also exposes sep005; the test_public_api umbrella assertion is updated in implementation. namespace-packaging is unaffected — sep005 is an alias, not a first-level portion, so _SUBPACKAGES is unchanged. -->

## Impact

- **Core repo only**: `sdypy/__init__.py` (alias map + `__all__`/`__dir__`); `tests/test_public_api.py` (umbrella assertion + a new sep005-resolves test); `README.rst` (package table); `docs/source/packages.rst` (sep005 entry); `docs/seps/sep-0005.rst` (compliance-package note + ratification path); new `openspec/specs/...`-style `sep005-standard` spec.
- **Users**: `sd.sep005` now resolves; `sdypy.FRF.assert_sep005` and direct `import sdypy_sep005` continue to work unchanged.
- **Unchanged / out of scope**: the `sdypy_sep005` package itself (standalone, not ours to push); pyFRF (no edit needed); any cross-package *adoption* of the sep005 dict format by io/FRF readers (a future enhancement, not this change). **Deferred to maintainer**: the SEP 5 Draft→Accepted flip (team, at the final review); no new version bump (core docs/test changes fold into the umbrella's next release).
