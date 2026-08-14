"""P9-B1 entry criterion 2b — `formula_source` is passed LITERALLY at every call site.

**Why an AST scan and not a grep.** A grep for `formula_source` would go green on
`recalculate(..., formula_source=src)`, and `src` is exactly the shape the rule exists to
forbid: a caller that computes which formulas it means has re-opened the question F19 closed.
The two meanings must be readable off the call site by a person, not traced through a variable.

**The three things asserted, and each one alone is insufficient.**

1. Every `recalculate(...)` call under `src/cdfc/` passes `formula_source` as a keyword whose
   value is a string *constant*. A missing argument is already a `TypeError` at run time; this
   catches the computed one, which is not.
2. Every calling module appears in `FORMULA_SOURCE_CONTRACT` **with the source it actually
   passes**. Without this, a caller could flip `FILING` to `TEMPLATE` and the published table
   would keep saying otherwise — the rule true in the document and false in the code.
3. Every row of the table has a real caller. Without this, a row survives the deletion of the
   module it describes, and the contract accumulates statements about code that is gone.

Assertion 3 is the one that would have been left out. A table row with no caller is not
harmless: it is a published rule nobody executes, which is the shape this project keeps finding
in its own instrument.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.calc.evaluate import FORMULA_SOURCE_CONTRACT  # noqa: E402

SRC = REPO / "src"
SCAN = SRC / "cdfc"


def _module_of(path: Path) -> str:
    rel = path.relative_to(SRC).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _call_sites() -> list[tuple[str, int, ast.Call]]:
    """Every `recalculate(...)` call in the scan root, with its module and line."""
    out: list[tuple[str, int, ast.Call]] = []
    for path in sorted(SCAN.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if name == "recalculate":
                out.append((_module_of(path), node.lineno, node))
    return out


def _literal_source(call: ast.Call) -> str | None:
    for kw in call.keywords:
        if kw.arg == "formula_source":
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                return kw.value.value
            return None          # present, but computed — which this test exists to refuse
    return None


def test_contract__formula_source_is_explicit() -> None:
    """Assertion 1. A missing or computed argument fails the build."""
    sites = _call_sites()
    assert sites, (
        "no `recalculate` call site was found under src/cdfc/. A scan that finds nothing "
        "reports success, which is the failure mode this whole file is written against."
    )
    bad = [(m, ln) for m, ln, c in sites if _literal_source(c) is None]
    assert not bad, (
        f"{len(bad)} recalculate() call site(s) do not pass a LITERAL formula_source: {bad}. "
        "A computed argument reconciles the two meanings at run time, which is F19 restored."
    )


def test_contract__every_caller_is_in_the_published_table() -> None:
    """Assertion 2. The table says what the code does, or the table is wrong."""
    declared = {r.caller: r.source for r in FORMULA_SOURCE_CONTRACT}
    for module, line, call in _call_sites():
        assert module in declared, (
            f"{module}:{line} calls recalculate() and is not in FORMULA_SOURCE_CONTRACT. "
            "An unlisted caller is a second, unpublished meaning of 'recalculate'."
        )
        assert _literal_source(call) == declared[module], (
            f"{module}:{line} passes formula_source={_literal_source(call)!r} but the published "
            f"contract says {declared[module]!r}. The rule is true in one place and false in "
            "the other, which is worse than not having published it."
        )


def test_contract__every_published_row_has_a_caller() -> None:
    """Assertion 3. A row that outlives its module is a rule nobody executes."""
    calling = {m for m, _ln, _c in _call_sites()}
    orphans = sorted({r.caller for r in FORMULA_SOURCE_CONTRACT} - calling)
    assert not orphans, (
        f"FORMULA_SOURCE_CONTRACT names {orphans} but no such module calls recalculate(). "
        "Delete the row or restore the caller — a published rule with no execution is the "
        "shape of every defect this project has found in its own instrument."
    )


def test_contract__the_two_sources_are_both_in_use() -> None:
    """The admission-side control. A contract in which every caller says the same thing is a
    contract that would be satisfied by deleting the argument — and the whole point of F19 is
    that the two callers genuinely differ."""
    used = {r.source for r in FORMULA_SOURCE_CONTRACT}
    assert used == {"TEMPLATE", "FILING"}, (
        f"the contract exercises only {sorted(used)}. If every caller wants the same source, "
        "the parameter is ceremony rather than a rule."
    )


def test_contract__the_rule_is_published_in_the_generated_contract() -> None:
    """C8b: here and nowhere else. The section is GENERATED, so this reads the artifact a
    reviewer would read rather than the table the other tests read."""
    text = (REPO / "EVALUATION-CONTRACT.md").read_text(encoding="utf-8")
    assert "## `formula_source` — which formulas 'recalculate' means" in text
    for r in FORMULA_SOURCE_CONTRACT:
        assert f"`{r.caller}`" in text, f"{r.caller} is in the table and not on the page"
    assert not (REPO / "docs" / "RECALCULATION-SOURCE.md").exists(), (
        "C8b: the rule lives in the generated EVALUATION-CONTRACT.md and in no second file."
    )


@pytest.mark.parametrize("bad_source", ["=formula_source=src", "no argument at all"])
def test_contract__the_scan_would_catch_its_own_negation(bad_source: str) -> None:
    """The scan's positive control, as a unit rather than as a claim: feed the analyser the two
    shapes it exists to reject and assert it rejects them. Without this, an analyser that
    returned `"TEMPLATE"` for everything would pass all four tests above."""
    src = (
        "recalculate(f, l, formula_source=src)" if "=" in bad_source
        else "recalculate(f, l)"
    )
    call = ast.parse(src).body[0].value          # type: ignore[attr-defined]
    assert _literal_source(call) is None
