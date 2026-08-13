"""P6-B1 — the fault model, versioned `v3`. **The code is the source; the document is generated.**

At P4 the arrangement was inverted: `docs/FAULT-MODEL-v3.md` was hand-written and a parser read the
ids out of it. That was right while the taxonomy was only a list of ids. It stops being right here,
because **an operator is executable** — `sites()` and `apply()` cannot live in a markdown table, and
a table beside the code is a second list. So the table moves into this module and
`tools/gen_fault_model_doc.py` renders the document, which
`test_contract__fault_model_doc_is_generated` asserts byte-identical.

`src/cdfc/predicates/fault_model.py` (P4's reader) now reads THIS module rather than the markdown,
so `claims_fault_classes` still validates against one taxonomy and there is still only one list.

**`model_digest` covers the OPERATOR TABLE, not the class names.** A version pinned in name only —
a digest that ignores what the operators do — lets a silently edited operator keep its `v3` label,
and every kill rate ever quoted is then qualified against a model that no longer exists. NC-Q33.

**The one hard constraint on the numbering: `F11` is the formula-override class.** P9's exit gate and
experiment E3 name a seeded `F11` pair by id. The other ids are illustrative and may shift; `F11`
may not.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, Final, Literal

from cdfc.canon import canonical_json, sha256_hex

FAULT_MODEL_VERSION: Final[str] = "v3"
HARNESS_VERSION: Final[str] = "p6-b1"


class Dtype(StrEnum):
    MILLI_USD_MILLION = "MILLI_USD_MILLION"
    COUNT = "COUNT"
    DATE = "DATE"
    TEXT = "TEXT"
    ENUM = "ENUM"


class Arity(StrEnum):
    CELL = "cell"    # one cell edited
    PAIR = "pair"    # two cells edited so the artifact stays self-consistent
    RANGE = "range"  # a contiguous block


MONEY = Dtype.MILLI_USD_MILLION
ALL_DTYPES: Final[frozenset[Dtype]] = frozenset(Dtype)


@dataclass(frozen=True, slots=True)
class Site:
    """One place a fault can be seeded. `dtype` comes from the PINNED BLANK, not from the filing."""

    sheet: str
    ref: str
    dtype: Dtype
    is_formula: bool = False
    vocabulary: tuple[str, ...] = ()
    # The value of the cell ONE ROW UP, when the campaign knows it. F08 duplicates it, and an
    # operator that had to go and look would need the workbook — which would make the fault model
    # depend on the artifact it is meant to perturb.
    value_above: Any = None

    @property
    def cell(self) -> str:
        return f"{self.sheet}!{self.ref}"


@dataclass(frozen=True, slots=True)
class FaultOperator:
    """One executable perturbation.

    `mutate(value, site, rng) -> new value | REMOVE`. Returning `REMOVE` empties the cell, which is
    a DIFFERENT fault from writing `0` — F05 carries both, deliberately, because `sum([]) == 0`.
    `None` means the operator does not apply at this site and no mutant is generated.
    """

    id: str
    name: str
    fn: Callable[[Any, Site, Any], Any]
    note: str = ""
    # A PAIR operator edits a second cell so the artifact stays SELF-CONSISTENT. That is what makes
    # the pair form the coordinated-misstatement seed: the inconsistency a single-cell edit leaves
    # behind is exactly what every relation the template encodes would have caught, and the pair
    # deletes it. `partner(site, ctx) -> (partner_site, new_value) | None`.
    partner: Callable[[Site, Any], tuple[Site, Any] | None] | None = None

    @property
    def is_pair(self) -> bool:
        return self.partner is not None

    def mutate(self, value: Any, site: Site, rng: Any) -> Any:
        return self.fn(value, site, rng)


REMOVE: Final[str] = "\x00REMOVE\x00"  # the sentinel for "empty this cell", never a value


@dataclass(frozen=True, slots=True)
class FaultClass:
    id: str
    name: str
    applies_to: frozenset[Dtype]
    arity: Arity
    source: Literal["abraham_erwig_2009", "cdfc"]
    citation: str
    rationale: str
    operators: tuple[FaultOperator, ...]

    def as_canonical_obj(self) -> dict[str, Any]:
        """What `model_digest` covers. **The operator ids and names are inside it**, so an edited
        operator moves the digest even when the class table is untouched."""
        return {
            "id": self.id,
            "name": self.name,
            "applies_to": sorted(str(d) for d in self.applies_to),
            "arity": str(self.arity),
            "source": self.source,
            "citation": self.citation,
            "rationale": self.rationale,
            "operators": [
                {"id": o.id, "name": o.name, "note": o.note, "is_pair": o.is_pair,
                 "body": _body_digest(o)}
                for o in self.operators
            ],
        }


def _body_digest(op: FaultOperator) -> str:
    """A digest of the operator's own SOURCE.

    Without it, `model_digest` covers the operator's NAME and not what it does — and NC-Q33's break
    is exactly a silently edited operator keeping its `v3` label. Renaming a variable moves the
    digest too, which is the conservative direction: a false alarm costs a re-pin, a missed change
    costs every kill rate ever quoted.
    """
    import inspect

    try:
        src = inspect.getsource(op.fn)
    except (OSError, TypeError):  # pragma: no cover - only for dynamically built operators
        src = repr(op.fn)
    return sha256_hex(src.encode("utf-8"))[:16]


# ---------------------------------------------------------------------------------------------
# The operators. Every one is a pure function of (value, site, rng).
# ---------------------------------------------------------------------------------------------


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        d = Decimal(str(value))
    except Exception:  # noqa: BLE001 - a non-numeric cell is simply not a site for this operator
        return None
    return int(d) if d == d.to_integral_value() else None


def _fits(n: int) -> bool:
    return -(2**63) <= n < 2**63


def _num(fn: Callable[[int], int]) -> Callable[[Any, Site, Any], Any]:
    def op(value: Any, _site: Site, _rng: Any) -> Any:
        n = _as_int(value)
        if n is None:
            return None
        out = fn(n)
        return out if _fits(out) and out != n else None

    return op


def _transpose(value: Any, _site: Site, _rng: Any) -> Any:
    n = _as_int(value)
    if n is None:
        return None
    s = str(abs(n))
    for i in range(len(s) - 1):
        if s[i] != s[i + 1]:
            swapped = s[:i] + s[i + 1] + s[i] + s[i + 2:]
            out = int(swapped) * (-1 if n < 0 else 1)
            return out if _fits(out) and out != n else None
    return None  # a run of identical digits has no transposition


def _blank(_value: Any, _site: Site, _rng: Any) -> Any:
    return REMOVE


def _zero(value: Any, _site: Site, _rng: Any) -> Any:
    return None if _as_int(value) == 0 else 0


def _round_to_million(value: Any, _site: Site, _rng: Any) -> Any:
    """F06 in this system's units. Values are an int64 count of 10^-3 USD Million, so "drop the
    2-dp quantum" is rounding to a whole USD Million — 1,000 units. This is the operator that
    generates `τ(n) = 5n` straddles, and it is the only source of v0's 22 "equivalents"."""
    n = _as_int(value)
    if n is None:
        return None
    out = round(n / 1000) * 1000
    return out if out != n and _fits(out) else None


