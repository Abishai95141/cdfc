"""P12-B1 — **the pre-registration's tables are a round trip, not a transcription.**

`PREREGISTRATION.md` is the one artifact in this build whose entire epistemic value is that it was
fixed before the model ran. A figure edited by hand after the fact would be invisible: the document
reads exactly the same either way. So the tables are parsed back OUT of the committed markdown and
compared to `power.power_table().as_markdown()` — **a hand-edited cell fails the build rather than
the review**, which is the only version of that commitment that does not depend on a reader.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment.power import (  # noqa: E402
    DELETE1,
    N1,
    _r3,
    cdf,
    power_table,
)

PREREG = REPO / "experiments" / "E6" / "PREREGISTRATION.md"
SPEC = REPO / "spec" / "04-path.md"

# The section boundary. Only §6 is generated, and comparing the WHOLE document's tables would fold
# in §3's generation parameters and §3's prompt hashes — three tables the power module does not
# produce and never should.
SECTION_START = "## 6. The power tables"
SECTION_END = "**Three consequences"


def _tables(text: str) -> set[tuple[str, ...]]:
    """Every markdown table in `text`, each as the tuple of its rows.

    Structural, not a regex over the whole blob: a table is a maximal run of lines beginning `|`.
    Comparing sets of row-tuples means a reordered table still matches and a changed digit does not,
    which is the discrimination this test needs and the one a substring scan would not have.
    """
    out: set[tuple[str, ...]] = set()
    block: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            block.append(stripped)
        elif block:
            out.add(tuple(block))
            block = []
    if block:
        out.add(tuple(block))
    return out


def test_e6__power_table_matches_preregistration() -> None:
    """**THE ROUND TRIP.** The committed §6 equals `power_table().as_markdown()`, cell for cell.

    Without it the document and the generator are two statements of the same numbers, and the one
    that drifts is the one nobody re-runs. `P(X ≤ 2 | n = 20, p = 0.30)` is the figure that already
    went wrong once upstream (§7), and it went wrong by exactly one digit in a table nobody
    recomputed.
    """
    doc = PREREG.read_text(encoding="utf-8")
    start, end = doc.index(SECTION_START), doc.index(SECTION_END)
    committed = _tables(doc[start:end])
    generated = _tables(power_table().as_markdown())

    assert len(generated) == 4, (
        f"the generator emitted {len(generated)} tables, not the four §6 carries — the comparison "
        "below would be over a set nobody checked"
    )
    assert committed == generated, (
        "the committed pre-registration and `power.power_table()` disagree.\n"
        f"only in the document: {sorted(committed - generated)}\n"
        f"only in the generator: {sorted(generated - committed)}\n"
        "A hand-edited figure in the pre-registration is the one edit that leaves no trace in the "
        "document's own prose."
    )


def test_e6__preregistration_carries_the_correction_notice() -> None:
    """§7 — the `0.036 → 0.035` correction, **naming the spec section it corrects.**

    A silently-applied correction and an edited pre-registration are indistinguishable to a reader
    with the specification open: both look like a document whose numbers do not match the source.
    The notice is what separates them, and it must name *where* — a correction that does not say
    what it corrects sends the reader to grep and is quietly dropped at the next edit.

    Both directions are asserted. The specification really does print `0.036` at that cell, so the
    notice describes a real disagreement rather than a defensive footnote; and `0.036` appears
    **nowhere in the pre-registration's own tables**, so the correction was applied as well as
    announced.
    """
    doc = PREREG.read_text(encoding="utf-8")
    assert "spec/04-path.md" in doc and "§1.1" in doc, (
        "the correction does not name the section it corrects"
    )
    assert "0.036" in doc and "0.035483" in doc, (
        "the correction must carry both the printed figure and the exact value it is wrong about"
    )

    # The source really is wrong, at that cell. Otherwise §7 is a footnote about nothing.
    assert "| 0.30 | 0.416 | 0.036 |" in SPEC.read_text(encoding="utf-8"), (
        "spec/04-path.md §1.1 no longer prints 0.036, so the correction notice describes a "
        "disagreement that does not exist — and a stale correction reads as a live one"
    )

    # And the corrected value is what the exact arithmetic actually produces.
    assert _r3(cdf(DELETE1, N1, Fraction(3, 10))) == "0.035"

    only_in_the_notice = [
        line for line in doc.splitlines() if "0.036" in line and not line.startswith("|")
    ]
    in_a_table = [line for line in doc.splitlines() if "0.036" in line and line.startswith("|")]
    assert only_in_the_notice and not in_a_table, (
        f"0.036 reached a table in the pre-registration: {in_a_table}. The correction was "
        "announced and not applied, which is worse than either alone."
    )


def test_e6__the_committed_preregistration_equals_its_generator_byte_for_byte() -> None:
    """The whole document, not only its tables. **This is the check that was missing.**

    `test_e6__power_table_matches_preregistration` above compares the power tables, and it passed
    while the committed document and `tools/e6/preregister.py` had genuinely diverged: three
    sentences of prose had been edited in the generator (to clear `ci/no-bare-rate.sh`) and never
    regenerated on disk. Nothing caught it in the tree. **The fresh clone caught it** — re-running
    the generator there produced a different `h0` and `lock()` refused, which is the refusal working
    exactly as designed and finding a real drift rather than a hypothetical one.

    A partial contract test is worse than none here, because it reports that a generated document
    equals its generator while checking a fifth of it. The tables were the part nobody would edit by
    hand; the prose was the part somebody did.
    """
    from pathlib import Path
    import sys

    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))
    from tools.e6.preregister import render

    on_disk = (repo / "experiments" / "E6" / "PREREGISTRATION.md").read_text(encoding="utf-8")
    assert on_disk == render(), (
        "experiments/E6/PREREGISTRATION.md is not what tools/e6/preregister.py produces. Run "
        "`make preregister`. A pre-registration that has drifted from its generator is a "
        "pre-registration whose hash protects a document nobody can re-derive."
    )
