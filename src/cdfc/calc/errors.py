"""Excel error values as first-class objects.

An error is a VALUE in Excel, not an exception: `IFERROR(1/0, "x")` returns `"x"`, and
`SUM(A1:A3)` where A2 is `#DIV/0!` returns `#DIV/0!`. Modelling errors as Python
exceptions would make the first case impossible and the second silently wrong.

They compare unequal to everything including themselves-by-value, so an error can never
satisfy a predicate by accident.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ErrorKind(StrEnum):
    DIV0 = "#DIV/0!"
    NA = "#N/A"
    VALUE = "#VALUE!"
    REF = "#REF!"
    NUM = "#NUM!"
    NAME = "#NAME?"


@dataclass(frozen=True)
class ExcelError:
    kind: ErrorKind

    def __str__(self) -> str:
        return str(self.kind)

    def __bool__(self) -> bool:
        # An error is never truthy. A predicate reading `if cell:` must not treat
        # #DIV/0! as a satisfied condition.
        return False


DIV0 = ExcelError(ErrorKind.DIV0)
NA = ExcelError(ErrorKind.NA)
VALUE = ExcelError(ErrorKind.VALUE)
REF = ExcelError(ErrorKind.REF)
NUM = ExcelError(ErrorKind.NUM)
NAME = ExcelError(ErrorKind.NAME)

BY_TEXT = {str(e): e for e in (DIV0, NA, VALUE, REF, NUM, NAME)}


def is_error(v: object) -> bool:
    return isinstance(v, ExcelError)


def first_error(*vals: object) -> ExcelError | None:
    """Excel's propagation rule: the first error in argument order wins."""
    for v in vals:
        if isinstance(v, ExcelError):
            return v
    return None
