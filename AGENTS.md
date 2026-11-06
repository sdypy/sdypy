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
| `openspec/specs/` | Canonical capability specs (8) — the normative contracts |
| `openspec/changes/` | In-flight OpenSpec changes; `archive/` holds completed ones |
| `docs/seps/` | SEP governance docs (SEP 1 levels, 2 API, 3 namespace, 5 sep005) |
| `tools/check_*.py` | Executable conformance checkers (docs, seps, public-api, nomenclature, template) |
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
python tools/check_docs.py --path .         # documentation conformance (umbrella)
python tools/check_seps.py --path .         # SEP metadata conformance (umbrella)
python -m build                       # build sdist + wheel
python docs/seps/tools/build_index.py                # generate the SEP index (before the docs build)
sphinx-build -b html docs/source docs/_build/html   # build docs
```

Three checkers audit a **sibling clone**, not this repo — each resolves exactly
one portion under `sdypy/`, and the umbrella provides none. Run them with a
sibling path:

```console
python tools/check_public_api.py --path ../sdypy-EMA        # curated __all__
python tools/check_nomenclature.py --path ../sdypy-EMA      # SEP 2 canonical names
python tools/check_sibling_template.py --path ../sdypy-EMA  # packaging template
```

`pypi_artifacts`-marked tests assert against *published* PyPI wheels; they are
the local pre-release gate and are deselected on GitHub CI.

## Required workflow: OpenSpec (spec-driven)

Non-trivial changes are **spec-first**: if you write one, do not edit behaviour
and back-fill a spec — propose the change, get the delta specs right, then
implement. A PR that arrives with code but no spec is not rejected: the
maintainer writes the spec before merge, and review checks it as the contract,
not as a description of whatever the code does.

1. **Propose** a change under `openspec/changes/<name>/` (`proposal.md`,
   `tasks.md`, and delta specs under `specs/<capability>/spec.md`).
2. **Validate**: `openspec validate <name> --strict` (every change needs at
   least one delta with a `#### Scenario:` block).
3. **Implement** the tasks; keep `tasks.md` checkboxes current.
4. **Open one PR** on a branch here, carrying the artifacts and the
   implementation.
5. **Review** the delta there — the human audit of the contract, with the
   artifacts in the first commit so they read apart from the code.
6. **Archive**: `openspec archive <name>` as the final commit once review
   converges, carrying the `REQUIREMENTS.md` roster update with it.
7. **Merge.**

A change is **trivial** when it adds, changes or removes no spec requirement and
no public name, however it was written: documentation, typos, version bumps,
test-only changes, bug fixes. It skips OpenSpec and is just steps 4, 5 and 7.
Not trivial: editing a SEP or a spec, or a test change that removes or weakens
a verifier listed in `REQUIREMENTS.md`.

A change spanning repositories puts its spec where the contract lives (the hub,
for org-wide contracts) and its tasks where the code lives (each sibling's own
OpenSpec change).

The OpenSpec skills/commands live in `.claude/` (`opsx:*` / `openspec-*`). If
`openspec/` or those commands are missing, run `openspec init` / `openspec
update` first. Operational or governance work with **no honest spec delta**
(e.g. PyPI releases, flipping a SEP's status) does **not** belong in OpenSpec —
track it in `REQUIREMENTS.md` § Pending instead.

## Definition of done

A change is ready for review when these checks have *run* and passed —
"should pass" is not done:

- CI is green on the PR.
- Non-trivial: `openspec validate <name> --strict` is clean, every box in
  `tasks.md` is ticked, and each new requirement has a test, a checker or a
  named human judge (its `REQUIREMENTS.md` row lands with the archive, step 6).
- A sibling's public names changed: the three sibling checkers above pass
  against that sibling.

## Conventions & virtues

- **Single source of truth, no duplication.** Every fact has one home; other
  files link to it. `REQUIREMENTS.md` indexes the specs; this file routes to
  both — none of them copy each other.
- **Lean on the SciPy stack**; don't reimplement general numerics.
- **MIT-licensed**, open development, multi-institutional. All contributions MIT.
- **SEP governance** decides cross-cutting design (`docs/seps/`, per SEP 0/1).
- **Public API is explicit** — every first-level package curates `__all__`
  (SEP 2). The umbrella exposes exactly the six sub-package names plus `sep005`.
- **Changes land through PRs.** Review weight scales with the change: a typo
  merges once CI is green, a contract change gets a real look. For a
  non-trivial change the human approval covers the contract: the spec delta,
  its tests and the public names. Correctness of the code rests on CI and on
  the person accountable for the PR; reading it line by line is the reviewer's
  call.
- **AI-assisted contributions are welcome**, including PRs an agent opens on
  its own. The PR description says which tool and model were used and for
  what. Before merge, a named person (the author or the merging maintainer) is
  accountable for the PR and must be able to explain and defend its code.
- **NumPy-style docstrings** unless a file clearly uses another style.
- Dev-only files (`openspec/`, `.claude/`, `REQUIREMENTS.md`, this file) are
  **not** shipped in the sdist — the `[tool.hatch.build.targets.sdist]`
  allow-list in `pyproject.toml` is explicit; keep it that way.

## For sibling repositories

Every first-level sibling copies the block below into its own `AGENTS.md`
verbatim (*Agent instructions link to the hub's org-wide rules*,
`sibling-package-template` spec); the hub's copy here is the block's only
home, so edit it only in this file.

<!-- >>> sdypy hub links -->
- [AGENTS.md](https://github.com/sdypy/sdypy/blob/main/AGENTS.md) — workflow and definition of done
- [docs/seps/](https://github.com/sdypy/sdypy/tree/main/docs/seps/) — SEP governance docs
- [docs/source/dev/nomenclature.rst](https://github.com/sdypy/sdypy/blob/main/docs/source/dev/nomenclature.rst) — naming a new public term (SEP 2)
- [openspec/specs/](https://github.com/sdypy/sdypy/tree/main/openspec/specs/) — canonical capability specs
- [REQUIREMENTS.md](https://github.com/sdypy/sdypy/blob/main/REQUIREMENTS.md) — requirements roster
<!-- <<< sdypy hub links -->

## Authoritative sources (read these, don't guess)

- Requirements & their verification → `REQUIREMENTS.md`
- Normative contracts → `openspec/specs/<capability>/spec.md`
- Governance & design rationale → `docs/seps/sep-000*.rst`
- Contribution process, style, CoC → `CONTRIBUTING.rst`, `docs/source/dev/`
- Naming a new public term → `docs/source/dev/nomenclature.rst` (SEP 2 states
  the rule; that page carries the procedure and the checker's limits)
