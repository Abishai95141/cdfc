"""Provider adapters for LAYER 2. **A transport, never a change to the promise.**

`propose()` and `extract()` both take a `transport` argument, documented *"so a caller may
substitute any client"*. This module supplies those clients. It exists because the alternative —
teaching `_call` about every provider — puts provider branching inside the one function whose
single promise is that **a failed call never looks like a clean empty result**, and that promise is
the reason the module is trustworthy.

## The shape a transport must honour

It receives the Anthropic-style payload `propose()` builds:

    {"model": str, "max_tokens": int, "system": str, "messages": [{"role", "content"}]}

and must return an Anthropic-style body, because that is what the caller reads:

    {"content": [{"type": "text", "text": "..."}]}

Anything else is a lie about what the model said. A transport that returns `{}` on an error would
be indistinguishable from a model that replied with nothing, which is exactly the failure
`ProposerError` exists to prevent — so every adapter here **raises** rather than degrading.

## Why this is not in the verdict closure

`cdfc.model` is in `BANNED_IN_VERDICT` **as a package**, so nothing here can reach a verdict root
however it is written. The model's output arrives at the system as a FILE that
`cdfc.evidence.run(proposals=...)` reads; no verdict-path code ever calls a provider.

## Credentials

Read from the environment, never from a file, never written to one, never echoed in an error.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Callable
from typing import Any, Final

from cdfc.model.propose import ProposerError

DEEPSEEK_BASE: Final[str] = "https://api.deepseek.com"
DEEPSEEK_MODEL: Final[str] = "deepseek-v4-flash"
TIMEOUT_S: Final[int] = 300

MIN_MAX_TOKENS: Final[int] = 32_768
"""A FLOOR on `max_tokens`, because `deepseek-v4-flash` is a REASONING model.

Measured 20 Aug 2026 on a 1,539-token prompt: `completion_tokens` 4,096 of which
**`reasoning_tokens` 4,060** — the model spent 99 percent of the caller's 4,096-token budget
thinking, emitted 114 characters, and stopped with `finish_reason: "length"` in the middle of a
JSON string.

The caller's `MAX_TOKENS` is 4,096 because that is a sane ceiling for an ANSWER. Here it is not
the answer's budget, it is the answer's budget PLUS the reasoning, so passing it through produces
a truncated reply on every call. A truncated reply is not a model that proposed nothing —
`parse()` correctly raised `ProposerError` on all three batches rather than reporting zero — but a
transport that guarantees truncation is a broken transport, not a strict one.

Raised here, in the adapter, rather than in `propose()`: this is a fact about one provider, and
`MAX_TOKENS` is a fact about the protocol.
"""


def _http_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", **headers}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def deepseek(*, model: str = DEEPSEEK_MODEL, api_key: str | None = None,
             base_url: str = DEEPSEEK_BASE) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """An OpenAI-compatible transport for DeepSeek, adapting BOTH directions.

    DeepSeek speaks the OpenAI chat schema: `system` is a message with `role="system"` rather than
    a top-level field, and the reply is `choices[0].message.content` rather than a `content` list.
    The adaptation is done here, in one place, so neither `propose()` nor `parse()` learns that a
    second provider exists.

    `response_format={"type": "json_object"}` is requested because `parse()` refuses a non-JSON
    reply outright — asking for JSON at the API level turns a common, recoverable formatting slip
    into a non-event rather than a `ProposerError`.
    """
    key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise ProposerError(
            "no DeepSeek API key. Set DEEPSEEK_API_KEY, or pass one. This module never reads a "
            "credential from a file and never stores one."
        )

    def _transport(payload: dict[str, Any]) -> dict[str, Any]:
        messages = []
        if payload.get("system"):
            messages.append({"role": "system", "content": payload["system"]})
        messages.extend(payload.get("messages", []))
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max(int(payload.get("max_tokens", 4096)), MIN_MAX_TOKENS),
            "temperature": 0,          # a proposal set that changes between runs is not evidence
            "response_format": {"type": "json_object"},
        }
        try:
            data = _http_json(f"{base_url.rstrip('/')}/chat/completions", body,
                              {"Authorization": f"Bearer {key}"})
        except Exception as exc:                                   # noqa: BLE001
            # Deliberately does not echo the key or the request body.
            raise ProposerError(
                f"the DeepSeek transport could not reach {base_url}: {type(exc).__name__}. This "
                "is NOT an empty proposal set — nothing is known about what the model would have "
                "proposed."
            ) from exc

        choices = data.get("choices") or []
        if not choices:
            raise ProposerError(
                f"DeepSeek returned no choices (keys: {sorted(data)}). Returning an empty reply "
                "here would report a transport fault as a model that proposed nothing."
            )
        # A TRUNCATED REPLY IS A FAULT, NOT A SHORT ANSWER. Without this the caller sees a
        # JSONDecodeError and reports "the model's reply is not JSON", which names the symptom and
        # hides the cause — the budget — and sent three batches to the same death before anyone
        # looked at finish_reason.
        finish = choices[0].get("finish_reason")
        if finish == "length":
            u = data.get("usage") or {}
            raise ProposerError(
                f"DeepSeek stopped at the token ceiling (finish_reason='length'; "
                f"completion={u.get('completion_tokens')}, "
                f"reasoning={(u.get('completion_tokens_details') or {}).get('reasoning_tokens')}). "
                f"The reply is TRUNCATED, not short: parsing it would silently drop every proposal "
                f"after the cut. Raise max_tokens above {MIN_MAX_TOKENS}."
            )
        text = (choices[0].get("message") or {}).get("content") or ""
        # Back into the shape the caller reads. One key, one type, no invention.
        return {"content": [{"type": "text", "text": text}]}

    return _transport
