## 1. Delete stale files

- [ ] 1.1 Delete `setup.py` from the repository root.
- [ ] 1.2 Delete `.travis.yml` from the repository root.
- [ ] 1.3 Delete `requirements.txt` from the repository root.
- [ ] 1.4 Delete `requirements.dev.txt` from the repository root.
- [ ] 1.5 Delete `docs/requirements.txt`.

## 2. Update pyproject.toml

- [ ] 2.1 Add a `[project.optional-dependencies]` `docs` entry: `sphinx`, `sphinx-rtd-theme`, `sphinx-copybutton>=0.5.2`.
- [ ] 2.1b Refactor the `dev` extra to reference the docs extra instead of duplicating its entries: `dev = ["sdypy[docs]", "twine", "wheel", "pytest", "build"]`.
- [ ] 2.2 Add `Programming Language :: Python :: 3.11` and `Programming Language :: Python :: 3.12` to the `classifiers` list.
- [ ] 2.3 Change the `Development Status` classifier from `5 - Production/Stable` to `4 - Beta`.
- [ ] 2.4 Remove the `requirements.txt` and `requirements.dev.txt` entries from the `[tool.hatch.build.targets.sdist]` include list.

## 3. Update docs/source/conf.py

- [ ] 3.1 Add `from importlib.metadata import version as _pkg_version` near the top of `conf.py`.
- [ ] 3.2 Replace the hard-coded `release = '0.5.1'` line with `release = _pkg_version("sdypy")`.
- [ ] 3.3 Replace the hard-coded `version = '0.5'` line with `version = ".".join(release.split(".")[:2])`.

## 4. Update CI workflow

- [ ] 4.1 In `.github/workflows/python-package.yml`, replace the line:
  ```
  if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
  ```
  with:
  ```
  pip install .
  ```

## 5. Update readthedocs.yaml

- [ ] 5.1 Replace the `python.install` entry that references `docs/requirements.txt` with a pip-based install:
  ```yaml
  python:
    install:
      - method: pip
        path: .
        extra_requirements:
          - docs
  ```

## 6. Purge tracked build output

- [ ] 6.1 Run `git rm -r --cached docs/source/_build` to remove the 131 tracked build files from the index without deleting them from the working tree.
- [ ] 6.2 Add the line `_build/` to `.gitignore` (covers any `_build` directory at any nesting depth; more general than the existing path-specific entries).

## 7. Verification gates

- [ ] 7.1 Run `python -m build` and inspect the sdist tarball: confirm it contains no `setup.py`, `.travis.yml`, `requirements.txt`, `requirements.dev.txt`, `openspec/`, or `.claude/` entries, and no path under `_build/`.
- [ ] 7.2 Run `python -m build` and inspect the wheel: confirm its contents are identical to a pre-change wheel (only `sdypy/` package files).
- [ ] 7.3 In a fresh virtual environment (NOT from `C:\Users\jasas\Work\OpenSource\SdyPy\`): install from the built sdist with `pip install <path-to-sdist>`, then run `python -c "import sdypy; print(sdypy.__version__)"` and confirm it succeeds without error.
  - Use `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\python.exe -m venv <fresh-path>` for the venv; activate and install from a neutral directory.
- [ ] 7.4 Run `git ls-files docs | Select-String _build` (PowerShell) and confirm it returns no matches.
- [ ] 7.5 Confirm `.gitignore` contains a line matching `_build/` (check with `Select-String _build .gitignore`).
- [ ] 7.6 Run the existing pytest suite: `C:\Users\jasas\Work\OpenSource\SdyPy\.venv\Scripts\pytest.exe tests/` and confirm all tests pass.
- [ ] 7.7 Run `openspec validate packaging-hygiene-sweep --strict` and confirm it passes with no errors.
