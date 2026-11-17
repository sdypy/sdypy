## 1. Workflows

- [x] 1.1 `python-package.yml`: add `workflow_call` to `on:`; triggers, matrix and steps otherwise unchanged
- [x] 1.2 `release-and-publish-to-pypi.yml`: move the default-branch refusal into a first job `default-branch`; add a job `test` (`uses: ./.github/workflows/python-package.yml`, `needs: default-branch`, `permissions: contents: read`, no secrets); `release` declares `needs: test`
- [ ] 1.3 Both workflows parse as YAML (done, PyYAML); actionlint not run — not installed locally, run it before merge or rely on GitHub rejecting an invalid workflow on the PR (not run: actionlint unavailable; workflows parse and CI passes)

## 2. Checker

- [x] 2.1 `check_test_workflow` reports a `python-package.yml` without a `workflow_call` trigger

## 3. Documentation

- [x] 3.1 `AGENTS.md` § Releasing: the workflow runs the tests first, a failing test stops the release

## 4. Tests

- [x] 4.1 `tests/test_release_workflow.py`: the release job needs the test job, which calls `./.github/workflows/python-package.yml` with read-only permissions and no secrets; publish and GitHub Release follow `release`; negative test on a workflow whose release job does not need the tests
- [x] 4.2 `tests/test_release_workflow.py`: the default-branch job is first, checks out nothing, and `test` needs it
- [x] 4.3 `tests/test_release_workflow.py`: the hub's `python-package.yml` has `workflow_call` next to `push`, `pull_request` and `workflow_dispatch`
- [x] 4.4 `tests/test_sibling_template.py`: a sibling test workflow without `workflow_call` is reported; one with it passes
- [x] 4.5 `pytest -m "not pypi_artifacts"` passes locally (Python 3.13: 189 passed); `check_docs.py` and `check_seps.py` pass
- [x] 4.6 CI green on the PR

## 5. Verification and roster

- [x] 5.1 `openspec validate release-runs-tests --strict` and `openspec validate --all --strict` are clean
- [x] 5.2 At archive: `REQUIREMENTS.md` rows — *The release runs the repository's tests first* → `tests/test_release_workflow.py` tests from 4.1; *Releases start only by hand* → 4.2 test; *Canonical test workflow* → 4.4 tests; *Core test workflow* → 4.3 test; § Pending entry for the sibling follow-ups below

## 6. Sibling adoption (recommended, not part of this change)

Siblings adopt the gate in their own time: copy the hub's new `release-and-publish-to-pypi.yml` and, in the same PR, add `workflow_call` to `python-package.yml`. Nothing here waits on it; it goes to `REQUIREMENTS.md` § Pending with the archive.
