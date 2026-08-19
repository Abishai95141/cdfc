"""P4-B4 — the harvest: relations the regulator's own blank encodes, turned into envelopes.

**Two rules it obeys and one it must not break.**

1. **Vocabularies resolve from the PINNED BLANK, never from a filed artifact.** The `Dropdown`
   sheet is hidden *and* the only unprotected sheet on FME; a filer who edits a vocabulary and then
   satisfies a membership check against their own edited vocabulary is NC-D01c, and it is invisible
   to every gate downstream.
2. **Every formula the class set cannot express becomes a typed `SkipRecord`**, with the sheet, the
   cell and the detail. Never a silent omission: an undeclared suppression is a coverage lie.
3. **This step cannot fail, only under-produce.** A harvest that raises has hidden something; a
   harvest that skips has declared it.

**Emission is a pure function of `(template_sha256, sheet index, cell ref)`.** Ids are assigned in
that order, so two harvests of one template produce byte-identical files. A harvest keyed on set
iteration order produces a different registry root every run.

**The fact-tree convention this harvest emits against**, stated once because every class depends on
it and P5's binding must reproduce it:

    a single cell   ->  { "v": <value>, "__cell__": "Sheet!REF" }
    a range         ->  { "cells": [ { "v": ..., "__cell__": ... }, ... ] }
    a vocabulary    ->  template.vocab.<slug>  =  [<string>, ...]

So `filing.<path>.v` is the value, `filing.<path>.__cell__` is the anchor a reader opens, and both
are DECLARED in `schema_keys`. An anchor that pre-flight does not guard produces a finding naming
no cell — a finding a filer cannot act on.
"""

from __future__ import annotations

import re
import zipfile
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from cdfc.schema.anchor import Anchor
from cdfc.ingest.reader_lxml import FormulaRecord, RawWorkbook, ValidationRecord, _sheet_parts, read
from cdfc.ingest.xmlsafe import fromstring
from cdfc.predicates.ast_walker import TemplateSchema
from cdfc.predicates.envelope import Candidate
from cdfc.schema.stable_keys import build_keys, col_to_index, split_ref

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

SkipKind = Literal[
    "iferror_wrapper",
    "if_conditional_carry",
    "other_formula",
    "list_unresolved",
    "dv_no_type",
    "function_outside_vocabulary",
    "key_unresolved",
]


@dataclass(frozen=True, slots=True)
class SkipRecord:
    """THE WEAK PILE, typed and counted. Every field required; no anonymous skips."""

    kind: SkipKind
    sheet: str
    ref: str
    detail: str

    def __post_init__(self) -> None:
        if not (self.kind and self.sheet and self.ref and self.detail):
            raise ValueError(
                "a skip with any field missing is an undeclared suppression, which is a coverage "
                f"lie: {self!r}"
            )


