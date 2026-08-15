"""P11-B1 — **the phase's centre of gravity.**

The attestation cannot express a pass, and that is a property of the schema rather than of whoever
last edited a renderer. Everything here is a walk over the schema document itself.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from tests.contract import schema_walk as W  # noqa: E402

SCHEMA = W.load()

# `if` / `then` / `else` subschemas are CONSTRAINTS, not object definitions. An
# `additionalProperties: false` inside one would forbid every property the branch does not itself
# mention — so the INVALID branch, which names only `settledFraction` and `verdict`, would reject a
# statement carrying `scope`. That is the opposite of a constraint, and it is why the requirement
# below is scoped to definitions.
CONSTRAINT_PATHS = (".if", ".then", ".else")


def test_contract__attestation_cannot_express_a_pass() -> None:
    """NC-A01. **The blocking rule**: no `result`, `status`, `pass`… at any depth.

    Not a naming preference. A surface that can render an all-clear will eventually render it
    wrongly, and prohibiting it in the schema is the only version of that commitment that is a
    system property.
    """
    hits = W.blocking_hits(SCHEMA)
    assert hits == [], f"the schema declares a banned property name: {hits}"
    assert len(list(W.property_names(SCHEMA))) > 50, (
        "the walk found almost no property names — it is descending nothing, and a walk that "
        "scans nothing reports success"
    )


def test_contract__banned_names_are_exact_not_substrings() -> None:
    """`canariesPassed` validates; a property literally named `passed` does not.

    A substring matcher rejects the specification's own payload. An exact matcher admits
    `overallStatus`. The rule needs both halves, and this asserts the boundary between them.
    """
    names = {n for n, _p in W.property_names(SCHEMA)}
    assert "canariesPassed" in names, "the spec's own liveness payload is missing from the schema"
    assert not (names & W.BANNED_EXACT), "an exactly-banned name reached the schema"

    planted = copy.deepcopy(SCHEMA)
    planted["$defs"]["livenessProof"]["properties"]["passed"] = {"type": "integer"}
    assert ("passed", "$.$defs.livenessProof.properties.passed") in W.blocking_hits(planted), (
        "a property literally named `passed` was not caught — the exact matcher is not matching"
    )
    assert W.blocking_hits(SCHEMA) == [], "and the real schema is still clean"


def test_contract__every_advisory_hit_is_allowlisted_with_an_argument() -> None:
    """**Equal in both directions**, and the second direction is the one people forget.

    A hit that is not allowlisted is a name nobody justified. An allowlist entry that is no longer
    a hit is a permission left lying around, and the next name that matches it inherits the
    argument.
    """
    hits = {n for n, _p in W.advisory_hits(SCHEMA)}
    allowed = W.allowlist()
    assert hits == set(allowed), (
        f"advisory hits and the allowlist disagree. Unjustified: {sorted(hits - set(allowed))}. "
        f"Stale permissions: {sorted(set(allowed) - hits)}."
    )
    for name, argument in allowed.items():
        assert len(argument) >= 40, f"{name}: an entry without an argument is a name waved through"
        assert "instrument" in argument.lower() or "ours" in argument.lower() or "our own" in argument.lower(), (
            f"{name}: the argument must say the thing that passed is OURS. A property may be named "
            "for something that passed only when the thing that passed is the instrument."
        )


def test_contract__the_advisory_scan_prints_its_hits() -> None:
    """It exists so `overallStatus` cannot arrive unseen, which requires it to be visible."""
    hits = W.advisory_hits(SCHEMA)
    assert hits, "the advisory scan found nothing at all — verify it is scanning"
    planted = copy.deepcopy(SCHEMA)
    planted["$defs"]["scope"]["properties"]["overallStatusCode"] = {"type": "string"}
    found = {n for n, _p in W.advisory_hits(planted)}
    assert "overallStatusCode" in found, (
        "`overallStatusCode` passed the advisory scan. It is exactly the name the advisory half "
        "exists for: not an exact match, and unmistakably a verdict."
    )


def test_contract__additional_properties_false_everywhere() -> None:
    """**Every** object schema, including inside `$defs` — minus the constraint branches."""
    offenders = [
        path for path, obj in W.object_schemas(SCHEMA)
        if obj.get("additionalProperties") is not False
        and not any(path.endswith(c) or f"{c}." in path for c in CONSTRAINT_PATHS)
    ]
    assert offenders == [], (
        f"{len(offenders)} object schema(s) admit unknown properties: {offenders}. An attestation "
        "that can carry a field nobody declared can carry a field nobody validated."
    )
    assert len(list(W.object_schemas(SCHEMA))) >= 15, "the walk is finding almost no objects"


def test_contract__the_constraint_branches_are_constraints_and_not_definitions() -> None:
    """The carve-out above, asserted rather than assumed.

    An `additionalProperties: false` inside the INVALID branch would forbid `scope`, `runState` and
    every other property the branch does not mention — turning a constraint into a redefinition and
    making every INVALID statement fail validation.
    """
    branch = SCHEMA["$defs"]["predicate"]["allOf"][0]
    assert set(branch) == {"if", "then"}
    assert "additionalProperties" not in branch["then"]
    assert set(branch["then"]["properties"]) == {"settledFraction", "verdict"}


def test_contract__top_level_is_scope() -> None:
    """The top-level object of the predicate is `scope`. It is not `result`, and it is not a
    summary: the first thing the document says is what it looked at."""
    props = SCHEMA["$defs"]["predicate"]["properties"]
    assert next(iter(props)) == "scope"
    assert "scope" in SCHEMA["$defs"]["predicate"]["required"]


def test_contract__four_statements_required() -> None:
    """REQUIRED FIELDS, not template strings. A template can be edited by anyone; a `required` in
    a JSON Schema fails the build."""
    st = SCHEMA["$defs"]["statements"]
    assert set(st["required"]) == {
        "boundedSilence", "purpose", "summaryIsNotSubstitute", "detectionBoundary"
    }
    for name, sub in st["properties"].items():
        assert sub.get("minLength", 0) >= 60, (
            f"{name} may be an empty string, so the disclaimer can be removed without failing "
            "validation — which is the whole thing making it a required field was meant to stop"
        )
    from cdfc.attest.statement import STATEMENTS

    assert set(STATEMENTS) == set(st["properties"]), "the code and the schema carry different sets"
    for name, text in STATEMENTS.items():
        assert len(text) >= 60, f"{name} is shorter than its own schema admits"


def test_contract__absent_empty_null_are_distinct() -> None:
    """`NONE ≠ NOASSERTION ≠ absent`, per field.

    `[]` means we determined there are none · `null` means we make no claim · an **omitted** field
    is a violation the validator rejects. SPDX's `NOASSERTION` collapse — one token for *we looked
    and found nothing* and *we did not look* — is what this rule exists to avoid.
    """
    pred = SCHEMA["$defs"]["predicate"]
    required = set(pred["required"])
    for field in ("invalidCauses", "counterEvidence", "openItems"):
        assert field in required, f"{field} may be omitted, so [] and absent are indistinguishable"
        assert pred["properties"][field]["type"] == "array", f"{field} must be an array, never null"
    for field in ("settledFraction", "verdict", "livenessProof", "residue", "falseFailureRate"):
        assert field in required, f"{field} may be omitted, so null and absent are indistinguishable"
        options = pred["properties"][field]["oneOf"]
        assert {"type": "null"} in options, f"{field} cannot express `we make no claim`"


def test_contract__invalid_carries_a_null_not_an_absence() -> None:
    """**F24, and it replaces a test that asserted the opposite of what `plan/03` P5-B4 asserts.**

    Three documents said three different things about one field in one state: present-and-null,
    forbidden, and omitted-is-a-violation. P5 and P11 each passed their own contract test while the
    integration produced an attestation that either failed validation or dropped the `null` that
    `E2E-INVALID` exists to assert.

    The ruling has three legs and all three are asserted here: the property is **present**, its
    value is **null**, and a statement **omitting** it fails validation.
    """
    branch = SCHEMA["$defs"]["predicate"]["allOf"][0]
    assert branch["if"]["properties"]["runState"]["const"] == "INVALID"
    then = branch["then"]
    # leg 1 — present
    assert set(then["required"]) == {"settledFraction", "verdict"}
    # leg 2 — null, expressed as a CONSTRAINT ON THE VALUE and never as a prohibition
    assert then["properties"]["settledFraction"] == {"const": None}
    assert then["properties"]["verdict"] == {"const": None}
    assert "not" not in then, (
        "the INVALID branch forbids the property instead of constraining its value. Forbidding it "
        "makes the one state we most need to express indistinguishable from a malformed statement."
    )
    # leg 3 — omission is a violation, which the predicate's own `required` already enforces
    assert {"settledFraction", "verdict"} <= set(SCHEMA["$defs"]["predicate"]["required"])


def test_contract__no_json_float_in_the_payload() -> None:
    """§0.7. No `.`, `e` or `E` inside any JSON number token of the canonicalised bytes.

    Money is an `int64` count of 10⁻³ USD Million; tolerances are integers; **rates are integer
    ppm**. A float in a hashed payload makes the canonicalisation implementation-dependent, which
    makes byte identity a claim about which machine ran it.
    """
    from tests.contract.attest_fixtures import sample_statement

    # **A PARSE HOOK, NOT A PATTERN OVER THE TEXT.** The first version of this test scanned the
    # canonicalised bytes with a number regex and reported a float — from inside the string
    # `"cdfc.calc P3 + celpy 0.5.0"`. A version string is not a JSON number, and a test that cannot
    # tell them apart fails on correct payloads and would eventually be relaxed to shut it up.
    # `parse_float` fires on an actual JSON float token and on nothing else.
    seen_ints: list[int] = []

    def _no_float(token: str) -> float:
        raise AssertionError(
            f"a JSON float reached the canonicalised payload: {token!r}. Money is an int64 count "
            "of 10^-3 USD Million, tolerances are integers, and rates are integer ppm — a float "
            "here makes the canonicalisation implementation-dependent, which makes byte identity "
            "a claim about which machine ran it."
        )

    payload = sample_statement().canonical().decode("utf-8")
    json.loads(payload, parse_float=_no_float, parse_int=lambda t: seen_ints.append(int(t)) or 0)
    assert seen_ints, "the payload carries no number at all — this test is checking nothing"

    # And the schema forbids one arriving later: every numeric property is `integer`.
    reals = [
        f"{path}.{name}"
        for path, obj in W.object_schemas(SCHEMA)
        for name, sub in obj["properties"].items()
        if isinstance(sub, dict) and sub.get("type") == "number"
    ]
    assert reals == [], f"the schema admits a JSON number (not integer) at: {reals}"


def test_contract__the_schema_and_the_builder_agree_on_the_required_set() -> None:
    """Two lists of the predicate's fields would drift, and the one that drifts is the one nobody
    is reading."""
    from cdfc.attest.statement import REQUIRED_PREDICATE_KEYS

    assert set(REQUIRED_PREDICATE_KEYS) == set(SCHEMA["$defs"]["predicate"]["required"])


def test_contract__the_manifest_pins_are_the_ones_verify_re_runs() -> None:
    """Eight pins plus the two run-level INPUTS. A pin the schema names and `verify` does not check
    is a pin nobody checks."""
    from cdfc.attest.statement import MANIFEST_PINS, MANIFEST_RUN_INPUTS

    declared = set(SCHEMA["$defs"]["manifest"]["required"])
    assert len(MANIFEST_PINS) == 8
    assert declared == set(MANIFEST_PINS) | set(MANIFEST_RUN_INPUTS)
    # Over the PROPERTY NAMES, not the document text — this schema's own `description` explains
    # why libreoffice is absent, and a substring scan that its own explanation defeats is a check
    # on the comments. Third time this shape has appeared in this build; each time the fix is to
    # scan the structure.
    tools = set(SCHEMA["$defs"]["toolVersions"]["properties"])
    assert "libreoffice" not in tools, (
        "libreoffice is deliberately absent from the pinned tool versions: it is not on the "
        "verdict path, and pinning it would imply it was"
    )
    assert tools == {"python", "lxml", "openpyxl", "celpy", "z3"}
