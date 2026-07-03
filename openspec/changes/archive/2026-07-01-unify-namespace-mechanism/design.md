## Context

`sdypy` is a namespace meta-package: the umbrella distribution plus independently developed first-level packages (`sdypy-EMA`, `sdypy-io`, `sdypy-FRF`, `sdypy-excitation`, `sdypy-view`, `sdypy-model`) that each contribute a sub-package under the shared `sdypy/` namespace. Today the namespace is assembled inconsistently:

- **core** (`sdypy/__init__.py`): `pkgutil.extend_path(...)` + a hard-coded `__version__` + eager `from sdypy import EMA, io, FRF, excitation, model, view`.
- **5 of 6 siblings**: no `sdypy/__init__.py` (PEP 420 native portions) — correct.
- **`sdypy-model`**: ships `sdypy/__init__.py` containing `from . import model` — incorrect; can shadow the namespace and break sibling discovery depending on `sys.path` order.

Two concrete problems follow: (1) SEP 3 mandates native namespace packages, but the core is not native and one sibling violates the no-`__init__.py` rule; (2) the eager re-exports make `import sdypy` import every sibling and its heavy dependencies — observed as a Qt import attempt (`No module named 'PyQt6'`) triggered merely by `import sdypy`.

Constraint: the README's documented usage (`import sdypy as sd; sd.EMA.Model(...)`, `sd.io.uff.UFF(...)`, etc.) depends on attribute access on the umbrella, which a pure-native namespace does not provide. The chosen design must preserve that ergonomics while fixing the inconsistency and the eager-import cost.

## Goals / Non-Goals

**Goals:**
- One documented namespace mechanism used identically across all seven repositories.
- Preserve the public API: `import sdypy as sd; sd.EMA…`, `from sdypy import EMA`, `import sdypy.EMA`, and `sd.__version__`.
- `import sdypy` is cheap — no eager import of sub-packages or their heavy backends.
- Single source of truth for the version.
- Enforce conformance automatically so the inconsistency cannot silently return.

**Non-Goals:**
- Defining the `sdypy-sep005` / unified-timeseries surface (`sd.sep005`) — deferred to its own change.
- Changing any sub-package's internal API or scientific behavior.
- Reworking distribution names, build backends, or release flow (covered by the later packaging-hygiene change).

## Decisions

**Decision 1 — Mechanism: core-owned lazy facade over native sibling portions (Option C).**
The core ships a small `sdypy/__init__.py` that (a) exposes the first-level names lazily via PEP 562 `__getattr__`, and (b) leaves the package a namespace-compatible portion so siblings still contribute. Siblings remain PEP 420 native (no `sdypy/__init__.py`).

Sketch:
```python
# sdypy/__init__.py
import importlib
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sdypy")
except PackageNotFoundError:           # editable/source checkout without dist metadata
    __version__ = "0+unknown"

_SUBPACKAGES = ("EMA", "io", "FRF", "excitation", "model", "view")

def __getattr__(name):                 # PEP 562: lazy, import-on-first-access
    if name in _SUBPACKAGES:
        module = importlib.import_module(f"{__name__}.{name}")
        globals()[name] = module       # cache so subsequent access is plain attribute
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__():
    return sorted(set(globals()) | set(_SUBPACKAGES))
```

*Alternatives considered:*
- **Option A — pure PEP 420 native (no `sdypy/__init__.py` anywhere).** Simplest and literal SEP 3, but removes `sd.EMA` attribute access and `sd.__version__`, breaking the README's documented usage. Rejected for v1.0 ergonomics.
- **Option B — formalize the current eager re-exports.** Smallest diff, keeps the sugar, but keeps the eager-heavy-import wart (`import sdypy` pulls pyvista/Qt). Rejected.

**Decision 2 — Version from installed metadata.** Use `importlib.metadata.version("sdypy")` so the wheel/`pyproject.toml` is the single source of truth, eliminating the duplicated hard-coded string and the dead `sdypy/core/__init__.py` version path that `setup.py` reads.

**Decision 3 — Siblings are native portions; no `sdypy/__init__.py` in any sibling.** Remove it from `sdypy-model`; assert its absence in the other five. This keeps the umbrella's `__init__.py` as the *only* `sdypy/__init__.py` on the path, so lazy resolution and namespace extension are deterministic.

**Decision 4 — Conformance test in the core.** A test that (a) imports `sdypy` and asserts no heavy backend modules (e.g. `pyvista`, `pyvistaqt`, `vtk`) are present in `sys.modules`, (b) round-trips lazy access for every name in `_SUBPACKAGES`, and (c) asserts `sd.__version__` is a non-empty string. A separate packaging check asserts no sibling distribution installs a `sdypy/__init__.py`.

**Decision 5 — Amend SEP 3.** Add a short section: "The umbrella `sdypy` package MAY provide a lazy facade (`__getattr__`) for first-level names and the package version; all other packages contributing to the namespace MUST be native PEP 420 portions (no `sdypy/__init__.py`)." This resolves the SEP-3-vs-README contradiction.

## Risks / Trade-offs

- **A `sdypy/__init__.py` in the umbrella means the namespace is no longer "pure" native** → Acceptable and explicitly documented in SEP 3; siblings remain native, which is what SEP 3 actually cares about for plug-in discovery.
- **PEP 562 `__getattr__` + namespace extension interaction** (does `from sdypy import EMA` still find the sibling when the umbrella owns `__init__.py`?) → Mitigation: verify both import styles in the conformance test across an editable install of the umbrella plus PyPI siblings (the current local setup), and a clean wheel install.
- **Static analysers / IDEs may not infer lazy attributes** → Mitigation: list names in `__dir__`; optionally add a `if TYPE_CHECKING:` import block or a `.pyi` stub in a follow-up so editors autocomplete `sd.EMA`.
- **`importlib.metadata.version` raises in a source tree without installed metadata** → Mitigation: `try/except PackageNotFoundError` fallback as shown.
- **Coordinating a release across `sdypy` + `sdypy-model`** → Mitigation: see Migration Plan; the umbrella change is backward compatible, the `sdypy-model` change is the only one that must ship.

## Migration Plan

1. Land the new core `sdypy/__init__.py` (lazy facade) and conformance test in the `sdypy` repo on `chore/openspec-and-namespace`; remove the stale `sdypy/core` version path if it blocks metadata sourcing.
2. In `sdypy-model`, remove `sdypy/__init__.py`, bump a patch version, release to PyPI. (This is the one strictly-required sibling release.)
3. Audit the other five siblings; no code change expected, only a confirming test/CI note.
4. Amend SEP 3 in the same core PR.
5. Verify end-to-end in a fresh venv: `pip install sdypy`, then run the conformance test and the README examples.
6. **Rollback**: the core change is backward compatible (the lazy facade is a superset of the old behavior), so rollback is reverting the core commit; the `sdypy-model` `__init__.py` removal can be reverted independently if discovery regressions appear.

## Open Questions

- Do we ship an IDE stub (`sdypy/__init__.pyi`) for autocomplete now, or defer to the docs/UX change? (Leaning defer.)
- Should the "no sibling `sdypy/__init__.py`" rule be enforced by a shared CI check in each sibling repo, or centrally via an interoperability test in the core? (Leaning a lightweight check in the core now, shared CI later with the template-standardization change.)
- Confirm the minimum Python: PEP 562 requires 3.7+; all packages already require ≥3.10, so no constraint conflict.
