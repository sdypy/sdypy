## Context

See proposal.md § Why for the motivation and the checker/CI table. The design-relevant constraints:

**The checker cannot import what it audits.** `sdypy.view` and `sdypy.model` import `pyvistaqt` → `qtpy` at package import time, so a plain `import` fails with `QtBindingsNotFoundError` anywhere without a Qt binding — which is the default local developer environment, and the reason `python-package.yml` installs `PySide6-Essentials` and a stack of headless X libraries. Static analysis avoids all of it. `check_public_api.py` already made this choice for `__all__` parsing; this checker extends it to signatures.

**The audited packages are, right now, non-conformant by design.** `extend-sep2-nomenclature` records the divergences as obligations on the siblings, whose releases are separately queued in `REQUIREMENTS.md` § Pending A. A checker that hard-fails core CI on those divergences would make this repo's CI red for work that belongs in six other repositories.

**The repo already solved that problem once.** The `pypi_artifacts` marker exists precisely for assertions about published sibling artefacts: registered in `pyproject.toml`, deselected by `python-package.yml` via `pytest -m "not pypi_artifacts"`, and run locally as the pre-release gate. `tests/test_public_api.py` uses it for exactly this situation.

## Goals / Non-Goals

**Goals**
- Make a nomenclature divergence loud at the moment someone tries to release it.
- Keep the roster honest: what the checker decides, it is credited for; what it cannot decide, it does not claim.
- Fix the one genuine CI omission (`check_docs.py`) while correcting the two claims that are false.

**Non-Goals**
- Enforcing the parts of the contract that are not statically decidable. A checker that guesses at "established term of art" produces false positives, and false positives are how a checker gets disabled.
- Auditing sibling *repositories* from this repo's CI. The checker takes a clone path; who runs it against which clone is the sibling's decision.
- Removing `sdypy/core` / `sdypy/testing`, or repairing `sibling-package-template`. Both are named in the proposal as separate work precisely so they are not smuggled in here.

## Decisions

**D1 — Static analysis over import-and-introspect.** Forced by the Qt constraint above, and better regardless: the checker runs in any environment, on any clone, without installing the package or its backends. The cost is that decorated or dynamically generated signatures are invisible to it; that is acceptable, because the first-level packages define their public surfaces as plain `def`/`class` statements — verified across all six in the inventory that produced the canonical table.

**D2 — Two test layers, split by the `pypi_artifacts` marker.** Unit tests on synthetic fixtures prove the checker's own logic and run in core CI with nothing installed; conformance tests audit the installed siblings and are marked, so they gate releases without reddening CI. *Alternative considered*: one layer, auditing installed siblings only — rejected, because the checker would then be untested whenever the siblings happen to be conformant, and untestable in an environment without them. *Alternative considered*: unmarked conformance tests with an allow-list of known divergences — rejected: an allow-list is a second, undocumented copy of the rename inventory that drifts from `REQUIREMENTS.md` the first time someone forgets to prune it.

**D3 — Declare the coverage boundary in the checker itself, not only in the roster.** The failure mode this guards against is a reader seeing `check_nomenclature.py` in a "Verified by" column and concluding the requirement is measured. `add-sep-governance-checks` set the precedent of a checker being the conformance authority for a *named subset* of a SEP, with the human parts explicitly excluded; this follows it. The docstring is the right home because it travels with the code when the checker is copied into a sibling repo.

**D4 — Wire `check_docs.py` into `docs.yml`, not `python-package.yml`.** It is a documentation-conformance checker and `docs.yml` is where `check_seps.py` already runs, immediately before the docs build; a failure there is diagnosable in the job that owns docs. Putting it in the test matrix would run it three times per push for no added signal.

**D5 — Correct the false claims rather than make them true.** `REQUIREMENTS.md` says the checkers are "also run in CI"; the fix is to describe reality (two run here, two audit sibling clones), not to invent a CI job that clones six repositories to satisfy a sentence. Likewise `AGENTS.md`'s `--path .` invocation is corrected to a sibling-clone path, because the command as written cannot succeed at the umbrella root and a contributor following the guide hits an error that looks like a broken repo.

**D6 — Canonical table lives in the checker as data, mirrored from SEP 2.** The same shape `check_public_api.py` uses for `CURATED`: a module-level dict with a comment pointing at the spec. It is duplication, and the alternative — parsing the RST grid table out of `sep-0002.rst` at runtime — trades a stable duplication for a brittle parser over a hand-maintained table. The mitigation is a unit test asserting that every canonical name in the checker's table appears in `docs/seps/sep-0002.rst`, so the mirror cannot drift silently.

## Risks / Trade-offs

- [False positives on a legitimate name the table does not cover] → the checker reports only names that are *evidenced divergences from a table entry* (a parameter named `xi` where `damping_ratio` is canonical), never unknown names. A parameter the table says nothing about is not a violation. This keeps the checker quiet enough to stay enabled.
- [The mirrored table drifts from SEP 2] → D6's unit test. If someone adds a row to SEP 2 without updating the checker the test still passes (the checker's set is a subset), which is the safe direction; the reverse — a checker enforcing a name SEP 2 never ratified — fails immediately.
- [The `pypi_artifacts` gate is never run, so divergences are found by nobody] → it is the same exposure the existing `pypi_artifacts` tests already carry, and `AGENTS.md` already documents plain `pytest` as the local pre-release run. This change does not make that worse, but it does not fix it either; a maintainer who never runs the local gate gets no benefit from either suite.
- [Static analysis misses a public name] → documented in the docstring alongside the other boundaries. The inventory showed no decorated public signatures across the six packages today; a sibling that introduces one silently loses coverage for it.

## Migration Plan

Additive: a new checker, a new test module, one CI step, two documentation corrections. Nothing existing changes behaviour, so there is no rollback beyond reverting the commit. The checker must land *after* `extend-sep2-nomenclature` archives, since it encodes that change's table.

## Open Questions

None that affect the specs or the task breakdown. Whether sibling repositories adopt the checker in their own CI is theirs to decide and changes nothing here.
