"""Sequence alignment over row signatures, with an explicit refusal when it is ambiguous."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Unaligned(StrEnum):
    """Why a field has no counterpart. CLOSED — and BOTH sides are declared, never just one."""

    DROPPED_BY_FILER = "dropped_by_filer"      # in the blank, absent from the filing
    ADDED_BY_FILER = "added_by_filer"          # in the filing, not declared by the blank
    ROW_UNMATCHED = "row_unmatched"            # its row aligned to nothing
    AMBIGUOUS = "ambiguous"                    # two candidate alignments of similar quality


@dataclass(frozen=True, slots=True)
class RowKey:
    sheet: str
    row: int


@dataclass(frozen=True, slots=True)
class Correspondence:
    """Which field here is which field there, and everything that did not align."""

    pairs: tuple[tuple[str, str], ...]                  # (blank ref, filing ref)
    unaligned: tuple[tuple[str, Unaligned], ...]
    blank_total: int
    filing_total: int
    ambiguous: bool
    detail: str = ""

    @property
    def aligned(self) -> int:
        return len(self.pairs)

    def lines(self) -> tuple[str, ...]:
        by: dict[str, int] = {}
        for _ref, why in self.unaligned:
            by[why.value] = by.get(why.value, 0) + 1
        out = [
            f"blank fields      {self.blank_total}",
            f"filing fields     {self.filing_total}",
            f"ALIGNED           {self.aligned} of {self.blank_total}",
        ]
        for k, v in sorted(by.items()):
            out.append(f"  {k:22} {v}")
        if self.ambiguous:
            out.append(f"REFUSED: {self.detail}")
        return tuple(out)


def _split(ref: str) -> tuple[int, int]:
    letters = "".join(c for c in ref if c.isalpha()).upper()
    digits = "".join(c for c in ref if c.isdigit())
    col = 0
    for ch in letters:
        col = col * 26 + (ord(ch) - 64)
    return (col, int(digits or 0))


def _signatures(blob: Path) -> dict[RowKey, tuple[tuple[int, str], ...]]:
    """Each row's CONTENT signature: its text cells by column.

    Text, not values: a filer changes values and that must not move the alignment. Two rows with
    the same labels in the same columns are the same row of the form.
    """
    from cdfc.evidence.workbook import read_cells

    rows: dict[RowKey, list[tuple[int, str]]] = {}
    for c in read_cells(blob):
        if not c.text or not c.is_text:
            continue
        col, row = _split(c.ref)
        rows.setdefault(RowKey(c.sheet, row), []).append((col, c.text.strip()))
    return {k: tuple(sorted(v)) for k, v in rows.items()}


def _lcs_pairs(a: list, b: list) -> list[tuple[int, int]]:
    """Longest common subsequence over row signatures, returned as index pairs.

    An insertion, a deletion and a reordering are all edits to a sequence, and an LCS reads all
    three. It is O(n*m) and the sheets here are hundreds of rows, not millions.
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = dp[i + 1][j + 1] + 1 if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    out: list[tuple[int, int]] = []
    i = j = 0
    while i < n and j < m:
        if a[i] == b[j]:
            out.append((i, j))
            i, j = i + 1, j + 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return out


def correspond(blank: Path, filing: Path, *, ambiguity_margin: float = 0.02) -> Correspondence:
    """Align the filing's fields to the blank's, or refuse.

    `ambiguity_margin`: if a sheet's alignment covers less than this fraction more than the
    trivial identity alignment would, the result is not trusted. Two candidate alignments of
    similar quality is the same hazard as two pinned blanks sharing a sheet set, and it must stay
    a refusal rather than become a coin toss.
    """
    from cdfc.measure.p5_run import surface_for

    blank_refs = sorted(surface_for(blank)[1])
    filing_refs = sorted(surface_for(filing)[1])
    sa, sb = _signatures(blank), _signatures(filing)

    sheets = sorted({k.sheet for k in sa} | {k.sheet for k in sb})
    row_map: dict[tuple[str, int], int] = {}
    shifts: dict[str, list[tuple[int, int]]] = {}
    ambiguous, detail = False, ""

    for sheet in sheets:
        ra = sorted(k.row for k in sa if k.sheet == sheet)
        rb = sorted(k.row for k in sb if k.sheet == sheet)
        siga = [sa[RowKey(sheet, r)] for r in ra]
        sigb = [sb[RowKey(sheet, r)] for r in rb]
        anchors = [(ra[i], rb[j]) for i, j in _lcs_pairs(siga, sigb)]
        for src, dst in anchors:
            row_map[(sheet, src)] = dst

        # --- ROWS WITH NO TEXT ARE CARRIED BY THE ANCHORS AROUND THEM -----------------------
        #
        # A row of pure data has no signature, so it never enters the LCS and would be reported
        # ROW_UNMATCHED. That is not a subtle case: it made the blank fail to align to ITSELF,
        # which the positive control caught. Once the text rows on either side are anchored, an
        # empty row between them is DETERMINED -- it sits at the same offset from its anchor,
        # which is exactly what a row insertion does to it.
        #
        # An empty row BELOW the last anchor takes that anchor's shift. One above the first
        # anchor takes the first anchor's shift. Neither is a guess: the shift is measured from
        # rows whose signatures matched.
        if anchors:
            for key in (k for k in sa if k.sheet == sheet):
                if (sheet, key.row) in row_map:
                    continue
                prior = [a for a in anchors if a[0] <= key.row]
                src, dst = (prior[-1] if prior else anchors[0])
                row_map[(sheet, key.row)] = key.row + (dst - src)
            # Rows present on the surface but carrying no text at all never reach `sa`, so they
            # are shifted by the same rule, resolved lazily at cell time below.
            shifts[sheet] = anchors
        # A sheet whose rows are ALL distinct signatures aligns trivially and tells us nothing;
        # one whose rows repeat can align many ways. Both are declared rather than assumed away.
        if siga and len({s for s in siga}) < len(siga) * (1 - ambiguity_margin):
            ambiguous = True
            detail = (f"{sheet}: {len(siga) - len(set(siga))} of {len(siga)} rows share a "
                      "signature, so more than one alignment fits")

    filing_set = set(filing_refs)
    pairs: list[tuple[str, str]] = []
    unaligned: list[tuple[str, Unaligned]] = []
    matched_filing: set[str] = set()

    for ref in blank_refs:
        sheet, cell = ref.rsplit("!", 1)
        col, row = _split(cell)
        tgt_row = row_map.get((sheet, row))
        if tgt_row is None:
            anchors = shifts.get(sheet)
            if not anchors:
                unaligned.append((ref, Unaligned.ROW_UNMATCHED))
                continue
            prior = [a for a in anchors if a[0] <= row]
            src, dst = (prior[-1] if prior else anchors[0])
            tgt_row = row + (dst - src)
        letters = "".join(c for c in cell if c.isalpha())
        cand = f"{sheet}!{letters}{tgt_row}"
        if cand in filing_set:
            pairs.append((ref, cand))
            matched_filing.add(cand)
        else:
            unaligned.append((ref, Unaligned.DROPPED_BY_FILER))

    for ref in filing_refs:
        if ref not in matched_filing:
            unaligned.append((ref, Unaligned.ADDED_BY_FILER))

    return Correspondence(
        pairs=tuple(pairs), unaligned=tuple(unaligned),
        blank_total=len(blank_refs), filing_total=len(filing_refs),
        ambiguous=ambiguous, detail=detail,
    )
