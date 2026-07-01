## Why

Only sdypy-EMA has real functional tests; io, FRF, excitation, and view ship `assert True` placeholders, model's FEM math is untested (its new conformance tests deliberately mock the assembly), and nothing anywhere exercises SDyPy's core promise — packages working together. Meanwhile core CI is permanently red (the PyPI-artifact conformance tests correctly flag stale published releases, masking real regressions) and runs deprecated `actions/checkout@v3` / `setup-python@v4` (release workflow even `@v2`), which GitHub force-migrates to Node 24 on **2026-06-16**.

## What Changes

- **Green matrix**: introduce a `pypi_artifacts` pytest marker on every core test that inspects published PyPI artifacts or PyPI-installed distributions; GitHub CI deselects them (`-m "not pypi_artifacts"`) so the matrix is green and meaningful. The marked tests become a **local, release-time gate** (user decision 2026-06-12: no need to run them on the GitHub server); they are run locally before the batched PyPI release.
- **Core workflow modernization**, aligning with the sibling template: `checkout@v4` + `setup-python@v5`, `pull_request` + `workflow_dispatch` triggers, `fail-fast: false`, a `python -m build` validation step; release workflow rebuilt on the sibling standard (`checkout@v4`, `setup-python@v5`, `pypa/gh-action-pypi-publish@release/v1`), **keeping token auth** (trusted publishing deferred to change #8, user decision 2026-06-12).
- **Real test baseline for the four empty siblings** (tests only — no shipped-code changes, no new version bumps; the additions fold into the pending unreleased versions):
  - FRF: `FRF` class behavior on synthetic signals (H1 estimation sanity), `assert_sep005` valid/invalid paths.
  - excitation: seeded shape/statistical sanity tests for the eleven curated functions.
  - io: `uff` write→read round-trip, `lvm` parsing of a generated file, `sfmov` reader if a minimal synthetic file is feasible.
  - view: Qt-free tests of the pure helpers (`create_fem_mesh`, `prepare_animation_displacements`, `prepare_animation_field`) and the informative `ImportError` from `Plotter3D` without PyQt6.
- **Real FEM correctness tests for model**: `Beam.solve()` vs analytical Euler–Bernoulli frequencies, `solve_eigenvalue` on an analytic 2-DOF system, `lumped` eigenfrequencies, `Shell`/`Tetrahedron` assembled-matrix properties (symmetry, positive (semi-)definiteness).
- **Cross-package interop suite in the core repo** (`tests/test_interop.py`): `model.lumped` → `EMA` identification (feasibility proven: <1% error, ~0.1 s); the full chain `excitation` signal → `lumped` response → `FRF` (H1) → `EMA`; `io.uff` round-trip of FRF data; `sdypy-sep005` smoke via `FRF.assert_sep005`.
- **EMA suite runtime cut** (~90 s → target ≤40 s) by lowering `pol_order_high` in the heavy fixtures, with the existing accuracy assertions unchanged.
- **CI verified green on all seven ladisk forks** — the four forks that have never run a workflow (EMA, io, FRF, excitation) get triggered naturally by the test-suite pushes.

## Capabilities

### New Capabilities
- `testing-ci`: the testing and CI contract for the core and first-level packages — the pypi_artifacts marker policy and CI deselection, required core workflow shape (triggers, matrix, action versions, build validation), the minimum real-test baseline per first-level package, the cross-package interop suite, and the green-matrix requirement.

### Modified Capabilities

<!-- none: sibling workflow FILES are untouched (the sibling-package-template contract from change #3 stays as-is); only test files are added in sibling repos. namespace-packaging, distribution-packaging, public-api requirements unchanged — their tests merely gain markers. -->

## Impact

- **Core repo**: both workflow files rewritten; `pyproject.toml` gains `[tool.pytest.ini_options]` (marker registration); markers added in `tests/test_namespace_conformance.py` and `tests/test_public_api.py`; new `tests/test_interop.py`; new `openspec/specs/testing-ci/spec.md`.
- **Siblings**: new/extended `tests/` files in EMA (runtime cut), io, FRF, excitation, view, model. No packaging, version, or shipped-code changes.
- **CI**: core matrix goes green immediately; the PyPI-conformance suite moves to the local release checklist (change #8 inherits it as a release gate).
- **Out of scope**: coverage metrics/ruff/pre-commit, trusted publishing (#8), docs (#6), extending the Python matrix beyond 3.10–3.12 (template/classifier change — team can revisit at the final review), GUI/display-dependent view tests, backend (3rd-level) test suites.
