"""P7-B3 — the versioned domain policy, and the decision rule while its value is a PLACEHOLDER.

**Why a domain at all.** `c.v >= -1e17` is **not** trivially true over the unconstrained integers:
Z3 finds a counterexample at `-1e18`, `¬P ∧ domain` is SAT, and a naive proof arm **admits the
predicate**. ALR's five bounds are degenerate only relative to the range of values a money cell in
a regulatory filing can carry. So the proof arm asks `¬(P ∧ domain)` where `domain` is a declared,
versioned, per-dtype bound.

**The value has no argued basis anywhere in this corpus and this build does not invent one.**
`domain-policy-v1.json` renders the literal string `PLACEHOLDER`, exactly as
`pervasiveness-policy-v1.json` does for `K` and `T`.

**DECISION RULE, stated in advance rather than discovered:** while the policy is `PLACEHOLDER`,
`proof_arm` returns `UNKNOWN` for every pure-bound predicate and routes it to the empirical arm.
`UNKNOWN` is UNPROVEN, never `non_degenerate`. **The ALR rejection does not need the policy** — it
is demonstrated at G2 and at G3's empirical arm — so the open item blocks nothing, and that is why
it is allowed to stay open.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

POLICY_PATH: Final[Path] = Path("domain-policy-v1.json")
PLACEHOLDER: Final[str] = "PLACEHOLDER"


@dataclass(frozen=True, slots=True)
class DomainPolicy:
    version: str
    implausible_magnitude: object
    dtypes: Mapping[str, Mapping[str, object]]
    why_placeholder: str

    @property
    def is_placeholder(self) -> bool:
        return self.implausible_magnitude == PLACEHOLDER

    def bound_for(self, dtype: str) -> tuple[int | None, int | None] | None:
        """`(lo, hi)`, or None when this dtype's bound is still a PLACEHOLDER.

        Returning None rather than a default is the whole discipline: a default here would be an
        invented number deciding which predicates are degenerate.
        """
        row = self.dtypes.get(dtype)
        if not row:
            return None
        lo, hi = row.get("lo"), row.get("hi")
        if lo == PLACEHOLDER or hi == PLACEHOLDER:
            return None
        return (lo, hi)  # type: ignore[return-value]

    def render(self) -> str:
        if self.is_placeholder:
            return (
                f"domain-policy-{self.version}: implausible_magnitude = PLACEHOLDER. Every "
                "pure-bound predicate therefore reaches G3's proof arm as UNKNOWN and is decided "
                "empirically."
            )
        return f"domain-policy-{self.version}: implausible_magnitude = {self.implausible_magnitude}"


def load(path: Path = POLICY_PATH) -> DomainPolicy:
    doc = json.loads(path.read_text(encoding="utf-8"))
    return DomainPolicy(
        version=doc["version"],
        implausible_magnitude=doc["implausible_magnitude"],
        dtypes=doc.get("dtypes", {}),
        why_placeholder=doc.get("why_placeholder", ""),
    )
