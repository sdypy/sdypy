## Context

The 2026-06-12 audits established:

- **Tests**: EMA has the only real suite (25 tests incl. accuracy assertions on real 10 MB data + synthetic pyLump data; ~90 s). model has 27 API-conformance tests with the FEM assembly mocked out. io/FRF/excitation/view have placeholder tests (`assert True` / import-only). Core has 81 tests: namespace conformance, public-api conformance, and PyPI-artifact checks — 7 currently red against stale PyPI releases by design.
- **Interop**: the only existing bridge is EMA's `test_tools/generate_synth_frf.py` (imports `pyLump` directly, bypassing `sdypy.model.lumped`). A probe confirmed `lumped → EMA` identification works: 2-DOF model, 1000 frequency points, identified natural frequencies/damping within 1% of analytic, ~0.1 s. `pyLump.get_FRF_matrix` returns `(n_dof, n_dof, n_freq)`; `EMA.Model` wants `(n_outputs, n_freq)` — slice `[input_dof, :, :]`.
- **CI**: core `python-package.yml` runs `checkout@v3`/`setup-python@v4` (Node-24 force date 2026-06-16), push-trigger only, fail-fast default, no build step; core release workflow is `@v2`-era with `pypa/gh-action-pypi-publish@v1.4.2`. All six sibling workflows are byte-identical, current (`@v4`/`@v5`), and green where they have run. Actions is enabled on all 7 ladisk forks; EMA/io/FRF/excitation forks have never had a run (pushes predate enablement). Core CI: 5/5 recent runs red, all from PyPI-artifact tests. No lint/coverage config exists anywhere beyond workflow-inline flake8.

Constraints: review model is "one big PR per repo at the end + batched PyPI release" — so the pending sibling versions (EMA 0.30.0, io 0.4.0, FRF/excitation/view/model 0.2.0) are still unreleased and absorb test additions without new bumps. Sibling workflow files are governed by the change #3 template contract and stay untouched. Token auth stays (user decision; trusted publishing → change #8).

## Goals / Non-Goals

**Goals:**
- Core CI matrix green on every push, with deprecated actions gone before the 2026-06-16 Node-24 forcing date.
- PyPI-artifact conformance becomes an explicitly local, release-time gate (marker-based).
- Every first-level package has at least a minimal *real* functional test of its own surface.
- A core interop suite proves the packages compose: signal → response → FRF → modal identification, plus io round-trip and sep005 smoke.
- All seven fork CIs demonstrated green.

