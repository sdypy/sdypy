## 1. Release workflow

- [x] 1.1 Rewrite `.github/workflows/release-and-publish-to-pypi.yml`: `workflow_dispatch` with `version`, default-branch check, version guard and bump, commit and tag, build, distribution check, atomic push, upload; publish job (environment `pypi`, `id-token: write`, token password); GitHub Release job
- [x] 1.2 actionlint is clean on the workflow
- [x] 1.3 Dry run on a clone of the hub: bump 0.6.0 → 0.6.1, build, distribution check pass; a second run is refused because the tag exists

## 2. Checker

- [x] 2.1 `check_release_workflow` compares the sibling's copy with the hub's, line endings aside; reports a missing hub copy instead of passing
- [x] 2.2 Keep the underscore-variant and `sync_version` checks; update the module docstring

## 3. Documentation

- [x] 3.1 `AGENTS.md` § Releasing: who, before, run, what it does, failures, check, don't
- [x] 3.2 Hub link block: add the `AGENTS.md § Releasing` link
- [x] 3.3 `AGENTS.md`: a version bump is not a PR, drop it from the trivial-change list
- [x] 3.4 `CONTRIBUTING.rst` and `docs/source/dev/readme.dev.rst` point at § Releasing; the SEP 2 pending-terms reminder moves there

## 4. Tests

- [x] 4.1 `tests/test_release_workflow.py`: checker (verbatim, line endings, drift, old tag workflow, missing, underscore, unreadable hub copy)
- [x] 4.2 Workflow shape: triggers, default-branch step, commit/tag/build order, atomic push before publishing, concurrency, actions and auth
- [x] 4.3 Embedded guards run from the workflow: bump writes only `[project] version`; malformed, existing-tag, not-newer and dynamic versions refused; distribution check passes and refuses
- [x] 4.4 Docs: `## Releasing` exists and the link block links to it
- [x] 4.5 `pytest -m "not pypi_artifacts"` on Python 3.13 locally — 182 passed
- [ ] 4.6 CI green on the PR

## 5. Verification and roster

- [x] 5.1 `openspec validate one-step-release --strict` is clean
- [ ] 5.2 At archive: update the `REQUIREMENTS.md` rows (*Canonical release workflow* and the new requirements → `check_sibling_template.py` and `tests/test_release_workflow.py`; *Core release workflow* → `tests/test_release_workflow.py`), and add § Pending entries: each sibling copies the workflow and the link block (six PRs), first hub release made by the workflow, optional `v*` tag ruleset
