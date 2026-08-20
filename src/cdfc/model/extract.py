"""LAYER 2, second mode — CLAIM EXTRACTION from prose. The model proposes; it still decides nothing.

## Why this exists, and what it replaces

`cdfc.correspond.schema` binds a source COLUMN to a template field on declared evidence. That works
on a custodian CSV and does nothing at all on a **PDF valuation pack**, which has no columns — and
prose sources are the half of the ingest claim nothing could read.

`docs/decisions/D-A3-02` assessed Microsoft GraphRAG for this and rejected adopting the package
while naming the one stage worth having: **claims/covariates extraction, which carries text-unit
references**. This is that stage, with GraphRAG's shape and none of its dependencies.

Measured, on 20 Aug 2026, before choosing:

    graphrag install          132 packages, incl. the Azure SDK trio, blis, nltk, pyarrow
    graphrag init             an INTERACTIVE wizard; hung 10+ minutes in automation
    required embedding model  text-embedding-3-large — and DeepSeek serves NO embedding model,
                              so the package could not run on the key it was to run on

**And its headline output could never survive here anyway.** A community summary is a synthesis over
many text units; it has no span, and there is no span it could have, so `A5`'s `REVERIFIES` would
refuse every one. The part that does survive is the part with a text reference, which is this.

## THE MODEL MUST QUOTE, AND WE LOCATE THE QUOTE

The model returns a `value` and the `evidence` — the exact sentence it read the value out of. It
does NOT return a span: a model-supplied offset is a number nobody checked, and `W0-C` measured
what trusting one costs (a locator returning `SUPPORTED` **20 of 20** on DELETED evidence).

So the span is found by `str.find` in the source, here, deterministically. Every claim's evidence
sentence is searched for in the document it was extracted from, and **only a claim whose sentence
the search locates becomes an observation**; the rest are counted as `evidence_not_located`. That is
the whole safety property, and it does not depend on the model being careful.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Final

from cdfc.model.propose import DEFAULT_MODEL, ProposerError, _call
from cdfc.qualify.textsource import InstrumentText

MAX_CHARS: Final[int] = 12_000


@dataclass(frozen=True, slots=True)
class ClaimCandidate:
    """One value the model says the document reports, with the text it read it out of."""

    value: str
    label: str          # what the model says the value IS, in the document's own words
    evidence: str       # the sentence the value appears in; MUST occur verbatim in the source
    model: str
    index: int

    def as_canonical_obj(self) -> dict[str, object]:
        return {"value": self.value, "label": self.label, "evidence": self.evidence,
                "model": self.model, "index": self.index}


@dataclass(frozen=True, slots=True)
class ClaimSet:
    """What one extraction produced, with the denominators that make it readable."""

    claims: tuple[ClaimCandidate, ...]
    model: str
    document: str
    chars_offered: int
    raw_blocks: int
    malformed: tuple[str, ...] = ()

    def counts(self) -> dict[str, int]:
        return {"claims": len(self.claims), "raw_blocks": self.raw_blocks,
                "malformed": len(self.malformed), "chars_offered": self.chars_offered}


SYSTEM: Final[str] = (
    "You extract reported VALUES from a financial or regulatory document. You decide nothing: "
    "every claim you make is checked against the document text by code that does not consult "
    "you, and a claim whose evidence is not found is discarded.\n\n"
    "For each value the document REPORTS, return:\n"
    '  value    — the figure or term exactly as written, e.g. "7,50,000" or "Registered FME (Retail)"\n'
    "  label    — what that value is, in the document's own words\n"
    "  evidence — the COMPLETE sentence containing the value, copied VERBATIM\n\n"
    "Rules:\n"
    "1. `evidence` must be copied character for character from the text you were given. Do not "
    "fix spelling, do not normalise spacing, do not join across an ellipsis. It is searched for "
    "in the document and only a match survives.\n"
    "2. `value` must appear inside `evidence`.\n"
    "3. Extract only what the document REPORTS. A threshold a rule imposes is not a reported "
    "value.\n"
    "4. Do not supply an offset, a position or a confidence. Offsets are computed from the text.\n"
    "5. Extract nothing when the document reports nothing. An empty list is a valid answer.\n\n"
    'Reply with JSON only: {"claims":[{"value":…,"label":…,"evidence":…}]}'
)


def extract(
    source: InstrumentText,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    transport: Any = None,
) -> ClaimSet:
    """Ask the model what values `source` reports. Returns candidates; locates nothing yet."""
    text = source.text
    if not text.strip():
        raise ProposerError(
            f"{source.instrument_id}: the source is empty, so an empty claim set would not "
            "distinguish 'the document reports nothing' from 'the model was shown nothing'."
        )
    offered = text[:MAX_CHARS]
    data = _call(
        {"model": model, "max_tokens": 4096, "system": SYSTEM,
         "messages": [{"role": "user", "content": offered}]},
        base_url=base_url, api_key=api_key, transport=transport,
    )
    body = "".join(
        b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()
    return parse(body, model=model, document=source.instrument_id, chars_offered=len(offered))


def parse(text: str, *, model: str, document: str, chars_offered: int) -> ClaimSet:
    """Parse a reply into claim candidates. Refuses malformed ones by name, never silently."""
    body = text.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        obj = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ProposerError(
            f"the model's reply is not JSON ({exc.msg}). Returning zero claims would report a "
            "parse failure as a document that reports nothing."
        ) from exc

    raw = obj.get("claims", []) if isinstance(obj, dict) else []
    out: list[ClaimCandidate] = []
    malformed: list[str] = []
    for i, c in enumerate(raw):
        if not isinstance(c, dict):
            malformed.append(f"#{i}: not an object")
            continue
        value, label = str(c.get("value", "")).strip(), str(c.get("label", "")).strip()
        evidence = str(c.get("evidence", ""))
        if not value:
            malformed.append(f"#{i}: empty value")
            continue
        if not evidence.strip():
            malformed.append(f"#{i}: no evidence sentence; there would be nothing to locate")
            continue
        if value not in evidence:
            # Rule 2. If the value is not inside the sentence the model says it read it from, the
            # two do not describe one observation and locating the sentence would not locate the
            # value.
            malformed.append(
                f"#{i}: value {value!r} was searched for inside its own evidence sentence and "
                "the search returned no match, so the two describe different text")
            continue
        out.append(ClaimCandidate(value=value, label=label, evidence=evidence, model=model,
                                  index=i))
    return ClaimSet(claims=tuple(out), model=model, document=document,
                    chars_offered=chars_offered, raw_blocks=len(raw), malformed=tuple(malformed))


def locate(claims: ClaimSet, source: InstrumentText) -> tuple[tuple[Any, ...], tuple[str, ...]]:
    """Turn claims into `Observation`s by FINDING each value in the source. Returns `(obs, lost)`.

    THE SPAN IS COMPUTED HERE AND NOWHERE ELSE. A claim whose evidence the document does not
    contain, or whose value does not sit inside the located evidence, yields no observation — and
    is returned in `lost` so the denominator survives.

    A span inside a DISPUTED region is refused too: the parties disagree there, so the sentinel is
    what a re-read would return and `A5`'s `REVERIFIES` would pass on a character nobody wrote.
    """
    from cdfc.evidence.observe import Observation

    obs: list[Observation] = []
    lost: list[str] = []
    for c in claims.claims:
        ev_at = source.text.find(c.evidence.strip())
        if ev_at == -1:
            lost.append(f"{c.value!r}: evidence_not_located — the sentence is not in {claims.document}")
            continue
        rel = c.evidence.strip().find(c.value)
        lo = ev_at + rel
        hi = lo + len(c.value)
        if source.text[lo:hi] != c.value:
            lost.append(f"{c.value!r}: value_not_at_computed_span")
            continue
        if source.is_disputed((lo, hi)):
            lost.append(f"{c.value!r}: span_in_disputed_region — the readers disagree there")
            continue
        unit = source.unit_at((lo, hi))
        obs.append(Observation(
            value=c.value, document=claims.document, span=(lo, hi),
            page=unit.page if unit is not None else None,
            context=source.text[max(0, lo - 60):hi + 60],
        ))
    return tuple(obs), tuple(lost)


def label_binding(
    claims: ClaimSet, observations: Sequence[Any], fields: Any
) -> dict[str, tuple[Any, ...]]:
    """Bind located observations to fields by the model's LABEL against the template's label.

    Deliberately crude and declared so: token overlap, no weights. `cdfc.correspond.schema` is the
    measured binder and this is the fallback for a source with no columns to match on. `A5`
    adjudicates whatever it is handed, so a weak binder costs coverage and cannot cost correctness
    — which is the property the six conditions exist to provide.
    """
    import re

    def toks(s: str) -> set[str]:
        return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower())}

    by_value: dict[str, list[Any]] = {}
    for o in observations:
        by_value.setdefault(o.value, []).append(o)

    out: dict[str, list[Any]] = {}
    for c in claims.claims:
        ct = toks(c.label)
        if not ct:
            continue
        for f in fields.fields:
            if len(ct & toks(f.label)) >= 2:
                out.setdefault(f.ref, []).extend(by_value.get(c.value, []))
    return {k: tuple(v) for k, v in out.items() if v}
