"""P9-B1 — the degree map. **Money is degree 1 and gets `τ(n) = 5n`. Everything else is 0.**

`'1. Introduction'!D17` is *"Total No. of Schemes of the FME authorised by IFSCA"*, computed as
`SUM(D18:D20)` over three COUNTIF-bearing rows. Under a blanket `τ(n) = 5n` a filing could be
wrong by **fifteen schemes** and the check would pass. **A person, and a scheme, is not a rounded
quantity** — so the tolerance is zero unless the cell is *positively established* as money.

**The direction of the default is the whole design.** A tolerance wrongly applied to a count hides
a fault and nothing goes red; a tolerance wrongly withheld from a money cell produces a false
alarm, which is visible, arguable and cheap. So `MONEY` must be proved and everything else is the
fallback — never the other way round.

**The evidence is the regulator's own text, and it travels with the answer.** FME's tables declare
their units on their face: `Table 3.1: … (USD Million)`, `Amount (USD Million)`, `(Nos.)`,
`No. of Investors`, `Number of complaints …`. A degree assigned without naming the cell and the
string that licensed it is an opinion, so `Assignment` carries both and `test_degree__every_money_cell_names_its_evidence`
asserts it. This is step 1 of P9-B2's authoring protocol applied to a value rather than a relation:
*name the artifact fact, or it is a refusal.*

**Nearest marker wins, and a tie is a refusal.** A `%` column inside a `(USD Million)` table is a
ratio, not money, and the column header is nearer than the table title. When one level carries
both a money marker and a count marker, that level is `AMBIGUOUS` and the degree is 0 — a tie
broken towards money would be the one silent path back to a tolerance on a count.

**A DEFECT THIS MODULE DOES NOT FIX, and it is recorded rather than quietly worked around.**
`harvest_classes/sum_identity.py` gives EVERY `=SUM(range)` a `tau(n) = 5n` tolerance without
asking what the cells hold, so the harvested predicate over `'1. Introduction'!D17` carries
`τ = 15` today. That is NC-E08's defect standing in the harvest, and repairing it moves every
envelope digest and P7's whole funnel — outside P9's scope and too large to do as a side effect.
`docs/measurements/P9-template-diff-ceiling.md` publishes the count of harvested predicates whose
tolerance this module would refuse, dated, as an open item.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from cdfc.schema.anchor import Anchor
from cdfc.schema.stable_keys import col_to_index, split_ref

CellKey = str

Degree = Literal[0, 1]
Basis = Literal["MONEY_MARKER", "COUNT_MARKER", "RATIO_MARKER", "DATE_MARKER", "AMBIGUOUS", "NO_MARKER"]

# The regulator's own unit declarations, lower-cased. Deliberately narrow: a broad money
# vocabulary is a tolerance applied to whatever it over-matched, which is the failure this
# module exists to prevent. Every string below appears verbatim in the FME workbook.
#
# **Written WITHOUT parentheses**, because `_parenthesised` strips them before classifying. A
# marker spelled `(nos.)` never matched the inner text `Nos.`, so every table whose unit sits in
# a parenthesis-only header cell — `'4. Investors'!C3` — fell through to `NO_MARKER`. It reached
# the right degree by the wrong route, which is the shape that survives a test asserting only the
# number.
MONEY_MARKERS: Final[tuple[str, ...]] = ("usd million", "usd mn", "in usd", "usd")

# Counts. `no.` is not in the list on its own — `Phone No.` and `Registration No.` are neither
# counts nor money, and matching them would only move a cell from one degree-0 basis to another,
# but the basis is published, so it must be true and not merely harmless.
COUNT_MARKERS: Final[tuple[str, ...]] = (
    "nos.", "nos", "no. of", "nos. of", "number of", "no of", "count of",
    "s. no", "sl. no", "s.no", "total no.",
)

RATIO_MARKERS: Final[tuple[str, ...]] = ("%", "percentage", "per cent", "ratio")

# **"as at the end of quarter" is NOT a date marker, and neither is "period".** They say WHEN a
# figure is measured, not WHAT it is measured in — and the regulator writes them in the same
# sentence as the unit: `Total Portfolio Value of Scheme, as at the end of quarter (in USD
# Million)`. Reading them as unit declarations made that column AMBIGUOUS and cost it its
# tolerance. A date marker has to say the cell HOLDS a date.
DATE_MARKERS: Final[tuple[str, ...]] = ("date", "dates", "dd/mm/yyyy")

# How far up a column to look for a header before giving up. Twelve is `build_keys`'s own reach;
# using a different number here would make two modules disagree about what a header is.
HEADER_REACH: Final[int] = 12


@dataclass(frozen=True, slots=True)
class Assignment:
    cell: CellKey
    degree: Degree
    basis: Basis
    evidence_cell: str | None
    evidence_text: str | None

    def __post_init__(self) -> None:
        if self.degree == 1 and not self.evidence_text:
            raise ValueError(
                f"{self.cell} was assigned degree 1 with no evidence. Money is the degree that "
                "buys a tolerance, so it is the one that must name the regulator's own words."
            )


def tau_for(a: Assignment, n_summands: int) -> int:
    """`τ(n) = 5n` units for degree 1; **0** for everything else. Integers only."""
    from cdfc.facts.units import tau

    return tau(n_summands) if a.degree == 1 else 0


def _parenthesised(text: str) -> str:
    """Only the `(…)` groups. **A table title is prose; a parenthesis is a declaration.**

    `Table 3.6: … in which 30% or more of the Total   rate-ok:the-regulator's-own-title-text
    Portfolio Value` contains `%`, and `Table 3.1: … as at the end of quarter (USD Million)`
    contains a date phrase. Neither says anything about the units of a column. Reading whole
    titles as unit declarations made 46 of FME's 505 formula cells `AMBIGUOUS` — including
    `'3. Portfolio'!O7`, the flagship's own worked example — because the regulator writes
    *when* the figure is measured in the same sentence as *what* it is measured in.

    The regulator's unit idiom is parenthesised and it is used consistently: `(USD Million)`,
    `(Nos.)`. So above the column header, only parentheses are read.
    """
    out, depth, buf = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
            if depth == 1:
                buf = []
                continue
        elif ch == ")":
            if depth == 1:
                out.append("".join(buf))
            depth = max(0, depth - 1)
            continue
        if depth >= 1:
            buf.append(ch)
    return " ; ".join(out)


def _tokens(text: str) -> tuple[str, ...]:
    """Lower-cased words. Punctuation other than `.` and `%` becomes a space, and `%` is split
    off so that a percent sign is its own token.   rate-ok:no-rate-here,-a-tokeniser-rule

    **Tokens and not substrings, and it cost a real misclassification to learn.** `ratio` is a
    substring of `Registration`, so `'1. Introduction'!D40` — *"Date of Registration of FME"* —
    matched both the date marker and the ratio marker and came out `AMBIGUOUS`. A degree decided
    by substring is a degree decided by whatever the marker list accidentally spells.
    """
    out: list[str] = []
    buf: list[str] = []
    for ch in text.lower():
        if ch.isalnum() or ch == ".":
            buf.append(ch)
            continue
        if buf:
            out.append("".join(buf))
            buf = []
        if ch == "%":
            out.append("%")
    if buf:
        out.append("".join(buf))
    return tuple(out)


def _has(marker: str, tokens: tuple[str, ...]) -> bool:
    """`marker`'s own tokens appearing consecutively in `tokens`."""
    want = _tokens(marker)
    if not want:
        return False
    return any(
        tokens[i : i + len(want)] == want for i in range(len(tokens) - len(want) + 1)
    )


