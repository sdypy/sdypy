"""Conformance tests for the sibling-package-template on-ramp and
supported-Python-set checks (`add-sibling-onramp` change).

Two layers, as for the other repo-layer checkers: `tools/check_sibling_template.py`
is the conformance authority; this module invokes its functions directly
against synthetic fixtures written to `tmp_path`, one test per new or changed
spec-delta scenario, named after the scenario it exercises. Each fixture
contains only the files the function under test reads - not a full sibling
clone - matching how `tests/test_nomenclature.py` and `tests/test_sep_governance.py`
test their own checkers.

Nothing here touches an installed distribution or a network resource, so no
test carries the `pypi_artifacts` marker - these run on every CI push.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# Single source of truth for the rules lives in the checker.
sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_sibling_template import (  # noqa: E402
    AGENTS_LINKS_END,
    AGENTS_LINKS_START,
    PYTHON_FLOOR,
    SHARED_RULES_END,
    SHARED_RULES_START,
    SUPPORTED_PYTHON,
    check_agents_md,
    check_claude_md,
    check_openspec_config,
    check_pyproject,
    check_test_workflow,
    extract_marker_block,
)

HUB_AGENTS_BLOCK = (
    "%s\n"
    "- [AGENTS.md](https://github.com/sdypy/sdypy/blob/main/AGENTS.md)\n"
    "- [REQUIREMENTS.md](https://github.com/sdypy/sdypy/blob/main/REQUIREMENTS.md)\n"
    "%s" % (AGENTS_LINKS_START, AGENTS_LINKS_END)
)

# The real marker carries a trailing note ("... - edit them there"); reproduced
# here so the substring-match behaviour of extract_marker_block is exercised.
HUB_RULES_BLOCK = (
    "  %s (openspec/config.yaml) - edit them there\n"
    "  proposal:\n"
    "    - State whether the change is trivial.\n"
    "  %s" % (SHARED_RULES_START, SHARED_RULES_END)
)


def write(root, rel_path, text):
    """Write `text` to `root / rel_path`, creating parent directories."""
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# extract_marker_block: the shared helper (task 2.1)
# --------------------------------------------------------------------------

def test_extract_marker_block_returns_none_when_a_marker_is_missing():
    assert extract_marker_block("no markers here", "<!-- >>> x -->", "<!-- <<< x -->") is None


def test_extract_marker_block_normalises_line_endings():
    text = "before\r\n<!-- >>> x -->\r\ncontent\r\n<!-- <<< x -->\r\nafter\r\n"
    block = extract_marker_block(text, "<!-- >>> x -->", "<!-- <<< x -->")
    assert block == "<!-- >>> x -->\ncontent\n<!-- <<< x -->"


def test_extract_marker_block_matches_a_marker_that_carries_trailing_text():
    block = extract_marker_block(HUB_RULES_BLOCK, SHARED_RULES_START, SHARED_RULES_END)
    assert block == HUB_RULES_BLOCK


# --------------------------------------------------------------------------
# AGENTS.md carries the hub's link block
# --------------------------------------------------------------------------

def test_agents_md_carries_the_hub_link_block(tmp_path):
    write(tmp_path, "AGENTS.md", "Router text.\n\n%s\n\nMore text.\n" % HUB_AGENTS_BLOCK)
    violations = []
    check_agents_md(tmp_path, HUB_AGENTS_BLOCK, violations)
    assert violations == []


def test_missing_agents_md_is_reported(tmp_path):
    violations = []
    check_agents_md(tmp_path, HUB_AGENTS_BLOCK, violations)
    assert violations == ["on-ramp: AGENTS.md missing"]


def test_agents_md_with_no_link_block_is_reported(tmp_path):
    write(tmp_path, "AGENTS.md", "No markers at all.\n")
    violations = []
    check_agents_md(tmp_path, HUB_AGENTS_BLOCK, violations)
    assert violations == ["on-ramp: AGENTS.md has no hub link block"]


def test_agents_md_with_an_edited_link_block_is_reported(tmp_path):
    edited = HUB_AGENTS_BLOCK.replace("AGENTS.md]", "agents.md]")
    write(tmp_path, "AGENTS.md", edited)
    violations = []
    check_agents_md(tmp_path, HUB_AGENTS_BLOCK, violations)
    assert violations == ["on-ramp: AGENTS.md link block does not match the hub's"]


def test_a_broken_hub_link_block_is_reported_not_silently_passed(tmp_path):
    """A hub-side regression (the hub's own AGENTS.md lost its marker block)
    must not read as every sibling conforming - it is reported even when the
    sibling's own AGENTS.md carries a perfectly good-looking block
    (review round 1, finding 3)."""
    write(tmp_path, "AGENTS.md", "Router text.\n\n%s\n\nMore text.\n" % HUB_AGENTS_BLOCK)
    violations = []
    check_agents_md(tmp_path, None, violations)
    assert len(violations) == 1
    assert "hub AGENTS.md link block not found" in violations[0]


# --------------------------------------------------------------------------
# Claude Code reads AGENTS.md
# --------------------------------------------------------------------------

def test_claude_md_is_the_one_line_pointer(tmp_path):
    write(tmp_path, "CLAUDE.md", "@AGENTS.md\n")
    violations = []
    check_claude_md(tmp_path, violations)
    assert violations == []


def test_claude_md_without_a_trailing_newline_is_accepted(tmp_path):
    write(tmp_path, "CLAUDE.md", "@AGENTS.md")
    violations = []
    check_claude_md(tmp_path, violations)
    assert violations == []


def test_missing_claude_md_is_reported(tmp_path):
    violations = []
    check_claude_md(tmp_path, violations)
    assert len(violations) == 1
    assert "CLAUDE.md" in violations[0]


def test_extended_claude_md_is_reported(tmp_path):
    write(tmp_path, "CLAUDE.md", "@AGENTS.md\nSee also README.rst.\n")
    violations = []
    check_claude_md(tmp_path, violations)
    assert len(violations) == 1
    assert "CLAUDE.md" in violations[0]


# --------------------------------------------------------------------------
# OpenSpec configuration carries the hub's shared rules
# --------------------------------------------------------------------------

def test_a_sibling_carries_the_shared_rules_unchanged(tmp_path):
    write(tmp_path, "openspec/config.yaml", "context: |\n  own context\n\nrules:\n%s\n" % HUB_RULES_BLOCK)
    violations = []
    check_openspec_config(tmp_path, "EMA", HUB_RULES_BLOCK, violations)
    assert violations == []


def test_a_drifted_rules_block_is_reported(tmp_path):
    drifted = HUB_RULES_BLOCK.replace("State whether the change is trivial.", "Say something else.")
    write(tmp_path, "openspec/config.yaml", "rules:\n%s\n" % drifted)
    violations = []
    check_openspec_config(tmp_path, "EMA", HUB_RULES_BLOCK, violations)
    assert violations == ["on-ramp: openspec/config.yaml shared rules do not match the hub's"]


def test_a_config_with_no_marker_block_is_reported(tmp_path):
    write(tmp_path, "openspec/config.yaml", "rules:\n  proposal: []\n")
    violations = []
    check_openspec_config(tmp_path, "EMA", HUB_RULES_BLOCK, violations)
    assert violations == ["on-ramp: openspec/config.yaml has no shared rules block"]


def test_a_missing_configuration_is_reported_for_a_non_shim_sibling(tmp_path):
    violations = []
    check_openspec_config(tmp_path, "EMA", HUB_RULES_BLOCK, violations)
    assert violations == ["on-ramp: openspec/config.yaml missing"]


@pytest.mark.parametrize("shim", ["FRF", "excitation"])
def test_a_shim_is_not_required_to_carry_openspec_configuration(tmp_path, shim):
    violations = []
    check_openspec_config(tmp_path, shim, HUB_RULES_BLOCK, violations)
    assert violations == []


def test_a_broken_hub_rules_block_is_reported_not_silently_passed(tmp_path):
    """Same masking risk as AGENTS.md: a hub-side regression in
    openspec/config.yaml must not read as every non-shim sibling conforming
    (review round 1, finding 3)."""
    write(tmp_path, "openspec/config.yaml", "context: |\n  own context\n\nrules:\n%s\n" % HUB_RULES_BLOCK)
    violations = []
    check_openspec_config(tmp_path, "EMA", None, violations)
    assert len(violations) == 1
    assert "hub openspec/config.yaml shared rules block not found" in violations[0]


def test_a_shim_stays_exempt_even_when_the_hub_rules_block_is_broken(tmp_path):
    """The shim exemption is checked first: a shim needs no openspec/config.yaml
    regardless of whether the hub's own block is intact."""
    violations = []
    check_openspec_config(tmp_path, "FRF", None, violations)
    assert violations == []


# --------------------------------------------------------------------------
# Canonical test workflow on the supported Python set
# --------------------------------------------------------------------------

BASE_WORKFLOW = """\
name: Python package

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: %(matrix)s

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: |
          %(install)s
      - name: Lint
        run: flake8 .
      - name: Test
        run: pytest
      - name: Build
        run: python -m build
"""


def write_workflow(tmp_path, install, matrix=None):
    """Write a minimal python-package.yml varying only install and matrix."""
    versions = matrix if matrix is not None else sorted(SUPPORTED_PYTHON)
    matrix_literal = "[" + ", ".join('"%s"' % v for v in versions) + "]"
    text = BASE_WORKFLOW % {"install": install, "matrix": matrix_literal}
    workflows_dir = tmp_path / ".github" / "workflows"
    write(workflows_dir, "python-package.yml", text)
    return workflows_dir


@pytest.mark.parametrize("install", [
    "pip install .",
    "pip install .[dev]",
    'pip install ".[dev]"',
    "pip install '.[dev]'",
    'pip install ".[dev,docs]"',
])
def test_pip_install_with_extras_is_accepted(tmp_path, install):
    workflows_dir = write_workflow(tmp_path, install)
    violations = []
    check_test_workflow(workflows_dir, violations)
    assert not any("must be installed via" in v for v in violations)


def test_requirements_txt_is_still_rejected(tmp_path):
    workflows_dir = write_workflow(tmp_path, "pip install -r requirements.txt")
    violations = []
    check_test_workflow(workflows_dir, violations)
    assert any("references a requirements file" in v for v in violations)


def test_matrix_not_covering_the_supported_set_is_reported(tmp_path):
    workflows_dir = write_workflow(tmp_path, "pip install .", matrix=["3.11", "3.12"])
    violations = []
    check_test_workflow(workflows_dir, violations)
    assert any("does not cover the supported set" in v for v in violations)


def test_matrix_covering_the_supported_set_passes(tmp_path):
    workflows_dir = write_workflow(tmp_path, "pip install .")
    violations = []
    check_test_workflow(workflows_dir, violations)
    assert not any("does not cover" in v for v in violations)


# --------------------------------------------------------------------------
# Metadata consistency with the supported Python set
# --------------------------------------------------------------------------

CONFORMING_PYPROJECT = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sdypy-EMA"
version = "1.0.0"
requires-python = "%(floor)s"
license = {text = "MIT"}
readme = {file = "README.rst"}
classifiers = [
%(classifiers)s
    "License :: OSI Approved :: MIT License",
    "Development Status :: 4 - Beta",
]

[project.urls]
Homepage = "https://github.com/ladisk/sdypy-EMA"
Source = "https://github.com/ladisk/sdypy-EMA"

[project.optional-dependencies]
docs = ["sphinx"]
dev = ["pytest", "sdypy-EMA[docs]"]

[tool.hatch.build.targets.wheel]
packages = ["sdypy"]

[tool.hatch.build.targets.sdist]
include = ["sdypy"]
"""


def write_pyproject(tmp_path, floor=None, classifiers=None):
    """Write a conforming pyproject.toml, varying only floor and classifiers."""
    (tmp_path / "README.rst").write_text("readme\n", encoding="utf-8")
    versions = classifiers if classifiers is not None else sorted(SUPPORTED_PYTHON)
    classifiers_block = "\n".join(
        '    "Programming Language :: Python :: %s",' % v for v in versions
    )
    text = CONFORMING_PYPROJECT % {
        "floor": floor or (">=%s" % PYTHON_FLOOR),
        "classifiers": classifiers_block,
    }
    write(tmp_path, "pyproject.toml", text)


def test_requires_python_floor_is_the_oldest_supported_version(tmp_path):
    write_pyproject(tmp_path)
    violations = []
    check_pyproject(tmp_path, "EMA", violations)
    assert violations == []


def test_wrong_requires_python_floor_is_reported(tmp_path):
    write_pyproject(tmp_path, floor=">=3.10")
    violations = []
    check_pyproject(tmp_path, "EMA", violations)
    assert any("requires-python" in v for v in violations)


def test_classifiers_not_matching_the_supported_set_are_reported(tmp_path):
    write_pyproject(tmp_path, classifiers=["3.10", "3.11", "3.12"])
    violations = []
    check_pyproject(tmp_path, "EMA", violations)
    assert any("do not match the supported set" in v for v in violations)
