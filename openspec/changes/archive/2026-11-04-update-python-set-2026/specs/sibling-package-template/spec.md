## MODIFIED Requirements

### Requirement: Supported Python versions follow SPEC 0
The Python minor versions a first-level sdypy namespace package supports SHALL follow Scientific Python's SPEC 0: from the oldest minor version released less than three years ago through the newest stable CPython release for which the current NumPy and SciPy releases both publish wheels. The concrete set SHALL be declared in exactly one place, the sibling template checker; every other requirement refers to it as *the supported set*. At the time of this change (2026-11-04) the supported set is 3.13, 3.14 and 3.15.

#### Scenario: The declared set matches SPEC 0
- **WHEN** the supported set declared in the checker is compared with the SPEC 0 drop schedule, the CPython release list and the wheels published by the current NumPy and SciPy releases
- **THEN** it contains every stable minor version released less than three years ago for which both publish wheels, and no older one

#### Scenario: The set has a single declaration
- **WHEN** the hub's tools, tests and specs are searched for the supported Python versions of a sibling
- **THEN** the concrete versions appear only in the checker's declaration and in this requirement's dated note

## ADDED Requirements

### Requirement: Backend libraries support the supported Python set
The backend libraries the consortium maintains and the first-level packages wrap or depend on (pyFRF, pyExSi, pyEMA, pyuff, pyLump, lvm_read and pyMRAW) SHALL support the supported set: a `requires-python` floor equal to its oldest version, a `Programming Language :: Python :: 3.x` classifier for every version of the set and for no other version, a CI test matrix that covers the set, and, where the library has a `readthedocs.yaml`, a docs build on the set's oldest version. Running the sibling template checker with `--python-only` on a clone SHALL check exactly these points, without requiring an `sdypy/` portion, and exit non-zero on any mismatch.

#### Scenario: A conforming backend passes the Python-only check
- **WHEN** `python tools/check_sibling_template.py --python-only --path <backend-clone>` is run on a clone whose floor, classifiers, workflow matrix and docs Python follow the supported set
- **THEN** the checker exits 0

#### Scenario: An old floor is reported
- **WHEN** the Python-only check runs on a clone declaring `requires-python = ">=3.10"`
- **THEN** the checker reports the floor and exits non-zero

#### Scenario: A matrix missing a supported version is reported
- **WHEN** the Python-only check runs on a clone whose workflows do not test every version of the supported set
- **THEN** the checker reports the matrix and exits non-zero

#### Scenario: Only the Python points are checked
- **WHEN** the Python-only check runs on a clone that has no `sdypy/` portion, no `AGENTS.md` and no release workflow
- **THEN** none of these is reported