@dataclass(frozen=True, slots=True)
class HarvestResult:
    template_sha256: str
    workbook: str
    candidates: tuple[Candidate, ...]
    by_class: Mapping[str, int]
    skipped: tuple[SkipRecord, ...]
    cells_reachable: frozenset[str]
    schema: TemplateSchema = field(repr=False, default=None)  # type: ignore[assignment]
    # `obligation_id -> (construct_kind, construct_parts, sheet, ref)`. P7-B1 renders these into
    # TEMPLATE obligations and locates each in `template_instrument.emit()`. It is a property of
    # the OBLIGATION and deliberately not of the `Candidate`, so no envelope digest moves.
    constructs: Mapping[str, tuple[str, tuple[str, ...], str, str]] = field(
        repr=False, default_factory=dict
    )
    # `predicate_id -> harvest class`. B0 is defined as the template's own formula-derived
    # identities, so the baseline needs to know which predicates those are without re-running the
    # emission and risking a different order.
    class_of: Mapping[str, str] = field(repr=False, default_factory=dict)

    @property
    def skips_by_kind(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for s in self.skipped:
            out[s.kind] = out.get(s.kind, 0) + 1
        return dict(sorted(out.items()))


# --- the CEL path grammar -------------------------------------------------------------

_NON_SEGMENT = re.compile(r"[^A-Za-z0-9_]+")


def cel_segment(text: str) -> str:
    """One lawful CEL identifier from arbitrary sheet or label text.

    A segment may not start with a digit, and three of the nine workbooks have sheets named
    `1. …`, `2. …`, `3. …`. Prefixing rather than dropping keeps `3. Portfolio` and `Portfolio`
    distinguishable — two sheets collapsing to one segment would merge two cells' keys and the
    settled fraction would count one of them twice.
    """
    slug = _NON_SEGMENT.sub("_", text.strip()).strip("_").lower() or "unnamed"
    return f"n_{slug}" if slug[0].isdigit() else slug


def cel_path(sheet: str, ref: str) -> str:
    """`filing`-relative path for one cell. Deterministic in `(sheet, ref)` and nothing else."""
    col, row = split_ref(ref)
    return f"{cel_segment(sheet)}.r{row}.c{col.lower()}"


def range_path(sheet: str, sqref: str) -> str:
    first = sqref.split()[0].split(":")[0].replace("$", "")
    col, row = split_ref(first)
    return f"{cel_segment(sheet)}.dv_{col.lower()}{row}"


# --- reading the pinned blank ------------------------------------------------------------

_CELL = re.compile(r"^\$?([A-Z]{1,3})\$?(\d+)$")
_RANGE_REF = re.compile(
    r"^(?:'([^']+)'|([A-Za-z0-9_. ]+))!(\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)$"
)
PURE_CARRY = re.compile(r"^'?[^!'\[\]]+'?!\$?[A-Z]{1,3}\$?\d+$")


def single_call(body: str, name: str) -> str | None:
    r"""The argument text iff `body` is EXACTLY `NAME(...)` — one call, nothing around it.

    A greedy `^NAME\((.+)\)$` also matches `COUNTIF(a,"x") + COUNTIF(b,"y")`, and the harvest
    then emitted an expression built from an argument list that was really two calls and a `+`.
    Two of those were unparseable CEL; a third that happened to parse would have been a
    well-formed predicate stating a relation the template does not encode. Parentheses are
    counted rather than matched by a pattern.
    """
    if not body.upper().startswith(name.upper() + "("):
        return None
    depth = 0
    for i, ch in enumerate(body):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return body[len(name) + 1 : i] if i == len(body) - 1 else None
    return None
SUM_CALL = re.compile(r"^SUM\((.+)\)$", re.S)
COUNT_CALL = re.compile(r"^COUNTIFS?\((.+)\)$", re.S)
IFERROR_CALL = re.compile(r"^IFERROR\((.+)\)$", re.S)


def expand(rng: str) -> list[str]:
    rng = rng.replace("$", "")
    if ":" not in rng:
        return [rng] if _CELL.match(rng) else []
    a, b = rng.split(":", 1)
    ma, mb = _CELL.match(a), _CELL.match(b)
    if not (ma and mb):
        return []
    c1, r1 = col_to_index(ma.group(1)), int(ma.group(2))
    c2, r2 = col_to_index(mb.group(1)), int(mb.group(2))
    out = []
    for r in range(min(r1, r2), max(r1, r2) + 1):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            letters = ""
            n = c
            while n:
                n, rem = divmod(n - 1, 26)
                letters = chr(65 + rem) + letters
            out.append(f"{letters}{r}")
    return out


@dataclass
class HarvestContext:
    """Everything a harvest class may read. All of it from the PINNED BLANK."""

    blob: Path
    wb: RawWorkbook
    template_sha256: str
    sheet_index: dict[str, int]
    cell_text: dict[str, dict[str, str]]
    cell_values: dict[str, dict[str, Any]]
    formulas_by_sheet: dict[str, list[FormulaRecord]]
    validations_by_sheet: dict[str, list[ValidationRecord]]
    defined_names: dict[str, str]
    key_of: dict[tuple[str, str], str]
    vocabularies: dict[str, list[str]]
    skips: list[SkipRecord] = field(default_factory=list)

    def skip(self, kind: SkipKind, sheet: str, ref: str, detail: str) -> None:
        self.skips.append(SkipRecord(kind=kind, sheet=sheet, ref=ref, detail=detail))

    def sheet_exists(self, name: str) -> bool:
        return name in self.sheet_index


def _load_context(blob: Path) -> HarvestContext:
    wb = read(blob)
    import hashlib

    digest = hashlib.sha256(blob.read_bytes()).hexdigest()
    text: dict[str, dict[str, str]] = {}
    values: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(blob) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss = fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(f"{{{M}}}t")) for si in ss.iter(f"{{{M}}}si")]
        for name, _state, part in _sheet_parts(z):
            if part not in z.namelist():
                continue
            root = fromstring(z.read(part))
            t: dict[str, str] = {}
            v: dict[str, Any] = {}
            for c in root.iter(f"{{{M}}}c"):
                ref = c.get("r") or ""
                node = c.find(f"{{{M}}}v")
                raw = node.text if node is not None else None
                if raw is None:
                    inline = c.find(f"{{{M}}}is")
                    raw = "".join(x.text or "" for x in inline.iter(f"{{{M}}}t")) if inline is not None else None
                if raw is None:
                    continue
                if c.get("t") == "s":
                    try:
                        raw = shared[int(raw)]
                    except (ValueError, IndexError):
                        raw = ""
                v[ref] = raw
                if c.get("t") in ("s", "str", "inlineStr") or not _is_number(raw):
                    t[ref] = str(raw)
            text[name] = t
            values[name] = v

    sheet_index = {s.name: i for i, s in enumerate(wb.sheets)}
    formulas: dict[str, list[FormulaRecord]] = {}
    for f in wb.formulas:
        formulas.setdefault(f.sheet, []).append(f)
    validations: dict[str, list[ValidationRecord]] = {}
    for d in wb.validations:
        validations.setdefault(d.sheet, []).append(d)

    # THE ADMISSION SET, and it is not the stable key.
    #
    # `build_keys` returns `{stable_key: Field}`, and the stable key is NOT INJECTIVE — that is
    # what `collision_census` measures. Two cells collapsing to one key would make two predicates
    # read one fact, so the CEL path is derived per cell from `(sheet, ref)` instead, which is
    # injective by construction and exact because the predicate is bound to a pinned template
    # digest.
    #
    # What the induction is still used for is ADMISSION: a cell the key induction never saw is a
    # cell no predicate may name, and it becomes a typed `key_unresolved` skip rather than a
    # silent omission.
    key_of: dict[tuple[str, str], str] = {}
    for s in wb.sheets:
        unlocked = {r for sh, r in wb.unlocked_cells if sh == s.name}
        formula_refs = {f.ref for f in formulas.get(s.name, ())}
        induced = set(text.get(s.name, {})) | unlocked | formula_refs
        fields = build_keys(
            sheet=s.name,
            cell_text=text.get(s.name, {}),
            unlocked=unlocked,
            formula_refs=formula_refs,
            merged_ranges=wb.merged_ranges,
        )
        by_ref = {f.resolved_ref: f.stable_key for f in fields.values() if f.resolved_ref}
        for ref in induced:
            key_of[(s.name, ref)] = by_ref.get(ref, Anchor.cell(s.name, ref).render())

    return HarvestContext(
        blob=blob,
        wb=wb,
        template_sha256=digest,
        sheet_index=sheet_index,
        cell_text=text,
        cell_values=values,
        formulas_by_sheet=formulas,
        validations_by_sheet=validations,
        defined_names={d.name: d.value for d in wb.defined_names},
        key_of=key_of,
        vocabularies={},
    )


