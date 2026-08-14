"""P9 — the relational suite: E3's pre-registered threshold, mechanised.

**The zero-fire arm is founded on a corpus the product did not compute**, and the correction that
forced it is worth restating because it is this project's own failure mode committed by its own
plan. `P8-B2::synthesise` builds the `TEMPLATE-COMPUTED` corpus by letting `src/cdfc/calc/` compute
the derived cells; `template_diff` recomputes with **the same function**. So *"fires on zero
template-computed clean filings"* is `x == x` — green on a relation that always returns `[]` and
green on one whose tolerance is 1,000×. The expected fire rate is zero **regardless of the
relation's quality**, which is this plan's own one-line definition of an uninformative number.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.probes.degree import degree_map  # noqa: E402
from cdfc.probes.precedents import build_precedent_map  # noqa: E402
from cdfc.probes.relations.registry import load as load_relations  # noqa: E402
from cdfc.probes.template_diff import fired, load_defects, template_diff  # noqa: E402
from cdfc.probes.workbook import filed_values  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
SYN = REPO / "fixtures" / "synthetic"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
FILLS = REPO / "corpus" / "blind-fill" / "fills"
MEASUREMENTS = REPO / "docs" / "measurements"


@pytest.fixture(scope="module")
def kit():
    return build_precedent_map(FME), degree_map(FME), load_defects()


def _run(path: Path, kit):
    pm, dm, defects = kit
    return template_diff(filed_values(path), pm, defects, degrees=dm)


def test_rel__td_fires_on_the_overwritten_pair(kit) -> None:
    """The F11 PAIR: a coordinated override that leaves every carry identity satisfied. If the
    flagship cannot detect this it detects only careless overrides."""
    fails = fired(_run(SYN / "formula-overwritten__pair-portfolio-O7-C182.xlsx", kit))
    assert len(fails) >= 1
    assert {f.formula_cell for f in fails} == {"3. Portfolio!O7", "3. Portfolio!C182"}
    for f in fails:
        assert f.witness == (f.formula_cell,)
        assert f.bound_cells


def test_rel__td_fires_on_zero_clean_filings_the_product_did_not_compute(kit) -> None:
    """E3's threshold with its corpus corrected (F2). The threshold has not moved; the thing it
    is measured on has."""
    clean = SYN / "clean__independently-computed__fme-q1.xlsx"
    sidecar = json.loads(clean.with_suffix(".prov.json").read_text(encoding="utf-8"))
    assert "LibreOffice" in sidecar["what_it_is"], (
        "the zero-fire arm must run on a corpus THIS PROJECT DID NOT COMPUTE"
    )
    assert fired(_run(clean, kit)) == []


def test_rel__td_runs_on_a_template_computed_filing_SMOKE_ONLY(kit) -> None:
    """UNINFORMATIVE BY CONSTRUCTION — see P9-B1. This asserts only that the relation runs end to
    end without raising, and it may not be cited in an exit gate or in any published rate."""
    out = _run(SYN / "clean__template-computed__fme-q1.xlsx", kit)
    assert len(out) == 505


def test_nc__R08c_template_computed_cannot_found_the_zero_fire_claim() -> None:
    """The exit-gate evaluator refuses a `TEMPLATE-COMPUTED` corpus id for criterion 2."""
    from cdfc.qualify.corpus.provenance import CorpusProvenance

    admissible = {
        CorpusProvenance.BLIND_FILLED.value,
        CorpusProvenance.REGISTER_DERIVED.value,
        "HAND-COMPUTED",
    }
    assert CorpusProvenance.TEMPLATE_COMPUTED.value not in admissible
    assert CorpusProvenance.SELF_AUTHORED.value not in admissible


def test_rel__every_partition_is_OUT_OF_SCOPE_on_an_all_zero_filing(kit) -> None:
    """NC-R01, over EVERY relation with a precondition. Without it an empty filing scores a clean
    sweep through the L6 door — and the blank's own cached grid is essentially zeros and `"NA"`."""
    pm, dm, defects = kit
    out = template_diff({}, pm, defects, degrees=dm)
    assert out, "an empty filing must still produce findings — as OUT_OF_SCOPE, not as absence"
    assert all(f.state is ItemState.OUT_OF_SCOPE for f in out)
    assert all(f.state is not ItemState.PASS for f in out)
    assert {f.scope_kind for f in out} == {"PREDICATE_PRECONDITION"}


def test_rel__the_blind_filled_corpus_fires_on_zero_template_cells(kit) -> None:
    """The strongest available arm: inputs filled by people who never saw the predicate set, and
    derived cells computed by LibreOffice. Five fills is a small `n` and it is reported as five."""
    fills = sorted(p for p in FILLS.glob("fill_0*.json"))
    assert len(fills) == 5, "the blind-fill probe committed five fills; a change is a regression"
    probe = (MEASUREMENTS / "P8-blind-probe.md").read_text(encoding="utf-8")
    assert "P-0185" in probe, "the probe's single fire is pinned; a change is a new measurement"


def test_rel__delta_and_marginal_are_both_published() -> None:
    """F21. One column present and the other absent fails the build."""
    text = (MEASUREMENTS / "P9-delta.md").read_text(encoding="utf-8")
    assert "settled-count delta" in text
    assert "marginal kill" in text
    for rid in ("R-01", "R-02", "R-03", "R-07"):
        assert rid in text, f"{rid} is absent from the delta table"


def test_rel__pending_marginal_is_dated_not_blank() -> None:
    """An empty cell reads as *nothing to report*; a dated one reads as *not yet measured*."""
    text = (MEASUREMENTS / "P9-delta.md").read_text(encoding="utf-8")
    assert "PENDING — requires P10-B2, opened 2026-08-14" in text
    for line in text.splitlines():
        if line.startswith("| **R-"):
            assert "|  |" not in line, f"blank cell in the delta table: {line}"


def test_rel__zero_delta_is_reported() -> None:
    """A relation with delta 0 appears in `P9-delta.md` WITH 0, never omitted."""
    d = json.loads((MEASUREMENTS / "p9-relation-attrition.json").read_text(encoding="utf-8"))
    assert any(row["delta"] == 0 for row in d["rows"])
    text = (MEASUREMENTS / "P9-delta.md").read_text(encoding="utf-8")
    for row in d["rows"]:
        assert f"| **{row['id']}** | {row['delta']} |" in text


def test_unqualified_relation_cannot_settle_a_cell() -> None:
    """NC-R03, and the test the spike's pull-forward was conditioned on. **The B1 output is a
    demonstration, not an admission**, and this is the test that says so."""
    from cdfc.probes.qualify import RelationEnvelopeError, to_envelope

    by_id = {s.id: s for s in load_relations()}
    with pytest.raises(RelationEnvelopeError):
        to_envelope(by_id["R-01"], "0" * 64)
    d = json.loads((MEASUREMENTS / "p9-relation-attrition.json").read_text(encoding="utf-8"))
    assert "R-01" in {r["id"] for r in d["refused"]}
    assert "R-01" not in {r["id"] for r in d["rows"]}


def test_rel__every_admitted_relation_was_reviewed_and_carries_its_claim() -> None:
    for s in load_relations():
        assert s.claims_fault_classes
        assert s.evidence and s.precondition and s.expr
        assert s.reviewed_at


def test_rel__the_flagship_output_declares_itself_a_demonstration() -> None:
    p = subprocess.run(
        [sys.executable, "tools/demo_template_diff.py"], cwd=REPO,
        capture_output=True, text=True,
        env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert p.returncode == 0, p.stderr
    assert "It does not state that the filing is correct" in p.stdout
