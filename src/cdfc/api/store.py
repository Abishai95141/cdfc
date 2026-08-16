"""P14-B3 completion — the read-only view of what is on disk.

The handlers were stubs returning empty collections: the CONTRACT layer was real and tested (a
`status` property genuinely could not reach a client) while nothing behind it served data. This
module is the repair, and it is deliberately **read-only**.

## Why read-only, and why it reads `run.jsonl` rather than `run.db`

`evaluate/run.write()` produces three artifacts per run: `run.jsonl`, `run.db` and
`manifest.json`. The API reads the **jsonl**, because that is the file the attestation covers and
the file `cdfc verify` re-derives. Serving from the database would serve a projection of the run
rather than the run, and a digest that matches a file nobody serves is not a reproducibility
claim — the same rule `get_report` already follows by reading `report.html` off disk rather than
re-rendering it.

An API that could WRITE a run would be an API that can change what a signed statement covers.
There is no code path here that opens a file for writing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

RUNS_DIR: Final[Path] = Path("reports/runs")

# The closure states, exactly as `verdict/states.py` fixes them. Kept here as a tuple so the wire
# order is stable across responses -- a client diffing two payloads must diff content.
SETTLED_STATES: Final[tuple[str, ...]] = ("PASS", "FAIL")


class RunNotFound(LookupError):
    """No run with that id is on disk. Never confused with a run that produced nothing."""


@dataclass(frozen=True, slots=True)
class StoredRun:
    """`manifest.json` is the HEADER; `run.jsonl` is the evaluation STREAM.

    The first version of this class assumed the jsonl carried a typed header record and returned
    empty for everything -- it would have served a run with no counts and no error. The stream is
    flat: one record per cell evaluation, with no `kind` discriminator, and the closure counts live
    in the manifest beside the digest that covers them.
    """

    run_id: str
    path: Path
    manifest: dict[str, Any]
    records: tuple[dict[str, Any], ...]

    def header(self) -> dict[str, Any]:
        return self.manifest

    def closure(self) -> dict[str, Any]:
        c = self.manifest.get("closure")
        if not c:
            raise RunNotFound(
                f"{self.run_id}: the manifest carries no closure. It is NOT served as zero: a "
                "missing measurement and a measured zero are different facts, and this project is "
                "named for the difference."
            )
        return c


def load(run_id: str, *, runs_dir: Path = RUNS_DIR) -> StoredRun:
    d = runs_dir / run_id
    stream, manifest = d / "run.jsonl", d / "manifest.json"
    if not stream.is_file() or not manifest.is_file():
        raise RunNotFound(f"{run_id} is not on disk at {d} (need run.jsonl and manifest.json)")
    records = tuple(
        json.loads(line) for line in stream.read_text(encoding="utf-8").splitlines() if line.strip()
    )
    return StoredRun(
        run_id=run_id, path=stream,
        manifest=json.loads(manifest.read_text(encoding="utf-8")),
        records=records,
    )


def run_ids(*, runs_dir: Path = RUNS_DIR) -> tuple[str, ...]:
    if not runs_dir.is_dir():
        return ()
    return tuple(sorted(d.name for d in runs_dir.iterdir() if (d / "manifest.json").is_file()))


def cells(run: StoredRun, *, state: str | None = None, reason: str | None = None
          ) -> tuple[dict[str, Any], ...]:
    out = run.records
    if state:
        out = tuple(r for r in out if str(r.get("state", "")).upper() == state.upper())
    if reason:
        out = tuple(r for r in out if str(r.get("reason") or "").upper() == reason.upper())
    return out


def checks(run: StoredRun, *, predicate_id: str | None = None) -> tuple[dict[str, Any], ...]:
    """One row per DISTINCT predicate, with the cells it settled. Never one row per cell."""
    by_pred: dict[str, dict[str, Any]] = {}
    for r in run.records:
        pid = r.get("predicate_id")
        if pid is None or (predicate_id and pid != predicate_id):
            continue
        row = by_pred.setdefault(pid, {"predicateId": pid, "version": r.get("version"),
                                       "cellsEvaluated": 0, "settles": 0, "states": {}})
        row["cellsEvaluated"] += 1
        row["settles"] += 1 if r.get("settles") else 0
        st = str(r.get("state", "UNKNOWN"))
        row["states"][st] = row["states"].get(st, 0) + 1
    return tuple(by_pred[k] for k in sorted(by_pred))


class BreakdownNotInArtifact(LookupError):
    """The per-reason breakdown is not derivable from `run.jsonl`. **Declared, never invented.**"""


def unchecked_groups(run: StoredRun) -> tuple[dict[str, Any], ...]:
    """The per-reason breakdown of the unchecked set — **or a refusal, never a fabricated code.**

    `run.jsonl` records the cells that were EVALUATED: 1,946 records, every one carrying a
    `predicate_id`. The 1,849 cells with no predicate are not in the stream at all; they exist only
    as `closure.noPredicate` in the manifest.

    The first version of this function defaulted a null reason to `"NO_PREDICATE"` and served
    `{"reasonCode": "NO_PREDICATE", "count": 1849}`. **That code is not in the closed
    thirty-member vocabulary** — there are seven `no_predicate.*` codes and none of them is it. It
    was invented here, and an invented reason code on the wire is worse than no breakdown: a client
    would render it beside real codes, and nobody downstream could tell which of the two it was.

    So this raises. The endpoint serves the TOTAL, which the manifest does carry, and says the
    breakdown is not in this artifact. The repair is upstream — persist the unevaluated cells with
    their reasons — and it is a change to `evaluate/run.write`, not to a default here.
    """
    from_stream: dict[str, int] = {}
    for r in run.records:
        if r.get("settles"):
            continue
        code = r.get("reason")
        if code:
            from_stream[str(code)] = from_stream.get(str(code), 0) + 1
    total = run.closure().get("noPredicate", 0) + run.closure().get("indeterminate", 0) \
        + run.closure().get("notRun", 0) + run.closure().get("error", 0)
    if sum(from_stream.values()) != total:
        raise BreakdownNotInArtifact(
            f"{run.run_id}: the stream accounts for {sum(from_stream.values())} unsettled cells "
            f"and the closure counts {total}. run.jsonl records only cells that were EVALUATED, "
            "so the no-predicate set is absent from it. The total is served; the breakdown is not "
            "invented."
        )
    return tuple({"reasonCode": k, "count": v} for k, v in sorted(from_stream.items()))


def unchecked_total(run: StoredRun) -> int:
    c = run.closure()
    return c["noPredicate"] + c["indeterminate"] + c["notRun"] + c["error"]


def fraction_of(run: StoredRun) -> dict[str, Any]:
    """The six counts, READ from the run rather than recomputed.

    Recomputing here would give the API its own arithmetic, and two implementations of the settled
    fraction is one more than this project can defend. The run is the measurement.
    """
    c = run.closure()
    return {
        "settled": c["settled"],
        "notChecked": c["noPredicate"],
        "unsettled": c["indeterminate"] + c["notRun"] + c["error"],
        "inScope": c["inScope"],
        "outOfScope": c["outOfScope"],
        "informational": c["informational"],
        "cellsTotal": c["cellsTotal"],
    }
