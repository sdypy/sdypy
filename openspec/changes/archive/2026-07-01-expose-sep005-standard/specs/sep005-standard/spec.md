## Purpose
The contract for how the SEP 5 unified-timeseries standard is surfaced in SDyPy: the umbrella facade alias `sd.sep005` over the standalone `sdypy_sep005` distribution (explicitly NOT a `sdypy.sep005` namespace portion), its presence in the umbrella `__all__`/`__dir__`, its documentation, and the SEP 5 ratification path. Established by the `expose-sep005-standard` change.

## ADDED Requirements

### Requirement: Umbrella exposes sep005 as a facade alias
The `sdypy` umbrella SHALL expose `sep005` as an attribute that resolves, lazily on first access, to the installed `sdypy_sep005` distribution. The alias MUST be defined separately from the first-level sub-package mechanism (`_SUBPACKAGES`), because `sdypy_sep005` is a standalone top-level module and not a `sdypy.sep005` namespace portion. Accessing `sep005` MUST NOT attempt to import a non-existent `sdypy.sep005` module.

#### Scenario: sd.sep005 resolves to the sdypy_sep005 validator module
- **WHEN** a user runs `import sdypy as sd` and accesses `sd.sep005`
- **THEN** `sd.sep005` is the validator module of the `sdypy_sep005` distribution (identical to `importlib.import_module("sdypy_sep005.sep005")`, since the package `__init__` holds only `__version__`)
- **AND** `sd.sep005.assert_sep005` is callable

#### Scenario: sep005 access is lazy
- **WHEN** a fresh interpreter runs `import sdypy`
- **THEN** `sys.modules` contains no `sdypy_sep005` entry until `sdypy.sep005` is first accessed

#### Scenario: sep005 is not a namespace portion
- **WHEN** the alias resolution for `sep005` is inspected
- **THEN** it imports the top-level `sdypy_sep005` module and does not import or require a `sdypy.sep005` module
- **AND** `sep005` is not a member of the umbrella's `_SUBPACKAGES`

### Requirement: sep005 is listed in the umbrella public surface
The umbrella `__all__` SHALL include `sep005` in addition to the six first-level sub-package names, and `dir(sdypy)` SHALL include `sep005`. The umbrella `__all__` conformance test SHALL assert that `__all__` equals the six sub-package names plus the sep005 alias.

#### Scenario: sep005 appears in __all__ and __dir__
- **WHEN** `import sdypy` is run
- **THEN** `"sep005"` is in `sdypy.__all__`
- **AND** `"sep005"` is in `dir(sdypy)`

#### Scenario: from sdypy import * binds sep005
- **WHEN** a user runs `from sdypy import *` in a fresh namespace
- **THEN** `sep005` is present in that namespace alongside the six sub-packages

### Requirement: sep005 is documented as the SEP 5 standard
The SEP 5 standard and its `sd.sep005` access SHALL be documented: the README package listing and the documentation site's packages page MUST include a sep005 entry that identifies it as the unified-timeseries standard and compliance validator (the `sdypy_sep005` distribution), distinct from the six functional sub-packages, and note that `sdypy.FRF.assert_sep005` re-exports the validator.

#### Scenario: README documents sep005
- **WHEN** the core `README.rst` is read
- **THEN** it lists `sep005` as the SEP 5 unified-timeseries standard / compliance validator reachable as `sd.sep005`

#### Scenario: Docs packages page documents sep005
- **WHEN** the documentation packages page (`docs/source/packages.rst`) is read
- **THEN** it contains a sep005 entry describing the SEP 5 standard and linking the `sdypy-sep005` distribution and SEP 5

### Requirement: SEP 5 records its compliance package and ratification path
`docs/seps/sep-0005.rst` SHALL be updated to record that the compliance package called for by SEP 5 now exists (`sdypy-sep005`, exposed as `sd.sep005`), replacing the "a package ... is to be developed" wording, and SHALL be placed on the Draft → Accepted path. The actual `:Status:` change to Accepted (with a `:Resolution:`) is a gated team act and MAY remain pending after this change.

#### Scenario: SEP 5 references the existing compliance package
- **WHEN** `docs/seps/sep-0005.rst` is read after this change
- **THEN** it states that the compliance/validator package exists (`sdypy-sep005`, accessible as `sd.sep005`) rather than "to be developed"

#### Scenario: SEP 5 status flip is not forced by this change
- **WHEN** `docs/seps/sep-0005.rst` `:Status:` is inspected immediately after this change is applied
- **THEN** it MAY still read `Draft` (the flip to `Accepted` is a separate, team-gated act)
