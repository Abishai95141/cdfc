"""P14-B1 — standing open items, **rendered with their age**.

`plan/07`: an item with a sent date and no reply date renders as
*"asked <date>, no reply after <n> days"* — **never as absence**. A question nobody answered
becomes more visible as it gets older, not less.

`now` is a PARAMETER derived from the run, never a clock read: nothing under `src/cdfc/` reads the
wall clock (`ci/no-clock-in-core.sh`), and a report whose contents depend on when it was rendered
is a report that cannot be re-derived byte for byte.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

DOCS: Final[tuple[Path, ...]] = (
    Path("docs/OPEN-ITEMS.md"),
    Path("docs/FIELD-OBSERVATIONS.md"),
)

# `- [ASKED 2026-08-13] text` / `- [OPEN] text`
ITEM: Final[re.Pattern[str]] = re.compile(
    r"^-\s*\[(?P<kind>ASKED|OPEN)(?:\s+(?P<date>\d{4}-\d{2}-\d{2}))?\]\s*(?P<text>.+?)\s*$"
)


@dataclass(frozen=True, slots=True)
class OpenItem:
    text: str
    age: str


def _age(kind: str, when: str | None, now: date) -> str:
    if kind == "ASKED" and when:
        days = (now - date.fromisoformat(when)).days
        return f"asked {when}, no reply after {days} days"
    return "open, undated"


def standing_open_items(run: Any = None, *, now: date | None = None,
                        docs: tuple[Path, ...] = DOCS) -> tuple[OpenItem, ...]:
    """Every unanswered item, with its age. **An empty list renders as one; it is never absent.**"""
    if now is None:
        stamp = str(getattr(run, "run_id", "") or "")
        m = re.search(r"(\d{4}-\d{2}-\d{2})", stamp)
        # No date anywhere is reported as undated rather than defaulted to today: "today" is a
        # clock read, and it would make the report's contents a function of when it was rendered.
        now = date.fromisoformat(m.group(1)) if m else None
    out: list[OpenItem] = []
    for doc in docs:
        if not doc.is_file():
            continue
        for line in doc.read_text(encoding="utf-8").splitlines():
            m = ITEM.match(line.strip())
            if not m:
                continue
            age = (_age(m.group("kind"), m.group("date"), now) if now
                   else f"{m.group('kind').lower()}, age not computable without a run date")
            out.append(OpenItem(text=m.group("text"), age=age))
    return tuple(out)
