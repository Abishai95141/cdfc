"""PATH B of the unlocked-cell mask — a separately written resolver.

Implements the SAME rule as `docs/PROTECTION-RESOLUTION.md`, and imports NOTHING from
`styles_mask.py`. A differential check between two modules that share a resolver is one
function called twice.

Where it differs, deliberately:

* A resolves the locked bit lazily, per cell, from parallel lists.
  B **pre-resolves the entire style table once** into a flat `tuple[bool, ...]` and then
  indexes it. A bug in inheritance surfaces as a whole-table divergence rather than a
  per-cell one.
* A enumerates worksheet parts through `workbook.xml`'s relationship graph.
  B enumerates them from `[Content_Types].xml`, as reader A′ does — so a part-enumeration
  bug cannot be shared with A.
* A tests `find(<f>) is not None`. B collects the set of formula-bearing cell references
  first and subtracts it, so the exclusion is a set operation rather than a per-cell
  branch.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from cdfc.ingest.xmlsafe import fromstring

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
CTYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
WORKSHEET_CT = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"

DEFAULT_LOCKED = True  # OOXML: a cell is locked unless something says otherwise


def _prefetch_style_locks(z: zipfile.ZipFile, *, absence_means_unlocked: bool) -> tuple[bool, ...]:
    """Resolve EVERY style id up front. Returns locked-bit by style index."""
    try:
        st = fromstring(z.read("xl/styles.xml"))
    except KeyError:
        return ()

    def _lock_of(xf) -> bool | None:
        """None means 'no <protection> element at all' -> inherit (rule 3).

        An element present without @locked is locked by ECMA-376 attribute default
        (rule 2a), which is a resolved True and not an inheritance case.
        """
        prot = xf.find(f"{{{MAIN}}}protection")
        if prot is None:
            return None
        v = prot.get("locked")
        return True if v is None else (v == "1")

    named: list[bool | None] = []
    csx = st.find(f"{{{MAIN}}}cellStyleXfs")
    if csx is not None:
        named = [_lock_of(xf) for xf in csx.findall(f"{{{MAIN}}}xf")]

    resolved: list[bool] = []
    cx = st.find(f"{{{MAIN}}}cellXfs")
    if cx is not None:
        for xf in cx.findall(f"{{{MAIN}}}xf"):
            own = _lock_of(xf)
            if own is not None:
                resolved.append(own)
                continue
            if absence_means_unlocked:
                resolved.append(False)
                continue
            parent_ix = xf.get("xfId")
            parent = None
            if parent_ix is not None and parent_ix.isdigit() and int(parent_ix) < len(named):
                parent = named[int(parent_ix)]
            resolved.append(DEFAULT_LOCKED if parent is None else parent)
    return tuple(resolved)


def _worksheet_parts(z: zipfile.ZipFile) -> list[str]:
    ct = fromstring(z.read("[Content_Types].xml"))
    return sorted(
        o.get("PartName", "").lstrip("/")
        for o in ct.iter(f"{{{CTYPES}}}Override")
        if o.get("ContentType") == WORKSHEET_CT
    )


def count_field_surface(
    blob_path: Path, *, exclude_formula_cells: bool = True, absence_means_unlocked: bool = False
) -> int | None:
    """The denominator, by path B. `None` when no sheet declares protection (rule 6)."""
    with zipfile.ZipFile(blob_path) as z:
        locks = _prefetch_style_locks(z, absence_means_unlocked=absence_means_unlocked)
        parts = [p for p in _worksheet_parts(z) if p in z.namelist()]

        protected_anywhere = False
        parsed = {}
        for part in parts:
            root = fromstring(z.read(part))
            parsed[part] = root
            if root.find(f"{{{MAIN}}}sheetProtection") is not None:
                protected_anywhere = True

        # rule 6, before rule 5
        if not protected_anywhere:
            return None

        total = 0
        for part, root in parsed.items():
            unlocked_refs: set[str] = set()
            formula_refs: set[str] = set()
            for c in root.iter(f"{{{MAIN}}}c"):
                ref = c.get("r", "")
                raw = c.get("s")
                idx = int(raw) if raw is not None and raw.isdigit() else 0
                locked = locks[idx] if idx < len(locks) else DEFAULT_LOCKED
                if not locked:
                    unlocked_refs.add(ref)
                for child in c:
                    if child.tag == f"{{{MAIN}}}f":
                        formula_refs.add(ref)
                        break
            # set subtraction rather than a per-cell branch
            total += len(unlocked_refs - formula_refs if exclude_formula_cells else unlocked_refs)
    return total
