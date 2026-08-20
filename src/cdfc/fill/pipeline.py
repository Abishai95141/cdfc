"""THE LINK: stored artefacts -> bound evidence -> adjudicated fills. Deterministic end to end.

## What this closes

`A5` adjudicates a binding and requires one as an INPUT; `A1c` use 2 produces one, matching a
source column to a template field on declared evidence with EM-derived weights; the registry stores
the uploads. All three existed and **nothing joined them**, so the product's own sentence —
*ingest, resolve, map, populate* — was demonstrated by no path.

This is that path, and it is deliberately thin. It introduces no new judgement: every decision it
makes is made by a component that was already measured, and its own job is to carry values between
them without losing what they said.

    registry digest  ->  addressable text (two parsers, disputed rows excluded)
                     ->  source columns
                     ->  A1c match: column -> field, or a refusal
                     ->  observations with SPANS into that text
                     ->  A5: six conditions, two lanes, a declaration that must close

## THE SPAN IS THE POINT, AND IT IS WHY THIS IS NOT A LOOKUP

A binder could hand `A5` a value and a field. It would pass `GROUNDED`, and `REVERIFIES` would be
unfalsifiable — an observation whose span is invented re-reads whatever the binder wrote there.

So the observation's span is located **in the source text**, and a value that cannot be found in
the document it claims to come from produces no observation at all. `W0-C` is the measurement that
makes this non-negotiable: a similarity locator returned `SUPPORTED` **20 of 20** on evidence that
had been deleted.

## What it does NOT do

It does not write a workbook — `ci/no-openpyxl-writer.sh`, and fills are data. It does not decide
which artefacts to use: a caller names digests, exactly as a run names its inputs.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from cdfc.correspond.schema import SchemaMatch, columns_from_rows, match
from cdfc.evidence.fields import FieldSet, from_template
from cdfc.evidence.observe import Observation
from cdfc.fill.propose import FillDeclaration, propose
from cdfc.ingest.tabular import header_and_rows, read_delimited
from cdfc.qualify.textsource import InstrumentText
from cdfc.registry import ArtefactKind, Registry


@dataclass(frozen=True, slots=True)
class FillRun:
    """One end-to-end fill: what it used, what it matched, what it proposed."""

    template_digest: str
    source_digest: str
    merkle_root: str
    schema_match: SchemaMatch
    declaration: FillDeclaration
    unlocatable: tuple[tuple[str, str], ...]     # (field ref, the value that was not in the source)

    def lines(self) -> tuple[str, ...]:
        return (
            f"template   {self.template_digest[:16]}…",
            f"source     {self.source_digest[:16]}…",
            f"inputs     merkle {self.merkle_root[:16]}…",
            "",
            *self.schema_match.lines(),
            "",
            *self.declaration.lines(),
            "",
            f"values a column offered that are NOT IN the source text  {len(self.unlocatable)}",
        )


def _locate(source: InstrumentText, value: str) -> Observation | None:
    """An observation for `value`, at a span in `source` — or None if it is not there.

    `find_all` returns disputed occurrences too, and one is REFUSED here rather than returned: a
    span inside a region the two parsers disagree on is exactly the row whose field boundaries were
    a guess. `A5`'s `REVERIFIES` would pass on it, because the sentinel is what it would re-read.
    """
    v = str(value).strip()
    if not v:
        return None
    for lo, hi in source.find_all(v):
        if source.is_disputed((lo, hi)):
            continue
        unit = source.unit_at((lo, hi))
        return Observation(
            value=v, document=source.instrument_id, span=(lo, hi),
            page=unit.page if unit is not None else None,
            context=source.text[max(0, lo - 40):hi + 40],
        )
    return None


def run(
    registry: Registry,
    *,
    template_digest: str,
    source_digest: str,
    template_path: Path | None = None,
    delimiter: str = ",",
) -> FillRun:
    """Bind a stored source export to a stored template and adjudicate the fills.

    `template_path` exists because the field-surface reader wants a workbook on disk and the
    registry stores bytes; the digest is still the identity and is what the run records.
    """
    inputs = registry.inputs([template_digest, source_digest])

    meta = registry.meta(source_digest)
    if meta.kind is not ArtefactKind.SOURCE:
        raise ValueError(
            f"artefact {source_digest[:12]}… is declared {meta.kind.value!r}, not 'source'. Kind "
            "is declared by the uploader and this pipeline reads a SOURCE; binding a filing or a "
            "rules corpus as evidence would be a different operation wearing this one's name."
        )

    raw = registry.get(source_digest)
    source = read_delimited(raw, instrument_id=f"source:{source_digest[:12]}",
                            delimiter=delimiter)

    blank = template_path or Path(registry.meta(template_digest).filename)
    fields: FieldSet = from_template(blank)

    header, rows = header_and_rows(raw, delimiter=delimiter)
    columns = columns_from_rows(header, rows)
    m = match(columns, fields)

    # A1c gives column -> field. Turn each matched column's VALUES into observations LOCATED in
    # the source text; a value that is not there yields nothing, and is counted.
    by_name = {c.name: c for c in columns}
    binding: dict[str, list[Observation]] = {}
    unlocatable: list[tuple[str, str]] = []
    for col_name, field_ref, _w in m.pairs:
        col = by_name.get(col_name)
        if col is None:
            continue
        for v in col.values:
            o = _locate(source, v)
            if o is None:
                if str(v).strip():
                    unlocatable.append((field_ref, str(v)[:40]))
                continue
            binding.setdefault(field_ref, []).append(o)

    decl = propose(
        fields, {k: tuple(v) for k, v in binding.items()}, source,
        binding_provenance=(
            f"cdfc.correspond.schema.match over {len(columns)} source column(s) from artefact "
            f"{source_digest[:12]}…, EM-weighted"
        ),
    )
    return FillRun(
        template_digest=template_digest, source_digest=source_digest,
        merkle_root=inputs.merkle_root, schema_match=m, declaration=decl,
        unlocatable=tuple(sorted(set(unlocatable))),
    )
