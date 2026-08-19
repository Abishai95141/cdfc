"""LAYER 1b — the template becomes `Field` nodes whose TYPE the workbook itself declares.

This is the second of the three doors meaning arrives through, and the cheapest: `=SUM(D18:D20)`
means *the total of those*, a validation list means a closed vocabulary, a protection mask means
*a filer writes here*. None of it needs a model.

**THE LABELLING RULE IS PINNED HERE, AND IT HAD TO BE.** `M-CEIL` measured three defensible
readings of *"this field has a label"* over the SAME 3,747-cell surface and got 3,104 fields,
498 fields, and an unreproducible 724 -- a denominator that moves by a factor of six with an
unwritten convention. The 3,104 reading is the one to refuse: those fields share 154 distinct
labels between them, because it walks left to the row header and hands the same label to every
column in the row. It labels ROWS. So `ADJACENT_LEFT` is the rule, it is named, and a caller who
wants another one has to add it here where the count that depends on it is visible.
"""

from __future__ import annotations

import re

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final
from pathlib import Path

from cdfc.evidence.vocabulary import Asks, FieldType


class LabelRule(StrEnum):
    """How a field acquires its label. The denominator is a function of this choice."""

    ADJACENT_LEFT = "adjacent_left"      # the cell immediately to the left holds text
    NEAREST_LEFT = "nearest_left"        # the nearest text anywhere to the left -- LABELS ROWS


PINNED_RULE: LabelRule = LabelRule.ADJACENT_LEFT

# --- A PLACEHOLDER IS NOT A LABEL, AND ON THIS RETURN MOST OF THEM WERE -----------------------
#
# `N2` measured the labelled population under the pinned rule at 498 and then read the labels:
# **351 of them are the literal string `NA`**, which this form uses as filler in the column to the
# left of a field. Verified against the workbook's own cells, not inferred. Counting those as
# labelled fields inflated the population fourfold and made the FACT/ATTESTATION split read
# 481/17 when over genuinely-labelled fields it is 130/17 — attestations are about one field in
# nine, not one in twenty-nine.
#
# The list is CLOSED and short because it was derived by enumerating every label of four
# characters or fewer on the pinned return rather than by guessing what a placeholder looks like.
# A field whose neighbour is a placeholder is UNLABELLED, which is the honest state: we could not
# read its meaning, and `G-FIELD` reports that as `field_not_labelled` rather than as absent.
PLACEHOLDER: frozenset[str] = frozenset({
    "na", "n/a", "n.a.", "nil", "none", "-", "--", "---", ".", "..", "x",
})


def _is_placeholder(text: str) -> bool:
    return text.strip().strip(":").lower() in PLACEHOLDER


# --- NOR IS INSTRUCTION TEXT, OR A TABLE CAPTION ----------------------------------------------
#
# Reading all 125 distinct labels (N2) turned up two more classes that sit to the left of a field
# and are not that field's name:
#
#   numbered instructions   "1. Additional rows may be inserted to add more countries."
#   table captions          "Table 4.1: Details of investors in Investment Fund"
#   a bare lead-in          "Note:"
#
# Nine instructions, two captions and one lead-in on this return. They are excluded because a
# field whose "label" is a footnote has not been labelled — and calling it labelled is how a
# denominator comes to contain things nobody could name.
_NON_LABEL: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:\d+\.\s|Table\s+\d+\.\d+\s*:|Note\s*:\s*$)", re.I)


def _is_non_label(text: str) -> bool:
    return bool(_NON_LABEL.match(text.strip()))


@dataclass(frozen=True, slots=True)
class Field:
    ref: str                      # "Sheet!A1"
    label: str
    type: FieldType
    asks: Asks
    vocabulary: tuple[str, ...] = ()   # non-empty only for ENUM


@dataclass(frozen=True, slots=True)
class FieldSet:
    template_sha256: str
    surface_total: int            # the run's OWN denominator, unmodified
    label_rule: LabelRule
    fields: tuple[Field, ...]
    surface: frozenset[str] = frozenset()   # EVERY unlocked ref, labelled or not

    def by_ref(self) -> Mapping[str, Field]:
        return {f.ref: f for f in self.fields}

    def get(self, ref: str) -> Field | None:
        return self.by_ref().get(ref)

    def __len__(self) -> int:
        return len(self.fields)

    @property
    def attestations(self) -> tuple[Field, ...]:
        return tuple(f for f in self.fields if f.asks is Asks.ATTESTATION)


