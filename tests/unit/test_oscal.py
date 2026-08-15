"""P11-B3 — the projections, and the one case a naive projector gets wrong in the worst direction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest.projections import NotRepresentable, project_oscal, project_rocrate  # noqa: E402
from cdfc.attest.projections.oscal import (  # noqa: E402
    ALL_STATES,
    EXCLUDED_ONLY,
    LOSSY_NOTICE,
    NORMATIVE_URI,
    OBSERVED,
    SETTLED,
)
from cdfc.attest.projections.rocrate import BlobNotCarried  # noqa: E402
from cdfc.verdict.states import ItemState  # noqa: E402
from tests.contract.attest_fixtures import sample_statement  # noqa: E402

CELLS = [
    {"stable_key": "S!A1", "state": "PASS", "reason": None},
    {"stable_key": "S!A2", "state": "FAIL", "reason": None},
    {"stable_key": "S!A3", "state": "NOT_RUN", "reason": "not_run.deactivated"},
    {"stable_key": "S!A4", "state": "INDETERMINATE", "reason": "indeterminate.tolerance"},
    {"stable_key": "S!A5", "state": "NO_PREDICATE", "reason": "no_predicate.none_bound"},
    {"stable_key": "S!A6", "state": "ERROR", "reason": "error.predicate_raised"},
    {"stable_key": "S!A7", "state": "OUT_OF_SCOPE", "reason": "out_of_scope.not_applicable"},
    {"stable_key": "S!A8", "state": "INFORMATIONAL", "reason": None},
]


def _result(doc: dict) -> dict:
    return doc["assessment-results"]["results"][0]


def test_oscal__invalid_raises_not_representable(tmp_path: Path) -> None:
    """**And no file is written.**

    An OSCAL Assessment Result with zero findings is schema-valid and means nothing in particular,
    so a projector that emitted one for an `INVALID` run would publish a clean assurance document
    for a run in which we could not demonstrate our instrument was working.
    """
    before = set(tmp_path.iterdir())
    with pytest.raises(NotRepresentable) as e:
        project_oscal(sample_statement(invalid=True), cells=CELLS)
    assert "closed two-value enum" in str(e.value)
    assert "reads as *checked and nothing found*" in str(e.value)
    assert set(tmp_path.iterdir()) == before, "a file was written on the refusal path"


def test_oscal__there_is_no_flag_to_emit_it_anyway() -> None:
    """**The absence of a flag is the substance of the ruling.** A flag is what somebody sets when
    a pipeline is failing and the deadline is Friday."""
    import inspect

    sig = inspect.signature(project_oscal)
    assert set(sig.parameters) == {"statement", "cells"}, (
        f"project_oscal grew a parameter: {sorted(sig.parameters)}. If one of them can make an "
        "INVALID run project, the ruling is a preference."
    )
    src = Path(__import__("cdfc.attest.projections.oscal", fromlist=["x"]).__file__).read_text()
    assert "there is no flag to emit it anyway" in src.lower()


def test_oscal__every_unsettled_state_becomes_an_observation_and_an_exclusion() -> None:
    """Table-driven over all four unsettled states. **No finding is emitted for any of them.**

    OSCAL's `finding-target.status.state` is `{satisfied, not-satisfied}` and has no third member
    meaning *we did not look*. Mapping `NOT_RUN` onto either one would be inventing a verdict.
    """
    r = _result(project_oscal(sample_statement(), cells=CELLS))
    finding_ids = {f["title"] for f in r["findings"]}
    observed_ids = {o["title"] for o in r["observations"]}
    excluded_ids = {e["control-id"] for e in r["reviewed-controls"]["control-selections"][0]["exclude-controls"]}

    assert finding_ids == {"S!A1", "S!A2"}, "a finding was emitted for a cell we did not settle"
    for cell in CELLS:
        key, state = cell["stable_key"], cell["state"]
        if state in SETTLED:
            continue
        assert key not in finding_ids, f"{state} produced a finding"
        assert key in excluded_ids, f"{state} produced no exclusion"
        if state in OBSERVED:
            assert key in observed_ids, f"{state} produced no observation"
        else:
            assert state in EXCLUDED_ONLY


def test_oscal__the_projection_is_total_over_the_item_states() -> None:
    """**Eight states in, eight states mapped.** A state with no rule would be silently dropped,
    and a dropped cell is a cell this document implies was checked."""
    ours = {str(s) for s in ItemState}
    assert ALL_STATES == ours, f"unmapped states: {sorted(ours - ALL_STATES)}"
    with pytest.raises(NotRepresentable) as e:
        project_oscal(sample_statement(), cells=[{"stable_key": "X", "state": "NEW", "reason": None}])
    assert "no projection rule" in str(e.value)


def test_oscal__projection_never_gains_a_state() -> None:
    """The projection's state set is a **function** of ours; a projection state with no pre-image
    fails. Gaining one would mean the projection can say something the attestation cannot."""
    r = _result(project_oscal(sample_statement(), cells=CELLS))
    emitted = {f["target"]["status"]["state"] for f in r["findings"]}
    assert emitted <= set(SETTLED.values())
    assert set(SETTLED.values()) == {"satisfied", "not-satisfied"}


def test_oscal__lossy_prop_is_in_the_file() -> None:
    """**In the file, not in a README.** The reader who most needs the warning is the one who never
    saw the attestation."""
    doc = project_oscal(sample_statement(), cells=CELLS)
    props = {p["name"]: p["value"] for p in doc["assessment-results"]["metadata"]["props"]}
    assert props["lossy"] == "true"
    assert props["normative-artifact"] == NORMATIVE_URI
    assert "acting on less than the evidence" in props["lossy-notice"]
    assert LOSSY_NOTICE in _result(doc)["description"]


def test_oscal__valid_run_projects_and_declares_its_loss() -> None:
    """NC-A20's positive control. Without it, a projector that refused everything scores perfectly."""
    doc = project_oscal(sample_statement(), cells=CELLS)
    assert _result(doc)["findings"], "a VALID run produced no finding at all"
    assert doc["assessment-results"]["metadata"]["props"]


