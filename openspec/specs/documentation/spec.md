# documentation Specification

## Purpose
The contract for the `sdypy` umbrella documentation: a unified pydata-Sphinx site free of foreign-project residue, a reStructuredText README, a landing page and unified toctree, autodoc for own-code packages, unified SEP rendering via `build_index.py`, a standardised `readthedocs.yaml`, and a docs conformance checker with a CI job. Established by the `establish-docs-website` change.

**Scope:** Umbrella-local — the `sdypy` umbrella documentation site and its build.

## Requirements
### Requirement: No foreign-project residue

The core repository SHALL contain no SciPy or NumPy artefacts that were never adapted for SDyPy. Specifically: the `docs/source/building/` subtree (files `index.rst`, `linux.rst`, `windows.rst`, `macosx.rst`, `faq.rst`) MUST be deleted; `docs/seps/conf.py` MUST NOT reference NumPy-branded assets (`numpylogo.svg`, NumPy GitHub/Twitter URLs, `htmlhelp_basename`, LaTeX/man/texinfo titles reading "NumPy Enhancement Proposals", or intersphinx mappings to `numpy`/`scipy`); `sep-0000.rst` footnotes and links MUST point at SDyPy resources rather than the NumPy mailing list or NEPs; the dead `www.sdypy.org/devdocs` link in `roadmap.rst` MUST be removed; the `ttps://` clone-URL typo in `dev/contributing.rst` MUST be corrected; and the `__init__.py` module docstring "A project template for the SDyPy effort…" MUST be removed from `sdypy-io`, `sdypy-FRF`, and `sdypy-excitation`. Governance and CoC prose that intentionally acknowledges SciPy origin SHALL be preserved; an allowlist MUST cover these acknowledgements and example code such as `import numpy as np` so the conformance checker does not flag them as residue.

#### Scenario: Building subtree deleted
- **WHEN** the core repository file tree is inspected
- **THEN** none of `docs/source/building/index.rst`, `docs/source/building/linux.rst`, `docs/source/building/windows.rst`, `docs/source/building/macosx.rst`, `docs/source/building/faq.rst` exist

#### Scenario: SEP conf.py contains no NumPy branding
- **WHEN** `docs/seps/conf.py` is read
- **THEN** it contains no reference to `numpylogo`, NumPy GitHub or Twitter URLs, `htmlhelp_basename` set to a NumPy value, or intersphinx keys for `numpy` or `scipy`

#### Scenario: SEP 0 footnotes point at SDyPy
- **WHEN** `docs/seps/sep-0000.rst` is read
- **THEN** no footnote or hyperlink target points at the NumPy mailing list or the NumPy Enhancement Proposals (NEPs) site

#### Scenario: Template docstring removed from shim packages
- **WHEN** the `__init__.py` of `sdypy-io`, `sdypy-FRF`, and `sdypy-excitation` are read
- **THEN** none contains the text "A project template for the SDyPy effort"

#### Scenario: Allowlist exempts intentional acknowledgements
- **WHEN** `tools/check_docs.py --path <core>` is run
- **THEN** lines in governance.rst or code_of_conduct.rst that read "adapted from SciPy" do not trigger a residue failure
- **AND** example code containing `import numpy as np` in tutorial or usage pages does not trigger a residue failure

### Requirement: Unified Sphinx theme

Every `conf.py` in the core umbrella (`docs/source/conf.py`, `docs/seps/conf.py`) and in each of the six sibling packages SHALL set `html_theme = "pydata_sphinx_theme"`. Every `conf.py` SHALL include `"sphinx_copybutton"` in its `extensions` list. `sphinx.ext.napoleon` SHALL be present in the FRF `conf.py` extensions list (and confirmed present in all others that document APIs).

#### Scenario: Core source conf.py uses pydata theme with copybutton
- **WHEN** `docs/source/conf.py` in the core repo is read
- **THEN** `html_theme` equals `"pydata_sphinx_theme"`
- **AND** `"sphinx_copybutton"` appears in `extensions`

#### Scenario: SEP conf.py uses pydata theme
- **WHEN** `docs/seps/conf.py` is read
- **THEN** `html_theme` equals `"pydata_sphinx_theme"`

#### Scenario: All six sibling conf.py files use pydata theme with copybutton
- **WHEN** `docs/source/conf.py` of each sibling (`EMA`, `io`, `FRF`, `excitation`, `view`, `model`) is read
- **THEN** `html_theme` equals `"pydata_sphinx_theme"`
- **AND** `"sphinx_copybutton"` appears in `extensions`

#### Scenario: check_docs.py detects wrong theme
- **WHEN** `tools/check_docs.py --path <sibling>` is run on a sibling whose `conf.py` still sets `html_theme = "sphinx_rtd_theme"`
- **THEN** the script exits non-zero and reports the theme mismatch

### Requirement: Docs extras and requirements aligned with theme

