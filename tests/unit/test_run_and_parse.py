"""P12-B3 — the driver that refuses, and the parser that never raises on model output.

Two rules, and they point in opposite directions on purpose.

**`propose()` refuses more than it runs.** Four refusals fire before anything reaches a network,
and each closes a way the experiment could produce a number that looks the same and means something
else. On today's tree the third fires, for a structural reason rather than a configuration one.

**`parse()` has no failure path that is not a row.** A model that emits rubbish is *data about the
model*; an exception at that layer would end the batch and make the discard rate a function of
where in the batch the rubbish landed. The one thing that does raise is recording a reason outside
the closed six — that is a defect in us, and the two must not be handled the same way.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import digest  # noqa: E402
from cdfc.experiment import prereg, run  # noqa: E402
from cdfc.experiment.client import (  # noqa: E402
    MAX_RETRIES,
    ClientConfig,
    ModelClientUnavailable,
    build_client,
)
from cdfc.experiment.draw import Draw  # noqa: E402
from cdfc.experiment.parse import (  # noqa: E402
    DISCARD_REASONS,
    Discard,
    ParseOutcome,
    UnlistedDiscardReason,
    parse,
)
from cdfc.experiment.prereg import APPENDABLE, Lock, PreregistrationMissing  # noqa: E402
from cdfc.experiment.run import ArtefactHashesMissing, CandidateRecord, alias_splits  # noqa: E402

GOOD = REPO / "fixtures" / "predicates" / "good" / "P-0041__scheme-type-membership.yaml"


def _draw() -> Draw:
    """A one-obligation draw. Only its `sha256` is read by the refusals under test."""
    return Draw(
        pool_sha256="p" * 64, seed=20260815, order=(0,), drawn=(0,),
        stratum_a=(0,), stratum_b_all=(), stratum_b_generated=(),
        excluded_count=0, stage=1,
    )


def _record(**kw: object) -> CandidateRecord:
    base = dict(
        candidate_sha256="c" * 64, obligation_ordinal=0, regime="correctness", draw_index=0,
        model_id="claude-opus-5", model_identity_reported="claude-opus-5-20260101",
        prompt_sha256="p" * 64, api_batch_id="msgbatch_01", requested_at="2026-08-15T00:00:00Z",
        envelope=object(), discard_reason=None,
    )
    return CandidateRecord(**{**base, **kw})  # type: ignore[arg-type]


# --- the refusals that precede the first call ---------------------------------------------------


def test_propose__refuses_without_a_lock(tmp_path: Path) -> None:
    """No lock, no run. **The refusal is the experiment's only guarantee that the criterion
    predates the result** — everything else about the ordering is a claim in a document.
    """
    with pytest.raises(PreregistrationMissing) as e:
        prereg._read(tmp_path / "preregistration.lock.json")
    msg = str(e.value)
    assert "does not exist" in msg
    assert "propose()" in msg and "criterion predates the result" in msg, (
        "the refusal must say what is lost, or it reads as a missing-file error somebody fixes by "
        "creating the file"
    )


def test_propose__refuses_on_a_partial_lock() -> None:
    """`ArtefactHashesMissing`, **naming every field that is still absent.**

    Each missing hash is an artifact that could still change after the model had been asked. A
    baseline computed after seeing the candidates is not a baseline, and a pool re-curated after the
    draw makes `k of 20` a measurement of the curation. On this tree the refusal fires for a
    structural reason: there is no statutory instrument in the repository, so there is no pool.
    """
    partial = Lock(fields={"h0": "0" * 64, "committed_at": "2026-08-15"})
    with pytest.raises(ArtefactHashesMissing) as e:
        run.propose(_draw(), lock=partial)
    msg = str(e.value)
    for field in APPENDABLE:
        assert field in msg, f"{field} is missing from the lock and unnamed in the refusal"
    assert "does not proceed on a partial lock" in msg

    # A COMPLETE lock whose draw hash names a different draw is refused too — running against a
    # draw the lock does not name is running against a pool nobody fixed.
    complete = Lock(fields={
        "h0": "0" * 64, "committed_at": "2026-08-15",
        **{f: f[0] * 64 for f in APPENDABLE},
    })
    with pytest.raises(ArtefactHashesMissing) as e2:
        run.propose(_draw(), lock=complete)
    assert "pool nobody fixed" in str(e2.value)

    # And with the draw hash matching, the chain reaches the client and stops there — never the
    # network, and never the `NotImplementedError` beyond it.
    matching = Lock(fields={**complete.fields, "draw_sha256": _draw().sha256})
    with pytest.raises(ModelClientUnavailable):
        run.propose(_draw(), lock=matching)


def test_propose__has_no_attempt_parameter() -> None:
    """**Retry is impossible here, not discouraged.**

    A silent re-prompt understates the discard rate, and the discard pile is stage 0 of the funnel —
    so a retried batch produces a funnel that starts from a curated set while printing the planned
    count. A constant somebody can pass a different value to is a default, not a rule, so both
    halves are asserted: no parameter admits an attempt, and the one knob that exists refuses any
    value but zero.
    """
    banned = ("attempt", "retry", "retries")
    for fn in (run.propose, run.planned_calls, run.assert_ready, build_client):
        names = list(inspect.signature(fn).parameters)
        offenders = [n for n in names if any(b in n.lower() for b in banned)]
        assert offenders == [], f"{fn.__name__} admits {offenders}"

    assert MAX_RETRIES == 0
    assert ClientConfig().max_retries == 0
    with pytest.raises(ValueError) as e:
        ClientConfig(max_retries=1)
    assert "NC-M10" in str(e.value) and "funnel's stage 0" in str(e.value)


def test_client__is_unavailable_and_says_so() -> None:
    """`anthropic` is **deliberately** absent from `requirements.lock`, and the refusal says why.

    There is no offline stub and no cached-response mode. A driver that fell back to a stub would
    produce a runlog indistinguishable from a real one — and the runlog is what the git-ancestry
    check anchors on, so the stub would be attesting to an ordering that never happened.
    """
    with pytest.raises(ModuleNotFoundError):
        __import__("anthropic")

    with pytest.raises(ModelClientUnavailable) as e:
        build_client()
    msg = str(e.value)
    assert "requirements.lock" in msg, "the message must name where the SDK is deliberately absent"
    assert "deliberately absent" in msg
    assert "human-initiated, money-spending step" in msg, (
        "the message must distinguish 'could not be run' from 'produced nothing' — they are "
        "different facts and this exception is what keeps them apart"
    )


# --- the parser: every failure mode is a row ----------------------------------------------------


def _candidate(**over: object) -> str:
    obj = yaml.safe_load(GOOD.read_text(encoding="utf-8"))
    obj.update(over)
    return yaml.safe_dump(obj)


def test_parse__malformed_becomes_a_discard_row() -> None:
    """**All six reasons triggered on real input, and none of them raises.**

    An exception at this layer would end the batch, lose the rows already produced and — worst —
    make the discard rate a function of where in the batch the rubbish landed. Every reason below
    is provoked by an actual string or an actual envelope; none is asserted by constructing a
    `Discard` and calling that a test.
    """
    unread = _candidate(
        schema_keys=[
            "filing.intro.tbl15.rows",
            "filing.intro.tbl15.rows[*].scheme_type",
            "filing.intro.tbl15.rows[*].__cell__",
            "template.vocab.scheme_type",
            "filing.intro.tbl15.rows[*].never_read",
        ]
    )
    host_fn_caller = _candidate(
        schema_keys=["filing.intro.tbl11.n_schemes", "filing.intro.tbl11.__cell__"],
        applicable="has(filing.intro.tbl11.n_schemes)",
        expr="sum([filing.intro.tbl11.n_schemes]) >= 0",
        witness="[filing.intro.tbl11.__cell__]",
        host_fns=["sum"],
    )
    repeated = "id: P-0000\nversion: 1\n"

    cases: tuple[tuple[str, str, dict], ...] = (
        # unterminated flow sequence — yaml.YAMLError
        ("not_yaml", "a: [1, 2\n  b: :::\n", {}),
        # valid YAML that is not a mapping: the same reason, and it must not raise on `.get`
        ("not_yaml", "a bare scalar, which is not an envelope\n", {}),
        ("envelope_schema_invalid", "foo: 1\nbar: 2\n", {}),
        ("missing_clause_span",
         yaml.safe_dump({"clause": {"instrument": "IFSCA", "eId": "reg-9", "quote": "q"}}), {}),
        ("cel_parse_error", unread, {}),
        ("unknown_host_fn", host_fn_caller, {"host_fns": frozenset()}),
        ("duplicate_of_earlier_candidate", repeated,
         {"seen_digests": frozenset({digest(yaml.safe_load(repeated))})}),
    )

    seen: set[str] = set()
    for expected, raw, kwargs in cases:
        outcome = parse(raw, **kwargs)          # must not raise, whatever is in `raw`
        assert outcome.envelope is None and outcome.discard is not None, expected
        assert outcome.discard.reason == expected, (
            f"expected {expected}, got {outcome.discard.reason}: {outcome.discard.detail}"
        )
        assert outcome.discard.detail, "a discard with no detail is a row nobody can act on"
        seen.add(expected)

    assert seen == set(DISCARD_REASONS), (
        f"untriggered reasons: {sorted(set(DISCARD_REASONS) - seen)}. A reason that no input can "
        "reach is a bucket that will never be counted and will never be removed."
    )

    # The positive control. Without it every assertion above is satisfied by a parser that discards
    # everything, and the discard rate would be 100% by construction.
    good = parse(GOOD.read_text(encoding="utf-8"))
    assert good.discard is None and good.envelope is not None
    assert good.envelope.id == "P-0041"


def test_parse__discard_reasons_are_closed() -> None:
    """Six, and the set does not open. **`other` is where the reasons nobody wanted to name go to
    stop being counted**, and the closure is what makes that impossible rather than impolite."""
    assert DISCARD_REASONS == (
        "not_yaml",
        "envelope_schema_invalid",
        "missing_clause_span",
        "cel_parse_error",
        "unknown_host_fn",
        "duplicate_of_earlier_candidate",
    )
    for bad in ("other", "misc", "unknown", "", "NOT_YAML"):
        with pytest.raises(UnlistedDiscardReason):
            Discard(bad, "detail")

    # An outcome is an envelope OR a discard. Both would be a candidate simultaneously admitted and
    # rejected; neither would be a call whose result left no row at all.
    with pytest.raises(ValueError):
        ParseOutcome(None, None)
    with pytest.raises(ValueError):
        ParseOutcome(object(), Discard("not_yaml", "detail"))


# --- the runlog: identity is recorded, never manufactured ---------------------------------------


def test_run__alias_splits_counts_null_under_its_own_key() -> None:
    """**NC-M12.** Risk R19 is realised, not hypothetical: a failure cell moved 96.6% → 100% on the
    same prompt and harness *under the same alias, with no version bump.*

    So an alias that resolved to two underlying models mid-batch produces two keys — a pooled
    `k of 20` across two models is a number about neither — and a call the API answered without an
    identity is counted under `null`, never under the alias that was requested. Writing the
    requested alias in would manufacture agreement: the field would always match, and the check
    that alias drift is visible would be a check on our own defaulting.
    """
    records = (
        _record(model_identity_reported="claude-opus-5-20260101"),
        _record(model_identity_reported="claude-opus-5-20260101"),
        _record(model_identity_reported="claude-opus-5-20260214"),
        _record(model_identity_reported=None),
    )
    splits = alias_splits(records)

    assert len(splits) == 3, f"a split batch was pooled into {len(splits)} key(s): {splits}"
    assert splits["claude-opus-5-20260101"] == 2
    assert splits["claude-opus-5-20260214"] == 1

    null_keys = [k for k in splits if "null" in k]
    assert len(null_keys) == 1 and splits[null_keys[0]] == 1
    assert "claude-opus-5" not in null_keys[0].split()[0], (
        "the null bucket is keyed on the ABSENCE of an identity; keying it on the requested alias "
        "is exactly the defaulting NC-M12 exists to make visible"
    )
    assert sum(splits.values()) == len(records), "a record fell out of the split"


def test_record__model_identity_reported_is_never_the_empty_string() -> None:
    """`null` and `""` are different facts: *the API reported nothing* and *the API reported an
    empty identity*. Collapsing them is the SPDX `NOASSERTION` shape this build refuses everywhere
    else, and here it would make the alias-drift check unfalsifiable.
    """
    with pytest.raises(ValueError) as e:
        _record(model_identity_reported="")
    assert "never the empty string" in str(e.value) and "NC-M12" in str(e.value)

    assert _record(model_identity_reported=None).model_identity_reported is None
    assert _record(model_identity_reported=None).as_obj()["model_identity_reported"] is None, (
        "the field must be PRESENT and null in the row — an omitted field makes 'no identity' and "
        "'no such column' indistinguishable to whoever reads the runlog"
    )

    # And the XOR that keeps a call from leaving no row: an envelope with a discard reason, or a
    # malformed candidate with neither.
    with pytest.raises(ValueError):
        _record(envelope=None, discard_reason=None)
    with pytest.raises(ValueError):
        _record(envelope=object(), discard_reason="not_yaml")
    assert _record(envelope=None, discard_reason="not_yaml").discard_reason == "not_yaml"
