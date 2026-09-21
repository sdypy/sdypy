---
description: Draft the SEP 2 canonical-table amendment PR from the pending-terms ledger
---

Draft the amendment pull request that folds declared nomenclature terms into
SEP 2's canonical table.

**The procedure is defined in `docs/source/dev/nomenclature.rst`, section
"Adding a term to the canonical table". Read it and follow it — do not restate
or reinvent it here.** This command exists to save typing; if it is missing, the
documented procedure still works by hand.

Steps:

1. Find the open *SEP 2 pending terms* issue on `ladisk/sdypy` and collect the
   names it lists. If no such issue is open, there is nothing to amend — say so
   and stop.
2. For each name, follow the documented ordered steps: the `list-table` row in
   `docs/seps/sep-0002.rst`, then the `CANONICAL` entry in
   `tools/check_nomenclature.py` **only if** the canonical name replaces a
   spelling actually evidenced in a package.
3. Run `pytest tests/test_nomenclature.py`. The two mirror tests are the gate.
   Do not proceed if they fail.
4. Run `python tools/check_seps.py --path .` and confirm `:Status:` is unchanged.
5. Stop. Report what was added and what you left out, and hand the user the
   branch, commit and PR commands. Do not commit, push, or open the PR yourself.

Constraints:

- A name whose naming question was **not** settled in the pull request that
  introduced it does not belong in this amendment. Escalate it instead, per the
  documented escalation route.
- Leave the **Instead of** cell empty unless a divergent spelling is evidenced.
  Do not invent one to fill it.
- A human reviews and merges the amendment. This command never lands it.
