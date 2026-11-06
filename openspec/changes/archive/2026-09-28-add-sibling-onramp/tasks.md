## 1. Hub: the shared link block

- [ ] 1.1 Rebase this branch onto `main` once #11 (the marker-delimited shared rules block in `openspec/config.yaml`) has merged; verify `grep -c '# >>> shared rules from the sdypy hub' openspec/config.yaml` prints 1 — interim: this branch is stacked on #11's branch `openspec-config-context`; the marker check prints 1
- [x] 1.2 Add the link block to the hub's `AGENTS.md` between `<!-- >>> sdypy hub links -->` and `<!-- <<< sdypy hub links -->`: links only, absolute URLs to `sdypy/sdypy` on `main` — `AGENTS.md`, `docs/seps/`, `docs/source/dev/nomenclature.rst`, `openspec/specs/`, `REQUIREMENTS.md` (design.md Decision 2)

## 2. Template checker: on-ramp checks

- [x] 2.1 Add a helper that extracts a marker-delimited region (markers included, line endings normalised) and returns `None` when either marker is missing
- [x] 2.2 Check `AGENTS.md`: present, and its link block equals the hub's (*Agent instructions link to the hub's org-wide rules*)
- [x] 2.3 Check `CLAUDE.md`: present, and its content is exactly `@AGENTS.md` plus an optional trailing newline (*Claude Code reads AGENTS.md*)
- [x] 2.4 Check `openspec/config.yaml` for non-shim portions: present, and its shared rules block equals the hub's; skip for `FRF` and `excitation` (*OpenSpec configuration carries the hub's shared rules*)
- [x] 2.5 Read the hub's `AGENTS.md` and `openspec/config.yaml` relative to the checker file (`Path(__file__).resolve().parents[1]`), never relative to the working directory

## 3. Template checker: Python set and install step

- [x] 3.1 Replace `CI_MATRIX` with a single `SUPPORTED_PYTHON = {"3.12", "3.13", "3.14"}` and a comment naming SPEC 0 and the human who keeps it current; derive the `requires-python` floor from its minimum
- [x] 3.2 Accept `pip install .[<extras>]`, quoted or not, in the test workflow; keep rejecting any step that reads `requirements*.txt`
- [x] 3.3 Update the module docstring to list the new checks
- [x] 3.4 Verify no other hub file declares the sibling Python set: `grep -rn '3\.10' tools tests openspec/specs` returns only unrelated hits — the only remaining hits are in `openspec/specs/sibling-package-template/spec.md`, which the delta replaces at archive

## 4. Nomenclature checker: deprecated aliases

- [x] 4.1 Collect, per function, the parameters guarded by an `if` whose test names them and whose body calls `warnings.warn` with `DeprecationWarning` (positional or `category=`)
- [x] 4.2 Treat a function as deprecated when its body's top level calls `warnings.warn` with `DeprecationWarning` unconditionally, or it is decorated `@deprecated`; exempt all its parameters
- [x] 4.3 Skip exempt parameters in `check_function`; attributes are unaffected
- [x] 4.4 Verify `python tools/check_nomenclature.py --path ../sdypy-EMA` drops from 23 to 20 findings, the three removed being `Model.__init__` `frf_type`, `get_constants` `FRF_ind` and `FRF_reconstruct` `FRF_ind`

## 5. Tests

- [x] 5.1 Create `tests/test_sibling_template.py` with a minimal conforming sibling fixture built in `tmp_path` (only the files the new checks read), and one test per new or changed scenario: missing/edited `AGENTS.md` block, missing/extended `CLAUDE.md`, drifted/missing shared rules, shim without `openspec/`, `pip install ".[dev]"` accepted, `requirements.txt` rejected, matrix not covering the supported set, wrong `requires-python` floor
- [x] 5.2 Add to `tests/test_nomenclature.py` one test per ADDED scenario of *Deprecated aliases are not reported as divergences*, including the `UserWarning` and unguarded cases that must still be reported
- [x] 5.3 Confirm each new test fails against the checker as it was before this change (run it against `main`'s checker), so the tests exercise the new behaviour
- [x] 5.4 Run `pytest -m "not pypi_artifacts"` and `openspec validate --all --strict`; both pass

## 6. Verify against real siblings

- [x] 6.1 Run the template checker against `../sdypy-EMA` and record the result in the PR: expected violations are the new on-ramp files, the Python set, and the `readthedocs.yaml` extra — and no longer `pip install ".[dev]"`
- [x] 6.2 Run both changed checkers against every sibling clone present locally and confirm no crash (a missing `openspec/` or `AGENTS.md` is a reported violation, not an exception)

## 7. Review and archive

- [x] 7.1 Commit the change artifacts first, the implementation after, and open one PR on `ladisk/sdypy`
- [x] 7.2 After review converges: `openspec archive add-sibling-onramp`, with the `REQUIREMENTS.md` rows for the new requirements in the same commit — the SPEC 0 set as `manual` (hub maintainer, at each SPEC 0 quarterly drop), the rest as `check_sibling_template.py` / `check_nomenclature.py` with their tests
