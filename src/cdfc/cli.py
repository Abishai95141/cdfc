"""cdfc command-line entry point.

At P0 every subcommand except `--version` exits 2. That is not a placeholder: a stub
that exits 0 is an all-clear, and this product's entire thesis is that a silent success
carries no information. `test_cli__unimplemented_subcommand_exits_nonzero` proves it,
and `injectors/stub_exits_zero.py` proves the test can go red.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from cdfc import __version__
from cdfc.gates import GATES_MD, parse

PHASE = "P0"
EXIT_NOT_IMPLEMENTED = 2


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

    for name in ("ingest", "induce", "run", "qualify", "attest", "verify"):
        sub.add_parser(name, help=f"{name} (not implemented at phase {PHASE})")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(version_line())
        return 0

    if args.command is None:
        print(f"cdfc: no command given. Try `cdfc --version`. Phase {PHASE}.", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    if args.command == "harvest":
        return _harvest(args)

    # Every command below is specified and not built. It exits non-zero and says which
    # phase builds it, so a caller cannot mistake absence for success.
    owner = {
        "init": "P1",
        "ingest": "P1",
        "induce": "P2",
        "harvest": "P4",
        "run": "P5",
        "qualify": "P7",
        "attest": "P11",
        "verify": "P11",
    }.get(args.command, "unassigned")
    print(
        f"cdfc: `{args.command}` is not implemented at phase {PHASE}; it is built in {owner}.",
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
        from cdfc.measure.harvest_report import render_report

        args.report.write_text(render_report(results), encoding="utf-8")
        print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
