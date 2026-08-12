"""RFC 8785 canonicalisation — the property that a registry root is well defined.

*Invariant:* canonicalisation is insertion-order invariant.

*Why this generator:* keys are drawn from an alphabet including `U+2011 NON-BREAKING
HYPHEN`, the exact homoglyph found in a live IFSCA registration number, and characters
outside the BMP. RFC 8785 sorts by UTF-16 code units, which differs from Python's
code-point order precisely there — and two implementations disagreeing on key order
produce two Merkle roots for one registry.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.canon import NonCanonicalisable, canonical_json, digest  # noqa: E402

KEY_ALPHABET = "abzAZ09 -_/‑é中\U0001f600"

keys = st.text(alphabet=KEY_ALPHABET, min_size=1, max_size=6)
scalars = st.one_of(
    st.none(), st.booleans(), st.integers(min_value=-(2**63), max_value=2**63 - 1),
    st.text(alphabet=KEY_ALPHABET, max_size=8),
)
json_trees = st.recursive(
    scalars,
    lambda children: st.one_of(
        st.lists(children, max_size=4), st.dictionaries(keys, children, max_size=4)
    ),
    max_leaves=12,
)


def _shuffle(obj: object, rng: random.Random) -> object:
    if isinstance(obj, dict):
        items = list(obj.items())
        rng.shuffle(items)
        return {k: _shuffle(v, rng) for k, v in items}
    if isinstance(obj, list):
        return [_shuffle(v, rng) for v in obj]
    return obj


@given(json_trees, st.integers(min_value=0, max_value=2**32 - 1))
@settings(max_examples=250, deadline=None)
def test_prop__canonicalisation_is_order_invariant(tree: object, seed: int) -> None:
    rng = random.Random(seed)
    assert canonical_json(_shuffle(tree, rng)) == canonical_json(tree)


@given(json_trees)
@settings(max_examples=100, deadline=None)
def test_prop__digest_is_stable_under_reordering(tree: object) -> None:
    assert digest(_shuffle(tree, random.Random(7))) == digest(tree)


def test_canon__sorts_by_utf16_code_units_not_code_points() -> None:
    """The case that separates RFC 8785 from `json.dumps(sort_keys=True)`.

    U+FF3A (fullwidth Z, BMP) vs U+10000 (outside the BMP). By code point FF3A < 10000 is
    false; by UTF-16 code units the surrogate pair D800 DC00 sorts BEFORE FF3A. A registry
    root computed under the wrong order is a different root.
    """
    obj = {"Ｚ": 1, "\U00010000": 2}
    out = canonical_json(obj).decode()
    assert out.index('"\U00010000"') < out.index('"Ｚ"'), out


def test_canon__refuses_a_float() -> None:
    with pytest.raises(NonCanonicalisable, match="float"):
        canonical_json({"amount": 1.5})


def test_canon__has_no_insignificant_whitespace() -> None:
    assert canonical_json({"b": 1, "a": [1, 2]}) == b'{"a":[1,2],"b":1}'


def test_canon__escapes_control_characters_per_spec() -> None:
    assert canonical_json({"k": "a\nb\tc\x00"}) == b'{"k":"a\\nb\\tc\\u0000"}'
