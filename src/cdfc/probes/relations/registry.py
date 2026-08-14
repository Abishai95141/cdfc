"""P9-B2 — the relation registry, its loader, and the refusals the loader makes.

**The deliverable of this build is two counts, not a target.** An earlier version of this design
produced five relations of which **four false-alarm on a correct filing and the fifth is vacuous**.
The failure mode is *authoring*, not execution — so the row count of `catalogue.yaml` is a
MEASUREMENT published on the day the catalogue is written, `CATALOGUE_SIZE` is read from the file,
and no downstream denominator carries a literal. A layer that claims a round number it chose
before authoring anything is the coverage lie one document early.

**Every refusal below is the loader's, not a reviewer's.** Each corresponds to a step of the
authoring protocol, and each is a `RelationError` rather than a warning:

| protocol step | what the loader refuses |
|---|---|
| 1. name the artifact fact | an empty `evidence` |
| 2. `NECESSARY` or `EXPECTED` | anything else, and an `EXPECTED` row with no `guidance_note` |
| 3. write the precondition FIRST | an empty `precondition` |
| 4. declare the basis set | a `bases` that is not a singleton |
| 5. declare the degree map and the fault-class claim | an empty `claims_fault_classes` |
| 7. two humans sign | one signer without the literal weaker-review label |

**There is no second person on this project, so every row here is `SINGLE-SIGNER`.** That is not
a formality: `plan/05` ruling (c) says *what is not available is a second signature that nobody's
calendar contains*, so the label is carried on every row and
`test_reg__the_weaker_label_travels_with_every_relation_derived_number` asserts it renders beside
the numbers rather than in a residue section. It is the same discipline `D-P8-01` applies to the
blind-fill corpus and `geval.py` applies to arm 2.

**`subject_exists_at` exists for one row and is bounded like `ci/GATES.md`'s.** R-06 checks the
canary population, whose subject arrives at P10. A relation whose subject does not exist yet is
`NOT_RUN` with its phase named, and `test_reg__no_relation_is_permanently_pending` refuses a row
whose phase never comes — the escape hatch a `PENDING` field opens if nobody bounds it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Literal, get_args

from cdfc.verdict.reasons import ReasonCode
from cdfc.verdict.states import ItemState

Necessity = Literal["NECESSARY", "EXPECTED"]
Inputs = Literal["FILING_ONLY", "FILING_AND_BLANK", "TWO_CONSECUTIVE", "MANY_INSTANCES", "SELF_TEST"]

NECESSITIES: Final[frozenset[str]] = frozenset(get_args(Necessity))
INPUT_CLASSES: Final[frozenset[str]] = frozenset(get_args(Inputs))

WEAKER_REVIEW: Final[str] = "SINGLE-SIGNER — a weaker review"

# The input classes that cannot be run from one filing of one template. Each maps to the reason
# code that says WHY, because "absent from the report" and "present and NOT_RUN" are different
# claims and only the second one is a coverage declaration.
UNRUNNABLE: Final[Mapping[str, ReasonCode]] = {
    "TWO_CONSECUTIVE": ReasonCode.NR_INPUT_UNAVAILABLE_PRIOR_PERIOD,
    "MANY_INSTANCES": ReasonCode.NR_INPUT_UNAVAILABLE_COUNTERPARTY,
}

# Phases whose builds are complete. A `subject_exists_at` outside this set makes the relation
# un-runnable TODAY and names the phase that changes it.
COMPLETED_PHASES: Final[frozenset[str]] = frozenset(
    {"P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"}
)
KNOWN_PHASES: Final[frozenset[str]] = COMPLETED_PHASES | {"P10", "P11", "P12", "P13", "P14"}


class RelationError(ValueError):
    """A relation that does not load. Never a warning — an unloadable relation is not a relation."""


@dataclass(frozen=True, slots=True)
class RelationSpec:
    id: str
    title: str
    necessity: Necessity
    inputs: Inputs
    precondition: str                       # CEL. Non-degeneracy. Unmet ⇒ OUT_OF_SCOPE, never PASS
    expr: str                               # CEL
    witness: str                            # CEL
    bases: frozenset[str]
    evidence: str                           # the artifact fact or guidance note that licenses it
    reviewed_by: tuple[str, ...]
    reviewed_at: str
    claims_fault_classes: tuple[str, ...]
    reported_to_filer: bool = True
    subject_exists_at: str = "P9"
    guidance_note: str = ""                 # required when necessity == EXPECTED
    degree: Mapping[str, int] = field(default_factory=dict)
    builder: str = ""                       # a dotted callable that renders `expr` per template
    review_label: str = ""

    @property
    def expr_language(self) -> str:
        """`CEL` or `PYTHON`, **DERIVED and never declared.**

        A relation whose expression is `module:function` is Python; anything else is CEL. Deriving
        it stops a row claiming CEL while carrying a callable, which would fail at the subset
        check with an error about a parse rather than about a category.

        The distinction is load-bearing at P9-B4: only a CEL relation can become a P4 envelope,
        because the envelope's `expr` is checked against the admitted subset and its `schema_keys`
        are recovered from that expression's AST.
        """
        body = self.expr.strip()
        # **DERIVED FROM THE SHAPE OF A DOTTED CALLABLE, not from "has a colon and no space".**
        #
        # The old rule classified any space-free CEL containing `:` as PYTHON — a ternary
        # (`filing.a.v>0?1:0`) or a map literal (`{"k":filing.a.v}`) — so `to_envelope` would have
        # refused it with *"its expression is PYTHON, not CEL"*, a reason that is untrue, and the
        # refusal would have been published in the attrition table under it. It also ran the other
        # way: `cdfc.mod:fn # note` came out CEL and would reach the subset check. R-03's builder
        # emits ternaries today and was saved only by putting spaces around them.
        head, sep, tail = body.partition(":")
        if not sep or not tail:
            return "CEL"
        module, fn = head.strip(), tail.strip()
        looks_like_callable = (
            module.startswith("cdfc.")
            and all(part.isidentifier() for part in module.split("."))
            and fn.isidentifier()
        )
        return "PYTHON" if looks_like_callable else "CEL"

    @property
    def single_signer(self) -> bool:
        return len(self.reviewed_by) < 2

    @property
    def runnable_today(self) -> bool:
        return self.inputs not in UNRUNNABLE and self.subject_exists_at in COMPLETED_PHASES

    def unrunnable_reason(self) -> ReasonCode | None:
        """The reason code an un-runnable relation reports. **Not absence.**"""
        if self.inputs in UNRUNNABLE:
            return UNRUNNABLE[self.inputs]
        if self.subject_exists_at not in COMPLETED_PHASES:
            return ReasonCode.NR_DEACTIVATED
        return None

    def state_on_violation(self) -> ItemState:
        """`NECESSARY` ⇒ `FAIL`; `EXPECTED` ⇒ `INFORMATIONAL`. **No third path exists.**"""
        return ItemState.FAIL if self.necessity == "NECESSARY" else ItemState.INFORMATIONAL


def resolve_builder(dotted: str) -> Mapping[str, str]:
    """`module:function` → `{precondition, expr, witness}`.

    **Long CEL is GENERATED from the pinned blank, never typed into YAML.** R-02 addresses forty
    cells and R-03 eleven; hand-typing them is how a relation comes to name a cell nobody meant,
    and a review of 300 characters of dotted paths is not a review. The builder is deterministic
    in the template, so `catalogue.yaml` stays readable and the expression stays checkable.
    """
    import importlib

    mod_name, _, fn_name = dotted.partition(":")
    if not mod_name or not fn_name:
        raise RelationError(f"builder {dotted!r} is not `module:function`")
    if not mod_name.startswith("cdfc.probes.relations."):
        raise RelationError(
            f"builder {dotted!r} lives outside `cdfc.probes.relations`. A relation whose "
            "expression is built somewhere else is a relation nobody reviewing this package saw."
        )
    fn = getattr(importlib.import_module(mod_name), fn_name)
    out = fn()
    missing = [k for k in ("precondition", "expr", "witness") if not out.get(k)]
    if missing:
        raise RelationError(f"builder {dotted!r} returned no {missing}")
    return out


def _require(row: Mapping[str, Any], key: str, rid: str, why: str) -> Any:
    v = row.get(key)
    if v is None or (isinstance(v, (str, list, tuple)) and len(v) == 0):
        raise RelationError(f"{rid}: {key} is required — {why}")
    return v


def parse_row(row: Mapping[str, Any]) -> RelationSpec:
    """One catalogue row, or a refusal naming the protocol step it failed."""
    rid = str(row.get("id") or "<no id>")
    if row.get("builder"):
        row = {**row, **resolve_builder(str(row["builder"]))}

    necessity = _require(row, "necessity", rid, "step 2: NECESSARY violations FAIL, EXPECTED "
                         "violations are INFORMATIONAL, and there is no third path")
    if necessity not in NECESSITIES:
        raise RelationError(f"{rid}: necessity {necessity!r} is not one of {sorted(NECESSITIES)}")

    inputs = _require(row, "inputs", rid, "the input class decides whether it can run at all")
    if inputs not in INPUT_CLASSES:
        raise RelationError(f"{rid}: inputs {inputs!r} is not one of {sorted(INPUT_CLASSES)}")

    _require(row, "evidence", rid, "step 1: name the cell range, formula, guidance note or "
             "validation that licenses it. 'It seems like it should hold' is a refusal")
    _require(row, "precondition", rid, "step 3: write the non-degeneracy precondition FIRST. "
             "Written second, it is written to make the relation pass")
    _require(row, "expr", rid, "a relation with no expression settles nothing")
    _require(row, "claims_fault_classes", rid, "step 5: declare the fault classes this relation "
             "CLAIMS to cover, BEFORE any campaign. 'Whichever classes it turns out to kill' is a "
             "denominator chosen after the result, which is not a denominator")

    bases = frozenset(row.get("bases") or ())
    if len(bases) != 1:
        raise RelationError(
            f"{rid}: step 4 — `bases` must be a SINGLETON, got {sorted(bases)}. No relation may "
            "combine a non-look-through quantity with a look-through one: "
            "'3. Portfolio'!A130 puts Table 3.5 on one basis and Table 3.6 on the other, so a "
            "relation across them adds two different measurements of the same money."
        )

    reviewers = tuple(row.get("reviewed_by") or ())
    if not reviewers:
        raise RelationError(f"{rid}: step 7 — a relation with no reviewer has not been reviewed")
    label = str(row.get("review_label") or "")
    if len(reviewers) < 2 and label != WEAKER_REVIEW:
        raise RelationError(
            f"{rid}: step 7 — one signer, and the row does not carry {WEAKER_REVIEW!r}. "
            "A second signature nobody's calendar contains is not available; saying so is."
        )

    if necessity == "EXPECTED" and not row.get("guidance_note"):
        raise RelationError(
            f"{rid}: step 2 — an EXPECTED relation must name the note that makes the exception "
            "lawful. If you cannot name the note, it is not EXPECTED; it is unfinished."
        )

    phase = str(row.get("subject_exists_at") or "P9")
    if phase not in KNOWN_PHASES:
        raise RelationError(
            f"{rid}: subject_exists_at={phase!r} names no phase in this plan. A relation whose "
            "subject arrives at an unnamed phase is permanently pending."
        )

    reported = bool(row.get("reported_to_filer", inputs != "SELF_TEST"))
    if inputs == "SELF_TEST" and reported:
        raise RelationError(
            f"{rid}: a SELF_TEST relation is never reported to the filer. It measures US."
        )

    return RelationSpec(
        id=rid,
        title=str(_require(row, "title", rid, "a relation nobody can name is not reviewable")),
        necessity=necessity,
        inputs=inputs,
        precondition=str(row["precondition"]).strip(),
        expr=str(row["expr"]).strip(),
        witness=str(row.get("witness") or "").strip(),
        bases=bases,
        evidence=str(row["evidence"]).strip(),
        reviewed_by=reviewers,
        reviewed_at=str(_require(row, "reviewed_at", rid, "an undated review is not a review")),
        claims_fault_classes=tuple(row["claims_fault_classes"]),
        reported_to_filer=reported,
        subject_exists_at=phase,
        guidance_note=str(row.get("guidance_note") or "").strip(),
        degree=dict(row.get("degree") or {}),
        builder=str(row.get("builder") or ""),
        review_label=label,
    )


def catalogue_path() -> Path:
    return Path(__file__).with_name("catalogue.yaml")


def load(path: Path | None = None) -> tuple[RelationSpec, ...]:
    """The catalogue, IN FILE ORDER.

    File order and not sorted order: `test_det__relation_order_is_catalogue_order` pins it, and
    a relation set enumerated by `Path.glob` would be ordered by the filesystem, which differs
    between CI runner images and would break `verify` for a reason nobody would look for.
    """
    import yaml

    p = path or catalogue_path()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    rows = raw.get("relations") or []
    specs = tuple(parse_row(r) for r in rows)
    ids = [s.id for s in specs]
    if len(set(ids)) != len(ids):
        raise RelationError(f"duplicate relation ids in {p.name}: {sorted(ids)}")
    return specs


def catalogue_size(path: Path | None = None) -> int:
    """**A MEASUREMENT.** Every downstream denominator reads this, never a literal (F32)."""
    return len(load(path))


CATALOGUE_SIZE: Final[int] = catalogue_size()


def runnability(specs: Sequence[RelationSpec] | None = None) -> dict[str, Any]:
    """The split, with both integers computed. Neither is pinned anywhere."""
    rows = tuple(specs) if specs is not None else load()
    by_class: dict[str, int] = {}
    for s in rows:
        by_class[s.inputs] = by_class.get(s.inputs, 0) + 1
    unrunnable = [s for s in rows if not s.runnable_today]
    return {
        "total": len(rows),
        "by_input_class": dict(sorted(by_class.items())),
        "runnable": len(rows) - len(unrunnable),
        "unrunnable": len(unrunnable),
        "unrunnable_detail": [
            {"id": s.id, "inputs": s.inputs, "subject_exists_at": s.subject_exists_at,
             "reason": str(s.unrunnable_reason())}
            for s in unrunnable
        ],
        "single_signer": sum(1 for s in rows if s.single_signer),
        "reported_to_filer": sum(1 for s in rows if s.reported_to_filer),
    }
