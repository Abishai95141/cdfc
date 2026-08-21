"""C6 — the request handlers for the LIVE application: upload, map, fill, ASK, attest.

Every handler here derives what it serves from the return's stored inputs (`cdfc.api.derive`).
Nothing is cached and nothing is precomputed, so no screen can disagree with the run it shows.

## The PDF seam

`cdfc.ingest` is inside the verdict closure, so no PDF reader may live in it. A raw PDF is read by
`tools/pdf_ingest.py` at BUILD time, and this module takes that reader as an INJECTED callable —
`install_pdf_reader()` — exactly as `cdfc.model.propose(transport=…)` takes its client. With no
reader installed, a PDF upload is REFUSED with the reason and the remedy. It is not accepted and
silently stored as opaque bytes, which would put an unreadable corpus behind a green tick.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Final

from cdfc.api.derive import (
    DerivationRefused,
    fill_of,
    graph_payload,
    map_of,
    provisions_of,
    surface_of,
)
from cdfc.api.returns import (
    Return,
    ReturnNotFound,
    ReturnStore,
    StoredAnswer,
    answers_for,
    return_id,
)
from cdfc.ask import Answer, AnswerNotAdmitted, apply, questions_for
from cdfc.attest import dsse
from cdfc.registry import ArtefactKind, Registry, RegistryError

APP_ROOT_ENV: Final[str] = "CDFC_APP_ROOT"
DEFAULT_APP_ROOT: Final[str] = "runs/app"

# A PDF's magic bytes. Checked on the BYTES, never on the filename: an upload named `.txt` that is
# a PDF must not be read as text, and one named `.pdf` that is text must not be refused for a
# reader it does not need.
PDF_MAGIC: Final[bytes] = b"%PDF-"

_PDF_READER: Callable[[Path, str], bytes] | None = None


def install_pdf_reader(fn: Callable[[Path, str], bytes] | None) -> None:
    """Supply a build-time PDF reader. `fn(path, instrument_id) -> pinned instrument bytes`."""
    global _PDF_READER
    _PDF_READER = fn


def pdf_reader_installed() -> bool:
    return _PDF_READER is not None


def app_root() -> Path:
    return Path(os.environ.get(APP_ROOT_ENV) or DEFAULT_APP_ROOT)


def _registry() -> Registry:
    return Registry(app_root() / "registry")


def _returns() -> ReturnStore:
    return ReturnStore(app_root())


def _json(status: int, payload: Any):
    from cdfc.api.app import _json as j

    return j(status, payload)


def _err(status: int, error: str, detail: str, **extra: Any):
    from cdfc.api.app import _error

    return _error(status, error, detail, **extra)


def _body_json(req) -> Mapping[str, Any]:
    try:
        obj = json.loads(req.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"the body is not JSON: {e}") from e
    if not isinstance(obj, dict):
        raise ValueError("the body must be a JSON object")
    return obj


# --- capabilities -------------------------------------------------------------------------------

def get_capabilities(req, params):
    """What THIS deployment can actually do. A capability nobody wired reports false, not absent."""
    from cdfc.ask import ASKABLE, NOT_ASKABLE

    return _json(200, {
        "appRoot": str(app_root()),
        "pdfReader": {
            "installed": pdf_reader_installed(),
            "detail": (
                "a build-time PDF reader is installed and raw PDF corpora are read through it"
                if pdf_reader_installed() else
                "no PDF reader is installed in this process, so a raw PDF upload is REFUSED with "
                "a reason. cdfc.ingest is inside the verdict closure and may not contain one; the "
                "reader lives in tools/pdf_ingest.py and needs `docling` and `pdfplumber`. A PDF "
                "already pinned by `make pin-pdf` uploads and reads normally — it is text by then"
            ),
        },
        "askable": sorted(r.value for r in ASKABLE),
        "notAskable": {r.value: why for r, why in NOT_ASKABLE.items()},
        "artefactKinds": sorted(k.value for k in ArtefactKind),
    })


# --- artefacts ----------------------------------------------------------------------------------

def post_artefacts(req, params):
    """Upload one artefact. **The kind is DECLARED by the uploader and never sniffed.**

    `ArtefactKind`'s own docstring fixes that rule, and it matters here: the same CSV is evidence
    when it is a custodian feed and a corpus when it is a rules export, and no byte pattern
    distinguishes them.
    """
    kind_raw = (req.query.get("kind") or "").strip().lower()
    filename = (req.query.get("filename") or "").strip()
    if not req.body:
        return _err(422, "empty_upload",
                    "the upload has no bytes. An empty artefact is not an artefact with no "
                    "content in it; `absent != empty != zero`.")
    if not filename:
        return _err(422, "unnamed_upload",
                    "an artefact is stored under its digest and RECORDED with the name a human "
                    "uploaded it as. A nameless upload cannot be reported back to the person who "
                    "sent it.")
    try:
        kind = ArtefactKind(kind_raw)
    except ValueError:
        return _err(422, "unknown_kind",
                    f"{kind_raw!r} is not a declared artefact kind. The kinds are what this "
                    "system does different things with, not a taxonomy of file formats.",
                    kinds=sorted(k.value for k in ArtefactKind))

    body = req.body
    if body.startswith(PDF_MAGIC):
        if not pdf_reader_installed():
            return _err(
                501, "pdf_reader_not_installed",
                "this upload is a PDF and no PDF reader is installed in this process. "
                "`cdfc.ingest` is INSIDE the verdict closure and may not contain one, so a PDF is "
                "read at build time by tools/pdf_ingest.py, which needs `docling` and "
                "`pdfplumber`. Storing the bytes unread would put an unreadable corpus behind a "
                "green tick.",
                remedy="pip install docling pdfplumber, then `make pin-pdf`; or upload the pinned "
                       "`.text.json` that produces, which needs no reader at all",
            )
        tmp = app_root() / "incoming"
        tmp.mkdir(parents=True, exist_ok=True)
        raw_path = tmp / filename
        raw_path.write_bytes(body)
        try:
            body = _PDF_READER(raw_path, f"corpus:{filename}")     # type: ignore[misc]
        except Exception as exc:                                    # noqa: BLE001
            return _err(422, "pdf_not_readable",
                        f"the installed PDF reader refused this file: {type(exc).__name__}: {exc}")

    try:
        art = _registry().put(body, kind=kind, filename=filename)
    except RegistryError as e:
        return _err(422, "registry_refused", str(e))
    return _json(201, {**art.as_canonical_obj(), "uploadedBytes": len(req.body)})


def get_artefacts(req, params):
    reg = _registry()
    want = (req.query.get("kind") or "").strip().lower()
    kind = None
    if want:
        try:
            kind = ArtefactKind(want)
        except ValueError:
            return _err(422, "unknown_kind", f"{want!r} is not a declared artefact kind",
                        kinds=sorted(k.value for k in ArtefactKind))
    return _json(200, [a.as_canonical_obj() for a in reg.list(kind)])


def get_artefact_surface(req, params):
    """A template's induced field surface, or the REASON it is not derivable."""
    digest = params.get("digest", "")
    reg = _registry()
    try:
        meta = reg.meta(digest)
    except (RegistryError, FileNotFoundError, KeyError):
        return _err(404, "no_such_artefact", f"{digest[:16]}… is not in this registry")
    if meta.kind is not ArtefactKind.TEMPLATE:
        return _err(422, "not_a_template",
                    f"{meta.filename} was uploaded as {meta.kind.value!r}. A field surface is "
                    "induced from a TEMPLATE; inducing one from a source export would be a "
                    "different operation wearing this one's name.")
    return _json(200, surface_of(reg, digest).as_obj())


