"""Repo-layer nomenclature conformance checker (public-api spec, SEP 2).

Audits the public signatures of a first-level sdypy package clone against the
canonical variable table of SEP 2, without importing anything:
  * a public parameter or attribute whose name diverges from a canonical table
    entry is reported together with the name it should use,
  * a public index parameter must use the ``_idx`` suffix, never ``_ind``,
  * a bare ``n`` is not a count in a public signature (use ``n_<plural>``),
  * a public parameter must not be a single uppercase letter or an all-caps
    abbreviation - SEP 2 already binds parameters to snake_case.

Violations print to stdout as ``<file>: <rule>: <detail>`` and the script exits
non-zero.

Static analysis is deliberate, not a shortcut: ``sdypy.view`` and ``sdypy.model``
import pyvistaqt -> qtpy at package import time, so an import-and-introspect
checker cannot audit them without a Qt binding installed.

Coverage boundary - what this checker does NOT decide:
  * whether a newly coined compound name corresponds to an established term of
    art. SEP 2 makes the canonical table normative and the word-order guideline
    a heuristic that yields to established usage; deciding what is established
    is human judgement, tracked as `manual` in REQUIREMENTS.md.
  * whether a bare ``phi`` denotes a mode shape, a phase angle or a velocity
    potential, and whether a bare ``xi`` denotes a damping ratio or an element
    natural (isoparametric) coordinate. SEP 2 makes ``xi``/``eta``/``zeta`` canonical for
    element coordinates and ``damping_ratio`` canonical for damping, so the
    reading depends on what the routine computes - which static analysis cannot
    see. Only the unambiguous damping spellings ``nat_xi`` and ``pole_xi`` are
    enforced here. A bare ``xi`` used for damping, or a bare ``phi`` used for a
    mode shape, is left to the sibling suites. SEP 2 still forbids both: the
    rule is directional, and only its mechanical enforcement is dropped.
  * whether a deprecated alias emits ``DeprecationWarning`` and returns the same
    value as its canonical counterpart. That is runtime behaviour, verified by
    the sibling packages' own test suites.
  * names introduced by decorators or generated dynamically. Static analysis
    only sees plain ``def``/``class`` statements; the six first-level packages
    define their public surfaces that way today, but a sibling that changes
    that silently loses coverage here.
A name the canonical table says nothing about is never reported. The checker is
deliberately quiet about unknown names so that it stays enabled.

Usage:
    python tools/check_nomenclature.py --path ../sdypy-EMA

Kept separate from tools/check_public_api.py (which audits ``__all__``) on
purpose: the two checkers answer different questions and evolve independently.
"""
import argparse
import ast
import sys
from pathlib import Path

# Divergent spelling -> canonical name. Mirrors the "Instead of" column of the
# canonical variable table in docs/seps/sep-0002.rst; that column is the source
# of truth, this dict is the machine-readable mirror. tests/test_nomenclature.py
# pins the mirror in BOTH directions - no entry here that the SEP does not
# carry, and no SEP entry that is not enforced here - so neither side can drift.
CANONICAL = {
    # Modal quantities. A bare `xi` is deliberately absent: SEP 2 makes it a
    # canonical name for an element natural coordinate, so it cannot be reported
    # on sight. Only the unambiguous damping spellings are enforced.
    "nat_xi": "damping_ratio",
    "pole_xi": "damping_ratio",
    # A bare `phi` is absent for the same reason as a bare `xi`: it is the
    # standard symbol for a phase angle and for a velocity potential as well as
    # for a mode shape. `phi_X` and `phi_A` are unambiguous and stay.
    "phi_X": "mode_shape",
    "phi_A": "mode_shape",
    "nat_freq": "natural_freq",
    # System matrices
    "K": "stiffness_matrix",
    "M": "mass_matrix",
    "C": "damping_matrix",
    # `EI` is deliberately absent: it is a scalar bending rigidity (E*I), not a
    # stiffness matrix, and SEP 2's stiffness_matrix row explicitly disclaims it.
    # The parameter-case rule below still reports it as non-snake_case, without
    # inventing a wrong canonical name for it.
    # Mesh and geometry
    "org": "nodes",
    "conec": "elements",
    # Frequency
    "frequency": "freq",
    "sampling_frequency": "fs",
    "freq_sampling": "fs",
    "lower": "freq_lower",
    "f_lower": "freq_lower",
    "upper": "freq_upper",
    "f_upper": "freq_upper",
    "frf_type": "frf_form",
    # FEM material parameters, canonised by the previous SEP 2 round. Enforced
    # here too: the checker mirrors the whole table, not only its newest rows.
    "E": "young_modulus",
    "Young": "young_modulus",
    "nu": "poisson_ratio",
    "Poisson": "poisson_ratio",
    "rho": "density",
    "ro": "density",
    "Density": "density",
}

# SEP 2 exception: the established criterion functions keep the bare uppercase
# acronym as their name AND the modal-literature symbols as their arguments.
# Scoped to exactly these three names - `phi` anywhere else is a violation.
CRITERION_FUNCTIONS = {"MAC", "MSF", "MCF"}
CRITERION_ARGUMENTS = {"phi", "phi_X", "phi_A"}

