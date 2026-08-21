"""Everything a screen shows, DERIVED from a return's stored inputs. Nothing here is a snapshot.

One module, so there is exactly one place where the order of derivation is decided — the same
reason `evidence/run.py` is one function.

    artefacts + answers  ->  field surface  ->  binding  ->  fill declaration
                         ->  answers applied            ->  questions
                         ->  provisions x proposals     ->  adjudication -> graph -> coverage
                         ->  certificate

**No model is called from any of it.** LAYER 2 reaches the driver as a FILE, exactly as
`evidence.run(proposals: Path)` requires; this module reads a proposals artefact out of the
registry and hands the driver its path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from cdfc.api.returns import Return, answers_for
from cdfc.ask import Answer, QuestionSet, apply, claims_from, questions_for
from cdfc.ask.answers import Redirect
from cdfc.evidence.fields import FieldSet, SurfaceRefusal, from_template, select_rule
from cdfc.evidence.gates import adjudicate
from cdfc.evidence.graph import Graph, Node, NodeKind
from cdfc.evidence.graph import build as build_graph
from cdfc.evidence.proposal import load as load_proposals
from cdfc.evidence.provisions import ProvisionSet, from_divisions, from_instrument
from cdfc.evidence.query import Coverage, coverage
from cdfc.fill.pipeline import FillRun
from cdfc.fill.pipeline import run as fill_run
from cdfc.fill.propose import FillDeclaration
from cdfc.ingest.prose import read_text
from cdfc.qualify.instruments import deserialise
from cdfc.qualify.textsource import InstrumentText
from cdfc.registry import ArtefactKind, Registry


class DerivationRefused(RuntimeError):
    """A derivation that cannot be performed, with the reason. Never an empty result."""

    def __init__(self, reason: str, detail: str) -> None:
        self.reason, self.detail = reason, detail
        super().__init__(f"{reason}: {detail}")


# --- LAYER 1b: the template's field surface ---------------------------------------------------

@dataclass(frozen=True, slots=True)
class Surface:
    """A template's induced field surface, OR the reason it could not be induced.

    `absent != empty != zero`. `C1` measured 2 of the 9 real regulator workbooks shipping neither
    a protection mask nor a data validation, so neither induction signal exists for them; a
    `FieldSet` with zero fields would report those as templates with nothing in them.
    """

    template_digest: str
    filename: str
    fields: FieldSet | None
    refusal: SurfaceRefusal | None
    detail: str

    def as_obj(self) -> dict[str, Any]:
        if self.fields is None:
            return {"templateSha256": self.template_digest, "filename": self.filename,
                    "inducible": False, "refusal": (self.refusal.value if self.refusal else None),
                    "detail": self.detail, "surfaceTotal": None, "labelled": None}
        f = self.fields
        return {
            "templateSha256": self.template_digest, "filename": self.filename, "inducible": True,
            "refusal": None, "detail": "",
            "surfaceTotal": f.surface_total, "labelled": len(f.fields),
            "labelRule": f.label_rule.value,
            "attestations": len(f.attestations),
            "types": _counted(t.type.value for t in f.fields),
            "sample": [{"ref": x.ref, "label": x.label, "type": x.type.value,
                        "asks": x.asks.value, "vocabulary": list(x.vocabulary)}
                       for x in f.fields[:40]],
        }


def _counted(vals) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in vals:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def surface_of(registry: Registry, template_digest: str) -> Surface:
    meta = registry.meta(template_digest)
    path = registry.path(template_digest)
    try:
        fs = from_template(path, rule=select_rule(path))
    except Exception as exc:                                       # noqa: BLE001
        # A workbook this reader cannot open at all. Reported as a REFUSAL naming the exception,
        # never as a template with no fields: those are different facts about the upload.
        return Surface(template_digest, meta.filename, None, None,
                       f"{type(exc).__name__}: {exc}")
    if fs.refusal is not None:
        return Surface(template_digest, meta.filename, None, fs.refusal,
                       "the workbook ships no unlocked-cell protection mask, so the field surface "
                       "is not derivable from it. Two of the nine pinned regulator workbooks are "
                       "in this state and they also ship zero data validations, so neither "
                       "induction signal is present")
    return Surface(template_digest, meta.filename, fs, None, "")


# --- LAYER 1a: the rules corpus, segmented and addressable --------------------------------------

def corpus_text(registry: Registry, digest: str) -> InstrumentText:
    """A pinned instrument if the bytes deserialise as one, otherwise a plain-text corpus.

    The discrimination is on the BYTES, never on a filename: `fill.pipeline` already reads sources
    this way, and guessing from an extension would let a mislabelled upload be read the wrong way
    silently. A PDF reaches this only through `tools/pdf_ingest.py` at build time — see
    `handlers.post_artefacts`, which refuses raw PDF bytes with the reader that is missing.
    """
    raw = registry.get(digest)
    try:
        it, _kind, _name, _sha = deserialise(raw)
    except Exception:                                              # noqa: BLE001
        return read_text(raw, instrument_id=f"corpus:{digest[:12]}")
    return it


def provisions_of(registry: Registry, digest: str, *, only_with: str | None = "shall",
                  durable: bool = True) -> ProvisionSet:
    it = corpus_text(registry, digest)
    return (from_divisions if durable else from_instrument)(it, only_with=only_with)


# --- the fill, and the answers applied to it ----------------------------------------------------

@dataclass(frozen=True, slots=True)
class Filled:
    run: FillRun
    declaration: FillDeclaration     # AFTER answers; `run.declaration` is before them
    questions: QuestionSet
    surface: Surface
    applied: int
    redirected: int


def _redirects_of(r: Return) -> tuple[Redirect, ...]:
    return tuple(Redirect(ref=str(x["ref"]), document=str(x["document"]),
                          question_id=str(x.get("question_id", "")),
                          answered_by=str(x.get("answered_by", "")),
                          answered_at=str(x.get("answered_at", "")))
                 for x in r.redirects)


def fill_of(registry: Registry, r: Return) -> Filled:
    """Bind the sources, adjudicate, then apply the stored answers. Deterministic end to end.

    ## The two passes, and why the second one is not a retry

    A `not_locatable_in_source` answer names the DOCUMENT a value should have come from. It does
    not supply the value, so it cannot be asserted — it directs a re-read. `fill.pipeline` already
    has the mechanism: `claims`, rows of `{document, field, value}` that are LOCATED in the named
    document or refused. So the first pass produces what a column offered and could not find, the
    redirects turn those into claims, and the second pass looks where the filer said to look.

    A value found on the second pass is EVIDENCED, with a real span — which is the one shape of
    answer that can produce evidence rather than an assertion.
    """
    surface = surface_of(registry, r.template_digest)
    if surface.fields is None:
        raise DerivationRefused(
            "template_surface_not_inducible",
            f"{surface.filename}: {surface.detail}. A fill needs a field surface, and a template "
            "we cannot read must not be filled as though it had no fields.",
        )
    if not r.source_digests:
        raise DerivationRefused(
            "no_source",
            "this return names no source export, so there is nothing to bind evidence from. "
            "Upload a CSV, a workbook or a pinned document and add it to the return.",
        )

    tpath = registry.path(r.template_digest)
    first = fill_run(registry, template_digest=r.template_digest,
                     source_digest=list(r.source_digests), template_path=tpath,
                     subject=dict(r.subject) or None)

    redirects = _redirects_of(r)
    run = first
    if redirects:
        offered = dict(first.unlocatable)
        claims = claims_from(redirects, offered)
        if claims:
            run = fill_run(registry, template_digest=r.template_digest,
                           source_digest=list(r.source_digests), template_path=tpath,
                           subject=dict(r.subject) or None, claims=claims)

    docs = _documents(registry, r)
    qs = questions_for(run.declaration, surface.fields, binding=run.binding,
                       documents=list(docs), document_names=docs)

    stored = answers_for(r)
    by_id = qs.by_id()
    admissible = [Answer(question_id=a.question_id, value=a.value, answered_by=a.answered_by,
                         answered_at=a.answered_at)
                  for a in stored if a.question_id in by_id]
    result = apply(run.declaration, qs, admissible)

    # THE QUESTIONS ARE RE-DERIVED OVER THE POST-ANSWER DECLARATION, so an answered question stops
    # being asked. Deriving them once and filtering would leave the count and the list disagreeing
    # the moment `apply` refused one.
    remaining = questions_for(result.declaration, surface.fields, binding=run.binding,
                              documents=list(docs), document_names=docs)
    return Filled(run=run, declaration=result.declaration, questions=remaining, surface=surface,
                  applied=len(result.asserted), redirected=len(result.redirects))


def _documents(registry: Registry, r: Return) -> dict[str, str]:
    """`instrument id -> the name a person uploaded it as`.

    A `not_locatable_in_source` answer must SUBMIT the instrument id, because that is what a claim
    resolves against; a filer must SEE the filename, because that is what they recognise. Both, and
    the mapping is built here rather than guessed in `cdfc.ask`, which has no registry.
    """
    out: dict[str, str] = {}
    for d in r.source_digests:
        raw = registry.get(d)
        try:
            it, _k, _n, _s = deserialise(raw)
        except Exception:                                          # noqa: BLE001
            out[f"source:{d[:12]}"] = registry.meta(d).filename
        else:
            out[it.instrument_id] = registry.meta(d).filename
    return out


# --- LAYER 3/4: the graph over admitted proposals ------------------------------------------------

@dataclass(frozen=True, slots=True)
class Mapped:
    provisions: ProvisionSet
    fields: FieldSet
    graph: Graph
    coverage: Coverage
    proposals_total: int
    admitted: int
    refused: int
    refusal_rows: tuple[dict[str, Any], ...]


def map_of(registry: Registry, r: Return) -> Mapped:
    """THE DRIVER's layer order, over this return's own corpus, template and proposals."""
    if not r.corpus_digest:
        raise DerivationRefused(
            "no_corpus",
            "this return names no rules corpus, so there are no provisions to map a template "
            "against. Upload a corpus and add it to the return.",
        )
    if not r.proposals_digest:
        raise DerivationRefused(
            "no_proposals",
            "this return names no proposals file. LAYER 2 reaches the driver as DATA — the model "
            "writes proposals and the driver reads them — so a mapping with no proposals file has "
            "nothing for the five gates to adjudicate. `tools/gen_proposals.py` writes one.",
        )
    surface = surface_of(registry, r.template_digest)
    if surface.fields is None:
        raise DerivationRefused("template_surface_not_inducible", surface.detail)

    it = corpus_text(registry, r.corpus_digest)
    props = load_proposals(registry.path(r.proposals_digest))

    # THE PROPOSALS AND THE PROVISIONS MUST SHARE AN ADDRESS SPACE, and which one a file was
    # written in is a property of the file. Picking durable and refusing 172 proposals one at a
    # time at G-QUOTE would report an addressing mismatch as 172 ungrounded claims.
    durable = from_divisions(it, only_with="shall")
    provs = durable
    known = {x.eid for x in durable.provisions}
    if props.proposals and not any(x.eid in known for x in props.proposals):
        provs = from_instrument(it, only_with="shall")

    adj = adjudicate(props, provs, surface.fields)
    g = build_graph(adj, provs, surface.fields)
    rows = tuple(
        {"eid": v.proposal.eid, "field": getattr(v.proposal, "field_ref", ""),
         "planted": bool(v.proposal.is_planted),
         "refusals": [{"gate": gate, "reason": reason.value, "detail": detail}
                      for gate, reason, detail in v.refusals]}
        for v in adj.refused
    )
    return Mapped(provisions=provs, fields=surface.fields, graph=g,
                  coverage=coverage(g, adj, provs, surface.fields),
                  proposals_total=len(props.proposals), admitted=len(adj.admitted),
                  refused=len(adj.refused), refusal_rows=rows)


def graph_payload(m: Mapped, *, limit: int = 600) -> dict[str, Any]:
    """Nodes and edges, BY KIND, with the four populations kept apart.

    The old screen drew three circles from three counts. This serves the real adjacency, and it
    caps by taking the nodes an edge actually touches first — a truncation that dropped edges'
    endpoints would render a graph with more edges than nodes and no way to see it had been cut.
    """
    kinds = _counted(n.kind.value for n in m.graph.nodes)
    edges = [{"src": e.src, "dst": e.dst, "kind": e.kind.value} for e in m.graph.edges]
    touched = {e["src"] for e in edges} | {e["dst"] for e in edges}
    nodes = [n for n in m.graph.nodes if n.id in touched]
    isolated = [n for n in m.graph.nodes if n.id not in touched]
    shown = nodes[:limit]
    shown_ids = {n.id for n in shown}
    return {
        "counts": kinds,
        "edgeCounts": _counted(e["kind"] for e in edges),
        "nodesTotal": len(m.graph.nodes),
        "edgesTotal": len(edges),
        "isolatedTotal": len(isolated),
        "nodesShown": len(shown),
        "truncated": len(nodes) > limit,
        "populations": {
            "corpus": kinds.get(NodeKind.PROVISION.value, 0),
            "template": kinds.get(NodeKind.FIELD.value, 0),
            "binding": kinds.get(NodeKind.RULE.value, 0),
            "record": kinds.get(NodeKind.RECORD.value, 0),
            "entity": kinds.get(NodeKind.ENTITY.value, 0),
        },
        "nodes": [{"id": n.id, "kind": n.kind.value, "label": _node_label(n)} for n in shown],
        "edges": [e for e in edges if e["src"] in shown_ids and e["dst"] in shown_ids],
    }


# `Node.attrs` is a tuple of (key, value) PAIRS, not a mapping — read from the dataclass, not
# assumed. A `getattr(n, "label", "—")` here never fails and would publish an em-dash for every
# node in the graph, which is the defect that emptied a `governed` column across nine templates
# and rendered every provenance field as absent.
_LABEL_KEYS: Final[tuple[str, ...]] = ("label", "heading", "text", "eid", "ref", "title")


def _node_label(n: Node) -> str:
    attrs = dict(n.attrs)
    for key in _LABEL_KEYS:
        v = attrs.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()[:120]
    return n.id


def load_json(registry: Registry, digest: str) -> Any:
    return json.loads(registry.get(digest).decode("utf-8"))


def kind_of(registry: Registry, digest: str) -> ArtefactKind:
    return registry.meta(digest).kind


def template_path(registry: Registry, digest: str) -> Path:
    return registry.path(digest)
