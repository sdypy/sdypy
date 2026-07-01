## Context

The `sdypy` core repo accumulated stale packaging artefacts during its transition from setuptools/Travis CI to hatchling/GitHub Actions. The change #1 (`unify-namespace-mechanism`) deliberately deferred their cleanup while it established the build-backend, version-sourcing, and sdist-include-list foundations. This design covers the full sweep now that those foundations are in place.

Current state before this change:

- **`setup.py`**: parses `sdypy/core/__init__.py` for `__version__` with a regex. Change #1 emptied that file to a docstring, so `setup.py` raises `RuntimeError("Cannot find __version__ in …")` if run. Its classifiers contradict pyproject (`Development Status :: 3 - Alpha` and `Python :: 3.8` vs pyproject's `5 - Production/Stable` and `requires-python = ">=3.10"`).
- **`.travis.yml`**: configures Python 3.6/3.7 matrix, installs from `requirements.txt`, runs pytest. Real CI migrated to GitHub Actions; this file has not been updated since.
- **`requirements.txt`**: lists the seven `sdypy-*` dependencies, duplicating `[project] dependencies` in pyproject. Referenced by the live CI workflow via a guarded `if [ -f requirements.txt ]` line.
- **`requirements.dev.txt`**: lists the dev dependencies, duplicating `[project.optional-dependencies] dev` but missing `build` and `sphinx-copybutton>=0.5.2`.
- **`docs/requirements.txt`**: a third copy of a dependency subset (five `sdypy-*` packages + `sphinx-rtd-theme`), referenced by `readthedocs.yaml`. Missing sphinx itself, `sdypy-view`, `sdypy-model`, `sdypy-sep005`, and `sphinx-copybutton`; installs nothing from pyproject.
- **`docs/source/_build/`**: 131 files tracked by git (built HTML, `.doctrees`, `.buildinfo`). The `.gitignore` covers `docs/_build/` and `docs/build/` but not `docs/source/_build/`.
- **`docs/source/conf.py`**: hard-codes `version = '0.5'` and `release = '0.5.1'`, duplicating the pyproject version and violating the single-source-of-truth principle established in change #1.
- **`pyproject.toml` classifiers**: lists only `Programming Language :: Python :: 3.10` while CI tests 3.10, 3.11, and 3.12. Development status is `5 - Production/Stable`, which is misleading before v1.0.

## Goals / Non-Goals

**Goals:**

