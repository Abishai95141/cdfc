# docs/SURFACE-REGISTRY-LOG.md — the append-only growth log of `SURFACES`

**Why this file exists.** P14's exit gate reads `surfaces_passing_all_four_gates == len(SURFACES)`,
and P14 writes `SURFACES`. A surface that cannot be made to pass could be **deleted** from the
registry and the gate would go green with the negative-control sweep still reporting
`caught == active` — because the sweep catches a surface that renders through a known path, not one
**removed from the register**.

That is **M1** — this plan's founding defect, the numerator choosing its own denominator — sitting
inside the gate written to prevent it.

So the registry is diffed against **this log**, not against a previous commit: the check survives a
squash, a rebase, and a history rewrite. A row may be **retired** with a dated argument; it may
never be deleted. A retired row leaves the gate's **denominator** and stays in the **scan**.

| date | `\|SURFACES\|` | live | retired | change |
|---|---:|---:|---:|---|
| 2026-08-15 | 6 | 6 | 0 | P14-B1 creates the registry: `S01.report-file`, `S02.report-hero`, `S03.report-strapline`, `S04.report-band`, `S05.report-openitems`, `S06.cli-version` |

## The ids, append-only

```
S01.report-file
S02.report-hero
S03.report-strapline
S04.report-band
S05.report-openitems
S06.cli-version
```

**A retirement requires a dated row above naming the surface id and why it cannot be brought under
the gates.** `tests/surface/test_surface_registry.py::test_surface__a_retirement_with_a_dated_argument_is_accepted`
is the admission-side control — without it, "append-only" would be satisfiable by a rule that
forbids every change, and a registry that can never be corrected is its own problem.
