"""P14-B3 — the response models, and the two prohibitions baked into their SCHEMA.

The API may not express a pass. Two mechanisms, and neither is a runtime check that a caller could
be handed around:

* **`BANNED_PROPERTY_NAMES`** — no property at any depth of the GENERATED document may be called
  `result`, `status`, `pass`, `ok`, `clean`… The gate walks the emitted schema, not a hand-written
  list, so a model added without touching the gate is still scanned.
* **`fraction` never travels alone** — `SettledFractionOut` cannot be CONSTRUCTED with a fraction
  and without all six counts. It raises in `__post_init__`. A settled fraction whose denominator a
  client cannot see is the single most misreadable number this system emits.

## Why dataclasses and a hand-written schema emitter

pydantic's `extra="forbid"` and `@model_validator` are promises made in a keyword argument. This
project's own objection to Jinja's `autoescape=True` applies unchanged: the guarantee has to be a
property of what is emitted, not of what somebody remembered to pass. `json_schema()` below is
walked by `tests/contract/test_contract__api_cannot_express_a_pass.py`, which is the same recursive
walker NC-A01 uses — so the check is over the DOCUMENT a client actually receives.

`additionalProperties: False` is emitted on every object for the same reason `extra="forbid"`
existed: a consumer must not be able to write a `status` in at runtime either.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, Final, get_args, get_origin, get_type_hints

# A property whose NAME means "it passed". The list is closed and adding to it is a visible diff.
BANNED_PROPERTY_NAMES: Final[frozenset[str]] = frozenset({
    "result", "status", "pass", "passed", "passing",
    "compliant", "conformant", "ok", "success", "clean",
})

# EXACTLY FIVE. A blanket "no booleans" rule would be wrong -- `summaryIsNotSubstitute` is a
# required boolean and it carries a warning, not a verdict. An unbounded allowlist would be no
# rule. So: five, and a sixth requires a DoD line.
PERMITTED_BOOLEANS: Final[frozenset[str]] = frozenset({
    "summaryIsNotSubstitute", "computedTwiceAgreed", "thirdParty",
    "clean_corpus_independent_of_predicate", "reproduced",
})


class FractionTravelsAlone(ValueError):
    """A settled fraction was constructed without the six counts that give it a denominator."""


@dataclass(frozen=True, slots=True)
class DenominatorOut:
    generatingRule: str
    fieldSurface: int
    validated: bool = False  # NOT in PERMITTED_BOOLEANS on purpose -- see below.

    def __post_init__(self) -> None:
        # `validated` is internal and must never reach the wire; `json_schema` omits it. It exists
        # so the renderer can distinguish PROVISIONAL-UNVALIDATED from validated without inventing
        # a wire field whose name a reader would take as a verdict.
        pass


@dataclass(frozen=True, slots=True)
class SettledFractionOut:
    """The six counts, then the fraction. **Never the fraction on its own.**"""

    denominator: DenominatorOut
    outOfScope: int
    informational: int
    inScope: int
    settled: int
    unsettled: int
    notChecked: int
    denominatorWarning: str
    admissionState: str
    fraction: float | None = None

    def __post_init__(self) -> None:
        if self.fraction is None:
            return
        missing = [
            n for n in ("outOfScope", "informational", "inScope", "settled", "unsettled",
                        "notChecked")
            if getattr(self, n) is None
        ]
        if missing:
            raise FractionTravelsAlone(
                f"fraction={self.fraction} was constructed without {missing}. A settled fraction "
                "whose denominator a client cannot reconstruct is the most misreadable number this "
                "system emits, and the schema is where that is prevented rather than the renderer."
            )
        if not self.denominatorWarning.strip():
            raise FractionTravelsAlone(
                "fraction is present and denominatorWarning is empty. The denominator is the "
                "template's unlocked-cell mask and it has never been checked against a person "
                "filling the form in; a fraction that does not say so is a fraction read as truth."
            )
        if not self.admissionState.strip():
            raise FractionTravelsAlone(
                "fraction is present and admissionState is empty. NC-A05: no settled count travels "
                "without the admission state, on the wire as on the page."
            )


@dataclass(frozen=True, slots=True)
class TemplateOut:
    templateSha256: str
    name: str
    # `null`, never 0. NC-D03b's API twin: a template with no derivable protection mask has NO
    # ceiling, which is a different fact from a ceiling of zero and must not be readable as one.
    settledFractionCeiling: float | None


@dataclass(frozen=True, slots=True)
class UncheckedGroupOut:
    reasonCode: str
    count: int
    remedy: str


@dataclass(frozen=True, slots=True)
class RunOut:
    runId: str
    filingSha256: str
    templateSha256: str
    runState: str
    settledFraction: SettledFractionOut
    unchecked: tuple[UncheckedGroupOut, ...]
    summaryIsNotSubstitute: bool
    reportUrl: str
    attestationUrl: str


@dataclass(frozen=True, slots=True)
class RejectionOut:
    candidateId: str
    gate: str
    measured: str
    cellsItWouldHaveCovered: int


@dataclass(frozen=True, slots=True)
class ErrorOut:
    error: str
    detail: str
    structuralFingerprint: str | None = None


# Every model the document exposes. The gate walks THIS, so a model that exists and is not
# reachable from here is not on the wire either.
RESPONSE_MODELS: Final[tuple[type, ...]] = (
    DenominatorOut, SettledFractionOut, TemplateOut, UncheckedGroupOut, RunOut, RejectionOut,
    ErrorOut,
)

# Fields that exist on a dataclass for internal use and are NOT emitted. Kept explicit so the
# omission is a decision somebody wrote down rather than a field the emitter happened to skip.
NOT_ON_THE_WIRE: Final[frozenset[tuple[str, str]]] = frozenset({
    ("DenominatorOut", "validated"),
})

_PRIMITIVES: Final[dict[Any, str]] = {str: "string", int: "integer", float: "number",
                                      bool: "boolean"}


def _type_schema(tp: Any) -> dict[str, Any]:
    origin = get_origin(tp)
    if origin is tuple:
        (inner, _ellipsis) = get_args(tp) if len(get_args(tp)) == 2 else (get_args(tp)[0], None)
        return {"type": "array", "items": _type_schema(inner)}
    if origin is not None and type(None) in get_args(tp):  # X | None
        inner = next(a for a in get_args(tp) if a is not type(None))
        return {"anyOf": [_type_schema(inner), {"type": "null"}]}
    if dataclasses.is_dataclass(tp):
        return {"$ref": f"#/$defs/{tp.__name__}"}
    return {"type": _PRIMITIVES.get(tp, "string")}


def model_schema(model: type) -> dict[str, Any]:
    hints = get_type_hints(model)
    props: dict[str, Any] = {}
    required: list[str] = []
    for f in dataclasses.fields(model):
        if (model.__name__, f.name) in NOT_ON_THE_WIRE:
            continue
        props[f.name] = _type_schema(hints[f.name])
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
            required.append(f.name)
    return {
        "type": "object",
        "properties": props,
        "required": required,
        # A consumer must not be able to write a `status` in at runtime either.
        "additionalProperties": False,
    }


def json_schema() -> dict[str, Any]:
    """`$defs` for every response model. **The document the gate walks.**"""
    return {"$defs": {m.__name__: model_schema(m) for m in RESPONSE_MODELS}}
