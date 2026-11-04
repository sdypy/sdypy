## ADDED Requirements

### Requirement: Standardised readthedocs.yaml on the oldest supported Python

All seven `readthedocs.yaml` files (core + six siblings) SHALL conform to one shape: `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python` set to the oldest version of the supported set (`sibling-package-template` *Supported Python versions follow SPEC 0*), `sphinx.configuration: docs/source/conf.py`, and `python.install` using pip with the `docs` extra (`pip install .[docs]`). The Documentation URL in each package's `pyproject.toml` `[project.urls]` SHALL reflect the package's class: EMA and io keep their own RTD URLs; `sdypy-view` switches to `https://sdypy-view.readthedocs.io/`; `sdypy-model` gains a Documentation URL pointing at `https://sdypy-model.readthedocs.io/`; FRF and excitation retain their upstream backend documentation URLs per change #3 D6.

#### Scenario: Core readthedocs.yaml uses ubuntu-24.04 and the oldest supported Python
- **WHEN** the core `readthedocs.yaml` is read
- **THEN** `build.os` is `ubuntu-24.04`, `build.tools.python` is the oldest version of the supported set, and `sphinx.configuration` is `docs/source/conf.py`

#### Scenario: All sibling readthedocs.yaml files share the standard shape
- **WHEN** `readthedocs.yaml` in each of the six sibling clones is read
- **THEN** each sets `version: 2`, `build.os: ubuntu-24.04`, `build.tools.python` to the oldest version of the supported set, and installs via `pip install .[docs]`

#### Scenario: A docs Python other than the oldest supported version is reported
- **WHEN** `python tools/check_sibling_template.py --path <sibling>` is run on a clone whose `readthedocs.yaml` sets `build.tools.python` to a version other than the oldest of the supported set
- **THEN** the checker reports the docs Python and exits non-zero

#### Scenario: sdypy-view Documentation URL points at own RTD
- **WHEN** `[project.urls]` in `sdypy-view/pyproject.toml` is read
- **THEN** the `Documentation` key value is `https://sdypy-view.readthedocs.io/` or equivalent own-RTD URL

#### Scenario: check_docs.py detects wrong Documentation URL class
- **WHEN** `tools/check_docs.py --path <sdypy-view>` is run on a `sdypy-view` clone whose Documentation URL still points at its GitHub homepage
- **THEN** the script exits non-zero and reports the URL class mismatch

## REMOVED Requirements

### Requirement: Standardised readthedocs.yaml
**Reason**: It pins `build.tools.python: "3.12"`, including in a scenario name, while SPEC 0 dropped 3.12 on 2026-10-02; a package whose floor rises past the pinned version can no longer build its docs. A MODIFIED block cannot rename a scenario, so the requirement is replaced rather than edited.
**Migration**: Replaced by *Standardised readthedocs.yaml on the oldest supported Python*, which keeps every other obligation unchanged, takes the docs Python from the supported set, and adds a checker scenario.
