## 1. Core pytest config and pypi_artifacts markers

- [x] 1.1 Add `[tool.pytest.ini_options]` to `pyproject.toml` in the core repo: set `testpaths = ["tests"]` and register the marker `pypi_artifacts = "tests that fetch or assert PyPI-published artifact conformance"` under `markers`.
- [x] 1.2 Add `@pytest.mark.pypi_artifacts` to `test_published_sdist_has_no_stale_packaging` and `test_published_wheel_ships_only_own_portion` in `tests/test_namespace_conformance.py`. Add the same decorator to `test_sibling_ships_no_namespace_init` in the same file.
- [x] 1.3 Add `@pytest.mark.pypi_artifacts` to the five per-sibling parametrized test functions in `tests/test_public_api.py`: `test_subpackage_declares_nonempty_all`, `test_every_all_entry_resolves`, `test_no_banned_leak_names_in_all`, `test_module_entries_only_where_sanctioned`, `test_curated_surface_matches_spec`. Leave `test_umbrella_all_is_exactly_the_six_names`, the star-import test, and the drift advisory test unmarked.
- [x] 1.4 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest -m "not pypi_artifacts" --tb=short` from `C:\Users\jasas\Work\OpenSource\SdyPy\sdypy` and confirm all collected tests pass. Then run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest --collect-only` (no `-m` flag) and confirm the previously-marked tests still appear in the collected set.

## 2. Core GitHub Actions workflow rewrites

- [x] 2.1 Rewrite `.github/workflows/python-package.yml` in the core repo. Triggers: `push`, `pull_request`, `workflow_dispatch`. Matrix: `python-version: ["3.10", "3.11", "3.12"]` with `fail-fast: false`. Steps in order: `actions/checkout@v4`; `actions/setup-python@v5` with `python-version: ${{ matrix.python-version }}`; `pip install .`; `pip install pytest flake8 build`; two-pass flake8 (first pass `--count --select=E9,F63,F7,F82 --show-source --statistics`, second pass `--count --exit-zero --max-complexity=10 --max-line-length=127 --statistics`); `python -m pytest -m "not pypi_artifacts"`; `python -m build`.
- [x] 2.2 Rewrite `.github/workflows/release-and-publish-to-pypi.yml` in the core repo. Steps: `actions/checkout@v4`; `actions/setup-python@v5`; `pip install --upgrade pip build`; `python -m build`; `pypa/gh-action-pypi-publish@release/v1` with `password: ${{ secrets.PYPI_API_TOKEN }}`. Remove all `@v2`/`@v1.4.2` references.
- [x] 2.3 Confirm no sibling workflow file is touched — only the two files under `sdypy/.github/workflows/` are changed.

## 3. Core interop suite

- [x] 3.1 Create `tests/test_interop.py` in the core repo. Add the lumped→EMA test: instantiate a 2-DOF `sdypy.model.lumped.Model` with a fixed seed, call `get_FRF_matrix()` (returns shape `(n_dof, n_dof, n_freq)`), slice to `[input_dof, :, :]` to get `(n_outputs, n_freq)` for `sdypy.EMA.Model`, identify poles, assert identified natural frequencies within 2% rtol of `sdypy.model.lumped.Model.get_eig_freq()`. All imports via `sdypy.*` namespace only. No `pypi_artifacts` marker.
- [x] 3.2 Add the flagship end-to-end chain test to `test_interop.py`: `sdypy.excitation.pseudo_random` (fixed seed) → `sdypy.model.lumped.Model.get_response()` → `sdypy.FRF.FRF(exc, resp)` H1 estimate → `sdypy.EMA` identification → assert natural frequencies within 5% rtol of analytic. If H1-on-simulated-response is numerically unstable, fall back to averaging multiple noise realizations before relaxing tolerances; document the fixed seed in a comment.
- [x] 3.3 Add the io round-trip test to `test_interop.py`: prepare FRF data, build a dataset dict with `sdypy.io.uff.prepare_58(...)`, write it with `sdypy.io.uff.UFF(<path under pytest tmp_path>).write_sets(...)`, read back with `.read_sets()`, assert numeric equality with the original data. Use the pytest `tmp_path` fixture, not `tempfile.NamedTemporaryFile` (Windows cannot reopen an open NamedTemporaryFile).
- [x] 3.4 Add the sep005 smoke tests to `test_interop.py`: assert `sdypy.FRF.assert_sep005(valid_dict)` does not raise; assert `sdypy.FRF.assert_sep005(invalid_dict)` raises. No `pypi_artifacts` marker on any test in this file.

