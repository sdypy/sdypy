"""Repo-layer conformance checker for the sibling-package-template spec.

Audits a first-level sdypy namespace package working clone against the
template contract (openspec/specs/sibling-package-template/spec.md):
root-file hygiene, pyproject shape, workflow files, and the __init__.py
version-derivation pattern.

Usage:
    python tools/check_sibling_template.py --path <sibling-clone-dir>

Exits 0 when the clone conforms; exits 1 and prints every violation found
otherwise. Requires Python >= 3.11 (tomllib).
"""
import argparse
import re
import sys
import tomllib
from pathlib import Path

CI_MATRIX = {"3.10", "3.11", "3.12"}
FORBIDDEN_ROOT_FILES = (
    "setup.py",
    "setup.cfg",
    ".travis.yml",
    "sync_version.py",
)
TEST_WORKFLOW = "python-package.yml"
RELEASE_WORKFLOW = "release-and-publish-to-pypi.yml"
MIN_ACTION_MAJORS = {"actions/checkout": 4, "actions/setup-python": 5}


def find_package_name(root):
    """The single portion directory under sdypy/ names the package."""
    portions = [
        p.name
        for p in (root / "sdypy").iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    ] if (root / "sdypy").is_dir() else []
    if len(portions) != 1:
        return None
    return portions[0]


def check_root_hygiene(root, violations):
    for name in FORBIDDEN_ROOT_FILES:
        if (root / name).exists():
            violations.append("root: forbidden file present: %s" % name)
    for req in root.glob("requirements*.txt"):
        violations.append("root: forbidden file present: %s" % req.name)
    if (root / "sdypy" / "__init__.py").exists():
        violations.append(
            "namespace: sdypy/__init__.py present - portions must be native "
            "PEP 420 (namespace-packaging spec)"
        )