Each package's `[project.optional-dependencies]` `docs` extra in `pyproject.toml` and its `docs/requirements.txt` SHALL list `pydata-sphinx-theme`, `sphinx`, and `sphinx-copybutton`. No competing theme package (`sphinx-rtd-theme`, `sphinx-book-theme`, or implicit `alabaster`) SHALL appear in those lists. `sdypy-model` SHALL additionally drop `myst-parser` from its docs extra once `README.md` is converted to `README.rst`.

#### Scenario: Core docs extra lists pydata theme
- **WHEN** the `[project.optional-dependencies]` `docs` group in the core `pyproject.toml` is read
- **THEN** it contains `pydata-sphinx-theme`
- **AND** it does not contain `sphinx-rtd-theme` or `sphinx-book-theme`

#### Scenario: Sibling docs extra and requirements.txt match theme
- **WHEN** the `docs` extra in a sibling's `pyproject.toml` and its `docs/requirements.txt` are read
- **THEN** both list `pydata-sphinx-theme` and neither lists `sphinx-rtd-theme`, `sphinx-book-theme`, or `myst-parser` (for model, after README conversion)

#### Scenario: check_docs.py detects extra/theme mismatch
- **WHEN** `tools/check_docs.py --path <sibling>` is run on a repo whose docs extra lists `sphinx-book-theme` while `conf.py` sets `pydata_sphinx_theme`
- **THEN** the script exits non-zero and reports the mismatch

### Requirement: README standardised as reStructuredText

Every repository's README SHALL be named `README.rst`. `sdypy-model`'s `README.md` MUST be converted to `README.rst` (content preserved). Every README SHALL follow a common skeleton: H1 title, badge row, one-line description, Installation section, and Basic usage section. Badges MUST NOT be broken or target the wrong project: the excitation README tagline MUST describe `sdypy-excitation` (not `sdypy-FRF`); the EMA `|pytest|` badge target MUST read `sdypy-EMA` (not `sdypa-EMA`); and FRF's CI and binder badges MUST target the `sdypy-FRF` wrapper repository rather than `ladisk/pyFRF`.

#### Scenario: All READMEs are .rst files
- **WHEN** the root of each of the seven repositories (core + six siblings) is listed
- **THEN** a file named `README.rst` exists and no file named `README.md` exists

#### Scenario: Excitation tagline describes excitation not FRF
- **WHEN** `sdypy-excitation/README.rst` is read
- **THEN** the one-line description relates to excitation signal generation and does not describe FRF computation

#### Scenario: EMA badge target corrected
- **WHEN** `sdypy-EMA/README.rst` is read
- **THEN** the pytest badge target URL contains `sdypy-EMA` and not `sdypa-EMA`

#### Scenario: FRF badges target the wrapper repo
- **WHEN** `sdypy-FRF/README.rst` is read
- **THEN** the CI and binder badge URLs reference the `sdypy-FRF` repository rather than `ladisk/pyFRF`

#### Scenario: check_docs.py detects .md README
- **WHEN** `tools/check_docs.py --path <repo>` is run on a repository that has `README.md` but not `README.rst`
- **THEN** the script exits non-zero and reports the README format violation

### Requirement: Umbrella site landing page and unified toctree

The core `docs/source/index.rst` SHALL be a real landing page with a mission statement, install snippet, and package integration table. It SHALL contain a single coherent toctree wiring: a Getting started section (install and quickstart), a Packages page that links each of the six sibling packages to its documentation site, a SEPs section (the auto-generated index), and a Development section that explicitly includes the `dev/` pages (`contributing`, `governance`, `code_of_conduct`, `pep8`; `readme.dev` updated to drop dead references). No `dev/` page SHALL be orphaned from the toctree.

#### Scenario: Landing page exists with mission and install snippet
- **WHEN** `docs/source/index.rst` is rendered
- **THEN** it contains a mission statement for SDyPy, an install snippet, and a table or list linking the six sibling packages

#### Scenario: Dev pages are wired into the toctree
- **WHEN** `sphinx-build -b html docs/source docs/_build/html` is run on the core repo
- **THEN** no build warning of the form "document isn't included in any toctree" is emitted for any file under `docs/source/dev/`

#### Scenario: Packages page links all six siblings
- **WHEN** the Packages page in the rendered site is read
- **THEN** links to documentation sites for `EMA`, `io`, `FRF`, `excitation`, `view`, and `model` are all present

### Requirement: Unified SEP rendering via build_index.py

The `docs/seps/build_index.py` generator SHALL be the single source of truth for the SEP index, covering all SEPs including SEP 0005. It SHALL be invoked as part of the RTD build (via a `build.jobs.pre_build` step in `readthedocs.yaml` or a `conf.py` hook) so the rendered umbrella site always reflects the current SEP state. The manual `docs/source/SEPs.rst` include list (which manually `.. include::`s seps 0000–0004 and omits 0005) SHALL be retired and removed.

