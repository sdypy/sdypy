"""Repo-layer public-API conformance checker (public-api spec).

Audits a sibling clone's ``sdypy/<pkg>/__init__.py`` without importing it:
  * an explicit, non-empty ``__all__`` literal is present,
  * no ``import *`` line exists,
  * the ``__all__`` content matches the curated list from the public-api spec.

Violations print to stdout and the script exits non-zero.

For the two backend shims (FRF, excitation) it additionally runs an ADVISORY
drift check: backend public callables missing from the curated ``__all__`` are
reported so they get a conscious curation decision, but never affect the exit
code. Drift requires the backend to be importable in the running environment;
if it is not, the drift check is skipped with a notice.

Usage:
    python tools/check_public_api.py --path ../packages/sdypy-EMA

Kept separate from tools/check_sibling_template.py (packaging-file contract)
on purpose: the two checkers evolve independently.
"""
import argparse
import ast
import importlib
import sys
from pathlib import Path

# Curated public surfaces - mirrors openspec/specs (public-api capability).
CURATED = {
    "EMA": [
        "Model", "MAC", "MSF", "MCF", "complex_freq_to_freq_and_damp",
        "stabilization", "normal_modes", "pole_picking",
    ],
    "io": ["uff", "lvm", "mraw", "sfmov"],
    "FRF": ["FRF", "assert_sep005", "direction_dict"],
    "excitation": [
        "burst_random", "get_kurtosis", "get_psd", "impulse",
        "nonstationary_signal", "normal_random", "pseudo_random",
        "random_gaussian", "sine_sweep", "stationary_nongaussian_signal",
        "uniform_random",
    ],
    "view": [
        "Plotter3D", "create_fem_mesh", "prepare_animation_displacements",
        "prepare_animation_field", "copy_image_to_clipboard",
    ],
    "model": ["Beam", "Shell", "Tetrahedron", "solve_eigenvalue", "lumped", "mesh"],
}

# Shim packages whose curated list is a deliberate subset of a backend.
SHIM_BACKENDS = {"FRF": "pyFRF", "excitation": "pyExSi"}


def find_portion_init(clone_root):
    """Return (pkg_name, path to sdypy/<pkg>/__init__.py) for a sibling clone."""
    namespace_dir = clone_root / "sdypy"
    if not namespace_dir.is_dir():
        raise FileNotFoundError("no sdypy/ namespace dir under %s" % clone_root)
    portions = [
        d for d in namespace_dir.iterdir()
        if d.is_dir() and d.name != "__pycache__" and (d / "__init__.py").is_file()
    ]
    if len(portions) != 1:
        raise FileNotFoundError(
            "expected exactly one portion under %s, found: %s"
            % (namespace_dir, [d.name for d in portions])
        )
    return portions[0].name, portions[0] / "__init__.py"


def extract_all_literal(tree):
    """Return the list assigned to __all__ at module level, or None."""
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    value = ast.literal_eval(node.value)
                except ValueError:
                    return None
                return list(value) if isinstance(value, (list, tuple)) else None
    return None


def star_import_lines(tree):
    """Return the line numbers of any `from X import *` statements."""
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and any(alias.name == "*" for alias in node.names)
    ]


def drift_report(pkg, curated):
    """Advisory: backend public callables not in the shim's curated __all__."""
    backend_name = SHIM_BACKENDS[pkg]
    try:
        backend = importlib.import_module(backend_name)
    except ImportError as exc:
        print("DRIFT [%s]: backend %s not importable, skipped (%s)" % (pkg, backend_name, exc))
        return
    uncurated = sorted(
        name for name in dir(backend)
        if not name.startswith("_")
        and callable(getattr(backend, name))
        and not isinstance(getattr(backend, name), type(importlib))
        and name not in curated
    )
    if uncurated:
        print(
            "DRIFT [%s]: %s exposes public callables not curated in __all__ "
            "(advisory, decide whether to re-export): %s"
            % (pkg, backend_name, ", ".join(uncurated))
        )
    else:
        print("DRIFT [%s]: no uncurated %s callables" % (pkg, backend_name))


def check_clone(clone_root):
    """Return a list of violation strings for one sibling clone."""
    violations = []
    pkg, init_path = find_portion_init(clone_root)
    if pkg not in CURATED:
        return ["%s: unknown first-level package %r" % (clone_root, pkg)]
    tree = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))

    stars = star_import_lines(tree)
    if stars:
        violations.append(
            "%s: `import *` found on line(s) %s - shims must re-export explicitly"
            % (init_path, stars)
        )

    declared = extract_all_literal(tree)
    if declared is None:
        violations.append("%s: no literal __all__ assignment found" % init_path)
    elif not declared:
        violations.append("%s: __all__ is empty" % init_path)
    elif sorted(declared) != sorted(CURATED[pkg]):
        missing = sorted(set(CURATED[pkg]) - set(declared))
        extra = sorted(set(declared) - set(CURATED[pkg]))
        violations.append(
            "%s: __all__ does not match the curated public-api list "
            "(missing: %s, extra: %s)" % (init_path, missing or "-", extra or "-")
        )

    if pkg in SHIM_BACKENDS:
        drift_report(pkg, CURATED[pkg])
    return violations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path", required=True, type=Path,
        help="path to a sibling clone (the directory containing sdypy/<pkg>/)",
    )
    args = parser.parse_args(argv)

    try:
        violations = check_clone(args.path.resolve())
    except FileNotFoundError as exc:
        print("ERROR: %s" % exc)
        return 1

    if violations:
        for violation in violations:
            print("VIOLATION: %s" % violation)
        return 1
    print("OK: %s conforms to the public-api contract" % args.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
