## RENAMED Requirements

- FROM: `### Requirement: Umbrella `__all__` matches the six first-level names`
- TO: `### Requirement: Umbrella `__all__` is the six first-level names plus the sep005 alias`

## MODIFIED Requirements

### Requirement: Umbrella `__all__` is the six first-level names plus the sep005 alias
`sdypy/__init__.py` SHALL declare an `__all__` whose members are exactly the six first-level sub-package names `EMA`, `io`, `FRF`, `excitation`, `model`, `view` together with the `sep005` alias — seven names, no others. The umbrella's `__dir__` implementation MUST return a list that includes all seven names (consistent with the lazy facade), and the `__all__` content MUST exactly match that set.

`sep005` is not a first-level name and not a `sdypy.*` namespace portion: it is the facade alias to the standalone `sdypy_sep005` distribution (the SEP 5 unified-timeseries standard), surfaced on the umbrella for discoverability. Its presence in `__all__` is therefore governed jointly by this requirement and by the `sep005-standard` capability, which owns the alias's resolution target and its rationale.

#### Scenario: Umbrella `__all__` lists exactly the six first-level names
- **WHEN** `import sdypy` is run and `sdypy.__all__` is inspected
- **THEN** exactly six first-level names are present — `EMA`, `io`, `FRF`, `excitation`, `model`, `view` — and no seventh sub-package name
- **AND** the only further member is the `sep005` alias, so the list equals `["EMA", "io", "FRF", "excitation", "model", "view", "sep005"]` (order may vary)

#### Scenario: `from sdypy import *` imports all six subpackages
- **WHEN** a user runs `from sdypy import *` in a fresh namespace
- **THEN** `EMA`, `io`, `FRF`, `excitation`, `model` and `view` are all present in that namespace
- **AND** `sep005` is present alongside them, because the star-import resolves every member of `__all__` through the lazy `__getattr__`

#### Scenario: Umbrella `__dir__` is consistent with `__all__`
- **WHEN** `dir(sdypy)` is called after `import sdypy`
- **THEN** all seven names `"EMA"`, `"io"`, `"FRF"`, `"excitation"`, `"model"`, `"view"`, `"sep005"` appear in the result
