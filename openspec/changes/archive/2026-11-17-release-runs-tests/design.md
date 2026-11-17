## Context

- The release workflow is the hub's file, copied verbatim into every sibling
  and compared by `tools/check_sibling_template.py`, so the gate cannot name
  anything package-specific.
- The sibling template already fixes the test workflow's file name:
  *Canonical test workflow on the supported Python set* requires
  `.github/workflows/python-package.yml`, and the checker reports it missing.
- No default branch is protected, so no required status check exists to rely
  on.
- A `workflow_dispatch` run has `github.sha` = the head of the default branch
  when the run started; every `actions/checkout` in the run, including in a
  called workflow, checks out that commit.

## Decisions

**1. Call the test workflow as a reusable workflow.** The release workflow
gets a job `test` with `uses: ./.github/workflows/python-package.yml`, and
`python-package.yml` gets `on: workflow_call`. The release job `needs: test`.
The tests run in the same run, on the same commit the release job checks out,
with the same matrix, lint and build steps as on a push. The path is the same
in every repository, so the release file stays verbatim.
*Alternative rejected:* query the check runs of `HEAD` with `gh api` before
bumping. It needs the name of the check to wait for, has to handle checks that
are still running or never ran (a commit pushed by `GITHUB_TOKEN` triggers no
workflow), and tests a different run than the one releasing. Not simpler.

**2. The default-branch check becomes its own first job.** With the tests in
a job before `release`, a check that stays the first step of `release` would
come after the test job's checkout and after a full matrix run. A job
`default-branch` (one step, no checkout) runs first and `test` needs it. A
failure there skips the rest of the run, which shows as failed, not skipped.
*Alternative rejected:* an `if:` on the test job, which would show a skipped,
green-looking run (decision 4 of `one-step-release`).

**3. Least privilege for the called workflow.** The `test` job declares
`permissions: contents: read` and passes no secrets (no `secrets: inherit`).
The test workflow needs neither write access nor secrets.

**4. Enforce the trigger in the checker.** A sibling copying the new release
workflow without adding `workflow_call` to its test workflow would have a
release workflow that GitHub refuses to start. `check_test_workflow` reports
a `python-package.yml` with no `workflow_call` trigger, so the template check
catches it before a release is attempted.

## Risks / Trade-offs

- **A missing or uncallable test workflow stops the release.** If a
  repository's `python-package.yml` is renamed, missing, or has no
  `workflow_call` trigger, GitHub rejects the release workflow when it starts
  (invalid workflow) and nothing runs. The failure is loud and nothing is
  changed; the checker reports the cause beforehand.
- **Order of the sibling update.** A sibling that copies the release workflow
  must add `workflow_call` to `python-package.yml` in the same PR, otherwise
  its next release fails at start-up as above.
- **Flaky tests block a release.** Re-run the failed jobs; the release job
  then runs.
- **Longer releases.** The run takes the matrix time plus the release. If the
  default branch moves during the tests, the atomic push is rejected as
  before and nothing is published.
- **The release commit itself is not tested.** It differs from the tested
  commit only by the version line, and the run builds and checks the
  distributions from it.
- **Concurrency.** The run-level `concurrency: release` group also covers the
  called test jobs; a push-triggered run of `python-package.yml` is a
  separate run and is unaffected.
