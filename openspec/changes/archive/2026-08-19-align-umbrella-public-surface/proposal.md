## Why

Two canonical capability specs contradict each other about the same object. `openspec/specs/public-api/spec.md` § *Umbrella `__all__` matches the six first-level names* states that `sdypy/__init__.py` SHALL declare `__all__ = ["EMA", "io", "FRF", "excitation", "model", "view"]` and that the list contains "no others". `openspec/specs/sep005-standard/spec.md` states that the umbrella `__all__` SHALL include `sep005` **in addition to** the six names, and that the conformance test SHALL assert exactly that. Both are canonical; they cannot both hold.

The shipped code and the test suite already implement the sep005 side: `sdypy/__init__.py` declares `__all__ = list(_SUBPACKAGES) + list(_ALIASES)` (seven names), `tests/test_public_api.py::test_umbrella_all_is_the_six_subpackages_plus_sep005` asserts seven, and `REQUIREMENTS.md` and `AGENTS.md` both describe the surface as "the six sub-package names plus `sep005`". The `public-api` requirement is therefore the sole outlier — and it is falsified by a green test suite, which is the worst kind of stale requirement: nothing fails, so nothing draws attention to it.

The drift is a leftover of sequencing, not a disagreement. `standardize-public-api` (2026-07-01) wrote the six-name requirement; `expose-sep005-standard`, archived the same day, added the alias in the `sep005-standard` capability and never amended the requirement it superseded. The `public-api` spec's own `## Purpose` line already says "plus the `sep005` alias" — only the requirement body and its three scenarios were left behind.

## What Changes

- **Rename the requirement** *Umbrella `__all__` matches the six first-level names* → *Umbrella `__all__` is the six first-level names plus the `sep005` alias*, so the header states the contract rather than contradicting it.
- **Modify the requirement body and all three scenarios** to the seven-name surface: `__all__` equals the six sub-package names plus `sep005`; `from sdypy import *` binds all seven; `dir(sdypy)` includes all seven. This restates in `public-api` what `sep005-standard` already requires — deliberately, because `public-api` is the capability a reader consults for "what is the umbrella's public surface", and a reader who stops there today gets the wrong answer.
- **No code, test, tooling or documentation change.** The tree already conforms; this change moves the specification onto the behaviour that ships, not the reverse.
- **Not in scope**: the *sep005 appears in `__all__` and `__dir__`* requirement in `sep005-standard` stays exactly where it is. `sep005-standard` remains the owner of *why* the alias exists and of the alias-resolution contract; `public-api` owns only the shape of the umbrella's curated surface. This is duplication of a fact across two capabilities, which the project's single-source rule normally forbids — see design.md for why it is the lesser evil here.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `public-api`: the *Umbrella `__all__`* requirement is renamed and its body plus all three scenarios are corrected from six names to the six names plus the `sep005` alias, matching `sep005-standard`, `sdypy/__init__.py` and `tests/test_public_api.py`.

## Impact

- **Core repo only**: `openspec/specs/public-api/spec.md` (one requirement block, at archive time) and its `**Scope:**` preamble line, which names the requirement being renamed and must be updated by hand — the delta mechanism covers requirements, not the spec preamble.
- **Users**: none. No shipped code changes; `sdypy.__all__` is unaffected.
- **Tests / CI**: none. `test_umbrella_all_is_the_six_subpackages_plus_sep005` and `test_star_import_of_umbrella_yields_subpackages_and_sep005` already encode the corrected requirement and stay green throughout.
- **`REQUIREMENTS.md`**: no row change needed — the `public-api` row already reads "Umbrella `__all__` = the six names (+ `sep005` alias)" and was correct all along.
- **Unchanged / out of scope**: the `sep005-standard` capability; the six curated sibling `__all__` lists; the umbrella's lazy-import mechanism; the deprecation policy; SEP 2 and SEP 5 prose and their `:Status:` fields.
