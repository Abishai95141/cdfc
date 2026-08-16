"""P14-B3 — the API cannot express a pass, asserted over the GENERATED document.

Every walk here is over `openapi_document()`, never over a hand-written list of models. A model
added without touching this file is still scanned, which is the only version of this check that
survives the next person adding an endpoint in a hurry.
"""

from __future__ import annotations

import pytest

from cdfc.api.openapi import openapi_document
from cdfc.api.routes import MUTATING, ROUTES
from cdfc.api.schemas import (
    BANNED_PROPERTY_NAMES,
    PERMITTED_BOOLEANS,
    DenominatorOut,
    FractionTravelsAlone,
    SettledFractionOut,
)

# The recursive keys a JSON Schema can hide a property under. NC-A01's walker, reused: a check
# that only looked at `properties` would miss `$defs`, and a `status` inside an `anyOf` reaches a
# client exactly as well as one at the top level.
NESTING_KEYS = (
    "properties", "$defs", "definitions", "allOf", "anyOf", "oneOf", "not", "items",
    "prefixItems", "patternProperties", "additionalProperties", "propertyNames", "components",
    "schemas", "paths", "responses", "content", "schema",
)


def _walk_properties(node, path="$"):
    """Yield `(json_path, property_name, subschema)` for every property at any depth."""
    if isinstance(node, dict):
        for name, sub in (node.get("properties") or {}).items():
            yield f"{path}.properties.{name}", name, sub
        for key in NESTING_KEYS:
            if key not in node:
                continue
            child = node[key]
            if isinstance(child, dict):
                for k, v in child.items():
                    yield from _walk_properties(v, f"{path}.{key}.{k}")
                yield from _walk_properties(child, f"{path}.{key}")
            elif isinstance(child, list):
                for i, v in enumerate(child):
                    yield from _walk_properties(v, f"{path}.{key}[{i}]")


def test_contract__no_banned_property_at_any_depth() -> None:
    doc = openapi_document()
    hits = [
        (p, n) for p, n, _ in _walk_properties(doc)
        if n.lower() in {b.lower() for b in BANNED_PROPERTY_NAMES}
    ]
    assert not hits, (
        f"a property whose NAME means the filing passed reaches a client: {hits}. "
        "This product's whole claim is that it reports what it did not check; a `status` field is "
        "how that claim is lost in an integration nobody reviewed."
    )


def test_contract__every_boolean_is_on_the_permitted_list() -> None:
    """A blanket no-booleans rule would be wrong; an unbounded allowlist would be no rule."""
    doc = openapi_document()
    booleans = {n for _, n, sub in _walk_properties(doc)
                if isinstance(sub, dict) and sub.get("type") == "boolean"}
    assert booleans <= PERMITTED_BOOLEANS, (
        f"{sorted(booleans - PERMITTED_BOOLEANS)} are booleans on the wire and not on the "
        "permitted list. Exactly five are permitted and a sixth requires a DoD line."
    )


def test_contract__fraction_never_travels_alone() -> None:
    """Constructing the model with a fraction and no denominator RAISES. Schema, not renderer."""
    with pytest.raises(FractionTravelsAlone):
        SettledFractionOut(
            denominator=DenominatorOut("v3", 3747), outOfScope=0, informational=0, inScope=3747,
            settled=1898, unsettled=0, notChecked=1849,
            denominatorWarning="", admissionState="PRE-GATE", fraction=0.5065,
        )
    with pytest.raises(FractionTravelsAlone):
        SettledFractionOut(
            denominator=DenominatorOut("v3", 3747), outOfScope=0, informational=0, inScope=3747,
            settled=1898, unsettled=0, notChecked=1849,
            denominatorWarning="PROVISIONAL-UNVALIDATED", admissionState="", fraction=0.5065,
        )


def test_contract__the_six_counts_make_a_fraction_constructible() -> None:
    """The admission-side twin. Without it, a model that refused everything would score perfectly."""
    ok = SettledFractionOut(
        denominator=DenominatorOut("v3", 3747), outOfScope=0, informational=0, inScope=3747,
        settled=1898, unsettled=0, notChecked=1849,
        denominatorWarning="PROVISIONAL-UNVALIDATED: the mask has never been checked against a "
                           "person filling the form in",
        admissionState="PRE-GATE", fraction=0.5065,
    )
    assert ok.fraction == 0.5065


def test_contract__every_object_forbids_extra_properties() -> None:
    """`additionalProperties: False` everywhere, so a consumer cannot write a `status` in either."""
    doc = openapi_document()
    offenders = [
        name for name, sub in doc["$defs"].items()
        if sub.get("additionalProperties") is not False
    ]
    assert not offenders, f"{offenders} admit extra properties"


def test_contract__mutating_paths_require_a_token() -> None:
    """TABLE-DRIVEN over the route table, never over a hand-written list.

    A new mutating path added without a token must fail the build. It can only do that if this
    test reads the same object the dispatcher does.
    """
    doc = openapi_document()
    for route in MUTATING:
        op = doc["paths"][route.path][route.method.lower()]
        assert op.get("security") == [{"operatorToken": []}], (
            f"{route.method} {route.path} is declared mutating and its OpenAPI operation carries "
            "no security requirement"
        )
        assert "401" in op["responses"] and "503" in op["responses"]


def test_contract__the_route_table_is_the_only_source_of_paths() -> None:
    doc = openapi_document()
    assert set(doc["paths"]) == {r.path for r in ROUTES}
    assert len(ROUTES) >= 18, "plan/07 §III.6 fixes ~18 paths"
