"""`nav_interval(scheme_type, open_closed, tenure) -> string` — and it MUST be able to say
`UNDERSPECIFIED`.

**The third value is the whole point of this function.** Regulation 51(1) makes the owed NAV
frequency, in part, *"in such manner as specified by the Authority"* — and for **close-ended
Restricted Schemes** the 29th IFSCA Authority Meeting of 24 July 2026 made it depend on approval by
investors holding 75% by value, **which the workbook does not collect**. There is no fact in the  # rate-ok: a regulatory threshold quoted from reg 51(1), not a rate this build computed
filing that determines the answer.

An item over an `UNDERSPECIFIED` interval becomes `NO_PREDICATE(no_predicate.no_obligation_specified)`
and **never** `no_predicate.not_yet_synthesised`. Conflating *the regulator did not legislate this*
with *we have not got round to it* is the most misleading thing this report could do: the first is
a fact about the rulebook, the second is a fact about our backlog, and only one of them is the
filer's problem.

A two-valued version of this function would have to pick `P6M` or `P1Y` for that case, and the
report would then present our guess as the rule.
"""

from __future__ import annotations

from typing import Any

from celpy import celtypes

from cdfc.predicates.host_fns import UNDERSPECIFIED, HostFn, vector_digest

# THE TWO KINDS OF UNKNOWN, and keeping them apart is the plan's own rule applied here.
#
#   UNDERSPECIFIED      the REGULATOR did not determine it -> no_predicate.no_obligation_specified
#   UNKNOWN_COMBINATION WE have no row for this combination -> no_predicate.not_yet_synthesised
#
# One is a fact about the rulebook and the other is a fact about our backlog, and only the first
# is the filer's problem. Returning one token for both was also BEHAVIOURALLY REDUNDANT — the
# mutation harness showed the close-ended-Restricted branch could be flipped to `!=` with no
# observable effect, because the table returned the same token anyway. Splitting the tokens made
# the branch load-bearing and killed the mutant, which is the honest way round: the test did not
# get stronger, the code got more truthful.
UNKNOWN_COMBINATION = "UNKNOWN_COMBINATION"

NAME = "nav_interval"
VERSION = "1"
SIGNATURE = "nav_interval(string, string, string) -> string"

# What the regulation determines WITHOUT reference to a fact the workbook does not collect.
# Everything else is UNDERSPECIFIED, and the list is short on purpose: it is easier to add a row
# with an authority than to notice a row that should never have been there.
_DETERMINED: dict[tuple[str, str], str] = {
    ("RETAIL", "OPEN"): "P1M",
    ("RETAIL", "CLOSE"): "P3M",
    ("NON-RETAIL", "OPEN"): "P3M",
    ("NON-RETAIL", "CLOSE"): "P6M",
    ("VENTURE-CAPITAL", "CLOSE"): "P1Y",
}


def _norm(v: Any) -> str:
    return str(v).strip().upper().replace("-ENDED", "").replace(" ", "-")


def nav_interval(scheme_type: Any, open_closed: Any, tenure: Any) -> Any:
    st, oc = _norm(scheme_type), _norm(open_closed)
    oc = "OPEN" if oc.startswith("OPEN") else ("CLOSE" if oc.startswith("CLOSE") else oc)
    if st == "RESTRICTED" and oc == "CLOSE":
        # The 75%-by-value investor approval is not a field of this workbook.  # rate-ok: a threshold in the rule, not a measurement
        return celtypes.StringType(UNDERSPECIFIED)
    return celtypes.StringType(_DETERMINED.get((st, oc), UNKNOWN_COMBINATION))


def register_into(reg: Any) -> None:
    reg.register(HostFn(
        name=NAME, version=VERSION, signature=SIGNATURE, returns_tristate=True,
        fn=nav_interval, test_vector_sha256=vector_digest(NAME),
        mutation_score_json=f"reports/host_fns/{NAME}.mutation.json",
        authored_by="cdfc P4-B3",
    ))