def get_artefact_provisions(req, params):
    """A corpus, segmented and addressable — the eIds a proposal must cite."""
    digest = params.get("digest", "")
    reg = _registry()
    try:
        meta = reg.meta(digest)
    except (RegistryError, FileNotFoundError, KeyError):
        return _err(404, "no_such_artefact", f"{digest[:16]}… is not in this registry")
    if meta.kind not in (ArtefactKind.RULES, ArtefactKind.INSTRUMENT):
        return _err(422, "not_a_corpus",
                    f"{meta.filename} was uploaded as {meta.kind.value!r}, and provisions are "
                    "segmented from a rules corpus or an instrument.")
    durable = (req.query.get("addressing") or "durable").strip().lower() != "coordinate"
    only = req.query.get("only_with")
    only_with = None if only == "" else (only or "shall")
    try:
        pv = provisions_of(reg, digest, only_with=only_with, durable=durable)
    except Exception as exc:                                        # noqa: BLE001
        return _err(422, "corpus_not_segmentable",
                    f"{meta.filename}: {type(exc).__name__}: {exc}")
    from cdfc.api.derive import corpus_text

    it = corpus_text(reg, digest)
    agreement = {k: list(v) for k, v in it.agreement().items()}
    return _json(200, {
        "digest": digest, "filename": meta.filename,
        "instrumentId": pv.instrument_id, "instrumentSha256": pv.instrument_sha256,
        "addressing": "durable" if durable else "coordinate",
        "onlyWith": only_with,
        "provisionsTotal": len(pv.provisions),
        "durableCount": pv.durable_count,
        "refusedMarkers": len(pv.refused_markers),
        "unitsTotal": len(it.units),
        "disputedTotal": len(it.disputed),
        # TWO VECTORS, NEVER AVERAGED. A text corpus is corroborated by two of OUR segmenters
        # (SAME_AUTHOR); a pinned PDF by two independent extractors (EXTERNAL). Presenting them as
        # one number would grade a text upload as though a second party had read it.
        "agreement": agreement,
        "provisions": [{"eid": p.eid, "eidKind": p.eid_kind, "page": p.page,
                        "span": list(p.span), "text": p.text[:400]}
                       for p in pv.provisions[:200]],
    })