def _is_number(s: Any) -> bool:
    try:
        float(str(s))
        return True
    except (TypeError, ValueError):
        return False


def resolve_vocabulary(ctx: HarvestContext, sheet: str, formula1: str | None) -> tuple[list[str] | None, str]:
    """A vocabulary from the PINNED BLANK. Never from a filing — NC-D01c."""
    f1 = (formula1 or "").strip()
    if not f1:
        return None, "empty formula1"
    if f1.startswith('"') and f1.endswith('"'):
        return [v.strip() for v in f1[1:-1].split(",") if v.strip()], "literal"
    target = ctx.defined_names.get(f1, f1)
    m = _RANGE_REF.match(target.strip())
    if m:
        src_sheet, rng = (m.group(1) or m.group(2)), m.group(3)
    elif _CELL.match(target.strip().split(":")[0].replace("$", "")):
        src_sheet, rng = sheet, target.strip()
    else:
        return None, f"unresolved reference {target[:48]!r}"
    vals = ctx.cell_values.get(src_sheet)
    if vals is None:
        return None, f"sheet {src_sheet!r} is not in this workbook"
    vocab = [str(vals[c]).strip() for c in expand(rng) if c in vals and str(vals[c]).strip()]
    return (vocab or None), ("defined name" if f1 in ctx.defined_names else "range")


# --- the harvest ------------------------------------------------------------------------


def _classes() -> list[Any]:
    from cdfc.predicates.harvest_classes import ALL_CLASSES

    return list(ALL_CLASSES)


