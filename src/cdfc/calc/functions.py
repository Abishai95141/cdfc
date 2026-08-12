"""The function vocabulary — one module-level callable per Excel function.

Scoped by MEASUREMENT, not by guesswork: `tools/measure/function_census.py` counts what
the nine prescribed workbooks actually use. Twenty distinct functions appear; the ones
below cover every occurrence.

An unimplemented function is `NOT_RUN(unimplemented: NAME)` — never a guess, and never
swallowed. `IFERROR` around an unimplemented call must NOT convert it into a value:
IFERROR catches Excel ERRORS, and "we did not implement this" is not one. Conflating them
is how an evaluator comes to report a clean number for a formula it cannot compute.

Every numeric path is `Decimal` under a pinned context. There is no float anywhere in this
package and `ci/no-float-money.sh` fails the build if one appears.
"""

from __future__ import annotations

import datetime as _dt
from collections.abc import Callable, Iterable, Sequence
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation, localcontext
from typing import Any

from cdfc.calc.errors import DIV0, NA, NUM, VALUE, ExcelError, first_error, is_error

PRECISION = 34  # IEEE 754-2008 decimal128, which is what a spreadsheet engine models


class Unimplemented(Exception):
    """A function we do not implement. Surfaces as NOT_RUN, never as a value."""

    def __init__(self, name: str) -> None:
        super().__init__(f"unimplemented: {name}")
        self.name = name


def _nums(vals: Iterable[Any]) -> list[Decimal]:
    """Excel's coercion for numeric aggregates: text and blanks are SKIPPED, not zeroed."""
    out: list[Decimal] = []
    for v in vals:
        if v is None or isinstance(v, bool) or is_error(v):
            continue
        if isinstance(v, Decimal):
            out.append(v)
        elif isinstance(v, int):
            out.append(Decimal(v))
        elif isinstance(v, str):
            s = v.strip()
            if not s:
                continue
            try:
                out.append(Decimal(s))
            except InvalidOperation:
                continue
    return out


def _flat(args: Sequence[Any]) -> list[Any]:
    out: list[Any] = []
    for a in args:
        if isinstance(a, (list, tuple)):
            out.extend(_flat(a))
        else:
            out.append(a)
    return out


# --------------------------------------------------------------------------------
# the vocabulary
# --------------------------------------------------------------------------------


def SUM(*args: Any) -> Any:
    flat = _flat(args)
    if (e := first_error(*flat)) is not None:
        return e
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return sum(_nums(flat), Decimal(0))


def ROUND(value: Any, digits: Any = Decimal(0)) -> Any:
    if (e := first_error(value, digits)) is not None:
        return e
    nums = _nums([value])
    if not nums:
        return VALUE
    d = _nums([digits])
    places = int(d[0]) if d else 0
    with localcontext() as ctx:
        ctx.prec = PRECISION
        q = Decimal(1).scaleb(-places)
        # Excel rounds half AWAY FROM ZERO. Python's default is half-to-even, and the
        # difference shows on exactly the .5 cases a filer's totals land on.
        return nums[0].quantize(q, rounding=ROUND_HALF_UP)


def IF(cond: Any, then: Any = True, otherwise: Any = False) -> Any:
    if is_error(cond):
        return cond
    truthy = bool(cond) if not isinstance(cond, Decimal) else cond != 0
    return then if truthy else otherwise


def IFERROR(value: Any, fallback: Any) -> Any:
    """Catches EXCEL ERRORS ONLY.

    `Unimplemented` is deliberately not caught here — it propagates out of the evaluator
    as NOT_RUN. An IFERROR that swallowed it would turn "we cannot compute this" into a
    clean fallback value, which is this project's failure mode inside a formula.
    """
    return fallback if is_error(value) else value


def COUNTIF(rng: Any, criterion: Any) -> Any:
    cells = _flat([rng])
    crit = criterion
    if isinstance(crit, str):
        c = crit.strip().strip('"')
        if c.startswith("*") and c.endswith("*") and len(c) > 1:
            needle = c.strip("*").lower()
            return Decimal(sum(1 for v in cells if isinstance(v, str) and needle in v.lower()))
        if c.startswith("*"):
            needle = c.lstrip("*").lower()
            return Decimal(sum(1 for v in cells if isinstance(v, str) and v.lower().endswith(needle)))
        if c.endswith("*"):
            needle = c.rstrip("*").lower()
            return Decimal(sum(1 for v in cells if isinstance(v, str) and v.lower().startswith(needle)))
        return Decimal(sum(1 for v in cells if isinstance(v, str) and v.lower() == c.lower()))
    target = _nums([crit])
    if not target:
        return Decimal(0)
    return Decimal(sum(1 for v in _nums(cells) if v == target[0]))


def ROWS(rng: Any) -> Any:
    cells = _flat([rng])
    return Decimal(len(cells))


