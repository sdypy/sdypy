## Why

SDyPy's documentation is incoherent and partly belongs to another project: the core `docs/source/building/` subtree is verbatim *SciPy* build instructions, `docs/seps/conf.py` is NumPy-branded (logo, Twitter, GitHub URLs, LaTeX/man titles) and SEP 0's footnotes point at the NumPy mailing list. SEP rendering is forked (the umbrella manually `.. include::`s seps 0000–0004 and misses 0005, while the real `build_index.py` generator RTD never runs). Across the six siblings the docs diverge on three themes (book/rtd/alabaster), two README formats, and four different documentation-URL conventions, with three packages (FRF/excitation/view) not registered on Read the Docs at all and a scatter of bugs (template docstrings, a copy-pasted excitation tagline, model's `.md`→RST parser misconfiguration, model's `include README.rst` pointing at a `.md` file, an `sdypa` badge typo, empty `code.rst` autodoc stubs). For a trustworthy v1.0 the docs must read as one project.

## What Changes

- **Strip all foreign-project residue** from the core docs: delete the SciPy `docs/source/building/` subtree, de-NumPy `docs/seps/conf.py`, fix SEP 0's NumPy footnotes/links, remove dead `www.sdypy.org/devdocs` references and the `ttps://` clone-URL typo, and reword the remaining SciPy-derived governance/CoC prose to keep only the intentional "adapted from SciPy" acknowledgements.
- **Unify the Sphinx theme** on `pydata-sphinx-theme` across the core umbrella and all six siblings; align each `[project.optional-dependencies] docs` extra and `docs/requirements.txt` with that theme (removing the current extra-vs-conf.py mismatches) and enable `sphinx-copybutton` (already in the extra but never activated in core).
- **Standardize READMEs on reStructuredText**: convert `sdypy-model`'s `README.md` → `README.rst` (fixing its broken `include`), drop now-unneeded `myst-parser` from model's docs, and bring all READMEs to a common skeleton (title, badges, install, usage) — fixing the excitation tagline, the EMA `sdypa` badge typo, and pointing FRF's badges at the sdypy wrapper rather than upstream `ladisk/pyFRF`.
- **Build the unified RTD umbrella** (`sdypy.readthedocs.io`): a real landing page (mission, install, package table) with one coherent toctree that wires in the `dev/` pages (currently orphaned), all six packages, and the SEPs; **unify SEP rendering** on the `build_index.py` generator (auto-indexing all SEPs incl. 0005) run as part of the RTD build, retiring the manual `SEPs.rst` include list; fill the empty `roadmap.rst` placeholder subsections.
- **Wire autodoc** for packages with their own code: replace the empty `code.rst` stubs in `sdypy-view` and `sdypy-model` (and core's commented-out block) with real `automodule` directives over the curated public API.
- **Standardize `readthedocs.yaml`** to one shape (build OS/Python, install method, sphinx path) across core + six.
- **Add docs conformance**: a core docs-build CI job (`sphinx-build` must succeed) and a repo-layer `tools/check_docs.py` (theme is pydata, README is `.rst`, no foreign-project residue, docs-extra matches theme, documentation-URL target correct per package class).
- **No new version bumps**: docs/README live in the sdist but the pending unreleased versions (EMA 0.30.0, io 0.4.0, FRF/excitation/view/model 0.2.0) absorb these changes — same approach as change #5.

## Capabilities

### New Capabilities
- `documentation`: the documentation and website contract for the core umbrella and the six first-level packages — the no-foreign-residue rule, the unified `pydata-sphinx-theme` + `.rst` README standard, the umbrella RTD site structure (landing page, unified toctree wiring packages/SEPs/dev, auto-generated SEP index), the per-package docs baseline (conf.py shape, copybutton, autodoc for own-code packages, docs-extra/theme alignment, documentation-URL target by package class), the standardized `readthedocs.yaml`, and the conformance checks (core docs-build job + `tools/check_docs.py`).

### Modified Capabilities

<!-- none: the testing-ci capability (change #5) is untouched (a separate docs.yml job is added, the test workflow is not modified); namespace-packaging/distribution-packaging/public-api/sibling-package-template requirements are unchanged. README format was left advisory by the template change, so this is a new contract rather than a delta. -->

## Impact

- **Core repo**: delete `docs/source/building/`; rewrite `docs/source/conf.py` (theme, copybutton, intersphinx, autodoc, title casing) and `docs/seps/conf.py` (de-NumPy); new landing `index.rst` + toctree; unified SEP build (`build_index.py` wired into RTD); fill `roadmap.rst`; new `.github/workflows/docs.yml`; new `tools/check_docs.py`; `pyproject.toml` docs extra → pydata theme; standardized `readthedocs.yaml`; new `openspec/specs/documentation/spec.md`.
- **All six siblings**: `docs/source/conf.py` theme → pydata; `docs` extra + `docs/requirements.txt` aligned; `readthedocs.yaml` standardized; README cleanup (model `.md`→`.rst`); real autodoc in view/model `code.rst`; module-docstring cleanup in io/FRF/excitation `__init__.py`; doc-URL fixes (model gains a Documentation URL; view's points at its RTD; FRF/excitation stay upstream per change #3).
- **Users**: coherent, on-brand docs; `import`/API behavior unchanged. The module-docstring cleanup changes `__doc__` text only.
- **Deferred to maintainer (infra, like Actions enablement)**: registering `sdypy-FRF`/`sdypy-excitation`/`sdypy-view` projects on readthedocs.io; the `sdypy.org` domain / any GitHub Pages landing site; an RTD rebuild of the stale `sdypy-model` site. **Out of scope**: trusted publishing (#8), the v1.0 release (#8), sep005 exposure (#7), and the latent `eigenvalue_solution.py` scipy-`eigh` bug found in change #5 (a code fix, tracked separately).
