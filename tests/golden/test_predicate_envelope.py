"""P4-B1 — the pinned envelope digests.

Per R-GOLD-2 a pinned digest is paired with a **value assertion on the parsed content**: a digest
alone tells a reviewer that something did not change, not that it is right. The value asserted is
D-P4-02's key grammar with the root restored, which is the whole reason the fixture exists.

FME `7d9a1960` is the workbook because it is the only one whose vocabularies live on a hidden,
unprotected `Dropdown` sheet — the case a root-qualified key grammar exists to express.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.canonical import code_sha256  # noqa: E402
from cdfc.predicates.loader import load_candidate, load_predicate  # noqa: E402

GOOD = REPO / "fixtures" / "predicates" / "good"
FME = "7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39"

# MEASURED at P4-B1 and reproduced in docs/measurements/P4-envelope-digests.md. These are
# properties of OUR code (`01` §1.3): they may move, with a recorded reason, and moving one
# without recording it is what this test is here to prevent.
P0041_DIGEST = "cfa3792f3157be6b93d0355778c3ab4be48fc8b7b5d48fb16668fbbab1c6a42f"
P0007_DIGEST = "5848bc8a15234c2c73a620603d97d2a9f243fee9f324176571b6a04405decce3"


def test_golden__envelope__P0041_digest() -> None:
    p = load_candidate(GOOD / "P-0041__scheme-type-membership.yaml")

    # R-GOLD-2: the value assertion beside the digest.
    assert p.schema_keys == (
        "filing.intro.tbl15.rows",
        "filing.intro.tbl15.rows[*].scheme_type",
        "filing.intro.tbl15.rows[*].__cell__",
        "template.vocab.scheme_type",
    ), "D-P4-02's grammar: root included, `[*]` for a comprehension-bound repeated node"
    assert p.template == FME
    assert p.obligation_source == "TEMPLATE" and p.clause is None
    assert p.clause_absent_reason == "derived_from_data_validation"
    assert p.claims_fault_classes == ("F12",), (
        "membership claims F12 and NOT F10: a legal enum substituted for another legal enum is "
        "invisible to a membership test by construction"
    )

    assert code_sha256(p) == P0041_DIGEST


def test_golden__envelope__P0007_digest() -> None:
    p = load_predicate(GOOD / "P-0007__intro-D17-integer-bound.yaml")
    assert p.schema_keys == ("filing.intro.tbl11.n_schemes", "filing.intro.tbl11.__cell__")
    assert p.claims_fault_classes == ("F01", "F03", "F06")
    assert p.state == "PROVISIONAL" and p.severity_tier == "ADVISORY"
    assert code_sha256(p) == P0007_DIGEST


def test_golden__the_measurement_file_carries_both_digests() -> None:
    """A pinned literal a reviewer cannot resolve to a published file is not traceable."""
    doc = (REPO / "docs" / "measurements" / "P4-envelope-digests.md").read_text(encoding="utf-8")
    for d in (P0041_DIGEST, P0007_DIGEST):
        assert d in doc, f"{d} is pinned in a golden but not published in the measurement file"
