"""P10-B1 — the canary loop's wall clock, and it lives **outside** the loop.

**DEVIATION FROM `plan/05`, recorded here.** The plan's file list names
`src/cdfc/selfcheck/timings.py`. Putting a clock read there would have required widening
`ci/no-clock-in-core.sh` — the gate whose whole job is to keep clocks out of the deterministic
core, and the gate the F23 ruling extends in the same breath. Widening a gate to admit the code it
was just extended to catch is the shape this project refuses.

So the timing lives in `src/cdfc/measure/perf/`, the directory that gate already exempts, and
`src/cdfc/selfcheck/` contains **no timing code at all**. That is strictly stronger than the plan's
arrangement: the loop cannot read a clock, rather than being trusted not to.
`test_tim__no_clock_is_reachable_from_the_selfcheck_package` walks the import closure and asserts
it.

**What is timed, and what the number may be used for.** `PERF-CANARY2` budgets the canary and
anti-canary loop over in-memory fact tables. The measured figure replaces the ≈70 ms DERIVED one on
the first green run. It is written to `reports/perf/<run_id>.jsonl`, which is **not** in
`run.jsonl`, **not** in the attestation, and **not** in `make determinism`'s or `verify`'s
comparison set — so no byte of it can reach a hashed payload, and
`test_tim__timings_are_written_outside_the_payload` checks that from the other side by asserting
none of its content appears in any of the three.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, TypeVar

from cdfc.measure.paths import PERF_DIR

T = TypeVar("T")

# `plan/05`'s budget row, verbatim. Recorded here so the tool that measures and the document that
# publishes read one list.
BUDGET_ID: Final[str] = "PERF-CANARY2"
BASELINE_MS: Final[int] = 70      # DERIVED from the measured 7,946 mutations/s
WARN_ABOVE_MS: Final[int] = 110
FAIL_ABOVE_MS: Final[int] = 160
SUPERSEDES: Final[str] = "PERF-CANARY (~35 ms) — the anti-canary was added in §0.4 and doubles the loop"


@dataclass(frozen=True, slots=True)
class Timing:
    run_id: str
    budget_id: str
    stage: str
    elapsed_ms: int
    n: int

    def as_row(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "budget_id": self.budget_id, "stage": self.stage,
            "elapsed_ms": self.elapsed_ms, "n": self.n,
            "baseline_ms": BASELINE_MS, "warn_above_ms": WARN_ABOVE_MS,
            "fail_above_ms": FAIL_ABOVE_MS,
            "verdict": verdict_for(self.elapsed_ms),
        }


def verdict_for(elapsed_ms: int) -> str:
    if elapsed_ms > FAIL_ABOVE_MS:
        return "FAIL"
    if elapsed_ms > WARN_ABOVE_MS:
        return "WARN"
    return "OK"


def timed(fn: Callable[[], T]) -> tuple[T, int]:
    """Run `fn` and return `(result, elapsed_ms)`. The ONLY clock read in the canary path."""
    start = time.perf_counter()
    out = fn()
    return out, int(round((time.perf_counter() - start) * 1000))


def write(timings: list[Timing], *, out_dir: Path | None = None) -> Path:
    """`reports/perf/<run_id>.jsonl`. Created on demand; the directory is gitignored output."""
    if not timings:
        raise ValueError(
            "refusing to write an empty timing file. An empty file at this path reads as "
            "`the loop ran and took no time`, which is the evidence-destroying repair F23 names."
        )
    target = (out_dir or PERF_DIR)
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{timings[0].run_id}.jsonl"
    path.write_text(
        "".join(json.dumps(t.as_row(), sort_keys=True) + "\n" for t in timings), encoding="utf-8"
    )
    return path
