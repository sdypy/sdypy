## Why

`sdypy.FRF.FRF` is pyFRF's `FRF` class, re-exported unchanged. Its public
surface names two FRF quantities with spellings that SEP 2 does not accept:

- The FRF estimator (`'H1'`, `'H2'`, `'Hv'`, `'ODS'`) is `frf_type` in the
  constructor and on the instance, and `type` in `get_FRF()`. `type` shadows
  the Python built-in, and `frf_type` is the spelling that `sdypy-EMA` used
  for the FRF form until it was renamed to `frf_form`. The same spelling means
  two different quantities on the EMA-to-FRF interop path.
- The FRF form (`'receptance'`, `'mobility'`, `'accelerance'`) is `form` in
  `get_FRF()`, while SEP 2's canonical name is `frf_form`.

SEP 2 excludes backend parameter names from its scope, and open PR #6 records
no canonical spelling for the estimator. Draft SEP 6 (PR #7) lists the
`frf_form` and `frf_estimator` renames as parked work. This change does that
work: it names the estimator `frf_estimator` and moves pyFRF to the canonical
names.

This is a non-trivial change: it adds a canonical name and renames public
parameters. It is also the first change that spans the hub and several
package repositories, which draft SEP 6 parks until a cross-repository
procedure exists. This change goes first on purpose, as a worked example for
SEP 6: the hub carries the specs, the SEP amendment and the task list, and
each package repository gets one linked pull request.

## What Changes

- **SEP 2 table**: add the row *FRF estimator* → `frf_estimator`, values
  `'H1'`, `'H2'`, `'Hv'`, `'ODS'`. ISO 7626 does not name this quantity, so
  the general guidelines govern (`frf_` prefix, same pattern as `frf_form`).
  ISO 18431-1's wording ("frequency response function of the first/second
  type") is recorded under "Relation to ISO 7626".
- **SEP 2 scope**: replace "Backend parameter names are out of scope" with a
  rule that binds re-exported backend objects. When a first-level package
  re-exports a backend class or function, that object's signature is part of
  the first-level public surface and follows SEP 2.
- **SEP 2 notes**: `frf_type`, `type` and `form` are context-dependent
  spellings (like `xi`). They are recorded in the notes below the table, not
  in the **Instead of** column, so the checker does not report every `type`
  or `form` parameter. This supersedes the paragraph that PR #6 adds.
- **pyFRF** (non-breaking, deprecated aliases through v1.x):
  - `FRF(frf_type=...)` → `FRF(frf_estimator=...)`, and the instance
    attribute `frf_type` → `frf_estimator`.
  - `get_FRF(type=..., form=...)` → `get_FRF(frf_estimator=..., frf_form=...)`.
  - The old keywords and the old attribute still work and emit
    `DeprecationWarning`. Positional calls do not change.
  - README, tutorial and showcase notebook use the new names. Release 1.5.0.
- **sdypy-FRF**: README and tests use the new names. Minimum pyFRF becomes
  1.5. Release 0.3.0.
- **sdypy-EMA**: `Model.add_frf()` changes from `get_FRF(form='receptance')`
  to a positional call, so it works with pyFRF before and after 1.5 without a
  warning. The public `LSFD`, `LSFD_proportional` and `LSFD_old` functions
  rename their `frf_type` parameter to `frf_form`, with a deprecated alias.
  The tutorial uses `frf_form=`. The changelog records the `frf_type` →
  `frf_form` rename. Release 0.31.0.
- **pyEMA**: the tutorial uses `frf_form=`. Its version follows sdypy-EMA
  (0.31.0). No code change: pyEMA re-exports sdypy-EMA.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `public-api`: a canonical name for the FRF estimator; SEP 2 binds the
  signatures of re-exported backend objects; context-dependent divergent
  spellings are recorded in the notes and verified by the owning package's
  tests; the rename inventory gains the pyFRF entries.

## Impact

- `sdypy`: `docs/seps/sep-0002.rst`, `REQUIREMENTS.md` (new rows, and the
  pending roster that today calls backend names out of scope),
  `tests/test_nomenclature.py` (pins that `type` and `form` are not enforced
  on sight), `tests/test_interop.py` (uses `get_FRF(type=...)` today).
  `tools/check_nomenclature.py`: only its docstring changes; `frf_type` →
  `frf_form` stays in its map.
- `pyFRF`: `pyFRF.py`, tests, `readme.rst`, `docs/source/tutorial.rst`,
  `Showcase.ipynb`, version.
- `sdypy-FRF`: `README.rst`, `tests/test_frf.py`, `pyproject.toml`, version.
- `sdypy-EMA`: `sdypy/EMA/EMA.py`, `docs/source/tutorial.rst`,
  `docs/source/changelog.rst`.
- `pyEMA`: `docs/source/tutorial.rst`, `pyEMA/__init__.py`, `pyproject.toml`.
- No behaviour changes. User code that passes the old keywords keeps working
  and gets a `DeprecationWarning`.
- PR #6 is superseded. Its author decides whether to close it or merge it
  first; this change adapts either way.
