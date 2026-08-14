"""P10-B3 — the adjudication record, its refusals, and Cohen's κ.

**What makes `|RESIDUE|` reproducible by a stranger** is not the fault model alone: it is the
fault model *and the adjudication record*, both content-addressed. Saying *"a third party can
re-run it"* without naming the adjudication record would repeat the error this whole specification
exists to correct.

## The record

    adjudication/<fault_model_version>/<filing_sha8>.jsonl   — one line per mutant, sorted by id

    {"mutant_id":"sha256:…","verdict":"WRONG","argument":"…","adjudicated_by":"…",
     "adjudicated_at":"2026-08-14","round":1}

`adjudication_record_sha256` is the RFC 8785 digest of the **sorted** file. **A verdict with no
`argument` is refused by the loader** — the same rule as `docs/EQUIVALENT-MUTANTS.md`, and for the
same reason: an adjudication without an argument is an opinion wearing a schema.

## κ, and why this build publishes it as UNMEASURED

`plan/05` P10-B3 requires a **second adjudicator who is not the first**, re-rating a seeded sample of
20 in every 100, and publishes Cohen's κ with its `n`. NC-N02 records that the INNOCUOUS/WRONG judgement
cannot be negatively controlled — injecting a wrong label is trivial, but the *correct* label is
the human's — and the prescribed substitute is exactly that second rater.

**There is no second rater on this project.** Everything else this build lacked a human for had a
mechanical substitute that was weaker in a stateable way: LibreOffice for an independent evaluator,
a foreign engine for arm 2, `SINGLE-SIGNER` for a second reviewer. **κ has no such substitute**,
and the two candidates are both worse than nothing:

- re-running the same rules produces κ = 1.0 by construction, which is a lie with a number on it;
- running a *second rule set* and calling its agreement κ dresses a mechanical agreement as an
  adjudication agreement — the "a count agreeing with a pin is evidence about the count" defect
  this project has now found seven times.

So `cohens_kappa` is built, tested against hand-computed vectors in both directions, and the
seeded-sample machinery works — and `docs/measurements/P10-residue.md` publishes **κ: UNMEASURED,
n = 0**, with the blocker named, and P10's exit criterion 7 is recorded **NOT MET**. A number with
a declared weakness is admissible; a number with an undeclared one is the thing we are against, and
a fabricated one is worse than either.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Final, Literal

from cdfc.canon import canonical_json, sha256_hex

Verdict = Literal["INNOCUOUS", "WRONG"]
VERDICTS: Final[frozenset[str]] = frozenset({"INNOCUOUS", "WRONG"})

# What a rater who is not a person must be labelled as, on every surface that quotes a number
# derived from this record. The same discipline as `SINGLE-SIGNER — a weaker review` and
# `SAME-AUTHOR — a weaker instrument`.
RULE_BASED: Final[str] = "RULE-BASED-v1 — a weaker adjudication, not a human judgement"

# The threshold `plan/05` explicitly refuses to invent one above. Below it the raters reconcile in
# writing and BOTH κ values are published; there is no silent re-rate and there is no pass mark.
RECONCILIATION_TRIGGER: Final[Decimal] = Decimal("0.6")


class AdjudicationError(ValueError):
    """A record that does not load. Never a warning — an unloadable record is not a record."""


@dataclass(frozen=True, slots=True)
class AdjudicationRow:
    mutant_id: str
    verdict: Verdict
    argument: str
    adjudicated_by: str
    adjudicated_at: str
    round: int = 1

    def __post_init__(self) -> None:
        if self.verdict not in VERDICTS:
            raise AdjudicationError(
                f"{self.mutant_id[:12]}: verdict {self.verdict!r} is not one of {sorted(VERDICTS)}"
            )
        if not self.argument or not self.argument.strip():
            raise AdjudicationError(
                f"{self.mutant_id[:12]}: a verdict with no argument is refused. An adjudication "
                "without an argument is an opinion wearing a schema — and |RESIDUE|'s whole claim "
                "is that a stranger can re-derive it, which means disagreeing with the reasons."
            )
        if not self.adjudicated_by:
            raise AdjudicationError(f"{self.mutant_id[:12]}: no adjudicator named")

    def as_row(self) -> dict[str, Any]:
        return {
            "mutant_id": self.mutant_id, "verdict": self.verdict, "argument": self.argument,
            "adjudicated_by": self.adjudicated_by, "adjudicated_at": self.adjudicated_at,
            "round": self.round,
        }


@dataclass(frozen=True, slots=True)
class AdjudicationRecord:
    """The whole record, plus the commitment made before round 1 began."""

    rows: tuple[AdjudicationRow, ...]
    fault_model_version: str
    filing_sha256: str
    sample_seed: int
    sample_fraction: str          # "20/100" — two integers, never a rate (R3)
    seed_committed_at: str        # the date the seed was written down
    rater_label: str = RULE_BASED

    def __post_init__(self) -> None:
        ids = [r.mutant_id for r in self.rows if r.round == 1]
        if len(set(ids)) != len(ids):
            raise AdjudicationError("a mutant is adjudicated twice in round 1")
        first = min((r.adjudicated_at for r in self.rows if r.round == 1), default=None)
        if first is not None and self.seed_committed_at > first:
            # The same rule `test_corpus__brief_predates_first_workbook` applies to the fill brief.
            raise AdjudicationError(
                f"the sample seed was committed on {self.seed_committed_at}, after the first "
                f"adjudication on {first}. **A commitment made after seeing the result is not a "
                "commitment**: a sample drawn afterwards is a choice."
            )

    def by_round(self, n: int) -> dict[str, Verdict]:
        return {r.mutant_id: r.verdict for r in self.rows if r.round == n}

    def verdict_of(self, mutant_id: str) -> Verdict:
        """Raises on an unadjudicated mutant. **Never defaulted to either value.**"""
        for r in self.rows:
            if r.mutant_id == mutant_id and r.round == 1:
                return r.verdict
        raise AdjudicationError(
            f"{mutant_id[:12]} has no adjudication row. It is not defaulted to INNOCUOUS (which "
            "would shrink the denominator) or to WRONG (which would grow the residue). Both "
            "directions are a judgement nobody made."
        )

    def serialise(self) -> str:
        """NDJSON, **sorted by mutant id**, one line per row. The sort is explicit."""
        rows = sorted(self.rows, key=lambda r: (r.round, r.mutant_id))
        return "".join(canonical_json(r.as_row()).decode("utf-8") + "\n" for r in rows)

    def digest(self) -> str:
        """RFC 8785 over the sorted lines plus the pre-registered sample commitment.

        The seed is inside the digest deliberately: a record whose sample was drawn under a
        different seed is a different record, and `|RESIDUE|` cites this hash.
        """
        return sha256_hex(
            canonical_json(
                {
                    "rows": [r.as_row() for r in sorted(self.rows, key=lambda x: (x.round, x.mutant_id))],
                    "fault_model_version": self.fault_model_version,
                    "filing_sha256": self.filing_sha256,
                    "sample_seed": self.sample_seed,
                    "sample_fraction": self.sample_fraction,
                    "seed_committed_at": self.seed_committed_at,
                    "rater_label": self.rater_label,
                }
            )
        )

    def sample(self) -> tuple[str, ...]:
        """The pre-seeded re-rating sample. **Drawn by a seeded PRNG, deterministically.**

        `random.Random(seed).sample` is not used: its algorithm is not a documented stable
        interface across CPython versions, so a record re-checked on another version could produce
        a different sample from the same seed — and the seed is inside the digest. A sort on a
        keyed digest is stable for ever.
        """
        num, den = (int(x) for x in self.sample_fraction.split("/"))
        ids = sorted({r.mutant_id for r in self.rows if r.round == 1})
        k = len(ids) * num // den
        keyed = sorted(ids, key=lambda m: sha256_hex(f"{self.sample_seed}:{m}".encode()))
        return tuple(sorted(keyed[:k]))


def load(path: Path, **meta: Any) -> AdjudicationRecord:
    rows = tuple(
        AdjudicationRow(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    return AdjudicationRecord(rows=rows, **meta)


# --------------------------------------------------------------------------------------------
# Cohen's κ
# --------------------------------------------------------------------------------------------


def cohens_kappa(
    round1: Mapping[str, str], round2: Mapping[str, str]
) -> tuple[Decimal | None, int]:
    """`(κ, n)` over the mutants BOTH raters rated. **κ is never returned alone.**

    `Decimal`, not float: κ is published beside `|RESIDUE|` and a number nobody can re-derive to
    the last place is a number two readers can disagree about for no reason (R4).

    Returns `(None, n)` when κ is undefined — one rater, no overlap, or perfect chance agreement
    (`p_e == 1`, which happens when both raters used exactly one label). **`None` is not zero**:
    zero means *no better than chance*, `None` means *the statistic does not apply here*, and
    reporting the first for the second is the substitution this whole system exists to refuse.
    """
    shared = sorted(set(round1) & set(round2))
    n = len(shared)
    if n == 0:
        return None, 0
    agree = sum(1 for m in shared if round1[m] == round2[m])
    p_o = Decimal(agree) / Decimal(n)

    labels = set(round1[m] for m in shared) | set(round2[m] for m in shared)
    p_e = sum(
        (Decimal(sum(1 for m in shared if round1[m] == c)) / Decimal(n))
        * (Decimal(sum(1 for m in shared if round2[m] == c)) / Decimal(n))
        for c in labels
    )
    if p_e == 1:
        return None, n
    return ((p_o - p_e) / (Decimal(1) - p_e)), n


def render_kappa(kappa: Decimal | None, n: int, *, reason: str = "") -> str:
    """κ with its `n`, or the reason there is no κ. **Never κ alone, and never a bare number.**"""
    if kappa is None:
        return f"κ: UNMEASURED (n = {n}) — {reason or 'the statistic does not apply to this record'}"
    flag = "" if kappa >= RECONCILIATION_TRIGGER else (
        f"  ** below {RECONCILIATION_TRIGGER}: the two raters reconcile IN WRITING, the "
        "reconciliation is appended as round 3 with its own hash, and BOTH κ values are "
        "published. Never a silent re-rate. **"
    )
    return f"κ = {kappa.quantize(Decimal('0.0001'))} over n = {n} re-rated mutants{flag}"