def ROW(ref: Any = None) -> Any:
    """ROW() with no argument is the caller's own row; the evaluator supplies it."""
    if ref is None:
        raise Unimplemented("ROW() without an explicit reference")
    return ref


def AND(*args: Any) -> Any:
    flat = _flat(args)
    if (e := first_error(*flat)) is not None:
        return e
    return all(bool(v) for v in flat if v is not None)


def OR(*args: Any) -> Any:
    flat = _flat(args)
    if (e := first_error(*flat)) is not None:
        return e
    return any(bool(v) for v in flat if v is not None)


def MOD(a: Any, b: Any) -> Any:
    if (e := first_error(a, b)) is not None:
        return e
    na, nb = _nums([a]), _nums([b])
    if not na or not nb:
        return VALUE
    if nb[0] == 0:
        return DIV0
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return na[0] % nb[0]


def CONCAT(*args: Any) -> Any:
    flat = _flat(args)
    if (e := first_error(*flat)) is not None:
        return e
    return "".join("" if v is None else str(v) for v in flat)


def _as_date(v: Any) -> _dt.date | None:
    if isinstance(v, _dt.date):
        return v
    n = _nums([v])
    if not n:
        return None
    # the 1900 serial system, with Excel's 1900-leap-year bug preserved
    return _dt.date(1899, 12, 30) + _dt.timedelta(days=int(n[0]))


def YEAR(v: Any) -> Any:
    d = _as_date(v)
    return VALUE if d is None else Decimal(d.year)


def MONTH(v: Any) -> Any:
    d = _as_date(v)
    return VALUE if d is None else Decimal(d.month)


def DAY(v: Any) -> Any:
    d = _as_date(v)
    return VALUE if d is None else Decimal(d.day)


def DATE(y: Any, m: Any, d: Any) -> Any:
    ny, nm, nd = _nums([y]), _nums([m]), _nums([d])
    if not (ny and nm and nd):
        return VALUE
    try:
        dt = _dt.date(int(ny[0]), int(nm[0]), int(nd[0]))
    except ValueError:
        return NUM
    return Decimal((dt - _dt.date(1899, 12, 30)).days)


def INDEX(array: Any, row_num: Any, col_num: Any = None) -> Any:
    cells = _flat([array])
    n = _nums([row_num])
    if not n:
        return VALUE
    i = int(n[0])
    if i < 1 or i > len(cells):
        return ExcelError.__call__(NA.kind) if False else NA
    return cells[i - 1]


def AGGREGATE(fn: Any, options: Any, *rest: Any) -> Any:
    """AGGREGATE(function_num, options, ...).

    Only function 15 (SMALL) is implemented, because that is the only one the corpus uses
    — measured, not assumed. Any other function number is Unimplemented rather than
    approximated, because an aggregate silently computing the wrong statistic is a clean
    confident wrong answer.
    """
    n = _nums([fn])
    if not n:
        return VALUE
    which = int(n[0])
    if which != 15:
        raise Unimplemented(f"AGGREGATE function_num={which}")
    if len(rest) < 2:
        return VALUE
    vals = sorted(_nums(_flat([rest[0]])))
    k = _nums([rest[1]])
    if not k:
        return VALUE
    i = int(k[0])
    if i < 1 or i > len(vals):
        return NUM
    return vals[i - 1]


def TODAY() -> Any:
    """A clock in the artifact.

    Refused rather than evaluated: a formula whose value changes daily cannot be
    re-derived, and this system's whole claim is that a report re-derives byte-identically.
    The cell becomes NOT_RUN with a reason, and that reason is visible.
    """
    raise Unimplemented("TODAY() — a clock in the artifact cannot be re-derived")


def SINGLE(v: Any) -> Any:
    """The implicit-intersection operator (@). Identity on a scalar."""
    flat = _flat([v])
    if len(flat) == 1:
        return flat[0]
    raise Unimplemented("SINGLE over a multi-cell range")


def DATEVALUE(v: Any) -> Any:
    if not isinstance(v, str):
        return VALUE
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            d = _dt.datetime.strptime(v.strip(), fmt).date()
        except ValueError:
            continue
        return Decimal((d - _dt.date(1899, 12, 30)).days)
    return VALUE


VOCABULARY: dict[str, Callable[..., Any]] = {
    "SUM": SUM, "ROUND": ROUND, "IF": IF, "IFERROR": IFERROR, "COUNTIF": COUNTIF,
    "ROWS": ROWS, "ROW": ROW, "AND": AND, "OR": OR, "MOD": MOD, "CONCAT": CONCAT,
    "YEAR": YEAR, "MONTH": MONTH, "DAY": DAY, "DATE": DATE, "INDEX": INDEX,
    "AGGREGATE": AGGREGATE, "TODAY": TODAY, "SINGLE": SINGLE, "DATEVALUE": DATEVALUE,
}
