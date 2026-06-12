## Context

Changes #1 and #2 established the core repo's packaging contract (`namespace-packaging`, `distribution-packaging` specs). The six first-level sibling packages predate that work and were audited 2026-06-12 (local clones under `packages/`). Summary of the audit:

| Dimension | EMA | io | FRF | excitation | view | model |
|---|---|---|---|---|---|---|
| Build definition | pyproject **+ setup.py** | pyproject **+ setup.py** | pyproject only | pyproject only | pyproject only | pyproject only |
| Version pyproject / `__init__` | 0.29.1 / 0.29.1 | 0.3.1 / 0.3.1 | 0.1.0 / 0.1.0 | **0.1.1 / 0.1.0 (mismatch)** | 0.1.7 / 0.1.7 | 0.1.5 / 0.1.5 |
| `sync_version.py` | yes | **no (release workflow broken)** | no | no | yes | yes |
| `requirements*.txt` | yes | yes | yes | yes | yes | yes |
| `.travis.yml` | yes (stale) | yes (stale) | no | no | no | no |
| CI matrix | 3.10–3.12 | 3.10–3.12 | 3.10–3.12 | 3.10–3.12 | **3.12 only** | **3.12 only** |
| Test workflow file | python-package.yml | python-package.yml | python-package.yml | python-package.yml | pytest.yaml | pytest.yaml |
| Actions versions | checkout@v3 / setup-python@v4 (all six; deprecated Node runtime, forced migration 2026-06-16) | | | | | |
| `readthedocs.yaml` | yes | yes | **no** | **no** | **no** | yes |
| Docs URL | own | own | **pyFRF's** | **pyExSi's** | GitHub | own |
| README | .rst | .rst | .rst | .rst | .rst | **.md** |
| Classifiers | 5 | 5 | 5 | 5 | 4 | 4 |

