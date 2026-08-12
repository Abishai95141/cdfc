"""P4-B2/B3 — the static key set must COVER what a program actually reads.

**This is the control on the phase's headline number.** `read_keys` is a static
over-approximation, and the settled fraction is only honest if it is a genuine *over*-approximation:
every key read at run time must be inside the declared set, or pre-flight is guarding keys the
predicate does not touch while missing ones it does.

The two arms are independent by mechanism, not by authorship. The static arm walks celpy's parse
tree and never evaluates anything. The dynamic arm evaluates the program against an instrumented
fact view and records what the runtime actually asked for. A defect in the static walker's
comprehension handling shows up here as an observed key outside the declared set.

**What this does not establish.** The reverse containment is not required and must not be asserted:
a static set STRICTLY LARGER than the dynamic one is correct and expected, because `||`
short-circuits and a `filter` that matches nothing never reaches its `map`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.evaluate.celrt import CelRuntime  # noqa: E402
from cdfc.facts.view import FactView  # noqa: E402
from cdfc.predicates.ast_walker import all_read_keys, read_keys  # noqa: E402
from cdfc.predicates.host_fns import default_registry  # noqa: E402
from cdfc.predicates.loader import load_candidate, load_predicate  # noqa: E402

GOOD = REPO / "fixtures" / "predicates" / "good"

FILING = {
    "a": {"b": 1},
    "rows": [
        {"x": 1, "__cell__": "S!A1"},
        {"x": -2, "__cell__": "S!A2"},
        {"x": 0, "__cell__": "S!A3"},
    ],
    "total": -1,
    "intro": {
        "tbl11": {"n_schemes": 3, "__cell__": "Intro!D17"},
        "tbl15": {
            "rows": [
                {"scheme_type": "AIF", "__cell__": "Intro!C25"},
                {"scheme_type": "", "__cell__": "Intro!C26"},
                {"scheme_type": "NOT-A-TYPE", "__cell__": "Intro!C27"},
            ]
        },
    },
}
TEMPLATE = {"v": {"k": ["a", "b"]}, "vocab": {"scheme_type": ["AIF", "PMS"]}}

CASES: list[tuple[str, str]] = [
    ("expr", "filing.a.b == 1"),
    ("expr", "filing.rows.all(r, r.x > 0)"),
    ("expr", "filing.rows.exists(r, r.x < 0)"),
    ("expr", "size(filing.rows) > 0"),
    ("applicable", "has(filing.a.b)"),
    ("witness", "filing.rows.filter(r, r.x <= 0).map(r, r.__cell__)"),
    ("expr", "sum(filing.rows.map(r, r.x)) == filing.total"),
    ("expr", 'filing.intro.tbl15.rows.all(r, r.scheme_type == "" || r.scheme_type in template.vocab.scheme_type)'),
    ("witness", 'filing.intro.tbl15.rows.filter(r, r.scheme_type != "" && !(r.scheme_type in template.vocab.scheme_type)).map(r, r.__cell__)'),
    ("expr", "filing.intro.tbl11.n_schemes >= 0"),
]


@pytest.fixture(scope="module")
def rt() -> CelRuntime:
    return CelRuntime(profile_version="P4", host_fns=default_registry())


@pytest.mark.parametrize("slot,src", CASES, ids=[c[1][:40] for c in CASES])
def test_diff__every_dynamic_read_is_inside_the_static_set(rt: CelRuntime, slot: str, src: str) -> None:
    static = set(read_keys(src, slot=slot))
    observed = set(
        rt.observed_keys(
            rt.compile(src, slot=slot),
            filing=FactView(FILING, root="filing"),
            template=FactView(TEMPLATE, root="template"),
        )
    )
    escaped = observed - static
    assert escaped == set(), (
        f"the runtime read {sorted(escaped)}, which static extraction did not report. The declared "
        "set is what pre-flight guards, so a key that escapes it is a key nobody checked was "
        "present — and the settled fraction is counting it as settled."
    )


def test_diff__the_corpus_actually_exercises_the_recorder(rt: CelRuntime) -> None:
    """The admission-side control. A recorder that records nothing satisfies every case above."""
    total = set()
    for slot, src in CASES:
        total |= set(
            rt.observed_keys(
                rt.compile(src, slot=slot),
                filing=FactView(FILING, root="filing"),
                template=FactView(TEMPLATE, root="template"),
            )
        )
    assert len(total) >= 6, f"the dynamic arm observed only {sorted(total)}; it proves nothing"
    assert any("[*]" in k for k in total), "no repeated node was traversed at all"
    assert any(k.startswith("template.") for k in total), "the template side was never read"


@pytest.mark.parametrize(
    "path,loader",
    [("P-0041__scheme-type-membership.yaml", load_candidate),
     ("P-0007__intro-D17-integer-bound.yaml", load_predicate)],
)
def test_diff__the_committed_envelopes_read_only_what_they_declare(rt: CelRuntime, path: str, loader) -> None:
    c = loader(GOOD / path)
    declared = set(c.schema_keys)
    observed: set[str] = set()
    for slot in ("applicable", "expr", "witness"):
        observed |= set(
            rt.observed_keys(
                rt.compile(getattr(c, slot), slot=slot),
                filing=FactView(FILING, root="filing"),
                template=FactView(TEMPLATE, root="template"),
            )
        )
    assert observed <= declared, f"{c.id} read {sorted(observed - declared)} undeclared"
    assert observed, f"{c.id} read nothing at all against this fact view; the case is vacuous"
    assert observed <= set(all_read_keys(c))
