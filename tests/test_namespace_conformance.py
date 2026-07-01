"""Conformance tests for the sdypy namespace mechanism.

Enforces the contract from SEP 3 / the unify-namespace-mechanism change:
  * importing the umbrella is lightweight (no heavy optional backends),
  * every first-level sub-package resolves via attribute / from-import / submodule,
  * __version__ is a non-empty string sourced from metadata,
  * no first-level sibling distribution ships a top-level sdypy/__init__.py.
"""
import importlib
import importlib.metadata as importlib_metadata
import io
import json
import re
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from functools import lru_cache

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
@pytest.mark.pypi_artifacts
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


# ---------------------------------------------------------------------------
# Distribution-layer checks for the sibling-package-template contract.
#
# These inspect the *latest published PyPI artifacts* of each sibling, so they
# stay red until a package's conformant release ships and flip green per
# publish (accepted in the standardize-package-template design).
# ---------------------------------------------------------------------------

# Stale packaging artefacts that must not appear at the root of a sdist.
_FORBIDDEN_SDIST_ENTRY = re.compile(
    r"^[^/]+/(setup\.py|setup\.cfg|requirements[^/]*\.txt|sync_version\.py|\.travis\.yml)$"
)


@lru_cache(maxsize=None)
def _published_artifacts(dist_name):
    """Fetch the latest release's sdist and wheel name lists from PyPI."""
    url = "https://pypi.org/pypi/%s/json" % dist_name
    with urllib.request.urlopen(url, timeout=30) as resp:
        meta = json.load(resp)
    sdist_names, wheel_names = None, None
    for f in meta["urls"]:
        with urllib.request.urlopen(f["url"], timeout=60) as resp:
            payload = io.BytesIO(resp.read())
        if f["packagetype"] == "sdist":
            with tarfile.open(fileobj=payload, mode="r:gz") as tar:
                sdist_names = tar.getnames()
        elif f["packagetype"] == "bdist_wheel":
            with zipfile.ZipFile(payload) as whl:
                wheel_names = whl.namelist()
    return meta["info"]["version"], sdist_names, wheel_names


def _artifacts_or_skip(dist_name):
    try:
        return _published_artifacts(dist_name)
    except (urllib.error.URLError, OSError) as exc:
        pytest.skip("PyPI unreachable for %s: %s" % (dist_name, exc))


@pytest.mark.parametrize("dist_name", _SIBLING_DISTRIBUTIONS)
@pytest.mark.pypi_artifacts
def test_published_sdist_has_no_stale_packaging(dist_name):
    """The latest PyPI sdist must not contain deleted packaging artefacts."""
    version, sdist_names, _ = _artifacts_or_skip(dist_name)
    if sdist_names is None:
        pytest.fail("%s %s publishes no sdist" % (dist_name, version))
    offenders = [
        n for n in sdist_names
        if _FORBIDDEN_SDIST_ENTRY.match(n.replace(chr(92), "/"))
    ]
    assert not offenders, (
        "%s %s sdist contains stale packaging artefacts: %s"
        % (dist_name, version, offenders)
    )


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_published_wheel_ships_only_own_portion(name):
    """The latest PyPI wheel may only ship sdypy/<pkg>/, never sdypy/__init__.py."""
    dist_name = "sdypy-%s" % name
    version, _, wheel_names = _artifacts_or_skip(dist_name)
    if wheel_names is None:
        pytest.fail("%s %s publishes no wheel" % (dist_name, version))
    portion_prefix = "sdypy/%s/" % name
    normalized = [n.replace(chr(92), "/") for n in wheel_names]
    # Positive assertion first: a wheel whose portion landed outside sdypy/
    # (e.g. hatchling stripping the namespace prefix) must fail loudly here,
    # not pass vacuously because no sdypy/* entry exists at all.
    assert any(n.startswith(portion_prefix) for n in normalized), (
        "%s %s wheel ships no files under %s - the portion is missing or "
        "landed outside the namespace: %s" % (dist_name, version, portion_prefix, normalized)
    )
    offenders = [
        n for n in normalized
        if n.startswith("sdypy/") and not n.startswith(portion_prefix)
    ]
    assert not offenders, (
        "%s %s wheel ships files outside its own portion %s: %s"
        % (dist_name, version, portion_prefix, offenders)
    )


@pytest.mark.parametrize("dist_name", _SIBLING_DISTRIBUTIONS)
def test_sibling_version_resolvable_from_metadata(dist_name):
    """importlib.metadata must resolve a non-empty version for installed siblings."""
    try:
        version = importlib_metadata.version(dist_name)
    except importlib_metadata.PackageNotFoundError:
        pytest.skip("%s not installed in this environment" % dist_name)
    assert isinstance(version, str) and version
