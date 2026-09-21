## Context

SEP 0 (`:Status: Active`) is the only ratified SEP and governs the form of every
other one, but nothing measures it: no capability, no `REQUIREMENTS.md` rows, no
checker. Four metadata drifts are already in the tree (`sep-0005` `:Type: Standards`;
`sep-0000` `:Created: 2-Nov-2020` and `:Author:`; `Provisional` missing from the
template vocabulary), and none of them is detectable today.

The enforcement that does exist lives inside `docs/seps/tools/build_index.py`, a
Jinja generator that raises `RuntimeError` on three conditions: a title not matching
`SEP <nr> — `, a missing `:Resolution:` on Accepted/Rejected/Withdrawn, and an
inconsistent `Superseded`/`Replaces` graph. Everything else is unchecked, and the
one failure mode that matters most is silent: `index.rst.tmpl` selects SEPs by exact
string equality on `Status`, so an unknown or mis-cased value drops the SEP from
every toctree section without any error.

Two constraints shape the solution. First, `documentation` already owns the SEP
*index* as a capability. Second, the two CI jobs install different things: `docs.yml`
installs `.[docs]` (sphinx, jinja2), while `python-package.yml` installs only `.`
plus pytest/flake8/build/PySide6 — no docutils, no jinja2.

## Goals / Non-Goals

**Goals**
- Make the mechanically checkable subset of SEP 0 a normative, verified contract.
- Detect metadata drift as a named violation, locally and in CI, before the docs build.
- Make the pending SEP 2/3/5 `Draft → Accepted` flips (§ Pending B) safe to perform.
- Fix the four evidenced drifts and align `sep-template.rst` with reality.

