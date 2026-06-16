## Context

The 2026-06-12 docs audits established the current state.

**Core** (`docs/`) is two disconnected Sphinx projects:
- `docs/source/` — the RTD-built umbrella. Clean-ish `conf.py` (project "SDyPy - Structural Dynamics Scientific Python", `sphinx_rtd_theme`, autodoc/viewcode/napoleon, dynamic version) but: `sphinx-copybutton` is in the `docs` extra yet never enabled; no intersphinx; LaTeX/man titles say lowercase "sdypy project"; `code.rst` autodoc is commented out; the whole `dev/` subtree (contributing, governance, governance_people, code_of_conduct, pep8, readme.dev) is orphaned from the toctree; `index.rst` links EMA/io to external RTD URLs but never wires view/model; `getting_started.rst` just includes README+CONTRIBUTING.
- `docs/seps/` — a standalone Sphinx project with a proper `build_index.py`+Jinja2 generator (`index.rst.tmpl`, validates SEP headers, statuses) that **RTD never runs**. Its `conf.py` is NumPy-branded throughout (numpy logo/Twitter/GitHub, htmlhelp basenames, LaTeX/man/texinfo titles "NumPy Enhancement Proposals", intersphinx to numpy/scipy). `scope.rst` (36 lines) and `roadmap.rst` (47 lines) have **real content** (the earlier "empty" note was wrong); roadmap has a couple of bodyless subsections. The umbrella renders SEPs instead via `docs/source/SEPs.rst` manually `.. include::`-ing seps 0000–0004 (misses 0005).

**Foreign residue**: `docs/source/building/{index,linux,windows,macosx,faq}.rst` are entirely SciPy/NumPy build instructions (`:orphan:` but still compiled). SEP 0 footnotes/links point at the numpy mailing list and neps. governance.rst/code_of_conduct.rst are SciPy-derived with intentional acknowledgements (keep those, reword stray "SciPy umbrella"/"SciPy work" prose).

**Website**: none. `sdypy.github.io` 404s, `sdypy.org` does not resolve, only `sdypy.readthedocs.io` is live (built from `docs/source/`). `roadmap.rst` links a dead `www.sdypy.org/devdocs`.

