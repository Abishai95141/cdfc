"""`assert_absent` — the ONLY sanctioned way to record an absence anywhere in this project.

Two claims in the research corpus collapsed because a search interface was mistaken for
the corpus it searched, and one of this session's own instruments reported a NUL byte in
every file because a shell cannot pass NUL as an argv pattern. An absence reported by an
instrument nobody proved could see a presence is not a finding; it is a broken query with
a confident face.

So: a count of zero is refused unless a positive control returns a POSITIVE count
**through the same interface**. Both numbers are written to the ledger, and the caller
gets back a row id. Downstream, `ci/no-bare-absence.sh` resolves that id and reads the
numbers — it does not grep for the words "positive control", because any author who has
read a lexical gate satisfies it in four words.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_LEDGER = Path(__file__).resolve().parents[3] / "reports" / "validation-ledger.jsonl"


class AbsenceWithoutControl(RuntimeError):
    """An absence was claimed without a positive control that returned a positive count."""


@dataclass(frozen=True)
class AbsenceClaim:
    row_id: str
    count: int
    positive_control_count: int
    corpus_id: str
    query_name: str

    @property
    def citation(self) -> str:
        """What a document must write next to an absence claim: `ledger:<row_id>`."""
        return f"ledger:{self.row_id}"


def _row_id(query_name: str, corpus_id: str, count: int, control: int) -> str:
    h = hashlib.sha256(f"{query_name}|{corpus_id}|{count}|{control}".encode()).hexdigest()
    return h[:16]


def assert_absent(
    query: Callable[[Any], int],
    *,
    positive_control: Callable[[Any], int],
    corpus: Any,
    corpus_id: str,
    query_name: str,
    ledger: Path | None = None,
) -> AbsenceClaim:
    """Record an absence, or refuse.

    Refuses (raises `AbsenceWithoutControl`) when the positive control returns 0 — which
    means the interface cannot see a presence, so its silence carries no information.
    Note the control must run through the SAME interface as the query; a control that
    uses a different reader proves the other reader works.
    """
    control_count = int(positive_control(corpus))
    count = int(query(corpus))

    path = ledger or DEFAULT_LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    rid = _row_id(query_name, corpus_id, count, control_count)
    row = {
        "row_id": rid,
        "query_name": query_name,
        "corpus_id": corpus_id,
        "count": count,
        "positive_control_count": control_count,
        "admissible": control_count > 0,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")

    if control_count <= 0:
        raise AbsenceWithoutControl(
            f"positive control for {query_name!r} returned {control_count} on corpus "
            f"{corpus_id!r}: the query cannot see a presence, so its absence is not a "
            f"finding. Ledger row {rid} records both counts."
        )
    return AbsenceClaim(rid, count, control_count, corpus_id, query_name)


def read_ledger(ledger: Path | None = None) -> dict[str, dict[str, Any]]:
    path = ledger or DEFAULT_LEDGER
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["row_id"]] = row
    return out
