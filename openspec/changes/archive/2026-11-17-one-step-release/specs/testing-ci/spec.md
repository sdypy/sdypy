## MODIFIED Requirements

### Requirement: Core release workflow has the required shape
The core `release-and-publish-to-pypi.yml` is the canonical release workflow of the `sibling-package-template` spec. It MUST use `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7` and `actions/download-artifact@v8`, build via `python -m build`, and publish via `pypa/gh-action-pypi-publish@release/v1` from a job in the `pypi` environment with `id-token: write` and `password: ${{ secrets.PYPI_API_TOKEN }}`, so that a repository with that secret publishes with the token and one without it publishes by trusted publishing.

#### Scenario: Release workflow uses current action versions and token auth
- **WHEN** `release-and-publish-to-pypi.yml` is inspected
- **THEN** `actions/checkout@v7`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/download-artifact@v8` and `pypa/gh-action-pypi-publish@release/v1` are used
- **AND** the publish step passes `password: ${{ secrets.PYPI_API_TOKEN }}`
- **AND** no Node 20 or older action majors remain (`@v1.4.2`, `@v2`, `@v3`, `actions/checkout@v4`, `actions/setup-python@v5`)

#### Scenario: One publish step serves token and trusted publishing
- **WHEN** the publish job is inspected
- **THEN** it runs in the `pypi` environment with `id-token: write` and passes `password: ${{ secrets.PYPI_API_TOKEN }}`
- **AND** in a repository without that secret the password is empty, and the publish action uses trusted publishing
