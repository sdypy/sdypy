## 1. Core: strip foreign-project residue

- [x] 1.1 Delete the SciPy build subtree: `docs/source/building/index.rst`, `linux.rst`, `windows.rst`, `macosx.rst`, `faq.rst` (the whole `docs/source/building/` directory).
- [x] 1.2 De-NumPy `docs/seps/conf.py`: remove/replace `html_logo = '../source/_static/numpylogo.svg'`, the `github_url`/`twitter_url`/wish-list URLs pointing at numpy, `htmlhelp_basename` NumPy values, the LaTeX/man/texinfo `*_documents` titles+authors reading "NumPy Enhancement Proposals"/"NumPy Developers", and the `intersphinx_mapping` numpy/scipy keys. Re-brand all to SDyPy (project "SDyPy Enhancement Proposals", SDyPy GitHub URL, htmlhelp_basename "sdypy-seps").
- [x] 1.3 Fix `docs/seps/sep-0000.rst`: retarget footnotes/links that point at the numpy mailing list and `numpy.org/neps` to the SDyPy equivalents (SDyPy GitHub / SEP index); keep SEP-process prose.
- [x] 1.4 Remove the dead `https://www.sdypy.org/devdocs` reference in `docs/seps/roadmap.rst` (replace with the RTD docs URL or drop).
- [x] 1.5 Fix the `ttps://github.com/sdypy/sdypy.git` typo (missing `h`) in `docs/source/dev/contributing.rst`.
- [x] 1.6 Reword stray copy-paste residue in `docs/source/dev/governance.rst` ("SciPy umbrella", "SciPy work" in prose, lines ~307–310) to SDyPy, but KEEP the explicit "adapted from the SciPy project's governance document" acknowledgement (and the equivalent in `code_of_conduct.rst`).

## 2. Core: conf.py, landing page, and unified SEP integration

- [x] 2.1 Rewrite `docs/source/conf.py`: set `html_theme = "pydata_sphinx_theme"`; add `"sphinx_copybutton"` to `extensions`; add `sphinx.ext.intersphinx` with a python/numpy mapping; fix the lowercase "sdypy project Documentation" LaTeX/man titles to "SDyPy"; add an `html_theme_options` with a top navbar containing links to the six package doc sites; keep dynamic version from `importlib.metadata`.
- [x] 2.2 Rewrite `docs/source/index.rst` as a real landing page: mission statement, `pip install sdypy` snippet, a package-integration table, and a single toctree with sections: Getting started, Packages, SEPs, Development.
- [x] 2.3 Create a Packages overview page (e.g. `docs/source/packages.rst`) listing all six siblings with one-line descriptions and links to each doc site (EMA/io/view/model own RTD; FRF→pyFRF docs, excitation→pyExSi docs).
- [x] 2.4 Wire the `dev/` pages into the toctree (Development section): `dev/contributing`, `dev/governance`, `dev/code_of_conduct`, `dev/pep8`, and `dev/governance_people` (remove its `:orphan:` or link it); update `dev/readme.dev.rst` to drop dead `.travis.yml`/`setup.py`/`requirements.dev.txt` references.
- [x] 2.5 Integrate SEP rendering: add a `build.jobs.pre_build` step to the core `readthedocs.yaml` that runs `python docs/seps/tools/build_index.py` so the generated SEP index (all SEPs incl. 0005) is current at build time; surface the SEP tree under the umbrella toctree (SEPs section). Delete the manual `docs/source/SEPs.rst` include list.
- [x] 2.6 Fill the bodyless subsections in `docs/seps/roadmap.rst` ("Interoperability", "User experience") with real content derived from the existing roadmap/scope text.

## 3. Core: autodoc, docs extra, readthedocs.yaml

- [x] 3.1 Replace the commented-out `automodule` block in `docs/source/code.rst` with active `.. automodule:: sdypy` (and the lazy-facade note) plus directives covering the umbrella's public surface; ensure it builds (the umbrella `__getattr__` is lazy — document the six names, do not force-import heavy backends).
- [x] 3.2 Update the core `pyproject.toml` `[project.optional-dependencies] docs` extra: list `sphinx`, `pydata-sphinx-theme`, `sphinx-copybutton>=0.5.2`; remove `sphinx-rtd-theme`.
- [x] 3.3 Standardize the core `readthedocs.yaml`: `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python: "3.12"`, `sphinx.configuration: docs/source/conf.py`, `python.install` pip `.` extra `docs`, plus the `build.jobs.pre_build` SEP step from 2.5.

## 4. Core: conformance checker and CI job

