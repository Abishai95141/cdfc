"""P4-B1 — the predicate JSON Schema, GENERATED from the record.

**The schema is not hand-written.** A hand-written schema and a dataclass are two declarations
of one shape, and the divergence is silent in the direction that matters: a field the record
requires and the schema does not is a field a YAML author may omit.

`fixtures/predicates/predicate.schema.json` is the generated schema, committed, and
`test_contract__committed_schema_matches_the_generated_one` asserts equality. Changing the record
without regenerating fails the build.

`additionalProperties: false` is emitted at every object depth — including inside
`clause.provisos[]`, which is the depth a hand-written schema forgets.
"""

from __future__ import annotations

import types
import typing
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Final, Literal, get_args, get_origin

from cdfc.predicates import envelope as _env

SCHEMA_ID: Final[str] = "https://cdfc.invalid/schema/predicate.schema.json"
SCHEMA_DIALECT: Final[str] = "https://json-schema.org/draft/2020-12/schema"

# Fields whose absence from the YAML is admissible because the record supplies a default that
# is itself lawful (an empty tuple is a real value: "this predicate has no external deps").
# Everything else is required. The list is explicit so that adding a default to the record does
# not quietly make a field optional in the schema.
_OPTIONAL_BY_DESIGN: Final[frozenset[str]] = frozenset({"external_deps", "provisos"})


class SchemaBuildError(TypeError):
    pass


def _unwrap_optional(tp: Any) -> tuple[Any, bool]:
    """`X | None` -> (X, True). Anything else -> (tp, False)."""
    origin = get_origin(tp)
    if origin in (typing.Union, types.UnionType):
        args = [a for a in get_args(tp) if a is not type(None)]
        if len(args) == 1:
            return args[0], True
        raise SchemaBuildError(f"only `X | None` unions are admissible in an envelope: {tp!r}")
    return tp, False


def _schema_for(tp: Any) -> dict[str, Any]:
    tp, nullable = _unwrap_optional(tp)
    origin = get_origin(tp)

    if origin is Literal:
        node: dict[str, Any] = {"enum": sorted(get_args(tp))}
    elif tp is str:
        node = {"type": "string"}
    elif tp is bool:
        node = {"type": "boolean"}
    elif tp is int:
        node = {"type": "integer"}
    elif origin in (tuple, list):
        args = get_args(tp)
        if len(args) == 2 and args[1] is Ellipsis:
            node = {"type": "array", "items": _schema_for(args[0])}
        elif args and all(a is int for a in args):
            # tuple[int, int] — a span. Fixed length, and the length is the point.
            node = {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": len(args),
                "maxItems": len(args),
            }
        else:
            raise SchemaBuildError(f"unsupported sequence type in an envelope: {tp!r}")
    elif is_dataclass(tp):
        node = object_schema(tp)
    else:
        raise SchemaBuildError(f"no JSON Schema mapping for {tp!r}")

    if nullable:
        if "enum" in node:
            node = {"enum": [*node["enum"], None]}
        elif "type" in node:
            node = {**node, "type": [node["type"], "null"]}
        else:
            node = {"anyOf": [node, {"type": "null"}]}
    return node


def object_schema(cls: type) -> dict[str, Any]:
    hints = typing.get_type_hints(cls)
    props: dict[str, Any] = {}
    required: list[str] = []
    for f in fields(cls):
        props[f.name] = _schema_for(hints[f.name])
        has_default = f.default is not MISSING or f.default_factory is not MISSING  # type: ignore[misc]
        if not has_default or f.name not in _OPTIONAL_BY_DESIGN:
            required.append(f.name)
    return {
        "type": "object",
        "additionalProperties": False,  # at EVERY depth, including provisos[]
        "properties": props,
        "required": sorted(required),
    }


def build_schema() -> dict[str, Any]:
    """The committed schema: a candidate envelope, or a predicate envelope, and nothing else."""
    return {
        "$schema": SCHEMA_DIALECT,
        "$id": SCHEMA_ID,
        "title": "cdfc predicate envelope",
        "description": (
            "GENERATED from src/cdfc/predicates/envelope.py. Do not hand-edit: "
            "tests/contract/test_contract__predicate_schema.py asserts this file equals the "
            "generated schema, so an edit here without a change to the record fails the build. "
            "There is deliberately no result, status or pass property at any depth."
        ),
        "oneOf": [{"$ref": "#/$defs/Candidate"}, {"$ref": "#/$defs/Predicate"}],
        "$defs": {
            "Candidate": object_schema(_env.Candidate),
            "Predicate": object_schema(_env.Predicate),
        },
    }