## 4. sdypy-FRF tests

- [x] 4.1 In `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-FRF\tests\`, create or extend `test_frf.py`. Add a test that constructs a synthetic SDOF response (fixed seed, known resonance frequency), instantiates `sdypy.FRF.FRF(sampling_freq, data)`, and asserts that the H1 magnitude peaks within a tolerance of the known resonance frequency. Add a test for `get_f_axis`: assert the returned array has the expected length and uniform spacing.
- [x] 4.2 Add `assert_sep005` tests to `test_frf.py`: construct a minimal valid sep005 dict and assert `sdypy.FRF.assert_sep005(valid)` does not raise; construct an invalid dict (missing required key or wrong type) and assert it raises.
- [x] 4.3 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-FRF\tests\ --tb=short` and confirm all new tests pass. Do NOT run from `C:\Users\jasas\Work\OpenSource\SdyPy\` as the folder shadows the package.

## 5. sdypy-excitation tests

- [x] 5.1 In `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-excitation\tests\`, create or extend `test_excitation.py`. For each of the eleven curated functions (`burst_random`, `get_kurtosis`, `get_psd`, `impulse`, `nonstationary_signal`, `normal_random`, `pseudo_random`, `random_gaussian`, `sine_sweep`, `stationary_nongaussian_signal`, `uniform_random`): assert the output shape and dtype are as documented.
- [x] 5.2 Add statistical sanity tests: `uniform_random` all outputs within bounds; `normal_random` sample mean ≈ 0 and sample std ≈ σ within tolerance (fixed seed); `sine_sweep` instantaneous frequency at t=0 matches `f_start` and at t=T matches `f_stop`; `get_psd` and `get_kurtosis` return expected values on a known deterministic input (fixed seed, compare to hand-computed or numpy reference).
- [x] 5.3 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-excitation\tests\ --tb=short` and confirm all tests pass.

## 6. sdypy-io tests

- [x] 6.1 In `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-io\tests\`, create or extend `test_io.py`. Add a uff round-trip test: construct FRF data as a numpy array, pass to `sdypy.io.uff.prepare_58(...)` to build a dataset dict, write it with `sdypy.io.uff.UFF(<path under pytest tmp_path>).write_sets(...)`, read back with `.read_sets()`, and assert numeric equality with the original array. Use the pytest `tmp_path` fixture (Windows cannot reopen an open `NamedTemporaryFile`).
- [x] 6.2 Add an lvm parse test: generate a minimal `.lvm`-format text string (header + two-column numeric data), write to a `tempfile.NamedTemporaryFile`, parse with `sdypy.io.lvm`, and assert the returned data matches the expected values.
- [x] 6.3 Add an sfmov test: attempt to construct a minimal synthetic sfmov binary file and test the reader. If the binary format cannot be hand-constructed without internal knowledge, add a test that imports `sdypy.io.sfmov` and exercises the error path (e.g., passing a non-existent path), and add a comment documenting why a round-trip test is skipped using `pytest.skip`.
- [x] 6.4 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-io\tests\ --tb=short` and confirm all tests pass (skip-decorated sfmov test counts as pass).

## 7. sdypy-view tests

