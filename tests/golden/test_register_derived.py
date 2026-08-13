"""P8-B2 — the REGISTER-DERIVED oracle, pinned by value.

**Both halves, and the gap between them is the exhibit.** The obvious format regex fires on 87 of
229 live registration numbers — every one a false failure — and set membership under the declared
normalisation fires on 0. A repair that passed only the first has replaced a false number with no
number; one that passed only the second is a reject-everything baseline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.corpus import register_derived as R  # noqa: E402

EXHIBIT = REPO / "fixtures/baselines/register-regex-ffr.json"

N = 229
FORMAT_FIRES = 87
STRAGGLERS = (
    "100",
    "IFSCA/FME/III/2022‑23/037",   # U+2011 — NOT U+002D
    "IFSCA/FME/IV/2023-24/033",
)


@pytest.fixture(scope="module")
def snapshot():
    return R.load(REPO / "fixtures/register")


def test_golden__format_regex_fires_on_87_of_229(snapshot):
    """**Both integers pinned.** Fetched first-hand on 13 Aug 2026; the specification's
    `87 of 228` came from a lane whose fetch lost one record, and the 87 reproduces."""
    assert snapshot.n == N
    assert snapshot.n_resolving() == N, "the predicate is SATISFIABLE — that is what makes 87 a "
    assert len(R.format_regex_fires(snapshot)) == FORMAT_FIRES


def test_golden__register_membership_admits(snapshot):
    """**THE ADMISSION-SIDE TWIN.** Set membership under the declared normalisation fires on 0 of
    229 — the admitted predicate cannot have a true positive in this population."""
    assert R.membership_fires(snapshot) == ()


def test_golden__the_three_stragglers(snapshot):
    """R-GOLD-2 value assertion, and the second one is byte-distinguishable from its U+002D twin."""
    found = tuple(sorted(n for n, _t in R.stragglers(snapshot)))
    assert found == tuple(sorted(STRAGGLERS))

    homoglyph = next(n for n in found if n.startswith("IFSCA/FME/III"))
    assert "‑" in homoglyph, "the LIVE registration number carries a NON-BREAKING HYPHEN"
    assert "-" not in homoglyph
    twin = homoglyph.replace("‑", "-")
    assert twin != homoglyph and R.FORMAT_REGEX.match(twin), (
        "its U+002D twin matches the regex; the live one does not. That single codepoint is the "
        "difference between a valid entity and a false failure."
    )


def test_golden__the_homoglyph_is_why_the_instrument_refuses_to_unify_dashes(snapshot):
    """The connection between this oracle and P7's text source, asserted rather than asserted-in-prose.

    `textsource.normalise` REFUSES to fold dashes, and this is the evidence: a homoglyph appears in
    a live regulatory identifier. A normaliser that unified them would make
    `test_g0__verbatim_quote_required` unfailable — the gate that catches exactly this.
    """
    from cdfc.qualify.textsource import REFUSED_TRANSFORMATIONS, normalise

    assert "unify_dashes" in {name for name, _why in REFUSED_TRANSFORMATIONS}
    homoglyph = next(n for n, _t in R.stragglers(snapshot) if "‑" in n)
    assert normalise(homoglyph) != normalise(homoglyph.replace("‑", "-")), (
        "the instrument text keeps them distinct"
    )
    # …and the MEMBERSHIP boundary folds them, which is the other half of the design.
    assert R.normalise(homoglyph) == R.normalise(homoglyph.replace("‑", "-"))


def test_golden__the_exhibit_ships_as_a_fixture(snapshot):
    """*"It ships as a fixture, not as an anecdote."* And the fixture agrees with a recomputation."""
    doc = json.loads(EXHIBIT.read_text(encoding="utf-8"))
    assert doc["n"] == N and doc["format_regex_fires"] == FORMAT_FIRES
    assert doc["membership_fires"] == 0
    assert doc["snapshot_sha8"] == snapshot.sha256, "the exhibit cites a snapshot that is not here"
    assert len(doc["stragglers"]) == 3
    assert any("U+2011" in s["codepoints_of_non_alphanumerics"] for s in doc["stragglers"])


def test_golden__a_missing_snapshot_does_not_degrade_to_a_format_guess(tmp_path):
    """NC-X01's shape. A membership check resolves against a SNAPSHOT or it does not resolve."""
    with pytest.raises(R.SnapshotMissing, match="does not degrade to a format guess"):
        R.load(tmp_path)
