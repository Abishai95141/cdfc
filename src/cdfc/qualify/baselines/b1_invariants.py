"""B1 — mined invariants over the clean filing. **THIS IS NOT DAIKON, AND IT SAYS SO.**

`plan/04` specifies *"Daikon over the clean corpus at `--conf_limit 0.99`; its trivia output
doubles as the degeneracy list"*. Daikon is a JVM tool that is not in this repository, is not in
the lockfile, and whose licence `docs/LICENCES.md` records as unopened. **Vendoring a name we did
not run would be the worst available outcome**: a baseline nobody can reproduce, cited as if it
were the published instrument.

So this is a small, inspectable invariant miner written here, and every claim about it is scoped
to what it does:

* **What it does.** Over one clean filing it mines four templates per numeric cell —
  `>= 0`, `<= 0`, `== k`, `is an integer` — and keeps an invariant only if it holds on **every**
  observation, which is the `--conf_limit 1.0` corner of Daikon's confidence rule, not `0.99`.
* **What it does NOT do.** No relations BETWEEN variables (Daikon's `x == y`, `x < y`,
  `x == a*y + b`), no sequence or container invariants, no statistical confidence, no
  implications. **Its recall against Daikon's is unmeasured and unmeasurable here.**
* **What that costs.** B1 is a WEAKER baseline than the plan specified, so a candidate's marginal
  kill over B1 is an OVERSTATEMENT of its marginal kill over Daikon. That direction flatters us,
  it is stated wherever B1's number is printed, and it is the reason B1's figure never appears
  without this sentence.

**One observation is not a corpus.** With a single clean filing every invariant that holds holds
trivially, so the mined set is presented as a DEGENERACY LIST — *"relations that are true of a
correct filing and therefore cannot distinguish one"* — rather than as a specification. That is
the use `plan/04` puts B1's trivia output to anyway.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final, Literal

NOT_DAIKON: Final[str] = (
    "B1 is a local invariant miner, NOT Daikon: four single-variable templates at confidence 1.0, "
    "no inter-variable relations. Marginal kill over it OVERSTATES marginal kill over Daikon."
)

Template = Literal["nonneg", "nonpos", "constant", "integral"]


@dataclass(frozen=True, slots=True)
class Invariant:
    cell: str  # "Sheet!REF"
    template: Template
    k: Decimal | None  # the constant, for `constant`

    def holds(self, value: Decimal) -> bool:
        if self.template == "nonneg":
            return value >= 0
        if self.template == "nonpos":
            return value <= 0
        if self.template == "constant":
            return self.k is not None and value == self.k
        return value == value.to_integral_value()

    def render(self) -> str:
        return {
            "nonneg": f"{self.cell} >= 0", "nonpos": f"{self.cell} <= 0",
            "constant": f"{self.cell} == {self.k}", "integral": f"{self.cell} is an integer",
        }[self.template]


def mine(observations: Sequence[Mapping[str, Decimal]]) -> tuple[Invariant, ...]:
    """Every template that holds on EVERY observation. Confidence 1.0, stated rather than tuned."""
    if not observations:
        return ()
    cells = sorted(set().union(*(set(o) for o in observations)))
    out: list[Invariant] = []
    for cell in cells:
        vals = [o[cell] for o in observations if cell in o]
        if not vals:
            continue
        for tmpl, k in (("nonneg", None), ("nonpos", None), ("integral", None),
                        ("constant", vals[0])):
            inv = Invariant(cell=cell, template=tmpl, k=k)  # type: ignore[arg-type]
            if all(inv.holds(v) for v in vals):
                out.append(inv)
    return tuple(out)


def _edited_value(new_xml: str) -> Decimal | None:
    """By PARSING the fragment. `ci/no-regex-over-xml.sh` caught the pattern version."""
    from cdfc.qualify.baselines.b2_degenerate import cell_value

    has_v, text = cell_value(new_xml)
    if not has_v:
        return None
    try:
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return None


def kill_set(stored, killed_rows: Sequence[Mapping], invariants: Sequence[Invariant]) -> frozenset[str]:
    """The mutants B1 kills: those whose recorded edit VIOLATES a mined invariant at that cell.

    Evaluated against the edit already committed in `killed.jsonl`, so nothing is re-run and
    nothing is re-measured — the same evidence, read through a different rule.
    """
    by_cell: dict[str, list[Invariant]] = {}
    for inv in invariants:
        by_cell.setdefault(inv.cell, []).append(inv)
    out: set[str] = set()
    for row in killed_rows:
        if row.get("observability") != "OBSERVABLE":
            continue
        for e in row.get("edits") or ():
            cell = f"{e.get('sheet_name')}!{e.get('ref')}"
            v = _edited_value(e.get("new_xml", ""))
            if v is None:
                continue
            if any(not inv.holds(v) for inv in by_cell.get(cell, ())):
                out.add(row["mutant_sha256"])
                break
    return frozenset(out)
