"""P4-B1 — a strict, closed JSON Schema validator for the envelope, and nothing more.

**Why not `jsonschema`.** The envelope schema is generated, closed and finite: no `$ref` cycles,
no `format`, no regex, no `patternProperties`. The full library's surface is mostly machinery this
schema never uses, and it would sit in the import closure of the verdict path. So the checker is
~90 lines, it is exercised by every fixture and by four negative controls, **and it is
differentially checked against `jsonschema` in `tests/differential/test_diff__envelope_schema.py`
on a corpus of good and broken envelopes** — because a hand-rolled validator that is silently
permissive is exactly this project's own failure mode.

`jsonschema` is a TEST dependency for that differential. It is not imported here and it is not in
the runtime set declared to `ci/licence-denylist.sh`.
"""

from __future__ import annotations

from typing import Any

__all__ = ["SchemaViolation", "validate"]


class SchemaViolation(ValueError):
    """The instance does not satisfy the schema. The message names the JSON pointer."""

    def __init__(self, pointer: str, message: str) -> None:
        self.pointer = pointer or "/"
        super().__init__(f"{self.pointer}: {message}")


def _types_ok(value: Any, want: str) -> bool:
    if want == "null":
        return value is None
    if want == "boolean":
        return isinstance(value, bool)
    if want == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if want == "string":
        return isinstance(value, str)
    if want == "array":
        return isinstance(value, (list, tuple))
    if want == "object":
        return isinstance(value, dict)
    raise SchemaViolation("", f"the schema names an unsupported type {want!r}")


def _resolve(schema: dict[str, Any], root: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if ref is None:
        return schema
    if not ref.startswith("#/"):
        raise SchemaViolation("", f"only local refs are admissible, got {ref!r}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def _check(value: Any, schema: dict[str, Any], root: dict[str, Any], ptr: str) -> None:
    schema = _resolve(schema, root)

    if "oneOf" in schema:
        errors = []
        matched = 0
        for i, sub in enumerate(schema["oneOf"]):
            try:
                _check(value, sub, root, ptr)
                matched += 1
            except SchemaViolation as e:
                errors.append(f"[{i}] {e}")
        if matched != 1:
            raise SchemaViolation(
                ptr, f"matched {matched} of {len(schema['oneOf'])} alternatives; " + " | ".join(errors)
            )
        return

    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            try:
                _check(value, sub, root, ptr)
                return
            except SchemaViolation:
                continue
        raise SchemaViolation(ptr, "matched none of the admissible alternatives")

    if "enum" in schema:
        # `True == 1` in Python but not in JSON, so equality alone would admit `true` where the
        # enum lists `1`. The type is compared before the value.
        if not any(
            isinstance(value, bool) == isinstance(m, bool) and value == m for m in schema["enum"]
        ):
            raise SchemaViolation(ptr, f"{value!r} is not one of {schema['enum']!r}")
        return

    if "type" in schema:
        wanted = schema["type"]
        wanted = wanted if isinstance(wanted, list) else [wanted]
        if not any(_types_ok(value, w) for w in wanted):
            raise SchemaViolation(ptr, f"expected {'|'.join(wanted)}, got {type(value).__name__}")

    if isinstance(value, dict) and "properties" in schema:
        props = schema["properties"]
        if schema.get("additionalProperties", True) is False:
            extra = sorted(set(value) - set(props))
            if extra:
                raise SchemaViolation(
                    ptr,
                    f"unknown field(s) {extra}. The envelope is a closed record: a field nobody "
                    "declared is a field no gate reads and no digest covers.",
                )
        for name in schema.get("required", ()):
            if name not in value:
                raise SchemaViolation(f"{ptr}/{name}", "required field is missing")
        for name, sub in props.items():
            if name in value:
                _check(value[name], sub, root, f"{ptr}/{name}")

    if isinstance(value, (list, tuple)) and "items" in schema:
        if "minItems" in schema and len(value) < schema["minItems"]:
            raise SchemaViolation(ptr, f"expected at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise SchemaViolation(ptr, f"expected at most {schema['maxItems']} items")
        for i, item in enumerate(value):
            _check(item, schema["items"], root, f"{ptr}/{i}")


def validate(instance: Any, schema: dict[str, Any]) -> None:
    """Raise `SchemaViolation` unless `instance` satisfies `schema`. Never repairs, never coerces."""
    _check(instance, schema, schema, "")
