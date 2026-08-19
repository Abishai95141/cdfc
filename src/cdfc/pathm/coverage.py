"""The rule-coverage declaration: *of N published at date D, we executed M — and here is why not.*

**This is the product claim, and its shape is the whole point.** Every incumbent reports what it
FOUND. This reports what it never LOOKED AT, over a denominator the publisher fixed rather than one
we chose — `N` is a property of the regulator's own artefact, named by its digest and its date.

Three properties are deliberate and each was paid for elsewhere in this build:

**The arithmetic closes.** `executed + sum(not executed) == N`, asserted, because a funnel whose
stages do not sum is a funnel that lost rules silently.

**Every reason is from a CLOSED vocabulary.** `docs/OPEN-ITEMS.md` records that a bucket counted
under a reason that is not true of it under-reports honestly and is still wrong. Four buckets in
this build were exactly that before they were read: 1,323 rules called `unparseable` were using
parenthesised row lists, 513 more were addressing ranges, and 114 more carried a third axis.

**No fraction renders without both integers.** `ci/no-bare-rate.sh` enforces it; the declaration
carries counts and lets the reader divide.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from cdfc.pathm.compile import Compiled, Refused, compile_rule
from cdfc.pathm.reader import read
from cdfc.pathm.statement import NotExecuted, RuleSet


@dataclass(frozen=True, slots=True)
class RuleCoverage:
    source_name: str
    source_sha256: str
    published_at: str
    published: int                                  # N, fixed by the publisher
    executed: int                                   # M
    not_executed: tuple[tuple[NotExecuted, int], ...]
    data_points: int

    def __post_init__(self) -> None:
        total = self.executed + sum(n for _r, n in self.not_executed)
        if total != self.published:
            raise ValueError(
                f"the declaration does not close: {self.executed} executed + "
                f"{total - self.executed} not executed = {total}, but {self.published} were "
                "published. A coverage table whose stages do not sum has lost rules silently."
            )

    def lines(self) -> tuple[str, ...]:
        out = [
            f"source            {self.source_name}",
            f"  sha256          {self.source_sha256}",
            f"  published at    {self.published_at}",
            "",
            f"of {self.published} rules published at {self.published_at}, "
            f"we executed {self.executed}.",
            "",
            "the typed reason for each of the other "
            f"{self.published - self.executed}:",
        ]
        for reason, n in self.not_executed:
            out.append(f"  {reason.value:28} {n:6} of {self.published}")
        out += ["", f"data points addressed by executed rules  {self.data_points}"]
        return tuple(out)


def declare(blob: Path) -> RuleCoverage:
    """Read, compile, and declare. **Nothing in this call graph reaches a model.**"""
    rs: RuleSet = read(blob)
    executed: list[Compiled] = []
    refused: Counter[NotExecuted] = Counter()
    for rule in rs.rules:
        result = compile_rule(rule)
        if isinstance(result, Compiled):
            executed.append(result)
        elif isinstance(result, Refused):
            refused.update([result.reason])
    return RuleCoverage(
        source_name=rs.source_name,
        source_sha256=rs.source_sha256,
        published_at=rs.published_at,
        published=len(rs),
        executed=len(executed),
        # Sorted by the vocabulary's own order, not by size: a table that reorders itself as the
        # numbers move is a table nobody can diff between releases.
        not_executed=tuple((r, refused[r]) for r in NotExecuted if refused[r]),
        data_points=sum(len(c.anchors) for c in executed),
    )
