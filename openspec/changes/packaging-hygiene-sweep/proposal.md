## Why

The `sdypy` core repo carries several stale packaging artefacts from before the project adopted hatchling and GitHub Actions: a broken `setup.py`, a dead `.travis.yml`, duplicated dependency lists in multiple `requirements*.txt` files, committed Sphinx build output, and version strings hard-coded in `docs/source/conf.py`. These create a misleading picture of the project, cause active breakage (running `setup.py` raises `RuntimeError`), and contradict the single-source-of-truth principle established in change #1. Cleaning them up now removes every cross-cutting packaging inconsistency before the remaining v1.0 changes build on top of this repo.

## What Changes

- **Delete** `setup.py` — broken (reads a now-docstring-only file for `__version__`), contradicts pyproject, hatchling is already the authoritative build backend.
- **Delete** `.travis.yml` — dead CI; real CI is GitHub Actions since the migration.
- **Delete** `requirements.txt` and `requirements.dev.txt` — both duplicate pyproject `[project] dependencies` / `[project.optional-dependencies] dev`; pyproject is the single source.
- **Fix CI** (`python-package.yml`) — replace the `requirements.txt` install line with `pip install .` so CI installs the actual package plus deps from pyproject (also closes the latent gap where CI never installed `sdypy` itself).
- **Add a `docs` extra** to `[project.optional-dependencies]` (sphinx, sphinx-rtd-theme, sphinx-copybutton≥0.5.2); the `dev` extra references it as `sdypy[docs]` instead of duplicating the sphinx entries; switch `readthedocs.yaml` to install via the new extra; delete `docs/requirements.txt` (third duplication, incomplete and drifted).
- **Purge committed Sphinx build output** — `git rm -r --cached docs/source/_build` (131 tracked files); add `_build/` pattern to `.gitignore`.
- **Single-source docs version** — derive `release` and `version` in `docs/source/conf.py` from `importlib.metadata` instead of hard-coded strings.
- **Align pyproject classifiers** — add `Programming Language :: Python :: 3.11` and `:: 3.12` to match the tested matrix; change `Development Status` from `5 - Production/Stable` to `4 - Beta` until the v1.0 release. **BREAKING (PyPI metadata)**: the development-status classifier is a team-visible change on PyPI.
- **Update sdist allow-list** — drop the now-deleted `requirements.txt`/`requirements.dev.txt` entries; keep the `docs/**/_build` excludes.

## Capabilities

### New Capabilities
- `distribution-packaging`: The contract that the core repo has exactly one build/dependency definition (`pyproject.toml`), no stale packaging or CI files, no tracked build artefacts, version single-sourced everywhere (package and docs), metadata consistent with the tested Python support matrix, and clean sdist/wheel contents.

### Modified Capabilities
<!-- None: the `namespace-packaging` spec requirements are unchanged by this sweep. No delta spec needed. -->

## Impact

- **Files deleted**: `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`, `docs/requirements.txt`, and 131 tracked files under `docs/source/_build/`.
- **Files modified**: `pyproject.toml` (classifiers, new `docs` extra, sdist include list), `.github/workflows/python-package.yml` (CI install step), `readthedocs.yaml` (install method), `docs/source/conf.py` (dynamic version), `.gitignore` (add `_build/`).
- **Runtime code**: no Python files under `sdypy/` are touched; zero behavioral change to the package itself.
- **PyPI**: next release will show `Development Status :: 4 - Beta` and the full `3.10/3.11/3.12` classifier set.
- **Contributors**: anyone who ran `pip install -r requirements.txt` locally must switch to `pip install .[dev]`; this is the expected workflow for pyproject-based projects.
