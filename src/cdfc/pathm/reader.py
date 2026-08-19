"""The published rule set, read off the raw zip. **Never openpyxl, never Docling.**

openpyxl silently drops the `x14` namespace (NC-CI02 turns its warning into an error) and Docling
drops formulas from spreadsheets. Neither matters for THIS file — it is a flat table — but the
reader is the same one the rest of the build uses, so the reason it is not openpyxl is that a
second reader is a second set of blind spots.

Every parse goes through `cdfc.ingest.xmlsafe.fromstring`, the ONE hardened factory. `NC-P08`
walks the AST to prove there is no second door.
"""

from __future__ import annotations

import hashlib
import re
import zipfile
from pathlib import Path

from cdfc.ingest.xmlsafe import fromstring
from cdfc.pathm.statement import PublishedRule, RuleSet

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# The publication date comes from the FILE'S OWN NAME, never from a clock and never from a
# spreadsheet cell. `of N published at date D` is a claim about the publisher's artefact, so D must
# be a property of that artefact.
DATE_IN_NAME = re.compile(r"(\d{4})[_-](\d{2})[_-](\d{2})")


class RuleSetError(RuntimeError):
    """The file is not a published rule set. Never downgraded to an empty one."""


def _shared(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    return ["".join(si.itertext()) for si in fromstring(z.read("xl/sharedStrings.xml")).iter(f"{M}si")]


def _cell(c, shared: list[str]) -> str:
    t = c.get("t")
    if t == "inlineStr":
        n = c.find(f"{M}is")
        return "".join(n.itertext()) if n is not None else ""
    v = c.find(f"{M}v")
    if v is None or v.text is None:
        return ""
    if t == "s":
        try:
            return shared[int(v.text)]
        except (ValueError, IndexError):
            return ""
    return v.text


def _col(ref: str) -> int:
    """`"AB12"` -> 27 (0-based). A row's cells may be SPARSE, so position by reference."""
    letters = "".join(ch for ch in ref if ch.isalpha()).upper()
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read(blob: Path) -> RuleSet:
    """Every published rule, with the columns named by the file's own header row."""
    raw = blob.read_bytes()
    with zipfile.ZipFile(blob) as z:
        shared = _shared(z)
        sheets = sorted(n for n in z.namelist()
                        if n.startswith("xl/worksheets/") and n.endswith(".xml"))
        if not sheets:
            raise RuleSetError(f"{blob}: no worksheet part")
        rows = list(fromstring(z.read(sheets[0])).iter(f"{M}row"))
    if len(rows) < 2:
        raise RuleSetError(f"{blob}: {len(rows)} rows; a rule set with no rules is not a rule set")

    def cells(row) -> dict[int, str]:
        return {_col(c.get("r") or "A1"): _cell(c, shared) for c in row.iter(f"{M}c")}

    header = {v.strip().lower(): i for i, v in cells(rows[0]).items()}
    need = ("vr code", "expression", "tables", "isactive")
    missing = [k for k in need if k not in header]
    if missing:
        raise RuleSetError(
            f"{blob}: header is missing {missing}. Found {sorted(header)}. A reader that "
            "defaulted a missing column would publish a coverage table over a population it "
            "could not see."
        )

    def get(c: dict[int, str], name: str) -> str:
        i = header.get(name)
        return (c.get(i, "") if i is not None else "").strip()

    out: list[PublishedRule] = []
    for row in rows[1:]:
        c = cells(row)
        code = get(c, "vr code")
        if not code:
            continue
        out.append(PublishedRule(
            code=code,
            framework=get(c, "frameworks"),
            module=get(c, "modules"),
            tables=get(c, "tables"),
            expression=get(c, "expression"),
            precondition=get(c, "precondtion") or get(c, "precondition"),
            description=get(c, "description"),
            active=get(c, "isactive").lower() != "inactive",
            severity=get(c, "severity"),
        ))

    m = DATE_IN_NAME.search(blob.name)
    return RuleSet(
        source_name=blob.name,
        source_sha256=hashlib.sha256(raw).hexdigest(),
        published_at=("-".join(m.groups()) if m else ""),
        rules=tuple(out),
    )
