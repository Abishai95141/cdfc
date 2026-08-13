"""P7-B0 — the D5 differential: two independent extractions of every pinned blank.

**What makes this a differential and not a ceremony.** Party A is this repository's raw reader plus
its own shared-formula shift; party B is `openpyxl`, which nobody here wrote. **The 211 shared
dependents on FME have no expression anywhere in the file** — their text is COMPUTED by
`calc/shift.materialise` — so until this test nothing in the project checked that computation
against a second implementation.

**The agreement rate is PUBLISHED, never assumed**, and it is published as two vectors so a check
against an outside library is never averaged with a check of two implementations by one author.

**The zero is only evidence because the harness can produce a non-zero**, which
`test_diff__a_perturbed_shift_is_reported_as_a_dispute` demonstrates by breaking the shift by one
row and watching the disputed count move.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify import template_instrument as TI  # noqa: E402
from cdfc.qualify.textsource import Corroboration  # noqa: E402

FIX = REPO / "fixtures" / "prescribed"
FME = FIX / "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


@pytest.fixture(scope="module")
def all_instruments():
    return {p.name: TI.emit(p) for p in sorted(FIX.glob("*.xlsx"))}


def test_diff__every_pinned_blank_has_two_parties(all_instruments):
    for name, it in all_instruments.items():
        assert len(it.manifests) == 2, name
        assert sum(1 for m in it.manifests if m.external) == 1, (
            f"{name}: exactly one party must be a library nobody here wrote. Two same-author "
            "readers agreeing is a check of one understanding written twice."
        )


def test_diff__the_two_parties_are_two_implementations(all_instruments):
    """The guard against comparing a party with itself, which would agree perfectly and mean
    nothing.

    **Identical per-instrument digests are the CORRECT outcome of perfect agreement** — on ALR
    both parties produce the same 652 units — so equality is not the tell. What distinguishes the
    parties is that their unit lists diverge wherever one of them is blind, and the corpus does
    contain such instruments. The live proof that the comparison has teeth is the perturbation
    control below; this test only refuses a corpus where the two names never separate.
    """
    separated = [
        name for name, it in all_instruments.items()
        if len({m.sha256 for m in it.manifests}) == 2
    ]
    assert separated, (
        "on every instrument in the corpus the two parties produced byte-identical unit lists. "
        "That is possible, but it means nothing here would notice if one reading were passed "
        "twice, so the corpus cannot carry this check."
    )
    for name, it in all_instruments.items():
        assert {m.extractor for m in it.manifests} == {"openpyxl", "reader_lxml+calc.shift"}, name


def test_diff__agreement_is_published_as_two_vectors(all_instruments):
    """Both vectors, both as `n/d`. Neither may be rendered without the other, and neither may be
    rendered as a bare rate — the rule `ingest/agreement.py` already enforces one level up."""
    doc = (REPO / "docs/measurements/P7-textsource.md").read_text(encoding="utf-8")
    ext_n = sum(it.agreement()["EXTERNAL"][0] for it in all_instruments.values())
    ext_d = sum(it.agreement()["EXTERNAL"][1] for it in all_instruments.values())
    same_n = sum(it.agreement()["SAME_AUTHOR"][0] for it in all_instruments.values())
    same_d = sum(it.agreement()["SAME_AUTHOR"][1] for it in all_instruments.values())
    assert f"`{ext_n} / {ext_d}`" in doc, "the EXTERNAL vector is not published with its denominator"
    assert f"`{same_n} / {same_d}`" in doc, "the SAME-AUTHOR vector is not published"
    assert "EXTERNAL" in doc and "SAME-AUTHOR" in doc


def test_diff__disagreements_are_enumerated_with_their_location(all_instruments):
    """Every disputed unit is listed with its page (for a workbook, the 1-based sheet ordinal) and
    every party's reading. A dispute counted but not shown is a number nobody can act on."""
    doc = (REPO / "docs/measurements/P7-textsource.md").read_text(encoding="utf-8")
    for name, it in all_instruments.items():
        for d in it.disputed:
            assert d.page >= 1
            assert len(d.readings) >= 2, f"{name}: a dispute needs two readings"
            assert d.key in doc, f"{name}: disputed unit {d.key} is not published"


def test_diff__a_perturbed_shift_is_reported_as_a_dispute(monkeypatch):
    """THE POSITIVE CONTROL. Break `calc/shift.materialise` by one row and the external party must
    report it.

    Without this the corpus-wide `0 disputed` above is indistinguishable from a harness that
    cannot see a disagreement — which is exactly the shape of defect this project exists to catch,
    committed inside the instrument that measures it.
    """
    import cdfc.calc.shift as shift

    real = shift.materialise

    def off_by_one_row(master_ref: str, master_text: str, target_ref: str) -> str:
        import re as _re

        out = real(master_ref, master_text, target_ref)
        return _re.sub(r"([A-Z]{1,3})(\d+)", lambda m: f"{m.group(1)}{int(m.group(2)) + 1}", out)

    monkeypatch.setattr(shift, "materialise", off_by_one_row)
    it = TI.emit(FME)
    disputed = it.counts()[Corroboration.DISPUTED.value]
    assert disputed > 0, (
        "the shift was perturbed by one row on every shared dependent and the harness reported no "
        "disagreement. The external party is not being compared."
    )
    assert it.addressable_fraction()[0] < it.addressable_fraction()[1], (
        "a disputed unit must leave the addressable text"
    )
    for d in it.disputed[:1]:
        assert it.text[d.span[0] : d.span[1]] == "�"


def test_diff__the_unperturbed_corpus_is_clean(all_instruments):
    """The measurement itself, asserted with both integers so it can never render as a bare rate."""
    agreed = sum(it.counts()[Corroboration.AGREED.value] for it in all_instruments.values())
    disputed = sum(it.counts()[Corroboration.DISPUTED.value] for it in all_instruments.values())
    total = sum(it.counts()["units_total"] for it in all_instruments.values())
    single = sum(it.counts()[Corroboration.SINGLE_PARTY.value] for it in all_instruments.values())
    assert agreed + disputed + single == total, "the three corroboration states must partition"
    assert disputed == 0, (
        f"{disputed} of {total} units disputed. This is a finding about one of the two readers "
        "and it belongs in docs/measurements/P7-textsource.md before this assertion moves."
    )
