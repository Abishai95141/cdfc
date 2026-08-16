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
S07.drop-screen
S08.api-openapi
S09.api-run
S10.api-portfolio
```

**A retirement requires a dated row above naming the surface id and why it cannot be brought under
the gates.** `tests/surface/test_surface_registry.py::test_surface__a_retirement_with_a_dated_argument_is_accepted`
is the admission-side control — without it, "append-only" would be satisfiable by a rule that
forbids every change, and a registry that can never be corrected is its own problem.


## 16 August 2026 — P14-B3 appended four rows. |SURFACES| 6 -> 10

| id | why it is a surface |
|---|---|
| `S07.drop-screen` | it renders to a browser and a banned phrase could reach it |
| `S08.api-openapi` | the generated document is READ BY CLIENTS; a `status` property there reaches every integration at once |
| `S09.api-run` | it carries a settled count on the wire, so SG3's rule applies: no count without its admission state |
| `S10.api-portfolio` | the administrator's table, and the one place a cross-template average could appear |

**A JSON surface is still a surface.** The temptation is to scope SG1-SG4 to HTML on the grounds
that nobody *reads* JSON — but an API response is read by an integration that renders it, and a
`status: "ok"` on the wire becomes a green tick in somebody else's dashboard. Scoping the copy
gates to the pages we happen to render would be the same defect as scoping the licence gate to the
runtime set: **a rule that only watches the door it was written for.**

The cardinality time series is the gate's own denominator, so it is recorded rather than inferred:
`|SURFACES|` was 6 at P14-B2 and is 10 at P14-B3. It has never decreased.
