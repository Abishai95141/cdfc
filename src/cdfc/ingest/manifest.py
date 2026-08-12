"""The extraction manifest — what was read, what was skipped, and WHAT WAS NOT UNDERSTOOD.

An output, not a log. A log is something nobody reads; a manifest is something a verdict
is conditioned on. The distinction is enforced: this object is frozen, it serialises
through `canonical_json`, and `test_contract__manifest_is_not_a_log` fails the build if a
free-text field appears anywhere other than a per-skip reason.

`constructs_not_understood` is the field that matters and the one with a declared limit.
It records qualified names the reader met and did not model — but it can only contain
**what we knew to look for**. A construct in a namespace we never enumerate is invisible
to it. This build does not close that hole; it makes the residue visible, which is the
difference between an unknown and an unknown nobody wrote down.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


class SkipWithoutReason(ValueError):
    """A skipped part with no stated reason. A silent skip is the defect this file exists for."""


@dataclass(frozen=True)
class Construct:
    part: str
    qname: str
    count: int
    first_ref: str | None

    def as_canonical_obj(self) -> dict[str, Any]:
        return {"part": self.part, "qname": self.qname, "count": self.count,
                "first_ref": self.first_ref}


@dataclass(frozen=True)
class ExtractionManifest:
    reader: str
    parts_read: tuple[str, ...]
    parts_skipped: tuple[tuple[str, str], ...]
    namespaces_seen: tuple[str, ...]
    constructs_not_understood: tuple[Construct, ...]
    guard: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for part, reason in self.parts_skipped:
            if not reason or not reason.strip():
                raise SkipWithoutReason(
                    f"part {part!r} was skipped with no reason. A skip with no reason is "
                    "indistinguishable from a part nobody looked at."
                )

    def as_canonical_obj(self) -> dict[str, Any]:
        return {
            "reader": self.reader,
            "parts_read": list(self.parts_read),
            "parts_skipped": [[p, r] for p, r in self.parts_skipped],
            "namespaces_seen": sorted(self.namespaces_seen),
            "constructs_not_understood": [c.as_canonical_obj() for c in self.constructs_not_understood],
            "guard": dict(self.guard) if self.guard else None,
        }


# The qualified names this reader models. Anything else met inside a worksheet part is
# recorded as not-understood. The set is deliberately explicit: a wildcard would make the
# residue field always empty, which is the same as not having it.
MODELLED = frozenset(
    {
        "c", "f", "v", "is", "t", "r", "row", "sheetData", "worksheet", "dimension",
        "sheetViews", "sheetView", "selection", "sheetFormatPr", "cols", "col",
        "sheetProtection", "mergeCells", "mergeCell", "dataValidations", "dataValidation",
        "formula1", "formula2", "pageMargins", "pageSetup", "printOptions", "extLst", "ext",
        "conditionalFormatting", "cfRule", "hyperlinks", "hyperlink", "autoFilter",
        "phoneticPr", "rPh", "legacyDrawing", "drawing", "tableParts", "tablePart",
        "headerFooter", "oddHeader", "oddFooter", "rowBreaks", "colBreaks", "brk",
        "picture", "controls", "control", "customSheetViews", "customSheetView",
        "dataConsolidate", "ignoredErrors", "ignoredError", "pane", "protectedRanges",
        "protectedRange", "sortState", "scenarios", "outlinePr", "pageSetUpPr",
    }
)


def scan_constructs(part: str, root: Any) -> tuple[list[Construct], set[str]]:
    """Walk a parsed part; return unmodelled qualified names and every namespace seen."""
    seen_ns: set[str] = set()
    counts: dict[str, int] = {}
    first: dict[str, str | None] = {}
    for el in root.iter():
        tag = el.tag
        if not isinstance(tag, str):
            continue
        if tag.startswith("{"):
            ns, local = tag[1:].split("}", 1)
            seen_ns.add(ns)
        else:
            ns, local = "", tag
        if local in MODELLED:
            continue
        counts[tag] = counts.get(tag, 0) + 1
        first.setdefault(tag, el.get("r") or el.get("ref") or el.get("sqref"))
    constructs = [
        Construct(part=part, qname=q, count=n, first_ref=first.get(q))
        for q, n in sorted(counts.items())
    ]
    return constructs, seen_ns


def build(
    *,
    reader: str,
    parts_read: Iterable[str],
    parts_skipped: Iterable[tuple[str, str]] = (),
    namespaces_seen: Iterable[str] = (),
    constructs_not_understood: Iterable[Construct] = (),
    guard: Mapping[str, Any] | None = None,
) -> ExtractionManifest:
    return ExtractionManifest(
        reader=reader,
        parts_read=tuple(parts_read),
        parts_skipped=tuple(parts_skipped),
        namespaces_seen=tuple(sorted(set(namespaces_seen))),
        constructs_not_understood=tuple(constructs_not_understood),
        guard=guard,
    )
