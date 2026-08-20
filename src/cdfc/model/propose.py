"""LAYER 2 — the model PROPOSES rule-to-field bindings AS DATA. It decides nothing.

## Where this sits, and the one thing that does not bend

    LAYER 1  DETERMINISTIC  corpus -> Provision (eId + exact span) · template -> Field
    LAYER 2  THE MODEL      proposes bindings AS DATA          <- this file
    LAYER 3  DETERMINISTIC  G-QUOTE · G-FIELD · G-TYPE · G-VOCAB · G-XREF
                            ONLY ADMITTED PROPOSALS BECOME NODES

**`cdfc.model` is in `BANNED_IN_VERDICT` and stays there.** Nothing on the verdict path imports
this module; `tests/negative/importgraph.py` walks the closure and fails the build if one does. A
proposal is an input to adjudication in exactly the way a filing is an input to a check — the model
is a *source of candidates*, never a source of verdicts.

That is not a restriction bolted onto an LLM feature. It is what makes an LLM feature safe enough to
have: the spike measured **3 of 3 planted errors caught by gates that decide without consulting the
model**, and `W0-C` measured what the alternative looks like — a similarity judgement returning
`SUPPORTED` **20 of 20** on evidence that had been DELETED.

## Why this ships now, and on what

`experiments/E6/DECISION.md` reads **`RETAIN-PROVISIONAL`** — admitted by the product owner on **no
measurement**, with the revocation condition recorded. `ci/barrier5.sh` admits that status only when
the record names who decided, states that nothing measured it, and says what revokes it.

E6's stated blocker — *"there is no statutory instrument in this repository"* — went stale on
16 Aug 2026 when `S1` pinned the IFSCA Regulations, and nobody noticed for four days.

## The transport, and why it is a base URL rather than a vendor

`base_url` is whatever speaks the Anthropic Messages API. That makes the routing a **deployment
choice**:

    ANTHROPIC_BASE_URL=http://localhost:3456   ANTHROPIC_API_KEY=dario     # a local proxy
    ANTHROPIC_BASE_URL=https://api.anthropic.com                           # direct

Nothing here knows which. **No credential is read from a file, none is logged, and none appears in
a proposal** — the key arrives as an argument or from the environment and is used once, on one
request. A proposer that persisted a token would put a subscription credential inside an artefact
this system content-addresses and hands to auditors.

## What a proposal is allowed to contain

A quote, a provision eId, a field ref, and the model's own stated reason. **Not a verdict, not a
score that anything reads, and not a value to fill** — `A5` fills, from `Observation`s that
re-verify byte-exact, and a model-supplied value would have no span to re-verify against.

`G-QUOTE` then requires the quote to occur verbatim in the cited provision, and admits only a
quote it locates there — without anybody consulting the model about how sure it was.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Final

DEFAULT_BASE_URL: Final[str] = "https://api.anthropic.com"
DEFAULT_MODEL: Final[str] = "claude-sonnet-5"
API_VERSION: Final[str] = "2023-06-01"
TIMEOUT_S: Final[float] = 120.0
MAX_TOKENS: Final[int] = 4096


class ProposerError(RuntimeError):
    """The proposer could not produce candidates. Never repaired, never defaulted to empty.

    An empty proposal set and a failed call are different facts: the first says the model found
    nothing, the second says we do not know what it would have found. Returning `()` for both
    would make a transport failure look like a clean negative result.
    """


@dataclass(frozen=True, slots=True)
class BindingProposal:
    """One candidate binding, as DATA. Carries no verdict and no admitted flag."""

    provision_eid: str
    field_ref: str
    quote: str                 # must occur VERBATIM in the provision; G-QUOTE checks it
    reason: str                # the model's own words, retained for the audit record
    model: str
    proposal_index: int

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "provision_eid": self.provision_eid, "field_ref": self.field_ref,
            "quote": self.quote, "reason": self.reason, "model": self.model,
            "proposal_index": self.proposal_index,
        }


@dataclass(frozen=True, slots=True)
class ProposalSet:
    """What one call produced, with the inputs it saw. The DENOMINATOR travels with it."""

    proposals: tuple[BindingProposal, ...]
    model: str
    provisions_offered: int
    fields_offered: int
    raw_blocks: int            # how many candidate objects the model emitted, before parsing
    malformed: tuple[str, ...] = ()

    def counts(self) -> dict[str, int]:
        return {
            "proposals": len(self.proposals),
            "raw_blocks": self.raw_blocks,
            "malformed": len(self.malformed),
            "provisions_offered": self.provisions_offered,
            "fields_offered": self.fields_offered,
        }


SYSTEM: Final[str] = (
    "You propose candidate bindings between provisions of a regulation and fields of a regulatory "
    "return. You do NOT decide anything: every proposal you make is checked by deterministic gates "
    "that do not consult you, and a wrong proposal is caught, not acted on.\n\n"
    "Rules:\n"
    "1. `quote` MUST be copied VERBATIM from the provision text you were given. Do not paraphrase, "
    "do not correct spelling, do not join across an ellipsis. Every quote is checked for a "
    "verbatim occurrence in the provision, and only a quote found there survives.\n"
    "2. `field_ref` MUST be one of the field references given to you, exactly as written.\n"
    "3. `provision_eid` MUST be one of the eIds given to you.\n"
    "4. Propose nothing when nothing fits. An empty list is a valid and useful answer.\n"
    "5. Do not propose a VALUE for any field. You are binding a rule to a field, not filling it.\n\n"
    'Reply with JSON only: {"proposals":[{"provision_eid":…,"field_ref":…,"quote":…,"reason":…}]}'
)


def _post(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "anthropic-version": API_VERSION,
            "x-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:                                   # noqa: BLE001
        # The message deliberately does not echo the key or the body.
        raise ProposerError(
            f"the proposer could not reach {url}: {type(exc).__name__}. This is NOT an empty "
            "proposal set — nothing is known about what the model would have proposed."
        ) from exc


def _call(
    payload: dict[str, Any], *, base_url: str | None, api_key: str | None, transport: Any,
) -> dict[str, Any]:
    """ONE transport, with ONE promise, shared by both LAYER 2 modes.

    Factored out when `extract.py` arrived: two modes each wrapping their own transport is two
    places for the promise to drift, and the promise — a failed call NEVER looks like a clean
    empty result — is the whole of what this function is for.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
    url = (base_url or os.environ.get("ANTHROPIC_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    if transport is None:
        if not key:
            raise ProposerError(
                "no API key. Set ANTHROPIC_API_KEY, or pass one. This module never reads a "
                "credential from a file and never stores one."
            )
        return _post(f"{url}/v1/messages", payload, key)
    try:
        return transport(payload)
    except ProposerError:
        raise
    except Exception as exc:                                   # noqa: BLE001
        raise ProposerError(
            f"the supplied transport failed: {type(exc).__name__}. This is NOT an empty result — "
            "nothing is known about what the model would have returned."
        ) from exc


def propose(
    provisions: Sequence[tuple[str, str]],
    fields: Sequence[tuple[str, str]],
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    transport: Any = None,
) -> ProposalSet:
    """Ask for candidate bindings. `provisions` is `(eId, text)`; `fields` is `(ref, label)`.

    `transport` exists so the tests exercise the parsing and the refusals without a network, and
    so a caller may substitute any client. It takes the request payload and returns the decoded
    response body.
    """
    if not provisions or not fields:
        raise ProposerError(
            f"nothing to propose over: {len(provisions)} provision(s), {len(fields)} field(s). "
            "An empty offer would make an empty result unreadable — it would not distinguish "
            "'the model proposed nothing' from 'the model was shown nothing'."
        )
    body = "\n".join(
        ["PROVISIONS:"]
        + [f"[{eid}] {text[:1200]}" for eid, text in provisions]
        + ["", "FIELDS:"]
        + [f"[{ref}] {label[:200]}" for ref, label in fields]
    )
    payload = {
        "model": model, "max_tokens": MAX_TOKENS, "system": SYSTEM,
        "messages": [{"role": "user", "content": body}],
    }
    data = _call(payload, base_url=base_url, api_key=api_key, transport=transport)
    text = "".join(
        b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return parse(text, model=model, provisions=provisions, fields=fields)


def parse(
    text: str, *, model: str,
    provisions: Sequence[tuple[str, str]], fields: Sequence[tuple[str, str]],
) -> ProposalSet:
    """Parse a reply into proposals, REFUSING every one that does not reference what it was shown.

    This is not the gate layer — `G-QUOTE` and `G-FIELD` still run afterwards and are what decide.
    It is the narrower job of refusing a proposal that is not even ABOUT the inputs: an eId or a
    field ref the model invented cannot be adjudicated, only discarded, and discarding it silently
    would let a hallucinated address vanish from the denominator.
    """
    eids = {e for e, _t in provisions}
    refs = {r for r, _l in fields}
    body = text.strip()
    if body.startswith("```"):
        body = body.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        obj = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ProposerError(
            f"the model's reply is not JSON ({exc.msg}). Returning zero proposals here would "
            "report a parse failure as a clean negative result."
        ) from exc

    raw = obj.get("proposals", []) if isinstance(obj, dict) else []
    out: list[BindingProposal] = []
    malformed: list[str] = []
    for i, p in enumerate(raw):
        if not isinstance(p, dict):
            malformed.append(f"#{i}: not an object")
            continue
        eid, ref = str(p.get("provision_eid", "")), str(p.get("field_ref", ""))
        quote, reason = str(p.get("quote", "")), str(p.get("reason", ""))
        if eid not in eids:
            malformed.append(f"#{i}: provision_eid {eid!r} was not offered")
            continue
        if ref not in refs:
            malformed.append(f"#{i}: field_ref {ref!r} was not offered")
            continue
        if not quote.strip():
            malformed.append(f"#{i}: empty quote; G-QUOTE has nothing to locate")
            continue
        out.append(BindingProposal(provision_eid=eid, field_ref=ref, quote=quote, reason=reason,
                                   model=model, proposal_index=i))
    return ProposalSet(
        proposals=tuple(out), model=model, provisions_offered=len(provisions),
        fields_offered=len(fields), raw_blocks=len(raw), malformed=tuple(malformed),
    )
