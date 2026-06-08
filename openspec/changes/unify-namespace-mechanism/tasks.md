## 1. Core umbrella: lazy facade

- [ ] 1.1 Rewrite `sdypy/sdypy/__init__.py` as a PEP 562 lazy facade: `__getattr__` resolving `EMA`, `io`, `FRF`, `excitation`, `model`, `view` on first access and caching into `globals()`; add `__dir__`.
- [ ] 1.2 Source `__version__` from `importlib.metadata.version("sdypy")` with a `PackageNotFoundError` fallback; remove the hard-coded version string.
- [ ] 1.3 Remove the eager `from sdypy import EMA, io, FRF, excitation, model, view` block.
- [ ] 1.4 Resolve the dead `sdypy/core/__init__.py` version path (empty file that `setup.py` reads) so the single source of truth is metadata; do not break the existing `sdypy.core` import surface if anything depends on it.
- [ ] 1.5 Add `[tool.hatch.build.targets.sdist]` with an explicit source-only `include` list so the published **sdist** excludes `openspec/`, `.claude/`, and `docs/**/_build`; verify with `python -m build` that neither the wheel nor the sdist contains dev docs. (Broader hygiene — deleting committed `docs/_build`, `setup.py`, `.travis.yml` — is deferred to the packaging-hygiene change.)

## 2. Sibling packages: native portions

- [ ] 2.1 Remove `sdypy/__init__.py` from `packages/sdypy-model` and confirm `from . import model` behavior is preserved via normal sub-package import.
- [ ] 2.2 Verify the other five siblings (`sdypy-EMA`, `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`, `sdypy-view`) ship no top-level `sdypy/__init__.py`.

## 3. Conformance tests

- [ ] 3.1 Add a test asserting `import sdypy` leaves `pyvista`, `pyvistaqt`, and `vtk` absent from `sys.modules`.
- [ ] 3.2 Add a test round-tripping lazy attribute access for every name in `_SUBPACKAGES`, plus `from sdypy import <name>` and `import sdypy.<name>`.
- [ ] 3.3 Add a test asserting `sdypy.__version__` is a non-empty string.
- [ ] 3.4 Add a packaging check asserting no first-level sibling distribution installs a `sdypy/__init__.py`.

## 4. Verification across install modes

- [ ] 4.1 In a fresh venv, `pip install sdypy` (wheel) and run the conformance tests green.
- [ ] 4.2 Re-run the existing editable-install setup (umbrella editable + PyPI siblings) and confirm both import styles and `sd.__version__` still work.
- [ ] 4.3 Run the README getting-started examples (`sd.EMA.Model`, `sd.io.uff.UFF`, `sd.FRF.FRF`, `sd.excitation`) and confirm they execute.

## 5. Governance & docs

- [ ] 5.1 Amend SEP 3 with the "core provides a lazy facade; siblings are native portions (no `sdypy/__init__.py`)" clause, resolving the SEP-3-vs-README contradiction.
- [ ] 5.2 Note in the change/PR that `sdypy-sep005` exposure (`sd.sep005`) is intentionally deferred to a separate change.

## 6. Release coordination

- [ ] 6.1 Bump a patch version and release `sdypy-model` to PyPI (the only strictly-required sibling release).
- [ ] 6.2 Confirm the umbrella change is backward compatible (lazy facade is a superset of prior behavior) before merging to the fork's `main`.
