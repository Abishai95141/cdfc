"""P4-B2 — the three properties static key extraction rests on.

The generator draws binding names from a pool that **deliberately collides** with fact-model
segment names (`rows`, `filing`, `template`, `x`). A lexical extractor passes a generator whose
binding names are all `q1`, `q2`, `q3`; it fails this one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.ast_walker import KeyRef, bound_cells, read_keys  # noqa: E402
from cdfc.predicates.cel_profile import check_subset  # noqa: E402
from cdfc.predicates.errors import KeyGrammarError, SubsetViolation  # noqa: E402

SLOW = settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])

# Names that collide with real fact-model segments on purpose.
BINDINGS = st.sampled_from(["r", "x", "rows", "filing", "template", "scheme_type", "row"])
SEGMENTS = st.sampled_from(["a", "b", "rows", "x", "intro", "tbl15", "scheme_type", "vocab"])
ROOTS = st.sampled_from(["filing", "template"])


@st.composite
def _path(draw: st.DrawFn, root: str | None = None) -> str:
    r = root or draw(ROOTS)
    n = draw(st.integers(1, 3))
    return ".".join([r, *[draw(SEGMENTS) for _ in range(n)]])


@st.composite
def _comprehension(draw: st.DrawFn) -> tuple[str, str]:
    """`(source, binding)` for a flat, admitted comprehension over the filing."""
    binding = draw(BINDINGS)
    coll = draw(_path(root="filing"))
    field = draw(SEGMENTS)
    macro = draw(st.sampled_from(["all", "exists", "exists_one"]))
    rhs = draw(st.sampled_from(['""', "0", "1"]))
    op = draw(st.sampled_from(["==", "!=", ">", ">=", "<", "<="]))
    assume(rhs != '""' or op in ("==", "!="))
    return f"{coll}.{macro}({binding}, {binding}.{field} {op} {rhs})", binding


@SLOW
@given(pair=_comprehension())
def test_prop__read_keys_never_reports_a_comprehension_variable(pair: tuple[str, str]) -> None:
    src, binding = pair
    keys = read_keys(src, slot="expr")
    assert keys, "a comprehension over a path always reads something"
    for k in keys:
        root = k.split(".")[0]
        assert root in ("filing", "template"), f"{k!r} is rooted at a name no document has"
        if binding not in ("filing", "template"):
            assert not k.startswith(f"{binding}."), (
                f"{k!r} reports the comprehension binding {binding!r} as a document root"
            )


@SLOW
@given(
    root=ROOTS,
    segs=st.lists(SEGMENTS, min_size=1, max_size=4),
    stars=st.lists(st.booleans(), min_size=1, max_size=4),
)
def test_prop__declared_key_grammar_roundtrips(root: str, segs: list[str], stars: list[bool]) -> None:
    parts = [root]
    for i, s in enumerate(segs):
        parts.append(s + ("[*]" if i < len(stars) and stars[i] else ""))
    dotted = ".".join(parts)
    assert KeyRef.parse(dotted).dotted() == dotted


@SLOW
@given(
    keys=st.lists(_path(root="filing"), min_size=0, max_size=5, unique=True),
    extra=_path(root="filing"),
)
def test_prop__bound_cells_is_monotone_in_the_key_set(keys: list[str], extra: str) -> None:
    """Adding a key never shrinks `bound_cells`.

    Catches an intersection written where a union was meant, which would make `cells_bound`
    under-report and turn real predicates into `ERROR(cells_bound_zero)` — a coverage claim
    silently reduced by a one-character mistake.
    """
    from cdfc.predicates.ast_walker import TemplateSchema

    schema = TemplateSchema({k: frozenset({f"S!{i}"}) for i, k in enumerate({*keys, extra})}, "t")

    class _C:
        def __init__(self, ks: tuple[str, ...]) -> None:
            self.schema_keys = ks

    smaller = bound_cells(_C(tuple(keys)), schema)
    larger = bound_cells(_C((*keys, extra)), schema)
    assert smaller <= larger


@SLOW
@given(pair=_comprehension())
def test_prop__every_generated_comprehension_is_inside_the_admitted_subset(
    pair: tuple[str, str],
) -> None:
    """The admission-side control for the generator itself.

    Without it, a generator producing only banned forms would make the property above vacuous:
    every example would raise before `read_keys` ran.
    """
    src, _ = pair
    check_subset(src, slot="expr")


@SLOW
@given(pair=_comprehension(), inner=_comprehension())
def test_prop__nesting_any_two_admitted_comprehensions_is_refused(
    pair: tuple[str, str], inner: tuple[str, str]
) -> None:
    outer_src, binding = pair
    body = inner[0].replace("filing.", f"{binding}.", 1)
    nested = outer_src.rsplit(")", 1)[0] + f" && {body})"
    with pytest.raises((SubsetViolation, KeyGrammarError)):
        check_subset(nested, slot="expr")
