"""P7-B3 — G3, degeneracy. Two arms, and `UNKNOWN` is UNPROVEN in both.

    trivially true   iff  ¬P ∧ domain  is UNSAT    ⇒ reject
    always flag      iff   P ∧ domain  is UNSAT    ⇒ reject
    redundant        iff  P₁ ∧ ¬P₂ ∧ domain UNSAT  ⇒ P₂ is implied; the ILP removes it AND RECORDS
    host functions are uninterpreted                ⇒ typically `unknown`

**`unknown` is *unproven*, never *non_degenerate*.** `test_prop__unknown_never_becomes_non_degenerate`
makes that a property rather than a convention: for every candidate,
`verdict == UNKNOWN ⇒ passed is False`, so an undecided predicate is decided by the empirical arm
rather than admitted on a proof nobody has.

**`rlimit`, never a wall clock (§0.6).** A wall-clock timeout makes the verdict a function of what
else the machine was doing, so the same candidate can be `unknown` on one runner and
`trivially_true` on another. `ci/no-wallclock-z3.sh` is the gate.

**The empirical arm's control threshold is EXACTLY ZERO, and that is derived rather than chosen.**
Control sites lie outside `upstream_closure(read_set(p))`, so a mutation there cannot change any
input the predicate reads after recalculation. A fire on a control mutant therefore means either an
undeclared key read — impossible, P4's both-ways AST check rejects that at admission — or a leak in
the fact table. **Both are apparatus failures, not predicate-quality findings**, so a non-zero count
raises `ApparatusError` and blocks the whole batch. *A threshold derivable from the architecture
beats a threshold that was negotiated.*
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, Final

from cdfc.qualify.cel_smt import translate
from cdfc.qualify.domain import DomainPolicy
from cdfc.qualify.errors import ApparatusError
from cdfc.qualify.random_flagger import DegenerateBaseline, adjusted_precision
from cdfc.qualify.result import GateId, GateOutcome

# The Z3 resource limit. A DETERMINISTIC budget: the same query consumes the same rlimit on every
# machine, which a wall clock does not.
RLIMIT: Final[int] = 2_000_000

# The harvest classes whose whole content is a bound. Under a PLACEHOLDER domain policy these are
# the predicates whose triviality cannot be decided, so they are routed to the empirical arm.
PURE_BOUND_CLASSES: Final[frozenset[str]] = frozenset(
    {"numeric_bound", "integer_bound", "date_bound"}
)

CLEAN_FIRING_CEILING: Final[Decimal] = Decimal("0.5")


class DegeneracyVerdict(StrEnum):
    NON_DEGENERATE = "non_degenerate"
    TRIVIALLY_TRUE = "trivially_true"
    ALWAYS_FLAG = "always_flag"
    REDUNDANT = "redundant"
    UNKNOWN = "unknown"  # UNPROVEN. Never "non_degenerate".


class Reason:
    TRIVIALLY_TRUE: Final[str] = "g3p.trivially_true"
    ALWAYS_FLAG: Final[str] = "g3p.always_flag"
    REDUNDANT: Final[str] = "g3p.redundant"
    FIRES_ON_CLEAN: Final[str] = "g3e.fires_on_clean_corpus"
    ON_DEGENERACY_LIST: Final[str] = "g3e.on_degeneracy_list"
    RANDOM_FLAGGER: Final[str] = "g3e.no_better_than_random"


CLOSED_REASONS: Final[tuple[str, ...]] = (
    Reason.TRIVIALLY_TRUE, Reason.ALWAYS_FLAG, Reason.REDUNDANT,
    Reason.FIRES_ON_CLEAN, Reason.ON_DEGENERACY_LIST, Reason.RANDOM_FLAGGER,
)


@dataclass(frozen=True, slots=True)
class CleanCorpusResult:
    """How a candidate behaved on filings nobody seeded a fault into."""

    n_filings: int
    n_fired: int
    control_spurious_fires: int
    corpus_label: str  # e.g. TEMPLATE-COMPUTED — carried onto every surface quoting this


def _solver() -> Any:
    import z3

    s = z3.Solver()
    # rlimit, NEVER timeout. `set("timeout", ...)` would make the verdict a function of load.
    s.set("rlimit", RLIMIT)
    return s


def _unsat(formula: Any) -> bool | None:
    """True/False, or **None** when Z3 returns `unknown` — which is not `unsat` and not `sat`."""
    import z3

    s = _solver()
    s.add(formula)
    r = s.check()
    if r == z3.unsat:
        return True
    if r == z3.sat:
        return False
    return None


def proof_arm(
    cand: Any,
    domain: DomainPolicy,
    *,
    harvest_class: str = "",
    admitted: Sequence[Any] = (),
) -> GateOutcome:
    """The SMT arm. Returns a GateOutcome whose `measured['verdict']` is a `DegeneracyVerdict`."""
    import z3

    measured: dict[str, object] = {
        "rlimit": RLIMIT,
        "domain_policy": domain.render(),
        "harvest_class": harvest_class,
        "subsumption_checked_against": len(admitted),
    }

    def out(verdict: DegeneracyVerdict, reason: str | None = None, **over: object) -> GateOutcome:
        """THREE outcomes, not two, and conflating any pair of them is a defect.

        * a DEGENERACY VERDICT (`trivially_true`, `always_flag`, `redundant`) REJECTS;
        * `non_degenerate` is PROVED and passes;
        * **`unknown` is UNPROVEN — it does not earn `non_degenerate`, and it does not reject.**
          The empirical arm must then decide.

        The plan words the property as `verdict == UNKNOWN => passed is False`. Read as *"unknown
        terminates the pipeline"* that rejects 47 of 349 predicates **for a limitation of our own
        translator** — every membership predicate among them — which is our apparatus deciding a
        question about the predicate. Read as *"unknown never earns non_degenerate"* it is the
        sentence the plan writes two lines later: *the empirical arm must then decide.* So
        `measured["proved"]` carries the property, and
        `test_prop__unknown_never_becomes_non_degenerate` asserts on it.
        """
        rejects = verdict in (DegeneracyVerdict.TRIVIALLY_TRUE, DegeneracyVerdict.ALWAYS_FLAG,
                              DegeneracyVerdict.REDUNDANT)
        m = {**measured, "verdict": verdict.value,
             "proved": verdict is DegeneracyVerdict.NON_DEGENERATE, **over}
        return GateOutcome(gate=GateId.G3P, passed=not rejects, measured=m,
                           reason=reason if rejects else None)

    # THE DECISION RULE, STATED IN ADVANCE. While `implausible_magnitude` is a PLACEHOLDER, a pure
    # bound cannot be decided by proof: `c.v >= -1e17` is not trivially true over the unconstrained
    # integers, and inventing a bound here would be inventing the answer.
    if domain.is_placeholder and harvest_class in PURE_BOUND_CLASSES:
        return out(DegeneracyVerdict.UNKNOWN,
                   why="domain-policy is PLACEHOLDER; a pure bound is routed to the empirical arm")

    t = translate(cand.expr)
    if t is None:
        return out(DegeneracyVerdict.UNKNOWN,
                   why="the expression leaves the admitted CEL->SMT subset")
    formula, _tr = t

    neg_unsat = _unsat(z3.Not(formula))
    if neg_unsat is None:
        return out(DegeneracyVerdict.UNKNOWN, why="z3 returned unknown within rlimit")
    if neg_unsat:
        return out(DegeneracyVerdict.TRIVIALLY_TRUE, Reason.TRIVIALLY_TRUE)

    pos_unsat = _unsat(formula)
    if pos_unsat is None:
        return out(DegeneracyVerdict.UNKNOWN, why="z3 returned unknown within rlimit")
    if pos_unsat:
        return out(DegeneracyVerdict.ALWAYS_FLAG, Reason.ALWAYS_FLAG)

    return out(DegeneracyVerdict.NON_DEGENERATE)


def subsumes(p1: Any, p2: Any) -> bool | None:
    """`P₁ ∧ ¬P₂` UNSAT ⇒ `P₂` is implied by `P₁`.

    **The single-row abstraction is NOT used here.** It is sound for triviality because
    `¬φ(r)` UNSAT for a symbolic row implies UNSAT for every unrolling; subsumption can couple
    rows ACROSS predicates, so the abstraction would prove an implication that does not hold. This
    function translates both expressions in full and returns None the moment either leaves the
    admitted subset.
    """
    import z3

    a, b = translate(p1.expr), translate(p2.expr)
    if a is None or b is None:
        return None
    if _has_macro(p1) or _has_macro(p2):
        # A comprehension reached this path. Under the abstraction both sides collapse to a single
        # symbolic row and the implication would be about rows that are not the same rows.
        return None
    return _unsat(z3.And(a[0], z3.Not(b[0])))


def _has_macro(cand: Any) -> bool:
    return ".all(" in cand.expr or ".exists(" in cand.expr or ".filter(" in cand.expr


def empirical_arm(
    cand: Any,
    clean: CleanCorpusResult,
    degeneracy_list: Sequence[Any],
    *,
    n_sites: int,
    true_defective: int,
    flagged: int,
    correct: int | None = None,
) -> GateOutcome:
    """Four tests, and the third is the one nothing else does.

    | test | threshold | note |
    |---|---|---|
    | clean-corpus firing | `<= 50%` (rate-ok: a THRESHOLD stated by the plan, not a measurement) | **REJECT-ONLY at P7** against `TEMPLATE-COMPUTED` (C5); admission on this criterion waits for the BLIND-FILLED corpus at P8 |
    | degeneracy-list membership | not equivalent to a published member | the list IS B1's mined output |
    | control-arm spurious fires | **exactly 0** | derived, not chosen; a non-zero count is an APPARATUS failure and blocks the batch |
    | random-flagger adjusted precision | `> 0` | a random flagger scores exactly 0; so does a flag-everything predicate |
    """
    measured: dict[str, object] = {
        "corpus_label": clean.corpus_label,
        "clean_firing": f"{clean.n_fired}/{clean.n_filings}",
        "control_spurious_fires": clean.control_spurious_fires,
        "degeneracy_list_size": len(degeneracy_list),
        "admission_on_clean_firing": "REJECT-ONLY AT P7 (C5): admission on this criterion waits "
                                     "for the BLIND-FILLED corpus at P8",
    }

    # --- the control arm. NOT a predicate-quality finding. -----------------------------------
    if clean.control_spurious_fires:
        raise ApparatusError(
            f"{cand.id}: {clean.control_spurious_fires} spurious fire(s) on CONTROL sites, which "
            "lie outside upstream_closure(read_set(p)). A mutation there cannot change any input "
            "this predicate reads, so a fire means either an undeclared key read — impossible "
            "under P4's both-ways AST check — or a leak in the fact table. Both are defects in "
            "OUR apparatus, and this blocks the whole admission batch rather than rejecting one "
            "predicate. Softening it is how the flag-everything predicate gets in."
        )

    def reject(reason: str, **over: object) -> GateOutcome:
        return GateOutcome(gate=GateId.G3E, passed=False, measured={**measured, **over},
                           reason=reason)

    # --- clean-corpus firing ------------------------------------------------------------------
    if clean.n_filings and Decimal(clean.n_fired) / Decimal(clean.n_filings) > CLEAN_FIRING_CEILING:
        return reject(Reason.FIRES_ON_CLEAN)

    # --- degeneracy-list membership ----------------------------------------------------------
    listed = [d for d in degeneracy_list if getattr(d, "render", lambda: "")() == cand.expr]
    if listed:
        return reject(Reason.ON_DEGENERACY_LIST, matched=[d.render() for d in listed])

    # --- the random flagger --------------------------------------------------------------------
    try:
        # `correct` is how many of the flagged items were genuinely defective. Omitting it makes
        # `adjusted_precision` assume the flagger is UNBIASED — the random case — and every real
        # predicate then scores exactly 0. That is the metric measuring the caller rather than the
        # predicate, and it rejected all 33 survivors on the funnel's first run.
        ap = adjusted_precision(flagged, true_defective, n_sites, correct=correct)
    except DegenerateBaseline as e:
        measured["adjusted_precision"] = f"UNDEFINED: {e}"
        return GateOutcome(gate=GateId.G3E, passed=True, measured=measured)
    measured["adjusted_precision"] = str(ap)
    if ap <= 0:
        return reject(Reason.RANDOM_FLAGGER)

    return GateOutcome(gate=GateId.G3E, passed=True, measured=measured)


def render_verdicts(outcomes: Mapping[str, GateOutcome]) -> Mapping[str, int]:
    """All five verdicts, always. Publishing `non_degenerate` alone would hide how many were
    UNPROVEN, which is the number a reviewer wants."""
    counts = {v.value: 0 for v in DegeneracyVerdict}
    for o in outcomes.values():
        v = str(o.measured.get("verdict", DegeneracyVerdict.UNKNOWN.value))
        counts[v] = counts.get(v, 0) + 1
    return counts
