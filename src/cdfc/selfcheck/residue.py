"""P10-B2 — `|RESIDUE|`: the count of WRONG mutants that nothing rejects.

*The first quantitative statement anyone has made about the limit of document-level verification
for a regulated filing.*

The procedure, verbatim from the spec, with the one thing it leaves implicit made explicit:

    1. Take the filing under test, F.
    2. Generate mutants of F under the declared, versioned fault model.
    3. Adjudicate each INNOCUOUS or WRONG.                              <- THE ONLY HUMAN STEP
    4. Run the full admitted predicate set AND every admitted relation over every WRONG mutant.
    5. RESIDUE := { WRONG mutants that no predicate and no relation rejects }
    6. Report |RESIDUE| and, per survivor, the class of falsehood it represents.

**Made explicit: step 4 runs the rejector set AS IT IS ON THE DAY, and that set is part of the
result.** `|RESIDUE| = 12` against an empty admitted set and `|RESIDUE| = 12` against 280 admitted
predicates are utterly different claims. So the result carries `{fault_model_version,
adjudication_record_sha256, registry_root, n_admitted_predicates, n_admitted_relations}` and
**`render()` refuses to print `|RESIDUE|` without all five.**

## On this build the admitted set is EMPTY, and that is a ceiling rather than a failure

The P7 funnel admits 0 of 348 and P9 admits 0 relations, so step 4's rejector set is empty and
**every WRONG mutant survives by construction.** `plan/05` P10's entry criteria anticipate exactly
this — *"on G-CORPUS's FAIL branch the admitted set is empty and the residue is computed over an
empty rejector set. **That is still a result** and it is a *ceiling*, published as such"* — and
NC-C07 exists to stop that ceiling being read as a strong measurement.

So this module computes and publishes **two** numbers, and the label travels with each:

| rejector set | what the number means |
|---|---|
| `ADMITTED` (empty) | the **CEILING**: `\\|RESIDUE\\| = wrong_total`. No check has been admitted, so nothing is claimed to be caught |
| `PRE-GATE` (the harvested fixture set) | what the harvest would catch **if** it were admitted. `PRE-GATE`, and not admissible in any gate, tier or published rate |

Reporting only the second would be quoting a rejector set nobody admitted; reporting only the
first would hide a measurement we have. Both, labelled.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final, Literal

from cdfc.selfcheck.adjudication import AdjudicationRecord, Verdict

MutantId = str

RejectorSet = Literal["ADMITTED", "PRE-GATE"]

# The five fields without which `|RESIDUE|` does not render. NC-C07.
REQUIRED: Final[tuple[str, ...]] = (
    "fault_model_version",
    "adjudication_record_sha256",
    "registry_root",
    "n_admitted_predicates",
    "n_admitted_relations",
)

CEILING_LABEL: Final[str] = (
    "CEILING — computed against an EMPTY admitted set. No predicate and no relation has been "
    "admitted, so every WRONG mutant survives by construction and this number is an upper bound "
    "on the residue, not a measurement of it."
)
PRE_GATE_LABEL: Final[str] = (
    "PRE-GATE — computed against harvested candidates that have NOT been through the gates. It "
    "may not be cited in a gate, in a severity tier, or in any published rate."
)


class ResidueError(ValueError):
    """A residue that must not be reported."""


@dataclass(frozen=True, slots=True)
class ResidueResult:
    survivors: tuple[MutantId, ...]
    wrong_total: int                 # THE DENOMINATOR
    innocuous_total: int
    unadjudicable_total: int         # INDETERMINATE: excluded from BOTH, counted here
    registry_root: str
    n_admitted_predicates: int
    n_admitted_relations: int
    fault_model_version: str
    adjudication_record_sha256: str
    rejector_set: RejectorSet
    by_class: Mapping[str, int] = None  # type: ignore[assignment]

    @property
    def size(self) -> int:
        return len(self.survivors)

    @property
    def label(self) -> str:
        return CEILING_LABEL if self.rejector_set == "ADMITTED" else PRE_GATE_LABEL

    def missing_fields(self) -> tuple[str, ...]:
        out = []
        for name in REQUIRED:
            value = getattr(self, name)
            if value is None or (isinstance(value, str) and not value.strip()):
                out.append(name)
        return tuple(out)

    def as_row(self) -> dict[str, Any]:
        return {
            "residue": self.size,
            "wrong_total": self.wrong_total,
            "innocuous_total": self.innocuous_total,
            "unadjudicable_total": self.unadjudicable_total,
            "registry_root": self.registry_root,
            "n_admitted_predicates": self.n_admitted_predicates,
            "n_admitted_relations": self.n_admitted_relations,
            "fault_model_version": self.fault_model_version,
            "adjudication_record_sha256": self.adjudication_record_sha256,
            "rejector_set": self.rejector_set,
            "label": self.label,
            "by_class": dict(sorted((self.by_class or {}).items())),
        }


def compute_residue(
    mutants: Sequence[Mapping[str, Any]],
    adjudication: AdjudicationRecord,
    rejected: Mapping[MutantId, Sequence[str]],
    *,
    registry_root: str,
    n_admitted_predicates: int,
    n_admitted_relations: int,
    rejector_set: RejectorSet,
    unadjudicable: Iterable[MutantId] = (),
) -> ResidueResult:
    """RESIDUE := { WRONG mutants that no predicate and no relation rejects }.

    `rejected` maps a mutant id to the ids that rejected it — `killed_by` from the campaign, plus
    any relation rejection. A mutant absent from that map, or present with an EMPTY list, survives.

    **An unadjudicated mutant RAISES.** It is not defaulted to INNOCUOUS (which would shrink the
    denominator) and not to WRONG (which would grow the residue). Both directions are a judgement
    nobody made, and one of them flatters us.
    """
    skip = set(unadjudicable)
    wrong: list[MutantId] = []
    innocuous = 0
    by_class: dict[str, int] = {}

    for m in mutants:
        mid = str(m["mutant_sha256"])
        if mid in skip:
            continue
        verdict: Verdict = adjudication.verdict_of(mid)      # raises if absent
        if verdict == "INNOCUOUS":
            innocuous += 1
            continue
        wrong.append(mid)
        if not rejected.get(mid):
            by_class[str(m.get("fault_class", "?"))] = by_class.get(str(m.get("fault_class", "?")), 0) + 1

    survivors = tuple(sorted(m for m in wrong if not rejected.get(m)))
    return ResidueResult(
        survivors=survivors,
        wrong_total=len(wrong),
        innocuous_total=innocuous,
        unadjudicable_total=len(skip),
        registry_root=registry_root,
        n_admitted_predicates=n_admitted_predicates,
        n_admitted_relations=n_admitted_relations,
        fault_model_version=adjudication.fault_model_version,
        adjudication_record_sha256=adjudication.digest(),
        rejector_set=rejector_set,
        by_class=by_class,
    )


def render(result: ResidueResult) -> str:
    """`|RESIDUE|` with all five of its fields, or a refusal. NC-C07.

    An unqualified `|RESIDUE| = 12` is not a smaller claim than a qualified one; it is a different
    and false one, because the reader supplies the missing rejector set from their own optimism.
    """
    missing = result.missing_fields()
    if missing:
        raise ResidueError(
            f"refusing to render |RESIDUE| without {list(missing)}. The number means nothing "
            "without the set it was computed against: |RESIDUE| = 12 against an empty admitted "
            "set and |RESIDUE| = 12 against 280 admitted predicates are utterly different claims, "
            "and a reader given only the number supplies the difference from their own optimism."
        )
    lines = [
        f"|RESIDUE| = {result.size} of {result.wrong_total} WRONG mutants",
        f"  rejector set          {result.rejector_set}: "
        f"{result.n_admitted_predicates} predicates, {result.n_admitted_relations} relations",
        f"  registry root         {result.registry_root}",
        f"  fault model           {result.fault_model_version}",
        f"  adjudication record   {result.adjudication_record_sha256}",
        f"  INNOCUOUS excluded    {result.innocuous_total}   "
        f"(they cannot be killed and must not be counted)",
        f"  unadjudicable         {result.unadjudicable_total}   "
        f"(INDETERMINATE: our evaluator could not decide what the document says)",
        "",
        f"  {result.label}",
    ]
    if result.by_class:
        lines.append("")
        lines.append("  survivors by class of falsehood:")
        for cls, n in sorted(result.by_class.items()):
            lines.append(f"    {cls}  {n}")
    return "\n".join(lines)


def not_inflatable(before: ResidueResult, after: ResidueResult) -> bool:
    """**Adding predicates cannot GROW the residue.** For `S ⊆ S'`, `RESIDUE(S') ⊆ RESIDUE(S)`.

    Monotone by construction — a mutant rejected by `S` is rejected by every superset of `S` — and
    asserted anyway, because "monotone by construction" is how a wrong optimisation ships.
    """
    return set(after.survivors) <= set(before.survivors)
