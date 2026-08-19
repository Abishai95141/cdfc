"""The evidence layer, end to end, with every gate observed REFUSING.

The fixture at `fixtures/evidence/fme-proposals.json` carries five proposals that are wrong ON
PURPOSE, one per gate. They are the positive controls: a gate that has never been seen refusing
is not evidence that it would. Each test below also DEFEATS its gate and requires the plant to be
admitted, because a test that only ever sees red cannot tell a working gate from a broken one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdfc.evidence.fields import LabelRule, from_template
from cdfc.evidence.gates import adjudicate
from cdfc.evidence.graph import EdgeKind, NodeKind, build
from cdfc.evidence.proposal import MalformedProposal, parse
from cdfc.evidence.provisions import from_instrument
from cdfc.evidence.query import Standing, coverage, standing
from cdfc.evidence.run import run
from cdfc.evidence.vocabulary import Asks, EIdKind, FieldType, Refusal
from cdfc.qualify.instruments import InstrumentStore

FME = Path("fixtures/prescribed/"
           "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
PROPOSALS = Path("fixtures/evidence/fme-proposals.json")
INSTRUMENT = "statute-fm-regulations-2025"


@pytest.fixture(scope="module")
def evidence():
    return run(instrument_id=INSTRUMENT, template=FME, proposals=PROPOSALS)


# --- the flow ---------------------------------------------------------------------------------

def test_evidence__runs_end_to_end(evidence) -> None:
    assert len(evidence.provisions) == 1218
    assert len(evidence.fields) > 0
    assert evidence.graph.counts()["Rule"] == len(evidence.adjudication.admitted)


def test_evidence__every_planted_error_is_refused(evidence) -> None:
    caught, planted = evidence.adjudication.planted_caught()
    assert planted == 5, "the fixture must carry one plant per gate"
    assert caught == planted, "a plant that was admitted is a gate that did not run"


def test_evidence__each_gate_is_the_one_that_refused_its_own_plant(evidence) -> None:
    """Not merely 'something refused it'. The NAMED gate must be the one that fired."""
    by_plant = {v.proposal.planted.split(":")[0]: {g for g, _r, _d in v.refusals}
                for v in evidence.adjudication.refused if v.proposal.is_planted}
    for gate in ("G-QUOTE", "G-FIELD", "G-TYPE", "G-VOCAB", "G-XREF"):
        assert gate in by_plant, f"no plant exercises {gate}"
        assert gate in by_plant[gate], f"{gate}'s plant was refused by {by_plant[gate]}, not {gate}"


def test_evidence__no_genuine_proposal_is_refused(evidence) -> None:
    """Every quote and field ref in the fixture was verified before it was written. A refusal
    here is a FALSE refusal, which is the failure mode a gate cannot be allowed to have."""
    refused, _total = evidence.adjudication.genuine_refused()
    assert refused == 0, [
        (v.proposal.eid, v.refusals) for v in evidence.adjudication.refused
        if not v.proposal.is_planted
    ]


# --- the negative controls: defeat each gate, require the plant through -----------------------

def _parts():
    it = InstrumentStore().get(INSTRUMENT)
    return from_instrument(it), from_template(FME)


def _plant(tag: str):
    rows = json.loads(PROPOSALS.read_text(encoding="utf-8"))
    return next(r for r in rows if r.get("planted", "").startswith(tag))


@pytest.mark.parametrize(("tag", "reason"), [
    ("G-QUOTE", Refusal.QUOTE_NOT_VERBATIM),
    ("G-FIELD", Refusal.FIELD_NOT_IN_SURFACE),
    ("G-TYPE", Refusal.TYPE_MISMATCH),
    ("G-VOCAB", Refusal.TERM_NOT_IN_VOCABULARY),
    ("G-XREF", Refusal.XREF_UNRESOLVED),
])
def test_evidence__gate_refuses_with_the_named_reason(tag, reason) -> None:
    provs, flds = _parts()
    adj = adjudicate(parse([_plant(tag)]), provs, flds)
    assert reason in adj.verdicts[0].reasons, adj.verdicts[0].refusals


def test_evidence__a_defeated_quote_gate_admits_the_plant(monkeypatch) -> None:
    """NC-shaped: neuter G-QUOTE and the plant sails through. Proves the earlier red was G-QUOTE
    doing work rather than another gate happening to refuse the same row."""
    from cdfc.evidence import gates

    provs, flds = _parts()
    monkeypatch.setattr(gates, "g_quote", lambda p, pr: None)
    adj = gates.adjudicate(parse([_plant("G-QUOTE")]), provs, flds)
    assert adj.verdicts[0].admitted, "G-QUOTE's plant is refused by some OTHER gate too"


def test_evidence__a_defeated_vocab_gate_admits_the_plant(monkeypatch) -> None:
    from cdfc.evidence import gates

    provs, flds = _parts()
    monkeypatch.setattr(gates, "g_vocab", lambda p, f: None)
    adj = gates.adjudicate(parse([_plant("G-VOCAB")]), provs, flds)
    assert adj.verdicts[0].admitted


# --- the graph carries no refused claim -------------------------------------------------------

def test_evidence__refused_proposals_are_not_reachable_in_the_graph(evidence) -> None:
    """The load-bearing property: a query cannot return an ungrounded claim."""
    rules = {n.id for n in evidence.graph.by_kind(NodeKind.RULE)}
    assert len(rules) == len(evidence.adjudication.admitted)
    for v in evidence.adjudication.refused:
        assert not [e for e in evidence.graph.edges
                    if e.kind is EdgeKind.GOVERNS and e.dst == f"field:{v.proposal.field_ref}"
                    and e.src not in rules]


def test_evidence__a_dangling_xref_never_becomes_an_edge(evidence) -> None:
    known = {f"prov:{p.eid}" for p in evidence.provisions.provisions}
    for e in evidence.graph.edges:
        if e.kind in (EdgeKind.CITES, EdgeKind.REFERS_TO):
            assert e.dst in known, f"{e.dst} is an edge to a provision that does not exist"


# --- the declaration ---------------------------------------------------------------------------

def test_evidence__every_count_travels_with_its_denominator(evidence) -> None:
    for line in evidence.coverage.lines():
        if any(w in line for w in ("governed", "cited", "caught", "refused", "labelled")):
            assert " of " in line, f"a bare count: {line!r}"


def test_evidence__coordinate_eids_are_reported_as_not_durable(evidence) -> None:
    """The pinned corpus is flat text, so nothing is durably addressable. That must be VISIBLE:
    a rule stored against a coordinate breaks when the instrument is re-extracted."""
    assert evidence.provisions.eid_kind is EIdKind.COORDINATE
    assert evidence.coverage.provisions_durable == 0


def test_evidence__the_labelling_rule_changes_the_denominator_and_is_declared() -> None:
    """M-CEIL: the labelled population moves by a large factor with an unwritten convention.
    Both rules are available, the pinned one labels FIELDS, and the loose one labels ROWS."""
    adjacent = from_template(FME, rule=LabelRule.ADJACENT_LEFT)
    nearest = from_template(FME, rule=LabelRule.NEAREST_LEFT)
    assert len(nearest) > len(adjacent) * 3, "the loose rule must admit far more fields"

    # THE DISCRIMINATOR IS FIELDS-PER-LABEL, not the raw counts. A rule that names FIELDS gives
    # each one its own label; a rule that names ROWS hands one header to every column in the row.
    # N2 measured 1.2 under the pinned rule and 4.8 under the loose one.
    def per_label(fs) -> float:
        return len(fs) / len({f.label for f in fs.fields})

    assert per_label(adjacent) < 2.0, "the pinned rule must label fields, near one-to-one"
    assert per_label(nearest) > per_label(adjacent) * 2, (
        "the loose rule is supposed to reuse one row header across a whole row"
    )
    assert adjacent.label_rule is LabelRule.ADJACENT_LEFT


def test_evidence__attestation_fields_are_identified_and_never_filled(evidence) -> None:
    att = evidence.fields.attestations
    assert att, "the return does carry attestations; finding none means the classifier died"
    assert all(f.asks is Asks.ATTESTATION for f in att)


def test_evidence__enum_fields_carry_the_workbooks_own_vocabulary(evidence) -> None:
    """openpyxl alone drops the x14 namespace and finds no vocabularies at all -- a clean, empty
    and wrong answer. This asserts the raw-zip reader is the one in use."""
    enums = [f for f in evidence.fields.fields if f.type is FieldType.ENUM]
    assert enums, "no ENUM field: the x14 validation reader is not wired in"
    assert all(f.vocabulary for f in enums)


# --- the third standing state -------------------------------------------------------------------

def test_evidence__read_as_a_condition_is_distinct_from_ungoverned() -> None:
    """The spike's query reported a field as untouched when a rule named it without governing it.
    Two states could not express that, so it reported the wrong one."""
    provs, flds = _parts()
    target = next(f for f in flds.fields if f.type is FieldType.ENUM)
    row = {"eid": provs.provisions[0].eid, "quote": provs.provisions[0].text[:20].strip(),
           "kind": "definition"}
    adj = adjudicate(parse([row]), provs, flds)
    g = build(adj, provs, flds)
    assert standing(g, target.ref) is Standing.UNGOVERNED
    cov = coverage(g, adj, provs, flds)
    assert cov.fields_governed + cov.fields_read + cov.fields_ungoverned == len(flds)


# --- the loader decides nothing -------------------------------------------------------------------

def test_evidence__loader_refuses_a_shapeless_proposal() -> None:
    with pytest.raises(MalformedProposal):
        parse([{"eid": "p1", "quote": "x"}])
    with pytest.raises(MalformedProposal):
        parse([{"eid": "p1", "quote": "x", "kind": "not_a_kind"}])


def test_evidence__unlabelled_is_not_the_same_refusal_as_absent() -> None:
    """The defect an adversarial audit found in the spike, and then in this gate.

    `4. Investors!C6` EXISTS and is in the 3,747-cell surface; it carries no label under the
    pinned rule. The spike refused it as `field_not_in_surface` and the resulting count was
    published as the proposer's error rate -- a defect in our reader wearing the model's name.
    Two reasons, because a bad citation and a gap in what we can read have different remedies.
    """
    provs, flds = _parts()
    p = provs.provisions[10]
    base = {"eid": p.eid, "quote": p.text[:25].strip(), "kind": "disclosure"}

    real_but_unlabelled = "4. Investors!C6"
    assert real_but_unlabelled in flds.surface, "the fixture premise moved"
    assert flds.get(real_but_unlabelled) is None, "it is supposed to be unlabelled"

    adj = adjudicate(parse([{**base, "field": real_but_unlabelled}]), provs, flds)
    assert Refusal.FIELD_NOT_LABELLED in adj.verdicts[0].reasons

    adj2 = adjudicate(parse([{**base, "field": "1. Introduction!ZZ999"}]), provs, flds)
    assert Refusal.FIELD_NOT_IN_SURFACE in adj2.verdicts[0].reasons


def test_evidence__no_refusal_reason_says_something_false_about_the_surface() -> None:
    """A refusal string that misdescribes the artifact is worse than no refusal: it sends the
    reader to fix the wrong thing. Every `field_not_in_surface` must be genuinely absent."""
    provs, flds = _parts()
    p = provs.provisions[10]
    for ref in sorted(flds.surface)[:40]:
        adj = adjudicate(
            parse([{"eid": p.eid, "quote": p.text[:25].strip(), "kind": "disclosure",
                    "field": ref}]), provs, flds)
        assert Refusal.FIELD_NOT_IN_SURFACE not in adj.verdicts[0].reasons, (
            f"{ref} is in the surface, yet a gate said it is not"
        )


def test_cell_string__only_the_last_bang_is_the_delimiter() -> None:
    """A sheet name may contain `!`; a reference may not. Found by the A1 adversarial audit.

    `Anchor.parse` right-split and was correct; eighteen call sites left-split and were not, so
    the anchor and the rest of the codebase disagreed about which `!` was the delimiter — on
    exactly the path A1 exists to serve, a buyer's own workbook. `ci/no-left-split-on-cell.sh`
    keeps the call sites honest; this pins the behaviour they must agree on.
    """
    from cdfc.schema.anchor import Anchor

    rendered = Anchor.cell("Bad!Name", "A1").render()
    assert rendered == "Bad!Name!A1", "render must stay byte-identical to the old f-string"
    assert Anchor.parse(rendered).table == "Bad!Name"
    assert rendered.rsplit("!", 1)[0] == "Bad!Name", "right-split is the correct one"
    assert rendered.split("!", 1)[0] == "Bad", "and left-split is the wrong one, demonstrably"


def test_cell_string__a_bang_sheet_survives_the_real_field_surface(tmp_path) -> None:
    """Not a string exercise: a workbook openpyxl accepts, through the shipped surface reader."""
    from openpyxl import Workbook
    from openpyxl.styles import Protection
    from openpyxl.worksheet.protection import SheetProtection

    from cdfc.measure.p5_run import surface_for
    from cdfc.schema.anchor import Anchor

    p = tmp_path / "bang.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Bad!Name"
    ws["A1"] = "Label"
    for row in ws.iter_rows(min_row=1, max_row=2, min_col=1, max_col=2):
        for c in row:
            c.protection = Protection(locked=False)
    ws.protection = SheetProtection(sheet=True)
    wb.save(p)

    refs = surface_for(p)[1]
    assert refs, "the fixture must yield a field surface or it tests nothing"
    for r in refs:
        assert Anchor.parse(r).table == "Bad!Name", f"{r} parsed to the wrong sheet"
        assert r.rsplit("!", 1)[0] == Anchor.parse(r).table


def test_cell_string__reads_resolves_a_bang_sheet_and_flips_when_split_wrongly() -> None:
    """The guard NC-A37 expects to FLIP. Without one that flips, the control proves nothing.

    `probes/qualify._reads` turns a cell string into a CEL path and asks whether a relation reads
    it. Under the correct right-split `Bad!Name!A1` yields `bad_name.r1.ca`; under the left-split
    the ref becomes `Name!A1`, `cel_path` raises `ValueError`, `_reads` swallows it and answers
    **False** — a relation silently reported as not reading a cell it does read.
    """
    from cdfc.predicates.harvest import cel_path
    from cdfc.probes.qualify import _reads
    from cdfc.probes.relations.registry import RelationSpec

    cell = "Bad!Name!A1"
    path = cel_path(*cell.rsplit("!", 1))
    spec = RelationSpec(
        id="R-BANG", title="a relation over a sheet whose name contains a bang",
        necessity="EXPECTED", inputs="FILING_ONLY",
        precondition="true", expr=f"filing.{path}.v > 0", witness=f"[filing.{path}.__cell__]",
        bases=frozenset(), evidence="the A1 adversarial audit", reviewed_by=("audit",),
        reviewed_at="2026-08-20", claims_fault_classes=(),
    )
    assert _reads(spec, cell) is True, (
        "the relation's expression literally contains this cell's path; answering False means "
        "the cell string was split on the wrong `!`"
    )
