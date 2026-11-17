## MODIFIED Requirements

### Requirement: Every first-level package declares an explicit `__all__`
Every first-level sdypy namespace package (`sdypy.EMA`, `sdypy.io`, `sdypy.FRF`, `sdypy.excitation`, `sdypy.view`, `sdypy.model`) SHALL declare a non-empty `__all__` list in its `sdypy/<pkg>/__init__.py`. Every name in `__all__` MUST resolve via `getattr` on the module object after import.

#### Scenario: `__all__` present and non-empty in each first-level package
- **WHEN** each of the six first-level packages is imported (`import sdypy.EMA`, `import sdypy.io`, `import sdypy.FRF`, `import sdypy.excitation`, `import sdypy.view`, `import sdypy.model`)
- **THEN** each module has an `__all__` attribute that is a non-empty list

#### Scenario: Every `__all__` entry resolves via getattr
- **WHEN** each of the six first-level packages is imported and `getattr(module, name)` is called for every name in `module.__all__`
- **THEN** no `AttributeError` is raised for any entry in any of the six packages

#### Scenario: Curated names match the design-specified lists
- **WHEN** the `__all__` of each package is inspected after import
- **THEN** `sdypy.EMA.__all__` contains exactly `["Model", "ModelPoly", "MAC", "MSF", "MCF", "complex_freq_to_freq_and_damp", "stabilization", "normal_modes", "pole_picking"]`
- **AND** `sdypy.io.__all__` contains exactly `["uff", "lvm", "mraw", "sfmov"]`
- **AND** `sdypy.FRF.__all__` contains exactly `["FRF", "assert_sep005", "direction_dict"]`
- **AND** `sdypy.excitation.__all__` contains exactly `["burst_random", "get_kurtosis", "get_psd", "impulse", "nonstationary_signal", "normal_random", "pseudo_random", "random_gaussian", "sine_sweep", "stationary_nongaussian_signal", "uniform_random"]`
- **AND** `sdypy.view.__all__` contains exactly `["Plotter3D", "create_fem_mesh", "prepare_animation_displacements", "prepare_animation_field", "copy_image_to_clipboard"]`
- **AND** `sdypy.model.__all__` contains exactly `["Beam", "Shell", "Tetrahedron", "solve_eigenvalue", "lumped", "mesh"]`