def _date_shift(days: int) -> Callable[[Any, Site, Any], Any]:
    def op(value: Any, _site: Site, _rng: Any) -> Any:
        n = _as_int(value)
        return n + days if n is not None else None

    return op


def _date_ddmm(value: Any, _site: Site, _rng: Any) -> Any:
    """DD<->MM on an Excel serial. Computed through the serial rather than through a date library:
    the fact model has no date type, and a library here would introduce one nobody declared."""
    import datetime as _dt

    n = _as_int(value)
    if n is None or n < 61:
        return None
    day = _dt.date(1899, 12, 30) + _dt.timedelta(days=n)
    if day.day > 12 or day.day == day.month:
        return None  # not swappable, or the swap is the identity
    try:
        swapped = day.replace(month=day.day, day=day.month)
    except ValueError:
        return None
    return (swapped - _dt.date(1899, 12, 30)).days


def _enum_other(value: Any, site: Site, rng: Any) -> Any:
    """F10 — one LEGAL vocabulary term for another. A membership predicate cannot see this, by
    construction. It is a designed miss and it belongs in the residue."""
    others = [m for m in site.vocabulary if m != str(value)]
    return rng.choice(sorted(others)) if others else None


def _vocab_outside(value: Any, site: Site, _rng: Any) -> Any:
    text = str(value)
    return None if not site.vocabulary else text + " (other)"


def _homoglyph(value: Any, _site: Site, _rng: Any) -> Any:
    """MEASURED: a live regulated entity's registration number carries `U+2011 NON-BREAKING
    HYPHEN` — visually identical to a hyphen, byte-wise different, invisible in any screenshot."""
    text = str(value)
    for plain, look_alike in (("-", "‑"), ("A", "А"), ("o", "ο")):
        if plain in text:
            return text.replace(plain, look_alike, 1)
    return None


