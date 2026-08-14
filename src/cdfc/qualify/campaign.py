"""P6-B3 — the Campaign record and its arithmetic. **Six integers, never a bare percentage.**

    GENERATED     G
    UNOBSERVABLE  U   recalculated grid identical, NO not_run cell traversed   — excluded from O
    INDETERMINATE I   recalculated grid identical, but a not_run cell WAS      — excluded from O
    OBSERVABLE    O = G − U − I
    UNREACHABLE   R   observable, but no distinguishing cell lies in any admitted read set
    KILLED        K   at least one predicate returned FAIL, under the P5 verdict model

    KILL RATE  KR = K/O     ← the headline. NEVER K/G. NEVER K/(G−E). NEVER K/(G−U) with I folded in.
    REACHABLE RKR = K/(O−R)
    UNOBS RATE  UR = U/G    ← a property of OUR OPERATOR MIX
    INDET RATE  IR = I/G    ← a property of OUR EVALUATOR, printed beside UR every time (F18)

`MS = |killed| / (|mutants| − |equivalent|)` needs `|equivalent|`, which is undecidable in general.
`K/O` needs no such term **because our mutants are data: "observable" is a diff, measured by
recalculation, whereas "equivalent" is a theorem.**

**`render()` never emits `U/G` without `I` beside it.** A build that cannot evaluate a cell would
otherwise bank that cell's mutants as unobservable and RAISE its own `K/O`, because `O = G − U − I`
is the denominator — the measurement error correlated with the quantity being measured, in the
direction that flatters us.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Final

from cdfc.qualify.fault_model import FAULT_CLASSES, FAULT_MODEL_VERSION, HARNESS_VERSION


class CampaignArithmeticError(ArithmeticError):
    """A rate whose denominator is zero. A campaign that observed nothing has told us nothing,
    and printing `0.0` for it would be a number with no information presented as a measurement."""


@dataclass(frozen=True, slots=True)
class ClassTally:
    G: int = 0
    U: int = 0
    I: int = 0  # noqa: E741 — the plan's name for the indeterminate count; renaming it hides F18
    O: int = 0  # noqa: E741
    R: int = 0
    K: int = 0

    def __post_init__(self) -> None:
        if self.O != self.G - self.U - self.I:
            raise CampaignArithmeticError(
                f"O={self.O} but G-U-I={self.G - self.U - self.I}. O is DEFINED as G−U−I; a tally "
                "that carries its own O is a tally that can disagree with its own arithmetic."
            )
        if self.K > self.O:
            raise CampaignArithmeticError(
                f"K={self.K} > O={self.O}: more mutants killed than were observable. The harness "
                "v1 printed 100.1% this way."  # rate-ok: the historical defect, named as one
            )
        if self.R > self.O:
            raise CampaignArithmeticError(f"R={self.R} > O={self.O}")
        if min(self.G, self.U, self.I, self.O, self.R, self.K) < 0:
            raise CampaignArithmeticError("a negative count")

    def __add__(self, other: ClassTally) -> ClassTally:
        return ClassTally(
            G=self.G + other.G, U=self.U + other.U, I=self.I + other.I,
            O=self.O + other.O, R=self.R + other.R, K=self.K + other.K,
        )

    def as_row(self) -> dict[str, int]:
        return {"G": self.G, "U": self.U, "I": self.I, "O": self.O, "R": self.R, "K": self.K}


def tally(*, G: int, U: int, I: int, R: int = 0, K: int = 0) -> ClassTally:  # noqa: E741
    return ClassTally(G=G, U=U, I=I, O=G - U - I, R=R, K=K)


@dataclass(frozen=True, slots=True)
class Campaign:
    campaign_id: str
    by_fault_class: Mapping[str, ClassTally]
    fault_model_version: str = FAULT_MODEL_VERSION
    fault_model_digest: str = ""
    harness_version: str = HARNESS_VERSION
    site_set_digest: str = ""
    evaluator_version: str = ""
    base_sha256: str = ""
    sampling_rule: str = ""
    indeterminate_cells: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    # THE PREDICATE SET THE CAMPAIGN CREDITED, AS A DIGEST.
    #
    # `killed.jsonl` records `killed_by: [<predicate id>]`, and G2 joins those ids to the CURRENT
    # candidate set to score every per-predicate kill vector. The harvest re-assigned ids twice
    # after this campaign was recorded (P7-B1's `<F|V>` discriminator, P8-B1's wildcard repair), so
    # 125 of the 126 credited ids carried a DIFFERENT `expr` at HEAD — `P-0009` went from a COUNTIF
    # tally to a vocabulary membership check on another range — and the only guard on the join was
    # a fault-model version string. G2 rejected 302 and admitted 46 on that evidence.
    #
    # An id is not an identity. This digest is over `(id, code_sha256)` for every candidate, so a
    # campaign whose predicates have moved refuses to be joined instead of answering about
    # somebody else.
    predicate_set_digest: str = ""

    @property
    def totals(self) -> ClassTally:
        out = ClassTally()
        for t in self.by_fault_class.values():
            out = out + t
        return out

    def kill_rate(self) -> Fraction:
        t = self.totals
        if t.O == 0:
            raise CampaignArithmeticError(
                "O == 0: nothing was observable, so this campaign has told us nothing. It does "
                "not print 0.0."
            )
        return Fraction(t.K, t.O)

    def reachable_kill_rate(self) -> Fraction:
        t = self.totals
        if t.O - t.R == 0:
            raise CampaignArithmeticError("O == R: every observable mutant was unreachable")
        return Fraction(t.K, t.O - t.R)

    def unobservable_rate(self) -> Fraction:
        t = self.totals
        if t.G == 0:
            raise CampaignArithmeticError("G == 0: no mutants were generated")
        return Fraction(t.U, t.G)

    def indeterminate_rate(self) -> Fraction:
        t = self.totals
        if t.G == 0:
            raise CampaignArithmeticError("G == 0: no mutants were generated")
        return Fraction(t.I, t.G)

    def render(self) -> str:
        """Six integers, `U/G`, `I/G` and the per-class vector. Never a lone percentage."""
        t = self.totals
        lines = [
            f"campaign {self.campaign_id}",
            f"  fault model {self.fault_model_version} ({self.fault_model_digest[:16]})  "
            f"harness {self.harness_version}  evaluator {self.evaluator_version}",
        ]
        if self.sampling_rule:
            lines.append(f"  sampling rule: {self.sampling_rule}")
        lines += [
            "",
            "  class    G      U      I      O      R      K   K/O",
            "  " + "-" * 52,
        ]
        for c in FAULT_CLASSES:
            v = self.by_fault_class.get(c.id, ClassTally())
            kr = f"{v.K}/{v.O}" if v.O else "—  (nothing observable)"
            lines.append(
                f"  {c.id}  {v.G:5d}  {v.U:5d}  {v.I:5d}  {v.O:5d}  {v.R:5d}  {v.K:5d}   {kr}"
            )
        lines += [
            "  " + "-" * 52,
            f"  TOTAL {t.G:5d}  {t.U:5d}  {t.I:5d}  {t.O:5d}  {t.R:5d}  {t.K:5d}",
            "",
            # U/G and I/G ALWAYS in the same string. F18: without I beside it, U/G describes our
            # apparatus while claiming to describe the fault model.
            f"  U/G = {t.U}/{t.G}   I/G = {t.I}/{t.G}   (I is OUR EVALUATOR, not the fault model)",
            f"  K/O = {t.K}/{t.O}" if t.O else "  K/O = undefined: nothing was observable",
        ]
        if t.O and t.O != t.R:
            lines.append(f"  K/(O-R) = {t.K}/{t.O - t.R}")
        lines.append("")
        lines.append(
            "  This says: the predicate set rejects K of O observable defects seeded under fault "
            f"model {self.fault_model_version}, of which U of G were discarded as unobservable and "
            "I of G could not be adjudicated by our own evaluator. It does NOT say what fraction "
            "of real filing errors are detected — the bridge is the coupling effect and there is "
            "no coupling study for financial filing data."
        )
        return "\n".join(lines)

    def as_manifest(self) -> dict[str, Any]:
        t = self.totals
        return {
            "campaign_id": self.campaign_id,
            "fault_model_version": self.fault_model_version,
            "fault_model_digest": self.fault_model_digest,
            "harness_version": self.harness_version,
            "site_set_digest": self.site_set_digest,
            "evaluator_version": self.evaluator_version,
            "base_sha256": self.base_sha256,
            "sampling_rule": self.sampling_rule,
            "predicate_set_digest": self.predicate_set_digest,
            "totals": t.as_row(),
            "by_fault_class": {k: v.as_row() for k, v in sorted(self.by_fault_class.items())},
            "unobservable_rate": f"{t.U}/{t.G}",
            "indeterminate_rate": f"{t.I}/{t.G}",
            "kill_rate": f"{t.K}/{t.O}" if t.O else None,
        }


V0_BASELINE: Final[Mapping[str, int]] = {"generated": 19782, "killed": 3574, "equivalent": 22}


def restate_v0(baseline: Mapping[str, int] = V0_BASELINE) -> str:
    """The v0 harness printed `MS = 3,574 / (19,782 − 22) = 18.09%`. This module REFUSES that form.  # rate-ok: the form being refused, quoted verbatim

    `E` (equivalence) is a THEOREM — undecidable in general, and v0's 22 were the round-to-integer
    operator's straddles, asserted rather than proved. `U` (unobservability) is a DIFF, measured by
    recalculation. They are not the same quantity and the denominators are not interchangeable.
    """
    g, k, e = baseline["generated"], baseline["killed"], baseline["equivalent"]
    return (
        f"v0 published MS = {k}/{g - e} = {k} killed over {g} generated less {e} asserted "
        f"equivalents. This build does not compute that "
        f"form: `E` is a theorem and `U` is a diff. v0's {e} 'equivalents' were all produced by the "
        "round-to-integer operator and were asserted, not proved. A further observation from v0 "
        "that is not arithmetic: every arithmetic operator killed at exactly 18.1%, identical to "  # rate-ok: v0's historical figure
        "the fraction of sites inside the field graph — for identity predicates that number is "
        "REACH, not QUALITY, and this report says which it is showing."
    )