def harvest(blob: Path) -> HarvestResult:
    """Derive every relation the class set can express. Cannot fail; only under-produce."""
    ctx = _load_context(blob)
    emitted: list[tuple[tuple[int, int, int, str], Any]] = []
    for cls in _classes():
        for order, draft in cls.emit(ctx):
            emitted.append((order, draft))
    emitted.sort(key=lambda t: t[0])

    candidates: list[Candidate] = []
    by_class: dict[str, int] = {}
    reachable: set[str] = set()
    key_to_cells: dict[str, set[str]] = {}
    constructs: dict[str, tuple[str, tuple[str, ...], str, str]] = {}
    class_of: dict[str, str] = {}
    for seq, (_order, draft) in enumerate(emitted, start=1):
        c = draft.build(f"P-{seq:04d}", ctx.template_sha256)
        candidates.append(c)
        # TWO CLASSES MAY DERIVE FROM ONE CONSTRUCT — a `custom` validation feeds both
        # `conditional_required` and a bound — so the obligation is shared and the construct
        # recorded for it must be the same text. A collision that DISAGREES is a defect in the
        # harvest, not a fact about the template, and it raises rather than being overwritten by
        # whichever class ran last.
        entry = (draft.construct_kind, draft.construct_parts, *draft.construct_at)
        prior = constructs.get(draft.obligation_id)
        if prior is not None and prior != entry:
            raise ValueError(
                f"{draft.obligation_id}: two harvest classes recorded different constructs for "
                f"one obligation: {prior!r} then {entry!r}. One of them is reading the wrong "
                "artifact, and the obligation's quote would be whichever ran last."
            )
        constructs[draft.obligation_id] = entry
        class_of[c.id] = draft.harvest_class
        by_class[draft.harvest_class] = by_class.get(draft.harvest_class, 0) + 1
        for key, cells in draft.key_cells.items():
            key_to_cells.setdefault(key, set()).update(cells)
            if key.startswith("filing."):
                reachable.update(cells)

    _sweep_unaccounted_formulas(ctx, constructs)

    schema = TemplateSchema(
        {k: frozenset(v) for k, v in key_to_cells.items()}, ctx.template_sha256
    )
    return HarvestResult(
        template_sha256=ctx.template_sha256,
        workbook=blob.name,
        candidates=tuple(candidates),
        by_class=dict(sorted(by_class.items())),
        skipped=tuple(ctx.skips),
        cells_reachable=frozenset(reachable),
        schema=schema,
        constructs=dict(sorted(constructs.items())),
        class_of=dict(sorted(class_of.items())),
    )


def _skip_kind_for(body: str) -> SkipKind:
    """The typed reason a formula body produced no obligation, from the body itself.

    `iferror_wrapper` and `if_conditional_carry` were declared in `SkipKind` from the day it was
    written and appeared NOWHERE else in the repository. They name exactly FME's silent pile —
    130 `IFERROR` and 14 `IF` — which is how a reader can tell the vocabulary was written for this
    sweep and the sweep was never connected.
    """
    b = body.strip().upper()
    if b.startswith("IFERROR("):
        return "iferror_wrapper"
    if b.startswith("IF("):
        return "if_conditional_carry"
    called = {tok for kind, tok in _tokenise_names(body) if kind == "func"}
    if called - {"SUM", "COUNTIF", "COUNTIFS"}:
        return "function_outside_vocabulary"
    return "other_formula"


def _tokenise_names(body: str) -> list[tuple[str, str]]:
    """`(kind, token)` for the function names in a body, via the EVALUATOR's own tokeniser.

    Not a pattern over the formula text: a census by regex reports whatever its author already
    believed the vocabulary was, and this is the module that exists to stop that.
    """
    from cdfc.calc.evaluate import tokenize

    try:
        return [(k, t.upper().removeprefix("_XLFN.")) for k, t in tokenize(body) if k == "func"]
    except Exception:  # noqa: BLE001 — an unparseable body is not a vocabulary claim
        return []


