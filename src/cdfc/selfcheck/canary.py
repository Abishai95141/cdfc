"""P10-B1 — the canary loop, the anti-canary, and the run-level disposition.

**The design's boldest claim lives in this file.** No assurance artifact in existence carries
evidence that the instrument that produced it was working on the specific document it examined. A
clean audit opinion does not. An SBOM does not. A validation report does not. This one refuses to
issue a verdict unless every check has just demonstrated, *on this filing*, that it can still catch
a fault it was admitted for.

The mechanism claims no novelty — it is two extra executions per predicate. What is load-bearing is
that the failure of the demonstration **withholds the verdict** rather than being logged.

---

## NOTHING IN THIS LOOP READS A CLOCK, and adversary F23 is why

`CanaryRow` carried an `elapsed_us` integer field — a wall-clock duration — inside a structure whose
canonicalised digest feeds `livenessProof` and `run.jsonl`. Two runs produce different microsecond
counts, therefore different bytes, therefore `E2E-VERIFY` fails permanently. And the obvious repair
is the dangerous one: deleting the field silently removes the evidence that the loop *executed*
rather than being replayed from a cache, which is death **D5**'s entire concern, in the layer whose
whole claim is that it ran.

So the ruling keeps both halves. Timings leave the payload entirely —
`selfcheck/timings.py` writes `reports/perf/<run_id>.jsonl`, outside `run.jsonl`, outside the
attestation and outside everything `verify` compares. And the evidence of execution stays, and it
is deterministic: `CanaryRow` retains `witness_digest`, `observability`, `intersects_read_set` and
`fired`, every one a function of the inputs, and `canariesRun == len(rows)` remains the assertion
that answers D5. **A count of rows produced by executions is stronger evidence of execution than a
duration is**, because a cached replay can carry a duration and cannot carry a per-witness digest
it did not compute.

## The counts are `len()` of a row set, never a variable

Death **D5** is *"the counts are asserted, not counted"* — `canariesRun := len(predicates)` instead
of `len(rows)`. Every count on `CanaryReport` is a property computed from a tuple, so there is no
assignment for a defect to live in, and relation **R-06** re-checks the published integer against
the rows written to `run.jsonl` from the other side.

## The anti-canary's threshold, stated rather than taken

`plan/05` writes the anti-canary as `fired = (evaluate(P, passcase).state != "PASS")`. **This
implementation turns the disposition on `state == FAIL` and publishes both counts.** The defect the
anti-canary exists to catch is NC-C08 — *the predicate has drifted to flagging everything* — and a
predicate that is `OUT_OF_SCOPE` or `NOT_RUN` on the clean pass case is not flagging anything; it
is inapplicable, which is a different fact with a different remedy. Reading inapplicability as
drift would turn a healthy run `INVALID` for a reason that is not a defect.

The weaker reading is not taken quietly: `anti_not_pass` is on the report beside `anti_fired`, both
render in `livenessProof`, and `test_c__the_anti_canary_publishes_both_readings` fails a report
that carries only one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

from cdfc.canon import canonical_json, sha256_hex
from cdfc.qualify.observability import Observability
from cdfc.selfcheck.selftest import EXPECTED_SILENT, P_SELFTEST_DEAD, SelfTestPredicate
from cdfc.selfcheck.thresholds import MAX_WITNESSES, ceiling_exceeded
from cdfc.selfcheck.witness import (
    FaultWitness,
    FilingImage,
    WitnessKeyUnresolved,
    apply,
    observability,
)
from cdfc.verdict.invalid import InvalidCause
from cdfc.verdict.reasons import ReasonCode

CanaryFailureKind = Literal[
    "PREDICATE_DID_NOT_FIRE",
    "WITNESS_MISSES_READ_SET",
    "SELFTEST_NOT_SILENT",
    "WHOLESALE_INAPPLICABILITY",
    "ANTI_CANARY_FIRED",
]

# The order in which two simultaneous failures are reported. Fixed, so a run with both a dead
# predicate and a dead loop reports the same kind on every machine — a `failure_kind` that depends
# on iteration order is not a diagnosis.
FAILURE_PRECEDENCE: Final[tuple[CanaryFailureKind, ...]] = (
    "SELFTEST_NOT_SILENT",       # the loop itself is not running: nothing else it says is evidence
    "ANTI_CANARY_FIRED",         # a predicate flags a clean filing: its kills mean nothing either
    "WITNESS_MISSES_READ_SET",   # the admission is wrong — a different remedy from the next one
    "PREDICATE_DID_NOT_FIRE",    # the code is wrong
    "WHOLESALE_INAPPLICABILITY", # neither: this filing cannot demonstrate the instrument
)


@dataclass(frozen=True, slots=True)
class CanaryRow:
    """ONE PER ATTEMPT. Four deterministic fields and an id.

    **NO DURATION FIELD. NO TIMESTAMP. NO `perf_counter`-DERIVED VALUE. EVER.** See the module
    docstring, adversary F23, `ci/no-timing-in-hashed-payload.sh` and
    `tests/contract/test_contract_timing.py`.
    """

    predicate_id: str
    witness_digest: str
    observability: str
    intersects_read_set: bool
    fired: bool
    # The item state the evaluation actually returned, and it is not redundant with `fired`.
    #
    # **`PASS` and `NOT_RUN` are opposite findings and the first version of this loop merged
    # them.** `fired = (state == FAIL)` reads both as *the canary stayed silent*, so a predicate
    # that COULD NOT RUN — because the fault landed on a cell whose partner the filing does not
    # carry — was reported as a dead check. Measured on `formula-overwritten__portfolio-O7.xlsx`:
    # of 20 silent canaries, none was a dead check. `PASS` is death D1; `NOT_RUN` is
    # inapplicability, and they have nothing in common except that no alarm sounded.
    outcome: str = "FAIL"

    def __post_init__(self) -> None:
        if self.fired != (self.outcome == "FAIL"):
            raise ValueError(
                f"{self.predicate_id}: fired={self.fired} with outcome={self.outcome!r}. `fired` "
                "is a FACT ABOUT the outcome, not a second opinion on it."
            )

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "predicate_id": self.predicate_id,
            "witness_digest": self.witness_digest,
            "observability": self.observability,
            "intersects_read_set": self.intersects_read_set,
            "fired": self.fired,
            "outcome": self.outcome,
        }


@dataclass(frozen=True, slots=True)
class CanaryReport:
    """The loop's whole output. Every count below is `len()` of a tuple — D5."""

    rows: tuple[CanaryRow, ...]
    anti_rows: tuple[CanaryRow, ...]
    inapplicable: tuple[str, ...]     # every stored witness was UNOBSERVABLE on this filing
    indeterminate: tuple[str, ...]    # no witness OBSERVABLE and at least one INDETERMINATE
    unresolved: tuple[str, ...]       # the witness's stable key is not in this filing's key set
    silent: tuple[str, ...]           # an observable witness was found and the predicate held
    missed_read_set: tuple[str, ...]  # silent, AND the witness lies outside the read set
    anti_fired: tuple[str, ...]       # FAILed its own clean pass case — NC-C08's drift
    anti_not_pass: tuple[str, ...]    # anything other than PASS. Published beside anti_fired
    selftest_silent: bool
    max_witnesses: int = MAX_WITNESSES

    def __post_init__(self) -> None:
        """`selftest_silent` is not an independent field; it is a fact about `silent`.

        Letting the two diverge is the one-line injection that makes §P10·L.4's hole reachable
        again: report `selftest_silent=True` while the self-test is not in the silent set, and the
        disposition goes green while the loop is not running. The loop computes it as
        `selftest.id in silent`; this refuses any other combination, so no caller can assemble one.
        """
        expected = bool(EXPECTED_SILENT & set(self.silent))
        if self.selftest_silent != expected:
            raise ValueError(
                f"selftest_silent={self.selftest_silent} but the silent set "
                f"{'contains' if expected else 'does not contain'} {sorted(EXPECTED_SILENT)}. "
                "The flag is a FACT ABOUT the silent set, not a second opinion on it: a report "
                "that claims the self-test stayed silent while it is not in the set is a loop "
                "reporting a result it did not compute."
            )

    # --- the counts, and there is no assignment for a defect to live in --------------------

    @property
    def predicate_rows(self) -> tuple[CanaryRow, ...]:
        """Every attempt EXCEPT the self-test's.

        The self-test is reported separately — `plan/05`'s `livenessProof` shows
        `canariesRun == canariesPassed` on a healthy run, and the self-test is silent BY DESIGN, so
        leaving it in the numerator would make a healthy run look like one canary short for ever.
        Its own outcome is `selfTestSilent`, and `rowsTotal` publishes the undivided count so
        nothing is hidden by the split.
        """
        return tuple(r for r in self.rows if r.predicate_id not in EXPECTED_SILENT)

    @property
    def canaries_run(self) -> int:
        return len(self.predicate_rows)

    @property
    def canaries_passed(self) -> int:
        return sum(
            1 for r in self.predicate_rows
            if r.observability == str(Observability.OBSERVABLE) and r.fired
        )

    @property
    def anti_canaries_run(self) -> int:
        return len(self.anti_rows)

    @property
    def anti_canaries_passed(self) -> int:
        return sum(1 for r in self.anti_rows if not r.fired)

    @property
    def failure_kind(self) -> CanaryFailureKind | None:
        found: set[str] = set()
        if not self.selftest_silent:
            found.add("SELFTEST_NOT_SILENT")
        if self.anti_fired:
            found.add("ANTI_CANARY_FIRED")
        real_silent = set(self.silent) - EXPECTED_SILENT
        if real_silent & set(self.missed_read_set):
            found.add("WITNESS_MISSES_READ_SET")
        if real_silent - set(self.missed_read_set):
            found.add("PREDICATE_DID_NOT_FIRE")
        if ceiling_exceeded(len(self.inapplicable), len(self.indeterminate), len(self.rows)):
            found.add("WHOLESALE_INAPPLICABILITY")
        for kind in FAILURE_PRECEDENCE:
            if kind in found:
                return kind
        return None

    def as_liveness_proof(self) -> dict[str, Any]:
        """The attestation object. Every value is an integer computed as `len()` of a row set.

        `canariesIndeterminate` renders **beside** `canariesInapplicable` and is never pooled into
        it: one is a fact about the filing, the other a fact about our evaluator (adversary F18).
        """
        return {
            "rowsTotal": len(self.rows),
            "canariesRun": self.canaries_run,
            "canariesPassed": self.canaries_passed,
            "antiCanariesRun": self.anti_canaries_run,
            "antiCanariesPassed": self.anti_canaries_passed,
            "canariesInapplicable": len(self.inapplicable),
            "canariesIndeterminate": len(self.indeterminate),
            "canariesUnresolved": len(self.unresolved),
            "antiCanariesFired": len(self.anti_fired),
            "antiCanariesNotPass": len(self.anti_not_pass),
            "selfTestSilent": self.selftest_silent,
            "maxWitnesses": self.max_witnesses,
        }

    def digest(self) -> str:
        """Order-invariant: the rows are sorted before canonicalisation.

        `test_prop__the_loop_is_order_independent` shuffles the predicate order and asserts this
        digest does not move. A liveness proof whose bytes depend on dictionary order is a proof
        that cannot be re-derived, which is P11's whole acceptance test one phase early.
        """
        return sha256_hex(
            canonical_json(
                {
                    "rows": sorted(
                        (r.as_canonical_obj() for r in self.rows),
                        key=lambda d: (d["predicate_id"], d["witness_digest"]),
                    ),
                    "anti_rows": sorted(
                        (r.as_canonical_obj() for r in self.anti_rows),
                        key=lambda d: (d["predicate_id"], d["witness_digest"]),
                    ),
                    "liveness": self.as_liveness_proof(),
                }
            )
        )


