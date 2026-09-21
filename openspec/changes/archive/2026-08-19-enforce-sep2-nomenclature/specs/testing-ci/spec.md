## ADDED Requirements

### Requirement: Every umbrella-runnable checker executes in core CI
Every `tools/check_*.py` conformance checker that is capable of running against the umbrella repository root SHALL be executed as a step in the core GitHub Actions workflows. Checkers that require a single-portion sibling clone and therefore cannot run at the umbrella root SHALL NOT be claimed as CI-covered; the documentation that lists them MUST record where they do run and show an invocation that succeeds.

At the time of this requirement, `tools/check_seps.py` and `tools/check_docs.py` run at the umbrella root and SHALL both execute in `docs.yml`; `tools/check_public_api.py` and `tools/check_sibling_template.py` require a sibling clone, because they resolve exactly one portion directory under `sdypy/` and the umbrella provides none.

#### Scenario: The documentation checker runs in CI
- **WHEN** the `docs.yml` workflow runs
- **THEN** it executes `python tools/check_docs.py --path .` and fails the job if the checker exits non-zero

#### Scenario: A sibling-clone checker is not claimed as CI-covered
- **WHEN** `REQUIREMENTS.md` § Canonical sources is inspected
- **THEN** it does not state that `check_public_api.py` or `check_sibling_template.py` runs in this repository's CI
- **AND** it records that they audit a sibling clone

#### Scenario: Documented invocations succeed as written
- **WHEN** a reader runs any checker invocation shown in `AGENTS.md` § Common commands, in the directory that entry specifies
- **THEN** the command runs to a verdict — it does not fail with "expected exactly one portion under .../sdypy"
