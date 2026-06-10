"""Conformance tests for the sdypy namespace mechanism.

Enforces the contract from SEP 3 / the unify-namespace-mechanism change:
  * importing the umbrella is lightweight (no heavy optional backends),
  * every first-level sub-package resolves via attribute / from-import / submodule,
  * __version__ is a non-empty string sourced from metadata,
  * no first-level sibling distribution ships a top-level sdypy/__init__.py.
"""
import importlib
import importlib.metadata as importlib_metadata
import subprocess
import sys

import pytest

import sdypy
from sdypy import _SUBPACKAGES  # source of truth for first-level names

# Derived from the single source of truth (_SUBPACKAGES) so a newly added
# first-level subpackage is automatically covered by the sibling-init check.
# Each first-level name maps 1:1 to its sibling distribution "sdypy-<name>".
_SIBLING_DISTRIBUTIONS = tuple("sdypy-%s" % name for name in _SUBPACKAGES)


def test_bare_import_does_not_pull_heavy_backends():
    """import sdypy must not eagerly import heavy optional backends.

    Runs in a fresh interpreter so earlier tests that touch sdypy.view cannot
    contaminate sys.modules.
    """
    code = (
        "import sys, sdypy; "
        "present = [m for m in ('pyvista', 'pyvistaqt', 'vtk') if m in sys.modules]; "
        "print(','.join(present))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    leaked = [m for m in result.stdout.strip().split(",") if m]
    assert leaked == [], "import sdypy eagerly imported heavy backends: %s" % leaked


@pytest.mark.parametrize("name", _SUBPACKAGES)
def test_attribute_access_resolves_subpackage(name):
    module = getattr(sdypy, name)
    assert module is importlib.import_module("sdypy.%s" % name)
    assert getattr(sdypy, name) is module  # cached into globals (PEP 562)


@pytest.mark.parametrize("name", _SUBPACKAGES)
def test_from_import_style(name):
    """A literal `from sdypy import <name>` resolves via the lazy facade.

    Runs in a fresh interpreter that issues ONLY the from-import, with no
    preceding `import sdypy.<name>`. CPython auto-binds an explicitly imported
    submodule onto its parent package, so a prior submodule import would let
    `from sdypy import <name>` succeed through that automatic binding instead
    of the package's PEP 562 __getattr__. Isolating the from-import here forces
    it through __getattr__, genuinely exercising the from-import facade.
    """
    code = (
        "from sdypy import %s as sub; "
        "import importlib; "
        "assert sub is importlib.import_module('sdypy.%s'); "
        "print('CONFORM_OK')"
    ) % (name, name)
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    # Some subpackages (e.g. view) emit a benign optional-backend notice on
    # stdout; the sentinel is what proves the import + identity assert passed.
    assert result.stdout.splitlines()[-1].strip() == "CONFORM_OK", result.stdout


@pytest.mark.parametrize("name", _SUBPACKAGES)
def test_submodule_import_style(name):
    """A literal `import sdypy.<name>` resolves the native PEP 420 portion.

    Runs in a fresh interpreter so attribute caching in this process cannot
    mask a broken namespace path.
    """
    code = (
        "import sdypy.%s as sub; "
        "import importlib; "
        "assert sub is importlib.import_module('sdypy.%s'); "
        "print('CONFORM_OK')"
    ) % (name, name)
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines()[-1].strip() == "CONFORM_OK", result.stdout


def test_unknown_attribute_raises_attribute_error():
    with pytest.raises(AttributeError):
        sdypy.does_not_exist


def test_version_is_non_empty_string():
    assert isinstance(sdypy.__version__, str)
    assert sdypy.__version__


@pytest.mark.parametrize("dist_name", _SIBLING_DISTRIBUTIONS)
def test_sibling_ships_no_namespace_init(dist_name):
    """No first-level sibling distribution may install sdypy/__init__.py.

    The umbrella package is the only distribution permitted to provide it.
    """
    try:
        dist = importlib_metadata.distribution(dist_name)
    except importlib_metadata.PackageNotFoundError:
        pytest.skip("%s not installed in this environment" % dist_name)
    offenders = [
        str(f)
        for f in (dist.files or [])
        if str(f).replace(chr(92), "/").lower() == "sdypy/__init__.py"
    ]
    assert not offenders, (
        "%s ships a namespace __init__.py (%s); first-level siblings must be "
        "native PEP 420 portions" % (dist_name, offenders)
    )
