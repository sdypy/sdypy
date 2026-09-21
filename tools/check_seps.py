"""Repo-layer SEP metadata conformance checker (sep-governance spec).

Audits the header preamble of every ``docs/seps/sep-<nnnn>.rst`` against the
mechanically checkable subset of SEP 0:

  * the required fields ``:Authors:``, ``:Status:``, ``:Type:``, ``:Created:``
    are present (``:Author:`` is the deprecated spelling);
  * ``:Resolution:`` is present and non-empty when the SEP is ratified
    (``Accepted`` / ``Rejected`` / ``Withdrawn``);
  * ``:Status:`` is one of the nine values ``index.rst.tmpl`` renders into a
    toctree section - anything else silently drops the SEP from the index;
  * ``:Type:`` is one of SEP 0's three kinds;
  * ``:Created:`` is an ISO 8601 ``yyyy-mm-dd`` date;
  * ``sep-template.rst`` declares the full Status and Type vocabularies and the
    canonical ``:Authors:`` field name.

Usage:
    python tools/check_seps.py --path .

Stdlib only, on purpose: this runs in the test job too, which installs neither
sphinx nor jinja2, so it cannot use docutils or import build_index.py.

Exit code is 0 when the SEP set conforms (and nothing is printed), 1 otherwise.
This checker is the conformance authority; the RuntimeErrors in
docs/seps/tools/build_index.py are retained as generator preconditions.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

# The nine values index.rst.tmpl renders into a toctree section. A SEP whose
# Status is outside this set appears in no section of the generated index, with
# no error - which is exactly what this vocabulary exists to prevent. The
# comparison is case-sensitive because the template's match is.
STATUS_VOCABULARY = (
    "Draft",
    "Active",
    "Provisional",
    "Accepted",
    "Final",
    "Deferred",
    "Superseded",
    "Rejected",
    "Withdrawn",
)

# SEP 0 section "Types" defines exactly these three kinds.
TYPE_VOCABULARY = ("Standards Track", "Informational", "Process")

# A ratified SEP must record where the decision was made.
RATIFIED_STATUSES = ("Accepted", "Rejected", "Withdrawn")

REQUIRED_FIELDS = ("Authors", "Status", "Type", "Created")

SEP_GLOB = "sep-[0-9][0-9][0-9][0-9].rst"
TEMPLATE_NAME = "sep-template.rst"
SEPS_SUBDIR = Path("docs") / "seps"

# build_index.py's field regex, kept identical so both read the same preamble.
_FIELD_RE = re.compile(r":([a-zA-Z\-]*): (.*)")
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_preamble(text):
    """Return the RST field-list preamble of a SEP as an ordered ``{field: value}``.

    The preamble is the first contiguous run of field lines; a value may
    continue onto following indented lines and the continuation is joined into
    the value (sep-0004's three-line ``:Authors:``). Parsing stops at the first
    blank line or first line that is neither a field nor a continuation, so
    field-list-like constructs later in the prose are never picked up.
    """
    fields = {}
    current = None
    for line in text.splitlines():
        match = _FIELD_RE.match(line)
        if match is not None:
            current = match.group(1)
            fields[current] = match.group(2).strip()
            continue
        if current is not None:
            if line.strip() and line[:1].isspace():  # indented continuation
                fields[current] = ("%s %s" % (fields[current], line.strip())).strip()
                continue
            break  # blank line or body text: the preamble is over
    return fields


def _placeholder_values(value):
    """Split a template placeholder ``<A | B | C>`` into its listed values."""
    inner = value.strip()
    if inner.startswith("<"):
        inner = inner[1:]
    inner, _, _ = inner.partition(">")
    return set(part.strip() for part in inner.split("|") if part.strip())


def check_sep_file(path, label=None):
    """Return the violations of one SEP file, as ``<file>: <rule>: <detail>`` lines."""
    label = label or path.name
    violations = []
    fields = parse_preamble(path.read_text(encoding="utf-8"))

    # ":Author:" satisfies the "who wrote it" requirement but with the retired
    # spelling: report the drift once, not also as a missing ":Authors:".
    deprecated_authors = "Author" in fields and "Authors" not in fields
    if deprecated_authors:
        violations.append(
            "%s: deprecated-field: ':Author:' is the retired spelling; use ':Authors:'" % label
        )

    for field in REQUIRED_FIELDS:
        if field == "Authors" and deprecated_authors:
            continue
        if not fields.get(field):
            violations.append("%s: missing-field: ':%s:' is required" % (label, field))

    status = fields.get("Status")
    if status and status not in STATUS_VOCABULARY:
        violations.append(
            "%s: status-vocabulary: ':Status: %s' is not permitted; permitted: %s"
            % (label, status, " | ".join(STATUS_VOCABULARY))
        )

    sep_type = fields.get("Type")
    if sep_type and sep_type not in TYPE_VOCABULARY:
        violations.append(
            "%s: type-vocabulary: ':Type: %s' is not permitted; permitted: %s"
            % (label, sep_type, " | ".join(TYPE_VOCABULARY))
        )

    created = fields.get("Created")
    if created and not _is_iso_date(created):
        violations.append(
            "%s: created-format: ':Created: %s' is not an ISO 8601 yyyy-mm-dd date"
            % (label, created)
        )

    if status in RATIFIED_STATUSES and not fields.get("Resolution"):
        violations.append(
            "%s: missing-resolution: ':Status: %s' requires a non-empty ':Resolution:'"
            % (label, status)
        )

    return violations


def _is_iso_date(value):
    if not _ISO_DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_template_file(path, label=None):
    """Return the violations of ``sep-template.rst``: it must declare the vocabularies."""
    label = label or path.name
    violations = []
    fields = parse_preamble(path.read_text(encoding="utf-8"))

    if "Authors" not in fields:
        violations.append(
            "%s: template-authors-field: the template must name the field ':Authors:'" % label
        )

    declared = _placeholder_values(fields.get("Status", ""))
    missing = [v for v in STATUS_VOCABULARY if v not in declared]
    extra = sorted(declared - set(STATUS_VOCABULARY))
    if missing or extra:
        violations.append(
            "%s: template-status-vocabulary: ':Status:' must list %s (missing: %s; unexpected: %s)"
            % (
                label,
                " | ".join(STATUS_VOCABULARY),
                ", ".join(missing) or "none",
                ", ".join(extra) or "none",
            )
        )

    declared = _placeholder_values(fields.get("Type", ""))
    missing = [v for v in TYPE_VOCABULARY if v not in declared]
    extra = sorted(declared - set(TYPE_VOCABULARY))
    if missing or extra:
        violations.append(
            "%s: template-type-vocabulary: ':Type:' must list %s (missing: %s; unexpected: %s)"
            % (
                label,
                " | ".join(TYPE_VOCABULARY),
                ", ".join(missing) or "none",
                ", ".join(extra) or "none",
            )
        )

    return violations


def check_repo(root):
    """Return every SEP metadata violation in a repository, sorted by file."""
    root = Path(root)
    seps_dir = root / SEPS_SUBDIR
    if not seps_dir.is_dir():
        raise FileNotFoundError("no SEP directory at %s" % seps_dir)

    sources = sorted(seps_dir.glob(SEP_GLOB))
    if not sources:
        raise FileNotFoundError("no sep-<nnnn>.rst files under %s" % seps_dir)

    violations = []
    for source in sources:
        violations.extend(check_sep_file(source, _label(source, root)))

    template = seps_dir / TEMPLATE_NAME
    if template.is_file():
        violations.extend(check_template_file(template, _label(template, root)))
    else:
        violations.append("%s: missing-field: the SEP template is missing" % TEMPLATE_NAME)

    return violations


def _label(path, root):
    try:
        return path.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:  # pragma: no cover - path outside the repo root
        return path.name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--path", default=".", type=Path,
        help="path to the repository holding docs/seps (default: the current directory)",
    )
    args = parser.parse_args(argv)

    try:
        violations = check_repo(args.path)
    except FileNotFoundError as exc:
        print("ERROR: %s" % exc)
        return 1

    for violation in violations:
        print(violation)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
