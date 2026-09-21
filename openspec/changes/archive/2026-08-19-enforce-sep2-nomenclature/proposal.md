## Why

`extend-sep2-nomenclature` writes a canonical name table and a set of rename obligations that bind all six first-level packages. Nothing measures them. That is the same shape of gap that `add-sep-governance-checks` closed for SEP metadata, and it fails the same way: silently. A sibling can ship `solve_eigenvalue(K, M)` or a fresh `xi=` parameter and every suite in the organisation stays green, because no test and no checker knows the table exists.

The gap is wider than the new table. `REQUIREMENTS.md` § Canonical sources states that the repo-layer checkers are "also run in CI", and for three of the four that is not true:

| Checker | In CI? | Runs at the umbrella root? |
|---|---|---|
| `check_seps.py` | yes (`docs.yml`) | yes |
| `check_docs.py` | **no** | yes — passes today, nothing runs it |
| `check_public_api.py` | **no** | **no** — exits 1: "expected exactly one portion under .../sdypy, found: ['testing', 'core']" |
| `check_sibling_template.py` | **no** | **no** — exits 2: "could not find exactly one portion directory" |

The last two are sibling-clone checkers by construction: they audit *one* namespace portion, and the umbrella provides none (it provides the facade plus the vestigial `sdypy/core` and `sdypy/testing` stubs). So `AGENTS.md`'s "Common commands" entry `python tools/check_public_api.py --path .` is an instruction that cannot succeed as written, and `REQUIREMENTS.md`'s CI claim describes a state that does not exist in either this repo or, verifiably, in the siblings.

`check_docs.py` is the one genuine omission: it passes at the umbrella root, it verifies documentation requirements the `documentation` capability declares, and it simply was never wired in.

## What Changes

- **Add `tools/check_nomenclature.py`**, following the established checker pattern (`--path`, one violation per line, exit 0/1, stdlib only). It audits public signatures by parsing them with `ast` — no import, so it works without a Qt binding, which matters because `view` and `model` cannot be imported without one.
- **Implement the mechanically decidable subset** of the nomenclature contract, and no more: parameter and public-attribute names checked against the canonical table (`mode_shape`, `damping_ratio`, `natural_freq`, `mass_matrix`, `stiffness_matrix`, `damping_matrix`, `nodes`, `elements`, `freq`, `freq_lower`, `freq_upper`, `frf_form`, …); the `n_<plural>` and `<name>_idx` affix conventions, including `_ind` as a named violation; single-uppercase-letter public parameters (`K`, `M`, `C`, `E`, `EI`); and the `MAC` / `MSF` / `MCF` argument exception, applied to exactly those three names and no others.
- **State what the checker does not cover**, in its module docstring and in `REQUIREMENTS.md`: "an established term of art" and the deprecated-alias behaviour are not statically decidable. Those stay `manual` / sibling-suite rows. A checker that silently covers 60 % of a contract while the roster implies 100 % is worse than no checker.
- **Add `tests/test_nomenclature.py`** in two layers, mirroring `tests/test_public_api.py`: unit tests of the checker against synthetic fixtures, which run in core CI and need no siblings installed; and conformance tests against the installed sibling sources, marked `pypi_artifacts` so they are deselected on GitHub CI and act as the local pre-release gate — the same mechanism that already holds the curated-`__all__` conformance.
- **Wire `check_docs.py` into CI** as a step in `docs.yml`, next to `check_seps.py`.
- **Correct the two inaccurate claims**: `REQUIREMENTS.md` § Canonical sources stops asserting that the sibling-clone checkers run in this repo's CI and says where they do run; `AGENTS.md` § Common commands shows `check_public_api.py` and `check_sibling_template.py` with a sibling-clone path rather than `--path .`.
- **Not in scope**: removing `sdypy/core` and `sdypy/testing`. They are the reason the sibling-clone checkers cannot run at the umbrella root, and they are undocumented in every spec, but deleting a shipped import surface is a `public-api` decision with its own deprecation question — a separate change.
- **Not in scope**: the stale `sibling-package-template` contract (`CI_MATRIX = {"3.10", "3.11", "3.12"}` in `check_sibling_template.py`, `requires-python = ">=3.10"` and `actions/checkout@v4` in its spec), which contradicts `testing-ci`'s `["3.12", "3.13", "3.14"]` and its explicit "`@v4`/`@v5` MUST NOT be reintroduced". Real, unrelated to SEP 2, and separately proposable.

## Capabilities

### New Capabilities
<!-- none. The contract being enforced is `public-api`'s; the CI shape is `testing-ci`'s. -->

### Modified Capabilities
- `public-api`: gains a requirement that nomenclature conformance is mechanically enforced by a standalone checker with a declared coverage boundary.
- `testing-ci`: gains a requirement that every checker capable of running at the umbrella root is executed in core CI, and that checkers requiring a sibling clone are documented as such rather than claimed as CI-covered.

## Impact

- **Core repo**: new `tools/check_nomenclature.py` and `tests/test_nomenclature.py`; one step added to `.github/workflows/docs.yml`; corrections to `REQUIREMENTS.md` § Canonical sources and `AGENTS.md` § Common commands.
- **CI cost**: two `ast`-parsing checkers over a handful of files — negligible, and no new dependency (stdlib only, consistent with `check_seps.py`, which must also run under `python-package.yml`, where neither docutils nor jinja2 is installed).
- **Core CI stays green**: the sibling conformance tests carry the `pypi_artifacts` marker, so the divergences that `extend-sep2-nomenclature` records as obligations do not turn this repo's CI red before the siblings have released.
- **Sibling repos**: the checker becomes available to them; adopting it in their own CI is their call and is not required by this change.
- **Depends on**: `extend-sep2-nomenclature`. The checker encodes the canonical table, so the table must be final first. Archiving these two out of order would encode a table that is still moving.
- **Unchanged / out of scope**: the canonical table's content; the renames themselves; `check_public_api.py`, `check_sibling_template.py` and `check_seps.py` behaviour; `sdypy/core` and `sdypy/testing`; the `sibling-package-template` staleness above.
