## 1. Checker

- [ ] 1.1 `tools/check_sibling_template.py`: the MIT classifier is required only for the table form; in both forms a non-MIT `License ::` classifier is reported

## 2. Tests

- [ ] 2.1 `tests/test_sibling_template.py`: one test per scenario of the delta spec

## 3. Verification and roster

- [ ] 3.1 `openspec validate accept-license-expression --strict` is clean
- [ ] 3.2 `pytest -m "not pypi_artifacts"` adds no failure to the baseline
- [ ] 3.3 In the archive commit, update REQUIREMENTS.md: add the new license tests to the verifier cell of *Metadata consistency with the supported Python set*
