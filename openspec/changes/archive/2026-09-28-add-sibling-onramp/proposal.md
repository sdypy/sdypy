## Why

The six sibling repositories carry no instructions for a contributor or an
agent: no `AGENTS.md`, no OpenSpec configuration, nothing that points at the
org-wide rules in this hub. An agent working in `sdypy-EMA` starts blind, and
nothing in the sibling-package-template contract requires otherwise, so the
checker cannot report it. SEP 6 (Draft, #7) names this as implementation step 4.

Two existing template rules also misfire against the first sibling to be
on-ramped. The canonical test workflow must install with exactly `pip install .`,
so EMA — whose tests need a dev-only dependency (`pyLump`) — is reported for
`pip install ".[dev]"`. And the Python set is pinned to 3.10–3.12, while the
current NumPy (2.5) and SciPy (1.18) require Python ≥ 3.12: a sibling's 3.10 and
3.11 legs test only against stale dependencies.

The nomenclature contract contradicts itself. *Evidenced divergences carry
deprecated aliases* requires a renamed name to stay as an alias, while *A
non-canonical parameter name is reported* names `frf_type` as a violation — so
EMA's `frf_type`, kept exactly as the alias the first requirement demands, is
reported by the checker the second requirement specifies.

## What Changes

- **Agent on-ramp** (new requirement): every sibling carries an `AGENTS.md`
  with the hub's link block verbatim, and a one-line `CLAUDE.md`
  (`@AGENTS.md`). Non-shim siblings also carry `openspec/config.yaml` with
  their own `context` and the hub's shared `rules` block verbatim. Each sibling
  writes its own context; the rules have one home, this hub's
  `openspec/config.yaml`.
- `check_sibling_template.py` gains the presence and verbatim-copy checks,
  comparing marker-delimited blocks as plain text (the checkers use the standard
  library only, which has no YAML parser).
- **Supported Python versions follow SPEC 0** (new requirement): a Python minor
  version is supported for 3 years after its release, and a new one once the
  current NumPy and SciPy both publish wheels for it. The concrete set has one
  home, the checker; today it is 3.12, 3.13, 3.14. *Canonical test workflow* and
  *Metadata consistency* now refer to that set instead of naming 3.10–3.12.
  **BREAKING** for the template: every sibling currently declaring
  `requires-python = ">=3.10"` is reported until it moves to `>=3.12`.
- The canonical test workflow may install `pip install .[<extras>]`; reading a
  `requirements*.txt` stays forbidden.
- The nomenclature checker does not report a **deprecated alias**: a parameter
  whose use raises `DeprecationWarning`, or any parameter of a function or
  method that is itself deprecated. It still reports the same name where no
  deprecation warning guards it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sibling-package-template`: ADDED *Agent on-ramp*, ADDED *Supported Python
  versions follow SPEC 0*; MODIFIED *Canonical test workflow* (extras allowed,
  Python set by reference), *Metadata consistency* (Python floor and classifiers
  by reference).
- `public-api`: MODIFIED *Nomenclature conformance is mechanically enforced*
  (deprecated aliases are not reported).

## Impact

- **Hub code:** `tools/check_sibling_template.py`, `tools/check_nomenclature.py`,
  their tests; `REQUIREMENTS.md` rows at archive.
- **Hub `AGENTS.md`:** gains the marker-delimited link block that siblings copy.
- **Depends on #11**, which adds the marker-delimited shared rules block to
  `openspec/config.yaml`. This branch is rebased onto `main` once #11 merges.
- **Siblings:** all six are reported by the hand-run template checker until each
  gets its on-ramp PR and Python bump; no sibling CI runs the checker yet
  (step 5, `add-sdypy-devtools`). The first is `sdypy-EMA`: expected template
  violations 0, nomenclature 20 (from 23) once its on-ramp PR lands.
- **Not in scope:** the hub's own Python set (`testing-ci`,
  `distribution-packaging`) — it already equals 3.12–3.14; following SPEC 0
  there is a separate change. Sibling `REQUIREMENTS.md` and baseline specs are
  deferred until a sibling's first real OpenSpec change.
