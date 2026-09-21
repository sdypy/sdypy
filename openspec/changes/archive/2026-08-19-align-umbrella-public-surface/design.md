## Context

See proposal.md § Why for the motivation. The design-relevant state is narrow: `openspec/specs/public-api/spec.md` and `openspec/specs/sep005-standard/spec.md` both make a normative statement about the membership of `sdypy.__all__`, and they disagree. The tree (`sdypy/__init__.py`, `tests/test_public_api.py`, `REQUIREMENTS.md`, `AGENTS.md`, and the `public-api` spec's own `## Purpose` line) uniformly implements the `sep005`-inclusive side, so there is no question of *which* statement is right — only of how to record the correction without breaking the project's single-source-of-truth rule more than necessary.

Two mechanical constraints shape the edit:

1. OpenSpec's `MODIFIED` operation replaces a requirement block wholesale, and `openspec validate --strict` rejects a `MODIFIED` block that drops any scenario the current spec still has. Scenario *names* are therefore effectively frozen by this change; only their bodies are free.
2. A delta acts on requirements. The `**Scope:**` line in the spec preamble names the requirement being renamed and is outside the delta mechanism, so it needs a hand edit.

## Goals / Non-Goals

**Goals**
- Leave no canonical spec asserting something the test suite disproves.
- Make `public-api` self-sufficient: a reader asking "what is the umbrella's public surface?" gets the complete, correct answer without having to also read `sep005-standard`.

**Non-Goals**
- Changing any shipped behaviour, test, or tool. If this change alters a single byte under `sdypy/`, `tests/` or `tools/`, it has overstepped.
- Relocating the `sep005` alias contract out of `sep005-standard`. Ownership of *why* the alias exists and *what it resolves to* stays there.
- Touching the other six `public-api` requirements, which are org-wide and unaffected.

## Decisions

**D1 — Rename the requirement rather than only editing its body.** The header *"Umbrella `__all__` matches the six first-level names"* is itself the false statement; a reader scanning headers would carry away the wrong contract even if the body were fixed. *Alternative considered*: keep the header and correct only the body — rejected, because headers are the index into a spec and this one would then contradict the paragraph beneath it. *Alternative considered*: `REMOVED` + `ADDED` of a freshly named requirement — rejected: it is semantically wrong (the requirement is being corrected, not retired), it forces a fictitious `**Migration**` note, and it makes the outcome depend on the order in which archive applies two operations to the same block.

**D2 — Keep all three original scenario names verbatim.** Constraint 1 above forces this, but it costs nothing here, because each name stays literally true under the corrected contract: `sep005` is *not* a first-level name and *not* a sub-package, so "lists exactly the six first-level names" and "imports all six subpackages" both remain accurate statements about a seven-member `__all__`. The `sep005` clause is added as an `**AND**` line in each scenario instead. Had the names been falsified by the correction, `REMOVED` + `ADDED` would have become the honest option despite D1.

**D3 — Restate the `sep005` membership fact in `public-api`, accepting duplication with `sep005-standard`.** The project rule is "every fact has one home; other files link to it", and this change knowingly bends it. The justification is that the two capabilities answer different questions: `sep005-standard` answers "what is the SEP 5 standard and how is it reached from the umbrella", `public-api` answers "what is the curated public surface". Membership of `__all__` is genuinely part of both answers, and the failure mode of *not* duplicating it is exactly the one being fixed — a reader who stops at `public-api` gets a wrong answer. The duplication is bounded to one sentence and made explicit in the requirement text, which names `sep005-standard` as the owner of the alias contract, so a future editor sees the coupling instead of discovering it.

**D4 — No new test.** `test_umbrella_all_is_the_six_subpackages_plus_sep005` and `test_star_import_of_umbrella_yields_subpackages_and_sep005` already assert exactly the corrected requirement, including the "no others" clause (they compare sorted equality, not containment). Adding a test here would duplicate coverage to no end; the verification column in `REQUIREMENTS.md` is already correct and needs no row change.

## Risks / Trade-offs

- [The duplicated `sep005` sentence drifts out of sync with `sep005-standard` in a future change] → the requirement text names `sep005-standard` as the owner, and both are asserted by the same two tests, so a divergence in either spec is caught the moment someone tries to implement it. The tests, not the prose, remain the tie-breaker.
- [The renamed requirement leaves stale references elsewhere] → one is known and handled (the `**Scope:**` preamble line, task 2.2); `grep -rn "matches the six first-level names"` at apply time proves there are no others.
- [`RENAMED` + `MODIFIED` on the same requirement in one delta is a combination this repo has not used before — every archived change to date is pure `ADDED`] → `openspec validate --strict` already resolves the `MODIFIED` block against the renamed target and passes, and task 3.1 re-validates immediately before archive. If archive nevertheless mishandles the pair, the fallback is to apply the rename by hand in `openspec/specs/public-api/spec.md` and reduce the delta to `MODIFIED` alone.

## Migration Plan

None. No shipped artefact changes, so there is nothing to deploy and nothing to roll back; reverting the change is `git revert` of a specs-only commit.

## Open Questions

None. The contradiction has one factually determined resolution, and the tree already implements it.
