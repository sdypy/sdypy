## 1. Confirm the drift before correcting it

- [x] 1.1 Record the evidence that the tree implements the seven-name surface, so the
      correction is demonstrably spec-side only: `python -c "import sdypy; print(sorted(sdypy.__all__))"`
      prints the six sub-package names plus `sep005`, and
      `pytest tests/test_public_api.py::test_umbrella_all_is_the_six_subpackages_plus_sep005 -q`
      passes against the current tree. (Requires an environment with a Qt binding installed —
      `pip install PySide6-Essentials` — otherwise the `view`/`model` imports raise
      `qtpy.QtBindingsNotFoundError` for reasons unrelated to this change.)
- [x] 1.2 Confirm the contradiction is confined to the one requirement:
      `grep -n "six first-level names" openspec/specs/public-api/spec.md` reports only the
      requirement header, its body, its first scenario, and the `**Scope:**` preamble line —
      and `grep -n "sep005" openspec/specs/public-api/spec.md` shows the `## Purpose` line
      already naming the alias.

## 2. Apply the spec correction

- [x] 2.1 Archive the delta (`openspec archive align-umbrella-public-surface`) so the rename and
      the corrected requirement body land in `openspec/specs/public-api/spec.md`. Verify the
      resulting main spec has exactly one `### Requirement:` header mentioning `sep005`, that
      the three scenario names are unchanged, and that the other six requirements of the
      capability are byte-identical to before.
- [x] 2.2 Hand-edit the `**Scope:**` preamble line of `openspec/specs/public-api/spec.md`: it
      names the requirement by its old title (`except the *Umbrella `__all__` matches the six
      first-level names* requirement, which is umbrella-local`). Update the quoted title to the
      new one. The scope classification itself — umbrella-local — is unchanged and must stay.
      This line is spec preamble, not a requirement, so the delta mechanism cannot carry it.
- [x] 2.3 Re-read the `## Purpose` line of the same file and confirm it needs no edit: it already
      reads "the umbrella exposing exactly the six first-level names plus the `sep005` alias".

## 3. Prove nothing else moved

- [x] 3.1 `openspec validate --strict` on all changes and `openspec list` show a clean tree.
- [x] 3.2 `git diff --stat` for the whole change touches only `openspec/`. If any path under
      `sdypy/`, `tests/`, `tools/`, `docs/` or `.github/` appears, the change has overstepped
      its scope — revert that file.
- [x] 3.3 `pytest -m "not pypi_artifacts"` is no worse than the pre-change baseline (see task 1.1
      for the Qt-binding caveat), and `REQUIREMENTS.md` needs no row edit — confirm the
      `public-api` row still reads "Umbrella `__all__` = the six names (+ `sep005` alias)".
- [x] 3.4 `grep -rn "matches the six first-level names" --include=*.md --include=*.rst .` returns
      nothing outside `openspec/changes/archive/`, proving no stale reference to the old
      requirement title survives.
