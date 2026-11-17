## Why

The canonical release workflow (`release-and-publish-to-pypi.yml`) bumps the
version, commits, tags, pushes to the default branch and publishes to PyPI
without running the test suite. The default branches are not protected, so a
commit whose tests fail can be released. `AGENTS.md` § Releasing asks the
maintainer to check that CI is green first, but nothing enforces it.

Non-trivial: it changes spec requirements of `sibling-package-template` and
`testing-ci`.

## What Changes

- **The release runs the repository's own tests first.** The release workflow
  calls the repository's test workflow, `.github/workflows/python-package.yml`,
  as a reusable workflow on the commit being released. The job that bumps,
  tags and pushes `needs` it, so a failing test, lint or build step stops the
  release before anything is changed or published.
- **The test workflow can be called.** `python-package.yml` gains an
  `on: workflow_call` trigger. Its other triggers, matrix and steps stay as
  they are.
- **The default-branch check becomes the first job.** It used to be the first
  step of the release job; the tests now run before that job, and the check
  must still come before any checkout.
- **The gate is the same in every repository.** The test workflow's file name
  is already fixed by the sibling template, so the release workflow stays one
  file copied verbatim. The template checker also requires the
  `workflow_call` trigger in a sibling's `python-package.yml`.
- `AGENTS.md` § Releasing says the workflow runs the tests first.

## Non-goals

- Reordering the push and the publish (the push still comes before PyPI).
- Branch protection on the default branches (on hold, tracked in
  `REQUIREMENTS.md` § Pending).
- Cleaning up the `PYPI_API_TOKEN` / trusted-publishing fallback.
- Gating the release on the docs build (`docs.yml`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sibling-package-template`: MODIFIED *Canonical test workflow on the
  supported Python set* (adds the `workflow_call` trigger), MODIFIED
  *Releases start only by hand from the default branch* (the check is the
  first job, before any checkout); ADDED *The release runs the repository's
  tests first*.
- `testing-ci`: MODIFIED *Core test workflow has the required shape* (adds the
  `workflow_call` trigger).

## Impact

- Hub: `.github/workflows/release-and-publish-to-pypi.yml`,
  `.github/workflows/python-package.yml`, `tools/check_sibling_template.py`,
  `tests/test_release_workflow.py`, `tests/test_sibling_template.py`,
  `AGENTS.md` § Releasing, `REQUIREMENTS.md` (at archive).
- Siblings are not required to follow at once; other work on their
  templates is in progress. Until a sibling copies the new release workflow
  and adds `workflow_call` to its `python-package.yml`, its existing release
  keeps working and `check_sibling_template.py` reports the drift when run on
  it. Adoption is tracked in `REQUIREMENTS.md` § Pending, and neither the
  archive of this change nor any check waits on it.
- A release takes as long as the test matrix plus the release itself.
