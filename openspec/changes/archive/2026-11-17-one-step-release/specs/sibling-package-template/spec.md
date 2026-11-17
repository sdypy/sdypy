## MODIFIED Requirements

### Requirement: Version single-sourced via installed metadata
Every first-level sdypy namespace package SHALL declare the authoritative version as a literal string in the `[project]` table of `pyproject.toml`. The corresponding `sdypy/<pkg>/__init__.py` SHALL derive `__version__` from installed distribution metadata via `importlib.metadata.version("sdypy-<pkg>")` with a `PackageNotFoundError` fallback of `"0+unknown"`. No `sync_version.py` script SHALL exist, and no workflow SHALL write the version anywhere except the release workflow's bump of `[project] version` in `pyproject.toml`.

#### Scenario: pyproject.toml contains literal version
- **WHEN** `pyproject.toml` is inspected
- **THEN** the `[project]` table contains a `version = "X.Y.Z"` literal (not `dynamic = ["version"]`)

#### Scenario: __init__.py derives __version__ from metadata
- **WHEN** `sdypy/<pkg>/__init__.py` is inspected
- **THEN** it contains `importlib.metadata.version("sdypy-<pkg>")` and a `PackageNotFoundError` handler that sets `__version__ = "0+unknown"`

#### Scenario: __version__ matches installed distribution after pip install
- **WHEN** the package is installed with `pip install .` (from a neutral directory, not the parent `SdyPy/` folder) and `import sdypy.<pkg>; print(sdypy.<pkg>.__version__)` is executed
- **THEN** the printed string matches the `version` field in `pyproject.toml`

#### Scenario: __version__ fallback in uninstalled source checkout
- **WHEN** `sdypy/<pkg>/__init__.py` is imported in a Python process where the distribution metadata is not present
- **THEN** `__version__` equals `"0+unknown"` without raising an exception

#### Scenario: Release workflow contains no version-sync step
- **WHEN** the workflows under `.github/workflows/` are inspected
- **THEN** no step references `sync_version.py`, and the only step that writes a version is the release workflow's bump of `[project] version` in `pyproject.toml`

## ADDED Requirements

### Requirement: Release workflow is the hub's file, copied verbatim
Every first-level sdypy namespace package SHALL provide `.github/workflows/release-and-publish-to-pypi.yml` whose content is the hub's file of the same name, character for character apart from line endings. The hub's copy is the file's only home; a sibling MUST NOT edit its copy. No file named with an underscore variant (e.g. `release_and_publish_to_pypi.yml`) SHALL exist.

#### Scenario: A verbatim copy conforms
- **WHEN** a sibling's release workflow equals the hub's, or differs from it only in line endings
- **THEN** no release-workflow violation is reported

#### Scenario: A drifted copy is reported
- **WHEN** a sibling's release workflow differs from the hub's in any other character, including the old tag-triggered workflow
- **THEN** the checker reports that it differs from the hub's release workflow and exits non-zero

#### Scenario: A missing release workflow is reported
- **WHEN** a sibling has no `.github/workflows/release-and-publish-to-pypi.yml`
- **THEN** the checker reports the missing file and exits non-zero

#### Scenario: An underscore-named variant is reported
- **WHEN** `.github/workflows/` contains a file such as `release_and_publish_to_pypi.yml`
- **THEN** the checker reports the underscore-named release workflow

#### Scenario: An unreadable hub copy is reported, not passed
- **WHEN** the checker cannot read the hub's release workflow
- **THEN** it reports the sibling's copy as unchecked instead of passing it


### Requirement: Releases start only by hand from the default branch
The canonical release workflow SHALL be triggered only by `workflow_dispatch` with a required `version` input and MUST NOT trigger on a tag push or any other event. Run from any ref other than the repository's default branch, it SHALL fail before checking out, changing or publishing anything.

#### Scenario: The workflow is started by hand with a version
- **WHEN** the workflow's `on:` block is inspected
- **THEN** it holds only `workflow_dispatch`, with a required `version` input

#### Scenario: A hand-pushed tag publishes nothing
- **WHEN** a maintainer pushes a `v*` tag by hand
- **THEN** no workflow run starts, because no trigger of the release workflow matches a tag push

#### Scenario: A run off the default branch fails
- **WHEN** the workflow is started on a branch other than the default branch
- **THEN** its first step fails with an error naming the default branch, before the checkout

### Requirement: The release workflow writes the version into pyproject.toml
The release workflow SHALL write the requested version into the `version` line of the `[project]` table of `pyproject.toml`, and into no other line, and SHALL confirm by re-parsing the file that `[project] version` now equals the requested version.

