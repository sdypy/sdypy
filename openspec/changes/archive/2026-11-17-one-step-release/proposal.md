## Why

Since `standardize-package-template` the version lives only in
`pyproject.toml`, so a release takes two steps: a commit that bumps the
version, then a `v*` tag on that commit, which triggers the PyPI upload.
Nothing checks that the tag and the version agree, and nothing stops a tag,
a GitHub Release or a version edit made by hand. Issue sdypy/sdypy#33 laid out
three options; the team chose option 3: a release workflow, started by hand
with the version, that bumps, then tags, and publishes, plus a guard and one
documented way to release.

Non-trivial: it changes spec requirements of `sibling-package-template` and
`testing-ci`.

## What Changes

- **The release workflow is started by hand** (`workflow_dispatch`, input
  `version`) on the default branch. It no longer triggers on a tag push, so a
  hand-pushed `v*` tag publishes nothing.
- **It bumps, then tags.** It writes the version into `[project] version` of
  `pyproject.toml`, commits *Release X.Y.Z*, tags that commit `vX.Y.Z`, builds,
  pushes the commit and the tag in one atomic push, publishes to PyPI and
  creates the GitHub Release. `pyproject.toml` stays current and the tag sits
  on the commit that carries the version.
- **Guard.** Before anything is pushed it refuses a malformed version, an
  existing tag, a version not newer than the current one, and distributions
  that do not carry the version.
- **One file for every repository.** The hub's workflow is copied verbatim
  into each first-level package, and the template checker compares the copy
  with the hub's. The publish step uses `PYPI_API_TOKEN` where a repository has
  it and falls back to trusted publishing otherwise (sdypy-EMA already
  publishes that way), so one file serves both.
- **One documented way to release:** a *Releasing* section in the hub's
  `AGENTS.md`, linked from the hub link block that every sibling copies, and
  pointers from `CONTRIBUTING.rst` and `docs/source/dev/readme.dev.rst`.
- The release commit goes to the default branch without a PR. A version bump
  is no longer a PR at all, so `AGENTS.md` drops it from the list of trivial
  changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `sibling-package-template`: MODIFIED *Version single-sourced via installed
  metadata* (the release workflow's bump is the one writer), REMOVED
  *Canonical release workflow* (it requires the tag trigger); ADDED *Release
  workflow is the hub's file, copied verbatim*, *Releases
  start only by hand from the default branch*, *The release workflow writes
  the version into pyproject.toml*, *The release tag sits on the version
  commit*, *The release is pushed atomically before it is published*, *The
  release workflow refuses an inconsistent version*, *Releasing is documented
  once, in the hub*.
- `testing-ci`: MODIFIED *Core release workflow has the required shape*
  (artifact actions, the `pypi` environment, token or trusted publishing).

## Impact

- Hub: `.github/workflows/release-and-publish-to-pypi.yml`,
  `tools/check_sibling_template.py`, `tests/test_release_workflow.py`,
  `AGENTS.md` (section and link block), `CONTRIBUTING.rst`,
  `docs/source/dev/readme.dev.rst`, `REQUIREMENTS.md` (at archive).
- Every sibling is reported by the checker until it copies the new workflow
  and the changed link block, in its own PR (tracked in `REQUIREMENTS.md`
  § Pending, not in this change).
- Repository settings, not files: the default branch must accept pushes from
  the workflow's `GITHUB_TOKEN` (no branch protection today); a tag ruleset on
  `v*` is optional.
