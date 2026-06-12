"""Distribution-layer conformance tests for the public-api contract.

Enforces the contract from the standardize-public-api change (amended SEP 2):
  * every first-level package declares a non-empty, resolvable __all__,
  * no third-party / stdlib name leaks into a curated surface,
  * module-type entries appear only where sanctioned,
  * the umbrella's __all__ is exactly the six first-level names,
  * the shim drift check is advisory (never fails).

NOTE: these tests run against the INSTALLED distributions. They are
expected-red against the packages currently published on PyPI (which predate
the public-api contract) and flip green per package as the batched releases
ship - same accepted pattern as the standardize-package-template tests.
"""
import inspect
import subprocess
import sys
from pathlib import Path

import pytest

import sdypy
from sdypy import _SUBPACKAGES

# Single source of truth for curated lists + drift logic lives in the checker.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from check_public_api import CURATED, SHIM_BACKENDS  # noqa: E402

BANNED_LEAK_NAMES = {
    "np", "scipy", "warnings", "os", "io", "platform", "subprocess", "pickle",
    "tqdm", "pv", "CubicSpline", "beta", "moment", "signal", "signals",
    "BackgroundPlotter", "BasePlotter", "haspyqt", "Image", "pyperclip",
}

# Names in a first-level __all__ that may resolve to module objects.
SANCTIONED_MODULE_ENTRIES = {
    "io": {"uff", "lvm", "mraw", "sfmov"},
    "EMA": {"stabilization", "normal_modes", "pole_picking"},
    "model": {"lumped", "mesh"},
}


def _import_or_skip(name):
    module = getattr(sdypy, name, None)
    if module is None:
        pytest.skip("sdypy.%s not installed in this environment" % name)
    return module


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_subpackage_declares_nonempty_all(name):
    module = _import_or_skip(name)
    declared = getattr(module, "__all__", None)
    assert isinstance(declared, list) and declared, (
        "sdypy.%s must declare a non-empty __all__ list" % name
    )


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_every_all_entry_resolves(name):
    module = _import_or_skip(name)
    declared = getattr(module, "__all__", None) or []
    unresolved = []
    for entry in declared:
        try:
            getattr(module, entry)
        except AttributeError:
            unresolved.append(entry)
    assert not unresolved, (
        "sdypy.%s __all__ contains unresolvable names: %s" % (name, unresolved)
    )


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_no_banned_leak_names_in_all(name):
    """The banned list applies to the six first-level packages only - the
    umbrella's __all__ legitimately contains 'io' (the sub-package name)."""
    module = _import_or_skip(name)
    declared = set(getattr(module, "__all__", None) or [])
    leaked = sorted(declared & BANNED_LEAK_NAMES)
    assert not leaked, "sdypy.%s __all__ leaks banned names: %s" % (name, leaked)


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_module_entries_only_where_sanctioned(name):
    module = _import_or_skip(name)
    declared = getattr(module, "__all__", None) or []
    sanctioned = SANCTIONED_MODULE_ENTRIES.get(name, set())
    offenders = [
        entry for entry in declared
        if inspect.ismodule(getattr(module, entry, None)) and entry not in sanctioned
    ]
    assert not offenders, (
        "sdypy.%s __all__ exposes unsanctioned module objects: %s" % (name, offenders)
    )


@pytest.mark.parametrize("name", _SUBPACKAGES)
@pytest.mark.pypi_artifacts
def test_curated_surface_matches_spec(name):
    module = _import_or_skip(name)
    declared = sorted(getattr(module, "__all__", None) or [])
    assert declared == sorted(CURATED[name]), (
        "sdypy.%s __all__ diverges from the public-api spec list" % name
    )


def test_umbrella_all_is_exactly_the_six_names():
    assert sorted(sdypy.__all__) == sorted(_SUBPACKAGES)
    assert set(_SUBPACKAGES) <= set(dir(sdypy))  # __dir__ consistency


def test_star_import_of_umbrella_yields_six_subpackages():
    """`from sdypy import *` is an explicit ask for everything: the six names
    (and nothing unexpected) land in the importing namespace. Fresh interpreter
    so the eager import cannot contaminate other tests."""
    code = (
        "ns = {}; exec('from sdypy import *', ns); "
        "got = sorted(k for k in ns if not k.startswith('_')); "
        "print(','.join(got))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    got = result.stdout.strip().splitlines()[-1].split(",")
    assert sorted(got) == sorted(_SUBPACKAGES), got


@pytest.mark.parametrize("name", sorted(SHIM_BACKENDS))
def test_shim_drift_check_is_advisory(name, capsys):
    """The drift check reports uncurated backend callables but never fails."""
    from check_public_api import drift_report

    drift_report(name, CURATED[name])  # must not raise regardless of drift
    out = capsys.readouterr().out
    assert "DRIFT [%s]" % name in out
