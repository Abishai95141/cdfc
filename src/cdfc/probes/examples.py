"""P9-B3 — `@example` pins. **APPEND-ONLY: one entry per real defect ever found.**

Methodology §1.2: every real defect found in review is pinned as an example, so the search can
never again have to *find* it. A search that has to rediscover a known defect will eventually fail
to, on the run where the budget is tight or the seed is unlucky, and the regression will present
as a flake rather than as a failure.

**A removed entry fails the build** (`test_examples__every_real_defect_is_pinned`). Entries are
never edited: a defect whose description changes is a second entry, because the first one is what
somebody actually saw.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Pin:
    id: str
    found_at: str          # the phase and build
    dated: str
    subject: str           # the module or relation the defect was in
    defect: str
    example: str           # the smallest input that reproduces it
    guard: str             # the test that keeps it dead


PINS: Final[tuple[Pin, ...]] = (
    Pin(
        id="EX-01",
        found_at="P9-B1",
        dated="2026-08-14",
        subject="cdfc.probes.template_diff.template_diff",
        defect=(
            "The precedent map's keys are `\"Sheet!Ref\"` strings and `recalculate` takes "
            "`(sheet, ref)` tuples. Passing the map straight through does not raise: it reads "
            "`key[0]` as the sheet name and gets the first CHARACTER, so every reference resolves "
            "against a sheet that does not exist and every cell comes back absent."
        ),
        example="template_diff(filed_values(CLEAN), pm, defects) on any clean filing",
        guard="tests/unit/test_probe_template_diff.py::test_td__fires_on_zero_cells_of_a_filing_the_product_did_not_compute",
    ),
    Pin(
        id="EX-02",
        found_at="P9-B1",
        dated="2026-08-14",
        subject="cdfc.probes.template_diff.template_diff",
        defect=(
            "A cell absent from BOTH `grid.values` and `grid.not_run` was compared against the "
            "filed value as though the recomputation had produced `None`. That turns *our "
            "apparatus said nothing* into *your filing is wrong* — the inversion "
            "`error.predicate_raised` and `not_run.source_unreadable` exist to keep apart."
        ),
        example="'1. Introduction'!C75, whose IFERROR/AGGREGATE chain the evaluator does not compute",
        guard="tests/unit/test_probe_template_diff.py::test_td__a_cell_the_evaluator_could_not_compute_is_NOT_RUN_never_FAIL",
    ),
    Pin(
        id="EX-03",
        found_at="P9-B1",
        dated="2026-08-14",
        subject="cdfc.probes.degree",
        defect=(
            "Markers were matched as SUBSTRINGS, so `ratio` matched inside `Registration` and "
            "`'1. Introduction'!D40` — \"Date of Registration of FME\" — came out AMBIGUOUS. A "
            "degree decided by substring is a degree decided by whatever the marker list "
            "accidentally spells."
        ),
        example='_classify("Date of Registration of FME")',
        guard="tests/unit/test_degree.py::test_degree__markers_are_tokens_and_not_substrings",
    ),
    Pin(
        id="EX-04",
        found_at="P9-B1",
        dated="2026-08-14",
        subject="cdfc.probes.degree",
        defect=(
            "Count markers were spelled WITH their parentheses — `(nos.)` — while "
            "`_parenthesised` strips them before classifying, so a table declaring its unit in a "
            "parenthesis-only header cell fell through to NO_MARKER. It reached the right degree "
            "by the wrong route, which is the shape that survives a test asserting only the number."
        ),
        example="assign('4. Investors', 'N5', {...'C3': '(Nos.)'})",
        guard="tests/unit/test_degree.py::test_degree__both_degrees_are_actually_used",
    ),
    Pin(
        id="EX-05",
        found_at="P9-entry",
        dated="2026-08-14",
        subject="tools/measure/evaluator_arm1.py",
        defect=(
            "The renderer printed `r['cells']` and `r['trivial_cells']`, which `compare()` had "
            "stopped returning. The script raised `KeyError: 'cells'` on every invocation, and no "
            "make target ran it — so `docs/measurements/P3-evaluator.md` was an artifact of a "
            "version that no longer executed, publishing FME as 495 agree / 10 not-run when the "
            "truth after P6's AGGREGATE repair was 475 / 30."
        ),
        example="make evaluator-arm1",
        guard="tests/golden/test_p9_ceiling.py::test_golden__the_published_file_carries_the_measured_numbers",
    ),
)

PIN_IDS: Final[frozenset[str]] = frozenset(p.id for p in PINS)
