"""NC-ASK — the guards for the questioning flow. Two crossed checks, four halves, four injectors.

## What each half is, and why one injector per half

`CLAUDE.md §3`: *"Each half of a check needs its OWN injector. An allowlist has two failure modes —
an undeclared entry, and a table full of entries nobody reaches."*

**The askable allowlist.** `ASKABLE` decides which of the eight closed refusal reasons become
questions. It fails in two directions: a reason that is not a question gets asked (`ASK01`), or a
row sits in the table that no refusal can ever carry (`ASK02`). The second is not hypothetical
here — `NOT_LOCATABLE_IN_SOURCE` was declared in `FillRefusal` and CONSTRUCTED NOWHERE until C6
wired it, measured 20 Aug 2026 by grepping every `FillRefusal.` site in `src/` and `tools/`.

**The asserted tier.** An answer becomes a value that is placed and never evidenced. It fails in
two directions too, and they are opposite: counting the answer as evidenced (`ASK03`) overstates
what was checked, and dropping it from the return (`ASK04`) hides the filer's own words from them.

Every guard is written over `ask_reference.declaration()`, a population built from `src/` code end
to end in which ALL EIGHT reasons arise. The pinned FME return produces only two of them, so a
guard written over that return alone would leave six rows of the table unmeasured and green.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ask_reference as ref  # noqa: E402
from cdfc.ask import ASKABLE, NOT_ASKABLE, Answer, apply, questions_for  # noqa: E402
from cdfc.fill.propose import FillRefusal  # noqa: E402

ANSWERED_AT = "2026-08-20T18:30:00+05:30"


@pytest.fixture(scope="module")
def population():
    d = ref.declaration()
    fs = ref.fieldset()
    qs = questions_for(d, fs, documents=list(ref.sources()))
    return d, fs, qs


def test_nc__ASK01_a_reason_that_is_not_a_question_is_never_asked(population) -> None:
    """`AskFieldNotLabelled`: a refusal nobody can answer is put to the filer as a question.

    On the pinned FME return `field_not_labelled` is 3,615 of 3,735 refusals, so asking it turns a
    screen with 129 answerable questions into one claiming 3,744.
    """
    _d, _fs, qs = population
    asked = {q.reason for q in qs.questions}
    for reason in NOT_ASKABLE:
        assert reason not in asked, (
            f"{reason.value} is declared NOT a question and a question carrying it was produced. "
            f"{NOT_ASKABLE[reason]}"
        )
    # And the population it belongs to is REPORTED, not silently dropped: a reason that is not a
    # question is still work, and hiding it is the opposite error from asking it.
    reported = {n.reason for n in qs.not_asked}
    assert FillRefusal.FIELD_NOT_LABELLED in reported, (
        "the unanswerable refusals are not reported at all. Not asking them is right; not "
        "COUNTING them tells a filer there is less to do than there is."
    )


def test_nc__ASK02_every_askable_reason_is_reachable(population) -> None:
    """`AskableGhostRow`: a question kind declared in the table that no refusal can ever carry.

    The reachability is measured over a declaration built from `src/` code, not asserted. A row
    whose reason never arises is a widget nobody is ever shown, and it makes the table look
    complete while covering less than it claims.
    """
    _d, _fs, qs = population
    carried = {q.reason for q in qs.questions}
    unreachable = sorted(r.value for r in set(ASKABLE) - carried)
    assert not unreachable, (
        f"{len(unreachable)} askable reason(s) are declared and no refusal in the reference "
        f"population carries them: {unreachable}. An allowlist full of entries nobody reaches "
        "refuses nothing and asks nothing — which is how `not_locatable_in_source` sat in "
        "`FillRefusal` being constructed by no code at all."
    )


def test_nc__ASK03_an_answer_is_never_counted_as_evidenced(population) -> None:
    """`AssertedCountsAsEvidenced`: the coverage count absorbs a value that re-read nothing.

    An EVIDENCED value cites a document and a span that re-reads byte-exact. An ASSERTED value is
    one a person typed. Merging them makes one number mean two things, which is the exact defect
    the `Derived` lane was created to avoid on the model's side.
    """
    d, _fs, qs = population
    before = len(d.admitted())
    answerable = next(q for q in qs.questions if q.shape.value == "value")
    out = apply(d, qs, [Answer(answerable.id, "5,00,00,000", "Asha Rao", ANSWERED_AT)])

    assert len(out.declaration.asserted) == 1, "the answer did not reach the asserted lane"
    assert len(out.declaration.admitted()) == before, (
        f"answering moved the EVIDENCED count from {before} to "
        f"{len(out.declaration.admitted())}. An answer re-reads nothing; counting it as evidence "
        "makes the coverage figure a claim nobody checked."
    )
    for a in out.declaration.asserted:
        assert a.as_canonical_obj()["evidenced"] is False
        assert a.resolved_by == "human"
        assert a.answered_by and a.answered_at and a.question_id


def test_nc__ASK04_an_answer_is_placed_in_the_return(population) -> None:
    """`AssertedNotPlaced`: the answer is recorded and does not appear in what is filed.

    The other half of ASK03 and the one a single control misses. `filled()` is the product's own
    count of what the return CARRIES, which is a different question from what was checked.
    """
    d, _fs, qs = population
    before = set(d.filled())
    answerable = next(q for q in qs.questions if q.shape.value == "value")
    out = apply(d, qs, [Answer(answerable.id, "5,00,00,000", "Asha Rao", ANSWERED_AT)])

    after = set(out.declaration.filled())
    assert answerable.ref in after, (
        f"{answerable.ref} was answered and is not in the return. A value the filer supplied, "
        "under their name, that no screen shows is a different falsehood from counting it as "
        "evidence and it is not a lesser one."
    )
    assert after - before == {answerable.ref}, (
        "answering one question changed the placed set by more than that one field"
    )
    assert out.declaration.counts()["filled_total"] == len(before) + 1


def test_nc__ASK05_positive_control_the_flow_still_asks_and_still_evidences(population) -> None:
    """The POSITIVE CONTROL. A declaration in which nothing succeeds proves nothing about a guard.

    This asserts the reference population is a real one: it evidences a field, it refuses six with
    six distinct reasons, it produces a question for every askable reason, and its declaration
    closes. If this fails, the four guards above are asserting over rubble.
    """
    d, _fs, qs = population
    assert len(d.admitted()) >= 1, "the reference population evidences nothing"
    assert len(qs.questions) == len(ASKABLE), (
        f"{len(qs.questions)} question(s) for {len(ASKABLE)} askable reason(s) — the reference "
        "population is meant to carry exactly one of each"
    )
    assert {r.reason for r in d.refused} == set(FillRefusal) - {
        FillRefusal.ATTESTATION_REQUIRES_SIGNATORY, FillRefusal.NO_OBSERVATION
    } | {FillRefusal.NO_OBSERVATION}, "the reference population lost a refusal reason"
    assert sum(n.count for n in qs.not_asked) == 2, (
        "both non-question reasons must arise, or ASK01 is guarding an empty set"
    )
