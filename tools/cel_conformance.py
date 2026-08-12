#!/usr/bin/env python
"""P4-B3 — the two-runtime CEL agreement harness (D-P4-04's fallback, and it is labelled as such).

**This is a DIFFERENTIAL, not a CONFORMANCE run**, and every surface that quotes its number says
so. The official suite is textproto driven through a conformance server; D-P4-04 caps that attempt
at two days and names this harness as the fallback. It is weaker for a reason that is not
hypothetical in this project: **two implementations wrong the same way are invisible to a
differential.**

What makes it worth running anyway: the second runtime is `cel-expr-python`, Google's own CEL
runtime with the C++ core — the reference implementation rather than a second interpretation of the
spec. An agreement between `celpy` and that is much stronger evidence than an agreement between two
third-party Python ports would be.

**The error-semantics slice is reported separately, and that is the whole point of the split.** The
CEL specification says an operand error in `&&`/`||` *"will be ignored"* when the other operand
determines the result. If the two runtimes differ THERE, the pre-flight guard's necessity argument
behaves differently between them — so a single blended percentage would hide the one disagreement
that changes a design decision.

    make cel-conformance        # writes docs/measurements/P4-cel-conformance.md
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

OUT = REPO / "docs" / "measurements" / "P4-cel-conformance.md"
JSON_OUT = REPO / "reports" / "p4-cel-conformance.json"

FACTS: dict[str, Any] = {
    "filing": {
        "a": {"b": 1},
        "n": 7,
        "s": "AIF",
        "blank": "",
        "flag": True,
        "rows": [{"x": 1, "c": "S!A1"}, {"x": -2, "c": "S!A2"}, {"x": 0, "c": "S!A3"}],
        "empty": [],
    },
    "template": {"v": {"k": ["AIF", "PMS"]}, "n": 7},
}


@dataclass(frozen=True)
class Case:
    slice: str
    src: str
    why: str = ""


# --- slice A: the admitted grammar's coverage set -------------------------------------
SUBSET: list[Case] = [
    Case("subset", "filing.a.b == 1"),
    Case("subset", "filing.a.b != 2"),
    Case("subset", "filing.n > 0"),
    Case("subset", "filing.n >= 7"),
    Case("subset", "filing.n < 8"),
    Case("subset", "filing.n <= 7"),
    Case("subset", 'filing.s == "AIF"'),
    Case("subset", 'filing.blank == ""'),
    Case("subset", "filing.flag"),
    Case("subset", "!filing.flag"),
    Case("subset", "filing.n + 1 == 8"),
    Case("subset", "filing.n - 1 == 6"),
    Case("subset", "filing.n * 2 == 14"),
    Case("subset", "filing.n / 7 == 1"),
    Case("subset", "filing.n % 2 == 1"),
    Case("subset", "-filing.n == -7"),
    Case("subset", 'filing.s in template.v.k'),
    Case("subset", 'filing.s in ["AIF", "PMS"]'),
    Case("subset", "filing.n == template.n"),
    Case("subset", "filing.flag ? filing.n == 7 : filing.n == 0", "ternary"),
    Case("subset", "has(filing.a.b)"),
    Case("subset", "has(filing.a.zzz)"),
    Case("subset", "size(filing.rows) == 3"),
    Case("subset", "size(filing.empty) == 0"),
    Case("subset", "filing.rows.all(r, r.x >= -2)"),
    Case("subset", "filing.rows.exists(r, r.x < 0)"),
    Case("subset", "filing.rows.exists_one(r, r.x == 0)"),
    Case("subset", "filing.empty.all(r, r.x > 0)", "all([]) is true — NC-Q01's shape"),
    Case("subset", "filing.empty.exists(r, r.x > 0)"),
    Case("subset", "filing.rows.filter(r, r.x < 0).size() == 1"),
    Case("subset", "filing.rows.map(r, r.c).size() == 3"),
    Case("subset", "filing.rows.map(r, r.x)"),
    Case("subset", "filing.rows.filter(r, r.x <= 0).map(r, r.c)"),
    Case("subset", 'filing.rows.all(r, r.c != "")'),
    Case("subset", 'filing["a"]["b"] == 1', "index syntax"),
]

# --- slice B: error semantics, reported on its own -------------------------------------
ERRORS: list[Case] = [
    Case("errors", "true || (1/0 == 1)", "error on the right of ||, absorbed"),
    Case("errors", "(1/0 == 1) || true", "error on the LEFT of || — the discriminating case"),
    Case("errors", "false && (1/0 == 1)", "error on the right of &&, absorbed"),
    Case("errors", "(1/0 == 1) && false", "error on the LEFT of &&"),
    Case("errors", "(1/0 == 1) || false", "no absorbing operand: the error must survive"),
    Case("errors", "(1/0 == 1) && true", "no absorbing operand"),
    Case("errors", "1/0 == 1", "the bare error"),
    Case("errors", "filing.missing.x == 1", "absent key"),
    Case("errors", "true || (filing.missing.x == 1)", "absent key absorbed by ||"),
    Case("errors", "(filing.missing.x == 1) || true", "absent key on the left"),
    Case("errors", "filing.rows.all(r, r.zzz > 0)", "absent field inside a comprehension"),
    Case("errors", "filing.empty.all(r, 1/0 == 1)", "vacuous over an empty list"),
]

ERROR = "<ERROR>"


def _norm(v: Any) -> Any:
    """One comparable Python value. Every error normalises to one token: the SHAPE is what agrees,
    not the wording, and two runtimes will never phrase an error the same way.

    **`celpy.celtypes.BoolType` subclasses `int`.** The first version of this function tested
    `isinstance(v, bool)`, which is False for it, so every celpy boolean fell through to the
    integer branch and became `1` or `0` — and `1 == True` in Python, so the harness reported
    AGREEMENT between `1` and `True` on 40 of 47 rows. A false agreement inside the instrument
    built to detect disagreement. The class check is by type name because celpy is imported
    lazily, and `agree_strict` below refuses cross-type equality outright.
    """
    s = str(v)
    if v is None:
        return ERROR
    if type(v).__name__ in ("BoolType", "bool"):
        return bool(v)
    if isinstance(v, (list, tuple)):
        return [_norm(x) for x in v]
    if type(v).__name__ in ("IntType", "UintType") or isinstance(v, int):
        return int(v)
    if any(s.startswith(p) for p in ("INVALID_ARGUMENT", "NOT_FOUND", "UNKNOWN", "INTERNAL", "OUT_OF_RANGE")):
        return ERROR
    if s in ("true", "false"):
        return s == "true"
    return s


def agree_strict(a: Any, b: Any) -> bool:
    """Equality that will not call `1` equal to `True`.

    Python's `==` does, and that is exactly how this harness once reported agreement between a
    runtime returning integers and one returning booleans.
    """
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(agree_strict(x, y) for x, y in zip(a, b, strict=True))
    if type(a) is not type(b):
        return False
    return a == b


def run_celpy(src: str) -> Any:
    import celpy

    env = celpy.Environment()
    try:
        prog = env.program(env.compile(src))
        return _norm(prog.evaluate(_celpy_facts()))
    except Exception:  # noqa: BLE001 — a program-level failure IS the observation here
        return ERROR


def _celpy_facts() -> Any:
    import celpy

    return {k: celpy.json_to_cel(v) for k, v in FACTS.items()}


def run_reference(src: str) -> Any:
    from cel_expr_python import cel

    env = cel.NewEnv()
    try:
        expr = env.compile(src, disable_check=True)
        value = expr.eval(data=FACTS)
        # `Value.plain_value()` unwraps to a real Python object. Comparing `str(Value)` instead
        # made a LIST look like the string `'[1, -2, 0]'` and reported two false disagreements —
        # a normalisation defect in the harness read as a divergence between the runtimes.
        if str(value.type()) == "ERROR":
            return ERROR
        return _norm(value.plain_value())
    except Exception:  # noqa: BLE001
        return ERROR


def main() -> int:
    try:
        import cel_expr_python  # noqa: F401
    except ImportError:
        print(
            "cel-expr-python is not installed. It is pinned in requirements.lock as a TEST "
            "dependency; a missing one is an environment defect, not a reason to report a "
            "one-runtime number as agreement.",
            file=sys.stderr,
        )
        return 2

    rows = []
    for case in [*SUBSET, *ERRORS]:
        a, b = run_celpy(case.src), run_reference(case.src)
        rows.append({"slice": case.slice, "src": case.src, "why": case.why,
                     "celpy": a, "reference": b, "agree": agree_strict(a, b)})

    by_slice = {}
    for s in ("subset", "errors"):
        sub = [r for r in rows if r["slice"] == s]
        by_slice[s] = {"agree": sum(1 for r in sub if r["agree"]), "total": len(sub)}

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(
        json.dumps({"label": "DIFFERENTIAL", "by_slice": by_slice, "rows": rows},
                   indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    OUT.write_text(_render(rows, by_slice), encoding="utf-8")
    print(f"subset {by_slice['subset']['agree']}/{by_slice['subset']['total']} · "
          f"errors {by_slice['errors']['agree']}/{by_slice['errors']['total']} "
          f"-> {OUT.relative_to(REPO)}")
    return 0


def _render(rows: list[dict], by_slice: dict) -> str:
    from importlib import metadata

    def ver(n: str) -> str:
        try:
            return metadata.version(n)
        except metadata.PackageNotFoundError:
            return "absent"

    s, e = by_slice["subset"], by_slice["errors"]
    lines = [
        "# P4-B3 — CEL runtime agreement",
        "",
        "## DIFFERENTIAL, not CONFORMANCE",
        "",
        "This number is produced by D-P4-04's fallback harness, not by the official CEL",
        "conformance suite. **Two implementations wrong the same way are invisible to a**",
        "**differential**, and that is not hypothetical in this project. Every surface quoting this",
        "figure carries the same label.",
        "",
        "What makes it worth running: the second runtime is **`cel-expr-python`, Google's own CEL",
        "runtime with the C++ core** — the reference implementation, not a second port. Agreement",
        "with it is stronger evidence than agreement between two third-party interpretations.",
        "",
        f"| runtime | version |",
        f"|---|---|",
        f"| `cel-python` (celpy) — **the runtime the registry root is qualified against** | {ver('cel-python')} |",
        f"| `cel-expr-python` (reference, test-only) | {ver('cel-expr-python')} |",
        "",
        "## The two slices, reported separately",
        "",
        "| slice | agreement | what it covers |",
        "|---|---|---|",
        f"| admitted subset | **{s['agree']}/{s['total']}** | every operator, macro and literal form the profile admits |",
        f"| error semantics | **{e['agree']}/{e['total']}** | operand errors under `&&` and `||`, both sides |",
        "",
        "**Why the split is not cosmetic.** The CEL specification says an operand error in `&&`/`||`",
        "*\"will be ignored\"* when the other operand determines the result. If the two runtimes",
        "differ THERE, the pre-flight guard's necessity argument behaves differently between them —",
        "so a single blended percentage would hide the one disagreement that changes a design",
        "decision.",
        "",
        "## Gate G-CELPY",
        "",
        "**The registry root is qualified against `cel-python`**, recorded in",
        "`qualified_against.evaluator_version` on every predicate envelope. The reference runtime is",
        "a check on it, not the thing predicates run on: it is a native extension whose availability",
        "is a platform question, and a verdict path that depends on a wheel building is a verdict",
        "path that can vanish.",
        "",
        "## Every row",
        "",
        "| slice | expression | celpy | reference | agree | note |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        mark = "yes" if r["agree"] else "**NO**"
        lines.append(
            f"| {r['slice']} | `{r['src']}` | `{r['celpy']}` | `{r['reference']}` | {mark} | {r['why']} |"
        )
    disagreements = [r for r in rows if not r["agree"]]
    lines += ["", "## Disagreements", ""]
    if not disagreements:
        lines.append("None on this coverage set. That is not a conformance claim; see the label above.")
    else:
        for r in disagreements:
            lines.append(f"- `{r['src']}` — celpy `{r['celpy']}`, reference `{r['reference']}`. {r['why']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