**Non-Goals:**
- Coverage thresholds, ruff, pre-commit, tox (candidate for post-v1.0).
- Trusted publishing / release process (change #8). Docs (change #6).
- Python 3.13+ matrix extension (would touch the #3 template + classifiers; team can decide at final review).
- Display-dependent view tests (Qt/VTK offscreen rendering is flaky in CI; helpers are tested Qt-free).
- Backend (pyFRF, pyExSi, pyuff, …) test suites — upstream scope.

## Decisions

### D1: `pypi_artifacts` marker; GitHub CI deselects it

All core tests that fetch published artifacts from PyPI over HTTP (`test_published_sdist_has_no_stale_packaging`, `test_published_wheel_ships_only_own_portion`) or that assert conformance of *installed distributions* which in CI come from PyPI (`test_sibling_ships_no_namespace_init`, all of `test_public_api.py`'s per-sibling `__all__` tests) get `@pytest.mark.pypi_artifacts`. The marker is registered in `[tool.pytest.ini_options]` (also setting `testpaths = ["tests"]`). CI runs `pytest -m "not pypi_artifacts"`. A plain local `pytest` still runs everything — the marked set is the pre-release local gate (user decision: these need not run on the GitHub server; change #8's release checklist runs them).

*Why marker rather than a separate advisory CI job?* User decision 2026-06-12. It also removes PyPI HTTP flakiness from CI entirely.

*Boundary subtlety*: the umbrella-level tests in `test_public_api.py` (`test_umbrella_all_is_exactly_the_six_names`, star-import test, drift advisory) are environment-local and stay unmarked. The per-sibling `__all__` tests are marked as a block (in CI the siblings come from PyPI); locally they run against whatever is installed — still green with the local clones installed.

### D2: Core workflows align with the sibling template

`python-package.yml`: triggers `push` + `pull_request` + `workflow_dispatch`; matrix unchanged `["3.10", "3.11", "3.12"]` with `fail-fast: false`; `checkout@v4` + `setup-python@v5`; install `pip install .` then `pip install pytest flake8 build`; the existing two-pass flake8; `pytest -m "not pypi_artifacts"`; final `python -m build` validation step. `release-and-publish-to-pypi.yml`: rebuilt to the sibling standard (`checkout@v4`, `setup-python@v5`, `pip install --upgrade pip build`, `python -m build`, `pypa/gh-action-pypi-publish@release/v1` with `password: ${{ secrets.PYPI_API_TOKEN }}`) — token auth kept. `workflow_dispatch` is added to the core test workflow only; sibling workflow files are not touched (template contract stability; the four silent forks get their first runs from the test-suite pushes anyway).

### D3: Minimal real-test baseline per package (tests only, no version bumps)

| Package | New tests (seeded, no network, no display) |
|---|---|
| FRF | `FRF(sampling_freq, data, …)` on a synthetic SDOF response: H1 magnitude peaks near the resonance; `get_f_axis` length/spacing; `assert_sep005` accepts a valid minimal sep005 dict and rejects an invalid one |
| excitation | the 11 curated functions: output shape/dtype; `uniform_random` within bounds; `normal_random` moments ≈ (0, σ); `sine_sweep` instantaneous-frequency endpoints; `get_psd`/`get_kurtosis` on known signals |
| io | `uff`: `prepare_58` → write → read round-trip preserves data; `lvm`: parse a small generated .lvm text file; `sfmov`: read a minimal synthetic file if the format permits hand-construction (else document why skipped) |
| view | `create_fem_mesh` returns a valid pyvista mesh for a toy quad; `prepare_animation_displacements`/`_field` shapes; `Plotter3D()` raises `ImportError` mentioning PyQt6 when PyQt6 is absent |
| model | `Beam.solve()` first natural frequencies vs analytical Euler–Bernoulli cantilever values (rtol ≤ 5%); `solve_eigenvalue` on an analytic 2-DOF K/M; `lumped.Model.get_eig_freq` vs hand-computed 1-DOF `sqrt(k/m)/2π`; `Shell.construct_global_matrices` and `Tetrahedron.assemble_matrices` produce symmetric K/M with non-negative eigenvalues on a minimal element |
| EMA | no new coverage needed; runtime cut: heavy fixtures' `pol_order_high` 60 → 30 (audit indicates modes still reliably identified), existing accuracy assertions must pass unchanged — that is the gate |

### D4: Interop suite lives in the core repo (`tests/test_interop.py`)

Four areas, all seeded and tolerance-based (rtol 2–5%), importing only through the `sdypy.*` namespace (that is the point — e.g. `sdypy.model.lumped`, not `pyLump`):

1. **lumped → EMA**: 2-DOF `sdypy.model.lumped.Model` → `get_FRF_matrix` → `sdypy.EMA.Model(frf=…, freq=…)` → poles → identified natural frequencies + damping vs `get_eig_freq()`/`get_damping_ratios()` (the proven probe).
2. **excitation → lumped → FRF → EMA** (flagship end-to-end): `sdypy.excitation.pseudo_random` excitation → `lumped.Model.get_response()` → `sdypy.FRF.FRF(exc, resp)` H1 estimate → `sdypy.EMA` identification vs the lumped model's analytic frequencies. If H1-on-simulated-response proves numerically unstable, fall back to averaging multiple noise realizations before relaxing tolerances; document the seed.
3. **io round-trip**: FRF data → `sdypy.io.uff.prepare_58` → write → read → numeric equality.
4. **sep005 smoke**: a minimal sep005 timeseries dict passes `sdypy.FRF.assert_sep005`; an invalid one raises. (Full sep005 exposure is change #7.)

These run in CI's unmarked set (no PyPI dependence — they use the installed packages, whatever their origin; in CI that is PyPI versions of siblings, all of which already provide the needed callables — `lumped`, `FRF`, `EMA.Model` exist in the old releases too, so the interop suite is green in CI both before and after the batched release).

### D5: No new version bumps; tests ride the pending releases

Sibling sdists ship `tests/` (template allow-list), but the pending versions (EMA 0.30.0, io 0.4.0, others 0.2.0) are unreleased — test additions fold into them. Shipped package code is untouched in this change, except nothing: all changes are test files, workflow files (core), and pyproject pytest config (core).

### D6: Relationship to the change #3 template contract

The `testing-ci` capability governs the CORE workflow shape and the test baseline; the `sibling-package-template` capability (still in change #3's folder, unsynced) continues to govern sibling packaging/workflow files. No sibling workflow file changes here, so no delta against that capability. If the team later wants `workflow_dispatch` in the sibling template, that is a one-line template amendment at the final review.

## Risks / Trade-offs

- [Marked tests never run on GitHub → stale-PyPI regressions invisible in CI] → deliberate (user decision); the local full `pytest` remains the release gate and change #8 codifies it in the release checklist.
- [Flagship end-to-end interop test numerically flaky] → fixed seeds, generous rtol, fallback design (averaged realizations) before tolerance relaxation; worst case it asserts frequencies only (damping is the fragile part).
- [EMA pol_order_high reduction breaks accuracy assertions] → the assertions ARE the gate; if 30 fails, walk up (40, 50) until green and record the floor.
- [sfmov synthetic file infeasible] → allowed to document-and-skip; the reader is small own-code, an import + error-path test is the floor.
- [CI installs siblings from PyPI, so new sibling tests don't run in core CI] → correct and intended: sibling tests run in each sibling's own CI (their workflows run `pytest` on their repo), which the test-suite pushes will trigger on all four silent forks.
- [view test depends on PyQt6 being absent in CI to test the ImportError path] → guard with `importorskip`-style conditional: assert the error only when PyQt6 is missing, skip otherwise.

## Migration Plan

1. Core: pytest config + markers (immediately unblocks green CI), workflow rewrites, interop suite.
2. Siblings: add test files (EMA runtime cut last, gated on its assertions).
3. Push order: siblings first (their CIs go green, including first-ever runs on the four silent forks), then core (its CI goes green with the marker deselection).
4. Rollback: all changes are additive test/workflow files; revert per repo.

## Open Questions

All resolved by the project lead on 2026-06-12:

- **Green-matrix mechanism**: `pypi_artifacts` marker; the marked tests do NOT run on the GitHub server at all — they are a local, release-time gate. CI deselects them.
- **Publish auth**: token auth kept; trusted publishing revisited in change #8.
