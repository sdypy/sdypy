## Why

The `sdypy` namespace is currently assembled three different ways across the seven repositories: the core uses `pkgutil.extend_path` and eagerly re-exports every sub-package, five of the six first-level packages are PEP 420 native (no `sdypy/__init__.py`), and `sdypy-model` wrongly ships a `sdypy/__init__.py` — a latent bug that can shadow the namespace and break `import sdypy.EMA` depending on `sys.path` order. This contradicts SEP 3, and the eager re-exports mean a bare `import sdypy` drags in the entire heavy stack (e.g. `sdypy-view` → `pyvista`/`pyvistaqt`/Qt). A trustworthy, consistent v1.0 needs a single, documented mechanism.

## What Changes

- Standardize the whole ecosystem on **one** mechanism: a **core-owned lazy facade over native sibling plug-ins** (decision recorded in design.md).
- The core `sdypy/__init__.py` resolves sub-packages **lazily** via PEP 562 module `__getattr__`, so `import sdypy as sd; sd.EMA…` and `sd.__version__` keep working while `import sdypy` stays lightweight (no eager import of heavy backends).
- `__version__` becomes a single source of truth via `importlib.metadata` instead of a hard-coded string.
- All first-level sibling packages MUST NOT ship a top-level `sdypy/__init__.py` (they remain PEP 420 native portions of the namespace).
  - **BREAKING (internal/packaging)**: remove `sdypy/__init__.py` from `sdypy-model`.
- Remove the eager `from sdypy import EMA, io, FRF, excitation, model, view` block from the core.
- Add a conformance test that asserts (a) `import sdypy` does not import heavy optional backends, (b) lazy attribute access works for all first-level names, and (c) no sibling ships `sdypy/__init__.py`.
- Amend SEP 3 to document the "core package provides a lazy facade; siblings are native portions" pattern, resolving its contradiction with the README's documented `sd.EMA` usage.
- Add a minimal `[tool.hatch.build.targets.sdist]` source-only include list so development docs introduced by this workflow (`openspec/`, `.claude/`) are never published in the sdist. The wheel already ships only `sdypy/`; this closes the sdist gap. (Broader packaging-hygiene cleanup is a separate change.)
- `sdypy-sep005` exposure (whether it becomes `sd.sep005`) is acknowledged here but its API contract is deferred to a separate change.

## Capabilities

### New Capabilities
- `namespace-packaging`: The contract governing how sub-packages integrate into the `sdypy` namespace and how the umbrella package exposes them — lazy attribute access for first-level names, version sourced from installed metadata, the prohibition on sibling `sdypy/__init__.py` files, and the conformance checks that enforce it.

### Modified Capabilities
<!-- None: no prior OpenSpec specs exist yet (openspec/specs/ is empty). SEP 3 is amended as documentation, not an OpenSpec spec delta. -->

## Impact

- **Code**: core `sdypy/__init__.py` (rewritten as lazy facade); `sdypy-model` (remove `sdypy/__init__.py`); the other five siblings audited to confirm no `sdypy/__init__.py`.
- **Public API**: `import sdypy as sd; sd.EMA…`, `from sdypy import EMA`, `import sdypy.EMA`, and `sd.__version__` all continue to work (README examples remain valid). Behavioral change: `import sdypy` no longer eagerly imports sub-packages or their heavy dependencies.
- **Packaging**: single source of truth for the version; no change to distribution names or install (`pip install sdypy`).
- **Docs/Governance**: SEP 3 amended; the version-duplication and `sdypy-model` issues from the audit are closed.
- **CI**: new conformance test added to the core package's test suite (and, optionally, mirrored as an interoperability check).
- **Repos touched**: `sdypy` (core), `sdypy-model`; verification across `sdypy-EMA`, `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`, `sdypy-view`.