# --- returns ------------------------------------------------------------------------------------

def post_returns(req, params):
    """Open a return over artefacts that were uploaded first. Idempotent by content."""
    try:
        body = _body_json(req)
    except ValueError as e:
        return _err(422, "bad_body", str(e))

    reg = _registry()
    template = str(body.get("templateDigest", "")).strip()
    sources = [str(x).strip() for x in body.get("sourceDigests", []) if str(x).strip()]
    corpus = str(body.get("corpusDigest", "")).strip()
    proposals = str(body.get("proposalsDigest", "")).strip()
    subject = {str(k): str(v) for k, v in dict(body.get("subject", {})).items()}
    opened_at = str(body.get("openedAt", "")).strip()
    label = str(body.get("label", "")).strip()

    if not opened_at:
        return _err(422, "undated_return",
                    "the return names no instant. The core reads no clock — `ci/no-clock-in-core."
                    "sh` — so the caller supplies it and an absent one is not defaulted.")
    for d, what in [(template, "templateDigest")] + [(s, "sourceDigests") for s in sources] \
            + ([(corpus, "corpusDigest")] if corpus else []) \
            + ([(proposals, "proposalsDigest")] if proposals else []):
        if not d:
            return _err(422, "missing_artefact", f"{what} is required and was not supplied")
        if not reg.has(d):
            return _err(422, "artefact_not_uploaded",
                        f"{what} names {d[:16]}…, which is not in this registry. Upload it first; "
                        "a return over an artefact nobody uploaded would cite a digest that "
                        "addresses nothing.")
    if reg.meta(template).kind is not ArtefactKind.TEMPLATE:
        return _err(422, "not_a_template",
                    f"{reg.meta(template).filename} was uploaded as "
                    f"{reg.meta(template).kind.value!r}, not 'template'.")

    inputs = reg.inputs([template, *sources] + ([corpus] if corpus else [])
                        + ([proposals] if proposals else []))
    rid = return_id(inputs.merkle_root, subject)
    store = _returns()
    try:
        existing = store.get(rid)
    except ReturnNotFound:
        existing = None
    if existing is not None:
        # SAME INPUTS, SAME RETURN. Re-opening must not discard answers somebody already gave.
        return _json(200, {**existing.as_obj(), "merkleRoot": inputs.merkle_root,
                           "reopened": True})
    r = store.put(Return(
        id=rid, template_digest=template, source_digests=tuple(sources), corpus_digest=corpus,
        proposals_digest=proposals, subject=subject, opened_at=opened_at, label=label,
    ))
    return _json(201, {**r.as_obj(), "merkleRoot": inputs.merkle_root, "reopened": False})


