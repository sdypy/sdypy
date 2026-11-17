## MODIFIED Requirements

### Requirement: Canonical test workflow on the supported Python set
Every first-level sdypy namespace package SHALL provide a GitHub Actions test workflow at `.github/workflows/python-package.yml`. The workflow SHALL trigger on push and pull-request events and SHALL be callable by another workflow (`workflow_call`), so the canonical release workflow can run it, run on `ubuntu-latest`, exercise a Python matrix that covers the supported set, install the package via `pip install .` or `pip install .[<extras>]`, run `flake8` and `pytest`, include a `python -m build` validation step, and use non-deprecated action major versions (at minimum `actions/checkout@v4` and `actions/setup-python@v5`).

#### Scenario: Test workflow file is named python-package.yml
- **WHEN** `.github/workflows/` is inspected
- **THEN** a file named `python-package.yml` exists and no file named `pytest.yaml` exists

#### Scenario: Test workflow triggers on push and pull_request
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the `on:` block includes both `push` and `pull_request` triggers

#### Scenario: Test workflow matrix covers the supported set
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the matrix `python-version` list contains every version of the supported set

#### Scenario: Test workflow installs the package from pyproject
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the install step is `pip install .` or `pip install .[<extras>]` (quoted or not) and no step reads a `requirements*.txt` file

#### Scenario: Test workflow includes build validation step
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** a step runs `python -m build` so a broken sdist or wheel fails CI rather than the next release

#### Scenario: Test workflow uses non-deprecated action versions
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** every `uses:` reference to `actions/checkout` is at `@v4` or later and every reference to `actions/setup-python` is at `@v5` or later

#### Scenario: Test workflow can be called by the release workflow
- **WHEN** `.github/workflows/python-package.yml` is inspected
- **THEN** the `on:` block includes a `workflow_call` trigger

#### Scenario: A test workflow without workflow_call is reported
- **WHEN** `python tools/check_sibling_template.py` runs on a clone whose `python-package.yml` has no `workflow_call` trigger
- **THEN** it reports the missing `workflow_call` trigger and exits non-zero

### Requirement: Releases start only by hand from the default branch
The canonical release workflow SHALL be triggered only by `workflow_dispatch` with a required `version` input and MUST NOT trigger on a tag push or any other event. Run from any ref other than the repository's default branch, it SHALL fail before any job checks out the repository, runs the tests, or changes or publishes anything.

#### Scenario: The workflow is started by hand with a version
- **WHEN** the workflow's `on:` block is inspected
- **THEN** it holds only `workflow_dispatch`, with a required `version` input

#### Scenario: A hand-pushed tag publishes nothing
- **WHEN** a maintainer pushes a `v*` tag by hand
- **THEN** no workflow run starts, because no trigger of the release workflow matches a tag push

#### Scenario: A run off the default branch fails
- **WHEN** the workflow is started on a branch other than the default branch
- **THEN** the workflow's first job, which checks out nothing, fails with an error naming the default branch
- **AND** every other job depends on it, directly or through another job, so none of them runs

## ADDED Requirements

### Requirement: The release runs the repository's tests first
The canonical release workflow SHALL run the repository's own test workflow, `.github/workflows/python-package.yml`, as a reusable workflow in the same run, on the commit being released, and the job that bumps, tags and pushes SHALL depend on it, so that the release MUST NOT bump, tag, push or publish unless every job of the test workflow passes. The call SHALL name the test workflow by that repository-relative path, grant it only `contents: read`, and pass it no secrets.

#### Scenario: The release job needs the test job
- **WHEN** the release workflow is inspected
- **THEN** a job `test` calls `./.github/workflows/python-package.yml` with `permissions: contents: read` and no `secrets`
- **AND** the job that bumps, tags and pushes declares `needs: test`, and the publish and GitHub Release jobs follow it

#### Scenario: Failing tests stop the release
- **WHEN** any job of the called test workflow fails
- **THEN** the job that bumps, tags and pushes does not run, nothing is pushed and nothing is published

#### Scenario: The gate is the same in every repository
- **WHEN** a sibling's release workflow is a verbatim copy of the hub's
- **THEN** it runs that sibling's own `python-package.yml`, because the call names the repository-relative path that the template requires
