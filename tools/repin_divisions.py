#!/usr/bin/env python
"""N1 — THE RE-PIN. Add the durable division layer to a pinned instrument, once, deliberately.

    make repin

`docs/measurements/N1-repin-blast-radius.md` recommended re-pinning before `A4`, while the blast
radius is near-zero, and said what a re-pin must be:

> `deserialise` recomputes a digest over the units, text and manifests and refuses a mismatch. **A
> re-pin therefore cannot happen by accident** — it is only possible as a deliberate act that
> recomputes the digest.

This is that act, and it is a one-shot: after it runs, `tools/pin_statute.py` produces the same
result from the PDF because `textsource.build()` now derives the division map itself.

## WHY IT DOES NOT RE-EXTRACT, WHICH IS THE FINDING

`docs/PLAN.md §8 F4` sized this as a re-extraction: recover provision numbers with a
layout-preserving pass, because *"the numbers are absent from our pinned corpus entirely."*

**They are not absent.** They are at the END of the heading unit — `'Net worth requirements 8'` —
where the Gazette's margin column puts them, and a pattern anchored on `^\\d{1,3}\\.` cannot see one.
So the divisions come out of the text the two parties ALREADY corroborated, and the re-pin

  * changes **no unit key**,
  * moves **no span**,
  * leaves the text **byte-identical**,

which this script ASSERTS rather than asserts-in-prose. All three are checked against the file it
is replacing, and a difference in any of them stops the run. The only thing that changes is the
digest, because the division map joins the payload it covers.

That converts N1's own prediction — *"a re-pin invalidates 100% of citations made against the
current corpus"* — into a narrower and better one: **that is true of a RESEGMENTATION, and this is
not one.** Every existing coordinate citation still resolves. What the re-pin buys is that
citations made from here on can be written against `div1_0008`, which survives the resegmentation
that would kill them.
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import digest  # noqa: E402
from cdfc.qualify.instruments import (  # noqa: E402
    InstrumentRow,
    deserialise,
    manifest_bytes,
    row_of,
    serialise,
)
from cdfc.qualify.provisions import recover  # noqa: E402
from cdfc.qualify.textsource import (  # noqa: E402
    REFUSED_TRANSFORMATIONS,
    TRANSFORMATIONS,
    Corroboration,
    DisputedRegion,
    ExtractionManifest,
    InstrumentText,
    ResolvedUnit,
    division_payload,
)

CORPUS = REPO / "corpus/instruments"


def rebuild(obj: dict) -> InstrumentText:
    """Reconstruct the instrument from its stored fields, with the division map derived.

    Reads the raw JSON rather than calling `deserialise`, because `deserialise` now recomputes a
    digest that includes the division map and would refuse the very file this exists to migrate.
    That refusal is correct and is the reason a re-pin has to be explicit.
    """
    units = tuple(
        ResolvedUnit(
            key=u["key"], page=u["page"], span=(u["span"][0], u["span"][1]),
            corroboration=Corroboration(u["corroboration"]),
            parties=tuple(u["parties"]), external_party=u["external_party"],
        )
        for u in obj["units"]
    )
    manifests = tuple(
        ExtractionManifest(
            extractor=m["extractor"], version=m["version"], external=m["external"],
            sha256=m["sha256"], n_units=m["n_units"], n_disputed=m["n_disputed"],
            n_blind=m["n_blind"], exclusion_mechanisms=tuple(m["exclusion_mechanisms"]),
        )
        for m in obj["manifests"]
    )
    divisions = recover(
        [(u.key, u.page, u.span, u.corroboration.value) for u in units], obj["text"]
    )
    payload = {
        "instrument_id": obj["instrument_id"],
        "transformations": [list(t) for t in TRANSFORMATIONS],
        "refused_transformations": [list(t) for t in REFUSED_TRANSFORMATIONS],
        "units": [
            [u.key, u.page, u.corroboration.value, list(u.parties), u.external_party, *u.span]
            for u in units
        ],
        "text": obj["text"],
        "manifests": [
            [m.extractor, m.version, m.external, m.sha256, m.n_units, m.n_disputed, m.n_blind,
             list(m.exclusion_mechanisms)]
            for m in manifests
        ],
        "divisions": division_payload(divisions),
    }
    return InstrumentText(
        instrument_id=obj["instrument_id"],
        text=obj["text"],
        units=units,
        disputed=tuple(
            DisputedRegion(key=d["key"], page=d["page"], span=(d["span"][0], d["span"][1]),
                           readings=dict(d["readings"]))
            for d in obj["disputed"]
        ),
        manifests=manifests,
        transformations=TRANSFORMATIONS,
        refused_transformations=REFUSED_TRANSFORMATIONS,
        divisions=divisions,
        sha256=digest(payload),
    )


def main() -> int:
    blobs = sorted(CORPUS.glob("*.text.json"))
    if not blobs:
        print("FAIL: no instruments to re-pin.")
        return 1

    migrated = 0
    for blob in blobs:
        obj = json.loads(blob.read_bytes().decode("utf-8"))
        before_text, before_units = obj["text"], list(obj["units"])
        it = rebuild(obj)

        # THE THREE ASSERTIONS. A re-pin that moved a span would invalidate every citation, so it
        # is checked here rather than believed -- CLAUDE.md's "assert your anchors", applied to the
        # anchors of the whole system.
        if it.text != before_text:
            print(f"FAIL: {blob.name}: the text changed. This is a RESEGMENTATION, not a re-pin, "
                  "and it invalidates every span recorded against this instrument.")
            return 1
        after = [
            {"key": u.key, "page": u.page, "span": list(u.span),
             "corroboration": u.corroboration.value, "parties": list(u.parties),
             "external_party": u.external_party}
            for u in it.units
        ]
        if after != before_units:
            print(f"FAIL: {blob.name}: {sum(1 for a, b in zip(after, before_units) if a != b)} "
                  "unit(s) changed. No unit may move in a re-pin that only adds addresses.")
            return 1

        blob.write_bytes(serialise(it, kind=obj["kind"], source_name=obj["source_name"],
                                   source_sha256=obj["source_sha256"]))
        c = it.divisions.counts()
        top = len(it.divisions.top_level())
        print(f"  {it.instrument_id:34} sha256 {obj['sha256'][:12]}… -> {it.sha256[:12]}…  "
              f"divisions {c['divisions_total']:5} (top {top:3})  refused {c['refused_total']:4}")
        migrated += 1

    rows: list[InstrumentRow] = []
    for blob in sorted(CORPUS.glob("*.text.json")):
        inst, kind, source_name, source_sha = deserialise(blob.read_bytes())
        rows.append(row_of(inst, kind=kind, source_name=source_name, source_sha256=source_sha))
    (CORPUS / "MANIFEST.json").write_bytes(manifest_bytes(rows))
    print(f"\n  re-pinned {migrated} instrument(s); MANIFEST.json rewritten with {len(rows)} rows.")
    print("  Every unit key and every span is unchanged, asserted above. Only the digest moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
