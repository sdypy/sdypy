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

#### Scenario: Template docstring removed from shim packages
- **WHEN** the `__init__.py` of `sdypy-io`, `sdypy-FRF`, and `sdypy-excitation` are read
- **THEN** none contains the text "A project template for the SDyPy effort"

#### Scenario: Allowlist exempts intentional acknowledgements
- **WHEN** `tools/check_docs.py --path <core>` is run
- **THEN** lines in governance.rst or code_of_conduct.rst that read "adapted from SciPy" do not trigger a residue failure
- **AND** example code containing `import numpy as np` in tutorial or usage pages does not trigger a residue failure

### Requirement: Autodoc wired for own-code packages

The `code.rst` autodoc page in the core umbrella, `sdypy-view`, `sdypy-model`, and `sdypy-FRF` SHALL contain real `.. automodule::` or `.. autoclass::` directives covering the curated public API. The commented-out autodoc block in core `docs/source/code.rst` MUST be replaced with active directives. `sdypy-view`'s `conf.py` SHALL declare `autodoc_mock_imports` for `PyQt6` (and `pyvistaqt` if needed) so the docs build succeeds without a Qt installation. The namespace packages `io` and `excitation` are NOT required to add autodoc. `FRF` holds its own code and is required to.

#### Scenario: Core code.rst contains active automodule directives
- **WHEN** `docs/source/code.rst` in the core repo is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive

#### Scenario: sdypy-view docs build succeeds without Qt
- **WHEN** `sphinx-build -b html docs/source docs/_build/html` is run in the `sdypy-view` clone without PyQt6 installed
- **THEN** the build completes without an ImportError

#### Scenario: sdypy-model code.rst contains active autodoc directives
- **WHEN** `docs/source/code.rst` in the `sdypy-model` clone is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive

#### Scenario: sdypy-FRF is not exempt from autodoc
- **WHEN** `docs/source/code.rst` in the `sdypy-FRF` clone is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive covering the curated FRF API
