"""The pinned fault taxonomy, as the ENVELOPE sees it.

**The source moved at P6 and this module followed it.** At P4 the taxonomy was a hand-written
markdown table and this module parsed it; that was right while a class was only an id. Once an
operator became executable the table moved into `src/cdfc/qualify/fault_model.py`, and
`docs/FAULT-MODEL-v3.md` became generated from it. This module now reads the same one list rather
than a second copy of it — which is the property that mattered all along.

`Candidate.claims_fault_classes` validates against `known_ids()`, so a claim naming a class nobody
defined is refused at load. The count assertion is kept: a row lost to a bad edit would otherwise
shrink the denominator of every kill rate in the programme without anything going red.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from cdfc.qualify.fault_model import (
    CLASS_COUNT,
    FAULT_MODEL_VERSION,
    FaultClass as _QualifyFaultClass,
    fault_classes as _qualify_classes,
    model_digest,
)

MODEL_VERSION: Final[str] = FAULT_MODEL_VERSION
EXPECTED_CLASSES: Final[int] = CLASS_COUNT

__all__ = [
    "MODEL_VERSION",
    "EXPECTED_CLASSES",
    "FaultClass",
    "FaultModelError",
    "fault_classes",
    "known_ids",
    "model_digest",
    "resolve",
]


class FaultModelError(ValueError):
    """The pinned taxonomy does not say what it must say."""


@dataclass(frozen=True, slots=True)
class FaultClass:
    """The envelope's view: what a CLAIM can name. Operators are the campaign's business."""

    id: str
    name: str
    operator: str
    applies_to: tuple[str, ...]
    scope: str
    rationale: str


def _adapt(c: _QualifyFaultClass) -> FaultClass:
    return FaultClass(
        id=c.id,
        name=c.name.replace("_", " "),
        operator=" · ".join(o.name.replace("_", " ") for o in c.operators),
        applies_to=tuple(sorted(str(d) for d in c.applies_to)),
        scope=str(c.arity),
        rationale=c.rationale,
    )


def fault_classes() -> dict[str, FaultClass]:
    """`{id: FaultClass}` in table order."""
    classes = {c.id: _adapt(c) for c in _qualify_classes()}
    if len(classes) != EXPECTED_CLASSES:
        raise FaultModelError(
            f"the pinned taxonomy parses to {len(classes)} classes, not {EXPECTED_CLASSES}. "
            "A lost row silently shrinks the denominator of every kill rate in the programme."
        )
    if "F11" not in classes:
        raise FaultModelError(
            "F11 is the formula-override class and is named by id in P9's exit gate. "
            "It may not be renumbered."
        )
    return classes


def known_ids() -> frozenset[str]:
    return frozenset(fault_classes())


def resolve(claim: str) -> FaultClass:
    classes = fault_classes()
    if claim not in classes:
        raise FaultModelError(
            f"{claim!r} is not a class of the pinned fault model {MODEL_VERSION}. "
            f"Admissible: {', '.join(sorted(classes))}."
        )
    return classes[claim]
