"""P9-B2 — the two checker self-tests. **Neither is ever reported to the filer.**

A self-test measures US. Putting it on the filer's report would put a finding about our apparatus
into a document about their filing, and `settledFraction` would count a cell nobody filed.
`reported_to_filer = False` is enforced by the loader, not by convention.

**These two are NOT CEL, and that is a distinction the registry carries rather than hides.**
`cel_profile.BOUND_ROOTS` is `{filing, template}` — a third free identifier is refused at compile
time, deliberately, because it is how a predicate reads something nobody declared. A self-test's
subject is neither the filing nor the template: it is the run's own record. So a `SELF_TEST`
relation's `expr` names a dotted Python callable, `expr_language` is `PYTHON`, and
`test_reg__self_test_expressions_are_python_and_the_rest_are_cel` asserts the two never mix.
Widening the CEL subset to let a self-test address the run would open the same door for a
predicate about the filing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Final

DENOMINATOR_EVIDENCE: Final[str] = (
    "Barrier 1 (G-DENOM). The field surface is computed twice by independent paths — "
    "`schema/styles_mask.py` and `schema/styles_mask_b.py` — and `docs/measurements/"
    "P2-field-surface.md` publishes 9 of 9 agreeing. The denominator of the product's headline "
    "number is the one quantity a single implementation must not be trusted with."
)

CANARY_EVIDENCE: Final[str] = (
    "§0.4 and P10-B1. The attestation reports `canariesRun` as an integer; if that integer is not "
    "the number of canary rows actually written to `run.jsonl`, the liveness proof is a claim "
    "about a loop nobody can count. A merged count would let a kill-case failure hide behind an "
    "anti-canary success."
)


class SelfTestUnavailable(RuntimeError):
    """The self-test's subject does not exist yet. Reported, never assumed to pass."""


def denominator_agrees(blank: Path) -> tuple[bool, str]:
    """R-05. The two independent field-surface computations agree on the pinned blank.

    Returns `(held, detail)`. It does not raise on disagreement: a disagreement is the FINDING,
    and a self-test that crashed would be reported as an apparatus error rather than as the
    result it is.
    """
    from cdfc.schema import styles_mask_b
    from cdfc.schema.styles_mask import Rule, build

    a = build(blank, Rule.V3).n_cells
    b = styles_mask_b.count_field_surface(blank)
    b_n = b[0] if isinstance(b, tuple) else b
    return a == b_n, f"styles_mask={a} styles_mask_b={b_n}"


def canary_population_agrees(run_record: Any = None) -> tuple[bool, str]:
    """R-06. `canaries_run` equals the number of canary rows written to `run.jsonl`.

    **The subject arrives at P10-B1.** Until then this returns `(False, …)` with a detail naming
    the phase — not `(True, …)`, because a self-test that passes by having nothing to check is the
    vacuous pass this whole layer exists to refuse, committed by the catcher.
    """
    if run_record is None:
        raise SelfTestUnavailable(
            "the canary loop is P10-B1; there is no canary population to count at P9. This "
            "relation is in the catalogue, reviewed and un-runnable, and it reports so."
        )
    declared = int(getattr(run_record, "canaries_run", 0))
    rows = len(getattr(run_record, "canary_rows", ()) or ())
    return declared == rows, f"declared={declared} rows={rows}"
