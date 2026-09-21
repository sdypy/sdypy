## 0. Precondition

- [x] 0.1 `extend-sep2-nomenclature` is archived and `openspec/specs/public-api/spec.md` contains
      the canonical-name requirements. The checker encodes that table; starting before it is
      final means encoding a moving target.

## 1. The checker

- [x] 1.1 Add `tools/check_nomenclature.py`, stdlib only (no third-party imports — it must run
      under `python-package.yml`, which installs only pytest, flake8, build and PySide6).
      CLI mirrors the existing checkers: `--path` (default `.`), one violation per line as
      `<file>: <rule>: <detail>`, exit `0` clean / `1` on any violation. Reuse
      `check_public_api.py`'s `find_portion_init` approach to locate the audited portion.
- [x] 1.2 Write the module docstring first, and state the coverage boundary in it: the checker
      does NOT decide whether a coined name is an established term of art, and does NOT verify
      that a deprecated alias emits `DeprecationWarning` or returns the canonical value. Those
      belong to sibling suites and to `manual` rows.
- [x] 1.3 Add the canonical table as a module-level dict mirroring `docs/seps/sep-0002.rst`,
      with a comment naming that file as the source: divergent spelling → canonical name
      (`xi`→`damping_ratio`, `phi`→`mode_shape`, `nat_freq`→`natural_freq`, `K`→`stiffness_matrix`,
      `M`→`mass_matrix`, `EI`→`stiffness_matrix`, `conec`→`elements`, `org`→`nodes`,
      `frequency`→`freq`, `lower`/`f_lower`→`freq_lower`, `upper`/`f_upper`→`freq_upper`,
      `frf_type`→`frf_form`).
- [x] 1.4 Implement signature auditing with `ast`, without importing the package: walk public
      `FunctionDef`/`AsyncFunctionDef`/`ClassDef` nodes (skip names starting with `_`, except
      `__init__`), collect `posonlyargs + args + kwonlyargs`, and drop `self`/`cls`.
      Gate: running it against a clone of `sdypy-view` in an environment with no Qt binding
      completes and reports, rather than raising `QtBindingsNotFoundError`.
- [x] 1.5 Implement the divergence rule: report a public parameter or attribute whose name is a
      key of the canonical table, naming the file, the function, the offending name and its
      canonical replacement. A name the table says nothing about is NOT a violation — this is
      what keeps the checker free of false positives (design D-risk 1).
- [x] 1.6 Implement the affix rules: a public parameter ending in `_ind` is a violation naming
      the `_idx` spelling; a public parameter named exactly `n` is a violation naming the
      `n_<plural>` convention.
- [x] 1.7 Implement the single-uppercase rule: a public parameter whose name is a single
      uppercase letter, or an all-uppercase abbreviation such as `EI`, is a violation — it
      breaches SEP 2's pre-existing snake_case rule for parameters as well as the table.
- [x] 1.8 Implement the criterion-function exception: `phi`, `phi_X`, `phi_A` are permitted as
      arguments of functions named exactly `MAC`, `MSF`, `MCF`, and are violations everywhere
      else. Assert both halves — a permissive check that never fires outside the exception is
      indistinguishable from no check.
- [x] 1.9 Gate: `python tools/check_nomenclature.py --path <clone of sdypy-model>` reports the
      known divergences (`K`, `M`, `EI`, `org`, `conec`, `frequency`, `n`, `nat_freq`) — the
      checker is proven to fail before any sibling is fixed.

## 2. Tests

- [x] 2.1 Add `tests/test_nomenclature.py`. Layer one: unit tests over synthetic fixtures written
      to `tmp_path` (following `tests/test_sep_governance.py`), covering each rule and each
      exception — canonical clone passes; `xi` reported; `_ind` reported; bare `n` reported;
      single uppercase reported; `MAC(phi_X, phi_A)` accepted; `foo(phi_X)` reported. These carry
      NO marker and run in core CI with no sibling installed.
- [x] 2.2 Add the mirror-drift test: every canonical name in the checker's table appears in
      `docs/seps/sep-0002.rst`. Direction matters — a checker enforcing a name SEP 2 never
      ratified must fail; a SEP 2 row the checker does not yet enforce must not.
- [x] 2.3 Layer two: conformance tests auditing the installed first-level packages, each marked
      `@pytest.mark.pypi_artifacts`, mirroring the parametrisation of `tests/test_public_api.py`.
- [x] 2.4 Gate: `pytest -m "not pypi_artifacts" tests/test_nomenclature.py` passes in an
      environment with no first-level package installed, and plain
      `pytest tests/test_nomenclature.py` selects the conformance layer.

## 3. CI wiring

- [x] 3.1 Add a `Check documentation conformance` step to `.github/workflows/docs.yml` running
      `python tools/check_docs.py --path .`, placed beside the existing `check_seps.py` step and
      before `build_index.py`.
- [x] 3.2 Do NOT add `check_public_api.py` or `check_sibling_template.py` to either workflow:
      both exit non-zero at the umbrella root by construction (`expected exactly one portion
      under .../sdypy, found: ['testing', 'core']`). Making them pass here would mean changing
      the umbrella's shipped package layout, which is out of scope.
- [x] 3.3 Verify the docs job still succeeds end to end: `check_seps.py`, `check_docs.py`,
      `build_index.py`, then the Sphinx build.

## 4. Correct the inaccurate claims

- [x] 4.1 `REQUIREMENTS.md` § Canonical sources: stop implying all four checkers run in this
      repo's CI. Record that `check_seps.py` and `check_docs.py` run in `docs.yml`, and that
      `check_public_api.py` and `check_sibling_template.py` audit a sibling clone. Add the
      `check_nomenclature.py` row.
- [x] 4.2 `REQUIREMENTS.md` § Legend: the `tools/check_*.py` bullet says "also run in CI" —
      qualify it to match 4.1.
- [x] 4.3 `AGENTS.md` § Common commands: change
      `python tools/check_public_api.py --path .` to a sibling-clone invocation
      (`--path ../sdypy-EMA`) and add `check_sibling_template.py` and `check_nomenclature.py`
      the same way, so every documented command succeeds in the directory it names.
- [x] 4.4 Add the new `public-api` and `testing-ci` rows to `REQUIREMENTS.md` for the
      requirements this change adds, attributing only what the checker actually decides.

## 5. Verify

- [x] 5.1 `openspec validate --strict` clean; `openspec archive enforce-sep2-nomenclature`.
- [x] 5.2 `pytest -m "not pypi_artifacts"` no worse than the pre-change baseline (Qt-binding
      caveat: `pip install PySide6-Essentials`, else `view`/`model` fail unrelatedly).
- [x] 5.3 Every invocation in `AGENTS.md` § Common commands is executed as written and reaches a
      verdict. This is the acceptance test for section 4 — the previous state failed it.
- [x] 5.4 Confirm the two deliberately excluded items are still untouched and still recorded as
      open: `sdypy/core` + `sdypy/testing`, and the stale `sibling-package-template` matrix
      (`CI_MATRIX = {"3.10", "3.11", "3.12"}` in `check_sibling_template.py` versus
      `testing-ci`'s `["3.12", "3.13", "3.14"]`).
