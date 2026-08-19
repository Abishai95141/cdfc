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
import json
import sys
from pathlib import Path

from cdfc import __version__
from cdfc.gates import GATES_MD, parse

EXIT_NOT_IMPLEMENTED = 2

# Which phase OWNS each command. A command with a handler in `HANDLERS` is built; one without
# exits 2 naming its owner. `PHASE` is computed from that rather than written down, because a
# literal phase string is exactly what sat at `"P0"` through five phases of shipped work.
OWNER = {
    "evidence": "A4",
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
                     help="the pinned FME reference template, and nothing else: this build checks "
                          "against that one blank, so naming any other workbook is REFUSED rather "
                          "than silently ignored")
    run.add_argument("--out", type=Path, default=Path("runs"))

    closure = sub.add_parser("closure", help="explain a run's seven-term closure (P5)")
    closure.add_argument("action", choices=["explain"])
    closure.add_argument("run_id", nargs="?", default=None)
    closure.add_argument("--out", type=Path, default=Path("runs"))

    # P11. `attest` takes `--time-verified` as an ARGUMENT because it is an input recorded in the
    # manifest: defaulting it to the clock would make every attestation differ from its own
    # re-derivation on the following day.
    attest = sub.add_parser("attest", help="sign a settlement statement over a checked filing (P11)")
    attest.add_argument("filing", type=Path)
    attest.add_argument("--time-verified", required=True,
                        help="ISO-8601 instant. An INPUT, never a clock read.")
    attest.add_argument("--out", type=Path, default=Path("runs"))

    verify = sub.add_parser("verify", help="re-derive a statement byte-for-byte and check its signature (P11)")
    verify.add_argument("attestation", type=Path)
    verify.add_argument("--blobs", type=Path, action="append", default=None,
                        help="a directory to resolve filing and template blobs from, by DIGEST")

    serve = sub.add_parser("serve", help="serve the drop screen and /v1/* over HTTP (P14-B3)")
    serve.add_argument("--host", default="127.0.0.1",
                       help="binds loopback by default; a public bind is an explicit argument")
    serve.add_argument("--port", type=int, default=8765)

    evid = sub.add_parser(
        "evidence",
        help="rules corpus + template + proposals -> gates -> graph -> coverage declaration")
    evid.add_argument("--instrument", default="statute-fm-regulations-2025",
                      help="a pinned instrument id from the corpus")
    evid.add_argument("--template", type=Path, required=True, help="the blank being governed")
    evid.add_argument("--proposals", type=Path, required=True,
                      help="a model's rule->field bindings, AS DATA. Nothing here calls a model.")
    evid.add_argument("--only-with", default=None,
                      help="restrict provisions to units containing this substring, e.g. shall")
    evid.add_argument("--triples", action="store_true", help="also print the RDF projection size")

    for name in ("ingest", "induce", "qualify"):
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


