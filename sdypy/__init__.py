"""SDyPy - Structural Dynamics Python (umbrella package).

The umbrella distribution is the only one that provides sdypy/__init__.py. It is
a lightweight lazy facade over the independently developed first-level
sub-packages (EMA, io, FRF, excitation, model, view), which are native PEP 420
portions of the sdypy namespace. See SEP 3.

- First-level names are imported lazily, on first attribute access (PEP 562),
  so 'import sdypy' stays cheap and does not pull heavy optional backends.
- __version__ is sourced from the installed distribution metadata.
"""
from pkgutil import extend_path

# Keep this package a namespace-compatible portion so the native sibling
# distributions (installed elsewhere on sys.path) still contribute their
# sub-packages under sdypy. Load-bearing: without it, 'import sdypy.EMA' cannot
# find the sibling portions.
__path__ = extend_path(__path__, __name__)

from importlib import import_module
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sdypy")
except PackageNotFoundError:  # source checkout without installed dist metadata
    __version__ = "0+unknown"

_SUBPACKAGES = ("EMA", "io", "FRF", "excitation", "model", "view")

# Aliases exposed on the umbrella that are NOT sdypy.* namespace portions.
# sep005 ships as the standalone distribution `sdypy_sep005` (the SEP 5
# unified-timeseries standard + compliance validator); the backends depend on
# it directly, so it stays a leaf package and is surfaced here only for
# discoverability as `sd.sep005`. The package __init__ holds only __version__;
# the validator API (assert_sep005, ...) lives in the `sdypy_sep005.sep005`
# module, so the alias targets that module (matching pyFRF's import). See SEP 5.
_ALIASES = {"sep005": "sdypy_sep005.sep005"}

# The umbrella's public API is the six first-level sub-package names plus the
# sep005 alias. `from sdypy import *` resolves each through __getattr__, i.e. it
# eagerly imports them - accepted behavior for an explicit "give me everything".
__all__ = list(_SUBPACKAGES) + list(_ALIASES)


def __getattr__(name):
    """Import a first-level sub-package or alias lazily on first access (PEP 562)."""
    if name in _SUBPACKAGES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module  # cache: subsequent access is a plain attribute
        return module
    if name in _ALIASES:
        module = import_module(_ALIASES[name])  # standalone leaf, e.g. sdypy_sep005
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_SUBPACKAGES) | set(_ALIASES))
