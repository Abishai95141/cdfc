"""P5 — the fact model, built from a filing and a pinned blank.

**The convention is the harvest's, stated once in `predicates/harvest.py` and reproduced here
because two builders of one shape drift.** A cell is `{v, __cell__}`; a range is `{cells: [...]}`;
a vocabulary is `template.vocab.<slug>`. `cel_path(sheet, ref)` is the key, and it is derived from
the pinned template so a filing bound to that template addresses the same cells.

**A blank NUMERIC cell is ABSENT, not zero.** There is no integer that means "empty", and mapping
one to `0` is F05's blank-and-zero conflation — which the fault model carries as two operators
rather than one. A blank TEXT or ENUM cell is the empty string, because a predicate must be able
to say `r.scheme_type == ""`.

**The template side resolves from the PINNED BLANK, never from the filing** (NC-D01c).
"""

from __future__ import annotations

import zipfile
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from cdfc.facts.fact_table import FactError
from cdfc.ingest.reader_lxml import _sheet_parts
from cdfc.ingest.xmlsafe import fromstring
from cdfc.predicates.harvest import M, cel_path, cel_segment, range_path, resolve_vocabulary

__all__ = ["filing_tree", "template_tree", "fact_set_for"]


def _insert(tree: dict, path: str, value: Any, cell: str) -> None:
    node = tree
    for seg in path.split("."):
        node = node.setdefault(seg, {})
    node["v"] = value
    node["__cell__"] = cell


def _coerce(raw: Any) -> Any:
    """A cell's stored text to a fact-model value. **Decimal, never float.**

    The first version converted through the binary floating-point type to decide whether a
    `ci/no-float-money.sh` caught it — correctly. A float in the facts package is a
    reproducibility bug wearing a value's clothes: two runs can disagree in the last places and
    the tolerance wide enough to absorb that is wide enough to absorb a real defect.

    A NON-INTEGRAL quantity is returned as TEXT rather than rounded. The fact model's numeric type
    is an int64 count of 10^-3 USD Million, and this builder does not know a cell's unit — so
    scaling here would be a units decision taken by whoever wrote the coercion. Left as text, the
    value is type-mismatched at pre-flight and the item is `NOT_RUN(source_unreadable)`, which
    says what happened.

    **`None` RAISES, and the canary loop is what found out why.** This function begins
    `text = str(raw)`, so `_coerce(None)` returned the four-character string `"None"` — and
    `p6_kill._patch` fed it exactly that, because `recalculate` returns `None` for a formula cell
    whose input has been blanked. Every such cell entered the mutant's fact tree as `"None"`, and
    an equality predicate over it returned `false`, and the campaign recorded a KILL. Measured on
    mutant `edfc99e6`: `P-0012`'s kill is `'' == 'None'`. The predicate compared two coercion
    artifacts.

    This module's own rule already said what the answer is — *"A blank NUMERIC cell is ABSENT, not
    zero … there is no integer that means empty"* — and there is no string that means it either.
    So the defect is made unrepresentable rather than discouraged: callers with a possibly-empty
    value route through `facts/patch.py::value_for`, which returns `ABSENT`, and `filing_tree`
    never inserts the key at all.
    """
    if raw is None:
        raise FactError(
            "_coerce(None) would return the string 'None', which compares unequal to every "
            "number and every other string — so an equality predicate over it returns false and "
            "the run records a FAIL that is an artifact of this coercion. A cell with no value is "
            "ABSENT: use facts/patch.py::value_for, which says so."
        )
    text = str(raw)
    try:
        d = Decimal(text)
    except (TypeError, ValueError, InvalidOperation):
        return text
    return int(d) if d == d.to_integral_value() else text


def filing_tree(blob: Path, *, ctx: Any = None) -> dict[str, Any]:
    """The `filing` side. Keys come from the pinned template's admission set, not from the filing.

    A cell the key induction never saw is not addressable, so a value written into it is not a
    fact of this model — and that is deliberate: a predicate cannot name it either.
    """
    from cdfc.predicates.harvest import _load_context

    ctx = ctx or _load_context(blob)
    filed = _cell_values(blob)
    tree: dict[str, Any] = {}
    for (sheet, ref) in ctx.key_of:
        values = filed.get(sheet, {})
        if ref not in values:
            continue                       # absent, and absence is a fact pre-flight can see
        _insert(tree, cel_path(sheet, ref), _coerce(values[ref]), f"{sheet}!{ref}")

    # The range nodes the data-validation classes emit against.
    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if not dv.sqref.split():
                continue
            from cdfc.predicates.harvest import expand

            refs = [c for part in dv.sqref.split() for c in expand(part.replace("$", ""))]
            cells = [
                {"v": _coerce(filed.get(sheet, {})[r]), "__cell__": f"{sheet}!{r}"}
                for r in refs
                if r in filed.get(sheet, {}) and (sheet, r) in ctx.key_of
            ]
            node = tree
            for seg in range_path(sheet, dv.sqref).split("."):
                node = node.setdefault(seg, {})
            node["cells"] = cells
    return tree


def template_tree(blob: Path, *, ctx: Any = None) -> dict[str, Any]:
    """The `template` side: the vocabularies, resolved from the PINNED BLANK."""
    from cdfc.predicates.harvest import _load_context

    ctx = ctx or _load_context(blob)
    vocab: dict[str, list[str]] = {}
    for sheet, records in ctx.validations_by_sheet.items():
        for dv in records:
            if dv.type != "list" or not dv.sqref.split():
                continue
            members, _how = resolve_vocabulary(ctx, sheet, dv.formula1)
            if not members:
                continue
            first = dv.sqref.split()[0].split(":")[0].replace("$", "")
            vocab[f"{cel_segment(sheet)}_{cel_segment(first)}"] = list(members)
    return {"vocab": vocab}


def _cell_values(blob: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(blob) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            shared = [
                "".join(t.text or "" for t in si.iter(f"{{{M}}}t")) for si in ss.iter(f"{{{M}}}si")
            ]
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            values: dict[str, Any] = {}
            for c in root.iter(f"{{{M}}}c"):
                ref = c.get("r") or ""
                node = c.find(f"{{{M}}}v")
                raw = node.text if node is not None else None
                if raw is None:
                    inline = c.find(f"{{{M}}}is")
                    raw = (
                        "".join(x.text or "" for x in inline.iter(f"{{{M}}}t"))
                        if inline is not None
                        else None
                    )
                if raw is None:
                    continue
                if c.get("t") == "s":
                    try:
                        raw = shared[int(raw)]
                    except (ValueError, IndexError):
                        raw = ""
                values[ref] = raw
            out[name] = values
    return out


def fact_set_for(filing: Path, template: Path) -> Any:
    """`FactSet(filing, template)` — the filing's values against the pinned blank's vocabularies."""
    from cdfc.facts.view import FactSet
    from cdfc.predicates.harvest import _load_context

    tctx = _load_context(template)
    return FactSet(filing_tree(filing, ctx=tctx), template_tree(template, ctx=tctx))


def cell_of(tree: Mapping[str, Any], key: str) -> str | None:
    node: Any = tree
    for seg in key.split(".")[1:]:
        if not isinstance(node, Mapping):
            return None
        node = node.get(seg)
    return node.get("__cell__") if isinstance(node, Mapping) else None
