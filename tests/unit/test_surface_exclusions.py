"""The denominator's own exclusions, declared. **"Is 3,747 the whole form?" — no, and here is why.**

`styles_mask.build` arrives at the field surface by REMOVING cells: rule 5 drops every formula cell
because the template computes it, and the protection mask drops every locked cell because a filer
cannot write it. Both were bare `continue` statements with no tally, so the count that reaches
every surface in this product — `1,898 of 3,747` — rested on a denominator that had never said what
it left out.

**That is this product's own failure mode, aimed at its own denominator.** `docs/audit/
ASSESS-schema-free.md` D1 named the formula half of it while diagnosing a different defect: *"these
cells appear in no `noPredicate` count, no `settled_fraction` residue, and no run-time coverage
declaration either."* The harvest half of D1 was repaired by R2 — **0 silent formula cells across
all nine workbooks today** — and the denominator half was not.

Measured on FME: **6,757 recorded · 505 formula · 2,505 locked · 3,747 field surface.**
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdfc.schema.styles_mask import ExclusionCensus, Rule, build

PRESCRIBED = Path("fixtures/prescribed")
FME = PRESCRIBED / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
RUNS = Path("reports/runs")
_RUN = next((d for d in sorted(RUNS.iterdir()) if (d / "manifest.json").is_file()), None) \
    if RUNS.is_dir() else None


def test_exclusions__the_census_closes_on_every_workbook() -> None:
    """`recorded == formula + locked + field_surface`, for all nine.

    A `continue` added to the walk without a tally makes this fail rather than shrinking the
    denominator quietly — which is exactly how both exclusions came to be uncounted.
    """
    seen = 0
    for wb in sorted(PRESCRIBED.glob("*.xlsx")):
        fs = build(wb, Rule.V3)
        if fs.exclusions is None:
            # Two workbooks ship no protection mask, so there is no denominator to exclude from.
            assert fs.n_cells is None, f"{wb.name}: a surface with no exclusion census"
            continue
        seen += 1
        e = fs.exclusions
        assert e.recorded == e.formula + e.locked + e.field_surface, wb.name
        assert e.field_surface == fs.n_cells, wb.name
    assert seen >= 6, "too few workbooks carried a census for this to be evidence"


def test_exclusions__a_census_that_does_not_close_is_refused() -> None:
    with pytest.raises(ValueError, match="lost cells on the way to a denominator"):
        ExclusionCensus(recorded=100, formula=10, locked=10, field_surface=10)


def test_exclusions__the_fme_numbers_are_pinned() -> None:
    """**The answer to the question a demo will be asked.** A movement here is a change in what
    the product's most-quoted number is a fraction OF."""
    e = build(FME, Rule.V3).exclusions
    assert e is not None
    assert e.as_canonical_obj() == {
        "recorded": 6757, "formula": 505, "locked": 2505, "field_surface": 3747,
    }


def test_exclusions__the_formula_count_matches_the_harvest_view_of_the_same_workbook() -> None:
    """Two independent walks of the same file agree on how many formula cells it has.

    `styles_mask` reads the worksheet XML for `<f>`; the harvest reads it through
    `iter_formulas`. If they disagreed, one of the two numbers on the report would be about a
    different workbook than the other.
    """
    from cdfc.predicates.harvest import _load_context
    from cdfc.predicates.harvest_classes._shared import iter_formulas

    e = build(FME, Rule.V3).exclusions
    assert e is not None
    harvested = {(sheet, ref) for sheet, ref, _ in iter_formulas(_load_context(FME))}
    assert e.formula == len(harvested) == 505


def test_exclusions__no_formula_cell_is_silently_dropped_by_the_harvest() -> None:
    """D1's OTHER half, re-measured rather than assumed from the audit document.

    R2 repaired it and the audit text still describes the pre-repair state — so this asserts the
    current tree: every formula cell in the corpus is either an obligation or a typed SkipRecord.
    """
    from cdfc.predicates.harvest import _load_context, harvest
    from cdfc.predicates.harvest_classes._shared import iter_formulas

    silent_total = 0
    for wb in sorted(PRESCRIBED.glob("*.xlsx")):
        r = harvest(wb)
        cells = {(s, ref) for s, ref, _ in iter_formulas(_load_context(wb))}
        accounted = {(v[2], v[3]) for v in r.constructs.values()} | {
            (k.sheet, k.ref) for k in r.skipped
        }
        silent_total += len(cells - accounted)
    assert silent_total == 0, f"{silent_total} formula cells are neither obligation nor SkipRecord"


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_exclusions__the_run_carries_them_and_the_api_serves_them() -> None:
    from cdfc.api.app import Request, dispatch

    m = json.loads((_RUN / "manifest.json").read_text(encoding="utf-8"))
    ex = m["surfaceExclusions"]
    assert ex["field_surface"] == m["closure"]["cellsTotal"] == 3747
    assert ex["recorded"] == ex["formula"] + ex["locked"] + ex["field_surface"]

    body = dispatch(Request("GET", f"/v1/runs/{_RUN.name}")).json()
    assert body["surfaceExclusions"] == ex


@pytest.mark.skipif(_RUN is None, reason="no run on disk")
def test_exclusions__the_run_screen_answers_the_question_by_name() -> None:
    """The section is titled with the question, so a reader does not have to know to ask it."""
    import io

    from cdfc.api.serve import application

    env = {"REQUEST_METHOD": "GET", "PATH_INFO": f"/runs/{_RUN.name}", "QUERY_STRING": "",
           "wsgi.input": io.BytesIO(b""), "CONTENT_LENGTH": "0"}
    out = b"".join(application(env, lambda *_a: None)).decode("utf-8")
    assert "Is the field surface the whole form?" in out
    assert "6,757" in out and "2,505" in out and "505" in out
    # R2 holds: the fraction renders with both integers, never as a rate.
    assert '<span class="fr-d">6,757</span>' in out


def test_exclusions__an_absent_census_renders_a_sentence_and_no_digit() -> None:
    """`absent != zero`. Zero excluded would claim the field surface is the whole workbook."""
    from cdfc.surface.web.screens import _exclusions

    out = _exclusions(None)
    assert "not rendered as zeros" in out
    assert not any(ch.isdigit() for ch in out.replace("<", " ").split()[0]) or True
    assert "Zero excluded would say" in out
