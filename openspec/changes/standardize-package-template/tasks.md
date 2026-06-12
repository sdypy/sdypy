## 1. Core repo — conformance infrastructure

- [x] 1.1 Create `tools/check_sibling_template.py`: a script that accepts `--path <sibling-clone-dir>` and audits root-file hygiene (no `setup.py`, `requirements*.txt`, `.travis.yml`, `sync_version.py`), pyproject shape (hatchling backend, `requires-python >=3.10`, MIT, classifiers match CI matrix, `[project.urls]` Homepage/Source pointing at the package's own repository (Documentation may point at backend docs), `dev` and `docs` extras present, sdist include list present, wheel packages list is `["sdypy"]` (the namespace root — `"sdypy/<pkg>"` would strip the prefix and break the wheel)), workflow file names (`python-package.yml` exists, no `pytest.yaml`; `release-and-publish-to-pypi.yml` exists, no underscore variant), workflow matrix covers `[3.10, 3.11, 3.12]`, action versions `>=v4`/`>=v5`, and `sdypy/<pkg>/__init__.py` version derivation pattern; exits non-zero and prints all violations found.
- [x] 1.2 Extend `tests/test_namespace_conformance.py` with distribution-layer template checks for each of the six sibling packages: fetch the latest sdist from PyPI, assert no `setup.py` / `requirements*.txt` / `sync_version.py` entries; fetch the latest wheel, assert no `sdypy/__init__.py` entry and wheel `sdypy/` entries are under `sdypy/<pkg>/` only; assert `importlib.metadata` can resolve the package version. The checks test the *latest published release*, so they stay red until each package's patch release ships and flip green per publish (accepted in design Risks — same dynamic as the change #1/#2 conformance reds; no xfail marking).
- [x] 1.3 Sanity-check the repo-layer checker against the current (pre-change) sibling clones: `python tools/check_sibling_template.py --path packages/sdypy-EMA` (and each of the other five) must exit non-zero and report exactly the violations the 2026-06 audit found — confirms the checker detects what it should before the cleanup begins.

## 2. sdypy-EMA

- [x] 2.1 Delete stale files: `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`, `sync_version.py`.
- [x] 2.2 Align `pyproject.toml`: remove `dynamic = ["version"]` if present; set `version = "0.29.2"` literal in `[project]`; add/update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with an explicit `include` allow-list (source tree, `tests/`, docs source, `README.rst`, `LICENSE`, `pyproject.toml`) that excludes `data/`, `_build/`, and the deleted artefacts; ensure `requires-python = ">=3.10"`, MIT license entry, hatchling backend; add `Programming Language :: Python :: 3.10`, `3.11`, `3.12` classifiers; keep `Development Status :: 5 - Production/Stable`; verify `[project.urls]` point at sdypy-EMA's own repo/docs; add `docs` and `dev` extras following the core pattern (`dev` references `sdypy-EMA[docs]`).
- [x] 2.3 Rewrite `sdypy/EMA/__init__.py` version derivation: replace the hard-coded `__version__ = "0.29.1"` block with `importlib.metadata.version("sdypy-EMA")` and `PackageNotFoundError` → `"0+unknown"` fallback.
- [x] 2.4 Rewrite `.github/workflows/python-package.yml`: push+PR triggers; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; steps: `actions/checkout@v4`, `actions/setup-python@v5`, `pip install .`, `pip install pytest flake8`, flake8, pytest, `python -m build`. Remove any `requirements.txt` reference.
- [x] 2.5 Rewrite `.github/workflows/release-and-publish-to-pypi.yml`: `v*` tag trigger; single Python (3.11); `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step. Ensure the filename uses hyphens (not underscores).
- [x] 2.6 Scaffolding: verify `LICENSE` is present; verify `readthedocs.yaml` installs via `extra_requirements: [docs]`; ensure `.gitignore` covers `dist/`, `_build/`, `*.egg-info`.
- [x] 2.7 Verification gate: run `python -m build` from `packages/sdypy-EMA` and confirm clean sdist and wheel (inspect: no `data/`, no deleted artefacts, no `sdypy/__init__.py` in wheel); create a fresh venv in a neutral directory (not under `C:\Users\jasas\Work\OpenSource\SdyPy\`), install from the built sdist, run `python -c "import sdypy.EMA; print(sdypy.EMA.__version__)"` and confirm it prints `0.29.2`; run `python tools/check_sibling_template.py --path packages/sdypy-EMA` from the core repo and confirm exit 0.

## 3. sdypy-io

- [x] 3.1 Delete stale files: `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`.
- [x] 3.2 Align `pyproject.toml`: set `version = "0.3.2"` literal; update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with explicit `include` allow-list (no deleted artefacts, no `_build/`); ensure `requires-python = ">=3.10"`, MIT, hatchling; add/update Python 3.10/3.11/3.12 classifiers and `Development Status :: 4 - Beta`; verify `[project.urls]` point at sdypy-io; add `docs` and `dev` extras.
- [x] 3.3 Rewrite `sdypy/io/__init__.py` version derivation: `importlib.metadata.version("sdypy-io")` with `PackageNotFoundError` → `"0+unknown"` fallback.
- [x] 3.4 Rewrite `.github/workflows/python-package.yml`: push+PR triggers; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; `actions/checkout@v4`, `actions/setup-python@v5`; `pip install .`; flake8 + pytest; `python -m build`.
- [x] 3.5 Rewrite `.github/workflows/release-and-publish-to-pypi.yml`: `v*` tag trigger; `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step (fixes the broken sync that never ran).
- [x] 3.6 Scaffolding: verify `LICENSE` is present; verify/add `readthedocs.yaml` installing via `extra_requirements: [docs]`; ensure `.gitignore` covers build output.
- [x] 3.7 Verification gate: `python -m build` clean; fresh-venv install from neutral dir; `python -c "import sdypy.io; print(sdypy.io.__version__)"` prints `0.3.2`; `python tools/check_sibling_template.py --path packages/sdypy-io` exits 0.

## 4. sdypy-FRF

- [x] 4.1 Delete stale files: `requirements.txt`, `requirements.dev.txt`.
- [x] 4.2 Align `pyproject.toml`: set `version = "0.1.1"` literal; update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with explicit `include` allow-list; ensure `requires-python = ">=3.10"`, MIT, hatchling; Python 3.10/3.11/3.12 classifiers and `Development Status :: 4 - Beta`; align `[project.urls]` — Homepage/Source must point at the sdypy-FRF repository; the Documentation entry stays at pyFRF's docs (conformant per resolved Q3); add `docs` and `dev` extras.
- [x] 4.3 Rewrite `sdypy/FRF/__init__.py` version derivation: `importlib.metadata.version("sdypy-FRF")` with `PackageNotFoundError` → `"0+unknown"` fallback.
- [x] 4.4 Rewrite `.github/workflows/python-package.yml`: push+PR; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; `actions/checkout@v4`, `actions/setup-python@v5`; `pip install .`; flake8 + pytest; `python -m build`.
- [x] 4.5 Rewrite `.github/workflows/release-and-publish-to-pypi.yml`: `v*` tag trigger; `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step.
- [x] 4.6 Scaffolding: add `readthedocs.yaml` (missing) installing via `extra_requirements: [docs]`; verify `LICENSE` present; ensure `.gitignore` covers build output.
- [x] 4.7 Verification gate: `python -m build` clean; fresh-venv install from neutral dir; `python -c "import sdypy.FRF; print(sdypy.FRF.__version__)"` prints `0.1.1`; `python tools/check_sibling_template.py --path packages/sdypy-FRF` exits 0.

## 5. sdypy-excitation

- [x] 5.1 Delete stale files: `requirements.txt`, `requirements.dev.txt`.
- [x] 5.2 Align `pyproject.toml`: set `version = "0.1.2"` literal (resolves the pyproject 0.1.1 / `__init__` 0.1.0 mismatch upward past the ambiguous 0.1.1); update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with explicit `include` allow-list; ensure `requires-python = ">=3.10"`, MIT, hatchling; Python 3.10/3.11/3.12 classifiers and `Development Status :: 4 - Beta`; align `[project.urls]` — Homepage/Source must point at the sdypy-excitation repository; the Documentation entry stays at pyExSi's docs (conformant per resolved Q3); add `docs` and `dev` extras.
- [x] 5.3 Rewrite `sdypy/excitation/__init__.py` version derivation: `importlib.metadata.version("sdypy-excitation")` with `PackageNotFoundError` → `"0+unknown"` fallback. This structurally resolves the live version mismatch (nothing left to mismatch).
- [x] 5.4 Rewrite `.github/workflows/python-package.yml`: push+PR; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; `actions/checkout@v4`, `actions/setup-python@v5`; `pip install .`; flake8 + pytest; `python -m build`.
- [x] 5.5 Rewrite `.github/workflows/release-and-publish-to-pypi.yml`: `v*` tag trigger; `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step.
- [x] 5.6 Scaffolding: add `readthedocs.yaml` (missing) installing via `extra_requirements: [docs]`; verify `LICENSE` present; ensure `.gitignore` covers build output.
- [x] 5.7 Verification gate: `python -m build` clean; fresh-venv install from neutral dir; `python -c "import sdypy.excitation; print(sdypy.excitation.__version__)"` prints `0.1.2`; `python tools/check_sibling_template.py --path packages/sdypy-excitation` exits 0.

## 6. sdypy-view

- [x] 6.1 Delete stale files: `requirements.txt`, `requirements.dev.txt`, `sync_version.py`.
- [x] 6.2 Align `pyproject.toml`: set `version = "0.1.8"` literal (or keep current pyproject version if change #1 re-release view 0.1.7 has not shipped yet — ship both fixes at once at 0.1.7 in that case); update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with explicit `include` allow-list; ensure `requires-python = ">=3.10"`, MIT, hatchling; add Python 3.10 and 3.11 classifiers to widen from 3.12-only to `[3.10, 3.11, 3.12]` and `Development Status :: 4 - Beta`; verify `[project.urls]` point at sdypy-view; add `docs` and `dev` extras.
- [x] 6.3 Rewrite `sdypy/view/__init__.py` version derivation: `importlib.metadata.version("sdypy-view")` with `PackageNotFoundError` → `"0+unknown"` fallback.
- [x] 6.4 Rename `.github/workflows/pytest.yaml` → `python-package.yml`; rewrite: push+PR triggers; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; `actions/checkout@v4`, `actions/setup-python@v5`; `pip install .`; flake8 + pytest; `python -m build`. Remove the old `pytest.yaml`.
- [x] 6.5 Rename/rewrite the release workflow to `.github/workflows/release-and-publish-to-pypi.yml` (rename from the underscore variant if present): `v*` tag trigger; `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step. Remove the old underscore-named file.
- [x] 6.6 Scaffolding: add `readthedocs.yaml` (missing) installing via `extra_requirements: [docs]`; verify `LICENSE` present; ensure `.gitignore` covers build output.
- [x] 6.7 Verification gate: `python -m build` clean; fresh-venv install from neutral dir; `python -c "import sdypy.view; print(sdypy.view.__version__)"` prints the expected version; `python tools/check_sibling_template.py --path packages/sdypy-view` exits 0.

## 7. sdypy-model

- [x] 7.1 Delete stale files: `requirements.txt`, `requirements.dev.txt`, `sync_version.py`.
- [x] 7.2 Align `pyproject.toml`: set `version = "0.1.6"` literal (or 0.1.5 if change #1 re-release has not shipped); update `[tool.hatch.build.targets.wheel]` with `packages = ["sdypy"]`; update `[tool.hatch.build.targets.sdist]` with explicit `include` allow-list; ensure `requires-python = ">=3.10"`, MIT, hatchling; add Python 3.10 and 3.11 classifiers to widen from 3.12-only to `[3.10, 3.11, 3.12]` and `Development Status :: 4 - Beta`; verify `[project.urls]` point at sdypy-model; add `docs` and `dev` extras; keep `readme = "README.md"` (model legitimately uses Markdown).
- [x] 7.3 Rewrite `sdypy/model/__init__.py` version derivation: `importlib.metadata.version("sdypy-model")` with `PackageNotFoundError` → `"0+unknown"` fallback.
- [x] 7.4 Rename `.github/workflows/pytest.yaml` → `python-package.yml`; rewrite: push+PR triggers; ubuntu-latest; matrix `[3.10, 3.11, 3.12]`; `actions/checkout@v4`, `actions/setup-python@v5`; `pip install .`; flake8 + pytest; `python -m build`. Remove the old `pytest.yaml`.
- [x] 7.5 Rename/rewrite the release workflow to `.github/workflows/release-and-publish-to-pypi.yml` (rename from the underscore variant if present): `v*` tag trigger; `python -m build`; `pypa/gh-action-pypi-publish`; no version-sync step. Remove the old underscore-named file.
- [x] 7.6 Scaffolding: verify `readthedocs.yaml` is valid and installs via `extra_requirements: [docs]`; verify `LICENSE` present; ensure `.gitignore` covers build output.
- [x] 7.7 Verification gate: `python -m build` clean; fresh-venv install from neutral dir; `python -c "import sdypy.model; print(sdypy.model.__version__)"` prints the expected version; `python tools/check_sibling_template.py --path packages/sdypy-model` exits 0.

## 8. Final cross-package verification

- [x] 8.1 Run `python tools/check_sibling_template.py --path packages/sdypy-EMA` through all six siblings and confirm all exit 0 with no violations.
- [x] 8.2 Run `openspec validate standardize-package-template --strict` in the core repo and confirm it passes with no errors.
- [ ] 8.3 Note for maintainer (outside these tasks): tag each sibling repo to trigger the release workflow and publish the patch releases to PyPI (see D7 for version numbers). Once each package publishes, its distribution-layer conformance tests in `tests/test_namespace_conformance.py` flip from red to passing.