def get_returns(req, params):
    return _json(200, [r.as_obj() for r in _returns().list()])


def _resolved(rid: str):
    return _returns().get(rid)


def get_return(req, params):
    """The return, and its fill declaration AFTER answers. Derived on this request."""
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        f = fill_of(reg, r)
    except DerivationRefused as e:
        return _json(200, {**r.as_obj(), "filled": None,
                           "refusal": {"reason": e.reason, "detail": e.detail}})

    d = f.declaration
    return _json(200, {
        **r.as_obj(),
        "refusal": None,
        "merkleRoot": f.run.merkle_root,
        "surface": f.surface.as_obj(),
        "filled": {
            "counts": d.counts(),
            "lines": list(d.lines()),
            "schemaMatchPairs": [{"column": c, "field": fr, "weight": round(float(w), 4)}
                                 for c, fr, w in f.run.schema_match.pairs],
            "evidenced": [{"ref": p.ref, "label": p.label, "value": p.value,
                           "document": p.document, "span": list(p.span), "page": p.page,
                           "context": p.context[:200],
                           "conditions": [{"name": c.name, "holds": c.holds, "detail": c.detail}
                                          for c in p.conditions]}
                          for p in d.admitted()],
            "derived": [x.as_canonical_obj() for x in d.derived],
            "asserted": [x.as_canonical_obj() for x in d.asserted],
            "attestations": [{"ref": a.ref, "label": a.label, "certifies": a.certifies,
                              "supporting": len(a.supporting)} for a in d.attestations],
            "unlocatable": [{"field": k, "value": v} for k, v in f.run.unlocatable[:50]],
        },
    })


def get_return_questions(req, params):
    """THE QUESTIONS — and, separately, the refusals that are NOT questions.

    Both, always. A screen that reported only the questions would understate the work by 3,615 on
    the pinned FME return, and one that headlined the refusal total as *"needs your judgement"*
    would overstate the ANSWERABLE work by the same amount. Neither number alone is honest.
    """
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        f = fill_of(reg, r)
    except DerivationRefused as e:
        return _err(422, e.reason, e.detail)

    qs = f.questions
    reason = (req.query.get("reason") or "").strip()
    rows = [q for q in qs.questions if not reason or q.reason.value == reason]
    try:
        limit = max(1, min(500, int(req.query.get("limit") or 100)))
    except ValueError:
        limit = 100
    return _json(200, {
        "returnId": r.id,
        "counts": qs.counts(),
        "lines": list(qs.lines()),
        "answeredSoFar": len(answers_for(r)),
        "questionsTotal": len(rows),
        "questions": [q.as_canonical_obj() for q in rows[:limit]],
        "truncated": len(rows) > limit,
        "notAsked": [{"reason": n.reason.value, "count": n.count, "why": n.why}
                     for n in qs.not_asked],
    })