# --- TYPE, read from the workbook's own number format ---------------------------------------
_MONEY = ("$", "usd", "inr", "₹", "€", "£", '"')
_DATE = ("yy", "dd", "mmm")


def _type_of(number_format: str, builtin: str, has_list: bool) -> FieldType:
    """The DECLARED type. `builtin` is the numFmtId's own meaning; `number_format` is a custom
    code. Neither is a guess -- a cell the workbook formats as nothing stays UNDECLARED."""
    if has_list:
        return FieldType.ENUM
    if builtin:
        return FieldType(builtin)
    nf = (number_format or "").strip().lower()
    if not nf or nf == "general":
        return FieldType.UNDECLARED
    if "%" in nf:
        return FieldType.PERCENT
    if any(t in nf for t in _DATE):
        return FieldType.DATE
    if any(t in nf for t in _MONEY):
        return FieldType.MONEY
    if "0" in nf or "#" in nf:
        return FieldType.NUMBER
    return FieldType.TEXT


# --- ASKS: can a grounded observation settle it? ---------------------------------------------
#
# The boundary is NOT a word list, and N2 is where that was settled by reading all 125 distinct
# labels on the pinned return. A first attempt keyed on "whether" and produced 17 attestations,
# among them *"Whether the sanction screening is manual or automated?"* and *"Whether FME has paid
# the applicable recurring fees"* — both of which a source document can answer. Calling those
# attestations would refuse to fill fields the system can evidence.
#
# THE PRINCIPLE: an ATTESTATION is a claim NO OBSERVATION CAN SETTLE. *"The FME is in compliance
# with the IFSCA (Fund Management) Regulations"* is a legal representation about a whole body of
# obligations; no span in any document makes it true, and a system that ticked it would be signing
# on the filer's behalf. *"Was there a true match against the UNSC list?"* is a question about an
# event, and an event leaves evidence.
#
# So the test is the CERTIFICATION SHAPE: a declarative in which the filer asserts compliance,
# adequacy or conformity, rather than an interrogative asking what happened. `_FACTUAL` runs
# first because a label asking for a number, a name or a date is a report whatever else it says.
_FACTUAL = ("number", "amount", "value", "total", "name", "date", "aum", "nav",
            "count", "isin", "lei", "address", "email", "pan", "url", "contact")
# Declarative certifications only. Every one of these asserts a state the filer VOUCHES for.
_CERTIFY = ("is in compliance", "are in compliance", "has been complied", "has complied",
            "has the necessary", "has put in place", "is in place", "in compliance with",
            "has been done", "has been maintained", "has been adhered")


def _asks(label: str) -> Asks:
    low = label.lower()
    if any(t in low for t in _FACTUAL):
        return Asks.FACT
    # An interrogative asks what happened; a declarative asserts a state. Only the second is a
    # thing a human must sign, and the `?` is the cheapest reliable signal of the first.
    if low.rstrip().endswith("?"):
        return Asks.FACT
    return Asks.ATTESTATION if any(t in low for t in _CERTIFY) else Asks.FACT


