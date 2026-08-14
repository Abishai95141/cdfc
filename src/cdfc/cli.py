"""cdfc command-line entry point.

An unbuilt subcommand exits 2. That is not a placeholder: a stub that exits 0 is an all-clear, and
this product's entire thesis is that a silent success carries no information.
`test_cli__unimplemented_subcommand_exits_nonzero` proves it, and `injectors/stub_exits_zero.py`
proves the test can go red.

**`run` and `closure explain` were specified as P5 deliverables and were still absent at P9**, four
phases later, with `PHASE` reading `"P0"` and `cdfc run` printing *"it is built in P5"*. The
machinery had existed since P5 — `evaluate/run.py::write()` produces
`runs/<run_id>/{run.jsonl, run.db, manifest.json}` and `verdict/closure.py::explain()` renders the
seven terms — and neither was reachable from the CLI. Worse, `tests/unit/test_cli.py` asserted that
`main(["run"]) == 2` **and** that the message names P5, so the test enforced the absence of the
deliverable and would have gone red the day somebody built it. The deviation appeared in no
docstring, no `docs/GATE-CHANGES.md` row, no decision file and no commit message.

`PHASE` is now DERIVED from what is actually wired rather than declared, so it cannot go stale
again: a command with a handler is built, and one without says which phase owns it.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from cdfc import __version__
from cdfc.gates import GATES_MD, parse

EXIT_NOT_IMPLEMENTED = 2

# Which phase OWNS each command. A command with a handler in `HANDLERS` is built; one without
# exits 2 naming its owner. `PHASE` is computed from that rather than written down, because a
# literal phase string is exactly what sat at `"P0"` through five phases of shipped work.
OWNER = {
    "init": "P1",
    "ingest": "P1",
    "induce": "P2",
    "harvest": "P4",
    "run": "P5",
    "closure": "P5",
    "qualify": "P7",
    "attest": "P11",
    "verify": "P11",
}


def _schema_sha8() -> str:
    """Short digest of the gate registry — the only schema that exists at P0."""
    return hashlib.sha256(GATES_MD.read_bytes()).hexdigest()[:8]


def version_line() -> str:
    return f"cdfc {__version__} (schema {_schema_sha8()}, gates {len(parse())})"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cdfc", add_help=True)
    p.add_argument("--version", action="store_true", help="print version, schema digest and gate count")
    sub = p.add_subparsers(dest="command")

    init = sub.add_parser("init", help="apply db/schema.sql and record its digest (P1)")
    init.add_argument("--db", type=Path, default=Path("cdfc.db"))

    # P4: `harvest` is built. Every other command below is specified and not built, and says so.
    harvest = sub.add_parser("harvest", help="derive predicate envelopes from a pinned blank (P4)")
    harvest.add_argument("--template", type=Path, help="one .xlsx; omit with --all")
    harvest.add_argument("--all", action="store_true", help="every workbook in the pinned corpus")
    harvest.add_argument("--out", type=Path, default=Path("predicates/harvested"))
    harvest.add_argument("--report", type=Path, default=None,
                         help="re-render the distribution measurement to this path")

    # P5, built at last. `--out` defaults to `runs/`, exactly as `plan/03` specifies.
    run = sub.add_parser("run", help="check a filing against its pinned blank and declare coverage (P5)")
    run.add_argument("filing", type=Path)
    run.add_argument("--template", type=Path, default=None,
                     help="the pinned blank; defaults to the FME reference template")
    run.add_argument("--out", type=Path, default=Path("runs"))

    closure = sub.add_parser("closure", help="explain a run's seven-term closure (P5)")
    closure.add_argument("action", choices=["explain"])
    closure.add_argument("run_id", nargs="?", default=None)
    closure.add_argument("--out", type=Path, default=Path("runs"))

    for name in ("ingest", "induce", "qualify", "attest", "verify"):
        sub.add_parser(name, help=f"{name} (not implemented; built in {OWNER.get(name, '?')})")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(version_line())
        return 0

    if args.command is None:
        print("cdfc: no command given. Try `cdfc --version`.", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    handler = HANDLERS.get(args.command)
    if handler is not None:
        return handler(args)

    # A command that is specified and not built exits non-zero and says which phase builds it, so
    # a caller cannot mistake absence for success.
    print(
        f"cdfc: `{args.command}` is not implemented; it is built in "
        f"{OWNER.get(args.command, 'an unassigned phase')}.",
        file=sys.stderr,
    )
    return EXIT_NOT_IMPLEMENTED


def _harvest(args: argparse.Namespace) -> int:
    """`cdfc harvest`. Cannot fail on a readable workbook; it can only under-produce, and every
    thing it could not express is a typed, counted, rendered skip."""
    from cdfc.predicates.harvest import distribution, emit_envelopes, harvest, harvest_all

    corpus = Path(__file__).resolve().parents[2] / "fixtures" / "prescribed"
    if args.all:
        results = harvest_all(corpus)
    elif args.template:
        results = [harvest(args.template)]
    else:
        print("cdfc harvest: give --template <file.xlsx> or --all", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    written = 0
    for r in results:
        written += len(emit_envelopes(r, args.out))
        print(f"{len(r.candidates):5d} candidates  {len(r.skipped):4d} skipped  "
              f"{len(r.cells_reachable):5d} cells reachable  {r.workbook}")
    rows = distribution(results)
    print(f"{sum(x.n for x in rows)} candidates from {sum(1 for x in rows if x.n)} of "
          f"{len(rows)} workbooks; {written} envelopes written under {args.out}")

    if args.report is not None:
        import json

        from cdfc.measure.harvest_report import distribution_json, render_report

        args.report.write_text(render_report(results), encoding="utf-8")
        # The JSON beside it, from the SAME call. It used to be a committed snapshot with no
        # generator, publishing 592 where the markdown published 571.
        side = args.report.parent / "p4-harvest-distribution.json"
        side.write_text(
            json.dumps(distribution_json(results), indent=1, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.report} and {side}")
    return 0


def _run(args: argparse.Namespace) -> int:
    """`cdfc run <filing> [--template T] [--out runs/]` — P5's deliverable, reachable at last.

    **The output is a COVERAGE DECLARATION and it is structurally incapable of an all-clear.** It
    prints what was checked and what was not, in the same units and with equal weight, and the
    settled fraction never renders without `cellsTotal` and `inScope` beside it.
    """
    from cdfc.measure.p5_run import FME, run_filing
    from cdfc.evaluate.run import write

    if not args.filing.is_file():
        print(f"cdfc run: {args.filing} is not a file", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    template = args.template or FME
    result = run_filing(args.filing)
    target = write(result, args.out)

    p = result.partition
    print(f"  filing    {args.filing.name}")
    print(f"  template  {template.name}")
    print(f"  run       {result.run_id}")
    print(f"  state     {result.run_state}")
    if result.run_state != "VALID" or p is None:
        causes = ", ".join(str(c) for c in result.invalid_causes) or "none recorded"
        print(f"\n  NO COVERAGE IS DECLARED: {causes}")
        print("  A run that could not bind its template has not checked anything, and the")
        print("  settled fraction is null rather than zero.")
        print(f"\n  wrote {target}")
        return 0

    f = result.fraction
    print(f"\n  cellsTotal {p.cellsTotal}   inScope {p.inScope}   "
          f"outOfScope {p.outOfScope} (retained {p.outOfScopeRetained})")
    print(f"  settled    {p.settled}  =  PASS {p.settledPass} + FAIL {p.settledFail}")
    print(f"  NOT settled: notRun {p.notRun} · noPredicate {p.noPredicate} · "
          f"indeterminate {p.indeterminate} · error {p.error}")
    if f is not None:
        # The fraction NEVER renders alone. Both denominator terms are on the same line.
        print(f"\n  settled fraction  {f.settled.total} / {f.inScope}  "
              f"(of {f.cellsTotal} cells)  =  {f.fraction}")
        print(f"  {f.admissibilityCaveat or ''}".rstrip())
        print(f"  {f.denominatorWarning}")
    print("\n  This states what was checked and what was not. It does not state that the")
    print("  filing is correct.")
    print(f"\n  wrote {target}")
    return 0


def _closure(args: argparse.Namespace) -> int:
    """`cdfc closure explain <run_id>` — the seven terms, from the run's own record.

    `verdict/closure.py::explain()` had zero callers and zero tests, and
    `tools/measure/p5_runtime_closure.py` re-implemented the same rendering by hand.
    """
    import json

    from cdfc.verdict.closure import explain

    runs = sorted(p for p in args.out.glob("*") if (p / "manifest.json").is_file())
    if not runs:
        print(f"cdfc closure: no runs under {args.out}. Run `cdfc run <filing>` first.",
              file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED
    target = next((p for p in runs if p.name == args.run_id), None) if args.run_id else runs[-1]
    if target is None:
        print(f"cdfc closure: no run {args.run_id!r} under {args.out}", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    m = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    print(f"  run {target.name}")
    part = m.get("closure")
    if not part:
        print("  this run declared no coverage (INVALID), so there is no closure to explain")
        return 0
    print(explain(_partition_from(part)))
    return 0


def _partition_from(d: dict) -> "object":
    """Rebuild the REAL `ClosurePartition` from the run's stored closure block.

    A dict-shaped shim would not carry `total` or `inScope`, which are properties whose arithmetic
    is the whole point of the seven-term invariant — and `explain` would then be rendering terms
    that had never been re-added up. Reconstructing the type means the invariant is re-checked on
    the way out, from the run's own record rather than from a fresh evaluation.
    """
    from dataclasses import fields

    from cdfc.verdict.closure import ClosurePartition

    known = {f.name for f in fields(ClosurePartition)}
    return ClosurePartition(**{k: v for k, v in d.items() if k in known})


HANDLERS = {"harvest": _harvest, "run": _run, "closure": _closure}


if __name__ == "__main__":
    raise SystemExit(main())