def _whitespace(value: Any, _site: Site, _rng: Any) -> Any:
    text = str(value)
    return text + " " if text and text == text.strip() else None


def _vocab_gap(value: Any, site: Site, _rng: Any) -> Any:
    """F14 — a value LEGAL under the template's own defective logic but outside the regulation.

    MEASURED on this corpus: the regulator's template computes a scheme total with three COUNTIFs
    that between them miss two of its nine legal Type-of-Scheme values. A filing using one of those
    two is admitted by every relation the template encodes — which is exactly what makes it P10's
    residue feedstock and not something any predicate here can catch.
    """
    members = sorted(site.vocabulary)
    if len(members) < 2:
        return None
    candidate = members[-1]
    return None if str(value) == candidate else candidate


def _formula_override(value: Any, site: Site, _rng: Any) -> Any:
    """F11 — a cell the pinned blank declares a formula for carries a LITERAL.

    Only at a formula site, and the literal is deliberately *different* from the computed value:
    an override that happens to equal this quarter's computed value is invisible to everything,
    which is a real filing hazard and a useless mutant.
    """
    if not site.is_formula:
        return None
    n = _as_int(value)
    return (n + 1) if n is not None and _fits(n + 1) else 1


def _duplicate_above(value: Any, site: Site, _rng: Any) -> Any:
    """F08 — the cell takes the value of the cell ONE ROW UP.

    A whole-row duplication is a RANGE edit, and the campaign seeds it cell-wise: every cell of the
    row takes the row above's value. Seeded at one cell it is the same fault observed at one
    coordinate, which is what a tally identity sees. The first version of this operator returned
    `None` unconditionally — a stub that produced **G = 0 for the class**, and a class that cannot
    seed contributes no evidence while still occupying a row in the published vector.
    """
    import re as _re

    m = _re.match(r"^([A-Z]+)(\d+)$", site.ref)
    if m is None or int(m.group(2)) <= 1:
        return None
    above = getattr(site, "value_above", None)
    if above is None or str(above) == str(value):
        return None
    return above


def _pair_partner_source(site: Site, ctx: Any) -> tuple[Site, Any] | None:
    """The PAIR form's second edit: change an INPUT of the overridden cell to match the literal.

    A single-cell F11 leaves the filing internally inconsistent, and the template's own relations
    would catch that. The pair edits an input as well, so every relation the template encodes is
    satisfied — **the inconsistency was deleted with the formula.** `TEMPLATE_DIFF` is the only
    thing in the design that can still see it, which is why P9's exit gate names a seeded F11 pair.
    """
    inputs = ctx.inputs_of(site) if hasattr(ctx, "inputs_of") else ()
    for partner in inputs:
        if partner.dtype in (MONEY, Dtype.COUNT) and not partner.is_formula:
            return partner, 1
    return None


def _pair_partner_carry(site: Site, ctx: Any) -> tuple[Site, Any] | None:
    """F13's pair form: move BOTH ends of a cross-sheet carry by the same amount.

    Both ends agree, so every cross-sheet equality still holds — and the number is wrong on both
    sheets. This is the seed a coordinated misstatement produces, and no equality can see it.
    """
    # The context returns the (site, value) pair already. Wrapping it again produced
    # ((Site, 3), 3), which surfaced 750 mutants into a 25-minute campaign as an AttributeError.
    return ctx.carry_counterpart(site) if hasattr(ctx, 'carry_counterpart') else None


def _carry_desync(value: Any, site: Site, _rng: Any) -> Any:
    """F13 — a cross-sheet carry target moved while its source is untouched."""
    n = _as_int(value)
    return n + 3 if n is not None and _fits(n + 3) else None


# ---------------------------------------------------------------------------------------------
# The fourteen classes.
# ---------------------------------------------------------------------------------------------

AE2009: Final[str] = (
    "R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', "
    "IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100"
)