**Non-Goals**
- Automating SEP 0's human process (champion, consensus, mailing-list discussion).
- Changing any SEP's technical content, status, or prose.
- Performing the SEP 2/3/5 ratification flips — this change only makes them checkable.
- Touching SEP 1's four-level integration scale (separate change; see D2).
- Changing `build_index.py` behaviour or the rendered index (`documentation`'s territory).

## Decisions

### D1: Capability boundary — `sep-governance` owns metadata, `documentation` owns the index
The draft of this change carried a sixth requirement, "the rendered index accounts for
every SEP". It was removed. `documentation` already states that `build_index.py` is the
single source of truth for the SEP index, covering all SEPs, invoked in the RTD build.
Restating index completeness here would give one fact two homes, which the project's
own conventions forbid. The silent-drop behaviour therefore appears in this change as
*motivation* (in `proposal.md` § Why and in the Status requirement's prose) and never as
a requirement. The split is: this capability constrains what a SEP **file declares**;
`documentation` constrains what the generator **renders**.

### D2: Only the mechanically checkable subset of SEP 0
Each candidate rule was admitted only if a command can return exit code 0 or 1 for it.
"Each SEP must have a champion who builds consensus" cannot, so it stays SEP 0 prose.
Admitting it would produce `REQUIREMENTS.md` rows whose verifier is `manual`, which by
convention belong in § Pending, not in the current-requirements table. The same filter
is why SEP 1 is not part of this change: its integration levels are largely *already*
verified through `public-api`, `namespace-packaging` and `sibling-package-template`, so
specifying them now would duplicate those capabilities — and SEP 1 is still `Draft`,
meaning its content is a governance decision, not yet a contract to formalise.

### D3: A standalone stdlib-only checker, not an extension of `build_index.py`
`tools/check_seps.py` follows the established pattern of `check_public_api.py`,
`check_docs.py` and `check_sibling_template.py`: `--path`, one line per violation, exit
0/1. It parses the RST field-list preamble with a regex extending the generator's own
`:([a-zA-Z\-]*): (.*)`, plus indented-continuation handling (needed for `sep-0004`'s
three-line `:Authors:`). **Stdlib only, no docutils** — the checker must also run under
`python-package.yml`, which installs neither sphinx nor jinja2. `sep-template.rst` is
excluded from the per-SEP field checks (as in `build_index.py`) but is itself checked
for its vocabulary placeholders.

Conformance is two-layer, as in the package-template change: the checker is the
authority and CI runs it directly; `tests/test_sep_governance.py` invokes the same
functions so a bare `pytest` also fails on a bad SEP.

### D4: The `Status` vocabulary is derived, not invented
The nine permitted values are exactly those `index.rst.tmpl` renders into a toctree
section: `Draft`, `Active`, `Provisional`, `Accepted`, `Final`, `Deferred`,
`Superseded`, `Rejected`, `Withdrawn`. Deriving it from the template guarantees the
property we actually want — a conforming SEP is always visible somewhere in the index.
Comparison is case-sensitive because the template's match is. `sep-template.rst` is
amended to declare the same nine (it omits `Provisional` today).

### D5: The `Type` vocabulary is SEP 0's three kinds
SEP 0 § Types defines Standards Track, Informational, Process. `sep-template.rst` lists
only two, and `sep-0005` uses a fourth spelling (`Standards`). The SEP 0 prose is the
authority: the template gains `Informational`, and `sep-0005` is corrected to
`Standards Track`. No current SEP is Informational; the value is admitted because SEP 0
defines it.

### D6: `:Authors:` is canonical; `:Author:` is a reported violation
Five of six SEPs already use `:Authors:`, against the template's `:Author:`. Majority
practice wins over the template, the template is amended, and `sep-0000` is migrated.
Recorded as maintainer-deferred in `proposal.md` § Impact: reversing this is one line
in the checker plus one in the template.

### D7: Checker runs before the generator; `build_index.py` is untouched
In `docs.yml` the checker step precedes the `build_index.py` step, so a metadata error
surfaces as a named violation rather than a traceback. The generator's three existing
`RuntimeError`s stay as generator preconditions — defence in depth, not the gate. The
spec states this explicitly so a future reader does not "clean up" the redundancy by
deleting the checks that CI depends on.

### D8: No version bump
No shipped code changes. `tools/`, `tests/` and `openspec/` are outside the sdist
allow-list, and `docs/seps/` content is documentation. This rides the umbrella's next
release with no version action.

## Rejected: extend `build_index.py` instead of adding a checker

It is the smallest diff and the checks would sit next to the parsing they extend. Rejected
because it couples conformance to the docs build: the generator needs jinja2, so it cannot
run in the test job; it emits tracebacks rather than violation lists; it cannot be run as a
pre-commit style local gate; and it would be the only conformance rule in the repo not
implemented as a `tools/check_*.py`. Also rejected: parsing with docutils (a docs-only
dependency, unavailable in the test job) and encoding the rules as a pytest file alone
(inconsistent with the three existing checkers, and not runnable outside a test session).

## Risks / Trade-offs

- **A stricter gate can block an unrelated PR.** A contributor editing SEP prose could
  trip a pre-existing metadata violation. Mitigated by fixing all four known drifts in
  this same change, so the tree is clean when the gate goes live.
- **Regex parsing is not a real RST parser.** It will not understand exotic field-list
  constructs. Accepted: it matches what `build_index.py` already does, over six files
  written from one template, and the stdlib-only constraint is binding.
- **Two enforcement points for `:Resolution:`** (checker and generator). Deliberate per
  D7 and stated in the spec, so it reads as defence in depth rather than as drift.
- **The `Status` vocabulary is coupled to `index.rst.tmpl`.** If a section is added to
  the template, the checker's list must follow. Accepted — that coupling is the point of
  D4, and it is documented in the requirement prose.

## Migration Plan

Single PR, no staging needed: fix the four drifts, add the checker and test, wire the CI
step. The gate is green from the first commit that introduces it because the drift fixes
land in the same change. No user-facing surface, no deprecation, nothing to sequence
against sibling releases.

## Open Questions

- Should `:Authors:` be structured (name + email per entry) and validated as such, or
  remain free text? Free text for now; structure is only worth it if something consumes it.
- Should the checker require a `Copyright` section and the public-domain footnote that
  `sep-template.rst` prescribes? All six SEPs have one today; deferred until there is a
  violation to justify the rule.
- Does SEP 4 (roadmap, `Draft`) want a capability of its own, or is it permanently prose?
