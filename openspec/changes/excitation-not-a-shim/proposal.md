## Why

`sdypy-excitation` used to be a shim: one `sdypy/excitation/__init__.py` that
imported its names from pyExSi. A change to `sdypy-excitation` moves pyExSi's
code into it (`sdypy/excitation/signals.py`) and drops the pyExSi dependency,
as `frf-not-a-shim` did for FRF. `sdypy-excitation` is now a regular package,
and no shim is left. The specs and checkers still treat excitation as a shim:
they exempt it from OpenSpec configuration and autodoc, accept pyExSi's
documentation as its Documentation URL, and run a drift check against pyExSi.

Non-trivial: it removes and changes spec requirements of `public-api`,
`sibling-package-template` and `documentation`.

## What Changes

- **`public-api`:** the requirements that exist only for shims are removed
  (*Shim packages use explicit curated re-exports*, *Advisory drift check for
  shims*). A new requirement keeps the rule that matters for a regular
  package: `sdypy/FRF/__init__.py` and `sdypy/excitation/__init__.py` have no
  `import *`, import their curated names from their own modules, declare a
  matching `__all__` and do not depend on pyFRF or pyExSi. The rule on
  re-exported backend objects no longer uses excitation as its example.
- **`sibling-package-template`:** the OpenSpec configuration exemption is
  gone, so `sdypy-excitation` must carry `openspec/config.yaml`. The
  Documentation URL of every package, `sdypy-excitation` included, must be its
  own site.
- **`documentation`:** `sdypy-excitation` is no longer exempt from autodoc.
  Only `io` is.
- **Checkers:** `tools/check_public_api.py` loses `SHIM_BACKENDS`, the drift
  report and its `importlib` import. `tools/check_sibling_template.py` loses
  `SHIM_PACKAGES`. `tools/check_docs.py` loses `UPSTREAM_DOC_TARGET`. Tests
  that used excitation as the example shim are removed or rewritten, and a new
  test shows that excitation is not exempt.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: REMOVED *Shim packages use explicit curated re-exports*,
  *Advisory drift check for shims*. ADDED *First-level packages import their
  curated names explicitly*. MODIFIED *SEP 2 binds the signatures of
  re-exported backend objects*.
- `sibling-package-template`: MODIFIED *OpenSpec configuration carries the
  hub's shared rules*, *Metadata consistency with the supported Python set*.
- `documentation`: MODIFIED *Autodoc wired for own-code packages*.

## Impact

- Hub: `tools/check_public_api.py`, `tools/check_sibling_template.py`,
  `tools/check_docs.py`, `tests/test_public_api.py`,
  `tests/test_sibling_template.py`, `REQUIREMENTS.md` (at archive).
- `sdypy-excitation` is reported by the sibling template checker until it adds
  `openspec/config.yaml`, and by the docs checker until its Documentation URL
  and autodoc page are its own. Both are `sdypy-excitation` work, not part of
  this change.
