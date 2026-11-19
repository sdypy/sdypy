## MODIFIED Requirements

### Requirement: Core test workflow has the required shape
The core `python-package.yml` MUST be triggered on `push`, `pull_request`, `workflow_dispatch` and `workflow_call` events. The matrix SHALL be exactly the supported set (declared in `tools/check_sibling_template.py`, `sibling-package-template` *Supported Python versions follow SPEC 0*) with `fail-fast: false`. The workflow MUST use `actions/checkout@v7` and `actions/setup-python@v7`, which run on the Node 24 runtime; the `@v4` / `@v5` majors used previously run on the deprecated Node 20 and MUST NOT be reintroduced. The install step SHALL run `pip install .` followed by `pip install pytest flake8 build`. The workflow MUST include the existing two-pass flake8 check, the `pytest -m "not pypi_artifacts"` step, and a final `python -m build` validation step.

#### Scenario: Workflow triggers are correct
- **WHEN** `python-package.yml` is inspected
- **THEN** the `on:` section lists `push`, `pull_request`, `workflow_dispatch` and `workflow_call`

#### Scenario: Matrix and action versions are correct
- **WHEN** `python-package.yml` is inspected
- **THEN** the matrix lists exactly the versions of the supported set, with `fail-fast: false`
- **AND** `actions/checkout@v7` and `actions/setup-python@v7` are used (Node 24; no Node 20 majors such as `actions/checkout@v4` or `actions/setup-python@v5`, and nothing older)

#### Scenario: Workflow includes build validation step
- **WHEN** `python-package.yml` is inspected
- **THEN** a step running `python -m build` is present after the pytest step