def _sweep_unaccounted_formulas(
    ctx: HarvestContext, constructs: Mapping[str, tuple[str, tuple[str, ...], str, str]]
) -> None:
    """**THE COMPLETENESS SWEEP: every formula is an obligation or a typed skip. Never neither.**

    This module's own contract, rule 2, says *"every formula the class set cannot express becomes a
    typed `SkipRecord`… never a silent omission: an undeclared suppression is a coverage lie."*
    It was false for **1,060 of the corpus's 1,495 formula cells**, because every class begins with
    a bare `continue` on a body it cannot match and nothing recorded the fall-through. FME
    published 59 skips against 144 silent drops; ALR published **2** against 620.

    That is the product's own failure mode in the module that defines it. The skip table is the
    ONLY place a reader could learn those cells exist — they are formula cells, so they are
    excluded from the field surface by construction, appear in no `noPredicate` count, and reach no
    run-time coverage declaration.

    The sweep is HERE, once, rather than in each of the nine classes, because completeness is a
    property of the class set as a whole: a class cannot know whether another class expressed the
    body it just declined, and nine chances to remember is nine chances to forget.
    """
    from cdfc.predicates.harvest_classes._shared import iter_formulas

    accounted = {(sheet, ref) for _k, _p, sheet, ref in constructs.values()}
    accounted |= {(s.sheet, s.ref) for s in ctx.skips}
    for sheet, ref, body in iter_formulas(ctx):
        if (sheet, ref) in accounted:
            continue
        accounted.add((sheet, ref))
        ctx.skip(
            _skip_kind_for(body),
            sheet,
            ref,
            f"no harvest class expressed this body: {body[:80]}",
        )


def emit_envelopes(res: HarvestResult, out_dir: Path) -> list[Path]:
    """Write one YAML per candidate, under `<out_dir>/<template8>/`. Byte-identical per run."""
    from cdfc.predicates.loader import dump

    target = out_dir / res.template_sha256[:8]
    target.mkdir(parents=True, exist_ok=True)
    for stale in sorted(target.glob("P-*.yaml")):
        stale.unlink()
    written: list[Path] = []
    for c in res.candidates:
        path = target / f"{c.id}__{c.kind}.yaml"
        path.write_text(_render_yaml(dump(c)), encoding="utf-8")
        written.append(path)
    return written


def _render_yaml(obj: Mapping[str, Any]) -> str:
    """A deliberately small, deterministic emitter.

    `yaml.safe_dump` is fine, but it sorts keys with Python's collation and quotes according to
    heuristics that have changed between releases — and these files are content-addressed by the
    envelope digest of what they parse to, so a serialiser whose output moves with a library
    upgrade produces a diff nobody asked for.
    """
    import json

    lines = [
        "# GENERATED by `cdfc harvest`. Do not hand-edit: the envelope digest is computed over",
        "# what this parses to, and an edit here produces a different predicate with a different",
        "# identity and no qualification record.",
    ]

    def render(value: Any, indent: int) -> list[str]:
        pad = " " * indent
        if isinstance(value, dict):
            out = []
            for k in sorted(value):
                v = value[k]
                if isinstance(v, (dict, list)) and v:
                    out.append(f"{pad}{k}:")
                    out.extend(render(v, indent + 2))
                elif isinstance(v, (dict, list)):
                    out.append(f"{pad}{k}: " + ("{}" if isinstance(v, dict) else "[]"))
                else:
                    out.append(f"{pad}{k}: {json.dumps(v)}")
            return out
        if isinstance(value, list):
            out = []
            for item in value:
                if isinstance(item, dict):
                    body = render(item, indent + 2)
                    out.append(f"{pad}- " + body[0].strip())
                    out.extend(body[1:])
                else:
                    out.append(f"{pad}- {json.dumps(item)}")
            return out
        return [f"{pad}{json.dumps(value)}"]

    lines.extend(render(dict(obj), 0))
    return "\n".join(lines) + "\n"


@dataclass(frozen=True, slots=True)
class DistributionRow:
    workbook: str
    sha8: str
    n: int
    by_class: Mapping[str, int]
    skips: int
    skips_by_kind: Mapping[str, int]
    cells_reachable: int


def distribution(results: Sequence[HarvestResult]) -> tuple[DistributionRow, ...]:
    """All rows, zeroes included. Publishing the total alone is banned — NC-Q73."""
    return tuple(
        DistributionRow(
            workbook=r.workbook,
            sha8=r.template_sha256[:8],
            n=len(r.candidates),
            by_class=r.by_class,
            skips=len(r.skipped),
            skips_by_kind=r.skips_by_kind,
            cells_reachable=len(r.cells_reachable),
        )
        for r in results
    )


def harvest_all(corpus: Path) -> list[HarvestResult]:
    return [harvest(p) for p in sorted(corpus.glob("*.xlsx"))]


def iter_drafts(ctx: HarvestContext) -> Iterator[Any]:  # pragma: no cover - convenience
    for cls in _classes():
        yield from cls.emit(ctx)
