"""P4-B1 — YAML → `Candidate` | `Predicate`, with the loader invariant.

**The loader invariant, as the spec states it: a predicate row with no qualification row does not
load.** It is enforced twice on purpose — once by the type (`evaluate_one(p: Predicate, ...)` will
not accept a `Candidate`) and once here at runtime. The post-hoc check is redundant and is kept for
the same reason the L2b post-hoc key guard is kept: **it is the one you can prove to a reviewer.**

`load_candidate` is used ONLY by `cdfc.qualify`. `load_predicate` is the run path, and it raises
`UnqualifiedPredicateError` on a candidate — naming the file and the missing key, because an error
that does not say which file it read sends a reviewer to grep.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from cdfc.predicates.envelope import (
    Candidate,
    Clause,
    EnvelopeSchemaError,
    ExternalDep,
    Predicate,
    Proviso,
    Qualification,
    QualifiedAgainst,
    Tolerance,
)
from cdfc.predicates.schema_build import build_schema
from cdfc.predicates.validate import SchemaViolation, validate

__all__ = [
    "UnqualifiedPredicateError",
    "EnvelopeSchemaError",
    "load_candidate",
    "load_predicate",
    "dump",
    "PREDICATE_KEYS",
]


class UnqualifiedPredicateError(Exception):
    """A predicate envelope with no qualification record. It does not load. Ever."""


# The five keys that separate a Predicate from a Candidate. Named once, read by the loader and
# by the error message, so the message can never name a key the check does not look at.
PREDICATE_KEYS: tuple[str, ...] = (
    "qualification",
    "qualified_against",
    "severity_tier",
    "state",
)


def _read(src: Path | Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    if isinstance(src, Mapping):
        return dict(src), "<mapping>"
    text = Path(src).read_text(encoding="utf-8")
    obj = yaml.safe_load(text)
    if not isinstance(obj, dict):
        raise EnvelopeSchemaError(f"{src}: an envelope file must contain one mapping")
    return obj, str(src)


def _span(v: Any, where: str) -> tuple[int, int]:
    if not (isinstance(v, (list, tuple)) and len(v) == 2):
        raise EnvelopeSchemaError(f"{where}: a span is two integers")
    return (int(v[0]), int(v[1]))


def _clause(v: Any, where: str) -> Clause | None:
    if v is None:
        return None
    return Clause(
        instrument=v["instrument"],
        eId=v["eId"],
        span=_span(v["span"], f"{where}.clause"),
        quote=v["quote"],
        provisos=tuple(
            Proviso(
                text=p["text"],
                disposal=p["disposal"],
                emits=p.get("emits"),
                span=_span(p["span"], f"{where}.clause.provisos"),
            )
            for p in v.get("provisos", ())
        ),
    )


def _common(raw: Mapping[str, Any], where: str) -> dict[str, Any]:
    tol = raw.get("tolerance")
    return {
        "id": raw["id"],
        "version": raw["version"],
        "kind": raw["kind"],
        "template": raw["template"],
        "schema_keys": tuple(raw["schema_keys"]),
        "host_fns": tuple(raw.get("host_fns") or ()),
        "obligation_id": raw["obligation_id"],
        "obligation_source": raw["obligation_source"],
        "clause": _clause(raw.get("clause"), where),
        "rationale": raw["rationale"],
        "clause_absent_reason": raw.get("clause_absent_reason"),
        "claims_fault_classes": tuple(raw["claims_fault_classes"]),
        "applicable": raw["applicable"],
        "expr": raw["expr"],
        "witness": raw["witness"],
        "reason_if_inapplicable": raw["reason_if_inapplicable"],
        "tolerance": None if tol is None else Tolerance(tau_units_per_summand=tol["tau_units_per_summand"]),
        "external_deps": tuple(
            ExternalDep(
                endpoint=d["endpoint"], field=d["field"], snapshot=d["snapshot"], on_missing=d["on_missing"]
            )
            for d in raw.get("external_deps") or ()
        ),
    }


def _validate_against_schema(raw: Mapping[str, Any], where: str) -> None:
    try:
        validate(raw, build_schema())
    except SchemaViolation as e:
        raise EnvelopeSchemaError(f"{where}: {e}") from e


def load_candidate(src: Path | Mapping[str, Any]) -> Candidate:
    """Load an envelope as a candidate. Used ONLY by `cdfc.qualify`.

    A candidate with a qualification block is refused: qualification is written by the pipeline,
    and an envelope that arrives already carrying one has skipped the gates it claims to have
    passed.
    """
    raw, where = _read(src)
    present = [k for k in PREDICATE_KEYS if k in raw]
    if present:
        raise EnvelopeSchemaError(
            f"{where}: a candidate carries {present}, which only the qualification pipeline "
            "writes. An envelope that arrives already qualified has skipped the gates."
        )
    _validate_against_schema(raw, where)
    return Candidate(**_common(raw, where))


def load_predicate(src: Path | Mapping[str, Any]) -> Predicate:
    """Load an envelope as a predicate. The run path. Raises on an unqualified envelope."""
    raw, where = _read(src)
    missing = [k for k in PREDICATE_KEYS if raw.get(k) is None]
    if missing:
        raise UnqualifiedPredicateError(
            f"{where}: predicate {raw.get('id', '<no id>')!r} does not load — missing "
            f"{missing}. A predicate whose error rate is unknown is not admitted, which is "
            "what makes the settled-fraction claim true by construction rather than by "
            "discipline."
        )
    _validate_against_schema(raw, where)
    q = raw["qualification"]
    qa = raw["qualified_against"]
    return Predicate(
        **_common(raw, where),
        qualification=Qualification(
            campaign_id=q["campaign_id"],
            kill_rate_claimed=q["kill_rate_claimed"],
            kill_rate_all_classes=q["kill_rate_all_classes"],
            false_failure_rate=q["false_failure_rate"],
            qualified_at=q["qualified_at"],
        ),
        qualified_against=QualifiedAgainst(
            evaluator_version=qa["evaluator_version"],
            fault_model_version=qa["fault_model_version"],
            corpus_sha256=qa["corpus_sha256"],
            template_sha256=qa["template_sha256"],
        ),
        severity_tier=raw["severity_tier"],
        state=raw["state"],
        withdrawn_reason=raw.get("withdrawn_reason"),
    )


def dump(c: Candidate | Predicate) -> dict[str, Any]:
    """The envelope as a plain mapping — the same projection the digest covers.

    Deliberately the projection and not a second serialiser: `dump(load(x))` must re-canonicalise
    to identical bytes, and two serialisers cannot be made to agree by testing.
    """
    from cdfc.predicates.canonical import envelope_projection

    obj = envelope_projection(c)
    obj.pop("__envelope_type__", None)
    return obj
