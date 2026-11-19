## MODIFIED Requirements

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

#### Scenario: Template docstring removed from io, FRF and excitation
- **WHEN** the `__init__.py` of `sdypy-io`, `sdypy-FRF`, and `sdypy-excitation` are read
- **THEN** none contains the text "A project template for the SDyPy effort"

#### Scenario: Allowlist exempts intentional acknowledgements
- **WHEN** `tools/check_docs.py --path <core>` is run
- **THEN** lines in governance.rst or code_of_conduct.rst that read "adapted from SciPy" do not trigger a residue failure
- **AND** example code containing `import numpy as np` in tutorial or usage pages does not trigger a residue failure

### Requirement: Unified SEP rendering via build_index.py

The `docs/seps/tools/build_index.py` generator SHALL be the single source of truth for the SEP index, covering all SEPs including SEP 0005. It SHALL be invoked as part of the RTD build (via a `build.jobs.pre_build` step in `readthedocs.yaml` or a `conf.py` hook) so the rendered umbrella site always reflects the current SEP state. The manual `docs/source/SEPs.rst` include list (which manually `.. include::`s seps 0000–0004 and omits 0005) SHALL be retired and removed.

#### Scenario: SEP 0005 appears in the rendered SEP index
- **WHEN** `build_index.py` is run and the umbrella docs are built
- **THEN** the rendered SEP index page includes an entry for SEP 0005

#### Scenario: Manual SEPs.rst is removed
- **WHEN** the core repository file tree is inspected
- **THEN** `docs/source/SEPs.rst` does not exist

#### Scenario: RTD build invokes build_index.py
- **WHEN** the core `readthedocs.yaml` is read
- **THEN** it contains a `pre_build` or equivalent step that invokes `build_index.py`

### Requirement: Standardised readthedocs.yaml on the oldest supported Python

All seven `readthedocs.yaml` files (core + six siblings) SHALL conform to one shape: `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python` set to the oldest version of the supported set (`sibling-package-template` *Supported Python versions follow SPEC 0*), `sphinx.configuration: docs/source/conf.py`, and `python.install` using pip with the `docs` extra (`pip install .[docs]`). The Documentation URL in each package's `pyproject.toml` `[project.urls]` SHALL reflect the package's class: EMA and io keep their own RTD URLs; `sdypy-view` switches to `https://sdypy-view.readthedocs.io/`; `sdypy-model` gains a Documentation URL pointing at `https://sdypy-model.readthedocs.io/`; `sdypy-FRF` points at its own Read the Docs site, because it is a regular package; only the shim `sdypy-excitation`, which has no hosted documentation, keeps its backend's (pyExSi) documentation URL.

#### Scenario: Core readthedocs.yaml uses ubuntu-24.04 and the oldest supported Python
- **WHEN** the core `readthedocs.yaml` is read
- **THEN** `build.os` is `ubuntu-24.04`, `build.tools.python` is the oldest version of the supported set, and `sphinx.configuration` is `docs/source/conf.py`

#### Scenario: All sibling readthedocs.yaml files share the standard shape
- **WHEN** `readthedocs.yaml` in each of the six sibling clones is read
- **THEN** each sets `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python` to the oldest version of the supported set, and installs via `pip install .[docs]`

#### Scenario: A docs Python other than the oldest supported version is reported
- **WHEN** `python tools/check_sibling_template.py --path <sibling>` is run on a clone whose `readthedocs.yaml` sets `build.tools.python` to a version other than the oldest of the supported set
- **THEN** the checker reports the docs Python and exits non-zero

#### Scenario: sdypy-view Documentation URL points at own RTD
- **WHEN** `[project.urls]` in `sdypy-view/pyproject.toml` is read
- **THEN** the `Documentation` key value is `https://sdypy-view.readthedocs.io/` or equivalent own-RTD URL

#### Scenario: sdypy-FRF Documentation URL points at its own RTD
- **WHEN** `tools/check_docs.py --path <sdypy-FRF>` is run on a `sdypy-FRF` clone whose Documentation URL points at `pyfrf.readthedocs.io`
- **THEN** the script exits non-zero and reports that the Documentation URL must be the package's own readthedocs.io site

#### Scenario: check_docs.py detects wrong Documentation URL class
- **WHEN** `tools/check_docs.py --path <sdypy-view>` is run on a `sdypy-view` clone whose Documentation URL still points at its GitHub homepage
- **THEN** the script exits non-zero and reports the URL class mismatch
