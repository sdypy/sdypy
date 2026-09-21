Nomenclature
============

SDyPy fixes one name per quantity across all first-level packages, so that
``sdypy.EMA``, ``sdypy.model`` and the rest do not each invent their own
spelling for a damping ratio or a stiffness matrix. The canonical names are
decided by `SEP 2`_ and reproduced below.

How to use the table
--------------------

* Writing a new public function or class? Look the quantity up in the
  **Symbol** column and use that name for the parameter or attribute.
* Renaming an existing one? Find your current spelling in the **Instead of**
  column; the row tells you what to move to. Keep the old name working as a
  deprecated alias — SEP 2's deprecation policy holds it through all of v1.x.
* Quantity not in the table? See `Proposing and recording a new term`_ below.

The table binds the **public surface** only: parameters, attributes and return
names that a caller can see. Local variables inside a numerical routine are
free to use whatever short symbols read best.

Two affix conventions ride alongside it: a count is ``n_<plural>``
(``n_modes``, ``n_nodes``), never a bare ``n``; an index is ``<name>_idx``
(``node_idx``), never ``_ind``.

Checking a proposed name
------------------------

``tools/check_nomenclature.py`` audits a sibling clone without importing it::

    python tools/check_nomenclature.py --path ../sdypy-EMA

**Nothing runs this for you.** The umbrella CI excludes it by design — each
clone-auditing checker resolves exactly one portion under ``sdypy/`` and the
umbrella provides none — and no sibling CI invokes it either. It is run by hand.

It decides four faults, and only these four:

``nomenclature``
    The name is recorded in SEP 2's **Instead of** column; use the canonical
    name from the same row.

``index-suffix``
    The name ends in ``_ind``; use ``_idx``.

``count-name``
    The name is a bare ``n``; name what it counts, as ``n_<plural>``.

``parameter-case``
    The name is all-uppercase and the table has no canonical entry for it;
    choose a descriptive ``snake_case`` name.

A clean run therefore means *no known fault*, not *a good name*. Whether a new
descriptive name is the right one is a reviewer's judgement, and the checker
cannot make it.

Proposing and recording a new term
----------------------------------

Conformance to SEP 2 is the **pull-request author's responsibility**. No tool
detects an undeclared new name.

Say you are adding residual vectors to a modal model, and the table has no entry
for them.

1. **Check the table.** No row covers the quantity, so a name has to be coined.
2. **Apply the rules that exist.** ISO 7626 does not define modal residual
   terms, so the general guidelines govern alone. Broader term first gives
   ``residual_vectors`` rather than ``vectors_residual``.
3. **Run the checker** against your clone. It will not object — see above for
   what that does and does not mean.
4. **Declare the name in the pull request** that introduces it, and let the
   reviewer assess it against the guidelines and ISO 7626. An uncontested name
   merges with the feature. No amendment to SEP 2 is required first.
5. **The name is recorded later.** Declared names collect on a *SEP 2 pending
   terms* issue and reach the canonical table through an amendment pull request
   that a maintainer triggers, with a reminder at release time. Recording never
   blocks a feature.

The pending-terms issue is not permanent. One is opened when the first name
since the last amendment is declared, and the amendment pull request closes it.
An open issue is therefore the signal that an amendment is due; between rounds
there is no issue at all.

If the pull request *cannot* settle the name — the guidelines and ISO conflict,
ISO is silent where a term was expected, or the reviewers disagree — it is
escalated to an issue plus a pull request amending SEP 2. That blocks the
contested name alone, not the rest of the feature.

Adding a term to the canonical table
------------------------------------

When the amendment is written, in this order:

1. Add the row to the ``list-table`` in ``docs/seps/sep-0002.rst``: Parameter,
   Symbol, Instead of, Unit, Description. Leave **Instead of** empty unless the
   canonical name replaces a spelling actually evidenced in a package.
2. If it does replace one, add that spelling to the ``CANONICAL`` map in
   ``tools/check_nomenclature.py``.
3. Run ``pytest tests/test_nomenclature.py``.

Step 3 is the gate. The two mirror tests hold the SEP and the checker set-equal
in both directions, so a table row whose divergent spellings are missing from
the map — or a map entry missing from the table — fails the suite rather than
merging silently.

The canonical table
-------------------

The table below is included from its single definition in `SEP 2`_. If you are
reading this file as source on GitHub rather than on the documentation site,
the table will not appear here — GitHub does not process file includes. Read it
in `SEP 2`_ instead, where it lives.

.. include:: ../seps/sep-0002.rst
   :start-after: .. canonical-table-start
   :end-before: .. canonical-table-end

Where this comes from
---------------------

The table above is not a copy. It is transcluded from
`SEP 2`_, which is its single definition and the source of truth for both the
canonical names and the divergent spellings they replace.
Editing the SEP updates this page.

See SEP 2 itself for the governance context: the deprecation policy, the rules
for naming modules, classes and constants, the public-API surface requirements,
and the SEP's current status.


.. _SEP 2: https://sdypy.readthedocs.io/en/latest/seps/sep-0002.html
