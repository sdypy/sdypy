## 1. Record the relation to ISO 7626 in SEP 2

- [x] 1.1 Add a short **"Relation to ISO 7626"** subsection to `docs/seps/sep-0002.rst`, after the canonical table, naming ISO 7626 Parts 1, 2 and 5 by title and edition (7626-1:2011, 7626-2:2015, 7626-5:2019)
- [x] 1.2 In that subsection record the FRF-form comparison in two sentences: `'mobility'` and `'accelerance'` agree with the ISO-preferred terms, and ISO prefers *accelerance* over *inertance*
- [x] 1.3 Record `'receptance'` as the single deliberate divergence from ISO 7626-1's *dynamic compliance*, with the reason and a link to issue #2
- [x] 1.4 State that a divergence is permitted but must be recorded in the same amendment that adopts the name
- [x] 1.5 Add ISO 7626-1:2011, -2:2015 and -5:2019 to the SEP's "References and Footnotes" section
- [x] 1.6 Keep the subsection short — it states the anchor and the one divergence, not the audit; the reasoning lives in issue #2
- [x] 1.7 Verify `:Status:` is still `Draft` and `python tools/check_seps.py --path .` exits 0

## 2. Add the proposal rule to SEP 2

- [x] 2.1 Add a short **"Proposing a new term"** subsection stating that a name for an uncovered quantity satisfies both the general guidelines and ISO 7626 where ISO defines the quantity, and that ISO's silence is not a violation
- [x] 2.2 State that the pull-request author declares the new public names their PR introduces, and the reviewer assesses them; conformance is the author's responsibility
- [x] 2.3 State that the discussion happens in that pull request and that no separate SEP amendment PR is required before it merges
- [x] 2.4 State that declared names are collected and added to the canonical table by a later amendment, and that recording never gates a feature
- [x] 2.5 State the escalation trigger and route in one sentence: a name the PR cannot settle goes to an issue plus a SEP amendment PR, blocking that name alone
- [x] 2.6 Cross-reference the existing precedence rule rather than restating it, and keep the whole subsection to roughly a screen — the operational detail belongs in the dev docs
- [x] 2.7 Rebuild the docs and confirm both subsections render and the transcluded canonical table is unaffected

## 3. Put the worked procedure in the dev docs

- [x] 3.1 On `docs/source/dev/nomenclature.rst`, add "Checking a proposed name": the `python tools/check_nomenclature.py --path <clone>` invocation and the four faults it decides (`nomenclature`, `index-suffix`, `count-name`, `parameter-case`)
- [x] 3.2 State plainly that nothing runs the checker automatically — the umbrella CI excludes it by design (`.github/workflows/docs.yml`), no other CI invokes it — and that a clean run means no known fault, not a good name
- [x] 3.3 Add "Adding a term to the canonical table" with the ordered steps: the `list-table` row in `docs/seps/sep-0002.rst`, the `CANONICAL` entry in `tools/check_nomenclature.py` for any evidenced divergent spelling, then `pytest tests/test_nomenclature.py`
- [x] 3.4 Add a worked example walking one new name through declaration, review and recording, so the procedure is concrete without putting an example in the SEP
- [x] 3.5 Verify the mirror is genuinely the gate: temporarily add a table row whose divergent spelling is absent from `CANONICAL`, confirm the two mirror tests fail, then revert
- [x] 3.6 Confirm `python tools/check_docs.py --path .` still passes

## 4. Wire up the ledger and the amendment command

- [x] 4.1 Document the "SEP 2 pending terms" issue convention in `docs/source/dev/nomenclature.rst`: one is opened when the first name since the last amendment is declared, and the amendment PR closes it; no issue is opened until there is a name to record
- [x] 4.2 Add a `.claude/` command that drafts the amendment PR from the ledger: read the declared names, add the table rows and any `CANONICAL` entries, run the mirror tests, and stop for human review
- [x] 4.3 Keep the command thin — it links to the dev-docs procedure and does not restate it, so the process still works by hand if the command is absent
- [x] 4.4 Add the release-time reminder to trigger the amendment, in the release checklist rather than as a schedule
- [x] 4.5 Add one router line to `AGENTS.md` pointing at the procedure

## 5. Record the requirements and the deferred work

- [x] 5.1 Add the five new `public-api` rows to `REQUIREMENTS.md`, each pointing at its verifying test or at `manual` (docs review) where the requirement is a human process
- [x] 5.2 Add a `REQUIREMENTS.md` § Pending entry for the PR-template work: no PR or issue template exists in the umbrella, any sibling, or `sdypy_template_project`, and the declaration line belongs in one; it touches the `sibling-package-template` capability and all six siblings
- [x] 5.3 Record in that entry that running `check_nomenclature.py` automatically is unresolved, and that propagation of these rules to the sibling namespace packages is being solved centrally and is out of scope here
- [x] 5.4 Confirm no `tools/check_nomenclature.py` change is needed: the proposal path is a human process and the checker's coverage boundary already declares it out of scope

## 6. Validate

- [x] 6.1 `openspec validate add-sep2-term-governance --strict` passes
- [x] 6.2 `pytest -m "not pypi_artifacts"` shows no new failures against the pre-change baseline (Qt-binding reds are environmental; `pypi_artifacts` reds are the known Bucket C gate)
- [x] 6.3 `python tools/check_docs.py --path .` and `python tools/check_seps.py --path .` both exit 0