@dataclass(frozen=True, slots=True)
class RunDisposition:
    """What the loop does to the run. `settledFraction` and `verdict` are `null`, never zero."""

    valid: bool
    cause: InvalidCause | None
    failure_kind: CanaryFailureKind | None
    deactivated: tuple[str, ...]      # predicates whose cells become NOT_RUN(not_run.deactivated)
    detail: str

    @property
    def deactivated_reason(self) -> ReasonCode:
        return ReasonCode.NR_DEACTIVATED


def run_canaries(
    image: FilingImage,
    predicates: Sequence[Any],
    witnesses: Mapping[str, Sequence[FaultWitness]],
    *,
    evaluate: Callable[[Any, Any], str],
    read_set_of: Callable[[Any], frozenset[str]],
    evaluate_selftest: Callable[[SelfTestPredicate, Any], bool],
    passcase_facts: Any,
    selftest: SelfTestPredicate = P_SELFTEST_DEAD,
) -> CanaryReport:
    """Every ACTIVE or PROVISIONAL predicate — relations included, because a relation is a predicate.

    The loop, stated exactly:

        for each predicate P:
            for w in P's stored kill cases (ordered, <= MAX_WITNESSES, diverse WITHIN the claim):
                obs = observability(w, this filing)
                if obs != OBSERVABLE: record the row; continue
                fired = (evaluate(P, apply(w, facts)) is FAIL)
                record the row; break        # the first observable witness is THE canary
            anti-canary: P must not FAIL its pinned clean pass case

    **`evaluate` and `read_set_of` are injected rather than imported.** `selfcheck/` must not pull
    the evaluation stack into its import closure: `g4_ffr.independent()` decides whether a corpus
    is an admissible oracle by intersecting import closures, so a module that drags in what it
    never executes reports itself less independent than it is. The callables come from
    `evaluate/run.py`, which already owns the runner.
    """
    rows: list[CanaryRow] = []
    anti: list[CanaryRow] = []
    inapplicable: list[str] = []
    indeterminate: list[str] = []
    unresolved: list[str] = []
    silent: list[str] = []
    missed: list[str] = []
    anti_fired: list[str] = []
    anti_not_pass: list[str] = []

    for p in predicates:
        pid = p.id
        read_set = read_set_of(p)
        stored = list(witnesses.get(pid, ()))
        saw_observable = False
        saw_indeterminate = False
        saw_unresolved = False
        saw_any = False

        for w in stored:
            try:
                obs, _cells = observability(w, image)
            except WitnessKeyUnresolved:
                saw_unresolved = True
                rows.append(
                    CanaryRow(pid, w.digest(), "UNRESOLVED", False, False, "NOT_RUN")
                )
                continue
            saw_any = True
            if obs is not Observability.OBSERVABLE:
                saw_indeterminate |= obs is Observability.INDETERMINATE_OBSERVABILITY
                rows.append(CanaryRow(pid, w.digest(), str(obs), False, False, "NOT_RUN"))
                continue

            in_read_set = w.recorded_at_cell in read_set
            state = evaluate(p, apply(w, image))
            fired = state == "FAIL"
            rows.append(CanaryRow(pid, w.digest(), str(obs), in_read_set, fired, state))
            if state not in ("FAIL", "PASS"):
                # **THE PREDICATE COULD NOT RUN**, which is neither a kill nor a miss. Its declared
                # key is absent on this filing, or its precondition is unmet, or the evaluator
                # could not decide — so the canary was never actually asked, and reading that as
                # `the check is dead` is the same category error as reading `NOT_RUN` as `PASS`
                # one layer down. Keep trying the remaining witnesses: another may land where this
                # filing carries what the predicate needs.
                continue
            saw_observable = True
            if not fired:
                silent.append(pid)
                if not in_read_set:
                    # A DISTINCT KIND, and merging it is the SPDX `NOASSERTION` collapse in
                    # miniature. Different remedies: re-qualify the admission, versus fix the code.
                    missed.append(pid)
            break

        if not stored:
            # **A PREDICATE WITH NO STORED KILL CASE STILL PRODUCES A ROW**, and the first version
            # of this loop did not — so `canariesRun` counted only the predicates that had
            # something to try, and the ceiling computed `315 / 34`, a ratio above 1 that is not a
            # fraction of anything. `canariesRun == len(rows)` is only an honest answer to death D5
            # if a row is written for every ATTEMPT, and an attempt that could not be made is
            # still an attempt: it is precisely the case the report has to show.
            rows.append(CanaryRow(pid, "", "NO_WITNESS", False, False, "NOT_RUN"))

        if not saw_observable:
            if saw_unresolved and not saw_any:
                unresolved.append(pid)
            elif saw_indeterminate:
                indeterminate.append(pid)
            else:
                # Includes a predicate with NO stored witness at all: it cannot demonstrate
                # liveness here, and that is inapplicability, not a pass.
                inapplicable.append(pid)

        clean_state = evaluate(p, passcase_facts)
        failed_clean = clean_state == "FAIL"
        anti.append(
            CanaryRow(pid, "anti:" + pid, "OBSERVABLE", True, failed_clean, clean_state)
        )
        if failed_clean:
            anti_fired.append(pid)
        if clean_state != "PASS":
            # BOTH readings, published side by side. `plan/05` turns the anti-canary on
            # `state != PASS`; this build turns the DISPOSITION on `state == FAIL`, because a
            # predicate that is OUT_OF_SCOPE or NOT_RUN on the clean pass case is inapplicable,
            # not drifting toward flagging everything. The weaker reading is not taken quietly.
            anti_not_pass.append(pid)

    # THE SELF-TEST, through the same runtime, with no flag and no environment variable.
    st_fired = evaluate_selftest(selftest, image.facts)
    rows.append(
        CanaryRow(selftest.id, "selftest:" + selftest.id, "OBSERVABLE", False, st_fired,
                  "FAIL" if st_fired else "PASS")
    )
    if not st_fired:
        silent.append(selftest.id)

    return CanaryReport(
        rows=tuple(rows),
        anti_rows=tuple(anti),
        inapplicable=tuple(sorted(inapplicable)),
        indeterminate=tuple(sorted(indeterminate)),
        unresolved=tuple(sorted(unresolved)),
        silent=tuple(sorted(silent)),
        missed_read_set=tuple(sorted(missed)),
        anti_fired=tuple(sorted(anti_fired)),
        anti_not_pass=tuple(sorted(anti_not_pass)),
        selftest_silent=(selftest.id in silent),
    )


