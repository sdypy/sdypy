"""Tests for the one-step release workflow (`one-step-release` change).

The workflow file `.github/workflows/release-and-publish-to-pypi.yml` is the
hub's, and every first-level package copies it verbatim. Three layers are
tested here, one test per spec-delta scenario where it can be exercised
offline:

- the sibling template checker compares a sibling's copy with the hub's;
- the hub's workflow has the required triggers and steps;
- the two Python guards embedded in the workflow (the version bump and the
  distribution check) are extracted and run against fixtures in `tmp_path`,
  so the code tested is the code the workflow runs.

Nothing here touches a network resource or a published distribution.
"""
import os
import re
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "release-and-publish-to-pypi.yml"
WORKFLOW_TEXT = WORKFLOW.read_text(encoding="utf-8")

sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_sibling_template import (  # noqa: E402
    AGENTS_LINKS_END,
    AGENTS_LINKS_START,
    RELEASE_WORKFLOW,
    check_release_workflow,
    extract_marker_block,
)


def write(root, rel_path, text):
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


# --------------------------------------------------------------------------
# Canonical release workflow: a sibling copies the hub's file verbatim
# --------------------------------------------------------------------------

def sibling_workflows(tmp_path, text):
    workflows_dir = tmp_path / ".github" / "workflows"
    write(workflows_dir, RELEASE_WORKFLOW, text)
    return workflows_dir


def test_a_verbatim_copy_of_the_hub_workflow_passes(tmp_path):
    violations = []
    check_release_workflow(sibling_workflows(tmp_path, WORKFLOW_TEXT), violations)
    assert violations == []


def test_a_copy_differing_only_in_line_endings_passes(tmp_path):
    violations = []
    crlf = WORKFLOW_TEXT.replace("\n", "\r\n")
    check_release_workflow(sibling_workflows(tmp_path, crlf), violations)
    assert violations == []


def test_a_drifted_copy_is_reported(tmp_path):
    violations = []
    drifted = WORKFLOW_TEXT.replace('python-version: "3.13"', 'python-version: "3.14"')
    assert drifted != WORKFLOW_TEXT
    check_release_workflow(sibling_workflows(tmp_path, drifted), violations)
    assert any("differs from the hub's release workflow" in v for v in violations)


def test_the_old_tag_triggered_workflow_is_reported(tmp_path):
    old = 'on:\n  push:\n    tags:\n      - "v*"\njobs: {}\n'
    violations = []
    check_release_workflow(sibling_workflows(tmp_path, old), violations)
    assert any("differs from the hub's release workflow" in v for v in violations)


def test_a_missing_release_workflow_is_reported(tmp_path):
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    violations = []
    check_release_workflow(workflows_dir, violations)
    assert violations == ["workflows: %s missing" % RELEASE_WORKFLOW]


def test_an_underscore_named_release_workflow_is_reported(tmp_path):
    workflows_dir = sibling_workflows(tmp_path, WORKFLOW_TEXT)
    write(workflows_dir, "release_and_publish_to_pypi.yml", WORKFLOW_TEXT)
    violations = []
    check_release_workflow(workflows_dir, violations)
    assert any("underscore-named" in v for v in violations)


def test_an_unreadable_hub_copy_is_reported_not_silently_passed(tmp_path, monkeypatch):
    import check_sibling_template
    monkeypatch.setattr(check_sibling_template, "_hub_release_workflow", lambda: None)
    violations = []
    check_sibling_template.check_release_workflow(
        sibling_workflows(tmp_path, WORKFLOW_TEXT), violations)
    assert any("could not be read" in v for v in violations)


# --------------------------------------------------------------------------
# Releases are made only by the release workflow
# --------------------------------------------------------------------------

def on_block(text):
    """The workflow's top-level `on:` block, up to the next top-level key."""
    return re.search(r"(?ms)^on:\n(.*?)(?=^\S)", text).group(1)


