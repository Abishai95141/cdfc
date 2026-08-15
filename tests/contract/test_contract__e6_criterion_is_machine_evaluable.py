"""P12-B1 — **F30's repair, as a contract.** A criterion that does not parse does not lock.

The finding: `beats_baselines` was written early, hashed early, and committed inside the one
artifact whose whole value is that it was fixed before the model ran — **and it was prose.**
*"Marginal kill strictly greater than B0"* has three readings and the weakest is trivially
satisfiable, so the lock protected a *sentence* rather than a *criterion*.

Being early is not enough. The threshold must be **arithmetic a program reads**, and the refusal
must fire **before the write**, or the prose form is what gets hashed. Everything below is that
ordering, asserted on the committed document and on copies of it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment import prereg  # noqa: E402
from cdfc.experiment.criterion import (  # noqa: E402
    THRESHOLDS,
    CriterionIsProse,
    assert_machine_evaluable,
    parse_criterion,
)
from cdfc.experiment.parse import DISCARD_REASONS, Discard, UnlistedDiscardReason  # noqa: E402
from cdfc.experiment.prereg import (  # noqa: E402
    ALL_FIELDS,
    LockIsAppendOnly,
    UnknownLockField,
)
from cdfc.experiment.run import CandidateRecord  # noqa: E402

PREREG = REPO / "experiments" / "E6" / "PREREGISTRATION.md"


def _copy(tmp_path: Path, *, replace: tuple[str, str] | None = None) -> tuple[Path, Path]:
    """The committed document, copied into `tmp_path`. **Never `lock()` against the real tree.**

    `lock()` writes, and a test that wrote into `experiments/E6/` would either clobber the
    committed lock or pass only on a machine where it had already been clobbered.
    """
    text = PREREG.read_text(encoding="utf-8")
    if replace is not None:
        old, new = replace
        assert old in text, f"the fixture's anchor {old!r} is not in the document"
        text = text.replace(old, new)
    tmp_path.mkdir(parents=True, exist_ok=True)
    doc = tmp_path / "PREREGISTRATION.md"
    doc.write_text(text, encoding="utf-8")
    return doc, tmp_path / "preregistration.lock.json"


def test_contract__preregistration_criterion_is_machine_evaluable() -> None:
    """The committed document parses, and **every threshold equals the constant it names.**

    A document and a program that disagree about a threshold are two gates with nobody having
    chosen which is real — and the disagreement resolves silently in favour of the code, because
    the code is the one that runs and the document is the one a reader checks.
    """
    import importlib

    declared = assert_machine_evaluable(PREREG)
    assert set(declared) == set(THRESHOLDS), (
        "the parsed block and the threshold registry differ, so one of the two directions of the "
        "check is scanning a set the other does not"
    )
    for name, (module_name, attr) in THRESHOLDS.items():
        actual = getattr(importlib.import_module(module_name), attr)
        assert declared[name] == actual, f"{name}: document {declared[name]}, code {actual}"
        assert isinstance(actual, int) and not isinstance(actual, bool)


def test_contract__a_prose_threshold_does_not_lock(tmp_path: Path) -> None:
    """**The refusal precedes the write, and that ordering is the whole repair.**

    If `lock()` wrote first and validated after, the prose criterion would already be hashed — and
    `h0` can never move, so the experiment's one immutable artifact would be immutably wrong. The
    second assertion is therefore the load-bearing one: *no lock file exists*.
    """
    doc, lock_path = _copy(tmp_path, replace=("RETAIN1 = 6", "RETAIN1 = at least six"))

    with pytest.raises(CriterionIsProse) as e:
        prereg.lock(doc, lock_path, committed_at="2026-08-15")

    assert "RETAIN1" in str(e.value) and "at least six" in str(e.value)
    assert not lock_path.exists(), (
        "a lock was written for a criterion that does not parse. The prose form is now hashed, and "
        "h0 cannot move — the experiment would run against a threshold with three readings."
    )


def test_contract__a_threshold_only_in_code_is_caught(tmp_path: Path) -> None:
    """The other direction: a constant the document never mentions is **a threshold outside the
    lock**, editable without touching the hashed file.

    This is the direction that would have caught F30's own shape — `MARGINAL_FLOOR_NUM` and
    `MARGINAL_FLOOR_DEN` did not exist when the prose was written, so a one-directional check
    would have passed on a document that stated no floor at all.
    """
    doc, lock_path = _copy(tmp_path, replace=("RETAIN2 = 12\n", ""))

    with pytest.raises(CriterionIsProse) as e:
        prereg.lock(doc, lock_path, committed_at="2026-08-15")

    assert "RETAIN2" in str(e.value), "the refusal must NAME the missing threshold"
    assert "only in code" in str(e.value)
    assert not lock_path.exists()

    # And the symmetric half: a threshold the document declares that no pure function reads.
    extra_doc, extra_lock = _copy(
        tmp_path / "extra", replace=("RETAIN2 = 12", "RETAIN2 = 12\nTAU_PERCENT = 10")
    )
    with pytest.raises(CriterionIsProse) as e2:
        prereg.lock(extra_doc, extra_lock, committed_at="2026-08-15")
    assert "TAU_PERCENT" in str(e2.value)
    assert not extra_lock.exists()


def test_contract__six_discard_reasons() -> None:
    """Closed at six, and **an unlisted reason is rejected at write time.**

    An open reason set acquires an `other` bucket, and `other` is where the reasons nobody wanted to
    name go to stop being counted — while the funnel keeps printing the planned denominator.
    """
    assert len(DISCARD_REASONS) == 6
    assert len(set(DISCARD_REASONS)) == 6, "a duplicated reason makes the set smaller than it reads"

    with pytest.raises(UnlistedDiscardReason) as e:
        Discard("other", "the bucket that absorbs whatever nobody wanted to name")
    assert "other" in str(e.value) and "stop being counted" in str(e.value)

    # And the same closure one layer up, where the row is actually written.
    with pytest.raises(ValueError) as e2:
        CandidateRecord(
            candidate_sha256="c" * 64, obligation_ordinal=0, regime="correctness", draw_index=0,
            model_id="claude-opus-5", model_identity_reported=None,
            prompt_sha256="p" * 64, api_batch_id="batch-1", requested_at="2026-08-15T00:00:00Z",
            envelope=None, discard_reason="timeout",
        )
    assert "timeout" in str(e2.value)


def test_contract__lock_field_set_is_closed_and_append_only(tmp_path: Path) -> None:
    """The lock's field set is CLOSED, and a field that is present cannot be emptied.

    **A note on the second half.** `append()` carries a loop that raises `LockIsAppendOnly` when a
    field would be *removed*, and it is unreachable through the public API: `merged` starts as a
    copy of `current.fields`, so no argument can delete a key. The property is enforced by
    construction, and what a caller *can* attempt — blanking a field, which is how a removal is
    expressed through this signature — is what is asserted here. Asserting the unreachable branch
    would mean asserting nothing.
    """
    doc, lock_path = _copy(tmp_path)
    prereg.lock(doc, lock_path, committed_at="2026-08-15")
    before = lock_path.read_bytes()

    with pytest.raises(UnknownLockField) as e:
        prereg.append(lock_path, model_id="claude-opus-5")
    assert "model_id" in str(e.value) and "closed" in str(e.value)

    with pytest.raises(LockIsAppendOnly) as e2:
        prereg.append(lock_path, h0="")
    assert "APPEND-ONLY" in str(e2.value)

    assert lock_path.read_bytes() == before, (
        "the lock on disk changed under a refused append. The refusals must precede the write, or "
        "a rejected edit still lands."
    )

    # A key outside the closed set cannot arrive by editing the file either — `_read` refuses it,
    # so the closure is a property of the artifact rather than of the one function that writes it.
    raw = json.loads(lock_path.read_text(encoding="utf-8"))
    raw["reviewed_by"] = "nobody"
    lock_path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(UnknownLockField):
        prereg.append(lock_path, textsource_sha256="a" * 64)
    assert "reviewed_by" not in ALL_FIELDS


def test_contract__the_criterion_block_is_the_one_the_document_prints() -> None:
    """A guard against a vacuous parse: the block really is read out of the committed markdown.

    `parse_criterion` finds a fence and reads lines. If the fence moved or the block emptied, every
    assertion above would still pass on a document stating nothing — the shape that has already
    cost this build seven checks defeated by their own prose.
    """
    declared = parse_criterion(PREREG)
    assert len(declared) == 10, f"the criterion block declares {len(declared)} thresholds, not ten"
    text = PREREG.read_text(encoding="utf-8")
    for name, value in declared.items():
        assert f"{name} = {value}" in text, (
            f"{name} is not printed in the document it was parsed from"
        )
