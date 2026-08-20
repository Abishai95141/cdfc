"""A1c uses 2 and 3 — schema matching and record linkage, both on DERIVED weights."""

from __future__ import annotations

from pathlib import Path

import pytest

from cdfc.correspond.link import Comparison, exact, link, numeric
from cdfc.correspond.schema import columns_from_rows, match
from cdfc.evidence.fields import from_template, select_rule

BLANK = Path("fixtures/prescribed/"
             "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")


@pytest.fixture(scope="module")
def fields():
    return from_template(BLANK, rule=select_rule(BLANK))


# --- use 2: a source column to a template field -------------------------------------------------

def test_use2__matches_paraphrased_headers_to_the_right_fields(fields) -> None:
    """No shared address space: a custodian export and a template have only meaning in common.
    Ground truth is a CONSTRUCTION -- these headers are the fields' own labels."""
    want = {
        "Name of FME": "1. Introduction!D9",
        "Registration Number of the Fund Management Entity (FME)": "1. Introduction!D8",
        "Date of Registration of FME": "1. Introduction!D11",
        "Legal Structure of FME": "1. Introduction!D12",
        "PAN of FME": "1. Introduction!D13",
    }
    cols = columns_from_rows(
        [*want, "Unrelated Column"],
        [["Meridian", "REG-001", "2025-04-01", "Company", "AAAAA1111A", "x"]])
    r = match(cols, fields)
    got = {c: f for c, f, _w in r.pairs}
    for col, ref in want.items():
        assert got.get(col) == ref, f"{col!r} matched {got.get(col)}, wanted {ref}"


def test_use2__a_column_nothing_supports_is_refused(fields) -> None:
    """It must not be forced onto the least-bad field. Absent is a state."""
    r = match(columns_from_rows(["Zzz Nonsense Header"], [["x"]]), fields)
    assert not r.pairs
    assert r.refused


def test_use2__the_weights_are_derived_not_chosen(fields) -> None:
    """The whole reason this is not a similarity threshold. W0-C measured what a threshold does."""
    r = match(columns_from_rows(["Name of FME", "PAN of FME"], [["a", "b"]]), fields)
    assert r.m and r.u
    assert any(a != b for a, b in zip(r.m, r.u)), "EM must separate match from non-match"


# --- use 3: record to record --------------------------------------------------------------------

def _cmps():
    return [Comparison("lei", exact), Comparison("name", exact), Comparison("nav", numeric)]


def test_use3__links_a_constructed_overlap_exactly() -> None:
    left = [{"lei": f"L{i:03d}", "name": f"Fund {i}", "nav": str(1000 + i)} for i in range(30)]
    right = [{"lei": f"L{i:03d}", "name": f"Fund {i}", "nav": str(1000 + i)} for i in range(15, 45)]
    res = link(left, right, _cmps())
    truth = {(i, i - 15) for i in range(15, 30)}
    assert {(i, j) for i, j, _w in res.pairs} == truth


def test_use3__em_converges_and_says_so() -> None:
    """A result from a fit that did not converge has no warrant. The criterion is the
    log-likelihood, which EM monotonically increases -- an absolute parameter delta cannot serve
    values spanning six orders of magnitude, and reported `converged: False` on a sound fit."""
    left = [{"lei": f"L{i:03d}", "name": f"F{i}", "nav": str(9000 + i * 7)} for i in range(40)]
    right = [dict(r) for r in left[10:]]
    res = link(left, right, _cmps())
    assert res.weights.converged, f"did not converge in {res.weights.iterations} iterations"


def test_use3__survives_degraded_records() -> None:
    """The case that discriminates. A clean population fits m=1.0/u=0.0 and proves nothing."""
    import sys

    sys.path.insert(0, "tools/measure")
    from n4_linkage import build, score

    left, right, truth = build()
    res = link(left, right, _cmps())
    s = score({(i, j) for i, j, _w in res.pairs}, truth)
    assert s["f1"] > 0.9, s
    assert res.weights.converged


def test_use3__a_tie_is_refused_not_broken() -> None:
    """Two candidates of comparable weight is the same hazard as two blanks sharing a sheet set."""
    left = [{"lei": "", "name": "Same", "nav": "100"}]
    right = [{"lei": "", "name": "Same", "nav": "100"},
             {"lei": "", "name": "Same", "nav": "100"}]
    res = link(left, right, _cmps())
    assert not res.pairs, "an exact tie must not be broken arbitrarily"
    # It is refused as UNLINKED with a reason, not as ambiguous: when every comparison is
    # worthless (m == u) the evidence does not favour either candidate over a stranger, which is
    # a different statement from "two candidates are close".
    assert res.unlinked and "positive evidence" in res.unlinked[0][1]


def test_use3__every_left_record_is_accounted_for() -> None:
    """linked + ambiguous + unlinked == the input. A linkage that drops records silently reports
    a coverage it does not have, and the dataclass refuses to be constructed that way."""
    import sys

    sys.path.insert(0, "tools/measure")
    from n4_linkage import build

    left, right, _truth = build()
    res = link(left, right, _cmps())
    assert len(res.pairs) + len(res.ambiguous) + len(res.unlinked) == res.left_total


def test_a1c__splink_is_a_reference_not_a_dependency() -> None:
    """Splink is what our linkage is SCORED AGAINST, never what it runs on.

    It brings duckdb, pandas and sqlglot, and `cdfc.correspond` is reachable from a coverage
    number. Keeping it out is the same closure decision as writing our own Datalog -- and unlike
    that one it is not a quality claim: `N4` measures both.
    """
    import ast
    import pathlib

    for f in pathlib.Path("src/cdfc/correspond").glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text(encoding="utf-8"))):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
            for n in names:
                assert not n.split(".")[0] in {"splink", "duckdb", "pandas"}, \
                    f"{f.name} imports {n}; splink is measurement-time only"
