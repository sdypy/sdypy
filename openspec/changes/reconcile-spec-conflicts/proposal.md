## Why

The canonical specs contradict each other in several places, and some cite
names and paths that no longer exist. Each change archived since July edited the
capability it was about and left the older statements in neighbouring specs
untouched. A reader cannot tell which statement binds.

The maintainer's rule: where two statements conflict, the newer one wins.
"Newer" is set below from `git log -S` / `git log -L` and from the dates of the
archive folders under `openspec/changes/archive/`.

Non-trivial: the change modifies and removes spec requirements (AGENTS.md
§ Required workflow). It adds no public name and changes no code.

## What Changes

1. **FRF Documentation URL.** `documentation` *Standardised readthedocs.yaml on
   the oldest supported Python* says FRF and excitation keep their upstream
   backend documentation URLs. That text comes from `establish-docs-website`
   (archived 2026-07-01, commit 1b28592). `sibling-package-template` *Metadata
   consistency with the supported Python set* says `sdypy-FRF` must use its own
   site. That text comes from `frf-not-a-shim` (2026-11-17, a991674).
   **Newer wins:** MODIFIED requirement. FRF points at its own Read the Docs
   site, and only excitation keeps pyExSi's. A scenario for FRF is added.
   `tools/check_docs.py` already exempts excitation only, so no code changes.
2. **Docs theme in the docs extra.** `distribution-packaging` *Single build
   definition* expects `sphinx-rtd-theme`. That text was synced on 2026-06-12
   (e7c4c6f, `packaging-hygiene-sweep`). `documentation` *Unified Sphinx theme*
   and *Docs extras and requirements aligned with theme* require
   `pydata-sphinx-theme` and ban `sphinx-rtd-theme`. Those come from
   `establish-docs-website`, implemented on 2026-06-16 (26abb8d). `pyproject.toml`
   agrees with them. **Newer wins:** MODIFIED requirement, and the scenario
   now names `pydata-sphinx-theme`.
3. **Where distribution-layer checks run.** `sibling-package-template`
   *Conformance checking* says they run in core CI on every push. That text was
   proposed on 2026-06-12 10:12 (6d1ea7c). `testing-ci` marks them
   `pypi_artifacts` and deselects them on GitHub CI, in text committed on
   2026-06-12 14:41 (9c3d294). *Every umbrella-runnable checker executes in core
   CI* (631c54f, 2026-08-19, "stop overclaiming CI") points the same way.
   **Newer wins:** MODIFIED requirement. The checks are the local release-time
   gate. A scenario now states that GitHub CI does not collect them.
4. **Change-scoped requirements in `testing-ci`.** REMOVED *Sibling workflow
   files are not modified by this change*. As a standing rule it contradicts
   `one-step-release` (2026-11-17), which has every sibling copy the hub's
   release workflow. Also REMOVED *All seven fork CIs are green after this
   change's pushes*, a one-off check on the `ladisk` forks with no live rule
   left. Each removal gives its reason in the delta.
5. **Stale details.** All MODIFIED, with the code as the newer side:
   - `testing-ci` *pypi_artifacts marker…*: the test was renamed to
     `test_umbrella_all_is_the_six_subpackages_plus_sep005` on 2026-06-16
     (5319a3e), after the spec text was written on 2026-06-12 (9c3d294).
   - `documentation` *Unified SEP rendering via build_index.py*: the generator
     has lived at `docs/seps/tools/build_index.py` since 236c78a (2020). The
     spec path was never right.
   - `distribution-packaging` *Version single-sourced everywhere*: the scenario
     used a hard-coded `0.6.0`. It now uses `X.Y.Z`.
   - `sep005-standard` *Umbrella exposes sep005 as a facade alias*: the
     requirement text said the alias resolves to the `sdypy_sep005`
     distribution, and its first scenario said `sdypy_sep005.sep005`. Both
     arrived in the same commit (1b28592), so the date cannot decide between
     them. The code (`_ALIASES` in `sdypy/__init__.py`, 5319a3e) and the
     archived design both use `sdypy_sep005.sep005`, so the text now names
     that module.
6. **Extra contradiction found.** `documentation` *No foreign-project residue*
   titles a scenario "removed from shim packages" over io, FRF and
   excitation. `public-api` *Shim packages use explicit curated re-exports*
   (`frf-not-a-shim`, newer) makes excitation the only shim. The
   `frf-not-a-shim` proposal says it fixed this, but the title was not changed.
   MODIFIED: the title names the three packages.

## Open questions

- **CI install step (item 6 of the brief).** `testing-ci` *Core test workflow
  has the required shape* says the install step runs `pip install .` and then
  `pip install pytest flake8 build`. The workflow also installs
  `PySide6-Essentials`. The `dev` extra holds `pytest` and `build` but not
  `flake8`. No other spec contradicts this, so it is left as it is. A possible
  follow-up: install the `dev` extra instead (a parallel PR is changing it).
- **`docs/requirements.txt`.** `documentation` *Docs extras and requirements
  aligned with theme* says each package's `docs/requirements.txt` lists the
  theme. `distribution-packaging` *Single build definition* and *Read the Docs
  install is complete and canonical* forbid that file in the core. None of the
  seven repositories has one. Here the newer text (`documentation`) would
  require a file that no repository has, so the rule gives a bad answer and
  nothing was changed. Proposed fix: drop the file from that requirement.
- **SEP 2 against `public-api`.** `docs/seps/sep-0002.rst` § Re-exported backend
  objects says "`sdypy.FRF.FRF` is pyFRF's `FRF` class", and the canonical-table
  note says `sdypy.FRF` re-exports pyFRF's `FRF`. `public-api` (`frf-not-a-shim`,
  newer) says `sdypy-FRF` holds its own code and must not depend on pyFRF.
  Fixing this means editing a SEP, which goes through its own review and is
  outside this specs-only change.
- **Release requirements.** None of the items needed changes to
  `release-and-publish-to-pypi.yml` or to the release requirements, which
  `release-runs-tests` is editing now.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `documentation`: MODIFIED *No foreign-project residue*, *Unified SEP
  rendering via build_index.py*, *Standardised readthedocs.yaml on the oldest
  supported Python*.
- `distribution-packaging`: MODIFIED *Single build definition*, *Version
  single-sourced everywhere*.
- `sibling-package-template`: MODIFIED *Conformance checking*.
- `testing-ci`: MODIFIED *pypi_artifacts marker registered and applied to all
  PyPI-dependent tests*. REMOVED *Sibling workflow files are not modified by
  this change*, *All seven fork CIs are green after this change's pushes*.
- `sep005-standard`: MODIFIED *Umbrella exposes sep005 as a facade alias*.

## Impact

- Specs only. No code, checker or test changes. `tools/check_docs.py` already
  matches item 1, and the test names, paths and alias already match item 5.
- At archive, `REQUIREMENTS.md` drops the two removed `testing-ci` rows and the
  fork-CI item in § Pending A. It also corrects the *Conformance checking* row
  ("distribution layer in core CI") and the `build_index.py` path. The
  `testing-ci` Purpose/Scope line still names the fork-CI requirement and
  needs editing by hand at archive, because a delta cannot change a Purpose.
