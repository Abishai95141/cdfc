"""Shared-formula materialisation — the master's expression, shifted to the dependent.

A shared formula stores its expression ONCE, on the master, with a `ref` covering the
range it applies to. Every other cell carries `<f t="shared" si="n"/>` and no text. On the
FME workbook that is 211 of 505 formula cells — 42% — and a reader that cannot materialise
them either loses them entirely or, worse, evaluates them with the MASTER's unshifted
references and returns a well-formed number for the wrong row.

Shifting rules, and each is a way to get it silently wrong:

* A relative reference shifts by the delta from master anchor to dependent.
* An ABSOLUTE component (`$`) does not shift. `$C$3` stays `$C$3`; `C$3` shifts its column
  only; `$C3` shifts its row only.
* A shift that carries a reference off the sheet is `#REF!`, not a clamp to row 1. Clamping
  produces a number; `#REF!` produces a finding.
* Sheet-qualified references shift their cell part, not the sheet name.
* Text inside string literals is never a reference and must not be touched.
"""

from __future__ import annotations

import re

# a cell reference with optional absolute markers, optionally sheet-qualified
REF = re.compile(
    r"""(?P<sheet>(?:'[^']+'|[A-Za-z_][\w.]*)!)?
        (?P<cabs>\$?)(?P<col>[A-Z]{1,3})
        (?P<rabs>\$?)(?P<row>\d+)""",
    re.X,
)
STRING = re.compile(r'"(?:[^"]|"")*"')

MAX_ROW = 1_048_576
MAX_COL = 16_384


def _col_to_i(c: str) -> int:
    n = 0
    for ch in c:
        n = n * 26 + (ord(ch) - 64)
    return n


def _i_to_col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def split_ref(ref: str) -> tuple[str, int]:
    m = re.match(r"^\$?([A-Z]{1,3})\$?(\d+)$", ref)
    if not m:
        raise ValueError(f"not a cell reference: {ref!r}")
    return m.group(1), int(m.group(2))


def shift_formula(text: str, drow: int, dcol: int) -> str:
    """Shift every RELATIVE reference in `text` by (drow, dcol).

    String literals are protected: a shift that rewrote `"A1 is required"` would corrupt
    the message a filer reads.
    """
    if drow == 0 and dcol == 0:
        return text

    # protect string literals by substitution, restore afterwards
    literals: list[str] = []

    def _stash(m: re.Match[str]) -> str:
        literals.append(m.group())
        return f"\x00{len(literals) - 1}\x00"

    guarded = STRING.sub(_stash, text)

    def _shift(m: re.Match[str]) -> str:
        sheet = m.group("sheet") or ""
        cabs, rabs = m.group("cabs"), m.group("rabs")
        col_i = _col_to_i(m.group("col"))
        row_i = int(m.group("row"))
        if not cabs:
            col_i += dcol
        if not rabs:
            row_i += drow
        if col_i < 1 or row_i < 1 or col_i > MAX_COL or row_i > MAX_ROW:
            # A shift off the sheet is #REF!, not a clamp. A clamp produces a number.
            return "#REF!"
        return f"{sheet}{cabs}{_i_to_col(col_i)}{rabs}{row_i}"

    shifted = REF.sub(_shift, guarded)
    return re.sub(r"\x00(\d+)\x00", lambda m: literals[int(m.group(1))], shifted)


def materialise(master_ref: str, master_text: str, dependent_ref: str) -> str:
    """The dependent's expression: the master's, shifted by their offset."""
    mc, mr = split_ref(master_ref)
    dc, dr = split_ref(dependent_ref)
    return shift_formula(master_text, dr - mr, _col_to_i(dc) - _col_to_i(mc))
