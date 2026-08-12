"""`sum(list<int>) -> int` — the only arithmetic aggregation the subset admits.

CEL has no `sum` macro, so summation is a host function rather than a language feature. That is
the better place for it anyway: it is where the refusal to accept a float lives, and a float in a
sum is how a money total acquires a tolerance nobody declared.
"""

from __future__ import annotations

from typing import Any

from celpy import celtypes

from cdfc.predicates.host_fns import HostFn, vector_digest

NAME = "sum"
VERSION = "1"
SIGNATURE = "sum(list<int>) -> int"


def sum_units(values: Any) -> Any:
    total = 0
    for v in values:
        # An integer, and nothing that merely converts to one. The first version refused floats
        # and blanks by name and fell through to `int(v)` for everything else — so `sum(["12"])`
        # silently coerced a string in a numeric column. The mutation harness found the guard was
        # not distinguishable by any published vector, which is how the coercion surfaced.
        # A blank is not zero: that is F05's blank-and-zero conflation, and the taxonomy carries
        # it as two operators rather than one.
        if isinstance(v, bool) or not isinstance(v, int):
            raise TypeError(
                f"sum() takes integers and met {type(v).__name__}. Money is an int64 count of "
                "10^-3 USD Million; a coercion here is a rounding decision nobody recorded, and "
                "a blank summed as zero is a fact nobody wrote."
            )
        total += v
    return celtypes.IntType(total)


def register_into(reg: Any) -> None:
    reg.register(HostFn(
        name=NAME, version=VERSION, signature=SIGNATURE, returns_tristate=False,
        fn=sum_units, test_vector_sha256=vector_digest(NAME),
        mutation_score_json=f"reports/host_fns/{NAME}.mutation.json",
        authored_by="cdfc P4-B3",
    ))
