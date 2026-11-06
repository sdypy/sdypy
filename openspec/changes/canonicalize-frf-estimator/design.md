## Context

`sdypy.FRF` re-exports pyFRF's `FRF` class unchanged (`sdypy-FRF` has no FRF
code of its own). pyFRF names the estimator `frf_type` (constructor, instance
attribute) and `type` (`get_FRF`), and the FRF form `form` (`get_FRF`).
`sdypy-EMA` already renamed its FRF-form parameter from `frf_type` to
`frf_form`, with a shim. `pyEMA` re-exports `sdypy-EMA` and has no code of its
own.

The checker (`tools/check_nomenclature.py`) audits one portion under `sdypy/`
in a sibling clone. It cannot see pyFRF, and on `sdypy-FRF` it sees only the
re-export line. Its map holds `frf_type` → `frf_form`, pinned two-way against
SEP 2's **Instead of** column.

## Goals / Non-Goals

**Goals**

- One canonical name per FRF quantity on the public surface a `sdypy` user
  sees: `frf_form` for the ratio, `frf_estimator` for H1/H2/Hv/ODS.
- No broken user code: every old keyword and attribute keeps working through
  v1.x with a `DeprecationWarning`, and positional calls do not change.
- A repeatable shape for a change that spans the hub and several package
  repositories.

**Non-Goals**

- Different defaults between packages (`sdypy-EMA` defaults to
  `'accelerance'`, `get_FRF` to `'receptance'`). This is a behaviour change,
  not a naming change.
- Renaming pyFRF's other public names (`exc_type`, `resp_type`,
  `sampling_freq`, `get_H1`, ...). They are recorded as observations only.
- Changes to the checker's scope, or checker runs in package CI (REQUIREMENTS.md
  § Pending D).
- `pyFRF.fft_tools.convert_frf(input_frf_type, output_frf_type)` uses
  `frf_type` in the FRF-form sense. `sdypy.FRF` does not re-export it, so the
  new scope rule leaves it out. Recorded as an observation.

## Decisions

**D1: `frf_estimator`, not `estimator` or `frf_type`.** The `frf_` prefix
matches `frf_form` and keeps the name unambiguous in a signature that also
takes window, averaging and delay options. Draft SEP 6 already uses the
name. `frf_type` is rejected because it collides with the old EMA spelling of
the FRF form. ISO 7626 does not define the quantity. ISO 18431-1 says
"of the first/second type", but `type` is ambiguous and shadows a built-in, so
this is recorded as a reasoned choice, not as an ISO divergence.

**D2: Keep `'ODS'` as an estimator value.** pyFRF offers it through the same
switch, and removing it is a behaviour change. It is an operational deflection
shape, not an H-estimator in the strict sense. The table row lists it with
that remark.

**D3: Context-dependent spellings go in the notes, not the column.** Putting
`type` or `form` in the **Instead of** column would make the checker report
every `type` or `form` parameter in all six packages. `frf_type` already maps
to `frf_form` in the column. It cannot map to two names, and its FRF-form
sense is the one the checker can see in the siblings. The estimator sense,
`type` and `form` go in a note below the table, the same way as `xi` and
`phi`. pyFRF's own tests verify these renames. The checker map does not
change. New hub tests pin that `type` and `form` are not in the map.

**D4: Shim shape, as in sdypy-EMA's `frf_type` shim.** The new name takes the
old parameter's position, so positional calls do not change. The old name
becomes a keyword-only parameter defaulting to `None`. If it is passed, the
method emits `DeprecationWarning` and the old value wins. There is no
`TypeError` when both are passed: the new names have real defaults (`'H1'`,
`'default'`, `'receptance'`), so "both passed" cannot be told apart from "only
the old one passed". The instance attribute `frf_type` becomes a property
over `frf_estimator` that emits the warning. Unlike sdypy-EMA's read-only
property it also has a setter, because pyFRF users can set the default
estimator after construction. Inside `get_FRF` the keyword `type` shadows the
built-in, as it does today; the body never calls `type(...)`.

Instances pickled with pyFRF 1.4 carry `frf_type` in their `__dict__`.
`FRF.__setstate__` moves it to `frf_estimator`, so old pickles still load.

The same shim applies to the public sdypy-EMA functions `LSFD`,
`LSFD_proportional` and `LSFD_old`: `frf_type` becomes `frf_form` in the same
position, with a keyword-only deprecated `frf_type`.

```python
def get_FRF(self, frf_estimator='default', frf_form='receptance', *,
            type=None, form=None):
```

**D5: `sdypy-EMA` calls `get_FRF` positionally.** Today it calls
`get_FRF(form='receptance')`. `sdypy-EMA` does not depend on pyFRF;
`add_frf()` takes any pyFRF object. `get_FRF('default',
'receptance')` works with pyFRF before and after 1.5.0 without a warning. A
keyword call would need either a minimum-version pin or a warning on older
installs.

**D6: One hub change, one pull request per repository.** The hub pull request
carries the specs, the SEP amendment and the hub tests. pyFRF, sdypy-FRF,
sdypy-EMA and pyEMA each get one pull request that links the hub pull request.
Merge order: hub, pyFRF (release 1.5.0), sdypy-FRF (needs pyFRF 1.5,
release 0.3.0), sdypy-EMA (release 0.31.0), pyEMA. Draft SEP 6 says tasks
live where the code lives; this change keeps all tasks in the hub on purpose,
so the whole cross-repository change reads in one place. SEP 6 can adopt or
reject that shape. The hub change is archived after the last package pull
request is merged, and the archive commit updates REQUIREMENTS.md.

**D7: Supersede PR #6.** PR #6 records the estimator sense of `frf_type`
with no canonical name. This change writes that note with `frf_estimator` in
it. The hub pull request states that it supersedes #6 and asks its author
whether to close #6 or merge it first. If #6 merges first, this change
rewrites its paragraph.

## Risks / Trade-offs

- **The checker cannot see pyFRF.** Conformance on the backend is enforced by
  pyFRF's tests only. → The hub spec names those tests as the verifier in
  REQUIREMENTS.md.
- **pyFRF 1.4 silently ignores the new keyword.** `FRF.__init__` takes
  `**kwargs`, so `FRF(..., frf_estimator='H2')` on 1.4 gives H1 with no error.
  → sdypy-FRF pins pyFRF 1.5; the pyFRF README states "since 1.5.0" next to
  the new keywords. Rejecting unknown kwargs is a behaviour change and is out
  of scope.
- **Warning noise.** Scripts that pass `frf_type=` or `form=` get a warning
  per call. → This is the SEP 2 deprecation policy; the message names the new
  keyword.
- **Draft SEP 6 may define a different cross-repo procedure.** → D6 is small
  and can be adapted. This change is a worked example for SEP 6.

## Open Questions

- Should SEP 2 bind third-level backends that no first-level package
  re-exports (for example pyExSi functions not re-exported by
  `sdypy-excitation`)? This change says no.

Resolved 2026-09-28 by the project lead: `'ODS'` stays an estimator value
(D2); pyEMA's version follows sdypy-EMA (0.31.0, task 5.2).
