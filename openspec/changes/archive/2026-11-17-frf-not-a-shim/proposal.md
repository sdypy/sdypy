## Why

`sdypy-FRF` used to be a shim: one `sdypy/FRF/__init__.py` that imported its
names from pyFRF. Its PR #7 moves pyFRF's code into `sdypy-FRF`
(`sdypy/FRF/frf.py`, `sdypy/FRF/fft_tools.py`) and drops the pyFRF dependency.
`sdypy-FRF` is now a regular package. Only `sdypy-excitation`, over pyExSi,
stays a shim. The specs and checkers still treat FRF as a shim, so they exempt
it from OpenSpec configuration and autodoc, and they run a drift check against
pyFRF.

Non-trivial: it changes spec requirements of `public-api`,
`sibling-package-template` and `documentation`.

## What Changes

- **`public-api`:** only `sdypy/excitation/__init__.py` is a shim. The FRF
  `__init__.py` has no `import *` and imports its curated names from its own
  modules. The advisory drift check covers pyExSi and excitation only. The
  rule on re-exported backend objects and the divergence inventory no longer
  name pyFRF.
- **`sibling-package-template`:** the OpenSpec configuration exemption names
  only `sdypy-excitation`, so `sdypy-FRF` must carry `openspec/config.yaml`.
  The Documentation URL of `sdypy-FRF` must be its own site, not pyFRF's.
- **`documentation`:** `sdypy-FRF` is no longer exempt from autodoc. The
  template-docstring scenario no longer calls its packages shims. `io` stays
  as it is.
- **Checkers:** `tools/check_public_api.py` keeps only excitation in
  `SHIM_BACKENDS`. `tools/check_sibling_template.py` keeps only excitation in
  `SHIM_PACKAGES`. `tools/check_docs.py` no longer accepts a pyFRF
  Documentation URL for `sdypy-FRF`. Tests that used FRF as the example shim
  use excitation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: MODIFIED *Shim packages use explicit curated re-exports*,
  *Advisory drift check for shims*, *SEP 2 binds the signatures of re-exported
  backend objects*, *Evidenced divergences carry deprecated aliases to the
  canonical names*.
- `sibling-package-template`: MODIFIED *OpenSpec configuration carries the
  hub's shared rules*, *Metadata consistency with the supported Python set*.
- `documentation`: MODIFIED *No foreign-project residue*, *Autodoc wired for
  own-code packages*.

## Impact

- Hub: `tools/check_public_api.py`, `tools/check_sibling_template.py`,
  `tools/check_docs.py`, `tests/test_public_api.py`,
  `tests/test_sibling_template.py`, `REQUIREMENTS.md` (at archive).
- `sdypy-FRF` is reported by the sibling template checker until it adds
  `openspec/config.yaml`, and by the docs checker until its Documentation URL
  and autodoc page are its own. Both are `sdypy-FRF` work, not part of this
  change.
