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

    for name in ("ingest", "induce", "harvest", "run", "qualify", "attest", "verify"):
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


if __name__ == "__main__":
    raise SystemExit(main())
