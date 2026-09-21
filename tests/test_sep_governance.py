"""Repo-layer conformance tests for the sep-governance contract (SEP 0 metadata).

Two layers, as for the other checkers: `tools/check_seps.py` is the conformance
authority and CI runs it directly; this module invokes the same functions so a
plain `pytest` run also fails on a non-conforming SEP set.

Nothing here touches a published wheel, so no test carries the
`pypi_artifacts` marker - these must run on every CI push.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SEPS_DIR = REPO_ROOT / "docs" / "seps"

# Single source of truth for the rules lives in the checker.
sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_seps import (  # noqa: E402
    STATUS_VOCABULARY,
    TYPE_VOCABULARY,
    check_repo,
    check_sep_file,
    check_template_file,
    parse_preamble,
)

CONFORMING = """\
====================
SEP 9 — Something
====================

:Authors: A Person <a@example.org>
:Status: Draft
:Type: Process
:Created: 2026-08-19


Abstract
--------
Body text, which may contain :Status: lookalikes.
"""


def write_sep(tmp_path, text, name="sep-0009.rst"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def rules(violations):
    """The rule component of each `<file>: <rule>: <detail>` violation line."""
    return [v.split(": ")[1] for v in violations]


# --- the repository itself ------------------------------------------------

def test_all_seps_conform():
    violations = check_repo(REPO_ROOT)
    assert not violations, "SEP metadata violations:\n" + "\n".join(violations)


def test_template_declares_vocabularies():
    violations = check_template_file(SEPS_DIR / "sep-template.rst")
    assert not violations, "\n".join(violations)


# --- the parser -----------------------------------------------------------

def test_parser_reads_the_preamble(tmp_path):
    fields = parse_preamble(CONFORMING)
    assert fields == {
        "Authors": "A Person <a@example.org>",
        "Status": "Draft",
        "Type": "Process",
        "Created": "2026-08-19",
    }


def test_multi_line_authors_is_read_in_full():
    """sep-0004's :Authors: continues onto two indented lines."""
    fields = parse_preamble((SEPS_DIR / "sep-0004.rst").read_text(encoding="utf-8"))
    for author in ("Janko Slavič", "Klemen Zaletelj", "Domen Gorjup"):
        assert author in fields["Authors"]


def test_parser_stops_at_the_end_of_the_preamble():
    """A field-list lookalike in the prose is not mistaken for a header field."""
    fields = parse_preamble(CONFORMING + "\n:Bogus: not a header field\n")
    assert "Bogus" not in fields


# --- one test per rule ----------------------------------------------------

def test_missing_field_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Created: 2026-08-19\n", ""))
    violations = check_sep_file(path)
    assert rules(violations) == ["missing-field"]
    assert ":Created:" in violations[0]


def test_deprecated_author_spelling_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Authors:", ":Author:"))
    violations = check_sep_file(path)
    # Reported once as the deprecated spelling, not also as a missing field.
    assert rules(violations) == ["deprecated-field"]
    assert ":Authors:" in violations[0]


def test_accepted_without_resolution_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Status: Draft", ":Status: Accepted"))
    violations = check_sep_file(path)
    assert rules(violations) == ["missing-resolution"]


def test_accepted_with_resolution_conforms(tmp_path):
    text = CONFORMING.replace(
        ":Status: Draft", ":Status: Accepted\n:Resolution: https://example.org/minutes"
    )
    assert check_sep_file(write_sep(tmp_path, text)) == []


def test_unknown_status_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Status: Draft", ":Status: In progress"))
    violations = check_sep_file(path)
    assert rules(violations) == ["status-vocabulary"]
    assert "In progress" in violations[0]
    for permitted in STATUS_VOCABULARY:
        assert permitted in violations[0]


def test_miscased_status_is_reported(tmp_path):
    """The index template matches Status by exact string equality."""
    path = write_sep(tmp_path, CONFORMING.replace(":Status: Draft", ":Status: draft"))
    assert rules(check_sep_file(path)) == ["status-vocabulary"]


def test_out_of_vocabulary_type_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Type: Process", ":Type: Standards"))
    violations = check_sep_file(path)
    assert rules(violations) == ["type-vocabulary"]
    assert "Standards" in violations[0]
    for permitted in TYPE_VOCABULARY:
        assert permitted in violations[0]


def test_non_iso_date_is_reported(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Created: 2026-08-19", ":Created: 2-Nov-2020"))
    violations = check_sep_file(path)
    assert rules(violations) == ["created-format"]
    assert "2-Nov-2020" in violations[0]


@pytest.mark.parametrize("value", ["20260819", "2026-13-01", "2026-8-19"])
def test_other_non_iso_dates_are_reported(tmp_path, value):
    path = write_sep(tmp_path, CONFORMING.replace("2026-08-19", value))
    assert rules(check_sep_file(path)) == ["created-format"]


def test_conforming_sep_has_no_violations(tmp_path):
    assert check_sep_file(write_sep(tmp_path, CONFORMING)) == []


def test_violations_name_the_file(tmp_path):
    path = write_sep(tmp_path, CONFORMING.replace(":Status: Draft", ":Status: draft"))
    assert check_sep_file(path, "docs/seps/sep-0009.rst")[0].startswith(
        "docs/seps/sep-0009.rst: "
    )


# --- the template rules ---------------------------------------------------

def test_template_missing_a_status_value_is_reported(tmp_path):
    text = (SEPS_DIR / "sep-template.rst").read_text(encoding="utf-8")
    path = write_sep(tmp_path, text.replace("Provisional | ", ""), "sep-template.rst")
    violations = check_template_file(path)
    assert rules(violations) == ["template-status-vocabulary"]
    assert "Provisional" in violations[0]


def test_template_missing_a_type_value_is_reported(tmp_path):
    text = (SEPS_DIR / "sep-template.rst").read_text(encoding="utf-8")
    path = write_sep(tmp_path, text.replace("Informational | ", ""), "sep-template.rst")
    violations = check_template_file(path)
    assert rules(violations) == ["template-type-vocabulary"]
    assert "Informational" in violations[0]


def test_template_deprecated_author_field_is_reported(tmp_path):
    text = (SEPS_DIR / "sep-template.rst").read_text(encoding="utf-8")
    path = write_sep(tmp_path, text.replace(":Authors:", ":Author:"), "sep-template.rst")
    assert rules(check_template_file(path)) == ["template-authors-field"]