def _classify(text: str) -> Basis | None:
    """The basis a single string licenses, or `None` when it says nothing about units."""
    t = _tokens(text)
    hits = {
        "MONEY_MARKER": any(_has(m, t) for m in MONEY_MARKERS),
        "COUNT_MARKER": any(_has(m, t) for m in COUNT_MARKERS),
        "RATIO_MARKER": any(_has(m, t) for m in RATIO_MARKERS),
        "DATE_MARKER": any(_has(m, t) for m in DATE_MARKERS),
    }
    found = [k for k, v in hits.items() if v]
    if not found:
        return None
    if len(found) > 1:
        # Both a money and a non-money marker at the same distance. A tie broken towards money
        # is the only silent path back to a tolerance on a count, so the tie is the refusal.
        return "AMBIGUOUS"
    return found[0]  # type: ignore[return-value]


def _by_row(sheet_text: Mapping[str, str]) -> dict[int, list[tuple[int, str, str]]]:
    """`row -> [(column index, ref, text)]`, sorted left to right."""
    rows: dict[int, list[tuple[int, str, str]]] = {}
    for ref, txt in sheet_text.items():
        try:
            col, row = split_ref(ref)
        except ValueError:
            continue
        if txt.strip():
            rows.setdefault(row, []).append((col_to_index(col), ref, txt))
    for cells in rows.values():
        cells.sort()
    return rows