def post_return_answers(req, params):
    """An answer becomes a value — labelled `resolved_by: human`, and NEVER counted as evidenced."""
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        body = _body_json(req)
    except ValueError as e:
        return _err(422, "bad_body", str(e))

    raw = body.get("answers")
    if not isinstance(raw, list) or not raw:
        return _err(422, "no_answers", "the body carries no `answers` array")

    try:
        f = fill_of(reg, r)
    except DerivationRefused as e:
        return _err(422, e.reason, e.detail)

    qs = f.questions
    by_id = qs.by_id()
    submitted: list[Answer] = []
    stored: list[StoredAnswer] = []
    for a in raw:
        if not isinstance(a, dict):
            return _err(422, "bad_answer", "each answer must be a JSON object")
        qid = str(a.get("questionId", "")).strip()
        q = by_id.get(qid)
        if q is None:
            return _err(422, "no_such_question",
                        f"{qid!r} is not a question this return currently puts. Question ids are "
                        "derived from the template digest, the field ref and the reason, so an id "
                        "from another run addresses another run's cell.")
        submitted.append(Answer(question_id=qid, value=str(a.get("value", "")),
                                answered_by=str(a.get("answeredBy", "")),
                                answered_at=str(a.get("answeredAt", ""))))
        stored.append(StoredAnswer(question_id=qid, ref=q.ref, value=str(a.get("value", "")),
                                   answered_by=str(a.get("answeredBy", "")),
                                   answered_at=str(a.get("answeredAt", ""))))

    # ADJUDICATE BEFORE STORING. An answer written to disk and then refused would leave the return
    # carrying an assertion the system never admitted, and the next derivation would drop it
    # silently — which is a stored fact that no screen shows.
    try:
        applied = apply(f.declaration, qs, submitted)
    except AnswerNotAdmitted as e:
        return _err(422, e.reason.value, e.detail)

    redirect_rows = [{"ref": x.ref, "document": x.document, "question_id": x.question_id,
                      "answered_by": x.answered_by, "answered_at": x.answered_at}
                     for x in applied.redirects]
    _returns().add_answers(r.id, stored, redirect_rows)

    after = fill_of(reg, _resolved(r.id))
    return _json(201, {
        "returnId": r.id,
        "admitted": len(applied.asserted),
        "redirected": len(applied.redirects),
        "asserted": [x.as_canonical_obj() for x in applied.asserted],
        "redirects": redirect_rows,
        "counts": after.declaration.counts(),
        "questionsRemaining": len(after.questions.questions),
        "note": ("an asserted value is placed in the return and is NOT counted as evidenced. "
                 "`admitted` in the counts is the evidenced total and it did not move."),
    })


def get_return_graph(req, params):
    """The REAL graph: nodes, typed edges, and the four populations kept apart."""
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        m = map_of(reg, r)
    except DerivationRefused as e:
        return _err(422, e.reason, e.detail)
    try:
        limit = max(10, min(2000, int(req.query.get("limit") or 600)))
    except ValueError:
        limit = 600
    return _json(200, {"returnId": r.id, **graph_payload(m, limit=limit)})


def get_return_map(req, params):
    """The driver's own declaration: provisions, proposals, the five gates, and what they refused."""
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        m = map_of(reg, r)
    except DerivationRefused as e:
        return _err(422, e.reason, e.detail)
    c = m.coverage
    return _json(200, {
        "returnId": r.id,
        "provisionsTotal": len(m.provisions),
        "durableCount": m.provisions.durable_count,
        "proposalsTotal": m.proposals_total,
        "admitted": m.admitted,
        "refused": m.refused,
        "refusals": list(m.refusal_rows[:100]),
        "coverage": {
            "surfaceTotal": c.surface_total, "labelledTotal": c.labelled_total,
            "labelRule": c.label_rule, "fieldsGoverned": c.fields_governed,
            "fieldsRead": c.fields_read, "fieldsUngoverned": c.fields_ungoverned,
            "provisionsTotal": c.provisions_total, "provisionsCited": c.provisions_cited,
            "provisionsDurable": c.provisions_durable, "rulesAdmitted": c.rules_admitted,
            "attestationFields": c.attestation_fields,
        },
        "lines": list(c.lines()),
        "graphCounts": m.graph.counts(),
    })