def check_pyproject(root, pkg, violations):
    pp_path = root / "pyproject.toml"
    if not pp_path.is_file():
        violations.append("pyproject: pyproject.toml missing")
        return
    try:
        data = tomllib.loads(pp_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        violations.append("pyproject: unparseable: %s" % exc)
        return

    backend = data.get("build-system", {}).get("build-backend")
    if backend != "hatchling.build":
        violations.append("pyproject: build-backend is %r, expected 'hatchling.build'" % backend)

    project = data.get("project", {})
    dist_name = "sdypy-%s" % pkg

    if project.get("name") != dist_name:
        violations.append("pyproject: project name is %r, expected %r" % (project.get("name"), dist_name))
    if "version" in project.get("dynamic", []):
        violations.append("pyproject: version is dynamic - must be a literal in [project]")
    elif not re.fullmatch(r"\d+\.\d+\.\d+", str(project.get("version", ""))):
        violations.append("pyproject: [project] version is %r, expected a literal X.Y.Z" % project.get("version"))

    if project.get("requires-python") != ">=3.10":
        violations.append("pyproject: requires-python is %r, expected '>=3.10'" % project.get("requires-python"))

    lic = project.get("license")
    lic_text = lic.get("text") if isinstance(lic, dict) else lic
    if lic_text != "MIT":
        violations.append("pyproject: license is %r, expected 'MIT'" % (lic,))

    classifiers = project.get("classifiers", [])
    declared = {
        m.group(1)
        for c in classifiers
        for m in [re.fullmatch(r"Programming Language :: Python :: (3\.\d+)", c)]
        if m
    }
    if declared != CI_MATRIX:
        violations.append(
            "pyproject: Python classifiers %s do not match the CI matrix %s"
            % (sorted(declared), sorted(CI_MATRIX))
        )
    if "License :: OSI Approved :: MIT License" not in classifiers:
        violations.append("pyproject: missing 'License :: OSI Approved :: MIT License' classifier")
    if not any(c.startswith("Development Status ::") for c in classifiers):
        violations.append("pyproject: missing a 'Development Status' classifier")

    urls = {k.lower(): v for k, v in project.get("urls", {}).items()}
    for key in ("homepage", "source"):
        url = urls.get(key, "")
        if dist_name.lower() not in url.lower():
            violations.append(
                "pyproject: urls.%s is %r - must point at the package's own "
                "repository (%s)" % (key, url or None, dist_name)
            )

    extras = project.get("optional-dependencies", {})
    for extra in ("docs", "dev"):
        if extra not in extras:
            violations.append("pyproject: optional-dependencies missing %r extra" % extra)
    dev = [d.replace(" ", "").lower() for d in extras.get("dev", [])]
    if "dev" in extras and ("%s[docs]" % dist_name.lower()) not in dev:
        violations.append("pyproject: dev extra must reference '%s[docs]'" % dist_name)

    hatch_targets = data.get("tool", {}).get("hatch", {}).get("build", {}).get("targets", {})
    # Must be the namespace ROOT: packages = ["sdypy/<pkg>"] makes hatchling
    # strip the sdypy/ prefix and ship <pkg>/ at the wheel top level.
    if hatch_targets.get("wheel", {}).get("packages") != ["sdypy"]:
        violations.append(
            "pyproject: [tool.hatch.build.targets.wheel] packages must be "
            "['sdypy'], got %r" % (hatch_targets.get("wheel", {}).get("packages"),)
        )
    if not hatch_targets.get("sdist", {}).get("include"):
        violations.append("pyproject: [tool.hatch.build.targets.sdist] must declare an explicit include allow-list")

    readme = project.get("readme")
    readme_file = readme.get("file") if isinstance(readme, dict) else readme
    if not readme_file or not (root / readme_file).is_file():
        violations.append("pyproject: readme field %r does not match a file in the repo root" % readme_file)


def _workflow_text(path):
    return path.read_text(encoding="utf-8") if path.is_file() else None


def check_action_versions(text, label, violations):
    for action, minimum in MIN_ACTION_MAJORS.items():
        for m in re.finditer(re.escape(action) + r"@v(\d+)", text):
            if int(m.group(1)) < minimum:
                violations.append(
                    "%s: %s@v%s is below the required @v%d"
                    % (label, action, m.group(1), minimum)
                )
        if action == "actions/checkout" and action + "@" not in text:
            violations.append("%s: no %s step found" % (label, action))


def check_test_workflow(workflows_dir, violations):
    for stale in ("pytest.yaml", "pytest.yml"):
        if (workflows_dir / stale).exists():
            violations.append("workflows: stale test workflow present: %s" % stale)
    text = _workflow_text(workflows_dir / TEST_WORKFLOW)
    if text is None:
        violations.append("workflows: %s missing" % TEST_WORKFLOW)
        return
    label = "workflows/%s" % TEST_WORKFLOW
    # Both trigger syntaxes are valid: block form ("on:\n  push:") and
    # inline-array form ("on: [push, pull_request]").
    if not re.search(r"on:\s*\[[^\]]*\bpush\b|^\s+push\s*:", text, re.M):
        violations.append("%s: no push trigger" % label)
    if "pull_request" not in text:
        violations.append("%s: no pull_request trigger" % label)
    matrix = set(re.findall(r"['\"](3\.\d+)['\"]", text))
    if not CI_MATRIX <= matrix:
        violations.append("%s: python matrix %s does not cover %s" % (label, sorted(matrix), sorted(CI_MATRIX)))
    if not re.search(r"pip install \.(?!\[)", text):
        violations.append("%s: package must be installed via 'pip install .'" % label)
    if "requirements" in text:
        violations.append("%s: references a requirements file" % label)
    for needle, what in (("flake8", "flake8 step"), ("pytest", "pytest step"),
                         ("python -m build", "build validation step")):
        if needle not in text:
            violations.append("%s: missing %s" % (label, what))
    check_action_versions(text, label, violations)


def check_release_workflow(workflows_dir, violations):
    if workflows_dir.is_dir():
        for f in workflows_dir.iterdir():
            if re.match(r"release.*_.*", f.name):
                violations.append("workflows: underscore-named release workflow present: %s" % f.name)
    text = _workflow_text(workflows_dir / RELEASE_WORKFLOW)
    if text is None:
        violations.append("workflows: %s missing" % RELEASE_WORKFLOW)
        return
    label = "workflows/%s" % RELEASE_WORKFLOW
    if not re.search(r"tags:\s*\n?\s*-?\s*['\"]?v\*", text):
        violations.append("%s: no v* tag trigger" % label)
    if "sync_version" in text:
        violations.append("%s: contains a version-sync step" % label)
    if "python -m build" not in text:
        violations.append("%s: missing 'python -m build'" % label)
    if "pypa/gh-action-pypi-publish" not in text:
        violations.append("%s: missing pypa/gh-action-pypi-publish publish step" % label)
    check_action_versions(text, label, violations)


def check_init_version(root, pkg, violations):
    init = root / "sdypy" / pkg / "__init__.py"
    if not init.is_file():
        violations.append("init: sdypy/%s/__init__.py missing" % pkg)
        return
    text = init.read_text(encoding="utf-8")
    label = "sdypy/%s/__init__.py" % pkg
    if not re.search(r"""version\(\s*["']sdypy-%s["']\s*\)""" % re.escape(pkg), text):
        violations.append("%s: __version__ must derive from importlib.metadata.version('sdypy-%s')" % (label, pkg))
    if "PackageNotFoundError" not in text or "0+unknown" not in text:
        violations.append("%s: missing PackageNotFoundError -> '0+unknown' fallback" % label)
    if re.search(r"""^__version__\s*=\s*["']\d""", text, re.M):
        violations.append("%s: hard-coded __version__ literal present" % label)


def check_scaffolding(root, violations):
    if not any(f.is_file() and f.name.upper().startswith("LICENSE")
               for f in root.iterdir()):
        violations.append("scaffolding: no LICENSE file at repo root")
    rtd = None
    for name in ("readthedocs.yaml", ".readthedocs.yaml", ".readthedocs.yml"):
        if (root / name).is_file():
            rtd = (root / name).read_text(encoding="utf-8")
            break
    if rtd is None:
        violations.append("scaffolding: readthedocs.yaml missing")
    elif not ("method: pip" in rtd and re.search(r"extra_requirements:\s*\n?\s*-?\s*\[?docs", rtd)):
        violations.append("scaffolding: readthedocs.yaml must install via pip with extra_requirements: [docs]")
    gi_path = root / ".gitignore"
    gi = gi_path.read_text(encoding="utf-8") if gi_path.is_file() else ""
    for pattern in ("dist", "_build", "egg-info"):
        if pattern not in gi:
            violations.append("scaffolding: .gitignore does not cover %r" % pattern)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", required=True, help="path to a sibling package working clone")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print("ERROR: %s is not a directory" % root)
        return 2

    pkg = find_package_name(root)
    if pkg is None:
        print("ERROR: could not find exactly one portion directory under %s" % (root / "sdypy"))
        return 2

    violations = []
    workflows_dir = root / ".github" / "workflows"
    check_root_hygiene(root, violations)
    check_pyproject(root, pkg, violations)
    check_test_workflow(workflows_dir, violations)
    check_release_workflow(workflows_dir, violations)
    check_init_version(root, pkg, violations)
    check_scaffolding(root, violations)

    name = "sdypy-%s" % pkg
    if violations:
        print("%s: %d template violation(s):" % (name, len(violations)))
        for v in violations:
            print("  - %s" % v)
        return 1
    print("%s: conforms to the sibling-package-template" % name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