FAULT_CLASSES: Final[tuple[FaultClass, ...]] = (
    FaultClass(
        "F01", "sign_flip", frozenset({MONEY, Dtype.COUNT}), Arity.CELL, "abraham_erwig_2009",
        AE2009,
        "The operator that kills a `>= 0` bound and does NOT kill a `>= -1e17` bound — which is "
        "how ALR's five vacuous bounds become visible as a per-class zero rather than as an opinion.",
        (FaultOperator("F01.a", "negate", _num(lambda n: -n)),),
    ),
    FaultClass(
        "F02", "scale_error", frozenset({MONEY}), Arity.CELL, "abraham_erwig_2009", AE2009,
        "The sheet's unit is USD Million; a filer entering USD is the modal unit slip.",
        (
            FaultOperator("F02.a", "times_ten", _num(lambda n: n * 10)),
            FaultOperator("F02.b", "divide_ten", _num(lambda n: n // 10)),
            FaultOperator("F02.c", "times_thousand", _num(lambda n: n * 1000)),
        ),
    ),
    FaultClass(
        "F03", "off_by_one", frozenset({MONEY, Dtype.COUNT}), Arity.CELL, "abraham_erwig_2009",
        AE2009,
        "Boundary. Counts get ZERO tolerance — a person is not a rounded quantity.",
        (
            FaultOperator("F03.a", "plus_one", _num(lambda n: n + 1)),
            FaultOperator("F03.b", "minus_one", _num(lambda n: n - 1)),
        ),
    ),
    FaultClass(
        "F04", "digit_transposition", frozenset({MONEY}), Arity.CELL, "abraham_erwig_2009", AE2009,
        "Keying error; survives a magnitude check, which is why a bound predicate cannot see it.",
        (FaultOperator("F04.a", "swap_adjacent_digits", _transpose),),
    ),
    FaultClass(
        "F05", "zero_out_or_blank", ALL_DTYPES, Arity.CELL, "abraham_erwig_2009", AE2009,
        "TWO operators, not one. `0` and blank are different facts, and `sum([]) == 0` is NC-Q01. "
        "A class that carried only one of them would make the two indistinguishable in the vector.",
        (
            FaultOperator("F05.a", "zero", _zero),
            FaultOperator("F05.b", "blank", _blank, note="empties the cell; never writes 0"),
        ),
    ),
    FaultClass(
        "F06", "round_to_integer", frozenset({MONEY}), Arity.CELL, "abraham_erwig_2009", AE2009,
        "The `tau(n) = 5n` straddle generator, and the source of "
        "`indeterminate.tolerance_straddle`. It produced all 22 of v0's 'equivalents'. "
        "COUNT is deliberately absent: rounding a count is not a rounding error, it is a "
        "different count.",
        (FaultOperator("F06.a", "round_to_usd_million", _round_to_million),),
    ),
    FaultClass(
        "F07", "row_omission", ALL_DTYPES, Arity.RANGE, "abraham_erwig_2009", AE2009,
        "Where a missing investor or holding hides. A RANGE operator: it edits every cell of one "
        "table row, which is still exactly one worksheet part.",
        (FaultOperator("F07.a", "delete_row_values", _blank,
                       note="applied to every cell of one table row"),),
    ),
    FaultClass(
        "F08", "row_duplication", ALL_DTYPES, Arity.RANGE, "abraham_erwig_2009", AE2009,
        "Double count; the tally identities exist for this.",
        (FaultOperator(
            "F08.a", "duplicate_the_value_above", _duplicate_above,
            note="the cell takes the value of the cell one row up, which is what a duplicated row "
                 "looks like cell-wise",
        ),),
    ),
    FaultClass(
        "F09", "date_shift", frozenset({Dtype.DATE}), Arity.CELL, "abraham_erwig_2009", AE2009,
        "FME carries six date bounds. `DD<->MM` is the one a reader cannot see in a rendered date.",
        (
            FaultOperator("F09.a", "plus_one_day", _date_shift(1)),
            FaultOperator("F09.b", "minus_one_quarter", _date_shift(-91)),
            FaultOperator("F09.c", "swap_day_and_month", _date_ddmm),
        ),
    ),
    FaultClass(
        "F10", "enum_substitution", frozenset({Dtype.ENUM}), Arity.CELL, "abraham_erwig_2009",
        AE2009,
        "One LEGAL vocabulary term for another. A membership predicate CANNOT see this, by "
        "construction — it is a DESIGNED MISS and it belongs in the residue. A non-zero kill rate "
        "here would be evidence that something is wrong with the campaign, not that we are good.",
        (FaultOperator("F10.a", "another_legal_member", _enum_other),),
    ),
    FaultClass(
        "F11", "formula_override", frozenset({MONEY, Dtype.COUNT}), Arity.PAIR, "cdfc", "",
        "THE FLAGSHIP. A cell the pinned blank declares a formula for carries a literal. The pair "
        "form leaves the filing perfectly self-consistent because the inconsistency was deleted "
        "with the formula, and TEMPLATE_DIFF is the only thing in the design that detects it.",
        (
            FaultOperator("F11.a", "literal_over_formula", _formula_override),
            FaultOperator(
                "F11.b", "literal_over_formula_pair", _formula_override,
                note="PAIR: the override plus a consistent input change, so the filing stays "
                     "self-consistent and only TEMPLATE_DIFF can see it",
                partner=_pair_partner_source,
            ),
        ),
    ),
    FaultClass(
        "F12", "vocabulary_drift", frozenset({Dtype.ENUM, Dtype.TEXT}), Arity.CELL, "cdfc", "",
        "MEASURED: one live regulated entity's registration number carries `U+2011 NON-BREAKING "
        "HYPHEN` — visually identical, byte-wise different, invisible in any screenshot.",
        (
            FaultOperator("F12.a", "outside_vocabulary", _vocab_outside),
            FaultOperator("F12.b", "homoglyph", _homoglyph),
            FaultOperator("F12.c", "trailing_whitespace", _whitespace),
        ),
    ),
    FaultClass(
        "F13", "carry_desync", frozenset({MONEY, Dtype.COUNT}), Arity.PAIR, "cdfc", "",
        "181 cross-sheet equalities on FME. This is the class they exist for, and the pair form is "
        "the coordinated-misstatement seed.",
        (
            FaultOperator("F13.a", "move_the_target", _carry_desync),
            FaultOperator(
                "F13.b", "move_both_ends", _carry_desync,
                note="PAIR: both ends of the carry move by the same amount, so every cross-sheet "
                     "equality still holds and the number is wrong on both sheets",
                partner=_pair_partner_carry,
            ),
        ),
    ),
    FaultClass(
        "F14", "vocabulary_gap_exploitation", frozenset({Dtype.ENUM}), Arity.CELL, "cdfc", "",
        "MEASURED: the regulator's template computes a scheme total with three COUNTIFs that "
        "between them MISS TWO of its nine legal Type-of-Scheme values. A filing exploiting that "
        "gap is undetectable by any relation the template encodes — P10's residue feedstock.",
        (FaultOperator("F14.a", "legal_but_uncounted", _vocab_gap),),
    ),
)

CLASS_COUNT: Final[int] = 14


def fault_classes(version: str = FAULT_MODEL_VERSION) -> tuple[FaultClass, ...]:
    if version != FAULT_MODEL_VERSION:
        raise ValueError(f"only fault model {FAULT_MODEL_VERSION} is built; asked for {version!r}")
    return FAULT_CLASSES


def by_id(class_id: str) -> FaultClass:
    for c in FAULT_CLASSES:
        if c.id == class_id:
            return c
    raise KeyError(f"{class_id!r} is not a class of fault model {FAULT_MODEL_VERSION}")


def known_ids() -> frozenset[str]:
    return frozenset(c.id for c in FAULT_CLASSES)


def operators(version: str = FAULT_MODEL_VERSION) -> tuple[FaultOperator, ...]:
    return tuple(op for c in fault_classes(version) for op in c.operators)


def class_of_operator(operator_id: str) -> FaultClass:
    return by_id(operator_id.split(".", 1)[0])


def canonical_table(version: str = FAULT_MODEL_VERSION) -> dict[str, Any]:
    return {
        "version": version,
        "classes": [c.as_canonical_obj() for c in fault_classes(version)],
    }


def model_digest(version: str = FAULT_MODEL_VERSION) -> str:
    """sha256 over the RFC 8785 canonical serialisation of the OPERATOR TABLE.

    It enters every qualification record and every campaign manifest, so a record carrying a digest
    this function no longer produces refuses to load — which is what makes "qualified against v3" a
    checkable statement rather than a label.
    """
    return sha256_hex(canonical_json(canonical_table(version)))


def normalise(text: str) -> str:
    """The normalisation F12 and F14 share, and `docs/PROVISO-MARKERS-v1.md` documents.

    NFKC, then whitespace folded, then case-folded. It is deliberately NOT applied inside the
    membership predicates: a homoglyph that normalises to a legal member IS a drift, and
    normalising before the check would make F12.b unkillable by construction.
    """
    folded = unicodedata.normalize("NFKC", text).replace(" ", " ")
    return " ".join(folded.split()).casefold()
