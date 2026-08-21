"""A reference fill declaration that exercises EVERY askable reason, and both that are not.

## Why this exists

`ASKABLE` is an allowlist, and an allowlist has two failure modes. One is an undeclared entry
getting through; the other is *a table full of entries nobody reaches* — a row whose question no
filer will ever be shown because the fill lane cannot produce its reason. `CLAUDE.md §3` requires
each half to have its own injector, and the second half needs a population to be measured against.

This is that population. It is built from `src/` code end to end — a real `InstrumentText`, real
`Observation` spans located in it, a real `FieldSet`, and `fill.propose.propose` — so an injector
that changes the questioning layer changes what this produces.

**It is not a mock.** The only thing synthetic about it is the source document, which is four lines
of CSV chosen so that all eight reasons arise in one run. The pinned FME return produces only two
of them, which is exactly why a guard written over that return alone would leave six rows of the
table unmeasured and green.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evidence.fields import Field, FieldSet, LabelRule  # noqa: E402
from cdfc.evidence.observe import Observation  # noqa: E402
from cdfc.evidence.vocabulary import Asks, FieldType  # noqa: E402
from cdfc.fill.propose import FillDeclaration, propose  # noqa: E402
from cdfc.ingest.tabular import read_delimited  # noqa: E402
from cdfc.qualify.textsource import InstrumentText  # noqa: E402

SHEET = "Return"

# Two documents. The second disagrees with the first about the PAN, which is what makes
# SUPPORT_CONTRADICTED arise from a real pair of located spans rather than from a hand-built pair.
CUSTODIAN = (
    b"PAN of FME,Name of the FME,Legal structure,Date of incorporation\n"
    b"AAACI1234K,Meridian Capital IFSC Ltd,Partnership,the third of March\n"
)
TRIAL_BALANCE = (
    b"PAN of FME,Name of the FME\n"
    b"AAACX9999Z,Meridian Capital IFSC Ltd\n"
)

FIELDS = (
    Field(f"{SHEET}!A1", "Name of the FME", FieldType.TEXT, Asks.FACT),
    Field(f"{SHEET}!A2", "PAN of FME", FieldType.TEXT, Asks.FACT),
    Field(f"{SHEET}!A3", "Date of incorporation", FieldType.DATE, Asks.FACT),
    Field(f"{SHEET}!A4", "Legal structure", FieldType.ENUM, Asks.FACT,
          vocabulary=("Company", "Limited Liability Partnership")),
    Field(f"{SHEET}!A5", "Contact person", FieldType.TEXT, Asks.FACT),
    Field(f"{SHEET}!A6", "Number of schemes managed", FieldType.NUMBER, Asks.FACT),
    Field(f"{SHEET}!A9", "Assets under management", FieldType.MONEY, Asks.FACT),
    Field(f"{SHEET}!A7",
          "The FME is in compliance with the IFSCA (Fund Management) Regulations",
          FieldType.TEXT, Asks.ATTESTATION),
)
# `A8` is in the SURFACE and not in `fields`: an unlocked cell no label resolves for. That is the
# FIELD_NOT_LABELLED population, which is 3,615 of 3,735 on the real return and is NOT a question.
SURFACE = frozenset({f.ref for f in FIELDS} | {f"{SHEET}!A8"})


def sources() -> dict[str, InstrumentText]:
    return {
        "custodian_register.csv": read_delimited(CUSTODIAN, instrument_id="custodian_register.csv"),
        "trial_balance.csv": read_delimited(TRIAL_BALANCE, instrument_id="trial_balance.csv"),
    }


def _at(src: InstrumentText, value: str) -> Observation:
    """An observation at the FIRST undisputed occurrence of `value`. Raises if it is not there."""
    for lo, hi in src.find_all(value):
        if src.is_disputed((lo, hi)):
            continue
        unit = src.unit_at((lo, hi))
        return Observation(value=value, document=src.instrument_id, span=(lo, hi),
                           page=(unit.page if unit else None),
                           context=src.text[max(0, lo - 30):hi + 30])
    raise AssertionError(
        f"{value!r} is not in {src.instrument_id}. The reference declaration builds its "
        "observations by LOCATING them, so a value that is not in the document cannot be bound — "
        "which is the property the whole fill lane rests on."
    )


def fieldset() -> FieldSet:
    return FieldSet(
        template_sha256="0" * 64, surface_total=len(SURFACE), label_rule=LabelRule.ADJACENT_LEFT,
        fields=FIELDS, surface=SURFACE, refusal=None,
    )


def declaration() -> FillDeclaration:
    """A declaration carrying every one of the eight reasons that can arise, and the attestation."""
    src = sources()
    cust, tb = src["custodian_register.csv"], src["trial_balance.csv"]

    binding = {
        # A1: two documents, one value, agreeing -> a clean evidenced fill. The positive control:
        # a declaration in which nothing succeeds does not prove a question was skipped correctly.
        f"{SHEET}!A1": (_at(cust, "Meridian Capital IFSC Ltd"),
                        _at(tb, "Meridian Capital IFSC Ltd")),
        # A2: two documents DISAGREE -> SUPPORT_CONTRADICTED.
        f"{SHEET}!A2": (_at(cust, "AAACI1234K"), _at(tb, "AAACX9999Z")),
        # A3: a DATE field handed prose -> TYPE_NOT_ADMITTED.
        f"{SHEET}!A3": (_at(cust, "the third of March"),),
        # A4: an ENUM handed a term the form does not declare -> VOCABULARY_NOT_ADMITTED.
        f"{SHEET}!A4": (_at(cust, "Partnership"),),
        # A6: a span that does NOT re-read at the offset it cites -> REVERIFICATION_FAILED. The
        # span is deliberately shifted by one, which is what a stale locator produces.
        f"{SHEET}!A6": (Observation(value="4", document="custodian_register.csv",
                                    span=(0, 1), page=None, context=""),),
        # A9 is bound to NOTHING and NOTHING was offered for it -> NO_OBSERVATION. It is a
        # different fact from A5 below and takes a different answer, which is the distinction
        # `NOT_LOCATABLE_IN_SOURCE` was declared for and had never once been able to make.
        # A5 is bound to NOTHING and is in `offered_but_absent` -> NOT_LOCATABLE_IN_SOURCE.
        # A7 is an attestation and never reaches the conditions at all.
        # A8 has no label -> FIELD_NOT_LABELLED.
    }
    return propose(
        fieldset(), binding, src,
        binding_provenance="tests/negative/ask_reference.py, a hand-bound reference population",
        offered_but_absent={f"{SHEET}!A5": "Asha Rao"},
    )