def disposition(cr: CanaryReport) -> RunDisposition:
    """`INVALID(invalid.canary_silent)` or `VALID`, and nothing in between.

    | condition | run state | `failure_kind` | settled fraction |
    |---|---|---|---|
    | `silent ⊋ {P-SELFTEST-0001}` | `INVALID` | `PREDICATE_DID_NOT_FIRE` / `WITNESS_MISSES_READ_SET` | `null` |
    | `not selftest_silent` | `INVALID` | `SELFTEST_NOT_SILENT` | `null` |
    | `anti_fired ≠ ∅` | `INVALID` | `ANTI_CANARY_FIRED` | `null` |
    | `(inapplicable + indeterminate) / rows > 0.25` | `INVALID` | `WHOLESALE_INAPPLICABILITY` | `null` |
    | otherwise | `VALID` | — | computed; inapplicable and indeterminate cells are `NOT_RUN(not_run.deactivated)` and **the fraction falls** |

    **`settledFraction` is `null` on every `INVALID` row — not zero, not omitted, `null`.** Zero is
    a finding about the filing; `null` is a finding about us, and the two must never be allowed to
    look alike. `verdict` is `null` for the same reason: `SETTLEMENT_INSUFFICIENT` is a statement
    about the filing's residue and this is a statement about our instrument.
    """
    kind = cr.failure_kind
    deactivated = tuple(sorted(set(cr.inapplicable) | set(cr.indeterminate) | set(cr.unresolved)))
    if kind is None:
        return RunDisposition(
            valid=True, cause=None, failure_kind=None, deactivated=deactivated,
            detail=(
                f"{cr.canaries_run} canaries, {cr.anti_canaries_run} anti-canaries; "
                f"{len(cr.inapplicable)} inapplicable and {len(cr.indeterminate)} indeterminate "
                f"predicates are NOT_RUN(not_run.deactivated), so the settled fraction falls"
            ),
        )
    return RunDisposition(
        valid=False,
        cause=InvalidCause.CANARY_SILENT,
        failure_kind=kind,
        deactivated=deactivated,
        detail=_detail(cr, kind),
    )