def test_oscal__identifiers_are_derived_and_not_generated() -> None:
    """`uuid4()` would make every projection differ from its own re-derivation, and both
    projections are in `make determinism`'s comparison set — because a lossy projection that is
    also non-deterministic is a second artifact a consumer could diff and mis-read."""
    a = project_oscal(sample_statement(), cells=CELLS)
    b = project_oscal(sample_statement(), cells=CELLS)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

    # **OVER THE AST, not over the text.** The first version scanned the source for `uuid4` and
    # found it — in the docstring explaining why `uuid4()` must not be used. That is the sixth
    # time in this build that a check has been defeated by prose describing the thing it checks
    # for, and every time the cure is the same: walk the structure. A scan a comment can turn red
    # is a scan a comment can also turn green.
    import ast

    import cdfc.attest.projections.oscal as m
    import cdfc.attest.projections.rocrate as r

    for module in (m, r):
        tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
        called = {
            getattr(n.func, "attr", "") or getattr(n.func, "id", "")
            for n in ast.walk(tree) if isinstance(n, ast.Call)
        }
        assert not (called & {"uuid1", "uuid4", "random", "token_hex", "now", "time"}), (
            f"{Path(module.__file__).name} generates an identifier or reads a clock: "
            f"{sorted(called & {'uuid1', 'uuid4', 'random', 'token_hex', 'now', 'time'})}"
        )


# --- the crate ---------------------------------------------------------------------------------


def test_rocrate__every_referenced_blob_is_present(tmp_path: Path) -> None:
    """The crate is self-contained or it fails. A crate naming a blob it does not carry is a
    bibliography: the recipient cannot open the thing the claim rests on."""
    blob = tmp_path / "filing.xlsx"
    blob.write_bytes(b"PK\x03\x04 content")
    crate = project_rocrate(sample_statement(), {"filing.xlsx": blob})
    files = [e for e in crate["@graph"] if e.get("@type") == "File"]
    assert len(files) == 1 and files[0]["sha256"]

    with pytest.raises(BlobNotCarried) as e:
        project_rocrate(sample_statement(), {"missing.xlsx": tmp_path / "nope.xlsx"})
    assert "bibliography" in str(e.value)


def test_rocrate__declares_its_own_lossiness(tmp_path: Path) -> None:
    blob = tmp_path / "f.xlsx"
    blob.write_bytes(b"x")
    crate = project_rocrate(sample_statement(), {"f.xlsx": blob})
    root = next(e for e in crate["@graph"] if e["@id"] == "./")
    assert "LOSSY PROJECTION" in root["description"]
    assert root["isBasedOn"]["@id"] == NORMATIVE_URI


def test_rocrate__can_carry_an_invalid_run_and_oscal_cannot() -> None:
    """**The two projections differ here on purpose.**

    A crate is a container for evidence; evidence that the instrument could not be demonstrated is
    still evidence. The OSCAL refusal is about a form whose vocabulary cannot say *we did not
    look* — not about `INVALID` being unmentionable.
    """
    crate = project_rocrate(sample_statement(invalid=True), {})
    root = next(e for e in crate["@graph"] if e["@id"] == "./")
    assert root["runState"] == "INVALID"
    with pytest.raises(NotRepresentable):
        project_oscal(sample_statement(invalid=True), cells=CELLS)


def test_projections__are_byte_identical_across_calls(tmp_path: Path) -> None:
    """`test_det__projections_are_byte_identical`'s content, asserted here so a regression is
    caught by the unit suite as well as by `make determinism`."""
    from cdfc.canon import canonical_json

    blob = tmp_path / "f.xlsx"
    blob.write_bytes(b"x")
    for build in (
        lambda: project_oscal(sample_statement(), cells=CELLS),
        lambda: project_rocrate(sample_statement(), {"f.xlsx": blob}),
    ):
        assert canonical_json(build()) == canonical_json(build())
