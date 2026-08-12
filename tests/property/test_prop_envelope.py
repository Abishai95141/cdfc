"""P4-B1 — the two properties the envelope's identity rests on.

`test_prop__every_envelope_field_is_covered_by_the_digest` is the one that pays for itself: it
reads the field list from `dataclasses.fields()` **at runtime**, so a field added to the record
without being added to the projection fails here rather than silently leaving the identity. It is
what made `claims_fault_classes` and `clause_absent_reason` part of the identity for free the
moment they were added, and it is the control behind NC-Q70.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path
from typing import Any

import yaml
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.canonical import code_sha256, envelope_projection, jcs  # noqa: E402
from cdfc.predicates.envelope import Candidate, Predicate  # noqa: E402
from cdfc.predicates.loader import load_candidate, load_predicate  # noqa: E402

GOOD = REPO / "fixtures" / "predicates" / "good"
P0041 = GOOD / "P-0041__scheme-type-membership.yaml"
P0007 = GOOD / "P-0007__intro-D17-integer-bound.yaml"

SLOW = settings(max_examples=120, deadline=None, suppress_health_check=[HealthCheck.too_slow])

# Keys drawn from an alphabet that includes non-ASCII and control-adjacent escapes: RFC 8785
# sorts by UTF-16 code unit, and the orders differ for anything outside the BMP.
_KEY = st.text(
    alphabet=st.sampled_from(list("abzAZ09_") + ["é", "字", "\U0001f600", "‑", ""]),
    min_size=1,
    max_size=6,
)


def _json_trees(depth: int = 0) -> st.SearchStrategy[Any]:
    leaves = st.none() | st.booleans() | st.integers(-(10**9), 10**9) | st.text(max_size=8)
    if depth >= 4:
        return leaves
    inner = _json_trees(depth + 1)
    return leaves | st.lists(inner, max_size=4) | st.dictionaries(_KEY, inner, max_size=4)


def _shuffle_keys(obj: Any, rnd: Any) -> Any:
    if isinstance(obj, dict):
        items = list(obj.items())
        rnd.shuffle(items)
        return {k: _shuffle_keys(v, rnd) for k, v in items}
    if isinstance(obj, list):
        return [_shuffle_keys(v, rnd) for v in obj]
    return obj


@SLOW
@given(tree=_json_trees(), seed=st.integers(0, 2**32 - 1))
def test_prop__jcs_is_order_invariant(tree: Any, seed: int) -> None:
    """Shuffling any dict's insertion order anywhere in the tree does not change jcs()."""
    import random

    twin = _shuffle_keys(tree, random.Random(seed))
    assert jcs(tree) == jcs(twin)


# --- the perturbation generator ---------------------------------------------------------


def _fields_of(obj: Any) -> tuple[str, ...]:
    return tuple(f.name for f in dataclasses.fields(obj))


def _perturb(value: Any) -> Any:
    """A different, still-lawful value for a single field. Type-preserving where it can be."""
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "~"
    if isinstance(value, tuple):
        return value[:-1] if len(value) > 1 else (*value, "~extra~")
    if value is None:
        return "~was-none~"
    if dataclasses.is_dataclass(value):
        first = _fields_of(value)[0]
        return dataclasses.replace(value, **{first: _perturb(getattr(value, first))})
    return "~perturbed~"


def _envelopes() -> list[Candidate | Predicate]:
    return [load_candidate(P0041), load_predicate(P0007)]


def _unvalidated_twin(env: Any, name: str, value: Any) -> Any:
    """A copy of `env` with one field changed, built WITHOUT running the record's validation.

    Deliberate. The property under test is *the digest covers every field*, which is a question
    about the canonical projection, not about the record's invariants. Restricting the
    perturbation to lawful values would silently skip every field whose admissible alternatives
    are constrained by another field — `clause`, `clause_absent_reason`, `obligation_source`,
    `withdrawn_reason` — and those are exactly the fields D-P4-06 and D-P4-07 added.
    """
    twin = object.__new__(type(env))
    for f in dataclasses.fields(env):
        object.__setattr__(twin, f.name, value if f.name == name else getattr(env, f.name))
    return twin


def test_prop__every_envelope_field_is_covered_by_the_digest() -> None:
    """For a valid envelope `p` and any SINGLE-FIELD perturbation `p'`, the digests differ.

    The field list comes from `dataclasses.fields()` at runtime, so this test grows with the
    record. A field added without being added to `envelope_projection` fails here.
    """
    for env in _envelopes():
        base = code_sha256(env)
        names = _fields_of(env)
        assert names, "an envelope with no fields has no identity"
        for name in names:
            twin = _unvalidated_twin(env, name, _perturb(getattr(env, name)))
            assert code_sha256(twin) != base, (
                f"perturbing {type(env).__name__}.{name} did not change code_sha256 — the "
                "field is not inside the identity, so it can be changed after admission "
                "without producing a new predicate"
            )


def test_prop__projection_covers_every_declared_field() -> None:
    """The structural half of the same guarantee, checked without perturbing anything."""
    for env in _envelopes():
        projected = set(envelope_projection(env))
        declared = set(_fields_of(env))
        assert declared <= projected, f"absent from the projection: {sorted(declared - projected)}"


@SLOW
@given(seed=st.integers(0, 2**32 - 1))
def test_prop__digest_is_invariant_to_yaml_mapping_order(seed: int) -> None:
    import random

    raw = yaml.safe_load(P0041.read_text(encoding="utf-8"))
    shuffled = _shuffle_keys(raw, random.Random(seed))
    assert code_sha256(load_candidate(shuffled)) == code_sha256(load_candidate(raw))
