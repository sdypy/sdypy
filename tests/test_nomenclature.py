"""Conformance tests for the SEP 2 nomenclature contract (public-api spec).

Two layers, deliberately split by the `pypi_artifacts` marker:

* **Unit tests** exercise `tools/check_nomenclature.py` against synthetic
  fixtures written to `tmp_path`. They need no first-level package installed
  and no Qt binding, so they run on every CI push.
* **Conformance tests** audit the *installed* first-level packages and carry
  the `pypi_artifacts` marker, so GitHub CI deselects them. They are the local
  pre-release gate: a sibling that publishes a divergent public name is caught
  before the next release, without reddening core CI for work that belongs in
  six other repositories.

The checker is the conformance authority; this module invokes the same
functions so a plain `pytest` run fails on the same conditions CI does.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SEP2 = REPO_ROOT / "docs" / "seps" / "sep-0002.rst"

# Single source of truth for the rules lives in the checker.
sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_nomenclature import (  # noqa: E402
    CANONICAL,
    CRITERION_ARGUMENTS,
    CRITERION_FUNCTIONS,
    check_clone,
)

FIRST_LEVEL = ("EMA", "io", "FRF", "excitation", "view", "model")


def write_clone(tmp_path, source, pkg="EMA"):
    """Materialise a one-portion sibling clone containing `source`."""
    portion = tmp_path / "sdypy" / pkg
    portion.mkdir(parents=True)
    (portion / "__init__.py").write_text(source, encoding="utf-8")
    return tmp_path


def rules(violations):
    """Return the rule names of a violation list, e.g. {'nomenclature'}."""
    return {v.split(": ")[1] for v in violations}


# --------------------------------------------------------------------------
# Layer one: the checker's own logic, on synthetic fixtures
# --------------------------------------------------------------------------

CONFORMING = '''\
"""A portion whose public surface uses only canonical names."""


def solve_eigenvalue(stiffness_matrix, mass_matrix, n_modes=10):
    return stiffness_matrix, mass_matrix, n_modes


class Model:
    def __init__(self, frf, freq, freq_lower, freq_upper, frf_form="receptance"):
        self.natural_freq = []
        self.damping_ratio = []
        self.mode_shape = None

    def add_mesh(self, nodes, elements, node_idx=0):
        return nodes, elements, node_idx
'''


def test_conforming_clone_passes(tmp_path):
    assert check_clone(write_clone(tmp_path, CONFORMING)) == []


def test_non_canonical_parameter_is_reported(tmp_path):
    src = "def damp(nat_xi):\n    return nat_xi\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert len(violations) == 1
    assert "damping_ratio" in violations[0]
    assert rules(violations) == {"nomenclature"}


@pytest.mark.parametrize(
    "name, canonical",
    [("phi_X", "mode_shape"), ("K", "stiffness_matrix"), ("M", "mass_matrix"),
     ("conec", "elements"), ("org", "nodes"), ("frequency", "freq"),
     ("lower", "freq_lower"), ("f_upper", "freq_upper"), ("frf_type", "frf_form")],
)
def test_each_divergent_spelling_names_its_replacement(tmp_path, name, canonical):
    src = "def f(%s):\n    return %s\n" % (name, name)
    violations = check_clone(write_clone(tmp_path, src))
    assert len(violations) == 1
    assert canonical in violations[0]


def test_non_canonical_attribute_is_reported(tmp_path):
    src = "class Model:\n    def solve(self):\n        self.nat_freq = []\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert len(violations) == 1
    assert "natural_freq" in violations[0]
    assert "attribute" in violations[0]


def test_index_suffix_ind_is_reported(tmp_path):
    src = "def pick(lower_ind):\n    return lower_ind\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert rules(violations) == {"index-suffix"}
    assert "_idx" in violations[0]


def test_idx_suffix_is_accepted(tmp_path):
    src = "def pick(node_idx):\n    return node_idx\n"
    assert check_clone(write_clone(tmp_path, src)) == []


def test_bare_n_is_reported_as_a_count(tmp_path):
    src = "def solve(n):\n    return n\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert rules(violations) == {"count-name"}
    assert "n_<plural>" in violations[0]


def test_n_plural_is_accepted(tmp_path):
    src = "def solve(n_modes, n_nodes):\n    return n_modes, n_nodes\n"
    assert check_clone(write_clone(tmp_path, src)) == []


def test_uppercase_abbreviation_is_reported(tmp_path):
    src = "def bend(EI):\n    return EI\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert rules(violations) == {"parameter-case"}
    # EI is a scalar bending rigidity, not a stiffness matrix: the checker must
    # not invent a canonical name it does not have.
    assert "stiffness_matrix" not in violations[0]


def test_criterion_functions_keep_the_literature_symbols(tmp_path):
    src = (
        "def MAC(phi_X, phi_A):\n    return phi_X, phi_A\n\n"
        "def MSF(phi_X, phi_A):\n    return phi_X, phi_A\n\n"
        "def MCF(phi):\n    return phi\n"
    )
    assert check_clone(write_clone(tmp_path, src)) == []


def test_the_exception_does_not_extend_beyond_the_criterion_functions(tmp_path):
    src = "def correlate(phi_X, phi_A):\n    return phi_X, phi_A\n"
    violations = check_clone(write_clone(tmp_path, src))
    assert len(violations) == 2
    assert all("mode_shape" in v for v in violations)


def test_private_names_are_not_audited(tmp_path):
    src = (
        "def _helper(xi, K):\n    return xi, K\n\n"
        "class _Internal:\n    def __init__(self, phi):\n        self.nat_freq = phi\n"
    )
    assert check_clone(write_clone(tmp_path, src)) == []


def test_local_variables_are_not_audited(tmp_path):
    src = "def solve(stiffness_matrix):\n    K = stiffness_matrix\n    return K\n"
    assert check_clone(write_clone(tmp_path, src)) == []


def test_unknown_names_are_never_reported(tmp_path):
    """The checker stays quiet about names the canonical table does not cover."""
    src = "def excite(burst_length, kurtosis_target, spectral_moment):\n    return 0\n"
    assert check_clone(write_clone(tmp_path, src)) == []


def test_missing_namespace_dir_is_an_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        check_clone(tmp_path)


# --------------------------------------------------------------------------
# Layer one: the mirror cannot drift away from SEP 2
# --------------------------------------------------------------------------

def sep2_instead_of_spellings():
    """Return the divergent spellings in SEP 2's "Instead of" column.

    The column is the source of truth for the migration map; `CANONICAL` is its
    mirror. Parsing the `list-table` is why the table is a `list-table`: one
    cell per line, no grid rules to reassemble.
    """
    lines = SEP2.read_text(encoding="utf-8").split("\n")
    start = lines.index(".. list-table::")
    rows, cur = [], None
    for line in lines[start:]:
        if line.startswith("   * - "):
            if cur is not None:
                rows.append(cur)
            cur = [line[7:].strip()]
        elif line.startswith("     - "):
            cur.append(line[7:].strip())
        elif line == "     -":
            cur.append("")
        elif cur is not None and not line.startswith(("   ", ".. list-table")):
            break
    if cur is not None:
        rows.append(cur)

    header, body = rows[0], rows[1:]
    column = header.index("Instead of")
    spellings = set()
    for row in body:
        cell = row[column]
        if not cell:
            continue
        spellings.update(part.strip().strip("`") for part in cell.split(","))
    return {name for name in spellings if name}


def test_sep2_instead_of_column_parses():
    """Guard the parser itself: a silently empty parse would pass every mirror
    test below, so assert the column is found and populated."""
    spellings = sep2_instead_of_spellings()
    assert len(spellings) > 15, sorted(spellings)
    assert "nat_freq" in spellings
    assert "conec" in spellings


def test_every_canonical_name_appears_in_sep2():
    """The checker must never enforce a target name SEP 2 has not ratified."""
    text = SEP2.read_text(encoding="utf-8")
    missing = sorted({name for name in CANONICAL.values() if name not in text})
    assert not missing, "checker enforces names absent from SEP 2: %s" % missing


def test_every_enforced_spelling_appears_in_sep2():
    """No checker-only rename.

    This is the assertion the module lacked. Pinning only the target names let
    the checker invent the left-hand side of the map, which is how a blanket
    `xi` -> `damping_ratio` rule got in and started reporting finite-element
    shape-function coordinates as violations.
    """
    unratified = sorted(set(CANONICAL) - sep2_instead_of_spellings())
    assert not unratified, (
        "checker enforces renames absent from SEP 2's \"Instead of\" column: %s"
        % unratified
    )


def test_every_sep2_spelling_is_enforced():
    """No SEP entry the checker quietly ignores."""
    unenforced = sorted(sep2_instead_of_spellings() - set(CANONICAL))
    assert not unenforced, (
        "SEP 2 requires renames the checker does not enforce: %s" % unenforced
    )


def test_bare_phi_is_not_enforced_as_a_mode_shape_spelling():
    """`phi` is the standard symbol for a phase angle and a velocity potential
    as well as for a mode shape.

    Enforcing it would tell a maintainer to rename the velocity potential of
    `model.acoustic_external` to `mode_shape`. SEP 2 still forbids `phi` for a
    mode shape - that rule is directional, and only the mechanical enforcement
    of a name the checker cannot classify is dropped.
    """
    assert "phi" not in CANONICAL
    assert CANONICAL["phi_X"] == "mode_shape"
    assert CANONICAL["phi_A"] == "mode_shape"


def test_velocity_potential_named_phi_is_not_reported(tmp_path):
    src = "def solve_problem(freq):\n    phi = 0.0\n    return phi\n"
    assert check_clone(write_clone(tmp_path, src, pkg="model")) == []


def test_bare_xi_is_not_enforced_as_a_damping_spelling():
    """SEP 2 makes `xi` canonical for element natural coordinates.

    Enforcing it as a damping spelling would tell a maintainer to rename
    `shape_functions(xi, eta)`, which would be wrong. The damping spellings that
    *are* unambiguous are enforced in its place.
    """
    assert "xi" not in CANONICAL
    assert CANONICAL["nat_xi"] == "damping_ratio"
    assert CANONICAL["pole_xi"] == "damping_ratio"


def test_element_coordinates_are_not_reported(tmp_path):
    src = "def shape_functions(xi, eta, zeta):\n    return xi, eta, zeta\n"
    assert check_clone(write_clone(tmp_path, src, pkg="model")) == []


def test_ei_is_reported_without_a_canonical_name(tmp_path):
    """`EI` is a scalar bending rigidity, not a stiffness matrix."""
    src = "def matrices_k_e(EI, length):\n    return EI * length\n"
    violations = check_clone(write_clone(tmp_path, src, pkg="model"))
    assert len(violations) == 1, violations
    assert "EI" in violations[0]
    assert "stiffness_matrix" not in violations[0]
    assert "EI" not in CANONICAL


def test_criterion_exception_is_documented_in_sep2():
    text = SEP2.read_text(encoding="utf-8")
    for name in sorted(CRITERION_FUNCTIONS | CRITERION_ARGUMENTS):
        assert name in text, "%s is exempted by the checker but absent from SEP 2" % name


# --------------------------------------------------------------------------
# Layer two: the installed first-level packages (local pre-release gate)
# --------------------------------------------------------------------------

def installed_portion(name):
    """Return the path of an installed first-level portion, or None."""
    try:
        spec = importlib.util.find_spec("sdypy.%s" % name)
    except (ImportError, ValueError):  # pragma: no cover - defensive
        return None
    if spec is None or not spec.origin:
        return None
    return Path(spec.origin).parent


@pytest.mark.pypi_artifacts
@pytest.mark.parametrize("name", FIRST_LEVEL)
def test_installed_package_uses_canonical_names(tmp_path, name):
    portion = installed_portion(name)
    if portion is None:
        pytest.skip("sdypy-%s is not installed" % name)

    # A one-portion clone view, so the checker resolves exactly this package.
    (tmp_path / "sdypy").mkdir()
    (tmp_path / "sdypy" / name).symlink_to(portion, target_is_directory=True)

    violations = check_clone(tmp_path)
    assert not violations, "sdypy-%s diverges from the SEP 2 nomenclature:\n%s" % (
        name, "\n".join(violations)
    )
