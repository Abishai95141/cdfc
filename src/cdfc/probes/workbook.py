"""One reader for the probe layer: the header text and the typed cell values of a workbook.

**Why this exists rather than an import of the harvest context.** `degree.py` needs a sheet's
header text and `template_diff.py` needs a filing's values. Both are available from
`cdfc.predicates.harvest._load_context`, and taking them from there would pull the entire harvest
— every harvest class, the CEL profile, the envelope, the loader — into `probes/`'s import
closure. That closure is not cosmetic: `g4_ffr.independent()` decides whether a corpus is an
admissible oracle for a predicate by intersecting the corpus generator's import closure with the
evaluation's, so a probe that drags in modules it never executes reports itself less independent
than it is, and a probe that shares a *computing* module with a generator must be caught. A
closure used as evidence has to be the truth.

**The typing rule is written here rather than imported from `cdfc.qualify.corpus._writer`, and
that duplication is deliberate.** `_writer` is inside the corpus generator's closure. Importing
its `_typed` would put the generator's own module into the checker's closure and make
`TEMPLATE_DIFF` non-independent of the corpus by construction — which is F2 exactly, arriving
through a two-line convenience import. The rule is nine lines and it is stated in both places.
"""

from __future__ import annotations

import zipfile
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cdfc.ingest.reader_lxml import _sheet_parts
from cdfc.ingest.xmlsafe import fromstring

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

Value = Decimal | str | bool | None


def _typed(text: str) -> Decimal | str:
    """A stored value carries its TYPE, not just its characters.

    A numeric cached value is a number; anything that does not parse as one stays a string,
    which is what an error literal or a genuine text result is. `Decimal`, never `float` (R4):
    a float in a filing is a value nobody can re-derive.
    """
    t = (text or "").strip()
    if not t:
        return t
    try:
        return Decimal(t)
    except (TypeError, ValueError, InvalidOperation):
        return text


def _shared_strings(z: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    ss = fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{{{M}}}t")) for si in ss.iter(f"{{{M}}}si")]


def read_grid(blob: Path) -> tuple[dict[str, dict[str, str]], dict[tuple[str, str], Value]]:
    """`(text by sheet, typed values by (sheet, ref))` in one pass over the archive.

    `text` holds only cells whose content is textual — the header and label material a degree
    assignment reads. `values` holds every cell, typed, formula cells included: the stored value
    of a formula cell is exactly what `TEMPLATE_DIFF` compares its recomputation against.
    """
    text: dict[str, dict[str, str]] = {}
    values: dict[tuple[str, str], Value] = {}
    with zipfile.ZipFile(blob) as z:
        shared = _shared_strings(z)
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            t: dict[str, str] = {}
            for c in root.iter(f"{{{M}}}c"):
                ref = c.get("r") or ""
                node = c.find(f"{{{M}}}v")
                raw = node.text if node is not None else None
                if raw is None:
                    inline = c.find(f"{{{M}}}is")
                    raw = (
                        "".join(x.text or "" for x in inline.iter(f"{{{M}}}t"))
                        if inline is not None else None
                    )
                if raw is None:
                    continue
                if c.get("t") == "s":
                    try:
                        raw = shared[int(raw)]
                    except (ValueError, IndexError):
                        raw = ""
                typed = raw if c.get("t") in ("s", "str", "inlineStr") else _typed(raw)
                values[(name, ref)] = typed
                if isinstance(typed, str):
                    t[ref] = typed
            text[name] = t
    return text, values


def cell_text(blob: Path) -> dict[str, dict[str, str]]:
    return read_grid(blob)[0]


def filed_values(blob: Path) -> dict[tuple[str, str], Value]:
    return read_grid(blob)[1]