#### Scenario: Only the project version changes
- **WHEN** the bump step runs with a valid new version on a `pyproject.toml` that also has a `version` key in a `[tool.*]` table
- **THEN** `[project] version` equals the new version, the `[tool.*]` value is unchanged, and no other byte of the file changes

### Requirement: The release tag sits on the version commit
The release workflow SHALL commit the bumped `pyproject.toml` as *Release X.Y.Z* and SHALL create the annotated tag `vX.Y.Z` on that commit, before building the distributions.

#### Scenario: Commit, tag, then build
- **WHEN** the workflow's steps are inspected
- **THEN** the bump precedes the commit, the commit precedes the tag, and the tag precedes `python -m build`

### Requirement: The release is pushed atomically before it is published
The release workflow SHALL push the release commit to the default branch and the tag in one `git push --atomic`, after the distributions are built and checked and before the publish job runs. Release runs SHALL be serialised, so two runs never race.

#### Scenario: Push after the checks, before publishing
- **WHEN** the workflow is inspected
- **THEN** the atomic push of `HEAD:refs/heads/<default branch>` and `refs/tags/v<version>` follows the distribution check, and the publish job `needs` the job that pushes

#### Scenario: A moved default branch stops the release
- **WHEN** the default branch gained a commit after the run started
- **THEN** the atomic push is rejected as non-fast-forward, neither ref is pushed and nothing is published

#### Scenario: Releases are serialised
- **WHEN** the workflow is inspected
- **THEN** it declares `concurrency` group `release` with `cancel-in-progress: false`

### Requirement: The release workflow refuses an inconsistent version
The release workflow SHALL fail before pushing or publishing anything when the requested version is not `X.Y.Z` optionally followed by `aN`, `bN` or `rcN`, when the tag `v<version>` already exists, when the version is not newer than the current `[project] version`, when `pyproject.toml` has no literal `[project] version`, or when the built distributions are not exactly one wheel and one sdist carrying the requested version.

#### Scenario: A malformed version is refused
- **WHEN** the bump step runs with `1.3`, `v1.3.0`, `1.3.0.dev1`, an empty string, or a version with surrounding whitespace
- **THEN** it fails with an error saying the version is not `X.Y.Z` and leaves `pyproject.toml` unchanged

#### Scenario: An existing tag is refused
- **WHEN** the bump step runs with a version whose `v` tag already exists
- **THEN** it fails with an error naming the existing tag and leaves `pyproject.toml` unchanged

#### Scenario: A version not newer than the current one is refused
- **WHEN** the bump step runs with a version equal to or older than the current `[project] version`, including a pre-release of it
- **THEN** it fails with an error naming the current version

#### Scenario: A dynamic version is refused
- **WHEN** `pyproject.toml` declares `dynamic = ["version"]` instead of a literal version
- **THEN** the bump step fails with an error saying there is no literal `[project]` version

#### Scenario: Distributions carrying another version are refused
- **WHEN** the distribution check runs and a wheel or sdist carries a version other than the requested one, or one of them is missing
- **THEN** it fails before the push

### Requirement: Releasing is documented once, in the hub
The hub's `AGENTS.md` SHALL have a `## Releasing` section that names the canonical release workflow as the only way to release, and the hub link block SHALL link to that section, so every sibling's `AGENTS.md` reaches it through its verbatim copy of the block.

#### Scenario: The hub documents releasing
- **WHEN** the hub's `AGENTS.md` is inspected
- **THEN** it has a `## Releasing` section that names `release-and-publish-to-pypi.yml`

#### Scenario: The link block reaches the section
- **WHEN** the hub link block is extracted
- **THEN** it contains a link to `https://github.com/sdypy/sdypy/blob/main/AGENTS.md#releasing`

## REMOVED Requirements

### Requirement: Canonical release workflow
**Reason**: It requires the workflow to trigger on a `v*` tag push, which is the two-step release that issue sdypy/sdypy#33 replaces: a hand-made tag published whatever version `pyproject.toml` held, and nothing checked that the two agreed. A MODIFIED block cannot drop the tag-trigger scenario, so the requirement is replaced rather than edited.
**Migration**: Replaced by *Release workflow is the hub's file, copied verbatim* (file name, no underscore variant, the hub's content) and *Releases start only by hand from the default branch*; building and publishing are covered by the copied file and by `testing-ci` *Core release workflow has the required shape*.
