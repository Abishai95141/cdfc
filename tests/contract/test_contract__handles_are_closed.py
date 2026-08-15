"""Every workbook and zip opened under `src/cdfc/` is closed. **By AST, not by grep.**

## Why this exists, and why it is a contract test rather than a note

An unclosed handle here does not cost a file descriptor. It costs a **`ResourceWarning` raised by
the garbage collector at whatever line happens to be executing when the finaliser runs** — and
under this repo's `filterwarnings = ["error"]` that fails an *unrelated* test and points the reader
at innocent code.

**It has now happened twice.**

| when | where | what it accused |
|---|---|---|
| P4 | `ingest/reader_openpyxl.py` — two workbooks, neither closed | an unrelated test, after a new dependency shifted collection order |
| P14-B2 | `qualify/template_instrument.py::_party_b` — one workbook, never closed | `ingest/reader_lxml.py:244`, a module that closes everything it opens |

The second took a full-suite run to surface, because with prompt collection the finaliser runs
inside its own test where nothing is watching. That is the worst property a defect can have: it is
invisible in isolation and blames a stranger in aggregate.

**So the rule is structural.** A call to `openpyxl.load_workbook` or `zipfile.ZipFile` under
`src/cdfc/` must have its result closed — through a `with` statement, through `contextlib.closing`,
or through an explicit `.close()` in the same function. A grep would have to read the shape of the
code; this walks it.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src" / "cdfc"

OPENERS = {"load_workbook", "ZipFile"}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute):
            return f.attr
        if isinstance(f, ast.Name):
            return f.id
    return None


def _managed_calls(tree: ast.AST) -> set[int]:
    """Every opener call that is syntactically inside a `with` header, possibly via `closing()`."""
    ok: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.With, ast.AsyncWith)):
            continue
        for item in node.items:
            expr = item.context_expr
            for sub in ast.walk(expr):
                if _call_name(sub) in OPENERS:
                    ok.add(id(sub))
    return ok


def _closed_names(tree: ast.AST) -> set[str]:
    """Names that are `closing(name)`d or `.close()`d anywhere in the module."""
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr == "close" and isinstance(f.value, ast.Name):
                out.add(f.value.id)
            if isinstance(f, ast.Name) and f.id == "closing":
                for a in node.args:
                    if isinstance(a, ast.Name):
                        out.add(a.id)
            if isinstance(f, ast.Attribute) and f.attr == "closing":
                for a in node.args:
                    if isinstance(a, ast.Name):
                        out.add(a.id)
    return out


def test_contract__every_workbook_and_zip_under_src_is_closed() -> None:
    offenders: list[str] = []
    scanned = 0
    for py in sorted(SRC.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        managed = _managed_calls(tree)
        closed = _closed_names(tree)
        for node in ast.walk(tree):
            if _call_name(node) not in OPENERS:
                continue
            scanned += 1
            if id(node) in managed:
                continue
            # `x = ZipFile(...)` is admissible when `x` is later closed or `with x:`-ed.
            parent_assign = next(
                (a for a in ast.walk(tree)
                 if isinstance(a, ast.Assign) and a.value is node
                 and any(isinstance(t, ast.Name) for t in a.targets)),
                None,
            )
            if parent_assign is not None:
                names = {t.id for t in parent_assign.targets if isinstance(t, ast.Name)}
                if names & closed or any(
                    isinstance(w, (ast.With, ast.AsyncWith))
                    and any(isinstance(i.context_expr, ast.Name) and i.context_expr.id in names
                            for i in w.items)
                    for w in ast.walk(tree)
                ):
                    continue
            offenders.append(
                f"{py.relative_to(REPO)}:{node.lineno}: "
                f"{_call_name(node)}() result is never closed"
            )

    assert scanned > 0, "no opener was found at all; this assertion would be vacuous"
    assert offenders == [], (
        "an unclosed handle under src/cdfc/:\n  " + "\n  ".join(offenders)
        + "\nIt does not cost a descriptor — it costs a ResourceWarning raised wherever the "
        "collector happens to be, which under filterwarnings=['error'] fails an UNRELATED test "
        "and blames innocent code. This has happened twice: reader_openpyxl at P4 and "
        "template_instrument at P14-B2."
    )


def test_contract__the_scan_reaches_the_known_openers() -> None:
    """THE ADMISSION-SIDE CONTROL: the walk finds the openers that exist.

    Without it, a walk that matched nothing would pass the test above while checking nothing —
    which is this project's own recurring defect, and it would be occurring inside the guard
    written for a different one.
    """
    found: set[str] = set()
    for py in sorted(SRC.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        for node in ast.walk(ast.parse(py.read_text(encoding="utf-8"))):
            if _call_name(node) in OPENERS:
                found.add(py.relative_to(REPO).as_posix())
    assert "src/cdfc/ingest/reader_openpyxl.py" in found
    assert "src/cdfc/qualify/template_instrument.py" in found
    assert "src/cdfc/ingest/container_guard.py" in found
