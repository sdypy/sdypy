"""Repo-layer documentation conformance checker (documentation spec).

Audits a repo (core or a sibling clone) WITHOUT building the docs:
  * every conf.py uses the unified pydata-sphinx-theme;
  * the README is README.rst (and no README.md remains);
  * the pyproject docs extra lists pydata-sphinx-theme and no competing theme;
  * no foreign-project residue strings appear (outside an allowlist);
  * the [project.urls] Documentation target matches the package's class
    (own Read the Docs site, or upstream backend docs for the thin wrappers).

Usage:
    python tools/check_docs.py --path .                       # core
    python tools/check_docs.py --path ../packages/sdypy-view  # a sibling

Exit code is non-zero if any violation is found. Kept separate from
tools/check_sibling_template.py and tools/check_public_api.py on purpose.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - py<3.11
    tomllib = None

THEME = "pydata_sphinx_theme"
COMPETING_THEMES = ("sphinx-rtd-theme", "sphinx-book-theme", "myst-parser")

# Specific residue strings (NOT generic "numpy"/"scipy", to avoid flagging the
# intentional "adapted from SciPy" acknowledgements or example `import numpy`).
RESIDUE_STRINGS = (
    "numpylogo",
    "NumPy Enhancement Proposals",
    "A project template for the SDyPy effort",
    "www.sdypy.org/devdocs",
    "sdypa-EMA",
)
# The clone-URL typo "ttps://" — match only when NOT part of "https://".
RESIDUE_REGEX = re.compile(r"(?<!h)ttps://")

# Lines containing any allowlist token are exempt from the residue scan.
ALLOWLIST_TOKENS = ("adapted from", "import numpy")

# Upstream-backend doc targets for the thin-wrapper packages; everyone else
# must point at their own readthedocs.io site.
UPSTREAM_DOC_TARGET = {"sdypy-FRF": "pyfrf", "sdypy-excitation": "pyexsi"}


def _load_pyproject(root):
    path = root / "pyproject.toml"
    if not path.is_file():
        return None, None
    if tomllib is not None:
        with path.open("rb") as fh:
            return tomllib.load(fh), path
    return None, path  # parsing unavailable; caller falls back to text


def check_theme(root, violations):
    conf_paths = [root / "docs" / "source" / "conf.py"]
    seps = root / "docs" / "seps" / "conf.py"
    if seps.is_file():
        conf_paths.append(seps)
    found_any = False
    for conf in conf_paths:
        if not conf.is_file():
            continue
        found_any = True
        text = conf.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"""html_theme\s*=\s*['"]%s['"]""" % THEME, text):
            violations.append("%s: html_theme is not '%s'" % (conf, THEME))
        if not re.search(r"""['"]sphinx_copybutton['"]""", text):
            violations.append("%s: 'sphinx_copybutton' not in extensions" % conf)
    if not found_any:
        violations.append("%s: no docs/source/conf.py found" % root)


def check_readme(root, violations):
    if not (root / "README.rst").is_file():
        violations.append("%s: README.rst is missing" % root)
    if (root / "README.md").is_file():
        violations.append("%s: README.md still present (must be .rst)" % root)


def check_docs_extra(data, root, violations):
    if data is None:
        violations.append("%s: cannot parse pyproject.toml (tomllib unavailable)" % root)
        return
    extras = data.get("project", {}).get("optional-dependencies", {})
    docs = extras.get("docs")
    if docs is None:
        violations.append("%s: no [project.optional-dependencies] docs extra" % root)
        return
    joined = " ".join(docs).lower()
    if "pydata-sphinx-theme" not in joined:
        violations.append("%s: docs extra does not list pydata-sphinx-theme" % root)
    for competing in COMPETING_THEMES:
        if competing in joined:
            violations.append("%s: docs extra lists competing '%s'" % (root, competing))


def check_doc_url(data, root, violations):
    if data is None:
        return  # already reported in check_docs_extra
    name = data.get("project", {}).get("name", "")
    urls = data.get("project", {}).get("urls", {})
    doc_url = next(
        (v for k, v in urls.items() if k.lower() in ("documentation", "docs")), None
    )
    upstream = UPSTREAM_DOC_TARGET.get(name)
    if upstream is not None:
        if doc_url is None or upstream not in doc_url.lower():
            violations.append(
                "%s: %s Documentation URL must point at upstream '%s' (got %r)"
                % (root, name, upstream, doc_url)
            )
    else:
        if doc_url is None:
            violations.append("%s: %s has no Documentation URL" % (root, name))
        elif "readthedocs.io" not in doc_url.lower():
            violations.append(
                "%s: %s Documentation URL must be its own readthedocs.io site (got %r)"
                % (root, name, doc_url)
            )


def check_residue(root, violations):
    scan_roots = [root / "docs"]
    for extra in ("README.rst", "README.md"):
        p = root / extra
        if p.is_file():
            scan_roots.append(p)
    # package __init__.py files (template docstring lives there)
    ns = root / "sdypy"
    if ns.is_dir():
        scan_roots.extend(ns.rglob("__init__.py"))

    files = []
    for sr in scan_roots:
        if sr.is_dir():
            files.extend(p for p in sr.rglob("*") if p.suffix in (".rst", ".py", ".md"))
        elif sr.is_file():
            files.append(sr)

    for f in files:
        if "_build" in f.parts:
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if any(tok in line for tok in ALLOWLIST_TOKENS):
                continue
            for residue in RESIDUE_STRINGS:
                if residue in line:
                    violations.append("%s:%d: residue %r" % (f, i, residue))
            if RESIDUE_REGEX.search(line):
                violations.append("%s:%d: residue 'ttps://' (clone-URL typo)" % (f, i))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--path", required=True, type=Path)
    args = parser.parse_args(argv)
    root = args.path.resolve()

    if not root.is_dir():
        print("ERROR: %s is not a directory" % root)
        return 1

    violations = []
    data, _ = _load_pyproject(root)
    check_theme(root, violations)
    check_readme(root, violations)
    check_docs_extra(data, root, violations)
    check_doc_url(data, root, violations)
    check_residue(root, violations)

    if violations:
        for v in violations:
            print("VIOLATION: %s" % v)
        return 1
    print("OK: %s conforms to the documentation contract" % root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