# Arguments that never carry a caller-visible name.
IMPLICIT_ARGUMENTS = {"self", "cls"}


def find_portion_dir(clone_root):
    """Return (pkg_name, path) of the single sdypy portion in a sibling clone."""
    namespace_dir = Path(clone_root) / "sdypy"
    if not namespace_dir.is_dir():
        raise FileNotFoundError("no sdypy/ namespace dir under %s" % clone_root)
    portions = [
        d for d in namespace_dir.iterdir()
        if d.is_dir() and d.name != "__pycache__" and (d / "__init__.py").is_file()
    ]
    if len(portions) != 1:
        raise FileNotFoundError(
            "expected exactly one portion under %s, found: %s"
            % (namespace_dir, sorted(d.name for d in portions))
        )
    return portions[0].name, portions[0]


def iter_source_files(portion_dir):
    """Yield the public modules of a portion, skipping private ones."""
    for path in sorted(Path(portion_dir).rglob("*.py")):
        parts = path.relative_to(portion_dir).parts
        # Skip anything under a private package, and private modules, but keep
        # __init__.py - it is the public entry point despite its underscores.
        if any(p.startswith("_") and p != "__init__.py" for p in parts):
            continue
        yield path


def _is_public(name):
    return not name.startswith("_")


def parameter_names(node):
    """Return the caller-visible parameter names of a function node."""
    a = node.args
    names = [arg.arg for arg in a.posonlyargs + a.args + a.kwonlyargs]
    for extra in (a.vararg, a.kwarg):
        if extra is not None:
            names.append(extra.arg)
    return [n for n in names if n not in IMPLICIT_ARGUMENTS]


def self_attribute_names(func_node):
    """Return public names assigned to `self.<name>` inside a method."""
    found = []
    for node in ast.walk(func_node):
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for target in targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
                and _is_public(target.attr)
            ):
                found.append(target.attr)
    return found


def check_name(name, kind, where):
    """Return a list of (rule, detail) violations for one public name."""
    # The canonical table is checked first: when a name is both non-canonical
    # and mis-cased (K, M, EI), naming its replacement is the better message,
    # and reporting one violation twice would be noise.
    if name in CANONICAL:
        return [(
            "nomenclature",
            "%s %s %r is not canonical, use %r (SEP 2 table)"
            % (where, kind, name, CANONICAL[name]),
        )]
    if name.endswith("_ind"):
        return [(
            "index-suffix",
            "%s %s %r must use the '_idx' suffix (SEP 2), not '_ind'"
            % (where, kind, name),
        )]
    if name == "n":
        return [(
            "count-name",
            "%s %s 'n' must name what it counts, as 'n_<plural>' (SEP 2)"
            % (where, kind),
        )]
    if name.isupper() and name.isalpha():
        return [(
            "parameter-case",
            "%s %s %r must be snake_case (SEP 2); the table has no canonical "
            "entry for it, so choose a descriptive name" % (where, kind, name),
        )]
    return []


def check_function(node, label, violations, class_name=None):
    """Audit one public function or method."""
    qualified = "%s.%s" % (class_name, node.name) if class_name else node.name
    exempt = node.name in CRITERION_FUNCTIONS

    for name in parameter_names(node):
        if exempt and name in CRITERION_ARGUMENTS:
            continue
        for rule, detail in check_name(name, "parameter", "%s():" % qualified):
            violations.append("%s: %s: %s" % (label, rule, detail))

    for name in self_attribute_names(node):
        for rule, detail in check_name(name, "attribute", "%s():" % qualified):
            violations.append("%s: %s: %s" % (label, rule, detail))


def check_module(path, label):
    """Return a list of violation strings for one source file."""
    violations = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return ["%s: unparsable: %s" % (label, exc)]

    # Only module-level definitions carry a public surface: a nested def is an
    # implementation detail regardless of its name.
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not _is_public(node.name):
                continue
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _is_public(sub.name) or sub.name == "__init__":
                        check_function(sub, label, violations, class_name=node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(node.name):
                check_function(node, label, violations)
    return violations


def check_clone(clone_root):
    """Return a sorted list of violation strings for one sibling clone."""
    clone_root = Path(clone_root).resolve()
    _, portion_dir = find_portion_dir(clone_root)
    violations = []
    for path in iter_source_files(portion_dir):
        label = path.relative_to(clone_root).as_posix()
        violations.extend(check_module(path, label))
    return violations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path", default=".", type=Path,
        help="path to a sibling clone (the directory containing sdypy/<pkg>/)",
    )
    args = parser.parse_args(argv)

    try:
        violations = check_clone(args.path)
    except FileNotFoundError as exc:
        print("ERROR: %s" % exc)
        return 1

    for violation in violations:
        print(violation)
    if violations:
        return 1
    print("OK: %s conforms to the SEP 2 nomenclature contract" % args.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
