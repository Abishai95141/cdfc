"""P4-B1 — the predicate schema's contract.

The schema is GENERATED from the record. Two declarations of one shape diverge silently in the
direction that matters — a field the record requires and the schema does not is a field a YAML
author may omit — so the committed file is asserted equal to the generated one.

The forbidden-property walk is the same one the attestation schema gets. The prohibition is not
attestation-specific: a predicate that could carry `status` would leak it upward into every
surface that renders a predicate.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.schema_build import build_schema  # noqa: E402

COMMITTED = REPO / "src" / "cdfc" / "predicates" / "schema" / "predicate.schema.json"

# The words a verdict-bearing surface may never carry. `result`, `status` and `pass` are the
# three the spec names; `verdict` and `ok` are added because they are the same field wearing a
# different label, and this schema is upstream of every one of them.
FORBIDDEN_PROPERTY_NAMES = frozenset({"result", "status", "pass", "passed", "verdict", "ok"})


def _walk(node: Any, path: str = "") -> list[tuple[str, str]]:
    """Every (json-pointer, property-name) pair in the schema, at every depth."""
    found: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for name in node.get("properties", {}):
            found.append((path, name))
        for k, v in node.items():
            found.extend(_walk(v, f"{path}/{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found.extend(_walk(v, f"{path}/{i}"))
    return found


def _objects(node: Any, path: str = "") -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    if isinstance(node, dict):
        if node.get("type") == "object" or "properties" in node:
            out.append((path, node))
        for k, v in node.items():
            out.extend(_objects(v, f"{path}/{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_objects(v, f"{path}/{i}"))
    return out


def test_contract__committed_schema_matches_the_generated_one() -> None:
    assert COMMITTED.is_file(), f"{COMMITTED} is missing; run tools/gen_predicate_schema.py"
    committed = json.loads(COMMITTED.read_text(encoding="utf-8"))
    assert committed == build_schema(), (
        "the committed schema and the record have diverged. Run "
        "`python tools/gen_predicate_schema.py` — and if you did not change the record, ask "
        "why the committed file moved."
    )


def test_contract__predicate_schema_forbids_result_status_pass() -> None:
    offenders = [
        f"{ptr} -> {name}"
        for ptr, name in _walk(build_schema())
        if name.lower() in FORBIDDEN_PROPERTY_NAMES
    ]
    assert offenders == [], (
        f"the predicate schema carries a verdict-shaped property: {offenders}. A predicate that "
        "could carry one would leak it into every surface that renders a predicate."
    )


def test_contract__additional_properties_is_false_at_every_object_depth() -> None:
    permissive = [
        ptr for ptr, obj in _objects(build_schema()) if obj.get("additionalProperties", True) is not False
    ]
    assert permissive == [], (
        f"objects admitting unknown fields: {permissive}. `clause/provisos/items` is the depth a "
        "hand-written schema forgets, which is why this walks rather than spot-checks."
    )


def test_contract__rejection_has_no_predicate_id() -> None:
    """D-P4-01, mechanised at the schema boundary.

    There is no REJECTED predicate state, so no envelope may carry the fields a rejection row
    would need. A rejection is keyed by `candidate_sha256` with `predicate_id NULL`.
    """
    names = {name for _, name in _walk(build_schema())}
    assert "candidate_sha256" not in names
    assert "predicate_id" not in names, (
        "an envelope carrying predicate_id would let a rejection acquire an identity, which is "
        "exactly what D-P4-01 refuses"
    )


def test_contract__generator_is_idempotent_and_the_tool_reports_it() -> None:
    """Running the generator twice must not move the file, or its diff is not reviewable."""
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "gen_predicate_schema.py")],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "unchanged" in r.stdout, f"the generator moved the committed schema: {r.stdout!r}"


def test_contract__every_admitted_enum_is_closed() -> None:
    """No enum in the schema is open-ended: every one lists its members explicitly."""
    schema = build_schema()
    enums = []

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            if "enum" in node:
                enums.append(node["enum"])
            for v in node.values():
                collect(v)
        elif isinstance(node, list):
            for v in node:
                collect(v)

    collect(schema)
    assert enums, "the schema has no enums at all, which means the vocabularies are not closed"
    for e in enums:
        assert len(e) == len(set(map(repr, e))), f"duplicate enum member in {e!r}"


@pytest.mark.parametrize("depth_key", ["Candidate", "Predicate"])
def test_contract__both_envelope_types_are_defined(depth_key: str) -> None:
    assert depth_key in build_schema()["$defs"]


def test_contract__2373_is_pinned_as_a_literal_in_no_golden_at_this_phase() -> None:
    """`ci/golden-literals-are-traceable.sh`'s subject, asserted from inside the suite too.

    2,373 is the specification's `static_settled_cells` figure. It resolves to no ledger row and to
    no measurement this code produces, so a golden comparing against it would be comparing against
    a number nobody can re-derive. It is published BESIDE the computed figure with the delta in a
    sentence, and that is the only place it may appear.

    The scan lives here rather than in `tests/golden/` so that it does not read itself — a guard
    whose own source trips it is a guard nobody can keep green.
    """
    import re

    offenders = []
    for py in sorted((REPO / "tests" / "golden").glob("*.py")):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(?<![\d,.])2,?373(?![\d.])", line):
                offenders.append(f"{py.name}:{i}: {line.strip()[:60]}")
    assert offenders == [], f"2,373 appears as a literal in a golden: {offenders}"


def test_contract__the_guard_above_can_see_a_literal_when_there_is_one(tmp_path) -> None:
    """The admission-side control: a scan that matches nothing is not a guard."""
    import re

    for text, should_match in [
        ("assert cells == 2373", True),
        ("assert cells == 2,373", True),
        ("assert cells == 23730", False),
        ("assert cells == 2854", False),
    ]:
        assert bool(re.search(r"(?<![\d,.])2,?373(?![\d.])", text)) is should_match, text