- [x] 4.1 Create `tools/check_docs.py` accepting `--path <repo>`. Assert per repo: `docs/source/conf.py` (or `docs/seps/conf.py` for the SEP project) sets `html_theme = "pydata_sphinx_theme"`; a `README.rst` exists and no `README.md`; the `docs` extra in `pyproject.toml` lists `pydata-sphinx-theme` and no competing theme (`sphinx-rtd-theme`/`sphinx-book-theme`/`myst-parser`); no foreign-residue strings (`numpylogo`, "NumPy Enhancement Proposals", "A project template for the SDyPy effort", `www.sdypy.org/devdocs`, `ttps://`) outside an allowlist (governance/CoC "adapted from SciPy" lines, ` import numpy as np` in code blocks); the `[project.urls]` Documentation target matches the package class (EMA/io/view/model own RTD, FRF/excitation upstream). Print all violations; exit non-zero on any. Keep separate from `check_sibling_template.py` and `check_public_api.py`.
- [x] 4.2 Create `.github/workflows/docs.yml` in the core repo: trigger on `push`/`pull_request`/`workflow_dispatch`; `actions/checkout@v4` + `actions/setup-python@v5` (py 3.12); `pip install .[docs]`; run `python docs/seps/tools/build_index.py`; run `sphinx-build -b html docs/source docs/_build/html` (must succeed; do NOT add `-W` yet). Do not modify the existing `python-package.yml` or `release-and-publish-to-pypi.yml`.
- [x] 4.3 Gate (core): install the docs deps into the venv (`C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pip install pydata-sphinx-theme sphinx sphinx-copybutton`), run `python docs/seps/tools/build_index.py` then `sphinx-build -b html docs/source docs/_build/html` from `C:\Users\jasas\Work\OpenSource\SdyPy\sdypy` and confirm it succeeds and the SEP index includes 0005; run `python tools/check_docs.py --path .` and confirm exit 0.

## 5. sdypy-EMA docs

- [x] 5.1 In the `packages/sdypy-EMA` clone, set `docs/source/conf.py` `html_theme = "pydata_sphinx_theme"`; keep `sphinx_copybutton`, autodoc, napoleon, intersphinx.
- [x] 5.2 Align `pyproject.toml` `docs` extra and `docs/requirements.txt` to `pydata-sphinx-theme` (remove `sphinx-rtd-theme` from the extra and `sphinx-book-theme` from requirements.txt).
- [x] 5.3 Standardize `readthedocs.yaml` (ubuntu-24.04, python 3.12, pip `.[docs]`).
- [x] 5.4 Fix the `|pytest|` badge target in `README.rst`: `sdypa-EMA` → `sdypy-EMA`.
- [x] 5.5 Gate: `sphinx-build -b html docs/source docs/_build/html` from the clone succeeds; `python C:\Users\jasas\Work\OpenSource\SdyPy\sdypy\tools\check_docs.py --path .` exits 0.

## 6. sdypy-io docs

- [x] 6.1 Set `docs/source/conf.py` theme → `pydata_sphinx_theme` (keep copybutton/autodoc/intersphinx).
- [x] 6.2 Align `pyproject.toml` `docs` extra and `docs/requirements.txt` to `pydata-sphinx-theme` (remove `sphinx-rtd-theme`).
- [x] 6.3 Standardize `readthedocs.yaml` (ubuntu-24.04/py3.12).
- [x] 6.4 Remove the "A project template for the SDyPy effort.." module docstring from `sdypy/io/__init__.py`, replacing it with a real one-line description of the io aggregator.
- [x] 6.5 Fix `docs/source/sfmov.rst` to use `from sdypy import io` / `io.sfmov` rather than bare `import pysfmov`.
- [x] 6.6 Gate: `sphinx-build` from the clone succeeds; `check_docs.py --path .` exits 0.

## 7. sdypy-FRF docs

