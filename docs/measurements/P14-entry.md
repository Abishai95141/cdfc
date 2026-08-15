# P14 entry — the surfaces, and the two decisions taken before the first template

**Written before P14-B1.** P14 is 12 engineer-days · B1 4 · B2 2 · B3 3 · B4 3.

---

## Why P14 and not P13

`plan/07` P14's entry criteria are **P5 complete** and **P0 complete**, and it says explicitly:
*"Not required, deliberately: P6, P9, P11, P12, P13."* B1–B3 render from `run.jsonl` and nothing
else. **P14 has been unblocked since day 60 and nothing has rendered a single number since.**

Verified on this tree before starting: one run over the reference filing produces **3,747 cells,
335,823 bytes of `run.jsonl`, settled fraction `0.5065`**, with `admissionState: PRE-GATE` and its
caveat already computed. Every input B1 needs exists. **Nothing consumes it.**

**P13 at `k = 0` is 4 engineer-days of a guard, a deferred clause graph, a fail-closed extractor
and a watcher — no buyer-visible output**, and its one substantial build (`propose.py`) is gated by
`ci/barrier5.sh` on a `RETAIN` decision that cannot be obtained, because no statutory instrument is
pinned (`docs/decisions/D-P7-01`). Building it next would add days and change nothing anyone can
look at.

---

## DECISION 1 — the buyer is the **administrator / consultancy**, not the single FME

Whoever files the same nine formats repeatedly for many entities, and eats the rework. Two
consequences, and the first is a hazard rather than a feature request.

### 1a. The never-average guard becomes the load-bearing control of this phase

`transfer/report.py::render_table` raises `AverageAttempted` if any caller reduces the per-template
rows to a single figure, and `plan/00` §7 already records *"averaging the settled fraction across
templates — it is a per-template property"* as a thing that fails a test.

**A portfolio view is precisely where somebody averages it.** *"Our clients average 87% settled"* is
the single most saleable sentence this product could emit and it is meaningless: the settled
fraction's denominator is a **different template's unlocked-cell mask** in every row. Averaging
them divides one workbook's cells by another workbook's, and the result is a number with no
denominator at all — **M1, the founding defect of this whole plan, re-entering through the screen
the buyer actually wants.**

> **RULING: the portfolio view renders a TABLE, one row per (entity, template, run), and there is
> no total row.** The guard is not a lint on the renderer; it is `AverageAttempted` raised from the
> only function that can produce the rows. A portfolio summary card, if one ships, carries counts —
> *runs, entities, templates* — never a fraction.

### 1b. The API is the integration surface, not a convenience

An administrator has its own workflow system. `/v1/*` (P14-B3) is where this product is consumed,
which means **the API is a surface under SG1–SG4 exactly like the HTML** — it is in `SURFACES`,
it renders numbers, and `NC-D03b`'s absent-vs-empty-vs-zero rule is an API contract before it is a
screen.

---

## DECISION 2 — ship **ADVISORY** and say so; the corpus is not funded

`G-CORPUS` is on its `FAIL` branch. There is no clean corpus, no predicate is admitted under G4,
and a single predicate cannot reach `BLOCKING` until **n ≥ 189** — 95–160 person-days of
blind-filling, which `plan/06` §2.7(b) names as *the real critical path of the product as opposed
to the paper*. It is not funded, and that is the decision rather than an omission.

**What that obliges the surface to do:**

| | |
|---|---|
| every FFR cell | renders `uninformative` — and via `render_ffr`'s **three** cases, not one: no qualification row, `SELF-AUTHORED` provenance, **or a corpus not computed-independent of the predicate** |
| the predicate-library column header | carries the corpus-provenance census |
| `admission_state(run)` | **computed from the contributing predicates' qualification rows**, never a constant, never a template literal. Today it computes `PRE-GATE` |
| the hero | carries `predicate set: PRE-GATE` in the same block as any settled count |
| `docs/OPEN-ITEMS.md` | carries the corpus as a standing item **rendered with its age**, so the gap gets louder rather than quieter |

**This is not a weakness to be managed on the surface. It is the product.** A tool that renders
`uninformative` where a competitor renders a rate is the tool whose numbers can be relied on when
it does print one.

---

## The hazard inside this phase's own exit gate

Criterion 1 reads `surfaces_passing_all_four_gates == len(SURFACES)` — **and this build writes
`SURFACES`.** A surface that cannot be made to pass SG1–SG4 can be deleted from the registry and
the gate goes green, with the sweep still reporting `caught == active`. That is **M1 again**: the
numerator choosing its own denominator, sitting inside the gate meant to prevent it.

So `SURFACES` and `REQUIRED_NUMBERS` are **append-only with a growth log**; a row may be *retired*
with a dated argument but never deleted; both cardinalities publish as a time series so a registry
that shrinks the day before a gate is read is visible in the artifact the gate is read from; and a
retired surface leaves the gate's **denominator** but stays in the **scan** — we may give up on
auditing a surface, never on prohibiting an all-clear on it. `NC-A30`, injector
`delete_failing_surface`.

---

## What ships, in order

| build | days | deliverable |
|---|---:|---|
| **B1** | 4 | `reports/<run_id>/report.html` — inline CSS/JS, **zero external references**, openable from `file://` with the network down, emailable, hashable, **and therefore the attested artifact**. A file has a hash; a single-page application does not |
| **B2** | 2 | The Unchecked panel — the 1,849 cells nobody checked, by name and reason. **The strongest thing this product renders** |
| **B3** | 3 | The drop screen and `/v1/*`, with the portfolio table and its no-total-row rule |
| **B4** | 3 | The predicate library, the funnel and the history chart, every FFR `uninformative`, corpus census in the header. **`RESTRICTED` is never treated as `PASS`** |

**The band never fills, structurally.** `band_segments` always ends with
`NOT_SETTLEABLE_FROM_ARTIFACT` and `RESIDUE`, both hatched, both with non-zero rendered width,
whether or not their counts are known — so `sum(settled widths) < total width` strictly, for every
input. A reader cannot see a full bar, because there is no input that produces one.

## What P14 does not settle, stated at entry

It does not make any check better, and it does not move severity. It converts the no-all-clear
commitment from a preference expressed in three documents into **four gates whose denominator is a
machine-maintained registry**. If a reader can conclude *"this filing is fine"* at a glance — from a
colour, a glyph, a chip, a trend, or a fraction near 1 — the phase failed regardless of what the
gates say, and `docs/DESIGN-ADAPTATION.md` already records that the gate catches tokens and cannot
catch a composition.
