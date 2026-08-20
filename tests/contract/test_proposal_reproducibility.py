"""THE MODEL IS NOT REPRODUCIBLE. The RUN must be anyway.

Measured 20 Aug 2026: two runs of `tools/e2e_matrix.py` over identical inputs, at
`temperature=0`, on `deepseek-v4-flash`:

    ALR_V2_3        9 proposals  ->  2
    ITFS_Monthly   11            ->  0
    AL_monthly      0            ->  10
    Quarterly_CMI  19            ->  42

Nothing in this repository can make a reasoning model's sampling deterministic, and a test that
claimed to would be worse than the non-determinism. What CAN hold — and what these tests pin — is
that **generation is a BUILD step whose output is content-addressed**, so a run that names a
proposal digest re-derives the same adjudication for ever.

This is exactly how an instrument is pinned. The model moves; the artefact does not.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from cdfc.evidence.fields import from_template, select_rule
from cdfc.evidence.gates import adjudicate
from cdfc.evidence.proposal import load
from cdfc.evidence.provisions import from_divisions, from_instrument
from cdfc.qualify.instruments import InstrumentStore

REPO = Path(__file__).resolve().parents[2]
PROPOSALS = REPO / "fixtures/evidence/fme-proposals-generated.json"
TEMPLATE = REPO / ("fixtures/prescribed/"
                   "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
INSTRUMENT = "statute-fm-regulations-2025"

pytestmark = pytest.mark.skipif(not PROPOSALS.is_file(), reason="no pinned proposal set")


def _adjudicate():
    it = InstrumentStore().get(INSTRUMENT)
    fs = from_template(TEMPLATE, rule=select_rule(TEMPLATE))
    props = load(PROPOSALS)
    known = {p.eid for p in from_divisions(it, only_with="shall").provisions}
    pv = (from_divisions(it, only_with="shall") if any(p.eid in known for p in props.proposals)
          else from_instrument(it, only_with="shall"))
    return adjudicate(props, pv, fs)


def test_repro__the_same_pinned_proposals_adjudicate_identically() -> None:
    """Twice over the same artefact. If this ever fails, the GATES became non-deterministic."""
    a, b = _adjudicate(), _adjudicate()
    assert len(a.admitted) == len(b.admitted), "the admitted count moved between two runs"
    assert len(a.refused) == len(b.refused)
    key = lambda adj: sorted((v.proposal.eid, v.proposal.field_ref or "") for v in adj.admitted)
    assert key(a) == key(b), (
        "the SAME proposal set admitted a different set of rules on a second run. The gates are "
        "deterministic by construction, so this is a defect in them, not in the model.")


def test_repro__the_proposal_set_carries_its_provenance() -> None:
    """A pinned artefact nobody can attribute is a pinned artefact nobody can re-derive."""
    side = PROPOSALS.with_suffix(".provenance.json")
    assert side.is_file(), (
        f"{PROPOSALS.name} has no provenance sidecar. Regenerate with tools/gen_proposals.py, "
        "which writes one naming the model, the instrument, the template and the prompt digest.")
    p = json.loads(side.read_text(encoding="utf-8"))
    for k in ("proposals_sha256", "model", "instrument_sha256", "template_sha256",
              "prompt_sha256", "addressing", "reproducible"):
        assert k in p, f"the provenance sidecar does not record {k!r}"
    assert p["reproducible"] is False, (
        "the sidecar claims the generation is reproducible. It is not, and saying so is the one "
        "thing this file exists to prevent.")


def test_repro__the_digest_in_the_sidecar_IS_the_bytes_on_disk() -> None:
    """A recorded digest that does not match the file is worse than no digest at all."""
    side = PROPOSALS.with_suffix(".provenance.json")
    if not side.is_file():
        pytest.skip("no sidecar")
    recorded = json.loads(side.read_text(encoding="utf-8"))["proposals_sha256"]
    actual = hashlib.sha256(PROPOSALS.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    assert recorded == actual, (
        f"the sidecar records {recorded[:16]}… and the file hashes to {actual[:16]}…. The "
        "proposals were edited after they were pinned.")