def from_template(blob: Path, *, rule: LabelRule = PINNED_RULE) -> FieldSet:
    """Field nodes over THE RUN'S OWN field surface -- never a private re-derivation of it.

    `surface_for` is the same denominator every run is scored over. Deriving the unlocked set a
    second time here would be a second list, and the one that drifts is the one nobody reads.
    """
    import hashlib

    from cdfc.evidence.workbook import read_cells
    from cdfc.measure.p5_run import surface_for

    total, refs = surface_for(blob)[0], surface_for(blob)[1]
    want: dict[str, set[str]] = {}
    for r in refs:
        sheet, cell = r.rsplit("!", 1)
        want.setdefault(sheet, set()).add(cell)

    cells = read_cells(blob)
    by_ref = {(c.sheet, c.ref): c for c in cells}
    texts: dict[tuple[str, int], dict[int, str]] = {}
    for c in cells:
        if not c.text or not c.is_text:
            continue
        col, row = _split(c.ref)
        texts.setdefault((c.sheet, row), {})[col] = c.text

    listed = _validation_lists(blob, by_ref)
    out: list[Field] = []
    for sheet, wanted in want.items():
        for ref in wanted:
            col, row = _split(ref)
            label = _label(texts.get((sheet, row), {}), col, rule)
            if label is None or _is_placeholder(label) or _is_non_label(label):
                continue
            key = f"{sheet}!{ref}"
            vocab = listed.get(key, ())
            c = by_ref.get((sheet, ref))
            out.append(Field(
                ref=key,
                label=label,
                type=_type_of(c.number_format if c else "", c.builtin if c else "", bool(vocab)),
                asks=_asks(label),
                vocabulary=vocab,
            ))
    return FieldSet(
        template_sha256=hashlib.sha256(blob.read_bytes()).hexdigest(),
        surface_total=total,
        label_rule=rule,
        fields=tuple(sorted(out, key=lambda f: f.ref)),
        surface=frozenset(refs),
    )


def _split(ref: str) -> tuple[int, int]:
    """`"AB12"` -> `(28, 12)`. Column letters to a 1-based index, and the row."""
    letters = "".join(ch for ch in ref if ch.isalpha())
    digits = "".join(ch for ch in ref if ch.isdigit())
    col = 0
    for ch in letters.upper():
        col = col * 26 + (ord(ch) - 64)
    return (col, int(digits or 0))


def _label(texts: Mapping[int, str], col: int, rule: LabelRule) -> str | None:
    if rule is LabelRule.ADJACENT_LEFT:
        return texts.get(col - 1)
    left = [c for c in texts if c < col]
    return texts[max(left)] if left else None


def _validation_lists(blob: Path, by_ref: Mapping[tuple[str, str], object]
                      ) -> dict[str, tuple[str, ...]]:
    """`{"Sheet!A1" -> permitted values}` for every list validation, x14 included.

    The vocabularies sit behind RANGE and DEFINED_NAME references rather than inline strings, so
    the range is resolved and its cells are read. A reference that will not resolve yields NO
    entry, leaving the field UNDECLARED -- a field whose vocabulary we could not read must not
    present as one with an EMPTY vocabulary, because `G-VOCAB` would then admit every term
    against it.
    """
    from cdfc.ingest.reader_lxml import read as read_raw

    raw = read_raw(blob)
    out: dict[str, tuple[str, ...]] = {}
    for v in raw.validations:
        if v.type != "list":
            continue
        vals = _values_at(by_ref, v.resolved_range or v.formula1 or "")
        if not vals:
            continue
        for cell in _expand(v.sqref):
            out[f"{v.sheet}!{cell}"] = vals
    return out


def _values_at(by_ref: Mapping[tuple[str, str], object], ref: str) -> tuple[str, ...]:
    if "!" not in ref:
        return ()
    sheet, rng = ref.rsplit("!", 1)
    sheet = sheet.strip("'").replace("$", "")
    vals = [t for cell in _expand(rng.replace("$", ""))
            if (c := by_ref.get((sheet, cell))) is not None
            and getattr(c, "is_text", False) and (t := getattr(c, "text", None))]
    return tuple(dict.fromkeys(vals))


def _expand(sqref: str) -> list[str]:
    """`"D2 D10:D12"` -> the individual A1 references it covers."""
    out: list[str] = []
    for part in (sqref or "").split():
        part = part.replace("$", "")
        lo, _, hi = part.partition(":")
        if not lo:
            continue
        lo_c, lo_r = _split(lo)
        hi_c, hi_r = _split(hi) if hi else (lo_c, lo_r)
        if 0 in (lo_c, lo_r, hi_c, hi_r):
            continue
        for r in range(min(lo_r, hi_r), max(lo_r, hi_r) + 1):
            for c in range(min(lo_c, hi_c), max(lo_c, hi_c) + 1):
                out.append(f"{_letters(c)}{r}")
    return out


def _letters(col: int) -> str:
    s = ""
    while col > 0:
        col, rem = divmod(col - 1, 26)
        s = chr(65 + rem) + s
    return s