def _evidence(args: argparse.Namespace) -> int:
    """`cdfc evidence`. **Exits non-zero when a proposal was refused**, because a run whose
    refusals nobody looked at is a run whose refusals nobody looked at."""
    from cdfc.evidence.run import run as evidence_run

    r = evidence_run(
        instrument_id=args.instrument,
        template=args.template,
        proposals=args.proposals,
        only_with=args.only_with,
    )
    print(r.report())
    if args.triples:
        print(f"\nRDF triples  {sum(1 for _ in r.graph.triples())}")
    return 0 if not r.adjudication.refused else 1


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

    **`--template` is refused when it names anything but the pinned blank, and the refusal is the
    honest answer.** It used to be accepted, printed as `template <whatever you passed>`, and then
    discarded: `run_filing()` has no template parameter — its body reads the pinned FME workbook
    through parameterless `lru_cache`d globals — so `cdfc run <FME filing> --template <ALR
    workbook>` produced a run byte-identical to the default one, whose manifest recorded
    `template_sha256` of the FME blank. The console line contradicted the artifact written beside
    it. Threading a template through that caching layer is a later phase's work; until it exists,
    the command refuses instead of reporting a template it did not use.
    """
    from cdfc.evaluate.run import write
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p5_run import FME

    if not args.filing.is_file():
        print(f"cdfc run: {args.filing} is not a file", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    if args.template is not None and not _is_pinned_template(args.template):
        print(
            f"cdfc run: refusing --template {args.template}. This build checks a filing against "
            f"the pinned reference template only:\n"
            f"    {FME}\n"
            "  The check would have run against that blank whatever you passed here, because the "
            "run path resolves the pinned workbook through cached globals and takes no template "
            "argument. Reporting your template while checking against ours is the one thing this "
            "command must not do, so it stops. Omit --template to check against the pinned blank.",
            file=sys.stderr,
        )
        return EXIT_NOT_IMPLEMENTED

    # The template ACTUALLY used, which is the pinned blank in every run this build can produce.
    # It is read from `FME` rather than from `args` so the printed line cannot drift from the
    # `template_sha256` the manifest records.
    template = FME
    result = run_filing(args.filing)
    target = write(result, args.out)

    p = result.partition
    print(f"  filing    {args.filing.name}")
    print(f"  template  {template.name}")
    print(f"  run       {result.run_id}")
    print(f"  state     {result.run_state}")

    # --- L6.5, and it prints BEFORE the coverage numbers -----------------------------------
    #
    # The order is the claim. The liveness proof is the licence for everything below it: a
    # settled fraction from an instrument that was not demonstrated on this document is a number
    # with no warrant, and printing the warrant afterwards invites reading the number first.
    _print_liveness(result)
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
    _render_report(result, target)
    return 0


def _is_pinned_template(path: Path) -> bool:
    """Is `path` the pinned FME blank — the same file, or the same bytes under another name?

    Digest equality is checked as well as path identity because a byte-identical copy of the pinned
    blank IS the pinned blank: checking against it is exactly what this build does anyway, so
    refusing it would be a refusal with no fact behind it. The only thing that cannot be honoured
    is a DIFFERENT workbook.
    """
    from cdfc.measure.p5_run import FME

    try:
        if path.resolve() == FME.resolve():
            return True
        if not path.is_file():
            return False
        return hashlib.sha256(path.read_bytes()).digest() == hashlib.sha256(
            FME.read_bytes()
        ).digest()
    except OSError:
        return False


def _render_report(result: object, target: "Path") -> None:
    """The self-contained `report.html`, beside the run. **P14-B1's renderer had no caller.**

    `render_report` has existed since P14-B1 and nothing in the pipeline invoked it, so no run on
    disk carried a report — which made `GET /v1/runs/{id}/report.html` a permanent 404 and the
    surface's *Download the report* a control that could not work. A renderer with no caller is a
    feature that passes its own unit tests and has never once run on a real artifact.

    It is rendered here rather than on request for the reason `api/handlers.get_report` states: the
    attestation covers the FILE, and a served page re-rendered per request is a second artifact
    with the same name.

    **A failure to render does not fail the run.** The coverage declaration is already on disk and
    already printed; losing it because a document would not render would be the tail wagging the
    dog. The failure is reported in full, and it is loud.
    """
    from cdfc.surface.render import render_report

    try:
        art = render_report(result, out=target / "report.html")
    except Exception as e:  # noqa: BLE001 — see the docstring; reported, never swallowed
        print(f"\n  REPORT NOT RENDERED: {type(e).__name__}: {e}", file=sys.stderr)
        print("  The run itself is on disk and its counts are above. The downloadable report is "
              "absent, and absent is what every surface will say.", file=sys.stderr)
        return
    print(f"  wrote {art.path}  ({art.n_bytes:,} bytes, sha256 {art.sha256[:16]}…)")


def _print_liveness(result: object) -> None:
    """The liveness proof, or the sentence that says there is not one.

    **A null proof renders in WORDS, never as zeros.** `canariesRun: 0` says the loop ran and found
    nothing to do; `livenessProof: null` says nobody asked. Printing the first for the second is
    the silent-success mechanism this product exists to refuse, in the layer whose whole subject is
    silent success.
    """
    from cdfc.measure.p10_run import NO_LIVENESS

    report = getattr(result, "liveness", None)
    disp = getattr(result, "liveness_disposition", None)
    if report is None:
        print(f"\n  {NO_LIVENESS}")
        return
    proof = report.as_liveness_proof()
    print(
        f"\n  liveness   canaries {proof['canariesPassed']}/{proof['canariesRun']} · "
        f"anti-canaries {proof['antiCanariesPassed']}/{proof['antiCanariesRun']} · "
        f"self-test silent {str(proof['selfTestSilent']).lower()}"
    )
    print(
        f"             inapplicable {proof['canariesInapplicable']} · "
        f"indeterminate {proof['canariesIndeterminate']} · "
        f"unresolved {proof['canariesUnresolved']}   (maxWitnesses {proof['maxWitnesses']})"
    )
    if disp is not None and not disp.valid:
        print(f"\n  LIVENESS FAILED — {disp.failure_kind}")
        print(f"  {disp.detail}")
    elif disp is not None and disp.deactivated:
        print(
            f"             {len(disp.deactivated)} predicate(s) NOT_RUN(not_run.deactivated): "
            "their liveness could not be demonstrated here, so they settle nothing here"
        )


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


def _attest(args: argparse.Namespace) -> int:
    """`cdfc attest <filing> --time-verified <instant>` — P11's deliverable.

    **There is nothing to sign until the canaries run**, so this goes through the P10 path and
    refuses to attest a run whose liveness was not demonstrated: signing a statement produced by an
    instrument nobody showed was working is the exact thing the liveness layer exists to prevent,
    committed one layer up.
    """
    from cdfc.attest import dsse
    from cdfc.evaluate.run import write as write_run
    from cdfc.measure.p10_run import run_filing
    from cdfc.measure.p11_attest import statement_for, write

    if not args.filing.is_file():
        print(f"cdfc attest: {args.filing} is not a file", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    result = run_filing(args.filing)
    write_run(result, args.out)
    if result.liveness is None:
        print(
            "cdfc attest: this run carries no liveness proof, so there is nothing to sign. An "
            "attestation without one is a statement about a filing produced by an instrument "
            "nobody demonstrated was working.",
            file=sys.stderr,
        )
        return EXIT_NOT_IMPLEMENTED

    statement = statement_for(result, filing=args.filing, time_verified=args.time_verified)
    path = write(statement, args.out)
    envelope = json.loads(path.read_text(encoding="utf-8"))

    print(f"  filing      {args.filing.name}")
    print(f"  run         {result.run_id}")
    print(f"  state       {result.run_state}")
    print(f"  verified    {statement.time_verified}   expires {statement.expires}")
    print(f"  signature   {envelope['signatures'][0]['keyid']}")
    print(f"  {envelope['signatures'][0]['implementation']}")
    _print_liveness(result)
    if result.run_state == "INVALID":
        print("\n  settledFraction and verdict are NULL — present, and null. This run makes no")
        print("  claim about the filing, which is a different thing from claiming zero.")
    print(f"\n  wrote {path}")
    return 0


def _verify(args: argparse.Namespace) -> int:
    """`cdfc verify <attestation.json>` — **the programme's acceptance test, as a command.**

    Two facts, reported separately and never merged: whether the payload re-derives, and whether
    the stored signature is valid over it.
    """
    from cdfc.attest.verify import BlobStore, verify

    if not args.attestation.is_file():
        print(f"cdfc verify: {args.attestation} is not a file", file=sys.stderr)
        return EXIT_NOT_IMPLEMENTED

    repo = Path(__file__).resolve().parents[2]
    roots = args.blobs or [repo / "fixtures"]
    result = verify(args.attestation, BlobStore(roots=roots), repo=repo)

    print(f"  artifact    {args.attestation}")
    print(f"  pins        {len(result.manifest_pins_checked)} checked: "
          f"{', '.join(result.manifest_pins_checked)}")
    print(f"  reproduced  {'YES' if result.reproduced else 'NO'}")
    sig = {True: "VALID", False: "INVALID", None: "NO KEY IN ENVELOPE — no claim"}[
        result.signature_valid
    ]
    print(f"  signature   {sig}")
    if not result.tree_clean:
        print("\n  WORKING TREE IS DIRTY. `code_git_sha` pins the COMMIT, not the tree, so this")
        print("  re-derivation ran against code the manifest does not describe. A `reproduced`")
        print("  from a dirty tree is a weaker statement than the same value from a clean one.")
    if result.detail:
        print(f"\n  {result.detail}")
    for d in result.diffs:
        print(f"    {d.render()}")
    print("\n  These are TWO FACTS. A changed report and a changed key are different events,")
    print("  and a tool that answered with one number could not tell you which happened.")
    return 0 if (result.reproduced and result.signature_valid is not False) else 1


def _serve(args) -> int:
    """Bind and serve. The import is LOCAL so `cdfc.cli` does not pull a socket into its closure.

    `cdfc.api.serve` is the one module in the package that opens one, and a top-level import here
    would put it in the closure of every CLI invocation -- including `cdfc run`, whose whole claim
    is that it computes a verdict with the network down.
    """
    from cdfc.api.serve import serve

    serve(args.host, args.port)
    return 0


HANDLERS = {"harvest": _harvest, "run": _run, "closure": _closure, "serve": _serve,
            "attest": _attest, "verify": _verify, "evidence": _evidence}


if __name__ == "__main__":
    raise SystemExit(main())
