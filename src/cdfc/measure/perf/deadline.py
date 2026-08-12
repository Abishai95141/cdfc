"""The wall-clock kill, and it lives HERE because a clock is not part of the deterministic core.

`ci/no-clock-in-core.sh` refuses `monotonic` anywhere under `src/cdfc` except this directory, and
the reason is not hygiene: **a wall-clock kill is not re-derivable.** The same run on a loaded
machine produces a different outcome, so an item killed by the clock cannot be reproduced from its
own bytes. The step budget can.

So the runtime takes a `deadline_factory` rather than reading a clock itself, and a result killed
by this one is marked `deterministic=False` and reports `budget="wall"`. A reviewer can tell the
two kinds of `BUDGET_EXCEEDED` apart, which is the whole point of keeping them distinguishable.
"""

from __future__ import annotations

import time
from collections.abc import Callable


def wall_deadline(wall_ms: int) -> Callable[[], bool]:
    """A predicate that becomes true `wall_ms` from now. Non-deterministic, by construction."""
    if wall_ms <= 0:
        raise ValueError("a wall budget of zero would kill every evaluation before it started")
    end = time.monotonic() + wall_ms / 1000.0
    return lambda: time.monotonic() >= end


def wall_deadline_factory(wall_ms: int) -> Callable[[], Callable[[], bool]]:
    """The factory shape `CelRuntime` takes: called once per evaluation, starting a fresh clock."""
    return lambda: wall_deadline(wall_ms)


def never() -> Callable[[], bool]:
    """The deterministic default: no wall kill at all, so no result depends on machine load."""
    return lambda: False