#### Scenario: SEP 0005 appears in the rendered SEP index
- **WHEN** `build_index.py` is run and the umbrella docs are built
- **THEN** the rendered SEP index page includes an entry for SEP 0005

#### Scenario: Manual SEPs.rst is removed
- **WHEN** the core repository file tree is inspected
- **THEN** `docs/source/SEPs.rst` does not exist

#### Scenario: RTD build invokes build_index.py
- **WHEN** the core `readthedocs.yaml` is read
- **THEN** it contains a `pre_build` or equivalent step that invokes `build_index.py`

### Requirement: Autodoc wired for own-code packages

The `code.rst` autodoc page in the core umbrella, `sdypy-view`, and `sdypy-model` SHALL contain real `.. automodule::` or `.. autoclass::` directives covering the curated public API. The commented-out autodoc block in core `docs/source/code.rst` MUST be replaced with active directives. `sdypy-view`'s `conf.py` SHALL declare `autodoc_mock_imports` for `PyQt6` (and `pyvistaqt` if needed) so the docs build succeeds without a Qt installation. The namespace shims `io`, `FRF`, and `excitation` are NOT required to add autodoc.

#### Scenario: Core code.rst contains active automodule directives
- **WHEN** `docs/source/code.rst` in the core repo is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive

#### Scenario: sdypy-view docs build succeeds without Qt
- **WHEN** `sphinx-build -b html docs/source docs/_build/html` is run in the `sdypy-view` clone without PyQt6 installed
- **THEN** the build completes without an ImportError

#### Scenario: sdypy-model code.rst contains active autodoc directives
- **WHEN** `docs/source/code.rst` in the `sdypy-model` clone is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive

### Requirement: Standardised readthedocs.yaml

All seven `readthedocs.yaml` files (core + six siblings) SHALL conform to one shape: `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python: "3.12"`, `sphinx.configuration: docs/source/conf.py`, and `python.install` using pip with the `docs` extra (`pip install .[docs]`). The Documentation URL in each package's `pyproject.toml` `[project.urls]` SHALL reflect the package's class: EMA and io keep their own RTD URLs; `sdypy-view` switches to `https://sdypy-view.readthedocs.io/`; `sdypy-model` gains a Documentation URL pointing at `https://sdypy-model.readthedocs.io/`; FRF and excitation retain their upstream backend documentation URLs per change #3 D6.

#### Scenario: Core readthedocs.yaml uses ubuntu-24.04 and Python 3.12
- **WHEN** the core `readthedocs.yaml` is read
- **THEN** `build.os` is `ubuntu-24.04`, `build.tools.python` is `"3.12"`, and `sphinx.configuration` is `docs/source/conf.py`

#### Scenario: All sibling readthedocs.yaml files share the standard shape
- **WHEN** `readthedocs.yaml` in each of the six sibling clones is read
- **THEN** each sets `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python: "3.12"`, and installs via `pip install .[docs]`

#### Scenario: sdypy-view Documentation URL points at own RTD
- **WHEN** `[project.urls]` in `sdypy-view/pyproject.toml` is read
- **THEN** the `Documentation` key value is `https://sdypy-view.readthedocs.io/` or equivalent own-RTD URL

#### Scenario: check_docs.py detects wrong Documentation URL class
- **WHEN** `tools/check_docs.py --path <sdypy-view>` is run on a `sdypy-view` clone whose Documentation URL still points at its GitHub homepage
- **THEN** the script exits non-zero and reports the URL class mismatch

### Requirement: Docs conformance checker and CI job

A script `tools/check_docs.py` SHALL exist in the core repository. When run as `python tools/check_docs.py --path <repo>` it SHALL assert, per repository: `conf.py` sets `pydata_sphinx_theme`; the README is `README.rst`; the `docs` extra lists `pydata-sphinx-theme` and not a competing theme; no foreign-project residue strings appear outside the allowlist; and the `[project.urls]` Documentation target matches the correct class for that package. A core `.github/workflows/docs.yml` CI job SHALL exist that installs `.[docs]`, invokes `build_index.py`, and runs `sphinx-build -b html docs/source docs/_build/html`; the job MUST fail on a Sphinx build error. The `-W` (warnings-as-errors) flag is NOT required initially.

#### Scenario: check_docs.py exits 0 on a conformant repo
- **WHEN** `python tools/check_docs.py --path <core>` is run after all changes in this spec are applied
- **THEN** the script exits with code 0 and reports no violations

#### Scenario: docs.yml CI job fails on Sphinx error
- **WHEN** a Sphinx build error is introduced (e.g., a broken directive) and the `docs.yml` workflow is triggered
- **THEN** the workflow step running `sphinx-build` exits non-zero and the job is marked failed

#### Scenario: check_docs.py is runnable on each sibling
- **WHEN** `python <core>/tools/check_docs.py --path <sibling>` is run on each of the six sibling clones after all changes are applied
- **THEN** each invocation exits with code 0

