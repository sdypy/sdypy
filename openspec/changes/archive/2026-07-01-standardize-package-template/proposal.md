## Why

Changes #1 (`unify-namespace-mechanism`) and #2 (`packaging-hygiene-sweep`) gave the core repo a single, clean packaging contract — pyproject-only, PEP 420 native namespace, version single-sourced, clean sdist/wheel, accurate metadata. The six first-level sibling packages (sdypy-EMA, sdypy-io, sdypy-FRF, sdypy-excitation, sdypy-view, sdypy-model) never received that treatment and have drifted into six slightly different packaging styles. A 2026-06 audit of the sibling clones found, among other divergences:

- **stale dual build definitions**: sdypy-EMA and sdypy-io still carry `setup.py` (EMA's even points at the wrong repo URL) plus stale `.travis.yml`; all six carry `requirements*.txt` alongside pyproject.
- **version triplication with a live failure**: version is hard-coded in `pyproject.toml` *and* `sdypy/<pkg>/__init__.py`, reconciled (in only 3 of 6 repos) by a `sync_version.py` script; sdypy-excitation is *currently mismatched* (pyproject `0.1.1` vs `__init__` `0.1.0`), and sdypy-io's release workflow never calls the sync script at all.
- **inconsistent CI**: sdypy-view and sdypy-model test only Python 3.12 while the rest test 3.10–3.12; two different workflow file naming schemes; all six use `actions/checkout@v3` / `setup-python@v4`, which run on a Node version GitHub deprecates 2026-06-16.
- **inconsistent metadata and docs scaffolding**: classifier sets differ (4 vs 5 entries, Development Status varies), sdypy-FRF and sdypy-excitation point their docs URL at their *backend's* docs (pyFRF / pyExSi), three repos lack `readthedocs.yaml`, sdypy-model alone uses README.md and sphinx-book-theme.

Without one written template, every future fix (and every future sub-package, per the SEP 4 roadmap) re-diverges. This is program change #3 of the v1.0 workstream and is the prerequisite for change #5 (testing & CI baseline) landing uniformly.

## What Changes

- Define one **canonical packaging template** for first-level sdypy namespace packages, as a spec in the core repo, covering: build definition, namespace layout, version sourcing, distribution contents, CI workflows, and project metadata.
- Bring all six sibling repos into conformance with the template:
  - Remove `setup.py`, `requirements.txt`, `requirements.dev.txt`, `.travis.yml`, and `sync_version.py` where present; `pyproject.toml` becomes the only build/dependency definition (mirrors core's `distribution-packaging` contract).
  - Single-source the version in `pyproject.toml`; `sdypy/<pkg>/__init__.py` derives `__version__` from installed distribution metadata (same pattern as core), eliminating the sync script and fixing the sdypy-excitation mismatch.
  - Confirm/keep PEP 420 native namespace layout (no `sdypy/__init__.py`) — already done in the working clones by change #1, restated as a template requirement.
  - Standardize the test workflow (one filename, Python 3.10–3.12 matrix, `pip install .` then pytest + flake8, current action versions) and the release workflow (tag-triggered build + PyPI publish, no version-sync step).
  - Align metadata: hatchling backend, `requires-python >= 3.10`, MIT license declaration, classifier set matching the CI matrix, Homepage/Source URLs pointing at the package's own repo (the Documentation URL of a thin wrapper may stay at its backend's docs), declared dev/docs extras.
  - Normalize repo scaffolding: README format, LICENSE file naming, `readthedocs.yaml` presence, `.gitignore` baseline.
- Add a **conformance check** so drift is detected, not re-audited by hand (mechanism decided in design.md: core-side conformance tests vs per-repo CI step vs checker script).
- Each sibling gets a patch version bump so the standardized packaging actually ships to PyPI.

**Not in scope**: real test suites for the placeholder packages (change #5), public-API/nomenclature alignment (change #4), docs content (change #6), git default-branch renaming (`main` vs `master` noted, deferred).

## Capabilities

### New Capabilities
- `sibling-package-template`: the packaging contract every first-level sdypy namespace package must satisfy — single build definition, metadata-derived version, namespace layout, distribution contents, CI workflow shape, metadata consistency — plus how conformance is verified.

### Modified Capabilities
<!-- none: `distribution-packaging` and `namespace-packaging` are core-repo contracts and their requirements do not change; the new capability references them where the template inherits their rules -->

## Impact

- **Repos**: all six sibling clones under `packages/` (file deletions, pyproject edits, `__init__.py` version derivation, workflow rewrites) + the core repo (new spec, conformance mechanism per design decision).
- **Releases**: six patch releases to PyPI once implemented (sequenced with the already-pending sdypy-model 0.1.5 / sdypy-view 0.1.7 re-releases from change #1).
- **CI**: sibling workflows renamed/rewritten; action version bumps remove the Node 20 deprecation warning ahead of GitHub's 2026-06-16 cutoff (core repo's own bump remains in change #5).
- **Behavioral note**: `sdypy.<pkg>.__version__` in a *source checkout without installed metadata* will return a fallback instead of the hard-coded string — same accepted trade-off as core (change #1/#2).
- **Remotes**: sdypy-view and sdypy-model currently work through ladisk forks; the other four clones track the sdypy org directly. Implementation lands on whatever remote each clone tracks; upstream PR flow is unchanged by this proposal.
