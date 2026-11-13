## Context

- Issue sdypy/sdypy#33, option 3, chosen by the team.
- Neither the hub's `main` nor the siblings' default branches are protected
  (checked 2026-11-06); four siblings use `master`, the hub, EMA and FRF use
  `main`.
- sdypy-EMA publishes by trusted publishing (environment `pypi`, this workflow
  file name); the hub and the other five use the `PYPI_API_TOKEN` secret.
- `pypa/gh-action-pypi-publish` takes the trusted-publishing path when the
  password is empty (`twine-upload.sh`, v1.14.3), and an absent secret
  evaluates to an empty string.

## Decisions

**1. One file, copied verbatim.** The workflow has nothing package-specific:
the default branch is read from the event, the package name from the built
files. The checker compares a sibling's copy with the hub's (line endings
aside), as it already does for the link block and the shared rules. Changing
the release procedure is then one hub edit plus a copy. *Alternative:* check
the workflow's shape with regular expressions, which accepts drift the hub
never reviewed.

**2. Token or trusted publishing from the same step.** The publish job runs in
the `pypi` environment with `id-token: write` and passes
`secrets.PYPI_API_TOKEN` as the password. A repository with the secret uploads
with it; one without it uses trusted publishing. Moving a repository to trusted
publishing is then a PyPI setting plus deleting the secret, not a workflow
change.

**3. Bump, build and check before pushing.** The commit and the tag are made
locally, the distributions are built and checked, and only then are both
pushed with `git push --atomic`. A refused version or a failed build leaves
the repository untouched. If the default branch moved during the run, the push
is rejected as non-fast-forward and nothing is published. `concurrency: release`
keeps two runs from racing.

**4. Fail, don't skip, off the default branch.** A job-level `if:` would show a
green, skipped run; a first step that exits with an error says why.

**5. The guards live in the workflow and are tested from it.** The version and
distribution checks are Python heredocs in the workflow, marked
`# release-step: <name>`. The tests extract them and run them against
fixtures, so what is tested is what runs, and siblings need no helper script.

**6. Rewrite only the `[project]` version line.** `hatch version` refuses a
static `project.version`, so the step rewrites the `version = "..."` line of
the `[project]` table with a regular expression and re-parses the file with
`tomllib` to confirm the result.

## Risks / Trade-offs

- **The workflow pushes to the default branch.** If branch protection is
  added later, the `GITHUB_TOKEN` push is refused; protection then needs a
  bypass for the workflow, or the release stops. The failure is loud and
  nothing is published.
- **A run that fails after the push** (PyPI outage, GitHub Release) leaves the
  tag and the bump commit in place. The documented fix is to re-run the
  failed jobs, which reuse the stored distributions.
- **Pushes by `GITHUB_TOKEN` trigger no workflows**, so CI does not run on the
  release commit. It changes only the version line, and the run built and
  checked the distributions.
- **Every sibling is reported** until its own PR copies the workflow and the
  link block.
