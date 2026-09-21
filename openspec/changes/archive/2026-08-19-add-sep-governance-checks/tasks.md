## 1. Conformance checker

- [x] 1.1 Add `tools/check_seps.py`, stdlib-only (no docutils, no jinja2 — it must also run
      under `python-package.yml`, which installs neither). CLI mirrors the existing checkers:
      `--path` (default `.`), one violation per line as `<file>: <rule>: <detail>`, exit `0`
      when clean and `1` otherwise. Discover `docs/seps/sep-[0-9][0-9][0-9][0-9].rst`;
      exclude `sep-template.rst` from the per-SEP field checks.
- [x] 1.2 Implement preamble parsing: extend `build_index.py`'s `:([a-zA-Z\-]*): (.*)` with
      indented-continuation handling, so `sep-0004.rst`'s three-line `:Authors:` is read in
      full. Expose the parser as a function the test module can import.
- [x] 1.3 Implement the field rules (spec: *Every SEP declares the required header fields*):
      `:Authors:`, `:Status:`, `:Type:`, `:Created:` all present; `:Author:` reported as the
      deprecated spelling; `:Resolution:` required and non-empty when `:Status:` is
      `Accepted`, `Rejected` or `Withdrawn`.
- [x] 1.4 Implement the vocabulary rules (spec: *Status* / *Type* requirements), case-sensitive:
      `Status` ∈ {Draft, Active, Provisional, Accepted, Final, Deferred, Superseded, Rejected,
      Withdrawn} — derived from the toctree sections of `index.rst.tmpl` (D4);
      `Type` ∈ {Standards Track, Informational, Process} — SEP 0 § Types (D5).
      On violation, print the offending value **and** the permitted set.
- [x] 1.5 Implement the date rule: `:Created:` parses as `yyyy-mm-dd` (`datetime.date.fromisoformat`).
- [x] 1.6 Implement the template checks: `sep-template.rst` declares all nine `Status` values
      (incl. `Provisional`), all three `Type` values, and `:Authors:` as the field name.
- [x] 1.7 Gate: `python tools/check_seps.py --path .` runs and reports exactly the four known
      drifts (sep-0005 Type, sep-0000 Created, sep-0000 Author, template vocabularies) —
      i.e. the checker is proven to fail *before* section 2 fixes them.

## 2. Fix the evidenced drifts

- [x] 2.1 `docs/seps/sep-0005.rst`: `:Type: Standards` → `:Type: Standards Track`. Header only —
      do NOT touch `:Status: Draft` (the flip to Accepted is team-gated, § Pending B).
- [x] 2.2 `docs/seps/sep-0000.rst`: `:Created: 2-Nov-2020` → `:Created: 2020-11-02`;
      `:Author:` → `:Authors:`. No prose changes.
- [x] 2.3 `docs/seps/sep-template.rst`: `:Author:` → `:Authors:`; add `Provisional` to the
      `:Status:` placeholder (nine values); add `Informational` to the `:Type:` placeholder
      (three values). Leave the `:Resolution:` line's existing wording unchanged.
- [x] 2.4 Gate: `python tools/check_seps.py --path .` now exits `0` with no output.

## 3. Tests

- [x] 3.1 Add `tests/test_sep_governance.py` importing the checker's functions (two-layer
      conformance, D3): `test_all_seps_conform` asserts the checker reports no violations on
      the repository, failing with the violation list in the assertion message.
- [x] 3.2 Add unit tests over the parser and rules using `tmp_path` fixtures, one per rule:
      missing field, `:Author:` spelling, `Accepted` without `:Resolution:`, unknown status,
      mis-cased status (`draft`), out-of-vocabulary type (`Standards`), non-ISO date
      (`2-Nov-2020`), multi-line `:Authors:` read in full.
- [x] 3.3 Add `test_template_declares_vocabularies` covering task 1.6.
- [x] 3.4 No `pypi_artifacts` marker anywhere in this file — nothing here depends on a
      published wheel; it must run on every CI push.
- [x] 3.5 Gate: `pytest tests/test_sep_governance.py -q` green; then
      `pytest -m "not pypi_artifacts"` green (no regression in the existing suite).

## 4. CI wiring

- [x] 4.1 In `.github/workflows/docs.yml`, add a `Check SEP metadata` step running
      `python tools/check_seps.py --path .` from the repo root, placed **before** the
      `Generate SEP index` step (D7).
- [x] 4.2 Confirm `build_index.py` is left byte-identical — its three `RuntimeError`s stay as
      generator preconditions, not as the gate.
- [x] 4.3 Gate: run the docs job's sequence locally — `python tools/check_seps.py --path .`,
      then `python tools/build_index.py` from `docs/seps`, then
      `python -m sphinx -b html docs/source docs/_build/html` — all three succeed.

## 5. Verification and archive

- [x] 5.1 Run `python tools/check_docs.py --path .` and `python tools/check_public_api.py --path .`
      — both still exit `0` (the SEP header edits must not trip the docs residue allowlist).
- [x] 5.2 Run `openspec validate add-sep-governance-checks --strict` and confirm no errors
      (5 requirements, each with at least one `#### Scenario:`).
- [x] 5.3 Run `openspec archive add-sep-governance-checks` — the delta folds into
      `openspec/specs/sep-governance/spec.md` and the change moves to `archive/`.
- [x] 5.4 Add a `### sep-governance` section to `REQUIREMENTS.md` *after* the archive (the file
      is a derived index, not a source): five rows mapping each requirement to
      `pytest::test_all_seps_conform` / the per-rule unit tests and `tools/check_seps.py`.
      Add `tools/check_seps.py` to the § Canonical sources table.
- [x] 5.5 Cross-check § Pending B: note there that the SEP 2/3/5 `Draft → Accepted` flips are
      now gated by `check_seps.py` (a flip without `:Resolution:` fails CI). Do NOT perform
      the flips — they remain team-gated.
