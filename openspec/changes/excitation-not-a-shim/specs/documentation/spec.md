## MODIFIED Requirements

### Requirement: Autodoc wired for own-code packages

The `code.rst` autodoc page in the core umbrella, `sdypy-view`, `sdypy-model`, `sdypy-FRF` and `sdypy-excitation` SHALL contain real `.. automodule::` or `.. autoclass::` directives covering the curated public API. `sdypy-view`'s `conf.py` SHALL declare `autodoc_mock_imports` for `PyQt6` (and `pyvistaqt` if needed) so the docs build succeeds without Qt. Only the namespace package `io` is not required to add autodoc.

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

#### Scenario: sdypy-excitation is not exempt from autodoc
- **WHEN** `docs/source/code.rst` in the `sdypy-excitation` clone is read
- **THEN** it contains at least one uncommented `.. automodule::` or `.. autoclass::` directive covering the curated excitation API
