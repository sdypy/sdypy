## 1. Workflows

- [ ] 1.1 `python-package.yml`: add `workflow_call` to `on:`; triggers, matrix and steps otherwise unchanged
- [ ] 1.2 `release-and-publish-to-pypi.yml`: move the default-branch refusal into a first job `default-branch`; add a job `test` (`uses: ./.github/workflows/python-package.yml`, `needs: default-branch`, `permissions: contents: read`, no secrets); `release` declares `needs: test`
- [ ] 1.3 Both workflows parse as YAML; actionlint if available

## 2. Checker

- [ ] 2.1 `check_test_workflow` reports a `python-package.yml` without a `workflow_call` trigger

## 3. Documentation

- [ ] 3.1 `AGENTS.md` § Releasing: the workflow runs the tests first, a failing test stops the release

## 4. Tests

- [ ] 4.1 `tests/test_release_workflow.py`: the release job needs the test job, which calls `./.github/workflows/python-package.yml` with read-only permissions and no secrets; publish and GitHub Release follow `release`; negative test on a workflow whose release job does not need the tests
- [ ] 4.2 `tests/test_release_workflow.py`: the default-branch job is first, checks out nothing, and `test` needs it
- [ ] 4.3 `tests/test_release_workflow.py`: the hub's `python-package.yml` has `workflow_call` next to `push`, `pull_request` and `workflow_dispatch`
- [ ] 4.4 `tests/test_sibling_template.py`: a sibling test workflow without `workflow_call` is reported; one with it passes
- [ ] 4.5 `pytest -m "not pypi_artifacts"` passes locally; `check_docs.py` and `check_seps.py` pass
- [ ] 4.6 CI green on the PR

## 5. Verification and roster

- [ ] 5.1 `openspec validate release-runs-tests --strict` and `openspec validate --all --strict` are clean
- [ ] 5.2 At archive: `REQUIREMENTS.md` rows — *The release runs the repository's tests first* → `tests/test_release_workflow.py` tests from 4.1; *Releases start only by hand* → 4.2 test; *Canonical test workflow* → 4.4 tests; *Core test workflow* → 4.3 test; § Pending entry for the sibling follow-ups below

## 6. Sibling follow-ups (cross-repo, each in the sibling's own PR)

Each sibling copies the hub's new `release-and-publish-to-pypi.yml` verbatim **and**, in the same PR, adds `workflow_call` to its `python-package.yml`; `check_sibling_template.py --path <clone>` passes afterwards.

- [ ] 6.1 sdypy-EMA
- [ ] 6.2 sdypy-io
- [ ] 6.3 sdypy-FRF
- [ ] 6.4 sdypy-excitation
- [ ] 6.5 sdypy-model
- [ ] 6.6 sdypy-view
