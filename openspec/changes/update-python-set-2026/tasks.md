## 1. Checker

- [ ] 1.1 Set `SUPPORTED_PYTHON = {"3.13", "3.14", "3.15"}` in `tools/check_sibling_template.py`
- [ ] 1.2 Move the floor and classifier checks into a helper shared by the full and the Python-only mode
- [ ] 1.3 Add the `readthedocs.yaml` check: `build.tools.python` equals the oldest supported version; skipped when the file is absent
- [ ] 1.4 Add `--python-only`: no portion lookup; checks floor, classifiers, the union of the Python versions in all workflow files, and the docs Python
- [ ] 1.5 Update the module docstring

## 2. Hub follows the set

- [ ] 2.1 `pyproject.toml`: `requires-python = ">=3.13"`, classifiers 3.13–3.15
- [ ] 2.2 `python-package.yml` matrix 3.13–3.15 (and its PySide6 comment); `docs.yml` and the release workflow on 3.13
- [ ] 2.3 `readthedocs.yaml`: `build.tools.python: "3.13"`
- [ ] 2.4 `AGENTS.md` § Development environment points to the supported set instead of naming versions

## 3. Tests

- [ ] 3.1 Tests for the docs Python check: matching passes, other version reported, absent file not reported
- [ ] 3.2 Tests for `--python-only`: conforming clone exits 0, old floor reported, missing matrix version reported, no portion / `AGENTS.md` / release workflow not reported
- [ ] 3.3 Test that the hub passes `--python-only` and its core matrix equals the set exactly
- [ ] 3.4 Run `pytest -m "not pypi_artifacts"` on Python 3.13 locally; CI green on 3.13, 3.14 and 3.15
- [ ] 3.5 Feed a synthetic violation (hub matrix with 3.12 added) and see the hub test fail

## 4. Verification and roster

- [ ] 4.1 `openspec validate update-python-set-2026 --strict` is clean
- [ ] 4.2 `grep -rn '3\.12' openspec/specs tools tests` after archive returns no Python-set hits
- [ ] 4.3 At archive: update the `REQUIREMENTS.md` rows (classifiers, core matrix, readthedocs, SPEC 0 set) and add the backend row (verifier: `check_sibling_template.py --python-only` and its tests)