def _detail(cr: CanaryReport, kind: CanaryFailureKind) -> str:
    """Name the dead predicate(s). A run withheld without naming what died is unactionable."""
    real_silent = sorted(set(cr.silent) - EXPECTED_SILENT)
    if kind == "SELFTEST_NOT_SILENT":
        return (
            f"{_SELFTEST_ID} reported that it FIRED. Its expr is the literal `true` and no fault "
            "can make it FAIL, so this is not a finding about the filing — the loop is not "
            "running, or it is reporting results it did not compute."
        )
    if kind == "ANTI_CANARY_FIRED":
        return (
            f"{len(cr.anti_fired)} predicate(s) FAILed their own pinned clean pass case: "
            f"{', '.join(cr.anti_fired[:8])}. A check that flags a filing known to be correct has "
            "drifted to flagging everything, and its kill rate is evidence of nothing."
        )
    if kind == "WITNESS_MISSES_READ_SET":
        return (
            f"{len(cr.missed_read_set)} predicate(s) stayed silent on a witness that lies OUTSIDE "
            f"their read set: {', '.join(cr.missed_read_set[:8])}. The remedy is to re-qualify "
            "the admission, NOT to fix the code — which is why this is a distinct kind."
        )
    if kind == "PREDICATE_DID_NOT_FIRE":
        return (
            f"{len(real_silent)} admitted predicate(s) did not catch a fault they were admitted "
            f"for, on this filing: {', '.join(real_silent[:8])}. The check is dead."
        )
    return (
        f"{len(cr.inapplicable)} inapplicable + {len(cr.indeterminate)} indeterminate of "
        f"{cr.canaries_run} attempts exceeds the pre-registered ceiling. This filing cannot "
        "demonstrate the instrument, so no coverage is declared over it."
    )


_SELFTEST_ID: Final[str] = P_SELFTEST_DEAD.id
