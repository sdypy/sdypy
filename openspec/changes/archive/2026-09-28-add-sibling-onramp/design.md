## Context

See proposal.md — Why. Constraints that shape the approach:

- The checkers depend on the Python standard library only (*Nomenclature
  conformance is mechanically enforced*; `check_sibling_template.py` likewise),
  so they cannot parse YAML.
- The checkers run from a hub clone against a sibling clone
  (`--path ../sdypy-EMA`), so the hub's own files are at a fixed location
  relative to the checker.
- OpenSpec gives no inheritance of `context`/`rules` between repositories:
  Stores share specs only (verified 2026-09-15). Each sibling needs its own
  `openspec/config.yaml`.
- OpenSpec 1.13 rejects a MODIFIED block that drops a scenario name present in
  the main spec, and has no way to rename a scenario.

## Goals / Non-Goals

**Goals:**
- Each shared text has exactly one home in the hub; siblings carry verbatim
  copies that the checker compares.
- The concrete Python set is written once.
- EMA's properly deprecated `frf_type` and `FRF_ind` stop being reported.

**Non-Goals:**
- Running any checker in sibling CI (step 5, `add-sdypy-devtools`).
- The sibling-side files themselves: each sibling gets them in its own PR.
- A sibling `REQUIREMENTS.md`, or baseline specs describing current behaviour.
- The hub's own Python set.

## Decisions

**1. Shared blocks are delimited by marker comments and compared as text.**
The hub's `AGENTS.md` carries a link block between
`<!-- >>> sdypy hub links -->` and `<!-- <<< sdypy hub links -->`; the hub's
`openspec/config.yaml` carries its rules between `# >>> shared rules from the
sdypy hub` and `# <<< shared rules` (added in #11). The checker extracts the
region from the hub file and from the sibling file, markers included, and
compares the strings after normalising line endings. *Alternatives:* parse
`config.yaml` and compare the `rules` mapping — needs PyYAML, breaking the
stdlib-only rule; copy the whole file byte for byte — forces a generic context
that cannot say what the package is; a separate master file under `tools/` —
a second home for text the hub already carries.

**2. The hub link block contains links only, as absolute URLs to
`sdypy/sdypy` on `main`.** Relative paths would resolve inside the sibling.
Contents: the hub's `AGENTS.md` (workflow and definition of done), `docs/seps/`,
the SEP 2 naming page, `openspec/specs/`, `REQUIREMENTS.md`. No prose rule sits
in the block, so it changes only when a hub file moves. `nomenclature.rst` is
not yet upstream (it waits on sdypy/sdypy#29); its link resolves once that
merges.

**3. Shims are identified by the portion name** (`FRF`, `excitation`), the same
set `check_public_api.py` already uses for its shim handling. *Alternative:* a
flag declared by each sibling — a sibling could then exempt itself.

**4. The supported Python set lives in `check_sibling_template.py`**, replacing
`CI_MATRIX` (3.10–3.12) with 3.12, 3.13, 3.14. The floor for `requires-python`
is derived from it (`min`). Keeping it current is a named human task: the hub
maintainer updates the set when SPEC 0's quarterly drop schedule removes a
version, or when the current NumPy and SciPy both publish wheels for a new
CPython minor. *Rejected:* requiring a new minor on its release day — sibling CI
would have to pass on a Python its dependencies do not yet build for.
*Alternative:* compute the set from
today's date and a release table — a checker whose verdict changes with the
calendar is not deterministic.

**5. A deprecated alias is recognised from the code, not from a marker.** A
parameter is exempt when an `if` whose test names it has a body that calls
`warnings.warn(...)` with `DeprecationWarning` as the second positional
argument or the `category=` keyword; all parameters of a function are exempt
when such a call sits unconditionally at the top level of its body, or when it
is decorated `@deprecated` (`warnings.deprecated`, `typing_extensions`). This
matches EMA's existing code (`EMA.py:86–92`, `:818–825`, `:888`) with no new
convention for sibling authors. *Alternative:* a `# sep2: deprecated-alias`
comment — a new convention, and it can drift from the actual warning. The
coverage boundary is unchanged: whether the alias *behaves* correctly (warns,
returns the same value) remains outside the checker's scope.

**6. Two requirements are replaced rather than modified.** *Canonical test
workflow* and *Metadata consistency* carry `3.10, 3.11, and 3.12` and
`at least 3.10` in scenario names. A MODIFIED block cannot rename a scenario
(Context), and keeping the old names would leave the spec contradicting itself.
They are REMOVED and re-ADDED as *… on/with the supported Python set*, with every
other obligation copied unchanged.

## Risks / Trade-offs

- **Every sibling fails the new template checks until on-ramped.** Acceptable:
  the checker is hand-run only until step 5, and each sibling's on-ramp PR is
  small. EMA goes first.
- **Moving the Python floor to 3.12 drops 3.10/3.11 for all siblings.** The
  current NumPy and SciPy already require ≥ 3.12, so those legs test stale
  dependencies. EMA's maintainers agreed; the other siblings' maintainers see
  it in their on-ramp PRs.
- **The set is out of date within days.** SPEC 0 drops 3.12 on 2026-10-02
  (released 2023-10-02). Kept at 3.12–3.14 on purpose: the hub maintainer
  updates it at the drop, the `manual` check this requirement names — so
  siblings on-ramped before then bump their floor twice.
- **Static alias detection can be fooled** — for example a function that warns
  `DeprecationWarning` at the top for an unrelated reason exempts all its
  parameters. The failure is a missed report, never a false one, and the
  sibling test suites still own alias behaviour.
- **After step 5 the checker no longer runs from a hub clone**, so the shared
  blocks must ship inside `sdypy-devtools`. `add-sdypy-devtools` owns that.
