# AGENTS.md — SDyPy contributor & agent guide

Guidance for anyone (human or AI) developing the **SDyPy core umbrella**. It is
tool-agnostic on purpose: Claude Code reads it via a one-line `CLAUDE.md`
(`@AGENTS.md`); other tools can point their own rule-files here too.

This file is a **router, not a rulebook** — it orients you and links the
authoritative sources. When guidance and a linked source disagree, the linked
source wins. Keep this file thin; do not restate the specs or SEPs here.

## What this package is

`sdypy` is the **umbrella distribution** for Structural Dynamics Python. It ships
the *only* `sdypy/__init__.py` — a lightweight, lazy PEP 562 facade over six
independently developed first-level sub-packages (`EMA`, `io`, `FRF`,
`excitation`, `model`, `view`), which are native PEP 420 namespace portions
published as separate distributions. It also surfaces the SEP 5 timeseries
standard as the alias `sd.sep005`. The umbrella holds **no science code** — only
the facade, packaging, docs, tests, and governance. See
`docs/seps/sep-0003.rst` (namespace) and `README.rst`.

## Repository map

| Path | What lives there |
|---|---|
| `sdypy/__init__.py` | The umbrella lazy facade (the only real source) |
| `REQUIREMENTS.md` | Single-source roster: every requirement → its verifying test/checker |
| `openspec/specs/` | Canonical capability specs (7) — the normative contracts |
| `openspec/changes/` | In-flight OpenSpec changes; `archive/` holds completed ones |
| `docs/seps/` | SEP governance docs (SEP 1 levels, 2 API, 3 namespace, 5 sep005) |
| `tools/check_*.py` | Executable conformance checkers (public-api, docs, template) |
| `tests/` | Functional, interop, and conformance test suites |
| `.github/workflows/` | CI: `python-package.yml`, `docs.yml`, `release-and-publish-to-pypi.yml` |

## Development environment

- **Python ≥ 3.12** (tested 3.12–3.14). Use **`uv`** for envs and installs
  (`uv venv`, `uv pip install -e ".[dev]"`), not plain `pip`/`conda`.
- Build backend is **hatchling**; there is no `setup.py`.

## Common commands

```console
uv pip install -e ".[dev]"            # dev install (docs + test + build tools)
pytest -m "not pypi_artifacts"        # the CI test set (skips the PyPI gate)
pytest                                # full local run incl. pypi_artifacts gate
python tools/check_public_api.py --path .   # public-api conformance
python tools/check_docs.py --path .         # documentation conformance
python -m build                       # build sdist + wheel
sphinx-build -b html docs/source docs/_build/html   # build docs
```

`pypi_artifacts`-marked tests assert against *published* PyPI wheels; they are
the local pre-release gate and are deselected on GitHub CI.

## Required workflow: OpenSpec (spec-driven)

Non-trivial changes are **spec-first**. Do not edit behaviour and back-fill a
spec — propose the change, get the delta specs right, then implement.

1. **Propose** a change under `openspec/changes/<name>/` (`proposal.md`,
   `tasks.md`, and delta specs under `specs/<capability>/spec.md`).
2. **Validate**: `openspec validate <name> --strict` (every change needs at
   least one delta with a `#### Scenario:` block).
3. **Implement** the tasks; keep `tasks.md` checkboxes current.
4. **Archive**: `openspec archive <name>` folds the delta into
   `openspec/specs/` and moves the change to `archive/`.

The OpenSpec skills/commands live in `.claude/` (`opsx:*` / `openspec-*`). If
`openspec/` or those commands are missing, run `openspec init` / `openspec
update` first. Operational or governance work with **no honest spec delta**
(e.g. PyPI releases, flipping a SEP's status) does **not** belong in OpenSpec —
track it in `REQUIREMENTS.md` § Pending instead.

## Conventions & virtues

- **Single source of truth, no duplication.** Every fact has one home; other
  files link to it. `REQUIREMENTS.md` indexes the specs; this file routes to
  both — none of them copy each other.
- **Lean on the SciPy stack**; don't reimplement general numerics.
- **MIT-licensed**, open development, multi-institutional. All contributions MIT.
- **SEP governance** decides cross-cutting design (`docs/seps/`, per SEP 0/1).
- **Public API is explicit** — every first-level package curates `__all__`
  (SEP 2). The umbrella exposes exactly the six sub-package names plus `sep005`.
- **NumPy-style docstrings** unless a file clearly uses another style.
- Dev-only files (`openspec/`, `.claude/`, `REQUIREMENTS.md`, this file) are
  **not** shipped in the sdist — the `[tool.hatch.build.targets.sdist]`
  allow-list in `pyproject.toml` is explicit; keep it that way.

## Authoritative sources (read these, don't guess)

- Requirements & their verification → `REQUIREMENTS.md`
- Normative contracts → `openspec/specs/<capability>/spec.md`
- Governance & design rationale → `docs/seps/sep-000*.rst`
- Contribution process, style, CoC → `CONTRIBUTING.rst`, `docs/source/dev/`