def test_the_workflow_is_started_only_by_hand_with_a_version():
    block = on_block(WORKFLOW_TEXT)
    assert re.match(r"\s+workflow_dispatch:\n", block)
    assert re.search(r"(?m)^\s+version:\n(?:\s+.*\n)*?\s+required: true", block)
    for trigger in ("push", "pull_request", "release", "schedule", "workflow_run"):
        assert not re.search(r"(?m)^  %s:" % trigger, block), trigger


def test_a_hand_pushed_tag_publishes_nothing():
    # No trigger fires on a tag push: tags appear nowhere in the `on:` block.
    assert "tags" not in on_block(WORKFLOW_TEXT)


def test_a_run_off_the_default_branch_fails():
    step = re.search(r"(?ms)- name: Refuse to release.*?exit 1", WORKFLOW_TEXT).group(0)
    assert '"$GITHUB_REF" != "refs/heads/$DEFAULT_BRANCH"' in step
    assert WORKFLOW_TEXT.index("Refuse to release") < WORKFLOW_TEXT.index("actions/checkout")


def test_the_release_commit_and_tag_are_pushed_atomically_before_publishing():
    push = WORKFLOW_TEXT.index('git push --atomic origin "HEAD:refs/heads/$DEFAULT_BRANCH" "refs/tags/v$VERSION"')
    assert WORKFLOW_TEXT.index("release-step: check-dist") < push
    assert push < WORKFLOW_TEXT.index("pypa/gh-action-pypi-publish")
    assert re.search(r"(?m)^  publish:\n(?:.*\n)*?    needs: release$", WORKFLOW_TEXT)


def test_the_tag_sits_on_the_bump_commit():
    commit = WORKFLOW_TEXT.index('git commit -m "Release $VERSION"')
    tag = WORKFLOW_TEXT.index('git tag -a "v$VERSION"')
    build = WORKFLOW_TEXT.index("python -m build")
    assert WORKFLOW_TEXT.index("release-step: bump") < commit < tag < build


def test_releases_are_serialised():
    assert re.search(r"(?m)^concurrency:\n  group: release\n  cancel-in-progress: false$", WORKFLOW_TEXT)


def test_the_workflow_uses_current_actions_and_publishes_with_either_auth():
    for action in ("actions/checkout@v7", "actions/setup-python@v7",
                   "actions/upload-artifact@v7", "actions/download-artifact@v8",
                   "pypa/gh-action-pypi-publish@release/v1"):
        assert action in WORKFLOW_TEXT, action
    publish = re.search(r"(?ms)^  publish:\n(.*?)(?=^  \S)", WORKFLOW_TEXT).group(1)
    assert "environment:\n      name: pypi\n" in publish
    assert "id-token: write" in publish
    # An absent secret is an empty password, and the action then falls back
    # to trusted publishing, so one file serves both kinds of repository.
    assert "password: ${{ secrets.PYPI_API_TOKEN }}" in publish


# --------------------------------------------------------------------------
# The embedded guards, run as the workflow runs them
# --------------------------------------------------------------------------

def embedded_script(marker):
    """The Python heredoc of the workflow step whose first line is `marker`."""
    for body in re.findall(r"python - <<'EOF'\n(.*?)\n\s*EOF\n", WORKFLOW_TEXT, re.S):
        script = textwrap.dedent(body)
        if script.startswith("# release-step: %s\n" % marker):
            return script
    raise AssertionError("no embedded script %r in the release workflow" % marker)


PYPROJECT = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sdypy-demo"
version = "%s"
description = "demo"

