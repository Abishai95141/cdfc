"""C6 — a live return: the INPUTS are stored, and everything else is re-derived on every read.

## The one piece of state, and why it is only this

`web/README.md` gave the rule the old surface followed and this one keeps: *"a screen that
recomputes is a screen that can disagree with the run it claims to show."* The old surface obeyed
it by rendering a snapshot somebody else computed, which is also why nothing in it could be done.

The resolution is not to store more. It is to store **only what a human supplied** and to re-derive
the rest, exactly as `D-A3-01` decided for the evidence graph: a projection, never a store.

    STORED   the template digest · the source digests · the corpus · the subject · THE ANSWERS
    DERIVED  the field surface · the binding · the fill declaration · the questions · the graph
             · the coverage · the certificate

Answers are stored because a person's assertion is an INPUT — nothing can re-derive what somebody
said. Everything else is a function of the inputs, so a screen cannot disagree with the run: there
is no second copy to disagree with.

## The id is content-derived

A counter would renumber when a source is added, and a run's answers would silently re-target
another run's cells. The id is `sha256(merkle_root ‖ subject)`, so the same artefacts under the
same subject are the same return — and two returns over different evidence can never collide.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from cdfc.registry import Registry

RETURNS_DIRNAME: Final[str] = "returns"


class ReturnNotFound(LookupError):
    """No return with that id. Never confused with a return that has produced nothing yet."""


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


@dataclass(frozen=True, slots=True)
class StoredAnswer:
    """One answer as the filer gave it. The instant is theirs; this module reads no clock."""

    question_id: str
    ref: str
    value: str
    answered_by: str
    answered_at: str

    def as_obj(self) -> dict[str, str]:
        return {"question_id": self.question_id, "ref": self.ref, "value": self.value,
                "answered_by": self.answered_by, "answered_at": self.answered_at}


@dataclass(frozen=True, slots=True)
class Return:
    """The inputs to one filing. Nothing derived is in here, on purpose."""

    id: str
    template_digest: str
    source_digests: tuple[str, ...]
    corpus_digest: str                      # "" when no rules corpus has been attached
    proposals_digest: str                   # "" when no LAYER-2 proposals have been attached
    subject: Mapping[str, str]
    opened_at: str
    answers: tuple[StoredAnswer, ...] = ()
    label: str = ""
    redirects: tuple[Mapping[str, str], ...] = field(default_factory=tuple)

    def as_obj(self) -> dict[str, Any]:
        return {
            "id": self.id, "template_digest": self.template_digest,
            "source_digests": list(self.source_digests), "corpus_digest": self.corpus_digest,
            "proposals_digest": self.proposals_digest, "subject": dict(self.subject),
            "opened_at": self.opened_at, "label": self.label,
            "answers": [a.as_obj() for a in self.answers],
            "redirects": [dict(r) for r in self.redirects],
        }


def return_id(merkle_root: str, subject: Mapping[str, str]) -> str:
    h = hashlib.sha256(merkle_root.encode("utf-8") + b"\x1f" + _canonical(dict(subject)))
    return h.hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class ReturnStore:
    """Returns on disk, one canonical-JSON file each. Append and replace; never partial."""

    root: Path

    @property
    def dir(self) -> Path:
        return self.root / RETURNS_DIRNAME

    def put(self, r: Return) -> Return:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{r.id}.json").write_bytes(_canonical(r.as_obj()))
        return r

    def get(self, rid: str) -> Return:
        p = self.dir / f"{_safe(rid)}.json"
        if not p.is_file():
            raise ReturnNotFound(
                f"{rid!r} is not a return this deployment holds. A return is opened by POST "
                "/v1/returns over artefacts that were uploaded first."
            )
        return _from_obj(json.loads(p.read_bytes().decode("utf-8")))

    def list(self) -> tuple[Return, ...]:
        if not self.dir.is_dir():
            return ()
        out = [_from_obj(json.loads(p.read_bytes().decode("utf-8")))
               for p in sorted(self.dir.glob("*.json"))]
        return tuple(sorted(out, key=lambda r: (r.opened_at, r.id)))

    def add_answers(self, rid: str, answers: Sequence[StoredAnswer],
                    redirects: Sequence[Mapping[str, str]] = ()) -> Return:
        """Append. **An answer is never edited in place and never removed.**

        A filer who changes their mind supplies a new answer to the same question; both are on the
        record, and `answers_for` takes the LAST. Overwriting would make the earlier assertion —
        which somebody made, under their name, at an instant — disappear from the artefact that is
        supposed to say who said what.
        """
        r = self.get(rid)
        return self.put(Return(
            id=r.id, template_digest=r.template_digest, source_digests=r.source_digests,
            corpus_digest=r.corpus_digest, proposals_digest=r.proposals_digest,
            subject=r.subject, opened_at=r.opened_at, label=r.label,
            answers=r.answers + tuple(answers),
            redirects=r.redirects + tuple(dict(x) for x in redirects),
        ))


def answers_for(r: Return) -> tuple[StoredAnswer, ...]:
    """The EFFECTIVE answer per question — the last one given. The history stays in `r.answers`."""
    latest: dict[str, StoredAnswer] = {}
    for a in r.answers:
        latest[a.question_id] = a
    return tuple(latest.values())


def _safe(rid: str) -> str:
    if not rid or any(c not in "0123456789abcdef" for c in rid) or len(rid) > 64:
        raise ReturnNotFound(
            f"{rid!r} is not a return id. Ids are lowercase hex derived from the input merkle "
            "root, and a path component that is not one is refused rather than resolved."
        )
    return rid


def _from_obj(o: Mapping[str, Any]) -> Return:
    return Return(
        id=str(o["id"]), template_digest=str(o["template_digest"]),
        source_digests=tuple(str(x) for x in o.get("source_digests", ())),
        corpus_digest=str(o.get("corpus_digest", "")),
        proposals_digest=str(o.get("proposals_digest", "")),
        subject={str(k): str(v) for k, v in dict(o.get("subject", {})).items()},
        opened_at=str(o.get("opened_at", "")), label=str(o.get("label", "")),
        answers=tuple(StoredAnswer(
            question_id=str(a["question_id"]), ref=str(a["ref"]), value=str(a["value"]),
            answered_by=str(a["answered_by"]), answered_at=str(a["answered_at"]),
        ) for a in o.get("answers", ())),
        redirects=tuple({str(k): str(v) for k, v in dict(x).items()}
                        for x in o.get("redirects", ())),
    )


def registry_at(root: Path) -> Registry:
    return Registry(root / "registry")