Shared baseline (good news): all six already use hatchling, `requires-python >= 3.10`, MIT, and are PEP 420 native portions in their working clones (no `sdypy/__init__.py` — change #1 outcome; PyPI re-releases of model/view still pending).

Constraints: six independent repos, no shared CI infrastructure; sdypy-view and sdypy-model clones track ladisk forks, the other four track the sdypy org; OpenSpec tooling exists only in the core repo; sibling release publishing is done by the maintainer via tag push.

## Goals / Non-Goals

**Goals:**
- One written, normative packaging template for first-level sdypy packages — also the on-ramp for future SEP 4 sub-packages.
- All six siblings conformant: pyproject-only, version single-sourced, standardized CI/release workflows, consistent metadata, clean distributions.
- Conformance is checkable mechanically, so drift gets caught instead of re-audited.
- Fix the two live defects en route: sdypy-excitation version mismatch, sdypy-io release workflow missing version sync (mooted by removing sync entirely).

**Non-Goals:**
- Real test suites for placeholder packages (change #5 — the template only requires that a `tests/` suite exists and CI runs it).
- Public-API/nomenclature alignment (change #4), docs content and theming (change #6).
- Git default-branch renaming (`main` vs `master` divergence noted; cosmetic, deferred).
- Registering Read the Docs projects for packages that lack them (external/manual; template only requires a valid `readthedocs.yaml`).
- Changing upstream-PR/fork workflow for view/model.

## Decisions

### D1: The template contract lives in the core repo as an OpenSpec capability spec

`openspec/specs/sibling-package-template/spec.md` in the core repo (this change's delta spec, promoted on sync).

- **Why core, not per-repo specs:** six copies of a contract re-diverge — the exact failure mode this change cures. The core repo is the program home (SEPs, existing `namespace-packaging` spec already governs sibling behavior from core), and the siblings carry no OpenSpec tooling.
- **Why not a separate template/cookiecutter repo:** a seventh repo to maintain, and scaffolding-from-template is a future need (new SEP 4 sub-packages), not the current one (standardizing six existing repos). A cookiecutter can later be generated *from* the spec; the spec is the source of truth either way.
- Sibling repos get no spec copy. Their conformance is enforced by checking (D2), not by documentation they could let rot.

### D2: Two-layer conformance checking

1. **Distribution layer (automatic, core CI):** extend the existing core conformance test pattern (`tests/test_namespace_conformance.py`, which already inspects sibling PyPI artifacts for the forbidden `sdypy/__init__.py`) with template checks that are verifiable from published artifacts: no `setup.py`/`requirements*.txt` in sdists, wheel contains only the package's namespace portion, version metadata present. Runs on every core CI run; catches drift in what actually ships.
2. **Repo layer (dev-time, core-side script):** a checker script in the core repo (`tools/check_sibling_template.py`) that audits a sibling working clone by path — root-file hygiene, pyproject shape (backend, requires-python, classifiers-vs-CI-matrix, URLs), workflow files and their matrices, `__init__.py` version derivation. Run locally against `packages/*` during this change and any time drift is suspected; it is the mechanical replacement for the manual audit that opened this change.

- **Why not a conformance step in each sibling's CI:** it needs the checker in all six repos — either six diverging copies or a fetch-from-core coupling that makes sibling CI depend on core repo availability/layout. Revisit in change #5 (CI baseline), where a shared reusable workflow (`workflow_call`) could host it properly.
- **Why not GitHub-API auditing of the six repos from core CI:** rate limits, token plumbing, and it tests the repo tip rather than what users install. The distribution layer already covers the user-facing surface automatically.

### D3: Version single-sourcing — pyproject literal is authoritative; `__init__` derives from installed metadata

Same pattern as core (change #1/#2): `version = "X.Y.Z"` literal in `[project]`; `sdypy/<pkg>/__init__.py` does `__version__ = importlib.metadata.version("sdypy-<pkg>")` with `PackageNotFoundError` → `"0+unknown"` fallback. `sync_version.py` and the release-workflow sync step are deleted.

- **Alternative considered — hatch dynamic version** (`dynamic = ["version"]`, `[tool.hatch.version] path = "sdypy/<pkg>/__init__.py"`): also single-source, keeps a literal in code (nicer for source checkouts). Rejected for consistency: core already standardized on pyproject-authoritative + metadata derivation, and one program-wide pattern beats two equally-good ones. The source-checkout fallback trade-off was already accepted for core.
- Fixes sdypy-excitation's live mismatch structurally (there is nothing left to mismatch) and moots sdypy-io's broken release sync.

### D4: Canonical CI — one test workflow, one release workflow

- **Test workflow** `python-package.yml` (majority name; view/model's `pytest.yaml` renamed): trigger on push + PR; ubuntu-latest; Python `[3.10, 3.11, 3.12]` matrix (view/model widened from 3.12-only); steps = checkout → setup-python → `pip install .` → `pip install pytest flake8` → flake8 → pytest → `python -m build` (build validation, so a broken sdist/wheel fails CI rather than the next release). Action versions: current majors at implementation time (≥ checkout@v4, setup-python@v5) — clearing the Node 20 deprecation before GitHub's 2026-06-16 forced migration.
- **Release workflow** `release-and-publish-to-pypi.yml` (majority name; view/model's underscore variant renamed): trigger on `v*` tag push; single Python (3.11); build sdist+wheel; publish to PyPI; **no version-sync step**. Auth stays token-based as today (trusted publishing is an open question, Q1).
- **Why `pip install .` + explicit test tools rather than `.[dev]`:** the dev extra carries docs/release tooling (sphinx, twine) irrelevant to the test job; mirrors core's CI install contract from change #2.

### D5: Metadata template

- Backend hatchling, `requires-python = ">=3.10"`, MIT license declaration, explicit `[tool.hatch.build.targets.wheel]` packages list and an sdist allow-list (core's change #2 pattern: source, tests, docs source, README, LICENSE, pyproject; never `_build/`, junk, or deleted artifacts). Large binary test data (EMA's ~11 MB `data/`) stays out of both wheel and sdist — repo-only; tests needing it run from a checkout.
- Classifiers: `Programming Language :: Python :: 3.10/3.11/3.12` MUST match the CI matrix (spec'd); Intended Audience/Topic/License entries from the template. **Development Status is per-package judgment, not templated**: EMA (0.29.1, mature, real test suite) keeps `5 - Production/Stable`; the 0.x packages get `4 - Beta`, matching the core decision from change #2. Flagged team-reviewable (Q2).
- `[project.urls]` Homepage/Source MUST point at the package's *own* repository. The Documentation entry MAY point at the backend library's docs (pyFRF/pyExSi) for thin wrappers without hosted docs of their own — resolved Q3: the wrapper is thin and the backend docs are the real content; per-package RTD hosting is a change #6 question.
- Extras: `dev` and `docs`, following the core pattern (docs tooling in `docs`, dev references it).

### D6: Scaffolding normalized where it's packaging, advisory where it's authoring

Required by template: correctly-declared README (`readme` field matches the actual file), `LICENSE` file present, `readthedocs.yaml` present and valid (pip install with `docs` extra), `.gitignore` covering build output. **Not required:** README format (model keeps `.md`; the other five keep `.rst`) and Sphinx theme (model keeps book-theme for now) — those are authoring/docs concerns that change #6 will unify if the team wants; forcing conversions here is churn outside the packaging mandate.

### D7: Release sequencing

Each sibling gets a patch bump so the standardized packaging ships: EMA → 0.29.2, io → 0.3.2, FRF → 0.1.1, excitation → 0.1.2 (resolving the mismatch upward past the ambiguous 0.1.1), view → 0.1.8, model → 0.1.6 — **unless** the still-pending change #1 re-releases (model 0.1.5, view 0.1.7) have not shipped by implementation time, in which case those two ship once with both fixes at their current pyproject version. Publishing remains a maintainer action (tag push), outside this change's tasks proper; the change is implementation-complete when all six repos pass conformance locally and are pushed.

## Risks / Trade-offs

- [Rewritten release workflows are untested until the next tag push] → the test workflow's `python -m build` step validates the build half on every push; the publish step reuses each repo's existing, known-working PyPI auth mechanism unchanged.
- [`__version__` fallback (`"0+unknown"`) in source checkouts without installed metadata] → same accepted trade-off as core; `pip install -e .` in dev environments restores real versions; documented in the template.
- [Six repos to land + release; partial-completion window where some siblings conform and some don't] → per-repo task groups with identical verification gates; the conformance checker makes the remaining gap visible at any point; no cross-package runtime coupling is touched, so partial states are safe.
- [view/model work flows through ladisk forks while the others push to the sdypy org] → implementation lands on whatever remote each clone tracks (as in change #1); upstream PR flow unchanged; conformance checks are remote-agnostic.
- [Distribution-layer conformance tests in core CI hit PyPI and stay red until all six patch releases are published] → same dynamic as the current change #1/#2 conformance reds (known, external); checks are written to test the *latest* release so each publish flips its package green.
- [Removing `requirements.txt` may break unknown consumers pinning via raw-URL requirements files] → low likelihood (these files mostly mirrored pyproject deps); deps remain installable via `pip install sdypy-<pkg>`; called out in release notes.

## Migration Plan

Per sibling repo (×6), in one commit series each: delete stale files → pyproject alignment → `__init__.py` version derivation → workflow rewrite/rename → scaffolding files. Verification gate per repo before push: `python -m build` clean; fresh-venv `pip install .` then import + `__version__` check (from a neutral dir — never the parent `SdyPy` dir, folder shadowing); `tools/check_sibling_template.py` green. Core repo: add the checker script + extend conformance tests + (on archive) promote the spec. Rollback: per-repo `git revert`; no data or API migration involved.

## Open Questions

All resolved by the maintainer 2026-06-12:

- **Q1 — PyPI trusted publishing:** **keep token-based auth** for now; trusted publishing revisited at change #5 or #8. (Design default confirmed.)
- **Q2 — Development Status for EMA:** **EMA keeps `5 - Production/Stable`**, the 0.x packages get `4 - Beta` (D5 confirmed as written).
- **Q3 — Docs URLs / RTD registration:** **thin wrappers keep their Documentation URL pointing at the backend's docs** (pyFRF/pyExSi); no RTD registration in this change. D5's URL rule is scoped accordingly (Homepage/Source own-repo only); per-package docs hosting is a change #6 question.
