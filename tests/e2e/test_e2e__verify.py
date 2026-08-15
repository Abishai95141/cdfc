"""P11-B2 — the four end-to-end flows. **The programme's acceptance test.**

*If it does not reproduce, it does not ship.*

Each flow runs the real pipeline against a real workbook, signs a real envelope and verifies it.
Nothing here is a fixture of a statement; the point of an end-to-end test is that every layer under
it was exercised by the same command a user would run.
"""

from __future__ import annotations

import base64
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest.verify import BlobStore, verify  # noqa: E402
from cdfc.measure.p10_run import run_filing  # noqa: E402
from cdfc.measure.p11_attest import statement_for, write  # noqa: E402
from cdfc.measure.p5_run import FME, TEMPLATE_COMPUTED  # noqa: E402

TIME_VERIFIED = "2026-08-14T00:00:00Z"
FIXTURES = REPO / "fixtures"


@pytest.fixture(scope="module")
def attested(tmp_path_factory) -> tuple[Path, Path]:
    """`(attestation path, out dir)` for one real, signed run of the clean FME fill."""
    out = tmp_path_factory.mktemp("runs")
    result = run_filing(TEMPLATE_COMPUTED)
    statement = statement_for(result, filing=TEMPLATE_COMPUTED, time_verified=TIME_VERIFIED)
    return write(statement, out), out


def test_e2e__VERIFY_byte_identical(attested) -> None:
    """**E2E-VERIFY.** The payload re-derives byte for byte and the stored signature is valid.

    Both facts, and both green. This is the flow the whole phase exists for.
    """
    path, _out = attested
    result = verify(path, BlobStore(roots=[FIXTURES]), repo=REPO)

    assert result.reproduced is True, result.detail + "\n" + "\n".join(
        d.render() for d in result.diffs
    )
    assert result.signature_valid is True
    assert result.diffs == ()
    assert len(result.manifest_pins_checked) == 10, (
        "eight pins plus the two run-level inputs; a pin the schema names and verify does not "
        "check is a pin nobody checks"
    )


