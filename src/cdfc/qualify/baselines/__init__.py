"""P7-B3 — the three free baselines a candidate must beat.

**Why a baseline at all.** SPADE's own paper records that selecting **all** generated candidates
yields 100% coverage at 100% false-failure rate (rate-ok: quoted from SPADE's own paper, not
measured here). And a published neural oracle was beaten on 68.9% of its bugs (rate-ok: a
published figure, quoted), at twice its precision, by `NoException` — *"the code did not throw"*. A gate that
does not compare against the free thing is a gate that cannot tell an expensive check from a cheap
one.

**MARGINAL KILL IS A SET DIFFERENCE.** `|kills(p)| − |kills(B)|` can be negative while `p` still
catches mutants `B` misses, and it is precisely the mutants `B` misses that make `p` worth having.
So every marginal figure here is `|kills(p) \\ kills(B)|` over the SAME campaign — one denominator,
two sets, no comparison of studies.

**And it is reported against each baseline separately, never against the union alone**, because a
union figure hides which baseline did the work.

| baseline | what it is | how its kill set is derived |
|---|---|---|
| `B0` | the template's own checkable relations | the harvest's own formula-derived identity classes: the relations the regulator's blank ALREADY encodes, before any of our work |
| `B1` | mined invariants over the clean filing, at a declared confidence | `b1_invariants.py` — **NOT Daikon**, and it says so |
| `B2` | the degenerate arm: *"no cell is blank and no cell errors"* | a mutant whose recorded edit leaves the cell blank or an error literal |
"""

from __future__ import annotations

from cdfc.qualify.baselines.b0_template import B0_CLASSES, kill_set as b0_kill_set
from cdfc.qualify.baselines.b1_invariants import Invariant, mine, kill_set as b1_kill_set
from cdfc.qualify.baselines.b2_degenerate import kill_set as b2_kill_set

__all__ = ["B0_CLASSES", "Invariant", "b0_kill_set", "b1_kill_set", "b2_kill_set", "mine"]
