## MODIFIED Requirements

### Requirement: Umbrella exposes sep005 as a facade alias
The `sdypy` umbrella SHALL expose `sep005` as an attribute that resolves, lazily on first access, to the validator module `sdypy_sep005.sep005` of the installed `sdypy_sep005` distribution (the package `__init__` holds only `__version__`). The alias MUST be defined separately from the first-level sub-package mechanism (`_SUBPACKAGES`), because `sdypy_sep005` is a standalone top-level module and not a `sdypy.sep005` namespace portion. Accessing `sep005` MUST NOT attempt to import a non-existent `sdypy.sep005` module.

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