# --- the certificate ----------------------------------------------------------------------------

# WHAT THE CERTIFICATE DOES NOT SAY. Rendered INTO the artefact, not into a screen that renders it,
# so a certificate detached from this application still carries its own limits.
CERTIFICATE_DOES_NOT_SAY: Final[tuple[str, ...]] = (
    "that any figure in the return is CORRECT. The claim is provenance: which document and which "
    "span each value came from, and a typed reason for every cell that has none.",
    "that the filing is complete. Nothing here bounds RECALL — we report the fields a binder "
    "proposed, never the ones nobody proposed.",
    "that an ASSERTED value was checked. A value a human supplied in answer to a question "
    "re-reads nothing; it is placed in the return, labelled `resolved_by: human`, and excluded "
    "from every evidenced count.",
    "that a DERIVED value was checked. A model produced it and no span supports it.",
    "that the checks are gate-qualified. G4 admits 0, and no fill-accuracy number exists.",
    "that the signature is trustworthy. It is made with the PUBLISHED demo key "
    "`cdfc-demo-key-do-not-trust`, by a non-constant-time Ed25519 implementation that refuses to "
    "sign with any other key.",
)


def get_return_certificate(req, params):
    """A signed coverage certificate over the return's inputs and its four lanes.

    The payload is canonical JSON and the signature is deterministic (RFC 8032 derives the nonce
    from the key and the message), so the same return signs to the same 64 bytes and the signature
    is part of the byte-identity claim rather than an exception to it.
    """
    reg = _registry()
    try:
        r = _resolved(params.get("id", ""))
    except ReturnNotFound as e:
        return _err(404, "no_such_return", str(e))
    try:
        f = fill_of(reg, r)
    except DerivationRefused as e:
        return _err(422, e.reason, e.detail)

    d = f.declaration
    counts = d.counts()
    inputs = reg.inputs([r.template_digest, *r.source_digests]
                        + ([r.corpus_digest] if r.corpus_digest else [])
                        + ([r.proposals_digest] if r.proposals_digest else []))
    payload_obj = {
        "returnId": r.id,
        "openedAt": r.opened_at,
        "merkleRoot": inputs.merkle_root,
        # `RunInputs` carries the DIGESTS and the root — read the metadata back from the
        # registry rather than assuming an `artefacts` attribute the dataclass does not have.
        "inputs": [{"digest": d, "kind": reg.meta(d).kind.value,
                    "filename": reg.meta(d).filename, "size": reg.meta(d).size}
                   for d in inputs.digests],
        "templateSha256": d.template_sha256,
        "surfaceTotal": d.surface_total,
        "lanes": {
            "evidenced": counts["admitted"],
            "derived": counts["derived"],
            "asserted": counts["asserted"],
            "refused": counts["refused"],
            "awaitingSignature": counts["attestations"],
        },
        "placedInReturn": counts["filled_total"],
        "refusedByReason": {k[len("refused_"):]: v for k, v in counts.items()
                            if k.startswith("refused_")},
        "asserted": [x.as_canonical_obj() for x in d.asserted],
        "questionsOutstanding": len(f.questions.questions),
        "doesNotSay": list(CERTIFICATE_DOES_NOT_SAY),
    }
    payload = json.dumps(payload_obj, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    env = dsse.sign(payload)
    return _json(200, {
        "certificate": payload_obj,
        "envelope": {
            "payloadType": env.payload_type,
            "keyid": env.keyid,
            "sig": env.sig.hex(),
            "publicKey": env.public_key.hex(),
            "payloadSha256": hashlib.sha256(payload).hexdigest(),
        },
    })