def _table_title_row(rows: Mapping[int, list[tuple[int, str, str]]], row: int) -> int:
    """The row of the nearest `Table n.m: …` heading at or above `row`, else 1.

    It bounds the unit search. **Without the bound, a table that declares no unit inherits the
    previous table's** — which is how a count acquires a tolerance from a sentence written about
    a different table three screens up.
    """
    candidates = [
        r for r in rows
        if r <= row and any(t.strip().lower().startswith("table ") for _c, _ref, t in rows[r])
    ]
    return max(candidates) if candidates else 1


def column_spans(merged_ranges: tuple[str, ...]) -> dict[str, tuple[int, int]]:
    """`anchor ref -> (first column index, last column index)` for every merged range.

    **This is what stops a unit declaration leaking sideways.** The regulator writes a table-wide
    unit as a MERGED cell across the data block — `'4. Investors'!C3` is `C3:N3`, so `(Nos.)`
    genuinely applies to columns C through N — and a per-column unit as an ordinary cell:
    `'2. Summary'!G4`, *"Stated Target Corpus … (USD Million)"*, is not merged and applies to
    column G alone.

    Reading every parenthesised unit as table-wide put **130 of 223** published `MONEY_MARKER`
    cells on text columns — `Type of Scheme`, `Name of Scheme`, `IFSCA Authorisation Number` —
    each licensed by `G4`, seven columns away. The published count of money cells was not a count
    of money cells, and the guard was a pinned integer plus a check that the evidence field was
    non-empty — never that the string named THAT cell's unit.
    """
    out: dict[str, tuple[int, int]] = {}
    for rng in merged_ranges:
        if ":" not in rng:
            continue
        a, b = rng.split(":", 1)
        try:
            ca, _ra = split_ref(a)
            cb, _rb = split_ref(b)
        except ValueError:
            continue
        lo, hi = col_to_index(ca), col_to_index(cb)
        prev = out.get(a)
        # A ref can anchor more than one range (FME has `A1:O1` and `A1:C1`). The WIDEST span is
        # the one the regulator drew across the table; a narrower duplicate is a leftover.
        if prev is None or (hi - lo) > (prev[1] - prev[0]):
            out[a] = (lo, hi)
    return out


