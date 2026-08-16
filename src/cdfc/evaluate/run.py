"""P5 — one run, end to end: bind, select, evaluate, roll up, close, and compute the fraction.

**The order is not negotiable and each step's failure has its own outcome.**

    bind      -> Unbound ESCALATES into both vocabularies and every cell is NOT_RUN
    select    -> an empty active set is an honest report, not an error
    evaluate  -> the nine transitions, in evaluation order
    roll up   -> from the DENOMINATOR's rows, never accumulated from the evaluations
    close     -> the seven terms, or report generation ABORTS
    fraction  -> the object, or `null` — never a zero standing in for one

**No clock is read here.** `received_at` is an argument, so a run is re-derivable from its own
bytes. The run id is the digest of what went into it, not a timestamp.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cdfc.canon import canonical_json, sha256_hex
from cdfc.evaluate.binding import Bound, TemplateCatalogue, Unbound, bind_template
from cdfc.evaluate.celrt import CelRuntime
from cdfc.evaluate.rollup import RunCell, materialise, roll_up_run
from cdfc.evaluate.runner import RunCheck, evaluate_all, unbound_checks
from cdfc.evaluate.selection import RunProfile, Selection, select
from cdfc.predicates.envelope import Predicate
from cdfc.predicates.host_fns import default_registry
from cdfc.verdict import InvalidCause, ItemState, ReasonCode
from cdfc.verdict.closure import ClosurePartition, ClosureViolation, assert_closed, partition
from cdfc.verdict.settled_fraction import Denominator, SettledFraction, compute, serialise


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    filing_sha256: str
    template_sha256: str | None
    run_state: str
    invalid_causes: tuple[InvalidCause, ...]
    checks: tuple[RunCheck, ...]
    cells: tuple[RunCell, ...]
    partition: ClosurePartition | None
    fraction: SettledFraction | None
    keys_checked: int = 0
    keys_type_checked: int = 0
    closure_error: str = ""
    selection: Selection | None = field(default=None, repr=False)
    # P10. `None` means the loop did not run on this filing — which is NOT the same as running
    # and finding nothing, so it renders as an explicit absence rather than as zeros.
    liveness: Any = None
    liveness_disposition: Any = None

    def unchecked_by_reason(self) -> dict[str, int]:
        """`{reason_code: n}` over every cell no predicate settled. **Counted, never defaulted.**

        A cell that is unsettled and carries no reason at all is a defect rather than a category,
        so it is counted under its own explicit key instead of being dropped — a breakdown that
        silently omits what it could not classify is a breakdown that always sums to something
        tidy and never to the total.
        """
        out: dict[str, int] = {}
        for cell in self.cells:
            if cell.settled_by is not None:
                continue
            if str(cell.state) in ("ItemState.PASS", "ItemState.FAIL", "PASS", "FAIL"):
                continue
            code = str(cell.reason) if cell.reason is not None else "UNCLASSIFIED_no_reason_recorded"
            out[code] = out.get(code, 0) + 1
        return dict(sorted(out.items()))

    def as_manifest(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "filing_sha256": self.filing_sha256,
            "template_sha256": self.template_sha256,
            "run_state": self.run_state,
            "invalid_causes": [c.value for c in self.invalid_causes],
            "checks": len(self.checks),
            "cells": len(self.cells),
            "keys_preflighted": self.keys_checked,
            "keys_type_checked": self.keys_type_checked,
            "closure": None if self.partition is None else self.partition.as_row(),
            # THE PER-REASON BREAKDOWN OF THE UNCHECKED SET, in the header where the closure is.
            #
            # `run.jsonl` is one line per EVALUATION, so a cell nothing evaluated leaves no trace
            # in it — which is why `api/store.unchecked_groups` had to REFUSE to serve a breakdown
            # rather than invent one. The counts live here instead of in the stream because the
            # stream's byte order is what the attestation covers and what `cdfc verify` re-derives;
            # adding rows to it would change a file whose identity is the claim.
            "uncheckedByReason": self.unchecked_by_reason(),
            # WHAT THE DENOMINATOR EXCLUDED, so a reader can answer *is the field surface the
            # whole form?* The honest answer for FME is no — 505 cells the template computes and
            # 2,505 a filer cannot write are removed before the count begins — and until this
            # field existed nothing anywhere said so. A denominator that does not declare its own
            # exclusions is the coverage lie this product is named for, aimed at itself.
            "surfaceExclusions": _surface_exclusions(),
            "livenessProof": None if self.liveness is None else self.liveness.as_liveness_proof(),
            "livenessFailureKind": (
                None if self.liveness_disposition is None
                else self.liveness_disposition.failure_kind
            ),
            **serialise(self.fraction),
        }


def _surface_exclusions() -> dict[str, Any] | None:
    """The FME field surface's exclusion census, or `None` when it cannot be derived.

    Read here rather than threaded through `execute()` because it is a property of the TEMPLATE,
    not of the run: every run against the same blank excludes the same cells, and passing it as a
    parameter would invite a caller to supply a different one.
    """
    try:
        from cdfc.measure.p5_run import FME
        from cdfc.schema.styles_mask import Rule, build

        ex = build(FME, Rule.V3).exclusions
    except Exception:  # noqa: BLE001 — an underivable census is a state, reported as absent
        return None
    return None if ex is None else ex.as_canonical_obj()


def run_id_for(filing_sha256: str, registry_root: str, profile: RunProfile) -> str:
    """A digest of the inputs, not a timestamp. Two identical runs share an id, which is the point."""
    return sha256_hex(
        canonical_json(
            {
                "filing": filing_sha256,
                "registry_root": registry_root,
                "profile": profile.name,
                "profile_digest": profile.digest,
                "exclude": sorted(profile.exclude),
                "spike": profile.spike,
            }
        )
    )[:16]


def execute(
    filing: Path,
    *,
    catalogue: TemplateCatalogue,
    predicates: Sequence[Predicate],
    schema: Any,
    field_surface: int | None,
    denominator: Denominator,
    registry_root: str,
    profile: RunProfile,
    facts: Any,
    surface_cells: Sequence[str],
    rt: CelRuntime | None = None,
    liveness: Any = None,
    # Per-cell reason for cells NO predicate settles. Supplied by the caller because only the
    # caller knows which candidates were harvested and which of them a gate refused; this module
    # sees the admitted set and would otherwise have to say `not_yet_synthesised` for every one.
    unchecked_reasons: Mapping[str, ReasonCode] | None = None,
) -> RunResult:
    import hashlib

    filing_sha = hashlib.sha256(filing.read_bytes()).hexdigest()
    rid = run_id_for(filing_sha, registry_root, profile)
    rt = rt or CelRuntime(profile_version="P5", host_fns=default_registry())

    binding = bind_template(filing, catalogue)
    if isinstance(binding, Unbound):
        checks = unbound_checks([p.id for p in predicates])
        cells = tuple(
            RunCell(
                stable_key=k, state=ItemState.NOT_RUN,
                reason=ReasonCode.NR_TEMPLATE_UNBOUND, settled_by=None,
            )
            for k in sorted(surface_cells)
        )
        # BOTH vocabularies. Audit V.7.3: they are not alternatives.
        return RunResult(
            run_id=rid, filing_sha256=filing_sha, template_sha256=None, run_state="INVALID",
            invalid_causes=(InvalidCause.TEMPLATE_UNBOUND,), checks=checks, cells=cells,
            partition=None, fraction=None,
        )

    assert isinstance(binding, Bound)
    sel = select(registry_root, binding.template_sha256, profile, predicates=predicates)
    outcome = evaluate_all(sel, facts=facts, schema=schema, rt=rt)

    # --- L6.5: THE LIVENESS PROOF, AND IT IS TAKEN BEFORE THE FRACTION IS COMPUTED ----------
    #
    # The order is not incidental. A predicate the loop could not demonstrate on THIS filing is
    # `NOT_RUN(not_run.deactivated)` and its cells stop being settled — so the deactivation has to
    # reach `roll_up_run`, not be noted beside the number afterwards. And when the loop fails, the
    # fraction is `null` rather than being computed and then suppressed: a suppressed number is a
    # number somebody can un-suppress.
    report, disp = (None, None)
    checks = outcome.checks
    causes = list(outcome.invalid_causes)
    if liveness is not None:
        from cdfc.evaluate.liveness import run as run_liveness

        report, disp = run_liveness(liveness)
        if disp.deactivated:
            checks = _deactivate(checks, frozenset(disp.deactivated))
        if not disp.valid:
            causes.append(disp.cause)

    table = materialise(surface_cells, reasons=unchecked_reasons)
    cells = roll_up_run(table, checks)

    part: ClosurePartition | None = None
    closure_error = ""
    try:
        part = partition(cells, field_surface if field_surface is not None else len(cells))
        assert_closed(part)
    except ClosureViolation as e:
        closure_error = str(e)
        causes.append(InvalidCause.CLOSURE_VIOLATED)
        part = None

    run_state = "INVALID" if causes else "VALID"
    fraction = (
        None if part is None
        else compute(part, sel, denominator, run_state)
    )
    return RunResult(
        run_id=rid, filing_sha256=filing_sha, template_sha256=binding.template_sha256,
        run_state=run_state, invalid_causes=tuple(sorted(set(causes), key=str)),
        checks=checks, cells=cells, partition=part, fraction=fraction,
        keys_checked=outcome.keys_checked, keys_type_checked=outcome.keys_type_checked,
        closure_error=closure_error, selection=sel,
        liveness=report, liveness_disposition=disp,
    )


def _deactivate(
    checks: Sequence[RunCheck], deactivated: frozenset[str]
) -> tuple[RunCheck, ...]:
    """A predicate the canary loop could not demonstrate here settles nothing here.

    `NOT_RUN(not_run.deactivated)`, replacing whatever it returned — including a `PASS`. **The
    fraction falls, and that is the whole point**: a check whose liveness was not demonstrated on
    this filing has not covered the cells it binds, and letting its `PASS` stand would put coverage
    in the numerator that nothing demonstrated.
    """
    out = []
    for c in checks:
        if c.predicate_id not in deactivated:
            out.append(c)
            continue
        out.append(
            RunCheck(
                predicate_id=c.predicate_id, version=c.version,
                state=ItemState.NOT_RUN, reason=ReasonCode.NR_DEACTIVATED,
                witness=(), cells_bound=c.cells_bound, order=5, settles=False,
                keys_checked=c.keys_checked, keys_type_checked=c.keys_type_checked,
                detail=(
                    "no stored kill case for this predicate is observable on this filing, so its "
                    "liveness could not be demonstrated here"
                ),
            )
        )
    return tuple(out)


def run_jsonl(result: RunResult) -> str:
    """NDJSON, ONE LINE PER EVALUATION, ordered by `(predicate_id, version, stable_key)`.

    An explicit sort key, so the file is byte-stable across runs, machines and hash seeds. Not one
    line per cell: a cell read by three predicates is three facts, and collapsing them loses which
    predicate settled it.
    """
    rows = []
    for cell in result.cells:
        for ev in cell.evaluations:
            rows.append(
                {
                    "run_id": result.run_id,
                    "predicate_id": ev.predicate_id,
                    "version": ev.version,
                    "stable_key": cell.stable_key,
                    "state": str(ev.state),
                    "reason": None if ev.reason is None else str(ev.reason),
                    "scope_kind": ev.scope_kind,
                    "settles": ev.settles,
                    "witness": list(ev.witness),
                }
            )
    rows.sort(key=lambda r: (r["predicate_id"], r["version"], r["stable_key"]))
    return "".join(canonical_json(r).decode("utf-8") + "\n" for r in rows)


def write(result: RunResult, out_dir: Path) -> Path:
    """`runs/<run_id>/{run.jsonl, run.db, manifest.json}`. The db is a FILE, therefore hashable."""
    from cdfc.store.db import digest_of, open_db

    target = out_dir / result.run_id
    target.mkdir(parents=True, exist_ok=True)
    (target / "run.jsonl").write_text(run_jsonl(result), encoding="utf-8")

    db_path = target / "run.db"
    db_path.unlink(missing_ok=True)
    conn = open_db(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO run(run_id, filing_sha256, template_sha256, registry_root, "
        "profile, profile_digest, received_at, run_state, field_surface, keys_checked, "
        "keys_type_checked) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            result.run_id, result.filing_sha256, result.template_sha256,
            getattr(result.selection, "registry_root", ""),
            getattr(getattr(result.selection, "profile", None), "name", ""),
            getattr(getattr(result.selection, "profile", None), "digest", ""),
            "",                                   # received_at: an ARGUMENT, empty when not given
            result.run_state,
            None if result.partition is None else result.partition.cellsTotal,
            result.keys_checked, result.keys_type_checked,
        ),
    )
    conn.executemany(
        "INSERT OR REPLACE INTO run_invalid(run_id, cause) VALUES (?,?)",
        [(result.run_id, c.value) for c in result.invalid_causes],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO run_check(run_id, predicate_id, version, state, reason, "
        "scope_kind, informational_note, witness, cells_bound, transition_order, settles, detail) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (result.run_id, c.predicate_id, c.version, str(c.state),
             None if c.reason is None else str(c.reason), c.scope_kind, c.informational_note,
             " ".join(c.witness), len(c.cells_bound), c.order, int(c.settles), c.detail)
            for c in result.checks
        ],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO run_cell(run_id, stable_key, state, reason, scope_kind, "
        "settled_by, in_scope, requalify) VALUES (?,?,?,?,?,?,?,?)",
        [
            (result.run_id, c.stable_key, str(c.state),
             None if c.reason is None else str(c.reason), c.scope_kind, c.settled_by,
             int(c.in_scope), int(c.requalify))
            for c in result.cells
        ],
    )
    conn.commit()
    conn.close()

    manifest = result.as_manifest() | {"run_db_sha256": digest_of(db_path)}
    (target / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return target
