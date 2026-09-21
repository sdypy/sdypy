## Why

SEP 0 is the only SEP with `:Status: Active` — it is the ratified process document that governs every other SEP — yet nothing measures it: it has no capability spec, zero rows in `REQUIREMENTS.md`, and no checker. The only normative mention of `sep-0000` anywhere in `openspec/specs/` is a footnote-residue scenario in the `documentation` capability. The result is metadata drift that is already in the tree: `sep-0005.rst` declares `:Type: Standards`, which is in neither the template's `Standards Track | Process` nor SEP 0's three documented kinds; `sep-0000.rst` declares `:Created: 2-Nov-2020` where `sep-template.rst` mandates `yyyy-mm-dd`; the author field is spelled `:Author:` in SEP 0 and the template but `:Authors:` in SEPs 1–5; and `Provisional` is rendered by `index.rst.tmpl` and tracked by `build_index.py` while being absent from the template's status vocabulary.

The failure mode is silent, not loud. `index.rst.tmpl` selects SEPs by exact string equality on `Status`, so a mis-cased or unknown status (`draft`, `In progress`) drops that SEP out of *every* toctree section: it disappears from the published index with no warning and no error. `build_index.py` validates only the title format, the `Resolution`-for-Accepted rule, and the Superseded/Replaces graph; author, status vocabulary, type vocabulary and date format are never checked. This is also badly timed: `REQUIREMENTS.md` § Pending B queues the Draft → Accepted flips for SEP 2, 3 and 5, and `:Resolution:` is required for Accepted — today the only thing standing between that governance act and a red docs build is a `RuntimeError` raised inside a documentation generator, with no way to check it locally before pushing.

## What Changes

- **Add a `sep-governance` capability**: the mechanically checkable subset of SEP 0 — the header preamble contract every `docs/seps/sep-<nnnn>.rst` must satisfy. The human parts of SEP 0 (champion, consensus-building, mailing-list discussion) are explicitly **not** requirements and stay as SEP 0 prose.
- **Add `tools/check_seps.py`**, a standalone conformance checker following the existing `check_public_api.py` / `check_docs.py` / `check_sibling_template.py` pattern (`--path`, exit 0/1, one line per violation), plus a thin `tests/test_sep_governance.py` so a plain `pytest` run catches the same violations.
- **Fix the four evidenced drifts**: `sep-0005.rst` `:Type: Standards` → `Standards Track`; `sep-0000.rst` `:Created: 2-Nov-2020` → `2020-11-02` and `:Author:` → `:Authors:`; `sep-template.rst` gains `Informational` in the `Type` vocabulary, `Provisional` in the `Status` vocabulary, and `:Authors:` as the canonical spelling.
- **Run the checker in CI** in the `docs.yml` job, *before* `build_index.py`, so a metadata error is reported as a named violation rather than as a generator traceback.
- **Canonical spelling decision**: `:Authors:` wins over `:Author:` (5 of 6 SEPs already use it; it reads correctly for the multi-author norm). This is a one-line flip in the checker if the team prefers the template's `:Author:` — see Impact.
- **No change to `build_index.py`**: its existing `RuntimeError`s are generator preconditions and stay as defence in depth. The checker is the conformance authority and covers a superset.

## Capabilities

### New Capabilities
- `sep-governance`: the contract for SEP document metadata — the required header fields, the closed `Status` and `Type` vocabularies, the ISO 8601 `Created` format, the conditional `Resolution` field, and the requirement that all of it is enforced by a standalone checker in CI.

### Modified Capabilities

<!-- none. `documentation` owns SEP *rendering* ("Unified SEP rendering via build_index.py": the generator is the single source of truth for the index, covers all SEPs, runs in the RTD build). `sep-governance` owns SEP *metadata*. The silent-drop failure in the Why is the motivation linking them, but it is not restated as a requirement here — index completeness has one home, and it is already `documentation`. The `documentation` "No foreign-project residue" scenario about sep-0000 footnotes concerns prose content, not header fields, so it is untouched. -->

## Impact

- **Core repo only**: new `tools/check_seps.py`, `tests/test_sep_governance.py`; edits to `docs/seps/sep-0000.rst` (2 header lines), `docs/seps/sep-0005.rst` (1 header line), `docs/seps/sep-template.rst` (3 vocabulary lines), `.github/workflows/docs.yml` (one checker step); new `sep-governance` section in `REQUIREMENTS.md` (added at archive time, per the index-not-source rule).
- **Users**: none. No shipped code, no API surface, no packaging change. `openspec/`, `tools/` and `tests/` are already excluded from the sdist allow-list.
- **Contributors**: a SEP with a malformed header now fails CI instead of silently vanishing from the index. Authoring a new SEP from `sep-template.rst` unchanged still passes.
- **Unchanged / out of scope**: SEP prose and technical content; `build_index.py` behaviour (`documentation` capability); the sibling repos (they hold no SEPs); the Draft → Accepted flips for SEP 2/3/5 (governance, `REQUIREMENTS.md` § Pending B — this change makes those flips *checkable*, it does not perform them); SEP 1's four-level integration scale, whose requirements overlap the existing `public-api` / `namespace-packaging` / `sibling-package-template` capabilities and are a separate change once SEP 1 leaves Draft.
- **Deferred to maintainer**: the `:Authors:` vs `:Author:` decision above, if the team wants the template's spelling instead.
