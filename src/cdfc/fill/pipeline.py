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

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from cdfc.correspond.schema import SchemaMatch, columns_from_rows, match
from cdfc.evidence.fields import FieldSet, from_template
from cdfc.evidence.observe import Observation
from cdfc.fill.propose import FillDeclaration, propose
from cdfc.ingest.tabular import header_and_rows, read_delimited
from cdfc.qualify.instruments import deserialise
from cdfc.qualify.textsource import InstrumentText
from cdfc.registry import ArtefactKind, Registry


@dataclass(frozen=True, slots=True)
class FillRun:
    """One end-to-end fill: what it used, what it matched, what it proposed."""

    template_digest: str
    source_digest: str            # the FIRST source; `source_digests` carries them all
    merkle_root: str
    schema_match: SchemaMatch
    declaration: FillDeclaration
    unlocatable: tuple[tuple[str, str], ...]     # (field ref, the value that was not in the source)
    source_digests: tuple[str, ...] = ()

    def lines(self) -> tuple[str, ...]:
        return (
            f"template   {self.template_digest[:16]}…",
            f"sources    {len(self.source_digests) or 1}  "
            f"{[d[:12] + '…' for d in (self.source_digests or (self.source_digest,))]}",
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
    source_digest: str | Sequence[str],
    template_path: Path | None = None,
    delimiter: str = ",",
    subject: Mapping[str, str] | None = None,
    claims: Sequence[Mapping[str, str]] | None = None,
) -> FillRun:
    """Bind a stored source export to a stored template and adjudicate the fills.

    `template_path` exists because the field-surface reader wants a workbook on disk and the
    registry stores bytes; the digest is still the identity and is what the run records.
    """
    # ONE OR MANY SOURCES. A filing is assembled from a custodian feed AND a trial balance AND a
    # cap table; binding one at a time and taking the last would silently drop the others.
    digests = [source_digest] if isinstance(source_digest, str) else list(source_digest)
    if not digests:
        raise ValueError("a fill run names no source; there would be nothing to bind evidence from.")
    inputs = registry.inputs([template_digest, *digests])

    for d in digests:
        meta = registry.meta(d)
        if meta.kind is not ArtefactKind.SOURCE:
            raise ValueError(
                f"artefact {d[:12]}… is declared {meta.kind.value!r}, not 'source'. Kind is "
                "declared by the uploader and this pipeline reads a SOURCE; binding a filing or a "
                "rules corpus as evidence would be a different operation wearing this one's name."
            )

    raws = {d: registry.get(d) for d in digests}

    # C4 — A SOURCE IS NOT ALWAYS A TABLE.
    #
    # A custodian feed is delimited bytes with a header row. A PDF valuation pack is neither: it
    # was read at BUILD time into a pinned `InstrumentText` (B3) and what the registry stores is
    # that text. Both must reach the fill, because *"custodian feeds, trial balance sheets, cap
    # tables, and PDF valuation packs"* is one sentence and one pipeline.
    #
    # The discrimination is on the BYTES THEMSELVES, not on a filename or a declared kind: a
    # pinned instrument deserialises and a CSV does not. Guessing from an extension would let a
    # mislabelled upload be read the wrong way silently.
    sources: dict[str, InstrumentText] = {}
    prose: set[str] = set()
    for d in digests:
        try:
            it, _kind, _name, _sha = deserialise(raws[d])
        except Exception:                                      # noqa: BLE001
            sources[d] = read_delimited(raws[d], instrument_id=f"source:{d[:12]}",
                                        delimiter=delimiter)
        else:
            # A PINNED source. Its spans are already computed and corroborated by two parsers,
            # and its DISPUTED regions already refuse — `_locate` skips them exactly as it does
            # for a delimited source.
            sources[d] = it
            prose.add(d)
    # The FIRST source is the one A5 adjudicates spans against. Every observation records the
    # document it came from, so a caller can tell them apart; what must not happen is a span from
    # one document being re-verified against another, which would pass on a coincidence.
    source = sources[digests[0]]

    blank = template_path or Path(registry.meta(template_digest).filename)
    fields: FieldSet = from_template(blank)

    # A RETURN IS FILED BY ONE ENTITY, ABOUT THAT ENTITY.
    #
    # A custodian register holds every FME the administrator serves. Binding all of them to one
    # return offers four different PANs for one cell, and `A5`'s UNIQUE condition correctly refuses
    # every one as contradicted — the fill count went to ZERO the moment the demo registers were
    # given a realistic population. That is not a bug in the resolver or in A5; it is a missing
    # question. `subject` answers it: the rows this filing is about.
    #
    # When the sources describe more than one subject and nobody said which, the run REFUSES
    # rather than picking. Filing one entity's figures under another's name is the worst thing
    # this system could do, and a silent choice is how it would happen.
    columns = []
    subjects_seen: set[tuple[str, ...]] = set()
    for d in digests:
        if d in prose:
            # A prose source has no header row, so it offers no columns and A1c has nothing to
            # match. Its values arrive through `claims` instead. Skipping it here is not dropping
            # it: it is still in `sources`, and every claim is located against it.
            continue
        header, rows = header_and_rows(raws[d], delimiter=delimiter)
        if subject:
            keys = [k for k in subject if k in header]
            if keys:
                idx = {k: header.index(k) for k in keys}
                rows = [r for r in rows
                        if all(str(r[idx[k]]).strip() == subject[k] for k in keys
                               if idx[k] < len(r))]
        for k in ("PAN of FME", "PAN"):
            if k in header:
                col = header.index(k)
                subjects_seen.add(tuple(sorted({str(r[col]).strip() for r in rows
                                                if col < len(r) and str(r[col]).strip()})))
        columns.extend(columns_from_rows(header, rows))

    distinct = {v for group in subjects_seen for v in group}
    if subject is None and len(distinct) > 1:
        raise ValueError(
            f"the sources describe {len(distinct)} subjects (e.g. {sorted(distinct)[:3]}) and the "
            "run does not name one. A return is filed BY one entity ABOUT that entity; binding a "
            "whole register to it offers several values for every cell, and choosing silently "
            "would file one entity's figures under another's name."
        )
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
            # Locate in WHICHEVER source actually contains it, and record which one. A value found
            # in the trial balance must not be recorded as coming from the custodian feed.
            o = next((x for x in (_locate(src, v) for src in sources.values()) if x is not None),
                     None)
            if o is None:
                if str(v).strip():
                    unlocatable.append((field_ref, str(v)[:40]))
                continue
            binding.setdefault(field_ref, []).append(o)

    # CLAIMS — the prose half of the binder. Rows of `{document, field, value}` that a model read
    # out of a source at TOOL time.
    #
    # `cdfc.fill` is a VERDICT ROOT, so it cannot import `cdfc.model` and does not: the model's
    # output arrives as DATA, exactly as `evidence.run` takes its proposals as a file. What
    # happens here is deterministic and is the only part that may decide anything — the value is
    # LOCATED in the document the claim names, and a value that is not there yields no observation
    # at all. A claim is a hint about where to look, never evidence that something is there.
    by_instrument = {s.instrument_id: s for s in sources.values()}
    for c in claims or ():
        ref, value, doc = str(c.get("field", "")), str(c.get("value", "")), str(c.get("document", ""))
        if not ref or not value:
            continue
        # A CLAIM NAMES A DOCUMENT, NOT A DIGEST. `sources` is keyed by artefact digest because
        # that is the run's identity; a claim says `source-fincen-boir-instructions`, which is the
        # instrument's own id. Resolve BOTH, and refuse a name that matches neither rather than
        # falling back to "the only source" — a claim located against the wrong document would
        # pass REVERIFIES on a coincidence, which is the exact defect A5 was corrected for.
        src = sources.get(doc) or by_instrument.get(doc)
        if src is None:
            unlocatable.append((ref, f"{value[:30]} (names document {doc!r}; run has "
                                     f"{sorted(by_instrument)[:3]})"))
            continue
        o = _locate(src, value)
        if o is None:
            unlocatable.append((ref, str(value)[:40]))
            continue
        binding.setdefault(ref, []).append(o)

    decl = propose(
        fields, {k: tuple(v) for k, v in binding.items()},
        {src.instrument_id: src for src in sources.values()},
        binding_provenance=(
            f"cdfc.correspond.schema.match over {len(columns)} source column(s) from "
            f"{len(digests)} artefact(s), EM-weighted"
        ),
    )
    return FillRun(
        template_digest=template_digest, source_digest=digests[0],
        source_digests=tuple(digests),
        merkle_root=inputs.merkle_root, schema_match=m, declaration=decl,
        unlocatable=tuple(sorted(set(unlocatable))),
    )
