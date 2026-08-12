"""P4-B2 — the admitted subset and static key extraction.

The seven-form table is the build's own evidence. `test_golden__both_ways__fme` over the harvested
candidates is authored in B4, because B4 is what produces envelopes to run it against.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.ast_walker import (  # noqa: E402
    KeyRef,
    all_read_keys,
    bound_cells,
    called_host_fns,
    check_declared_keys,
    declared_vs_read,
    inferred_types,
    read_keys,
)
from cdfc.predicates.cel_profile import (  # noqa: E402
    ADMITTED_HOST_FNS,
    ADMITTED_MACROS,
    ADMITTED_OPERATORS,
    BANNED,
    SLOT_RETURN,
    check_subset,
)
from cdfc.predicates.errors import (  # noqa: E402
    DeclaredKeyUnread,
    KeyGrammarError,
    SubsetViolation,
    UndeclaredKeyRead,
)
from cdfc.predicates.loader import load_candidate, load_predicate  # noqa: E402

GOOD = REPO / "fixtures" / "predicates" / "good"
BROKEN = REPO / "fixtures" / "predicates" / "broken"

# The plan's table, verbatim. `r` is never a key, and `[*]` is never lost.
READ_KEY_TABLE: list[tuple[str, str, set[str]]] = [
    ("expr", "filing.a.b == 1", {"filing.a.b"}),
    ("expr", 'filing["a"]["b"] == 1', {"filing.a.b"}),
    ("expr", "filing.rows.all(r, r.x > 0)", {"filing.rows[*].x"}),
    ("expr", "filing.rows.all(r, r.x in template.v.k)", {"filing.rows[*].x", "template.v.k"}),
    ("expr", "size(filing.rows) > 0", {"filing.rows"}),
    ("applicable", "has(filing.a.b)", {"filing.a.b"}),
    (
        "witness",
        "filing.rows.filter(r, r.x == 0).map(r, r.__cell__)",
        {"filing.rows[*].x", "filing.rows[*].__cell__"},
    ),
]


@pytest.mark.parametrize("slot,src,want", READ_KEY_TABLE, ids=[t[1][:32] for t in READ_KEY_TABLE])
def test_read_keys__table(slot: str, src: str, want: set[str]) -> None:
    assert set(read_keys(src, slot=slot)) == want


@pytest.mark.parametrize("slot,src,_want", READ_KEY_TABLE, ids=[t[1][:32] for t in READ_KEY_TABLE])
def test_read_keys__never_reports_a_comprehension_variable(slot: str, src: str, _want: set) -> None:
    for key in read_keys(src, slot=slot):
        assert not key.startswith(("r.", "s.", "r[", "x.")), (
            f"{key!r} is a comprehension binding reported as a document root — the defect a "
            "lexical extractor produces"
        )
        assert key.split(".")[0] in ("filing", "template")


def test_read_keys__index_syntax_normalises_to_the_dotted_grammar() -> None:
    assert read_keys('filing["a"]["b"] == 1') == read_keys("filing.a.b == 1")


def test_read_keys__a_non_literal_index_is_refused() -> None:
    """`filing[filing.i]` cannot be resolved statically, so it cannot be counted."""
    with pytest.raises(KeyGrammarError):
        read_keys("filing.rows[filing.i].x == 1")


# --- the both-ways check ------------------------------------------------------------------


def test_check_declared_keys__undeclared_read_raises_UndeclaredKeyRead() -> None:
    c = load_candidate(BROKEN / "P-NC04a__reads-undeclared.yaml")
    with pytest.raises(UndeclaredKeyRead) as e:
        check_declared_keys(c)
    assert e.value.keys == ("template.vocab.scheme_type",)


def test_check_declared_keys__declared_unread_raises_DeclaredKeyUnread() -> None:
    c = load_candidate(BROKEN / "P-NC04b__declares-unread.yaml")
    with pytest.raises(DeclaredKeyUnread) as e:
        check_declared_keys(c)
    assert e.value.keys == ("filing.intro.tbl15.rows[*].unread_column",)


def test_check_declared_keys__the_two_rejections_are_distinguishable() -> None:
    """NC-Q04. One collapsed `KeysMismatch` type would fail this.

    They have different remedies: the first means the pre-flight set is too small; the second
    means the settled numerator is overstated.
    """
    assert not issubclass(UndeclaredKeyRead, DeclaredKeyUnread)
    assert not issubclass(DeclaredKeyUnread, UndeclaredKeyRead)


def test_check_declared_keys__the_committed_fixtures_agree_both_ways() -> None:
    """The admission-side control: without it, a check that always raises would pass the two above."""
    for f, loader in (
        (GOOD / "P-0041__scheme-type-membership.yaml", load_candidate),
        (GOOD / "P-0007__intro-D17-integer-bound.yaml", load_predicate),
    ):
        c = loader(f)
        check_declared_keys(c)
        assert declared_vs_read(c) == ((), ())


def test_all_read_keys__is_the_union_over_the_three_slots() -> None:
    c = load_candidate(GOOD / "P-0041__scheme-type-membership.yaml")
    union = all_read_keys(c)
    assert "filing.intro.tbl15.rows" in union  # from `applicable`
    assert "template.vocab.scheme_type" in union  # from `expr`
    assert "filing.intro.tbl15.rows[*].__cell__" in union  # from `witness` only


# --- the subset ---------------------------------------------------------------------------


def test_check_subset__nested_comprehension_raises_with_offset() -> None:
    with pytest.raises(SubsetViolation) as e:
        check_subset("filing.rows.all(r, r.sub.all(s, s.x > 0))", slot="expr")
    assert e.value.construct == "nested comprehension"
    assert e.value.offset > 0, "a violation with no offset sends the author to grep"
    assert "exponential" in e.value.reason


def test_check_subset__filter_in_expr_slot_raises_but_in_witness_slot_passes() -> None:
    with pytest.raises(SubsetViolation) as e:
        check_subset("filing.rows.filter(r, r.x == 0)", slot="expr")
    assert e.value.construct == "filter() outside witness"

    # The full witness chain: refused in `expr` (the outermost construct is `map`, so that is the
    # violation reported first — a walk reports what it reaches first, not the worst one) and
    # admitted in `witness`, which is the admission side.
    chain = "filing.rows.filter(r, r.x == 0).map(r, r.__cell__)"
    with pytest.raises(SubsetViolation) as e2:
        check_subset(chain, slot="expr")
    assert e2.value.construct == "map() outside sum()"
    check_subset(chain, slot="witness")


def test_check_subset__map_is_admitted_only_inside_sum_outside_the_witness_slot() -> None:
    with pytest.raises(SubsetViolation, match="map"):
        check_subset("filing.rows.map(r, r.x)", slot="expr")
    check_subset("sum(filing.rows.map(r, r.amount)) == filing.total", slot="expr")


@pytest.mark.parametrize(
    "src,construct",
    [
        ('filing.a.matches("^x")', "matches()"),
        ('filing.a > timestamp("2026-01-01T00:00:00Z")', "timestamp/duration/now"),
        ("dyn(filing.a) == 1", "type()/dyn()"),
        ("filing.a == 1.5", "double literal"),
        ("filing.a == 2u", "bytes/uint/protobuf"),
        ('filing.a in {"x": 1}', "map literal"),
    ],
)
def test_check_subset__banned_constructs(src: str, construct: str) -> None:
    with pytest.raises(SubsetViolation) as e:
        check_subset(src, slot="expr")
    assert e.value.construct == construct
    assert e.value.reason == BANNED[construct], "the rejection prints the registered sentence"


def test_check_subset__binds_exactly_two_names() -> None:
    for src in ("other.a == 1", "r.x == 1", "vocabulary.a == 1"):
        with pytest.raises(SubsetViolation, match="unbound name"):
            check_subset(src, slot="expr")
    check_subset("filing.a == template.a", slot="expr")


def test_check_subset__an_unregistered_function_is_refused() -> None:
    with pytest.raises(SubsetViolation, match="unknown function"):
        check_subset("unknown_fn(filing.a)", slot="expr")
    with pytest.raises(SubsetViolation, match="unknown function"):
        check_subset("reg_resolves(filing.a)", slot="expr", host_fns=frozenset())


def test_check_subset__slot_return_shape_is_enforced_both_ways() -> None:
    with pytest.raises(SubsetViolation, match="wrong return shape"):
        check_subset("filing.a == 1", slot="witness")
    with pytest.raises(SubsetViolation, match="wrong return shape"):
        check_subset("[filing.a.__cell__]", slot="expr")
    check_subset("[filing.a.__cell__]", slot="witness")
    check_subset("filing.a == 1", slot="expr")


def test_profile__every_banned_key_carries_a_sentence() -> None:
    for construct, sentence in BANNED.items():
        assert len(sentence) > 40, f"{construct} has no explanation a predicate author can act on"
        assert not sentence.endswith("."), "sentences are composed into a message, not printed raw"


def test_profile__the_declared_vocabularies_are_closed() -> None:
    assert SLOT_RETURN == {"applicable": bool, "expr": bool, "witness": list}
    assert "matches" not in ADMITTED_MACROS
    assert {"all", "exists", "exists_one", "map", "filter"} <= ADMITTED_MACROS
    assert "**" not in ADMITTED_OPERATORS
    assert "sum" in ADMITTED_HOST_FNS


# --- the key grammar ------------------------------------------------------------------------


def test_key_ref__round_trips() -> None:
    for k in (
        "filing.intro.tbl15.rows[*].scheme_type",
        "template.vocab.scheme_type",
        "filing.a",
        "filing.a[*].b[*].c",
    ):
        assert KeyRef.parse(k).dotted() == k


def test_key_ref__refuses_a_key_that_does_not_name_a_document() -> None:
    """D-P4-02: the defect a root-dropped grammar cannot express is NC-D01c."""
    for k in ("intro.tbl15.rows[*].scheme_type", "vocab.scheme_type", "filing"):
        with pytest.raises(KeyGrammarError):
            KeyRef.parse(k)


# --- cells_bound ----------------------------------------------------------------------------


class _Schema:
    def __init__(self, mapping: dict[str, frozenset[str]]) -> None:
        self._m = mapping
        self.template_sha256 = "test"

    def cells_for(self, key: str) -> frozenset[str]:
        return self._m.get(key, frozenset())

    def keys(self) -> frozenset[str]:
        return frozenset(self._m)


def test_bound_cells__unions_the_filing_side_and_ignores_the_template_side() -> None:
    c = load_candidate(GOOD / "P-0041__scheme-type-membership.yaml")
    schema = _Schema({
        "filing.intro.tbl15.rows[*].scheme_type": frozenset({"Intro!C25", "Intro!C26"}),
        "filing.intro.tbl15.rows": frozenset({"Intro!C25", "Intro!C26"}),
        "template.vocab.scheme_type": frozenset({"Dropdown!A1", "Dropdown!A2"}),
    })
    cells = bound_cells(c, schema)  # type: ignore[arg-type]
    assert cells == {"Intro!C25", "Intro!C26"}
    assert not any(x.startswith("Dropdown!") for x in cells), (
        "a template vocabulary is not a cell of the artifact under check; counting it would "
        "inflate cells_bound with cells no filer wrote"
    )


def test_bound_cells__is_monotone_in_the_key_set() -> None:
    """An intersection written where a union was meant makes cells_bound under-report, and a
    predicate with cells_bound == 0 becomes ERROR(cells_bound_zero) instead of running."""
    schema = _Schema({"filing.a": frozenset({"S!A1"}), "filing.b": frozenset({"S!B1"})})

    class _C:
        schema_keys = ("filing.a",)

    class _C2:
        schema_keys = ("filing.a", "filing.b")

    assert bound_cells(_C(), schema) <= bound_cells(_C2(), schema)  # type: ignore[arg-type]
    assert len(bound_cells(_C2(), schema)) == 2  # type: ignore[arg-type]


# --- D-P5-03 type inference -----------------------------------------------------------------


def test_inferred_types__reads_the_local_evidence_and_records_ambiguity_as_None() -> None:
    t = inferred_types('filing.a == "x" && filing.b >= 0 && filing.c in template.v')
    assert t["filing.a"] == "STRING"
    assert t["filing.b"] == "INT"
    assert t["template.v"] == "LIST"
    # A key compared against both a string and an integer cannot be typed from the AST alone.
    ambiguous = inferred_types('filing.a == "x" || filing.a == 1')
    assert ambiguous["filing.a"] is None, (
        "an undecidable type must be recorded as undecided; a type check that did not happen is "
        "never reported as one"
    )


def test_called_host_fns__reports_only_registered_names() -> None:
    assert called_host_fns("sum(filing.rows.map(r, r.x)) == filing.t") == {"sum"}
    assert called_host_fns("reg_resolves(filing.a)") == {"reg_resolves"}
    assert called_host_fns("filing.a == 1") == frozenset()
