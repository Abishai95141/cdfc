"""P4-B1 — `cdfc.predicates.validate` against an independent JSON Schema implementation.

**Why this exists.** `validate.py` is ours, and a hand-rolled validator that is silently
permissive is this project's own failure mode: the checker reports OK, the envelope carries a
field nobody declared, and the digest covers it or does not — either way no gate went red. So the
decision to write it rather than depend on `jsonschema` at runtime is paid for HERE, by checking
it against `jsonschema` on a corpus of good and broken envelopes.

`jsonschema` is a TEST dependency, pinned in `requirements.lock`. It is not importable from
anything under `src/`, and `test_diff__jsonschema_is_not_in_the_runtime_closure` asserts that.

**What a differential does not buy.** Two implementations wrong the same way are invisible to it.
This one is a check on OUR validator against a widely-used one, not a conformance claim about
JSON Schema.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.schema_build import build_schema  # noqa: E402
from cdfc.predicates.validate import SchemaViolation, validate  # noqa: E402

jsonschema = pytest.importorskip(
    "jsonschema",
    reason="pinned in requirements.lock as a test dependency; a missing one is an environment "
    "defect, not a reason to skip quietly",
)

GOOD = REPO / "fixtures" / "predicates" / "good"
BROKEN = REPO / "fixtures" / "predicates" / "broken"


def _raw(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _mutations() -> list[tuple[str, Any]]:
    """A corpus of envelopes: the committed ones, plus one broken instance per defect class."""
    base = _raw(GOOD / "P-0007__intro-D17-integer-bound.yaml")
    cand = _raw(GOOD / "P-0041__scheme-type-membership.yaml")
    cases: list[tuple[str, Any]] = [
        ("good-predicate", base),
        ("good-candidate", cand),
        ("unknown-top-level-field", {**base, "confidence": "high"}),
        ("missing-required", {k: v for k, v in base.items() if k != "expr"}),
        ("wrong-type-version", {**base, "version": "1"}),
        ("wrong-type-schema_keys", {**base, "schema_keys": "filing.a"}),
        ("bad-enum-kind", {**base, "kind": "invented"}),
        ("bad-enum-state", {**base, "state": "REJECTED"}),
        ("bad-enum-absence-reason", {**cand, "clause_absent_reason": "because"}),
        ("null-where-string", {**base, "id": None}),
        ("bool-where-integer", {**base, "version": True}),
        ("nested-unknown-field", {
            **base, "tolerance": {"tau_units_per_summand": 5, "units": "USD"},
        }),
        ("span-too-long", {
            **cand, "obligation_source": "STATUTE", "clause_absent_reason": None,
            "clause": {"instrument": "X", "eId": "e", "span": [0, 1, 2], "quote": "q", "provisos": []},
        }),
        ("proviso-unknown-field", {
            **cand, "obligation_source": "STATUTE", "clause_absent_reason": None,
            "clause": {"instrument": "X", "eId": "e", "span": [0, 1], "quote": "q",
                       "provisos": [{"text": "t", "disposal": "DECLARED", "emits": "e",
                                     "span": [0, 1], "certainty": "high"}]},
        }),
        ("not-a-mapping", ["id"]),
        ("empty", {}),
    ]
    for f in sorted(BROKEN.iterdir()):
        cases.append((f"fixture:{f.name}", _raw(f)))
    return cases


def _ours(instance: Any) -> bool:
    try:
        validate(instance, build_schema())
        return True
    except SchemaViolation:
        return False


def _theirs(instance: Any) -> bool:
    try:
        jsonschema.validate(instance, build_schema())
        return True
    except jsonschema.ValidationError:
        return False


@pytest.mark.parametrize("label,instance", _mutations(), ids=[c[0] for c in _mutations()])
def test_diff__our_validator_agrees_with_jsonschema(label: str, instance: Any) -> None:
    ours, theirs = _ours(instance), _theirs(instance)
    assert ours == theirs, (
        f"{label}: ours says {'valid' if ours else 'invalid'}, jsonschema says "
        f"{'valid' if theirs else 'invalid'}. A disagreement in the permissive direction is a "
        "hole in the envelope's closed record."
    )


def test_diff__the_corpus_exercises_both_verdicts() -> None:
    """The admission-side control: without a valid instance the differential is vacuous."""
    verdicts = [_theirs(i) for _, i in _mutations()]
    assert any(verdicts), "no instance in the corpus is valid; the differential proves nothing"
    assert not all(verdicts), "no instance in the corpus is invalid; the same"


def test_diff__the_committed_schema_is_a_valid_json_schema() -> None:
    jsonschema.Draft202012Validator.check_schema(build_schema())


def test_diff__jsonschema_is_not_in_the_runtime_closure() -> None:
    """An AST import walk over src/. The runtime licence claim depends on this being true."""
    offenders = []
    for py in sorted((REPO / "src").rglob("*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            if any(n.split(".")[0] == "jsonschema" for n in names):
                offenders.append(str(py.relative_to(REPO)))
    assert offenders == [], f"jsonschema is imported from the runtime tree: {offenders}"