def test_e2e__TAMPER_names_the_artifact_it_cannot_find(attested, tmp_path: Path) -> None:
    """**E2E-TAMPER.** Flip one byte of the filing and re-verify: **a named diff, not a boolean.**

    From `verify`'s side a tampered filing is a filing whose digest is not in the store — because
    the store is content-addressed, so the attestation's subject simply is not there. That is the
    strongest available answer and it is reported as one: the digest that was attested, and the
    fact that no file carries it.
    """
    path, _out = attested
    tampered_dir = tmp_path / "blobs"
    tampered_dir.mkdir()
    raw = bytearray(TEMPLATE_COMPUTED.read_bytes())
    raw[len(raw) // 2] ^= 0x01
    (tampered_dir / TEMPLATE_COMPUTED.name).write_bytes(bytes(raw))
    shutil.copy2(FME, tampered_dir / FME.name)

    result = verify(path, BlobStore(roots=[tampered_dir]), repo=REPO)

    assert result.reproduced is False
    assert result.diffs, "a refusal with no named diff tells a reader nothing they can act on"
    diff = result.diffs[0]
    assert diff.artifact == "filing blob"
    assert diff.expected.startswith("sha256:")
    assert diff.actual == "ABSENT from the blob store"
    assert "this is not the artifact that was checked" in result.detail

    # And the signature is STILL valid, because the envelope was not touched. Two facts.
    assert result.signature_valid is True, (
        "tampering with the FILING must not change the answer about the SIGNATURE — they are "
        "different events and the tool has to be able to say which one happened"
    )


def test_e2e__TAMPER_ATTEST_separates_signature_from_payload(attested, tmp_path: Path) -> None:
    """**E2E-TAMPER-ATTEST.** Flip one byte of `attestation.json`: `signature_valid: false` **and**
    `reproduced: false`, reported as two separate facts.

    This is the flow that would be indistinguishable from a key rotation if `verify` re-signed.
    """
    path, _out = attested
    envelope = json.loads(path.read_text(encoding="utf-8"))
    payload = bytearray(base64.b64decode(envelope["payload"]))
    # Move a digit inside the settled count — a change to what the statement SAYS, not to its shape.
    marker = b'"settled":'
    at = payload.find(marker)
    assert at > 0, "the payload does not carry a settled count; this flow is tampering with nothing"
    payload[at + len(marker)] = ord("9") if payload[at + len(marker)] != ord("9") else ord("8")
    envelope["payload"] = base64.b64encode(bytes(payload)).decode("ascii")

    tampered = tmp_path / "attestation.json"
    tampered.write_text(json.dumps(envelope), encoding="utf-8")
    result = verify(tampered, BlobStore(roots=[FIXTURES]), repo=REPO)

    assert result.signature_valid is False, "the stored signature is over the ORIGINAL bytes"
    assert result.reproduced is False, "and the tampered payload does not re-derive"
    assert result.diffs and result.diffs[0].artifact == "attestation payload"
    assert result.diffs[0].byte_offset > 0
    row = result.as_row()
    assert row["signature_valid"] is False and row["reproduced"] is False, (
        "the two facts must be separately readable — a caller wanting one number is asking a "
        "question this tool refuses to answer"
    )


def test_e2e__INVALID_shows_no_fraction_of_any_kind(tmp_path: Path) -> None:
    """**E2E-INVALID.** An `INVALID` run: `settledFraction` is **present**, is `null`, and an
    omission **fails validation**. All three legs of F24's ruling, on a real run.
    """
    import dataclasses

    import jsonschema

    from cdfc.measure.p10_run import all_predicates, population
    from tools.attest_validate import schema

    # The whole harvest cannot demonstrate its own liveness — 315 of 348 carry no stored kill case
    # — so this run is INVALID(WHOLESALE_INAPPLICABILITY). A real cause, not a constructed one.
    result = run_filing(TEMPLATE_COMPUTED, predicates=all_predicates())
    assert result.run_state == "INVALID", "this fixture no longer produces an INVALID run"
    assert result.fraction is None

    statement = statement_for(result, filing=TEMPLATE_COMPUTED, time_verified=TIME_VERIFIED)
    obj = statement.as_obj()
    pred = obj["predicate"]

    assert "settledFraction" in pred and pred["settledFraction"] is None    # present, and null
    assert "verdict" in pred and pred["verdict"] is None
    # `canary_silent` is present, and it is not alone: over all 348 harvested candidates one also
    # RAISES, so the cause set is two. That is a fact about the pre-gate fixture set rather than
    # about this flow, and P10's `test_liveness__only_cause_is_canary_silent` is the test that
    # asserts EXACTLY `{canary_silent}` — over the population where that claim is the point.
    assert "invalid.canary_silent" in pred["invalidCauses"]
    assert all(c.startswith("invalid.") for c in pred["invalidCauses"])
    jsonschema.validate(instance=obj, schema=schema())

    omitted = json.loads(json.dumps(obj))
    del omitted["predicate"]["settledFraction"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=omitted, schema=schema())

    # **`scope` STAYS POPULATED on an INVALID run, and that is the distinction, not a leak.**
    #
    # An earlier version of this test asserted `fieldSurface is None` here, on the reasoning that a
    # run declaring no coverage should declare nothing. That is wrong, and the schema is right:
    # `scope` says what the run LOOKED AT, and the field surface is 3,747 cells of the pinned
    # template whether or not the instrument was demonstrated on this filing. Suppressing a fact we
    # have would be the mirror image of the defect this field exists to prevent.
    #
    # What must be null is the CLAIM — the fraction and the verdict — and it is. `scope` is the
    # predicate's top-level object precisely because the first thing the document says is what it
    # looked at, and that sentence is as true of an INVALID run as of a VALID one.
    assert pred["scope"]["fieldSurface"] == 3747
    assert pred["scope"]["runId"], "the run is still identified, so a reader can open it"
    assert pred["settledFraction"] is None and pred["verdict"] is None
    path = write(statement, tmp_path)
    assert b'"settledFraction":null' in path.parent.joinpath("statement.json").read_bytes()


def test_e2e__the_run_and_the_attestation_agree_on_the_run_id(attested) -> None:
    """The attestation is written beside `run.jsonl` under the same run id, so a reader following
    one artifact finds the others. An attestation nobody can join to its run is a claim about a
    run nobody can open."""
    path, out = attested
    run_id = path.parent.name
    payload = json.loads(base64.b64decode(json.loads(path.read_text())["payload"]))
    assert payload["predicate"]["scope"]["runId"] == run_id
    assert (out / run_id / "statement.json").is_file()
