"""A W3C PROV-O projection of a run and the artefacts it used. EXPORT ONLY.

## Why a standard rather than our own shape

The audit question a regulator asks is not *"what does your JSON say"* — it is *"which documents
produced this number, and who ran it"*. **W3C PROV** exists for exactly that, and its vocabulary is
already the one auditors' tooling reads: `prov:Entity` for a thing, `prov:Activity` for something
that happened, `prov:used` and `prov:wasGeneratedBy` for the edges between them.

Emitting PROV costs us nothing we were not already tracking. The registry is content-addressed, so
every `Entity` has a stable identifier that IS its hash; a run already names the digests it used,
which is `prov:used`; and the coverage declaration is `prov:wasGeneratedBy` that run. **The
provenance is not extra bookkeeping — it is the run manifest, in a vocabulary somebody else
standardised.**

## THIS IS A PROJECTION AND IT IS NEVER AN INPUT

Same rule as `Graph.triples()`: computed on demand from the artefacts, never stored, never read
back to decide anything. `rdflib` is deliberately absent — the projection is a stream of triples
and serialising N-Triples is a `join`. A graph library in the closure of code that answers a
coverage question is the trade `D-A3-01` refuses, and it would buy a serialiser.

## What is deliberately NOT claimed

PROV has `prov:wasAttributedTo` for agents, and this emits it **only when a signatory is named**.
A run nobody signed is attributed to nobody: inventing an agent — a hostname, a process owner —
would put a name against a filing that no person accepted. `A5`'s attestation lane exists for the
same reason.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Final

from cdfc.registry.store import Artefact, RunInputs

PROV: Final[str] = "http://www.w3.org/ns/prov#"
CDFC: Final[str] = "https://cdfc.dev/ns#"

# The one place the vocabulary is written down. A typo in a namespace produces triples that look
# right and join to nothing.
ENTITY: Final[str] = f"{PROV}Entity"
ACTIVITY: Final[str] = f"{PROV}Activity"
USED: Final[str] = f"{PROV}used"
GENERATED_BY: Final[str] = f"{PROV}wasGeneratedBy"
DERIVED_FROM: Final[str] = f"{PROV}wasDerivedFrom"
ATTRIBUTED_TO: Final[str] = f"{PROV}wasAttributedTo"
RDF_TYPE: Final[str] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def artefact_uri(digest: str) -> str:
    """A content address, as a URI. `sha256:` rather than a path, because the identity is the hash
    and a registry that moves must not invalidate a manifest."""
    return f"urn:sha256:{digest}"


def run_uri(run_id: str) -> str:
    return f"urn:cdfc:run:{run_id}"


def triples(
    run_id: str,
    inputs: RunInputs,
    artefacts: dict[str, Artefact],
    *,
    outputs: tuple[str, ...] = (),
    signatory: str = "",
) -> Iterator[tuple[str, str, str]]:
    """The run, its inputs and its outputs, as PROV triples. Deterministic and sorted.

    `artefacts` maps digest to its registry record; a digest with no record is emitted as an
    `Entity` anyway, because a run that named it used it and dropping the triple would make the
    provenance quieter than the truth.
    """
    run = run_uri(run_id)
    yield (run, RDF_TYPE, ACTIVITY)
    yield (run, f"{CDFC}merkleRoot", inputs.merkle_root)

    for d in inputs.digests:                    # already sorted by RunInputs
        e = artefact_uri(d)
        yield (e, RDF_TYPE, ENTITY)
        a = artefacts.get(d)
        if a is not None:
            yield (e, f"{CDFC}kind", a.kind.value)
            yield (e, f"{CDFC}filename", a.filename)
            yield (e, f"{CDFC}size", str(a.size))
            if a.media_type:
                yield (e, f"{CDFC}mediaType", a.media_type)
        yield (run, USED, e)

    for out in sorted(outputs):
        o = artefact_uri(out) if len(out) == 64 else f"urn:cdfc:output:{out}"
        yield (o, RDF_TYPE, ENTITY)
        yield (o, GENERATED_BY, run)
        for d in inputs.digests:
            yield (o, DERIVED_FROM, artefact_uri(d))

    # Only when a person accepted it. See the module docstring.
    if signatory.strip():
        yield (run, ATTRIBUTED_TO, f"urn:cdfc:agent:{signatory.strip()}")


def n_triples(rows: Iterator[tuple[str, str, str]]) -> str:
    """N-Triples. A join, not a library — see the module docstring on `rdflib`."""
    out = []
    for s, p, o in rows:
        obj = f"<{o}>" if o.startswith(("http://", "https://", "urn:")) else f'"{_esc(o)}"'
        out.append(f"<{s}> <{p}> {obj} .")
    return "\n".join(out) + ("\n" if out else "")


def _esc(v: str) -> str:
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