**Siblings** diverge badly:
- Themes: `sphinx_book_theme` (EMA, model), `sphinx_rtd_theme` (io, FRF), `alabaster` (excitation, view).
- README: `.rst` ×5, `.md` ×1 (model).
- RTD live: EMA, io, model (model stale at 0.1.4). 404: FRF, excitation, view.
- Documentation URL: own RTD (EMA, io); upstream backend (FRF→pyFRF, excitation→pyExSi, intentional per change #3 D6); GitHub homepage (view); none (model).
- `docs` extra vs `conf.py` theme mismatch in EMA/excitation/view; `napoleon` missing in FRF.
- Bugs: template module docstring "A project template for the SDyPy effort.." in io/FRF/excitation `__init__.py`; excitation README tagline copy-pasted from FRF; EMA `|pytest|` badge target `sdypa-EMA` (typo); FRF badges point at upstream `ladisk/pyFRF`; model `source_suffix` maps `.md`→`restructuredtext` (wrong); model `getting_started.rst` `.. include:: ../../README.rst` but file is `README.md`; empty `code.rst` autodoc stubs in view/model; io `sfmov.rst` uses bare `import pysfmov`; model `readthedocs.yaml` is ubuntu-24.04/py3.12 vs others ubuntu-22.04/py3.11.

Constraints: review model is "one big PR per repo + batched release at the end"; pending unreleased versions absorb doc changes (no new bumps). Sibling packaging/workflow files are governed by the change #3 template contract — this change touches docs files, `pyproject.toml` docs extra, `readthedocs.yaml`, READMEs, and (for docstring cleanup) `__init__.py`, but not the CI/release workflow files. RTD project registration and the domain need the maintainer's RTD/DNS access → deferred.

## Goals / Non-Goals

**Goals:**
- Zero foreign-project residue; the docs read as SDyPy throughout.
- One theme (`pydata-sphinx-theme`), one README format (`.rst`), one `readthedocs.yaml` shape across core + six.
- A coherent umbrella RTD site: real landing page, single toctree wiring dev + all six packages + a unified auto-generated SEP index.
- Autodoc actually wired for own-code packages (core, EMA already, view, model).
- Docs verified: a core docs-build CI job + a repo-layer `tools/check_docs.py`.

**Non-Goals:**
- A new website repo / GitHub Pages / the `sdypy.org` domain (decided: clean RTD umbrella only).
- Registering FRF/excitation/view on readthedocs.io, or rebuilding model's RTD (maintainer infra).
- Aggregating all six packages' docs into a single build (rejected: brittle).
- Touching the test/release workflows (change #5 / #8), shipped algorithmic code, or the `eigenvalue_solution.py` bug (separate code fix).
- Rich tutorials/examples beyond what exists (a coherent skeleton, not new pedagogy).

## Decisions

### D1: Theme = pydata-sphinx-theme everywhere; docs extras aligned

Every `conf.py` (core `docs/source`, core `docs/seps`, and all six siblings) sets `html_theme = "pydata_sphinx_theme"`. Each package's `[project.optional-dependencies] docs` extra and `docs/requirements.txt` list `pydata-sphinx-theme` + `sphinx` + `sphinx-copybutton`, dropping `sphinx-rtd-theme`/`sphinx-book-theme`/implicit-alabaster. `sphinx-copybutton` is enabled in every `conf.py` extensions list (it was already in the extra). `napoleon` is added to FRF (and confirmed present elsewhere). A minimal shared `html_theme_options` (logo text/navbar, github link) gives a consistent look; the core umbrella additionally gets navbar links to the six package RTD sites.

*Why pydata over book/rtd?* It is the scientific-Python ecosystem standard (NumPy/SciPy/pandas) and best fits an umbrella landing page with a top navbar linking out to member packages — the chosen "clean RTD umbrella" architecture. EMA/model (book theme, built on pydata) migrate most easily.

### D2: README = reStructuredText everywhere; common skeleton

`sdypy-model`'s `README.md` is converted to `README.rst` (content preserved; element-type sections kept). With no remaining `.md` docs, model drops `myst-parser` from its docs extra and its `source_suffix` reverts to `.rst`-only (killing the parser-mapping bug). All seven READMEs follow a common skeleton — H1 title, badge row, one-line description, Installation, Basic usage, and (for the core) the package-integration table. Fixes folded in: excitation's tagline (currently the FRF description) rewritten for excitation; EMA's `sdypa-EMA` badge typo → `sdypy-EMA`; FRF's CI/binder badges retargeted from `ladisk/pyFRF` to the sdypy wrapper repo. README badges are advisory in count but must not be broken or point at the wrong project.

### D3: Umbrella site = clean RTD, one toctree, unified SEP index

`docs/source/index.rst` becomes a real landing page (mission, install snippet, package table) with a single coherent toctree:
- **Getting started** (install + quickstart),
- **Packages** — a page linking each of the six to its own RTD site (EMA/io/view/model own sites; FRF/excitation to upstream backend docs, consistent with their Documentation URL),
- **SEPs** — the unified auto-generated index,
- **Development** — the now-wired `dev/` pages (contributing, governance, code_of_conduct, pep8; `governance_people` linked, `readme.dev` updated to drop dead `.travis.yml`/`setup.py`/`requirements.dev.txt` references).

**SEP unification**: retire `docs/source/SEPs.rst`'s manual include list. The `docs/seps/` generator (`build_index.py`) becomes the single source — run it as part of the RTD build so the SEP index (all SEPs incl. 0005, with statuses) is always current. Mechanism: a small RTD `build.jobs.pre_build` step (or a sphinx `conf.py` hook in `docs/source`) invokes `build_index.py` and surfaces the generated SEP tree under the umbrella toctree, so one RTD build produces the whole site including SEPs. `docs/seps/conf.py` is de-NumPy'd (it still supports a standalone `make html` for SEP authors, but RTD uses the integrated path). `roadmap.rst`'s bodyless subsections are filled; the dead `www.sdypy.org/devdocs` link is removed/replaced.

*Why integrate rather than keep two builds?* A single RTD build that includes SEPs is the "unified site" the roadmap asks for and removes the silent drift where the published SEPs lag the source. The standalone SEP Makefile is kept as a convenience but is no longer the only path.

### D4: Autodoc wired for own-code packages

Core `docs/source/code.rst` (commented-out block), `sdypy-view`'s empty `code.rst`, and `sdypy-model`'s empty `code.rst` get real `.. automodule::` / `.. autoclass::` directives over the curated public API (`__all__` from change #4). EMA already has working autodoc — left as-is (it documents `Model`, `tools`, etc.). io/FRF/excitation are namespace shims with no own classes — they keep hand-written showcase pages (io) or upstream-pointing index stubs (FRF/excitation); no autodoc is forced on them. The autodoc pages must import cleanly under the docs build (a packages-with-heavy-optional-backends caveat: view's pyvista/Qt import is guarded; autodoc uses `autodoc_mock_imports` for PyQt6 if needed).

### D5: Standardized readthedocs.yaml + per-package Documentation URLs

All seven `readthedocs.yaml` use one shape: `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python: "3.12"`, `sphinx.configuration: docs/source/conf.py`, `python.install: pip . [docs]`. (Standardize up to model's newer 24.04/3.12 rather than the older majority — forward-looking, matches the supported matrix top end.) Documentation URLs in `pyproject.toml`: EMA/io keep own RTD; **view** switches from its GitHub homepage to `https://sdypy-view.readthedocs.io/...`; **model** gains a Documentation URL (`https://sdypy-model.readthedocs.io/...`); **FRF/excitation** keep upstream backend docs (change #3 D6). These URLs presume RTD registration, which is deferred maintainer infra — the metadata is set correctly now so it's right the moment the projects are registered.

### D6: Conformance = core docs-build CI job + repo-layer checker

- **Build job**: a new core `.github/workflows/docs.yml` runs `pip install .[docs]` then `sphinx-build -b html docs/source docs/_build/html` and fails on build error. (Warnings-as-errors `-W` is **not** enabled initially — the existing tree has benign warnings; tightening to `-W` is a follow-up once clean.) It also runs `build_index.py` so the SEP integration is exercised. Siblings rely on their own RTD builds + the checker (their CI workflow files are not touched, per change #3 contract).
- **Checker**: `tools/check_docs.py --path <clone>` asserts, per repo: `conf.py` sets `pydata_sphinx_theme`; README is `README.rst`; the `docs` extra lists `pydata-sphinx-theme` and not a competing theme; no foreign-project residue strings (`numpy`/`scipy`/"project template for the SDyPy effort") outside an allowlist of intentional acknowledgements; the `[project.urls]` Documentation target matches the package's class (own-RTD vs upstream-backend). Kept separate from `check_sibling_template.py` and `check_public_api.py`.

*Why no heavy per-sibling docs-build in core CI?* Cross-repo builds are the rejected aggregation pattern; each sibling's RTD already builds it, and the checker catches the static invariants cheaply.

### D7: No new version bumps

Docs, README, and `readthedocs.yaml` ship in the sdist (template allow-list includes `docs/`), and the module-docstring cleanup touches `__init__.py` (shipped). But the pending versions (EMA 0.30.0, io 0.4.0, FRF/excitation/view/model 0.2.0) are unreleased, so these fold in — same rule as change #5. No `pyproject` version field changes.

## Risks / Trade-offs

- [pydata theme migration breaks an existing conf.py option] → each package's docs build is a gate during implementation (`sphinx-build` must succeed); pydata is a drop-in for book/rtd for basic usage.
- [Deleting `docs/source/building/` removes a real (if foreign) page someone linked] → it is `:orphan:` SciPy content with no SDyPy value; the package-integration story lives in README/landing. Acceptable break.
- [SEP `build_index.py` RTD integration is fiddly] → fallback: keep the standalone SEP build and, if the `pre_build` hook proves unreliable on RTD, commit the generated SEP index and wire it statically into the umbrella toctree (documented in tasks).
- [autodoc imports fail for view (Qt) under the docs builder] → `autodoc_mock_imports = ["PyQt6"]` (and pyvistaqt if needed); the public helpers/`Plotter3D` signature still document.
- [Documentation URLs point at not-yet-registered RTD projects] → correct-but-pending; flagged as maintainer infra; the checker validates the *target shape*, not live reachability.
- [check_docs residue scan false-positives on legitimate acknowledgements] → explicit allowlist (governance/CoC "adapted from SciPy" lines, example code `import numpy as np`).

## Migration Plan

1. Core: strip residue (delete building/, de-NumPy SEP conf.py, fix footnotes/links), theme+copybutton+autodoc in conf.py, landing page + unified toctree + SEP integration, fill roadmap, docs extra → pydata, standardized readthedocs.yaml, `docs.yml` + `check_docs.py`. Gate: `sphinx-build` succeeds; `check_docs.py --path .` green.
2. Six siblings (parallel): theme → pydata + extra/requirements aligned, README cleanup (model `.md`→`.rst`), autodoc in view/model `code.rst`, module-docstring cleanup, doc-URL + readthedocs.yaml fixes. Per-sibling gate: `sphinx-build` succeeds locally + `check_docs.py --path <clone>` green.
3. Push order: siblings then core (so the umbrella's outbound links resolve), per the established forks workflow.
4. Rollback: docs/config/README files are additive or self-contained; revert per repo.

## Open Questions

All resolved by the project lead on 2026-06-12 (team can revisit at the final review):
- **Site architecture** → clean RTD umbrella (`sdypy.readthedocs.io`); no new site repo, domain deferred.
- **Theme** → `pydata-sphinx-theme` across core + six.
- **README format** → reStructuredText everywhere (convert model).
- Carried forward (not re-asked): FRF/excitation Documentation URLs stay upstream (change #3 D6); RTD project registration + domain are deferred maintainer infra.
