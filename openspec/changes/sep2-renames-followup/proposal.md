## Why

sdypy-EMA 0.32.0 and sdypy-model 0.3.0 renamed public names and kept the old
ones as deprecated aliases. The `public-api` inventory of evidenced
divergences does not match what shipped: it says `pole_xi` → `damping_ratio`
(EMA shipped `pole_damping_ratio`) and `EI` → a matrix name (model shipped
`bending_stiffness`), and it lacks the model renames to table names.

## What Changes

- **`public-api`:** the inventory gains the model renames to SEP 2 table
  names: `A` → `mode_shape` (eigenvector attribute), `A` → `area`
  (cross-section) and `frequency` → `freq`. `pole_xi` and `EI` leave the
  inventory, because their new names are not table entries.
- The newly coined names (`pole_damping_ratio`, `frf_reconstructed`,
  `area_moment`, `bending_stiffness`, `jacobian`, `jacobian_det`,
  `shape_functions`, `greens_function`, `rotation_matrix`, `n_points`, ...)
  are not divergences from the table; they go to the SEP 2 pending-terms
  issue for the next amendment.
- **Tests:** `tests/test_interop.py` reads `natural_freq`, `damping_ratio`, `freq_lower` and `freq_upper`
  instead of the deprecated `nat_freq`, `nat_xi`, `lower` and `upper`.

Non-trivial: it changes a `public-api` requirement. No scenario changes.

## Impact

- `openspec/specs/public-api/spec.md` (one requirement, text only).
- `tests/test_interop.py`; needs `sdypy-EMA>=0.32.0`.