- [x] 7.1 Set `docs/source/conf.py` theme → `pydata_sphinx_theme`; add `sphinx.ext.napoleon` (missing) and keep `sphinx_copybutton`.
- [x] 7.2 Align `pyproject.toml` `docs` extra to `pydata-sphinx-theme` (add a `docs/requirements.txt` if absent listing the same); keep the Documentation URL pointing at upstream pyFRF docs (change #3 D6 — unchanged).
- [x] 7.3 Standardize `readthedocs.yaml` (ubuntu-24.04/py3.12).
- [x] 7.4 Remove the "A project template for the SDyPy effort.." module docstring from `sdypy/FRF/__init__.py`; replace with a real one-line description noting it re-exports pyFRF.
- [x] 7.5 Retarget the README badges from `ladisk/pyFRF` to the `sdypy-FRF` wrapper repository (CI badge → sdypy-FRF Actions; drop or fix the binder badge).
- [x] 7.6 Gate: `sphinx-build` from the clone succeeds; `check_docs.py --path .` exits 0.

## 8. sdypy-excitation docs

- [x] 8.1 Set `docs/source/conf.py` theme → `pydata_sphinx_theme` (currently `alabaster`); add `sphinx_copybutton`; fix `project` casing to a consistent form.
- [x] 8.2 Align `pyproject.toml` `docs` extra to `pydata-sphinx-theme` (add a `docs/requirements.txt` if absent); keep the Documentation URL pointing at upstream pyExSi docs (unchanged).
- [x] 8.3 Standardize `readthedocs.yaml` (ubuntu-24.04/py3.12).
- [x] 8.4 Remove the "A project template for the SDyPy effort.." module docstring from `sdypy/excitation/__init__.py`; replace with a real one-line description.
- [x] 8.5 Fix the README tagline (currently "Frequency response function as used in structural dynamics." — the FRF description) to describe excitation-signal generation.
- [x] 8.6 Gate: `sphinx-build` from the clone succeeds; `check_docs.py --path .` exits 0.

## 9. sdypy-view docs

- [x] 9.1 Set `docs/source/conf.py` theme → `pydata_sphinx_theme` (currently `alabaster`); keep `sphinx_copybutton`, napoleon; add `autodoc_mock_imports = ["PyQt6", "pyvistaqt"]` so autodoc builds without Qt.
- [x] 9.2 Align `pyproject.toml` `docs` extra to `pydata-sphinx-theme` (add a `docs/requirements.txt` if absent).
- [x] 9.3 Standardize `readthedocs.yaml` (ubuntu-24.04/py3.12).
- [x] 9.4 Change the `[project.urls]` Documentation from the GitHub homepage to `https://sdypy-view.readthedocs.io/en/latest/index.html`.
- [x] 9.5 Replace the empty `docs/source/code.rst` stub with active `.. automodule:: sdypy.view` (or `autoclass` for `Plotter3D` + the helper functions from `__all__`).
- [x] 9.6 Remove the sphinx-quickstart template comment from `docs/source/index.rst`.
- [x] 9.7 Gate: `sphinx-build` from the clone succeeds WITHOUT PyQt6 installed; `check_docs.py --path .` exits 0.

## 10. sdypy-model docs

- [x] 10.1 Convert `README.md` → `README.rst` (preserve the Beam/Shell/Tetrahedron sections + disclaimer; translate Markdown to reStructuredText).
- [x] 10.2 Fix `docs/source/getting_started.rst` `.. include:: ../../README.rst` (now resolves correctly after 10.1); remove any `.md`-specific handling.
- [x] 10.3 Set `docs/source/conf.py` theme → `pydata_sphinx_theme`; revert `source_suffix` to `.rst`-only (drop the `.md`→restructuredtext mapping); drop `myst_parser` from extensions; keep mathjax/autodoc/copybutton.
- [x] 10.4 Align `pyproject.toml` `docs` extra and `docs/requirements.txt` to `pydata-sphinx-theme` (drop `sphinx-book-theme` and `myst-parser`).
- [x] 10.5 Standardize `readthedocs.yaml` (already ubuntu-24.04/py3.12 — confirm it matches the canonical shape exactly).
- [x] 10.6 Add a `[project.urls]` Documentation key → `https://sdypy-model.readthedocs.io/en/latest/index.html`.
- [x] 10.7 Replace the empty `docs/source/code.rst` stub with active `.. autoclass::` directives for `Beam`, `Shell`, `Tetrahedron`, `solve_eigenvalue` (the `__all__` public API).
- [x] 10.8 Gate: `sphinx-build` from the clone succeeds; `check_docs.py --path .` exits 0.

## 11. Verification

- [x] 11.1 Run `python tools/check_docs.py --path .` for the core repo and `python C:\Users\jasas\Work\OpenSource\SdyPy\sdypy\tools\check_docs.py --path <clone>` for all six siblings; confirm all seven exit 0.
- [x] 11.2 Build the core umbrella docs (`python docs/seps/tools/build_index.py` then `sphinx-build -b html docs/source docs/_build/html` from the core repo) and confirm: build succeeds, the SEP index includes SEP 0005, and no "document isn't included in any toctree" warning is emitted for any `dev/` page.
- [x] 11.3 Build each sibling's docs (`sphinx-build -b html docs/source docs/_build/html` from each clone) and confirm all six succeed (view without PyQt6).
- [x] 11.4 Run `openspec validate establish-docs-website --strict` from the core repo and confirm no errors.
- [ ] 11.5 (Post-push, maintainer infra — NOT done here) Register `sdypy-FRF`, `sdypy-excitation`, `sdypy-view` on readthedocs.io; trigger a rebuild of the stale `sdypy-model` RTD site; decide the `sdypy.org` domain. Record as deferred.
