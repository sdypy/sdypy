## Why

The template spec says each first-level package SHALL declare "an MIT license",
and the checker reads that as "the classifier
`License :: OSI Approved :: MIT License` is present". The current packaging
standard (PEP 639) declares the license as an SPDX expression,
`license = "MIT"`, and deprecates license classifiers. sdypy-FRF
dropped the classifier on purpose (sdypy/sdypy-FRF#12) and now fails the
checker.

Non-trivial: it changes a spec requirement of `sibling-package-template`.

## What Changes

- **`sibling-package-template`:** *Metadata consistency with the supported
  Python set* states how MIT is declared: by `license = "MIT"`, which needs no
  license classifier, or by the legacy table `license = {text = "MIT"}`
  together with the MIT classifier. In both forms any `License ::` classifier
  present must be the MIT one. Every other `license` value, or none, still
  fails.
- **Checker:** `tools/check_sibling_template.py` requires the MIT classifier
  only for the table form, and in both forms reports a non-MIT `License ::`
  classifier. The check of the `license` value is unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sibling-package-template`: MODIFIED *Metadata consistency with the
  supported Python set*.

## Impact

- Hub: `tools/check_sibling_template.py`, `tests/test_sibling_template.py`,
  `REQUIREMENTS.md` (at archive).
- sdypy-FRF conforms without any change. io, model and EMA (string and
  classifier) and view and excitation (table and classifier) are not affected.
