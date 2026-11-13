## Context

SEP 2 is a table of settled names plus a heuristic for coining new ones. It has
no external anchor and no defined route from "a contributor needs a name" to
"the table has the name". In practice the name is chosen inside a package and
SEP 2 learns about it later, which is how `frf_type` came to mean the FRF ratio
in `sdypy-EMA` and the FRF estimator in `sdypy-FRF` at the same time.

The 2026-09-01 meeting fixed the rule: a new term follows the general guidelines
and the ISO 7626 terminology, and an unclear case goes to a discussion rather
than being settled silently.

## Goals / Non-Goals

**Goals**

- Give SEP 2 an external terminology anchor and put the one existing divergence
  on the record.
- Define a route from proposed name to table entry that is cheap in the common
  case and only expensive when the name is genuinely contested.
- Keep SEP 2 short: the rule in the SEP, the procedure in the dev docs.

**Non-Goals**

- No canonical name changes; no sibling code changes. The `frf_form` migration
  this enables is separate work.
- Not ratification. `:Status:` stays `Draft`, team-gated in § Pending B.
- No new checker, and no change to `check_nomenclature.py`.

## Decisions

**The author declares; nothing detects.** Conformance is the pull-request
author's responsibility, made concrete by a declaration line in the PR. This was
chosen over automated detection because detection cannot do the part that
matters. A measurement over the six installed packages found 239 distinct public
parameter names, 221 of them with no canonical table entry — a report of
"uncovered names" is 92% noise. Narrowing to names shared by two or more
packages leaves 5, which is triageable but still cannot distinguish an interop
hazard from two packages sensibly sharing a word, and would not have caught
`frf_type` at all, since `sdypy.FRF` re-exports `pyFRF` from outside the
namespace. Detection was dropped.

**The discussion lives in the feature PR, not in a SEP PR.** Requiring a SEP
amendment per name would open a PR every time someone thinks of a variable name
in a package they are working on, paying the cost on every name to catch the
rare contested one.

**Recording is deferred and batched.** Declared names collect on a *SEP 2
pending terms* issue and reach the table through a manually triggered amendment
PR. The issue is opened only when there is a name to record and is closed by the
amendment, so an open issue is itself the signal that an amendment is due — no
permanent issue sits empty between rounds. This
accepts a window in which a merged name is not yet in the table — the right
trade, since the alternative couples every sibling release to a SEP round, and
the two-way mirror tests already make table-versus-checker drift a test failure.

**The trigger is manual, not scheduled.** Term churn is low; a cron would mostly
produce empty PRs. A release-checklist reminder covers the realistic cadence
without coupling nomenclature to release timing.

**The process is documented tool-agnostically, and the agent command is a thin
wrapper.** `AGENTS.md` is tool-agnostic by design and forbids duplication, and
six sibling repos plus other tools have to follow this. So the procedure is
defined in `docs/source/dev/nomenclature.rst` and the `.claude/` command links to
it rather than restating it. If the command is absent the process still works.

**ISO is a source, not an override.** ISO 7626 joins the existing precedence
rule rather than replacing it, and its silence on a quantity is not a violation.
This keeps `'receptance'` legitimate as a recorded, reasoned divergence instead
of making SEP 2 non-conformant with its own new rule on the day it lands.

## Risks / Trade-offs

- **An undeclared name is invisible.** Nothing detects one, by design. The
  reviewer and the amendment round are the only backstops. Accepted: the
  alternatives were measured and do not work.
- **The batching window.** A name can be merged and in use before the table
  records it. Mitigated by the ledger and the mirror tests.
- **"Contested" is a judgement call.** Defined by symptom rather than by a test,
  because it cannot be one. The failure mode is a name settled too easily in
  review; the amendment round is the second chance to catch it.
- **ISO 7626 is paywalled.** Mitigated by SEP 2 recording the terms that matter
  for the quantities SDyPy actually names, so it is usable without the standard.

## Deferred

- **Propagation to the sibling namespace packages** is being solved centrally;
  this change stays inside `sdypy`.
- **PR and issue templates** do not exist in any repo. The declaration line
  belongs in one, but creating it touches `sibling-package-template` and all six
  siblings, so it is recorded in § Pending.
- **Running `check_nomenclature.py` automatically.** Nothing schedules it today;
  it is invoked by hand against a clone. Recorded in § Pending, not fixed here.
- **Generating the declaration from a public-name diff** could later automate
  the author's declaration step. Worth revisiting once the human path has been
  used a few times.
