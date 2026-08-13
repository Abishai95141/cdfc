"""B2 — the degenerate arm: *"no cell is blank and no cell errors"*.

The analogue of `NoException`, which found **68.9%** (rate-ok: a published figure, quoted) of a
published neural oracle's bugs at
**twice** its precision. It is the cheapest possible checker, it needs no regulation and no
template, and a candidate whose marginal kill over it is zero has bought nothing.

Its kill set is derived from evidence already on disk: a mutant kills B2 when its recorded edit
leaves the cell **blank** — no `<v>`, or an empty one — or writes an **Excel error literal**. That
is a rule applied to the committed `killed.jsonl`, not a new measurement.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

ERRORS: Final[frozenset[str]] = frozenset(
    {"#N/A", "#VALUE!", "#REF!", "#DIV/0!", "#NUM!", "#NAME?", "#NULL!"}
)

def kills_edit(new_xml: str) -> bool:
    has_v, text = cell_value(new_xml)
    if not has_v:
        return True  # the cell carries no value at all
    body = text.strip()
    return body == "" or body.upper() in ERRORS

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def cell_value(new_xml: str) -> tuple[bool, str]:
    """`(has a <v> child, its text)` — by PARSING the fragment, never by pattern.

    `ci/no-regex-over-xml.sh` caught the first version of this function matching `<v>([^<]*)</v>`.
    That gate exists because a pattern over OOXML returns a CORRECT COUNT with WRONG CONTENTS, and
    it has done so three times in this repository. A cell fragment is XML; it is parsed.
    """
    from cdfc.ingest.xmlsafe import fromstring

    if not (new_xml or "").strip():
        return False, ""
    try:
        c = fromstring(new_xml.encode("utf-8"))
    except Exception:  # noqa: BLE001 - a fragment we cannot parse carries no value we can read
        return False, ""
    v = c.find(f"{{{M}}}v")
    if v is None:
        v = c.find("v")  # a fragment written without the default namespace
    if v is None:
        return False, ""
    return True, (v.text or "")



def kill_set(killed_rows: Sequence[Mapping]) -> frozenset[str]:
    out: set[str] = set()
    for row in killed_rows:
        if row.get("observability") != "OBSERVABLE":
            continue
        if any(kills_edit(e.get("new_xml", "")) for e in row.get("edits") or ()):
            out.add(row["mutant_sha256"])
    return frozenset(out)


def predicate_text() -> str:
    """B2 as a sentence, so a report can print what it was compared against."""
    return "no cell is blank and no cell errors"
