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


def __getattr__(name):
    """Import a first-level sub-package lazily on first access (PEP 562)."""
    if name in _SUBPACKAGES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module  # cache: subsequent access is a plain attribute
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_SUBPACKAGES))