def assign(
    sheet: str,
    ref: str,
    sheet_text: Mapping[str, str],
    spans: Mapping[str, tuple[int, int]] | None = None,
) -> Assignment:
    """One cell's degree, with the string that licensed it. NEAREST marker wins.

    Three levels, and they do not read the same way:

    1. **the cell's own row label** — the leftmost text on its row. Full prose, all markers.
    2. **the column header** — the nearest non-empty text above it in its own column. Full prose.
    3. **the table's unit declaration** — the nearest *parenthesised* unit at or above the cell,
       anywhere in the table, bounded below by the table's own title row. Parentheses only.
    """
    cell = Anchor.cell(sheet, ref).render()
    col, row = split_ref(ref)
    rows = _by_row(sheet_text)

    def answer(basis: Basis, evidence_cell: str, text: str) -> Assignment:
        return Assignment(
            cell=cell,
            degree=1 if basis == "MONEY_MARKER" else 0,
            basis=basis,
            evidence_cell=Anchor.cell(sheet, evidence_cell).render(),
            evidence_text=text.strip()[:120],
        )

    # 1 — the row label
    for _ci, r, txt in rows.get(row, []):
        basis = _classify(txt)
        if basis is not None:
            return answer(basis, r, txt)
        break

    # 2 — the column header
    for rr in range(row - 1, max(0, row - HEADER_REACH) - 1, -1):
        txt = sheet_text.get(f"{col}{rr}", "")
        if txt.strip():
            basis = _classify(txt)
            if basis is not None:
                return answer(basis, f"{col}{rr}", txt)
            break

    # 3 — the table's parenthesised unit declaration, SCOPED TO THE COLUMNS IT SPANS
    spans = spans or {}
    ci = col_to_index(col)
    floor = _table_title_row(rows, row)
    for rr in range(row, floor - 1, -1):
        for _ci2, r, txt in rows.get(rr, []):
            inside = _parenthesised(txt)
            if not inside:
                continue
            # A TABLE TITLE is table-wide by nature: it names the table, so its unit applies
            # across it whether or not the regulator merged the cell. FME merges them (`A1:O1`);
            # a template that did not would otherwise lose the declaration entirely.
            title = txt.strip().lower().startswith("table ")
            lo, hi = spans.get(r, (_ci2, _ci2))
            if not title and not (lo <= ci <= hi):
                # A unit that does not span this column is another column's unit. `'2. Summary'!G4`
                # licensed `Type of Scheme` and `Name of Scheme` as money before this line existed.
                continue
            basis = _classify(inside)
            if basis is not None:
                return answer(basis, r, txt)

    return Assignment(cell=cell, degree=0, basis="NO_MARKER", evidence_cell=None, evidence_text=None)


def degree_map(blob: Path, cells: object = None) -> dict[CellKey, Assignment]:
    """The degree of every formula cell of the pinned blank (or of `cells`, if given).

    Built from the blank, never from a filing: a unit read from the filed artifact is a unit the
    filer could edit, which is NC-D01c.
    """
    from cdfc.ingest.reader_lxml import read
    from cdfc.probes.workbook import cell_text

    from decimal import Decimal

    from cdfc.probes.workbook import filed_values

    wb = read(blob)
    text = cell_text(blob)
    spans = column_spans(wb.merged_ranges)
    cached = filed_values(blob)
    if cells is None:
        targets = sorted((f.sheet, f.ref) for f in wb.formulas)
    else:
        targets = sorted(tuple(c.split("!", 1)) for c in cells)  # type: ignore[arg-type]

    out: dict[CellKey, Assignment] = {}
    for sheet, ref in targets:
        a = assign(sheet, ref, text.get(sheet, {}), spans)
        # --- THE CACHED-VALUE VETO, and it can only move a cell OUT of money ------------------
        #
        # A formula cell whose value IN THE PINNED BLANK is a non-numeric string is not an amount,
        # whatever any header says. `'3. Portfolio'!B7` caches `'NA'` and carries a scheme NAME;
        # `O7` caches `0` and carries a total. The regulator's own artifact separates them, and no
        # reading of the header text can.
        #
        # This exists because a table title legitimately spans its whole table — `A1:O1` on
        # Portfolio — so `(USD Million)` reaches the `Name of Scheme` column, and the blank's `NA`
        # placeholder rows sit between the cell and its real header, masking it. 30 cells survived
        # the column-span rule that way.
        #
        # It is a VETO and never a licence: it can take degree 1 to 0 and never the reverse, which
        # is the direction this module's default already argues for — a tolerance wrongly withheld
        # is a visible false alarm, one wrongly applied hides a fault.
        if a.degree == 1:
            v = cached.get((sheet, ref))
            if isinstance(v, str) and v.strip():
                try:
                    Decimal(v.strip())
                except Exception:  # noqa: BLE001 — a non-numeric cached value is the whole signal
                    a = Assignment(
                        cell=a.cell, degree=0, basis="NO_MARKER",
                        evidence_cell=a.evidence_cell,
                        evidence_text=f"the blank caches {v.strip()[:24]!r} here, so it is not an amount",
                    )
        out[Anchor.cell(sheet, ref).render()] = a
    return out