- A single build/dependency definition: `pyproject.toml` is the authoritative source for install dependencies, dev extras, docs extras, version, and classifiers.
- No stale packaging scripts (`setup.py`) or dead CI configs (`.travis.yml`) in the repo.
- No tracked build artefacts; `_build/` directories git-ignored regardless of nesting depth.
- Version single-sourced from installed metadata everywhere it appears (package facade from change #1; docs `conf.py` via `importlib.metadata`).
- CI installs the actual `sdypy` package (not just its deps) so the test suite runs against the installed package rather than the ambient source directory.
- Read the Docs installs `sdypy` plus full docs deps via one canonical `pip install .[docs]`, ensuring it can import every sub-package referenced in the docs.
- Classifier metadata reflects the actual tested Python matrix.

**Non-Goals:**

- CI matrix or lint overhaul (program change #5).
- Docs content rewrite (program change #6).
- Sibling repo standardization (program change #3 template).
- Git history rewrite (the tracked `_build` files are removed in a plain commit; history purge is not performed).
- Encoding or formatting changes to any file beyond what is required by the decisions below.
- Any behavioral change to the `sdypy` package or its public Python API — no files under `sdypy/` are touched.

## Decisions

**Decision 1 — Delete `setup.py` and `.travis.yml` outright.**
Both files are non-functional and misleading. `setup.py` is actively broken (RuntimeError). `.travis.yml` targets end-of-life Pythons (3.6/3.7) and a dead CI service. Keeping them increases confusion for contributors. No bridge or compatibility shim is needed because hatchling is already the sole build backend and GitHub Actions is already the sole CI provider.

*Alternative considered*: update `setup.py` to be consistent with pyproject. Rejected — maintaining two parallel build definitions is exactly the problem; the right answer is zero legacy files.

**Decision 2 — Delete `requirements.txt` and `requirements.dev.txt`; direct contributors to `pip install .[dev]`.**
Both files duplicate pyproject and have already drifted (`requirements.dev.txt` is missing two entries). Keeping them as thin `-e .` pointer files (e.g. `requirements.txt` containing `-e .`) was considered and rejected: it adds a file whose only value is saving one flag when typing `pip install`, while creating an ongoing maintenance surface.

*Alternative considered*: keep `requirements.txt` as `-e .[dev]` shortcut. Rejected — adds a file for zero functional benefit; pyproject extras are the documented mechanism.

**Decision 3 — CI: replace requirements install line with `pip install .`.**
The live workflow (`.github/workflows/python-package.yml`) runs:
```
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```
Once `requirements.txt` is deleted the condition is false and CI silently stops installing the runtime deps. Replacing the whole line with `pip install .` (a) ensures deps come from pyproject, (b) installs `sdypy` itself (the existing CI never did this — a latent gap where tests could import from the source directory shadow rather than the installed package), and (c) eliminates the file-existence guard. The flake8 and pytest steps are untouched.

*Alternative considered*: leave the guard in place; CI runs fine once the file is gone (condition is false, install silently skipped). Rejected — the latent gap where sdypy itself is never installed is a correctness risk; fixing it now is a small change with clear benefit.

**Decision 4 — Add a `docs` extra to pyproject; switch RTD to it; delete `docs/requirements.txt`.**
A `[project.optional-dependencies]` `docs` entry (sphinx, sphinx-rtd-theme, sphinx-copybutton≥0.5.2) is the canonical place for docs build dependencies, consistent with how the `dev` extra already handles test/build deps. Switching `readthedocs.yaml` to `pip install .[docs]` means RTD installs sdypy itself (so its imports work) plus the full docs toolchain, replacing the incomplete and drifted `docs/requirements.txt`.

The existing `dev` extra already lists sphinx, sphinx-rtd-theme, and sphinx-copybutton. To avoid re-introducing the duplication this change exists to remove, the `dev` extra drops those three entries and references the new extra via the standard self-reference `"sdypy[docs]"` (resolved by pip ≥21.2; widely used). `dev` then reads: `sdypy[docs]`, twine, wheel, pytest, build.

*Alternative considered*: keep `docs/requirements.txt` and add a `pip install .` step to `readthedocs.yaml`. Rejected — produces two partially-overlapping dependency sources; the extra is the cleaner single source. Also considered: listing the sphinx deps in both extras. Rejected — duplicate lists drift, which is the failure mode this whole change addresses.

**Decision 5 — Purge tracked `docs/source/_build/` via `git rm -r --cached`; add `_build/` to `.gitignore`.**
The 131 tracked files are generated output — they should never have been committed. `git rm -r --cached` removes them from the index without touching the working tree (the local build output is preserved for the developer). The `.gitignore` pattern `_build/` (without a leading slash or path prefix) matches any `_build` directory at any depth, which is more robust than the existing path-specific entries (`docs/_build/`, `docs/build/`).

*Alternative considered*: path-specific ignore `docs/source/_build/`. Rejected — `_build/` is the standard Sphinx output directory name; a general pattern future-proofs any nested docs structure. History rewrite via `git filter-branch` or BFG was considered and explicitly rejected as out of scope — the tracked files are non-sensitive generated HTML, the removal commit is sufficient.

**Decision 6 — Derive `release` and `version` in `docs/source/conf.py` from `importlib.metadata`.**
```python
from importlib.metadata import version as _pkg_version
release = _pkg_version("sdypy")
version = ".".join(release.split(".")[:2])
```
This extends the single-source-of-truth principle from change #1 to the docs build, eliminating a second location where the version string must be manually updated at each release.

*Alternative considered*: read `conf.py` version from `pyproject.toml` via `tomllib`. Rejected — requires a file-path assumption (`../../../pyproject.toml`) and `tomllib` is stdlib only from 3.11; `importlib.metadata` is available from 3.8+ and is already used in `sdypy/__init__.py`.

**Decision 7 — Classifier alignment: add `3.11`/`3.12`; change development status to `4 - Beta`.**
Adding the missing Python version classifiers makes the PyPI listing accurate. Changing from `5 - Production/Stable` to `4 - Beta` is an honest signal before the v1.0 milestone release; program change #8 (v1.0 release prep) will flip it back to `5`. This is called out as a reviewable team decision because it is visible on PyPI.

*Alternative considered*: leave the development status as `5 - Production/Stable` to avoid disruption. Rejected — the project is actively in a v1.0 push with known breaking changes planned; `5 - Production/Stable` before v1.0 is misleading.

**Decision 8 — sdist allow-list: drop deleted files, retain all other entries.**
The `[tool.hatch.build.targets.sdist]` include list set up in change #1 currently references `requirements.txt` and `requirements.dev.txt`. Once those files are deleted the entries are harmless but misleading. They are removed. The `docs/**/_build` exclude entries are retained as belt-and-braces even though the tracked files are being removed from the repo.

## Risks / Trade-offs

- **`pip install .[docs]` pins sphinx via the extra** → RTD builds are now constrained by the version range in pyproject. Mitigation: use `>=` lower bounds (not pinned versions) for all docs deps so Dependabot and RTD can update freely.
- **Removing `requirements.txt` breaks any contributor workflow that uses it** → Mitigation: the `pip install .[dev]` replacement is standard practice; document in the PR description and CONTRIBUTING.rst (a docs-content update, deferred to change #6).
- **`importlib.metadata` in `conf.py` requires sdypy to be installed when building docs locally** → This is already required to import sdypy in the docs; not a new constraint. Mitigation: the `docs` extra ensures the RTD environment is complete; local contributors need `pip install .[docs]`.
- **`Development Status :: 4 - Beta` is a PyPI-visible demotion** → This is intentional and accurate; flagged as a team-reviewable decision (Decision 7). Mitigation: plan change #8 (v1.0 release) explicitly restores `5 - Production/Stable`.
- **Git history retains the 131 build-output files** → Accepted as out of scope. The files are non-sensitive generated HTML. A future history rewrite can be done independently if repo size becomes a concern.

## Migration Plan

1. Delete `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`, `docs/requirements.txt`.
2. Add the `docs` extra to `pyproject.toml`; update classifiers and sdist include list.
3. Update `docs/source/conf.py` to derive version from metadata.
4. Update `.github/workflows/python-package.yml` (replace requirements install line).
5. Update `readthedocs.yaml` (switch to pip extra install).
6. Add `_build/` to `.gitignore`; run `git rm -r --cached docs/source/_build`.
7. Verify: `python -m build`, inspect sdist/wheel contents, fresh-venv install, pytest green, `git ls-files docs | grep _build` returns nothing.

**Rollback**: every deletion can be reverted via `git revert` or by restoring from the prior commit. The CI change (`pip install .`) is backward compatible — restoring the old guard line would only matter if `requirements.txt` were also restored. RTD continues to build from `readthedocs.yaml`; reverting the yaml entry restores the old (incomplete) docs install.

## Open Questions

- Should `sphinx-copybutton>=0.5.2` and `sphinx-rtd-theme` carry upper bounds to avoid surprise breakage on RTD? (Leaning no — prefer `>=` bounds and test breakage explicitly.)
- Is `CONTRIBUTING.rst` updated in this change to document `pip install .[dev]`? (Leaning defer to change #6, the docs content change, to avoid scope creep here.)
