"""P4-B3 — `celpy` against `cel-expr-python` over the admitted grammar. G-CELPY's evidence.

**Explicitly NOT one of the four required differentials D1–D4**, and it does not claim their status.
It is D-P4-04's fallback: the official conformance suite is textproto driven through a conformance
server, and this harness stands in for it under a different and weaker label.

The measurement file is `docs/measurements/P4-cel-conformance.md`, produced by
`tools/cel_conformance.py`. This test runs the same harness and asserts the file on disk is the one
the code produces — a measurement nobody can regenerate is a screenshot.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip(
    "cel_expr_python",
    reason="pinned in requirements.lock as a test dependency; a missing one is an environment "
    "defect, not a reason to report a one-runtime number as agreement",
)

import cel_conformance as harness  # noqa: E402

REPORT = REPO / "reports" / "p4-cel-conformance.json"
DOC = REPO / "docs" / "measurements" / "P4-cel-conformance.md"


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return [
        {"slice": c.slice, "src": c.src, "why": c.why,
         "celpy": harness.run_celpy(c.src), "reference": harness.run_reference(c.src)}
        for c in [*harness.SUBSET, *harness.ERRORS]
    ]


def test_diff__the_two_runtimes_agree_on_the_admitted_subset(rows: list[dict]) -> None:
    bad = [r for r in rows if r["slice"] == "subset" and not harness.agree_strict(r["celpy"], r["reference"])]
    assert bad == [], f"disagreements on the admitted grammar: {[r['src'] for r in bad]}"


def test_diff__the_error_semantics_slice_is_reported_on_its_own(rows: list[dict]) -> None:
    """If the runtimes differ HERE, the pre-flight guard's necessity argument differs with them."""
    bad = [r for r in rows if r["slice"] == "errors" and not harness.agree_strict(r["celpy"], r["reference"])]
    assert bad == [], f"disagreements on error semantics: {[(r['src'], r['celpy'], r['reference']) for r in bad]}"


def test_diff__the_comparison_will_not_call_one_equal_to_true() -> None:
    """The defect this harness actually had.

    `celpy.celtypes.BoolType` subclasses `int`, so a normaliser testing `isinstance(v, bool)`
    turned every celpy boolean into `1` — and `1 == True`, so the harness reported agreement
    between a runtime returning integers and one returning booleans on 40 of 47 rows. A false
    agreement inside the instrument built to detect disagreement.
    """
    assert harness.agree_strict(True, True)
    assert not harness.agree_strict(1, True)
    assert not harness.agree_strict(0, False)
    assert not harness.agree_strict([1], [True])


def test_diff__the_coverage_set_is_discriminating(rows: list[dict]) -> None:
    """The admission-side control. Two runtimes that both error on everything agree perfectly."""
    values = [r["celpy"] for r in rows]
    assert any(v is True for v in values), "no row evaluates to true"
    assert any(v is False for v in values), "no row evaluates to false"
    assert any(v == harness.ERROR for v in values), "no row errors, so the error slice is vacuous"
    assert any(isinstance(v, list) for v in values), "no row returns a list"


def test_diff__the_published_measurement_is_the_one_the_code_produces() -> None:
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "cel_conformance.py")],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert DOC.is_file() and REPORT.is_file()
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    assert data["label"] == "DIFFERENTIAL", (
        "the label travels with the number: two implementations wrong the same way are invisible "
        "to a differential, and calling it CONFORMANCE would claim otherwise"
    )
    doc = DOC.read_text(encoding="utf-8")
    assert "DIFFERENTIAL, not CONFORMANCE" in doc
    assert "error semantics" in doc
    for s in ("subset", "errors"):
        a, t = data["by_slice"][s]["agree"], data["by_slice"][s]["total"]
        assert t > 0 and f"**{a}/{t}**" in doc, f"the {s} slice's figure is not rendered"