- [x] 7.1 In `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-view\tests\`, create or extend `test_view.py`. Add a test for `create_fem_mesh`: call it with a toy quad element definition and assert the returned object has the attributes expected of a pyvista mesh (e.g., non-zero `n_points`).
- [x] 7.2 Add shape tests for `prepare_animation_displacements` and `prepare_animation_field`: pass synthetic node coordinates and displacement arrays and assert the output array shapes match the expected `(n_frames, n_nodes, 3)` or equivalent documented shape.
- [x] 7.3 Add the `Plotter3D` ImportError test: guard with `try: import PyQt6; HAS_PYQT6 = True; except ImportError: HAS_PYQT6 = False`; if `HAS_PYQT6` is False, assert that `sdypy.view.Plotter3D()` raises `ImportError` with a message mentioning `PyQt6`; if PyQt6 is present, `pytest.skip` the test with a note that PyQt6 is installed.
- [x] 7.4 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-view\tests\ --tb=short` and confirm all tests pass.

## 8. sdypy-model tests

- [x] 8.1 In `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-model\tests\`, create or extend `test_model.py`. Add a `Beam.solve()` accuracy test: instantiate a cantilever beam with known geometry and material parameters (fixed `young_modulus`, `density`, cross-section); call `solve()`; assert the first natural frequency is within 5% rtol of the analytical Euler–Bernoulli value `f1 = (1.875)^2 / (2*pi*L^2) * sqrt(E*I / (rho*A))`.
- [x] 8.2 Add a `solve_eigenvalue` test: define a 2-DOF stiffness matrix K and mass matrix M with known analytic eigenfrequencies; call `sdypy.model.solve_eigenvalue(K, M)`; assert returned frequencies match hand-computed values within 1% rtol.
- [x] 8.3 Add a `lumped.Model.get_eig_freq()` test: construct a 1-DOF `sdypy.model.lumped.Model` with spring constant k and mass m; assert `get_eig_freq()` returns `sqrt(k/m) / (2*pi)` within 0.1% rtol.
- [x] 8.4 Add matrix property tests for `Shell.construct_global_matrices` and `Tetrahedron.assemble_matrices`: for a minimal element, retrieve K and M, assert each is symmetric (i.e., `np.allclose(M, M.T)` and `np.allclose(K, K.T)`), and assert all eigenvalues of M and K are non-negative.
- [x] 8.5 Run `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-model\tests\ --tb=short` and confirm all tests pass.

## 9. sdypy-EMA runtime cut

- [x] 9.1 Locate the heavy EMA test fixtures that set `pol_order_high` in `C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-EMA\tests\`. Reduce `pol_order_high` from 60 to 30 in each such fixture.
- [x] 9.2 Run the full EMA test suite: `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-EMA\tests\ --tb=short -v`. The gate is that all existing accuracy assertions pass unchanged. If any accuracy assertion fails at `pol_order_high=30`, walk up to 40, then 50, and record the minimum passing value in a comment in the fixture.
- [x] 9.3 Confirm the total EMA suite runtime has decreased (target ≤ 40 s). Record the measured runtime in a comment in the fixture file next to the `pol_order_high` setting.

## 10. Verification and CI

- [x] 10.1 Run each sibling suite locally green: `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\packages\sdypy-<name>\tests\ --tb=short` for FRF, excitation, io, view, model, EMA. Confirm all six exit with no failures.
- [x] 10.2 Run the full core suite: `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest C:\Users\jasas\Work\OpenSource\SdyPy\sdypy\tests\ --tb=short`. Confirm the only red tests are the known `pypi_artifacts`-marked ones (currently 7 failures against stale PyPI releases); record which tests fail and confirm they all carry the marker.
- [x] 10.3 Run the deselected core suite: `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m pytest -m "not pypi_artifacts" C:\Users\jasas\Work\OpenSource\SdyPy\sdypy\tests\ --tb=short`. Confirm all tests pass with 0 failures and 0 errors.
- [x] 10.4 Run `openspec validate establish-testing-ci-baseline --strict` from `C:\Users\jasas\Work\OpenSource\SdyPy\sdypy` and confirm it exits with no errors.
- [ ] 10.5 (Post-push check — user-initiated) After pushing test-suite commits to all six sibling ladisk forks and the workflow+marker commits to the core ladisk fork, verify the latest GitHub Actions workflow run on each of the seven ladisk fork repositories concludes with success. The four previously-silent forks (sdypy-EMA, sdypy-io, sdypy-FRF, sdypy-excitation) should show their first-ever successful run. Record any unexpected failures and investigate.
