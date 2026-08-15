"""The recursive schema walker (methodology §1.9) — and the three-part rule it implements.

**The prohibition is on a PROPERTY NAME at any depth, and it has to be precise in both directions.**

`plan/05` P11-B1 states the problem exactly: **the specification's own payload contains
`canariesPassed`.** A substring matcher rejects the specification. An exact matcher admits
`overallStatus`. Neither is acceptable, so the rule has three parts and only the first one blocks:

1. **Exact, case-insensitive match on the property name** is the **blocking** gate.
2. **A substring scan over every property name is ADVISORY and prints its hits** on every run, so
   `overallStatus` cannot arrive unseen.
3. **Every advisory hit must appear in `NAME-ALLOWLIST.md` with a written argument, or the build
   fails.** An allowlist entry without an argument is refused by the loader — the same rule as
   `docs/EQUIVALENT-MUTANTS.md`, and for the same reason.

**The descent has to be total or it is decorative.** NC-A01's injector plants `status` inside a
`$defs` entry referenced from an `allOf` two levels down; a walker that only reads top-level
`properties` finds nothing and reports success. So it descends `properties`, `$defs`,
`definitions`, `allOf`, `anyOf`, `oneOf`, `not`, `items`, `prefixItems`, `patternProperties`,
`additionalProperties` and `propertyNames`, and `test_walk__descends_every_combinator` plants a
banned name under each one in turn and asserts every plant is found.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Final

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "src" / "cdfc" / "attest" / "schema" / "attestation.schema.json"
ALLOWLIST = REPO / "src" / "cdfc" / "attest" / "schema" / "NAME-ALLOWLIST.md"

# Part 1: the BLOCKING set. Exact, case-insensitive.
BANNED_EXACT: Final[frozenset[str]] = frozenset({
    "result", "status", "pass", "passed", "passing",
    "compliant", "conformant", "ok", "success", "clean",
})

# Part 2: the ADVISORY set. Substring, case-insensitive. Its hits do not block; they must be
# allowlisted with an argument.
ADVISORY_SUBSTRINGS: Final[tuple[str, ...]] = tuple(sorted(BANNED_EXACT))

# Every keyword whose value may contain a subschema. A walker that misses one is a walker a
# banned name can hide behind.
SUBSCHEMA_KEYWORDS: Final[tuple[str, ...]] = (
    "$defs", "definitions", "properties", "patternProperties", "dependentSchemas",
)
SUBSCHEMA_LISTS: Final[tuple[str, ...]] = ("allOf", "anyOf", "oneOf", "prefixItems")
SUBSCHEMA_VALUES: Final[tuple[str, ...]] = (
    "not", "items", "additionalProperties", "propertyNames", "contains",
    "if", "then", "else", "unevaluatedProperties", "unevaluatedItems",
)


def load() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def property_names(schema: Mapping[str, Any], path: str = "$") -> Iterator[tuple[str, str]]:
    """Every property name the schema declares, with the JSON path it sits at.

    Yields `(name, path)`. **`$defs` keys are NOT property names** — they are schema identifiers,
    and a definition called `status` that nothing references declares no property. The walker
    descends into them and reports the names they declare, which is the thing that matters.
    """
    if not isinstance(schema, Mapping):
        return
    for kw in ("properties", "patternProperties", "dependentSchemas"):
        for name, sub in (schema.get(kw) or {}).items():
            if kw == "properties":
                yield str(name), f"{path}.{kw}.{name}"
            yield from property_names(sub, f"{path}.{kw}.{name}")
    for kw in ("$defs", "definitions"):
        for name, sub in (schema.get(kw) or {}).items():
            yield from property_names(sub, f"{path}.{kw}.{name}")
    for kw in SUBSCHEMA_LISTS:
        for i, sub in enumerate(schema.get(kw) or []):
            yield from property_names(sub, f"{path}.{kw}[{i}]")
    for kw in SUBSCHEMA_VALUES:
        sub = schema.get(kw)
        if isinstance(sub, Mapping):
            yield from property_names(sub, f"{path}.{kw}")


def blocking_hits(schema: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Part 1. Exact, case-insensitive. **These fail the build.**"""
    return [(n, p) for n, p in property_names(schema) if n.lower() in BANNED_EXACT]


def advisory_hits(schema: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Part 2. Substring, case-insensitive. **These print, and must be allowlisted.**"""
    out = []
    for name, path in property_names(schema):
        low = name.lower()
        if low in BANNED_EXACT:
            continue                       # already blocking; not an advisory hit
        if any(s in low for s in ADVISORY_SUBSTRINGS):
            out.append((name, path))
    return out


def object_schemas(schema: Mapping[str, Any], path: str = "$") -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Every subschema that declares `properties` — i.e. every object schema, at any depth."""
    if not isinstance(schema, Mapping):
        return
    if "properties" in schema:
        yield path, schema
    for kw in ("properties", "patternProperties", "dependentSchemas", "$defs", "definitions"):
        for name, sub in (schema.get(kw) or {}).items():
            yield from object_schemas(sub, f"{path}.{kw}.{name}")
    for kw in SUBSCHEMA_LISTS:
        for i, sub in enumerate(schema.get(kw) or []):
            yield from object_schemas(sub, f"{path}.{kw}[{i}]")
    for kw in SUBSCHEMA_VALUES:
        sub = schema.get(kw)
        if isinstance(sub, Mapping):
            yield from object_schemas(sub, f"{path}.{kw}")


_ENTRY = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$", re.M)


def allowlist() -> dict[str, str]:
    """`{property name: argument}` from `NAME-ALLOWLIST.md`. **An entry with no argument raises.**"""
    if not ALLOWLIST.is_file():
        raise FileNotFoundError(
            f"{ALLOWLIST} does not exist, so every advisory hit is unexplained. An advisory scan "
            "whose hits nobody has to justify is a scan whose output nobody reads."
        )
    out: dict[str, str] = {}
    for name, argument in _ENTRY.findall(ALLOWLIST.read_text(encoding="utf-8")):
        if len(argument.strip()) < 40:
            raise ValueError(
                f"{name!r} is allowlisted with an argument of {len(argument.strip())} characters. "
                "An allowlist entry without an argument is a name somebody waved through — the "
                "same rule as docs/EQUIVALENT-MUTANTS.md."
            )
        out[name] = argument.strip()
    return out