[tool.demo]
version = "9.9.9"
"""


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org"})


@pytest.fixture
def repo(tmp_path):
    write(tmp_path, "pyproject.toml", PYPROJECT % "1.2.3")
    git(tmp_path, "init", "-q")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def run_step(marker, cwd, version):
    return subprocess.run([sys.executable, "-c", embedded_script(marker)], cwd=cwd,
                          env={**os.environ, "VERSION": version}, capture_output=True, text=True)


def version_of(repo):
    return tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))


def test_the_bump_writes_the_project_version_only(repo):
    result = run_step("bump", repo, "1.3.0")
    assert result.returncode == 0, result.stdout + result.stderr
    data = version_of(repo)
    assert data["project"]["version"] == "1.3.0"
    assert data["tool"]["demo"]["version"] == "9.9.9"
    assert (repo / "pyproject.toml").read_text(encoding="utf-8") == PYPROJECT % "1.3.0"


@pytest.mark.parametrize("version", ["1.3", "v1.3.0", "1.3.0.dev1", " 1.3.0", "1.3.0\n", ""])
def test_a_malformed_version_is_refused(repo, version):
    result = run_step("bump", repo, version)
    assert result.returncode == 1
    assert "is not X.Y.Z" in result.stdout
    assert version_of(repo)["project"]["version"] == "1.2.3"


def test_a_pre_release_version_is_accepted(repo):
    assert run_step("bump", repo, "1.3.0rc1").returncode == 0
    assert version_of(repo)["project"]["version"] == "1.3.0rc1"


def test_an_existing_tag_is_refused(repo):
    git(repo, "tag", "v1.3.0")
    result = run_step("bump", repo, "1.3.0")
    assert result.returncode == 1
    assert "tag v1.3.0 already exists" in result.stdout
    assert version_of(repo)["project"]["version"] == "1.2.3"


@pytest.mark.parametrize("version", ["1.2.3", "1.2.2", "1.2.3rc1"])
def test_a_version_not_newer_than_the_current_one_is_refused(repo, version):
    result = run_step("bump", repo, version)
    assert result.returncode == 1
    assert "is not newer than the current 1.2.3" in result.stdout


def test_a_dynamic_version_is_refused(repo):
    write(repo, "pyproject.toml", (PYPROJECT % "x").replace('version = "x"', 'dynamic = ["version"]'))
    result = run_step("bump", repo, "1.3.0")
    assert result.returncode == 1
    assert "no literal [project] version" in result.stdout


def write_dist(root, wheel_version, sdist_version):
    dist = root / "dist"
    dist.mkdir()
    if wheel_version:
        (dist / ("sdypy_demo-%s-py3-none-any.whl" % wheel_version)).write_bytes(b"")
    if sdist_version:
        (dist / ("sdypy_demo-%s.tar.gz" % sdist_version)).write_bytes(b"")


def test_distributions_carrying_the_version_pass(tmp_path):
    write_dist(tmp_path, "1.3.0", "1.3.0")
    result = run_step("check-dist", tmp_path, "1.3.0")
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_distribution_with_another_version_is_refused(tmp_path):
    write_dist(tmp_path, "1.3.0", "1.2.3")
    result = run_step("check-dist", tmp_path, "1.3.0")
    assert result.returncode == 1
    assert "carries version 1.2.3, expected 1.3.0" in result.stdout


def test_a_missing_sdist_is_refused(tmp_path):
    write_dist(tmp_path, "1.3.0", None)
    result = run_step("check-dist", tmp_path, "1.3.0")
    assert result.returncode == 1
    assert "expected one wheel and one sdist" in result.stdout


# --------------------------------------------------------------------------
# Releasing is documented once, in the hub
# --------------------------------------------------------------------------

AGENTS_TEXT = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_the_hub_agents_md_has_a_releasing_section():
    section = re.search(r"(?ms)^## Releasing\n(.*?)(?=^## )", AGENTS_TEXT)
    assert section, "AGENTS.md has no '## Releasing' section"
    assert RELEASE_WORKFLOW in section.group(1)


def test_the_hub_link_block_links_to_the_releasing_section():
    block = extract_marker_block(AGENTS_TEXT, AGENTS_LINKS_START, AGENTS_LINKS_END)
    assert "https://github.com/sdypy/sdypy/blob/main/AGENTS.md#releasing" in block
