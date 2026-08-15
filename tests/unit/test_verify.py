"""P11-B2 — `verify`'s own guards, and the one that has to be a walk over the code."""

from __future__ import annotations

import ast
import base64
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest import verify as V  # noqa: E402
from cdfc.attest.verify import BlobStore, Diff, VerifyResult, first_diffs  # noqa: E402


def test_v__verify_never_calls_sign() -> None:
    """**NC-A19, and a comment saying so is not the same as it being so.**

    A tool that re-signed to compare signatures would report a mismatch whenever the key differed
    and a match whenever it did not — and neither answer is about the report. This walks the module
    and asserts no signing function is called, and that the signing module is not even imported for
    a name that could be used later.
    """
    tree = ast.parse(Path(V.__file__).read_text(encoding="utf-8"))
    called = {
        getattr(n.func, "attr", "") or getattr(n.func, "id", "")
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
    }
    assert "sign" not in called, "verify calls a signing function"
    imported = {
        a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names
    }
    assert "ed25519" not in imported, (
        "verify imports the signing primitive. It needs `dsse.verify` and nothing else; importing "
        "the key operations puts them one keystroke from being used."
    )
    assert "sign" not in imported


def test_v__the_two_facts_are_separate_fields() -> None:
    """A caller wanting one number is asking a question this tool refuses to answer."""
    import dataclasses

    names = {f.name for f in dataclasses.fields(VerifyResult)}
    assert {"reproduced", "signature_valid", "diffs", "manifest_pins_checked"} <= names
    row = VerifyResult(
        reproduced=False, diffs=(), signature_valid=True, manifest_pins_checked=()
    ).as_row()
    assert row["reproduced"] is False and row["signature_valid"] is True, (
        "the two must be independently readable — a changed report and a changed key are "
        "different events"
    )


def test_v__signature_valid_is_tri_state() -> None:
    """`None` is not `False`. *We checked and it does not match* and *there is nothing here to
    check against* are different facts about the world."""
    from cdfc.attest import dsse

    env = dsse.sign(b'{"a":1}').as_obj()
    assert dsse.verify(env) is True
    env["signatures"][0].pop("publicKey")
    assert dsse.verify(env) is None, "a missing key must not read as an invalid signature"


def test_v__diffs_name_the_artifact_and_the_offset() -> None:
    """A reproduction check that answers only *no* tells the reader that something moved and
    nothing about what."""
    diffs = first_diffs("payload", b'{"a":1,"b":2}', b'{"a":1,"b":9}')
    assert len(diffs) == 1
    d = diffs[0]
    assert d.artifact == "payload" and d.byte_offset == 11
    assert "2" in d.expected and "9" in d.actual
    assert "byte 11" in d.render()


def test_v__identical_bytes_produce_no_diff() -> None:
    """The admission-side twin: without it, a differ that reports a diff for everything passes."""
    assert first_diffs("payload", b"same", b"same") == ()


def test_v__a_truncated_payload_names_where_it_ran_out_and_what_was_lost() -> None:
    """A truncated payload shares a prefix and differs in nothing until it ends.

    The diff is at the offset where the shorter one stopped, and it QUOTES the content that is
    missing — which is more useful than reporting two lengths, and is what the walker does.
    """
    diffs = first_diffs("payload", b"abcdef", b"abc")
    assert diffs and diffs[0].byte_offset == 3
    assert diffs[0].expected == "def" and diffs[0].actual == ""

    # And the pure length case with no readable content still reports SOMETHING rather than
    # silently returning no diffs, which would read as `reproduced`.
    assert first_diffs("payload", b"abc", b"abc") == ()


def test_v__the_blob_store_is_content_addressed(tmp_path: Path) -> None:
    """**Never name-addressed.** A store keyed on filename resolves `filing.xlsx` to whichever file
    currently has that name, which is exactly the substitution `verify` exists to detect."""
    import hashlib

    a = tmp_path / "one.xlsx"
    a.write_bytes(b"PK\x03\x04 one")
    store = BlobStore(roots=[tmp_path])
    digest = hashlib.sha256(a.read_bytes()).hexdigest()
    assert store.get(digest) == a

    # Rewrite the SAME NAME with different content: the old digest must no longer resolve.
    a.write_bytes(b"PK\x03\x04 two")
    fresh = BlobStore(roots=[tmp_path])
    with pytest.raises(V.BlobMissing) as e:
        fresh.get(digest)
    assert "not resolved by name instead" in str(e.value)


def test_v__the_pins_are_the_statement_module_s_list() -> None:
    """A pin `verify` checks and the schema does not name is a pin nobody declared, and the other
    way round is a pin nobody checks. One list."""
    from cdfc.attest.statement import MANIFEST_PINS, MANIFEST_RUN_INPUTS

    src = Path(V.__file__).read_text(encoding="utf-8")
    assert "MANIFEST_PINS" in src and "MANIFEST_RUN_INPUTS" in src
    assert len(MANIFEST_PINS) + len(MANIFEST_RUN_INPUTS) == 10


def test_v__an_incomplete_manifest_refuses_rather_than_re_running(tmp_path: Path) -> None:
    """A re-derivation against an incomplete manifest would be a re-run, not a check."""
    from cdfc.attest import dsse
    from tests.contract.attest_fixtures import sample_statement

    obj = sample_statement().as_obj()
    del obj["predicate"]["manifest"]["probe_seed"]
    payload = json.dumps(obj).encode("utf-8")
    env = dsse.sign(payload).as_obj()
    path = tmp_path / "attestation.json"
    path.write_text(json.dumps(env), encoding="utf-8")

    result = V.verify(path, BlobStore(roots=[tmp_path]), repo=REPO)
    assert result.reproduced is False
    assert "probe_seed" in result.detail
    assert "not a check" in result.detail
    assert result.signature_valid is True, (
        "the signature is a fact about the file on disk and is taken BEFORE anything is re-run, "
        "so a re-derivation failure cannot change it"
    )


def test_v__the_non_determinism_document_lists_six_and_six() -> None:
    """Exit criterion 8. **An enumeration that was complete until someone measured something is
    the standing hazard**, so the count is asserted rather than assumed."""
    text = (REPO / "docs" / "NON-DETERMINISM.md").read_text(encoding="utf-8")
    import re as _re

    # The numbered rows of the SIX-SOURCE table specifically. A looser filter also matched a row
    # of the byte-identity table below it and reported seven — a count about the wrong table is
    # exactly the defect shape this project keeps finding.
    rows = [ln for ln in text.splitlines() if _re.match(r"^\| \*\*\d+\*\* \|", ln)]
    assert len(rows) == 6, f"the document lists {len(rows)} sources, not six"
    for token in ("register", "wall clock", "iteration order", "floating point",
                  "probe seed", "durations we measured ourselves"):
        assert token in text, f"the enumeration does not name {token!r}"
    assert "perf_counter" in text, "the sixth source's mechanism is not named"
    assert "NOT VERIFIED IN THIS BUILD" in text, (
        "the second-machine boundary must be on the document's face, not inferred from the clone"
    )
