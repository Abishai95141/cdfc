# 07 — THE SURFACE, TRANSFER AND OPERATIONS PHASES
## P14 and P15, in full · build plan, part 7 · compiled 11 August 2026

**This document specifies P14 and P15 and nothing else.** It uses the phase IDs, the build numbering, the
ordering, the gates and the effort figures of `plan/00-decomposition.md`, and it satisfies
`plan/01-validation-methodology.md` — whose test taxonomy (§1), negative-control catalogue (§2), mutation
regime (§3), Definition of Done (§4), CI pipeline (§5) and fixture strategy (§6) are referenced **by name**
here and never restated. Where this document adds a catalogue entry it says so and gives the entry's full
shape; where it relies on an existing one it names the id and stops.

**Why these two phases are written together.** P14 builds the surfaces and P15 makes them move. Every
commitment this project has made is a commitment about what a *surface* is allowed to say, and the two
phases split at exactly one seam: **P14 asks whether a surface can be prevented from lying; P15 asks
whether it tells the truth when the world underneath it changes.** A no-green-tick gate that passes on a
frozen repository and a settled fraction that never falls are the same defect, one static and one dynamic.

---

## §0 — THE FOUR THINGS THIS DOCUMENT DECIDES BEFORE IT BEGINS

Four details are under-determined across the binding documents. Three are ambiguities to rule on; the
fourth is the set of registry edits these phases owe back to the methodology. Each is decided here, with
its reason, so that no build starts on an ambiguity and no addition ships unscanned.

### 0.1 The rendering package is `src/cdfc/surface/` — DECIDED

`plan/00-decomposition.md` §5 P14 names `surface/render.py`, `surface/api.py` and `surface/labels.py`, and
its P0 negative control names the fixture path `src/cdfc/surface/templates/report.html.j2`, which ships in
P0 — before P14 exists. `plan/01-validation-methodology.md` §0.4 lists the same directory as `report/`.

**Ruling: `src/cdfc/surface/`.** *Reason:* `report` already names two other things in this repository —
the *artifact* (`report.html`) and the CI output directory (`reports/`) — and three meanings of one word in
one tree is precisely how a scan set stops covering a directory without anyone noticing, which is NC-D01's
mechanism applied to our own CI. `surface/` names the category and collides with nothing.

**Consequence for the catalogue, and it is an improvement, not a compatibility shim.** NC-A02's injector
`injectors/plant_glyph.py` must not hard-code a directory string. It resolves its target from
`cdfc.surface.render.TEMPLATE_DIR` at injection time. A hard-coded literal would make the injector and the
gate agree about a path while the renderer used another — the two-implementations-one-misconception failure
of §7.5, in the one place we cannot afford it. `tests/negative/test_nc_ci.py::test_nc__A02e_injector_resolves_the_live_template_dir`
asserts the injector's target equals `render.TEMPLATE_DIR`.

### 0.2 The pixel-level audit uses a real browser — DECIDED, with its runner-up and switch trigger

`plan/00-decomposition.md` P14 is explicit: *"the equal-type-size property is checked by rendering and
measuring, not by reading the stylesheet."* Reading the stylesheet re-implements the cascade, and a
re-implementation can share the renderer's misconception.

**DECIDED: `playwright` (Python), test-time only, browser revision pinned in the CI image.** Licence
**Apache-2.0 — SECONDARY**; it enters `docs/LICENCES.md` as a **dev-time** dependency with `opened_by`
blank, and §5.2's Phase-2 blocking rule applies to *runtime* dependencies only, so it is admissible now and
must be opened before the code ships like every other SECONDARY row.
*Runner-up it beat:* parsing the compiled stylesheet with `tinycss2` and resolving the cascade ourselves.
*Switch trigger, stated in advance:* if the browser revision cannot be pinned reproducibly across the two
CI runner images, fall back to `ci/surface_audit.py --engine=cssom`, **and the report of that gate then
carries the literal string `WEAKER INSTRUMENT — cascade re-implemented, may share a misconception with the
renderer`** on every run. A degraded instrument that says it is degraded is admissible; one that does not
is the product's own failure mode.

**Hard constraint.** `playwright` must never become reachable from the online path.
`tests/negative/importgraph.py`'s banned import set for `cdfc.surface` gains `playwright`, `selenium`,
`subprocess`; `tests/unit/test_surface_imports.py::test_surface_has_no_browser_dependency` asserts it.
This is the same structural test as `test_no_libreoffice_online` and it exists for the same reason.

### 0.3 P15-B4's exit criterion depends on P11, which the skeleton's entry list does not name — SURFACED, not silently fixed

`plan/00-decomposition.md` gives P15's entry as P7 + P8 + P14-B4, and its exit gate as *"a deployed report
re-derives byte-identically from a clean clone"* — which is `cdfc verify`, and `verify` is P11-B2. Under the
§4.1 schedule P15 can start (day 95) before P11 finishes (day 104).

**Ruling: P15-B4's acceptance splits.** The **deployment** sub-gate (the container runs `make demo` offline
from a clean clone and serves the drop screen and the API) is evaluable at P15 start. The
**byte-identity-of-a-published-report** sub-gate is evaluated when P11 lands. If P11 has not landed when
P15's gate is read, the gate is recorded `DEFERRED — byte identity of a published report, pending P11-B2`
and that string renders in `docs/GATE-LIVENESS.md` and on the deployment status surface. **It is never
recorded as a pass.** A deferred gate that looks like a passed gate is the whole failure this plan exists
to refuse, at the level of the plan.

### 0.4 The deltas these two phases make to the methodology's own registries — stated once, here

These phases add directories, scripts and modules that `plan/01-validation-methodology.md` §0.4, §3.5 and
§5.3–5.4 do not list, because they did not exist when it was written. **An addition that is not entered in
those registries is an unscanned surface, which is NC-A10 applied to the test apparatus.** Each delta below
is therefore a required edit to the named file, made in the build that introduces it, and each is a DoD
line-G item.

**(a) Source tree.** `src/cdfc/report/` in methodology §0.4 re-reads **`src/cdfc/surface/`** (§0.1). Four
packages are new: `surface/` (P14), `transfer/` (P15-B1), `churn/` (P15-B2), `ops/` (P15-B3).

**(b) Test tree.** One new directory, **`tests/surface/`** — the rendered-DOM gate tests (`test_sg1.py`,
`test_sg4.py`, `test_registry.py`). It is separate from `tests/e2e/` because it needs a *rendered artifact*
plus a *browser*, and mixing a browser dependency into `tests/e2e/` would put `playwright` on the offline
demo path, which §0.2 forbids. Per methodology §1.0 it gets exactly one `Makefile` entry point,
**`make surface-audit`**, and it is added to `tests/test_suite_census.py`'s collected set so it cannot
silently shrink.

**(c) Mutation tiers — `docs/MUTATION-THRESHOLDS.md` gains four rows.** Methodology §3.5's Tier-S row reads
`report/`; it re-reads `surface/`. The three new packages are unlisted and are assigned here, each with the
argument §3.5 requires:

| Module | Tier | `K/V` floor | Argument |
|---|---|---:|---|
| `surface/` (rest) | S | 0.70 | Rendering. A survivor changes how a number looks, not whether it is right |
| `surface/labels.py`, `surface/admission.py` | **V** | **0.90** | Promoted — see P14-B1. They decide whether a number renders at all and whether it renders with its admission state |
| `surface/library.py`, `surface/funnel.py` | **V** | **0.90** | Promoted by the adversary pass. `library.py` decides whether a kill rate renders **with both of its denominators**, with its six-integer observability census and with its instrument-independence label; `funnel.py` decides whether a candidate a gate never evaluated is counted as a survivor. A surviving mutant in either publishes a confident number computed over a population the reader cannot see — which is verdict-critical behaviour that happens to live in a rendering package, the same argument that promoted `labels.py` |
| `churn/` | **Q** | **0.85** | It decides whether a predicate's numbers are hidden and whether it leaves the settled numerator. That is qualification behaviour that happens to live outside `qualify/` |
| `transfer/`, `ops/` | S | 0.70 | Neither is on the verdict path. `ops/staleness.py` is the exception in spirit and is covered instead by NC-X01, whose guard is behavioural |

**Every one of these is a raise or a same-level assignment. Nothing here lowers a threshold**, so §3.5's
"lowered only by an argument that the old one was wrong" rule is not engaged.

**(d) CI greps — `ci/GATES.md` and methodology §5.4's table gain four rows, and stage 2's clock moves.**
Methodology §5.4 requires that *every* grep have a planted control in `tests/negative/test_nc_ci.py`
asserting a non-zero exit. All four are given one here; the two that had none until this edit are marked ★.

| Script | Introduced by | **Catalogue id** | Scans | Forbids | Planted control in `tests/negative/test_nc_ci.py` |
|---|---|---|---|---|---|
| `ci/no-locale-format.sh` | P14-B1 | **NC-CI10** | `src/cdfc/surface/` | `locale.`, `{:n}`, `babel` | ★ `test_nc__CI10_locale_format_is_caught`, injector `injectors/locale_number_format.py` (reused from NC-A03) |
| `ci/no-imported-prior.sh` | P14-B2 | **NC-CI11** | `src/cdfc/surface/`, `remedies.yaml` | `1.72`; `NAV tolerance` used as a threshold rather than as a question | ★ `test_nc__CI11_imported_prior_is_caught`, injector `injectors/plant_luxembourg_threshold.py` (new — writes `1.72%` into a `Remedy.text`) |
| `ci/no-scheduled-polling.sh` | P15-B3 | NC-X07 | workflows, `fly.toml`, crontabs, `src/cdfc/ops/watcher.py` | a schedule while the endpoint's terms row is `read: false` or `polling_permitted: UNKNOWN` | `test_nc__X07_no_scheduled_polling_without_terms`, injector `add_scheduled_poll.py`; positive control `test_nc__X07b_manual_one_shot_is_permitted` |
| `ci/no-remembered-integer.sh` | P15-B3 | **NC-CI12** | `src/`, `docs/` | the literal `2235`/`2,235` on a line that also names the register | ★ `test_nc__CI12_withdrawn_integer_is_caught`, injector `injectors/quote_2235.py` (new) |

**Three of these four greps had a planted control and no catalogue entry, which is an orphan guard by
`plan/01-validation-methodology.md` §2's own meta-test.** `test_nc_meta__no_orphan_guard` requires every
test under `tests/negative/` to appear in the catalogue, and `test_nc_meta__catalogue_schema` requires one
entry per id; a guard named `test_nc__CI1_…` belonged to no entry at all, and its slug additionally sat one
character away from `02`'s `NC-CI01`. **Ids are drawn from `01` §2's canonical registry — this document references, it does not allocate
(C9) — and the guard slugs move with them.** Full entry shapes are given in
P14-B1, P14-B2 and P15-B3 respectively, in the §2 shape, each with its `flips:` values.

**Stage 2's and stage 12's wall clocks move**, and both movements are recorded in `ci/GATES.md`. The
arithmetic is not restated here: **`01` §5.3 owns the stage budget table**, `test_ci__stage_clocks_match_gates_md`
asserts the table and `ci/GATES.md` agree row for row, and the four gates above are four of that table's
stage-2 rows. Stage 12 moves 2 min → 3 min for P14's surface audit. The PR budget stays under 12 minutes.
**A stage whose clock moves without a recorded reason is how a budget stops being a budget**, and a
document that restates another document's total is how two budgets start disagreeing.

**(e) One document is created that no earlier phase creates: `docs/OPEN-ITEMS.md`.** P0 creates
`docs/FIELD-OBSERVATIONS.md` (E1, E1b — sender, date sent, date of reply or the standing absence);
`docs/OPEN-ITEMS.md` is its sibling for items that are *decisions nobody has argued* rather than *questions
nobody has answered* — `K`/`T`, `STALENESS_BOUND_DAYS`, the filer-signs legal review, Person A. It ships in
**P14-B1**, because `surface/openitems.py` reads both files and a reader that reads a file the plan never
creates is a broken build on day one. Row shape:
`{id, item, why_open, decision_rule, opened_at, closes_when, renders_as}` — `renders_as` is the literal
string the surface prints while the item is open, and for `K`/`T` and `STALENESS_BOUND_DAYS` that string is
`PLACEHOLDER`.

---

# P14 — THE SURFACES: REPORT, SCREENS, API, COPY GATES

**Effort: 12 engineer-days** · B1 4 · B2 2 · B3 3 · B4 3
*Assumption:* one competent engineer, ~6 productive hours/day, fluent in Python, Jinja2 and FastAPI, and
willing to write a headless-browser assertion harness rather than a stylesheet grep. No context switching.
Nothing in P14 requires a second person's calendar.

## P14 · What it settles

**Whether the no-green-tick commitment survives contact with a rendering surface, an API integration and an
intern.**

Precisely: whether the commitment can be made a **property of the system** rather than a property of the
people writing copy. Today it is a preference expressed in three documents and a shell script that has
never been observed to fail against a rendered artifact. P14 converts it into four gates whose denominator
is a machine-maintained registry of every surface that can show a human a number.

Three sub-questions no earlier phase can answer:

1. **Can a self-contained artifact carry every number the run produced?** "Self-contained" and "renders
   every number" are both claims with an unstated denominator until a registry supplies one.
2. **Can a settled count be made structurally unable to render without the admission state of the predicate
   set that produced it?** Criterion A11 states the requirement; nothing has ever enforced it.
3. **Is the copy gate scanning the surfaces that exist?** NC-A02b names this hazard for templates. P14
   raises it one level: a surface that is not in the registry is scanned by nothing.

## P14 · Entry criteria

| Build | Requires | Why the edge is real |
|---|---|---|
| **B1, B2, B3** | **P5 complete.** `run.jsonl`, the run record, the eight item states, the thirty reason codes, the eight run-level `invalid.*` causes, the seven-term closure and the settled-fraction object of spec §III.4.3 all exist and are stable | The renderer renders a *value object*, not a database. If the settled-fraction object's shape is still moving, every template is a guess and every test pins a shape that will change |
| **B1, B2, B3** | **P0 complete.** `ci/no-green-tick.sh` exists and has been **observed red** against a named broken build, recorded in `docs/GATE-LIVENESS.md` | P14 extends that gate. Extending a gate that has never been red extends nothing |
| **B2** | **P10 for the residue exhibits** — *soft*. The exhibit section ships in B2 and renders `not yet measured` until P10 lands | An absent section is how the panel's strongest row disappears silently. The section is never absent; only its contents are pending |
| **B3** | **P2 complete** for `/v1/templates` `field_surface` and `settled_fraction_ceiling` (`null` for the two workbooks with no protection mask) | The absent-vs-empty-vs-zero rule (NC-D03b) is an API contract before it is a screen |
| **B4** | **P7 complete** (the registry, the rejection rows, the five-gate funnel) **and P8 complete** (G4, the FFR fields, `severity_tier`) | The funnel needs rejection rows; the FFR column needs a G4 result — including a G4 result that is "no predicate is admissible", which is a result and renders |
| **B4** | **Gate G-CORPUS evaluated** — *any of its three ways* (`PASS`, `RESTRICTED`, `FAIL`) | G-CORPUS governs whether an FFR may carry **digits**, not whether the surface exists. On `FAIL` B4 ships with every FFR cell rendering `uninformative` and the corpus-provenance census in the column header; on `RESTRICTED` it ships digits only for the classes the ready-today corpora license, with the literal `G-CORPUS: RESTRICTED` in the header. **B4 must never treat `RESTRICTED` as `PASS`** |

**Not required, deliberately:** P6, P9, P11, P12, P13. B1–B3 render from `run.jsonl` and nothing else.

## P14 · Builds

---

### BUILD P14-B1 — THE REPORT: ONE SELF-CONTAINED HTML FILE · 4 days

**What it produces.** `reports/<run_id>/report.html` — inline CSS, inline JS, zero external references,
server-generated, openable from `file://` with the network stack down, emailable, hashable, and therefore
**the attested artifact**. A file has a hash; a single-page application does not.

#### Files created

```
src/cdfc/surface/__init__.py
src/cdfc/surface/labels.py          THE label registry, the surface registry, the number registry
src/cdfc/surface/render.py          the renderer and TEMPLATE_DIR
src/cdfc/surface/band.py            the stacked band's geometry and its never-fills invariant
src/cdfc/surface/inline.py          the asset inliner and the external-reference assertion
src/cdfc/surface/admission.py       the admission state, computed per run, never a constant
src/cdfc/surface/openitems.py       standing unanswered questions, rendered with their age
src/cdfc/surface/templates/report.html.j2
src/cdfc/surface/templates/_hero.html.j2
src/cdfc/surface/templates/_band.html.j2
src/cdfc/surface/templates/_failure_item.html.j2
src/cdfc/surface/templates/_strapline.html.j2
src/cdfc/surface/templates/_openitems.html.j2
src/cdfc/surface/templates/_invalid.html.j2
src/cdfc/surface/static/report.css      compiled, inlined at render time, never linked
src/cdfc/surface/static/report.js       ~50 lines: filter and expand. No fetch, no import
docs/OPEN-ITEMS.md                      NEW — see §0.4(e); openitems.py reads it and FIELD-OBSERVATIONS.md
ci/no-locale-format.sh                  NEW stage-2 grep, with its planted control — §0.4(d)
docs/measurements/P14-surface-audit.md
perf/BUDGET-CHANGES.md                  three new budget ids, appended
```

#### Public interface, verbatim

```python
# src/cdfc/surface/labels.py

@dataclass(frozen=True, slots=True)
class Label:
    id: str                      # "hero.left", "hero.right", "strapline.canaries", ...
    binding: str                 # the exact run-record path this label reads
    template: str                # "{F} failures across {S} checks"
    surfaces: tuple[str, ...]    # SurfaceSpec ids this label may appear on

@dataclass(frozen=True, slots=True)
class SurfaceSpec:
    id: str                      # "S02.report-hero"
    kind: Literal["HTML", "JSON", "STDOUT", "DOC"]
    renders: frozenset[Literal["SETTLED_COUNT", "FFR", "VERDICT_NAME", "STATE", "RATE", "NONE"]]
    entrypoint: str              # dotted path to the callable or template that produces it

@dataclass(frozen=True, slots=True)
class NumberSpec:
    id: str                                   # "settledFraction.unsettled.notRun"
    extract: Callable[[RunRecord], str]       # the rendered decimal string, canonical formatting
    surfaces: tuple[str, ...]                 # where it MUST appear

LABEL_REGISTRY:  Mapping[str, Label]
SURFACES:        tuple[SurfaceSpec, ...]      # THE denominator of this phase's number. APPEND-ONLY.
REQUIRED_NUMBERS: tuple[NumberSpec, ...]      # THE denominator of "renders every number". APPEND-ONLY.

SCAN_ROOTS:      tuple[str, ...]              # THE scan set. ci/no-green-tick.sh, SG1 and SG4 all read
                                              # THIS and never a directory literal. Created at P0 as
                                              # ("src/cdfc",); P14-B1 extends it. See 01 §5.4.
BANNED_GLYPHS:   frozenset[str]               # single source of truth, imported by ci/no-green-tick.sh
BANNED_PHRASES:  frozenset[str]
GREEN_HUE_BAND:  tuple[float, float] = (80.0, 160.0)   # HSL degrees; see SG4

def render_ffr(q: Qualification | None) -> FfrCell: ...
    # returns FfrCell(text="uninformative", digits=False) whenever the rate is uninformative, which is
    # THREE cases, not one:
    #   (a) q is None;
    #   (b) q.g4.corpus_provenance == SELF-AUTHORED;
    #   (c) q.g4.clean_corpus_independent_of_predicate is False -- the COMPUTED field of 01 §6.3 item 6,
    #       true whenever the corpus generator's import closure meets the predicate's evaluation closure
    #       or read_keys(p) intersects the corpus's computed_cells.
    # There is no code path in this function that formats a float in any of the three.
```

**Case (c) is new and it is the one that matters.** A clean corpus whose *input* cells are filled and whose
*derived* cells are computed by the same evaluator the arithmetic predicates re-check makes an arithmetic
predicate's false-failure rate **zero by construction, regardless of the predicate's quality** — and the
corpus generator is deterministic from a seed, so the `n ≥ 189` that buys `BLOCKING` costs one command.
`render_ffr` is the last place that can refuse to print it, and the refusal must not be keyed on the
provenance *label* alone. `qualify/g4_ffr.py` raises `UninformativeCorpusError` upstream; this function
fails closed if the exception was ever caught. `tests/unit/test_labels.py::test_render_ffr__non_independent_corpus_prints_no_digit`
asserts it, with the admission-side twin `test_render_ffr__register_derived_membership_prints_digits` —
`REGISTER-DERIVED` is genuinely independent of our evaluator and **must** still license an FFR, or this is
a refuse-everything renderer scoring perfectly on its own negative control.

#### `SURFACES` and `REQUIRED_NUMBERS` are append-only, because this phase's gate divides by them

**This is the phase's own instance of M1 — the numerator choosing its own denominator — and it sat inside
the exit gate.** Criterion 1 reads `surfaces_passing_all_four_gates == len(SURFACES)`, where `SURFACES` is
a registry **this build writes**. A surface that cannot be made to pass SG1–SG4 can be deleted from the
registry and the gate goes green, with `caught == active` still true and NC-A10 still silent — NC-A10
catches a surface that renders *through a known render path*, not a surface **removed from the register**.
The residue NC-N09 declares the *incompleteness* of the registry honestly and says nothing about its
*shrinkage*, which is a different and cheaper failure.

Both registries obey **R-DENOM-1** (`plan/01-validation-methodology.md` §5.1):

- **Append-only, with a growth log**, exactly like `tests/negative/catalogue.yaml`. A row may be
  **retired** — it keeps its entry and carries `retired_on` and `retired_because` — and may never be
  deleted. `tests/surface/test_registry.py::test_surface__registry_is_append_only` fails the build
  otherwise, by diffing the registry against its own log rather than against a previous commit, so the
  check survives a squash.
- **A retirement requires a dated argument** in `docs/measurements/P14-surface-audit.md`, naming the
  surface id and why it cannot be brought under the gates. This is the same mechanism the phase already
  requires for removing a `NumberSpec`; it now applies to `SurfaceSpec` too, and it is now a test rather
  than a sentence in the failure table.
- **Both cardinalities publish as a time series** — `|SURFACES|` and `|REQUIRED_NUMBERS|` per commit in
  `docs/measurements/P14-surface-audit.md` — so **a registry that shrinks the day before a gate is read is
  visible in the artifact the gate is read from.**
- `tests/surface/test_registry.py::test_surface__retired_rows_are_still_scanned` — a retired surface is
  removed from the gate's *denominator*, not from the *scan*. SG1 still greps it. A surface we gave up on
  auditing is not a surface we gave up on prohibiting.

New catalogue entry, appended in the §2 shape (id from this document's `A30–A49` block, per `01` §2):

```yaml
- id: NC-A30
  component: surface
  break: "a surface that cannot pass SG1-SG4 is deleted from SURFACES, so the gate's denominator shrinks to meet its numerator"
  measured_instance: "M1, the plan's own founding mechanism: 99.2% settled from a denominator built out of the numerator"
  injector: delete_failing_surface
  why_impossible: null
  guard_tests:
    - path: tests/surface/test_registry.py::test_surface__registry_is_append_only
      flips: true
    - path: tests/surface/test_registry.py::test_surface__gate_floor_is_the_logged_cardinality
      flips: true
    - path: tests/surface/test_registry.py::test_surface__retired_rows_are_still_scanned
      flips: false
  positive_control: tests/surface/test_registry.py::test_surface__a_retirement_with_a_dated_argument_is_accepted
  status: ACTIVE
```

`injectors/delete_failing_surface.py` removes one `SurfaceSpec` that is currently failing SG4 and re-runs
the audit; without the repair the audit prints a smaller pair of integers and passes.

```python
# src/cdfc/surface/admission.py

AdmissionState = Literal["PRE-GATE", "PARTIALLY-ADMITTED", "ADMITTED"]

def admission_state(run: RunRecord) -> AdmissionState: ...
    # Computed from the qualification rows of the predicates that PRODUCED THIS RUN'S counts.
    # PRE-GATE  iff no contributing predicate has a g4 row with corpus_provenance != SELF-AUTHORED.
    # Never read from a constant, a config file, or a template literal.
```

```python
# src/cdfc/surface/render.py

TEMPLATE_DIR: Final[Path]            # resolved once; injectors and the scan set read THIS
STATIC_DIR:   Final[Path]

@dataclass(frozen=True, slots=True)
class Hero:
    failures: int
    settled: int
    unchecked: int
    admission: AdmissionState        # NO DEFAULT. A Hero cannot be constructed without it.

def render_report(run: RunRecord, *, out: Path) -> ReportArtifact: ...
    # ReportArtifact(path, sha256, n_bytes, surfaces_rendered: frozenset[str])
    # Raises ClosureViolation  -> report generation ABORTS. There is no degraded report.
    # Raises UnregisteredSurface if a template emitted a surface id not in SURFACES.
```

```python
# src/cdfc/surface/band.py

Pattern = Literal["SOLID", "HATCH"]

@dataclass(frozen=True, slots=True)
class Segment:
    kind: Literal["SETTLED_PASS","SETTLED_FAIL","INDETERMINATE","NOT_RUN","NO_PREDICATE",
                  "ERROR","NOT_SETTLEABLE_FROM_ARTIFACT","RESIDUE"]
    count: int | None                # None == "not yet measured"; renders as such, never as 0
    pattern: Pattern
    label: str                       # ABSOLUTE COUNT. Never a percentage.

def band_segments(sf: SettledFraction, residue: Residue | None) -> tuple[Segment, ...]: ...
    # INVARIANT: the returned tuple always ends with NOT_SETTLEABLE_FROM_ARTIFACT and RESIDUE,
    # both HATCH, both with non-zero rendered width, whether or not their counts are known.
    # Therefore sum(settled widths) < total width, strictly, for every input. The band never fills.
```

```python
# src/cdfc/surface/inline.py
def inline_assets(html: str, *, static_dir: Path) -> str: ...
def assert_no_external_refs(html: str) -> None: ...
    # Raises ExternalReference naming the offending attribute and its value.
    # Scans: src, href, srcset, poster, data, action, formaction, @import, url(), <link>,
    #        fetch/XMLHttpRequest/WebSocket/import() literals in inlined script,
    #        and any attribute whose value matches r"^(https?:|//|ws{1,2}:)".
```

```python
# src/cdfc/surface/openitems.py
def standing_open_items(now: date) -> tuple[OpenItem, ...]: ...
    # Reads docs/FIELD-OBSERVATIONS.md and docs/OPEN-ITEMS.md.
    # An item with a sent date and no reply date renders as
    #   "asked <date>, no reply after <n> days"  -- NEVER as absence.
```

#### The hero, fixed in the label registry so it cannot drift

| Label id | Template | Binding |
|---|---|---|
| `hero.left` | `{F} failures across {S} checks` | `F = settledFraction.settled.fail` · `S = settledFraction.settled.total` |
| `hero.right` | `{U} fields were not checked` | `U = indeterminate + notRun + noPredicate + error` |
| `hero.admission` | `predicate set: {A}` | `A = admission_state(run)` |
| `hero.denominator_rule` | `denominator: {R}` | `R = settledFraction.denominator.generator_rule` — **required in the same block as any settled count** |
| `strapline.predicates` | `{N} predicates` | `N = len(run.active_predicates)` — **strap line only, never the hero** |

On the reference filing (the FME blank filled clean) these read `<F> / <S>` and `<U>`, against a field
surface of **3,747**. The subordinate fraction **63.3%** may appear in the strapline; it may never appear
in the hero, and no percentage may appear in the band.

**Those figures have three different warrants and the golden test must not flatten them. A draft of this
document flattened two of them, and the adversary pass found the third.**

- **`cellsTotal = 3,747` is a property of the published file.** It is in
  `plan/01-validation-methodology.md` §0.3's fixture table, it is MEASURED, and it is pinned as a literal.
  A change is a parser regression, full stop.
- **`S` and `U` are properties of OUR CODE, not of the published file, and they were pinned as literals
  labelled MEASURED. That is corrected here.** `2,373` is the settled-cell count of *our harvest over the
  pinned blank*; the first thing G3 does is reject predicates, which **lowers it** — so a pinned literal
  fails on correct behaviour and gets quietly updated, which is exactly the rot the normative golden split
  exists to prevent. Worse, the count does not currently reconcile with the harvest that will ship: the
  claim that 2,329 of 2,373 settled cells come from *53 validation predicates* rests on a predicate set the
  harvest does not produce, because FME's 54 validations yield **20** resolvable membership predicates.
  **Therefore:** `test_golden__report_hero__fme` asserts `S == len(static_settled_cells(schema, registry))`
  and `S + U == inScope`, both **relationally**; the literals `2,373` and `1,374` move into
  `docs/HARVEST-DELTA.md` under `test_harvest_count`'s regime, which is allowed to move **with a recorded
  reason**; and `docs/measurements/P4-harvest-distribution.md` must reconcile the computed figure against
  2,373 in writing. **A divergence is a finding, not a fixture update.**
- **`F` is not pinned either**, and was already correct here: spec §II.5.1 marks the `pass 2,361 / fail 12`
  split *illustrative, not a measurement*. `test_golden__report_hero__fme` asserts
  `F == run.settledFraction.settled.fail` and `F + pass == S`; it must never pin the literal `12`.
  `tests/golden/test_golden__report__fme.py::test_golden__hero_fail_count_is_not_a_literal` asserts, by AST
  walk over the golden module, that no integer literal is compared against `hero.left`'s `F` binding — and
  it is now generalised to `S` and `U` by the same walk.

**All three are enforced by one gate rather than by three habits.** `ci/golden-literals-are-traceable.sh`
(rule R-GOLD-3, `01` §1.3 and §5.4) resolves every integer literal compared in `tests/golden/` against
§0.3's fixture table or a `reports/validation-ledger.jsonl` row and fails on an untraceable one. §6 of this
document called that check *"the fourth impossible control"*; **it is not impossible — it is a grep over a
ledger**, and R-GOLD-2's script already walks the same files.

**And the pair `2,373 of 3,747` is a `REACH` number** (`01` §0.5), never a quality one. The hero renders it
with `hero.admission` (`PRE-GATE`) and `hero.denominator_rule` in the same block; the ledger row carries
`measures: REACH`; and the caveat may not contain a verb of verification.
`tests/unit/test_labels.py::test_labels__settled_count_never_renders_without_its_denominator_rule` asserts
`hero.denominator_rule` shares an ancestor with the settled count within 2 levels — **the same structural
assertion as NC-A05's `PRE-GATE` rule, for the same reason**: the 3,747 is produced by two code paths
implementing one rule we wrote, nothing can falsify that rule until `01` §6.3 item 8 runs, and a fraction
whose denominator's generating rule is not on screen is a fraction whose denominator cannot be questioned.

#### Validation — unit

| Test | Asserts |
|---|---|
| `tests/unit/test_labels.py::test_labels__hero_bindings_are_exact` | `hero.left`/`hero.right`/`hero.admission` bind exactly the four run-record paths above; a fifth binding is a diff |
| `tests/unit/test_labels.py::test_labels__predicate_count_is_not_a_hero_label` | `strapline.predicates.surfaces` excludes `S02.report-hero` |
| `tests/unit/test_admission.py::test_admission__pre_gate_when_every_contributor_is_self_authored` | over the current registry: `PRE-GATE` |
| `tests/unit/test_admission.py::test_admission__is_not_a_constant` | `admission_state` reads `run`; `grep` for a module-level `"PRE-GATE"` literal outside the `Literal` type fails |
| `tests/unit/test_band.py::test_band__labels_are_absolute_counts` | no `%` character in any `Segment.label` |
| `tests/unit/test_band.py::test_band__unknown_count_renders_not_measured` | `count=None` → label contains `not yet measured`, and **no digit** |
| `tests/unit/test_inline.py::test_inline__catches_every_external_form` | table-driven over 11 forms: `<link href>`, `<script src>`, `@import`, `url(https:…)`, `//cdn`, `srcset`, `poster`, `form action`, `fetch(` , `new WebSocket(`, dynamic `import(` |
| `tests/unit/test_openitems.py::test_openitems__unanswered_renders_its_age` | a field observation with `sent` and no `reply` renders `no reply after N days` |
| `tests/unit/test_render.py::test_render__hero_cannot_be_built_without_admission` | `Hero(failures=1, settled=2, unchecked=3)` raises `TypeError` |

**`test_render__hero_cannot_be_built_without_admission` is the phase's structural core.** Criterion A11 is
delivered by a dataclass with no default, not by a test that remembers to check. The test's job is to prove
the type-level guard exists.

#### Validation — property

| Property | Generator | Module |
|---|---|---|
| **The band never fills.** For every settled-fraction object and every residue state, `sum(w for s in segments if s.kind.startswith("SETTLED")) < total_width` strictly | random seven-term closure-consistent partitions over `N ∈ [1, 5000]` cells, `residue ∈ {None, Residue(k) for k ∈ [0, 500]}` | `surface/band.py` |
| **`U` is a closure corollary.** `hero.right == inScope − settled.total` for every closure-consistent partition | the same generator | `surface/labels.py` |
| **Rendering is idempotent and order-invariant.** Shuffling the insertion order of `run.checks` does not change `sha256(report.html)` | random permutations | `surface/render.py` |
| **No label loses a number.** For every run record, `{n.id for n in REQUIRED_NUMBERS} ⊆ ids extractable from the rendered DOM text` | random closure-consistent runs | `surface/labels.py` |

Generator note, per §7.9: at `max_examples = 50` these explore a small space. Every real defect found in
review is pinned as an `@example` — required, not optional.

#### Validation — golden, against the nine real workbooks

| Golden test | Workbook | Why that one |
|---|---|---|
| `tests/golden/test_golden__report__fme.py::test_golden__report_hero__fme` | FME `7d9a1960…` | The only workbook with hidden sheet, `x14` validations, shared formulas, a protection mask and cross-sheet carries live at once. **Exactly one literal is pinned — `cellsTotal = 3,747`, which is in `01` §0.3's fixture table.** `S`, `U` and `F` are asserted **relationally**: `S == len(static_settled_cells(schema, registry))`, `S + U == inScope`, `F == run.settledFraction.settled.fail`, `F + pass == S` (see the warrant note above; `2,373`/`1,374` live in `docs/HARVEST-DELTA.md`). Paired **value** assertion per R-GOLD-2: the **per-sheet field surface** renders `Portfolio 1,698 · Investors 897 · PMS 480 · Introduction 371 · Summary 231 · Complaints 25 · Compliance Status 23 · AML-CFT 22`, **which sums to 3,747 and is the denominator's per-sheet decomposition — it is NOT the unchecked split.** The test asserts the sum, so a future edit that relabels one for the other fails. Every literal in this module resolves under `ci/golden-literals-are-traceable.sh` |
| `tests/golden/test_golden__report__nomask.py::test_golden__report_settled_block_has_no_digits` | `IFSCA_Annual_Reporting_Format` **and** `Draft_ACAC_Format` | The two with no protection mask. The former is the dangerous one: a naive unlocked-cell count returns **8**, which looks like a small answer rather than like no answer. Reuses NC-D03's assertion technique — a regex over the rendered settled-fraction fragment must find no digit |
| `tests/golden/test_golden__report__zeroformula.py::test_golden__report_renders_zero_percent` | `EDR_1` | Zero formulas ⇒ mechanically derivable settled fraction 0%. **Publish it anyway** — a 0% that renders is the honest case and must not be special-cased into an empty state |
| `tests/golden/test_golden__report__invalid.py::test_golden__invalid_replaces_the_screen` | `fixtures/synthetic/renamed-sheet__portfolio.xlsx` | The `INVALID` screen is a *replacement*, not a banner. Asserts the hero, the band and the settled block are **absent from the DOM**, not merely hidden by CSS |

#### Validation — determinism

`make determinism` (methodology §1.5 mechanics: `TZ=Pacific/Kiritimati` vs `UTC`, `PYTHONHASHSEED=0` vs
`1`, `LC_ALL=C` vs `en_IN.UTF-8`, two working directories) must produce a byte-identical `report.html`.
`tests/determinism/test_det__report_bytes_identical` is the P14 entry point; it is the surface half of
NC-A03 and shares its five injectors (`now_in_renderer`, `unsorted_rollup`, `live_register`, `float_money`,
`locale_number_format`).

**One P14-specific determinism hazard, named because it is easy to miss:** number formatting. `1,374` under
`LC_ALL=en_IN.UTF-8` is `1,374`; under some locales it is `1.374`; under Indian digit grouping a larger
figure would be `13,74,000`. **DECIDED: all numeric formatting is done by
`surface/labels.py::fmt(n: int) -> str` with an explicit thousands separator and no locale call anywhere.**
`ci/no-locale-format.sh` (new, stage 2) forbids `locale.`, `{:n}` and `babel` under `src/cdfc/surface/`.

#### Validation — negative controls

*Existing catalogue entries this build relies on, named and not restated:* **NC-A02** (all-clear glyph or
phrase reaches a user surface, with its four tests including the scan-set coverage test `test_nc__A02b`),
**NC-A05** (headline renders without the admission state, and its `test_nc__A05b` equal-weight/hatched
companion), **NC-D03** (a denominator for a template with no protection mask), **NC-A03** (the report does
not re-derive), **NC-E05** (closure has a hole → report generation aborts).

*New catalogue entries added by this build.* Each is appended to `tests/negative/catalogue.yaml` in the §2
shape and is `ACTIVE` from the day B1 merges.

```yaml
- id: NC-A06
  component: surface
  break: "the report needs the network to render — a CDN font, an analytics beacon, a remote image"
  measured_instance: null
  injector: cdn_font
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_inline.py::test_inline__catches_every_external_form
      flips: true
    - path: tests/e2e/test_e2e__file_url.py::test_e2e__A10_file_url_offline_renders_every_number
      flips: true
    - path: tests/e2e/test_e2e__file_url.py::test_e2e__A10b_reference_report_renders_all_of_them
      flips: false
  positive_control: tests/e2e/test_e2e__file_url.py::test_e2e__A10b_reference_report_renders_all_of_them
  status: ACTIVE

- id: NC-A07
  component: surface
  break: "a number the run produced renders on no surface at all — a silent drop, not a wrong value"
  measured_instance: null
  injector: drop_a_number
  why_impossible: null
  guard_tests:
    - path: tests/e2e/test_e2e__file_url.py::test_e2e__A10_file_url_offline_renders_every_number
      flips: true
    - path: tests/unit/test_labels.py::test_labels__every_run_number_has_a_number_spec
      flips: false     # the SPEC still exists; only its render site was removed. This guard
                       # cannot see that, and saying so is the point of the field.
  positive_control: tests/unit/test_labels.py::test_labels__every_run_number_has_a_number_spec
  status: ACTIVE

- id: NC-A08
  component: surface
  break: "the stacked band reaches 100% — a full band is a green tick drawn as a rectangle"
  measured_instance: null
  injector: band_fills
  why_impossible: null
  guard_tests:
    - path: tests/property/test_prop_band.py::test_prop__band_never_fills
      flips: true
    - path: tests/surface/test_sg4.py::test_sg4__band_terminal_segments_have_width
      flips: true
    - path: tests/unit/test_band.py::test_band__all_pass_run_still_leaves_hatched_width
      flips: false
  positive_control: tests/unit/test_band.py::test_band__all_pass_run_still_leaves_hatched_width
  status: ACTIVE

- id: NC-A10
  component: surface
  break: "a rendering surface exists that is absent from SURFACES, so no gate ever scans it"
  measured_instance: "the same defect class as NC-A02b, one level up: scope truncation applied to our own audit"
  injector: unregistered_surface
  why_impossible: null
  guard_tests:
    - path: tests/surface/test_registry.py::test_surface__every_template_is_registered
      flips: true
    - path: tests/surface/test_registry.py::test_surface__every_json_response_model_is_registered
      flips: true
    - path: tests/surface/test_registry.py::test_surface__registry_count_is_printed_with_both_integers
      flips: false
  positive_control: tests/surface/test_registry.py::test_surface__registry_count_is_printed_with_both_integers
  status: ACTIVE

- id: NC-A11
  component: surface
  break: "an INVALID run renders anything other than the replacement screen — a banner over a live report"
  measured_instance: null
  injector: invalid_as_banner
  why_impossible: null
  guard_tests:
    - path: tests/golden/test_golden__report__invalid.py::test_golden__invalid_replaces_the_screen
      flips: true
    - path: tests/e2e/test_e2e__invalid.py::test_e2e__INVALID_shows_no_fraction_of_any_kind
      flips: true
    - path: tests/golden/test_golden__report__fme.py::test_golden__report_hero__fme
      flips: false
  positive_control: tests/golden/test_golden__report__fme.py::test_golden__report_hero__fme
  status: ACTIVE

- id: NC-A12
  component: surface
  break: "a standing unanswered question renders as silence rather than as an open item with its age"
  measured_instance: "E1 (IFSCA Division of Investment Funds) and E1b (KFin/CAMS/Basiz) are sent and unanswered"
  injector: openitems_suppress_unanswered
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_openitems.py::test_openitems__unanswered_renders_its_age
      flips: true
    - path: tests/surface/test_sg1.py::test_sg1__open_items_block_is_present_on_the_report
      flips: true
    - path: tests/unit/test_openitems.py::test_openitems__answered_renders_the_answer
      flips: false
  positive_control: tests/unit/test_openitems.py::test_openitems__answered_renders_the_answer
  status: ACTIVE

- id: NC-CI10
  component: surface
  break: "a number is formatted through the locale, so 1,374 renders as 1.374 or 13,74,000 and the report stops re-deriving"
  measured_instance: null
  injector: locale_number_format
  why_impossible: null
  guard_tests:
    - path: tests/negative/test_nc_ci.py::test_nc__CI10_locale_format_is_caught
      flips: true
    - path: tests/determinism/test_det__report_bytes_identical.py::test_det__report_bytes_identical
      flips: true
    - path: tests/unit/test_labels.py::test_labels__fmt_is_the_only_number_formatter
      flips: false
  positive_control: tests/unit/test_labels.py::test_labels__fmt_renders_the_reference_figures
  status: ACTIVE
```

**Every `guard_tests` list in this document is given in the `plan/01-validation-methodology.md` §2 shape,
with a `flips:` value per guard**, because the sweep asserts the *exact* set and not "at least one". Two
entries above carry a deliberate `flips: false` on a guard that the injector cannot reach — NC-A07's
`test_labels__every_run_number_has_a_number_spec`, which sees the registry and not the render site — and
that is the field doing its job: **under the old contract that entry would have been recorded `caught` on
the strength of the e2e guard while the registry guard was never exercised.** Declaring it `false` says so
in the artifact rather than hiding it in a passing count.

**Injectors created.** `tests/negative/injectors/cdn_font.py` (writes a `<link rel="stylesheet"
href="https://fonts.example/…">` into `_hero.html.j2`) · `drop_a_number.py` (removes one `NumberSpec`'s
render site) · `band_fills.py` (`band_segments` omits the two terminal segments) ·
`unregistered_surface.py` (adds **both** a template that renders a settled count **and** a FastAPI response
model, neither in `SURFACES` — one injector, because an injector that reaches only one of an entry's guards
leaves the other permanently unobserved) · `invalid_as_banner.py` (the `INVALID` path renders
`_invalid.html.j2` *above* the normal body rather than *in place of* it) ·
`openitems_suppress_unanswered.py` (filters items with no reply; on the reference fixture E1 and E1b are
the only items, so the block empties and SG1's presence assertion goes red) · `delete_failing_surface.py`
(NC-A30, above) · `locale_number_format.py` (already in the catalogue under NC-A03; **reused here as
NC-CI10's injector**, which is why NC-CI10's `flips` set names the determinism test too).

**`NC-A09` is deliberately not in this block.** It is reserved here and defined in **P14-B3**, because it is
the API prohibition and belongs beside the schema that enforces it. The catalogue is keyed, not ordered; a
reader who expects `A09` between `A08` and `A10` should look in B3 rather than assume a dropped entry.

**The admission-side positive controls, because a reject-everything renderer scores perfectly on the
negative controls alone** (methodology §2.3's standing rule, and DoD line C5):
`test_golden__report_hero__fme` proves the report *does* render the triple; `test_nc__D03c` (existing)
proves a masked template *does* yield a number; `test_openitems__answered_renders_the_answer` proves an
answered question renders its answer rather than being suppressed as noise.

#### Validation — performance, with three new budgets

| Budget id | Subject | Baseline | Fail above | Warn above | Note |
|---|---|---:|---:|---:|---|
| `PERF-RENDER` | `render_report` on the FME reference run | ~20 ms (DERIVED from spec §III.5's F13 figure) | 60 ms | 40 ms | New. Recorded in `perf/baseline.ci.json` on first green run |
| `PERF-SIZE` | `report.html` bytes, FME reference run | to be recorded on first run | 2 MB | 1.5 MB | New, and it is the **emailability** budget. Inlining everything is exactly how a self-contained file becomes un-sendable |
| `PERF-FILEOPEN` | first contentful paint from `file://`, headless, offline | to be recorded | 1,200 ms | 800 ms | New. Advisory in P14, blocking from P15 (`ci/GATES.md`) |

`PERF-CORE` (~30 ms, fail above 60 ms) and `PERF-ONLINE` (≈450 ms, fail above 900 ms) must not regress;
`render_report` sits inside `PERF-ONLINE`.

#### Validation — the end-to-end flow this build owns

`tests/e2e/test_e2e__file_url.py::test_e2e__A10_file_url_offline_renders_every_number` — **the phase's
headline test.** Mechanics:

1. `make demo` produces `reports/<run_id>/report.html` for the FME reference run.
2. Open a Playwright context with `offline=True` and `context.route("**", lambda r: r.abort())`, plus a
   `request` listener that appends every attempted request to a list.
3. `page.goto(f"file://{path}")`.
4. Assert the attempted-request list is **empty** — not "no failed requests", *no requests*.
5. `dom = page.inner_text("body")`.
6. For every `NumberSpec` in `REQUIRED_NUMBERS`: assert `spec.extract(run) in dom`, and on failure report
   **the spec id**, so the message names which number vanished rather than saying "assertion failed".
7. Assert `len(REQUIRED_NUMBERS) == n` where `n` is read from `docs/measurements/P14-surface-audit.md`'s
   last entry, so the denominator cannot silently shrink (the same discipline as
   `test_suite_census.py`).

`test_e2e__A10b_reference_report_renders_all_of_them` is its positive control and prints
`rendered = k of n` as two integers.

#### Mutation, per methodology §3.5

`surface/` is **Tier S** (threshold `K/V ≥ 0.70`, blocking two phases after first ship). **Two modules are
promoted to Tier V by this document, with the argument required by `docs/MUTATION-THRESHOLDS.md`:**
`surface/labels.py` and `surface/admission.py`, threshold `K/V ≥ 0.90`, **blocking from P14**. *Argument:*
these two decide whether a number renders at all and whether it renders with its admission state; a
surviving mutant in either is exactly criterion A11 or A4 failing silently, which is verdict-critical
behaviour that happens to live in a rendering package. The threshold is raised, never lowered, so
§3.5's rule is satisfied.

The phase gate prints, in this exact form:
`surface/labels.py: K/V = <k>/<v> (floor) · K/(V−E) = <k>/<v−e> with E = <e> adjudicated, arguments in
reports/mutation/surface_labels.ledger.jsonl · I = <i>, T = <t> (ids listed)`.

---

### BUILD P14-B2 — THE UNCHECKED PANEL · 2 days

**What it produces.** The panel that is the product. It sits on the report screen **above the fold**, is
not an appendix, and is grouped by reason code from the closed thirty-code vocabulary with a count per
group, a specific *"what would make this checkable"* per entry, and — beneath the reasons — **demonstrated
survivors from the residue set as exhibits, not reasons.**

#### Files created

```
src/cdfc/surface/unchecked.py
src/cdfc/surface/remedies.yaml
src/cdfc/surface/templates/_unchecked.html.j2
src/cdfc/surface/templates/_residue_exhibit.html.j2
ci/no-imported-prior.sh                 NEW stage-2 grep, with its planted control — §0.4(d)
```

#### Public interface

```python
# src/cdfc/surface/unchecked.py

@dataclass(frozen=True, slots=True)
class Remedy:
    id: str
    reason_code: str                  # one of the 30
    applies_to: str                   # a selector over stable keys / obligation ids; "*" is FORBIDDEN
    text: str                         # the instrument that would move this across the line
    source: str | None                # a citation, where one exists
    specific: bool                    # asserted True by the loader; a generic remedy does not load

@dataclass(frozen=True, slots=True)
class UncheckedGroup:
    reason_code: str
    count: int
    entries: tuple[UncheckedEntry, ...]
    remedy: Remedy

@dataclass(frozen=True, slots=True)
class UncheckedPanel:
    groups: tuple[UncheckedGroup, ...]
    total: int                        # == hero.right, asserted
    exhibits: tuple[ResidueExhibit, ...] | None   # None == "not yet measured", NEVER ()

def build_unchecked_panel(run: RunRecord, residue: Residue | None) -> UncheckedPanel: ...
    # Raises MissingRemedy(reason_code) if a rendered group has no matching Remedy.
    # There is no fallback string. A reason code with no remedy is a build error.
```

`exhibits=None` versus `exhibits=()` is the `absent ≠ empty` rule applied to our own panel: `None` renders
*"residue not yet measured — see P10"*, `()` renders *"we ran the residue procedure and it returned no
survivors"*, which per §7.3 and NC-C02 would itself be a finding. **They must not look alike.**

#### The canonical entry, writable today

Reason code `no_predicate.requires_judgment`, applying to *Third Schedule Part A(g) — whether the valuation
is appropriate*. Remedy text, verbatim in `remedies.yaml`:

> a materiality threshold by scheme class of the kind CSSF Circular 24/856 Tables 1–3 specify
> (0.20% money-market / 0.50% bond and mixed / 1.00% equity and other), plus a compensation-direction rule
> of the kind its Tables 4–5 specify.

`source: "CSSF Circular 24/856, Tables 1–5"`. **The Luxembourg 1.72% may never appear anywhere on this
surface** — it is a comparator for the pitch and an input to nothing (do-not-build row 9), and
`ci/no-imported-prior.sh` (new, stage 2) greps `src/cdfc/surface/` and `remedies.yaml` for `1.72` and for
the string `NAV tolerance` used as a threshold rather than as a question.

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_unchecked.py::test_unchecked__total_equals_hero_right` | `panel.total == hero.right` for the FME reference run and for 20 generated runs |
| unit | `tests/unit/test_unchecked.py::test_unchecked__missing_remedy_raises` | a group whose reason code has no `Remedy` raises `MissingRemedy`, does not render a placeholder |
| unit | `tests/unit/test_unchecked.py::test_unchecked__wildcard_remedy_does_not_load` | `applies_to: "*"` is refused by the loader |
| unit | `tests/unit/test_unchecked.py::test_unchecked__none_and_empty_exhibits_render_differently` | `None` and `()` produce different DOM text; a regex asserts the `None` case contains no digit |
| contract | `tests/contract/test_contract__remedies_cover_the_vocabulary.py::test_contract__every_renderable_reason_has_a_remedy` | for each of the 30 codes that can reach a cell, at least one `Remedy` exists, or the code is listed in `remedies.yaml`'s `deliberately_unremediable` block **with a written argument** |
| golden | `tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme` | the FME reference run's grouping, counts summing to **1,374**, and — R-GOLD-2 — the verbatim CSSF remedy string for `requires_judgment` |
| property | `tests/property/test_prop_unchecked.py::test_prop__panel_partitions_the_unsettled_set` | over random closure-consistent runs, `sum(g.count for g in groups) == total` and no cell appears in two groups |
| e2e | `tests/e2e/test_e2e__above_the_fold.py::test_e2e__unchecked_panel_is_above_the_fold` | headless at 1280×800 and at 390×844 (phone): the panel's bounding box top is above the viewport bottom **without scrolling**, on both |

**Negative controls.** *Existing:* **NC-C02** (the residue set comes back empty) — B2 consumes its output
and must render the two states distinctly. *New:*

```yaml
- id: NC-A13
  component: surface
  break: "the Unchecked panel falls back to a generic remedy string, so every entry says the same thing"
  measured_instance: null
  injector: generic_remedy_fallback
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_unchecked.py::test_unchecked__missing_remedy_raises
      flips: true
    - path: tests/unit/test_unchecked.py::test_unchecked__wildcard_remedy_does_not_load
      flips: true
    - path: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
      flips: false
  positive_control: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
  status: ACTIVE

- id: NC-A14
  component: surface
  break: "the residue exhibit section is omitted when the residue is unmeasured, so the panel's strongest row disappears silently"
  measured_instance: null
  injector: hide_unmeasured_residue
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_unchecked.py::test_unchecked__none_and_empty_exhibits_render_differently
      flips: true
    - path: tests/surface/test_registry.py::test_surface__residue_section_always_present
      flips: true
    - path: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
      flips: false
  positive_control: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
  status: ACTIVE

- id: NC-CI11
  component: surface
  break: "an imported prior — Luxembourg's 1.72%, or 'NAV tolerance' used as a threshold rather than as a question — reaches a remedy string"
  measured_instance: "do-not-build row 9: 1.72% is a comparator for the pitch and an input to nothing"
  injector: plant_luxembourg_threshold
  why_impossible: null
  guard_tests:
    - path: tests/negative/test_nc_ci.py::test_nc__CI11_imported_prior_is_caught
      flips: true
    - path: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
      flips: false     # the CSSF remedy text is a CITATION, not a threshold, and must stay green
  positive_control: tests/golden/test_golden__unchecked__fme.py::test_golden__unchecked_groups__fme
  status: ACTIVE
```

**`injectors/generic_remedy_fallback.py` installs `Remedy(applies_to="*", text="see documentation")`** —
deliberately both a generic fallback *and* a wildcard selector, so **both** of NC-A13's guards go red under
one injector. An injector that reached only the first would leave
`test_unchecked__wildcard_remedy_does_not_load` permanently unobserved while the entry still counted as
`caught`, which is the defect the `flips` field exists to expose.

**NC-CI11's `flips: false` row is load-bearing and is not decoration.** The remedy that ships is a
**citation** — CSSF Circular 24/856's Tables 1–5, quoted as the *kind of instrument* that would make the
judgment checkable — and the gate must not fire on it. A copy gate that also blocks the lawful case is a
gate people disable, which is the same argument `ci/no-scheduled-polling.sh` makes for its own positive
control (NC-X07b).

---

### BUILD P14-B3 — THE DROP SCREEN AND THE API · 3 days

**What it produces.** One control, no settings, no account; and the ~18-path `/v1` API of spec §III.6,
synchronous request/response, **no queue, no broker, no workers** — the deterministic core is ~30 ms and
the whole 19,782-mutant campaign is 2.5 s, both MEASURED.

#### Files created

```
src/cdfc/surface/api.py               the FastAPI application and the ~18 paths
src/cdfc/surface/schemas.py           response models with the two prohibitions baked in
src/cdfc/surface/openapi_guard.py     the recursive walk over the GENERATED OpenAPI document
src/cdfc/surface/templates/drop.html.j2
tests/contract/test_contract__api_cannot_express_a_pass.py
```

#### The paths, exactly as spec §III.6 §6 fixes them

| Method | Path | Notes binding on this build |
|---|---|---|
| `POST` | `/v1/filings` | multipart. `201 {run_id, filing_sha256, template_sha256, run_state, report_url, attestation_url}`. `413` over cap · `415` non-zip · **`422` on `template_unbound` with the structural fingerprint in the body**, so an operator can admit the new template |
| `GET` | `/v1/runs/{id}` | the full run record incl. `settledFraction`, `verdict`, `livenessProof`, `manifest` |
| `GET` | `/v1/runs/{id}/checks` | `?state=&reason=&predicate_id=` |
| `GET` | `/v1/runs/{id}/cells` | `?state=&reason=&sheet=` — the closure table |
| `GET` | `/v1/runs/{id}/report.html` · `/attestation.json` · `/log.jsonl` | the HTML is **byte-identical to disk**, and its `sha256` is in the manifest |
| `POST` | `/v1/runs/{id}/overrides` | operator token. **Both states retained**, inside the signed payload, counted separately |
| `POST` | `/v1/verify` | `{reproduced, diff[]}` |
| `GET` | `/v1/templates` · `/v1/templates/{sha}/schema` | `settled_fraction_ceiling` is **`null`** for the two workbooks with no protection mask |
| `POST` | `/v1/templates` | operator token. Runs T1–T6 and **stops at T7 awaiting a human signature** |
| `GET` | `/v1/predicates` · `/v1/predicates/{id}/versions/{v}` | the full qualification block incl. `g4_corpus_provenance`. **Public and unauthenticated by design** |
| `GET` | `/v1/rejections` | every candidate the gate refused, with gate, measured number, cells it would have covered |
| `GET` | `/v1/registry/roots` · `/v1/settled-fraction/history` | **must be able to step down** |
| `GET` | `/v1/healthz` · `/v1/openapi.json` | — |

**Authentication — the spec's date is gone; the substance is kept.** DECIDED: no authentication on read
paths; the three mutating paths (`POST /v1/runs/{id}/overrides`, `POST /v1/templates`, and any future
mutating path) require an operator token supplied as a bearer header and compared in constant time.
`tests/unit/test_api_auth.py::test_api__mutating_paths_require_a_token` is table-driven **over the route
table**, not over a hand-written list, so a new mutating path added without a token fails the build.

#### The two prohibitions, enforced by schema and by test

```python
# src/cdfc/surface/schemas.py

BANNED_PROPERTY_NAMES: Final[frozenset[str]] = frozenset({
    "result", "status", "pass", "passed", "passing",
    "compliant", "conformant", "ok", "success", "clean",
})

PERMITTED_BOOLEANS: Final[frozenset[str]] = frozenset({
    "summaryIsNotSubstitute", "computedTwiceAgreed", "thirdParty",
    "clean_corpus_independent_of_predicate", "reproduced",
})
# Exactly five. Adding a sixth is a visible diff and requires a DoD line.

class SettledFractionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")
    denominator: DenominatorOut
    outOfScope: int
    informational: int
    inScope: int
    settled: SettledOut
    unsettled: UnsettledOut
    fraction: float
    residue: ResidueOut | None
    declaredGaps: list[DeclaredGapOut]
    denominatorWarning: str

    @model_validator(mode="after")
    def _fraction_never_travels_alone(self) -> "SettledFractionOut": ...
        # All six counts required whenever `fraction` is present. Constructing this model
        # with `fraction` and without them raises ValidationError. Schema property, not a check.
```

| Test | Asserts |
|---|---|
| `tests/contract/test_contract__api_cannot_express_a_pass.py::test_contract__no_banned_property_at_any_depth` | the **generated** `/v1/openapi.json`, walked recursively through `properties`, `$defs`, `definitions`, `allOf`, `anyOf`, `oneOf`, `not`, `items`, `prefixItems`, `patternProperties`, `additionalProperties`, `propertyNames`, contains no `BANNED_PROPERTY_NAMES` member, case-insensitive. Reuses `tests/contract/schema_walk.py` from NC-A01 |
| `…::test_contract__every_boolean_is_on_the_permitted_list` | every boolean-typed property in the generated document is in `PERMITTED_BOOLEANS`. A blanket "no booleans" rule would be wrong — `summaryIsNotSubstitute` is a required boolean — and a rule with an unbounded allowlist would be no rule |
| `…::test_contract__fraction_never_travels_alone` | `SettledFractionOut(fraction=0.63)` raises `ValidationError` |
| `tests/unit/test_api.py::test_api__422_carries_the_structural_fingerprint` | an unbound template returns `422` with the fingerprint in the body |
| `tests/unit/test_api.py::test_api__extra_forbid_on_every_response_model` | walks every model in `schemas.py`; `extra="forbid"` on all of them, so a consumer cannot write a `status` in at runtime either |
| `tests/unit/test_api.py::test_api__templates_ceiling_is_null_not_zero` | `IFSCA_Annual_Reporting_Format` and `Draft_ACAC_Format` return `settled_fraction_ceiling: null`, JSON `null`, distinguishable from `0` — NC-D03b's API twin |

**Negative controls.** *Existing:* **NC-Q08** and specifically `test_nc__Q08b_api_returns_null` (an FFR with
`SELF-AUTHORED` provenance renders `ffr: null`, so a client cannot display it either); **NC-A01**'s
recursive walker, reused here against a *generated* document rather than a hand-written one; **NC-D03**'s
`null`-vs-zero rule. *New:*

```yaml
- id: NC-A09
  component: surface
  break: "an endpoint returns a bare settled fraction, or a boolean whose name means pass"
  measured_instance: null
  injector: api_bare_fraction
  why_impossible: null
  guard_tests:
    - path: tests/contract/test_contract__api_cannot_express_a_pass.py::test_contract__fraction_never_travels_alone
      flips: true
    - path: tests/contract/test_contract__api_cannot_express_a_pass.py::test_contract__no_banned_property_at_any_depth
      flips: true
    - path: tests/contract/test_contract__api_cannot_express_a_pass.py::test_contract__every_boolean_is_on_the_permitted_list
      flips: true
    - path: tests/unit/test_api.py::test_api__runs_endpoint_returns_all_six_counts
      flips: false
  positive_control: tests/unit/test_api.py::test_api__runs_endpoint_returns_all_six_counts
  status: ACTIVE
```

`injectors/api_bare_fraction.py` adds `class QuickOut(BaseModel): fraction: float; clean: bool` to
`schemas.py` and wires it to `GET /v1/runs/{id}/quick`. It must turn all three `flips: true` guards red and
leave the positive control green.

**One note on `PERMITTED_BOOLEANS`.** `clean_corpus_independent_of_predicate` stays on the list — it is a
required boolean on the wire — but under `plan/01-validation-methodology.md` §6.3 item 6 it is a **derived
property computed at G4 time, not an accepted input**. `tests/unit/test_api.py::test_api__independence_is_not_settable`
asserts the field is absent from every request model and present on every FFR-bearing response model, so a
client can read it and can never assert it. A boolean whose value a caller supplies is a claim, not a
measurement.

#### Performance

`PERF-API` (new): `POST /v1/filings` end-to-end on the FME reference filing, in-process TestClient, **fail
above 900 ms, warn above 700 ms** — the same envelope as `PERF-ONLINE`, because the API adds serialisation
and nothing else. There is no throughput budget: at **3.4 filings per working day** (868/yr MODELED, from
217 FMEs × 4 quarters) a throughput target would be theatre, and saying so is more useful than measuring it.

---

### BUILD P14-B4 — THE FFR-BEARING SURFACES · 3 days · **hard-gated on P8 (G-CORPUS)**

**What it produces.** Three surfaces the category does not have: the **predicate library**, the **five-gate
attrition funnel**, and **settled fraction over time**.

#### Files created

```
src/cdfc/surface/library.py
src/cdfc/surface/funnel.py
src/cdfc/surface/history.py
src/cdfc/surface/templates/library.html.j2
src/cdfc/surface/templates/rejected.html.j2
src/cdfc/surface/templates/funnel.html.j2
src/cdfc/surface/templates/history.html.j2
reports/settled-history.jsonl          append-only; the chart's only input
docs/measurements/P14-surface-audit.md
```

#### Public interface

```python
# src/cdfc/surface/library.py

@dataclass(frozen=True, slots=True)
class KillRateCell:
    G: int; U: int; I: int; O: int; R: int; K: int   # SIX integers. O == G - U - I.
    per_fault_class: Mapping[str, tuple[int, int]]   # class -> (K, O)
    indeterminate_cells: tuple[str, ...]             # the cells that made I non-zero, named
    instrument_label: str | None                     # "SAME-AUTHOR — a weaker instrument", or None
    # There is no code path that renders K/O without I beside it. `I` is the count of mutants whose
    # observability could not be decided because recalculation touched a cell the evaluator could
    # not compute. It is excluded from O and reported as its own integer.

@dataclass(frozen=True, slots=True)
class LibraryRow:
    predicate_id: str
    version: int
    clause: ClauseRef                 # eId + verbatim quote + page/bbox link
    cel_source: str
    claims_fault_classes: tuple[str, ...]   # NON-EMPTY, from the envelope, inside code_sha256
    kr_claimed: KillRateCell          # K/O over claims_fault_classes -- the registry bar's own number
    kr_all_classes: KillRateCell      # K/O over ALL FOURTEEN classes -- printed BESIDE it
    degeneracy: DegeneracyVerdict     # verdict + z3 witness sha256, or "unproven"
    ffr: FfrCell                      # from labels.render_ffr -- three uninformative cases, see B1
    severity_tier: Literal["BLOCKING", "ADVISORY"] | None
    liveness: LivenessWitnesses       # kill_case + pass_case digests
    flag_everything_would_have_scored: KillRateCell   # printed BESIDE each rule
    state: Literal["ACTIVE","PROVISIONAL","QUARANTINED","WITHDRAWN"]

def library_rows(registry_root: str, *, template: str | None) -> tuple[LibraryRow, ...]: ...
def rejected_rows(template: str | None, gate: str | None) -> tuple[RejectionRow, ...]: ...
```

**Three things in that dataclass are repairs, and each closes a way this surface could have printed a
confident wrong number. None of them is a display preference.**

**(a) Two kill rates, side by side, and the gap between them is the number a reviewer wants.** G2's
registry bar is `K/O ≥ 0.80` *"on the fault classes the predicate claims to cover"* — and the claim is
selected **after the campaign has run**, from the witnesses of mutants that already died. A `sum_identity`
predicate structurally blind to enum substitution, homoglyphs, carry desync and vocabulary gaps scores
`K/O = 0.21` overall, has three F01/F03 witnesses stamped on it, and is admitted `BLOCKING` at `0.97`.
`claims_fault_classes` therefore becomes a **required, non-empty envelope field inside `code_sha256`**
(`04`'s repair), and this surface's obligation is to make the selection visible: **`kr_claimed` and
`kr_all_classes` render in the same row, always both, and a row that renders one without the other does not
render at all.** A wide gap is not a failure — it is a predicate honestly declaring a narrow scope — but it
must be legible, because the alternative is a `0.97` whose denominator the predicate chose for itself.

**(b) Six integers, not two, and `I` is the new one.** `classify(clean, mutant)` marks a mutant
`UNOBSERVABLE` when the two recalculated grids are identical — and **a cell the evaluator could not compute
is identical in both grids by construction**, so every mutant whose only propagation path runs through an
unimplemented function, a cycle or an excluded engine-disagreement cell is silently removed from `O`.
Because `O = G − U`, each such exclusion **raises `K/O`**: the measurement error is correlated with the
quantity being measured, in the direction that flatters us. The three-way classification
(`OBSERVABLE · UNOBSERVABLE · INDETERMINATE_OBSERVABILITY`) is `04`'s repair; **the surface's half is that
`I` is published beside `U/G` every time either renders, with the offending cells named.** `U/G` is then
readable as what it is — a property of *our apparatus* — rather than as a property of the fault model.

**(c) `instrument_label`, and it is not cosmetic.** Every kill rate in this programme rests on the sentence
*"our evaluator reproduces the regulator's own values"*, which G-EVAL certifies. If G-EVAL's arm-2
expectation file was written by the evaluator's own author, that sentence is a self-check, `ci/GATES.md`
records **`PASSED — NOT INDEPENDENT`**, and `plan/01-validation-methodology.md` §1.4 requires the literal
string **`SAME-AUTHOR — a weaker instrument`** on *every surface that quotes a kill rate*. This field is
where that string lives, `test_library__kill_rate_carries_its_instrument_label` asserts a `KillRateCell`
cannot render with `instrument_label` unread, and the value is **read from `ci/GATES.md`, never from a
constant** — the same rule as `admission_state`.

```python
# src/cdfc/surface/funnel.py

FUNNEL_STAGES: Final[tuple[str, ...]] = (
    "generated", "G0.scope", "G1.binds", "G3.proof", "G2.kill", "G3.empirical", "G4.ffr",
)   # THE ORDER IS THE GATE ORDER. It is not a display preference.

def attrition_funnel(obligation_id: str) -> tuple[FunnelStage, ...]: ...
    # FunnelStage(name, entered: int, skipped: int, survived: int,
    #             rejections: tuple[RejectionRow, ...])
    # THREE integers per stage, and `entered == skipped + survived + len(rejections)` is asserted.
    # A SKIPPED candidate is one the gate DOES NOT APPLY TO. It is rendered in its own column and
    # is NEVER counted as a survivor.
```

**`skipped` is new, and without it the funnel's first stage is either a constant or a lie.** G0 is a
verbatim-quote guard: its six closed rejection reasons all presuppose a clause. The 280 harvested FME
candidates are derived from the workbook's own formulas and data validations — they cite no regulation and
carry `clause: None`. **No document said what G0 does with them**, and both branches are bad: if G0 rejects
them, all 280 die at stage one, ALR's five `≥ −1e17` bounds never reach G3, and **D-REJECT — this plan's
flagship demonstration that the gate is not decorative — becomes unreachable**; if G0 silently skips them,
stage one reads `280 → 280`, the funnel's first column is a constant, and *a gate that does not apply to
the population it is run over is reporting a pass it did not compute.* Both branches pass their own phase's
tests in isolation, which is why nobody would have found it before P7.

`03`/`04` own the disposition ruling. **This surface owns making it countable**, and the obligations here
are three:

1. **Three integers at every stage, `entered / skipped / survived`**, never two.
   `tests/unit/test_funnel.py::test_funnel__stage_arithmetic_closes` asserts
   `entered == skipped + survived + len(rejections)` for every stage, so a skip cannot be laundered into a
   survival by omission.
2. **A stage whose `skipped` equals its `entered` renders as `NOT APPLICABLE — 0 evaluated`**, not as a
   full-width survival bar. `test_funnel__a_wholly_skipped_stage_does_not_render_as_a_pass`.
3. **THE OBLIGATION COVERAGE PAIR is published as a subordinate number — TWO numbers, never one**
   (arbitration **C2**) — on `S13.attrition-funnel`, appended to `reports/validation-ledger.jsonl` with
   `measures: CENSUS`:
   **`predicates_with_a_STATUTE_obligation / 280`, today `0 / 280`**, and
   **`predicates_with_a_TEMPLATE_obligation / 280`, today `280 / 280`.**
   They render **together or not at all** — `test_surface__both_obligation_counts_render_or_neither_does`,
   raising `UnpairedObligationCount` — and the surface **never adds them together**. The sentence
   ***no harvested predicate yet implements a statutory clause*** renders verbatim beside them.
   Publishing a zero is the honest case and must not be special-cased into an empty state — the same rule
   this phase already applies to `EDR_1`'s 0%. *This entry previously published the single, unqualified
   `harvested_predicates_with_an_obligation / 280`, "and today reads `0 / 280`" — which under the arbitrated
   mechanism is **wrong by 280**. The pair is the repair, and the qualifier is not optional: an unqualified
   obligation count is the defect, in either direction.*

```python
# src/cdfc/surface/history.py

def history_points(template_sha256: str) -> tuple[HistoryPoint, ...]: ...
    # HistoryPoint(at, settled, field_surface, admission, cause: str | None)
    # `cause` is REQUIRED and non-empty whenever settled decreased from the previous point.
    # Raises UnlabelledStepDown otherwise. A step-down with no cause does not render.
```

#### The gate that governs digits, not existence

`labels.render_ffr` was written in **B1** and has no code path that formats a number for a `SELF-AUTHORED`
corpus, an absent corpus, **or a corpus whose generator is not independent of the predicate**. B4 adds
surfaces that *display* an `FfrCell`; it does not add the ability to print one. **The gate cannot be
defeated by adding a surface, because the surface calls the function and the function cannot print.**

**G-CORPUS has three outcomes, not two, and this surface renders all three distinctly.** The gate as
originally stated required `n ≥ 30` with `corpus_provenance` in a six-member set — which
`synthesise(..., n=30)` satisfies in one command, from a corpus the product generated about itself. *The
gate whose entire purpose is to stop a self-authored FFR from shipping was satisfiable without a single
filing anyone outside this repository touched*, and its PASS branch says the FFR-bearing surfaces ship.
`00`/`04` own the threshold split; this document owns the fact that **the middle outcome must be a visible
state rather than an undetected pass**:

| Outcome | What licensed it | What B4 renders |
|---|---|---|
| **PASS** | `n_blind_or_real ≥ 30` | digits, with `corpus_id`, `corpus_provenance`, `n` and a Wilson interval, per SG2 |
| **RESTRICTED** | only `TEMPLATE-COMPUTED` / `REGISTER-DERIVED` reached `n ≥ 30` | digits **only** for the predicate classes those corpora license — membership, bounds, dates, `conditional_required`; every arithmetic row renders `uninformative`; the column header carries the literal string **`G-CORPUS: RESTRICTED`** and names which classes are licensed |
| **FAIL** | neither | every cell renders `uninformative`; the header carries the corpus-provenance census (`SELF-AUTHORED: n · BLIND-FILLED: 0 · …`); no digit appears anywhere |

`tests/unit/test_library.py::test_library__three_corpus_outcomes_render_distinctly` asserts the three
produce different DOM text and that only the first two contain a digit — the same `absent ≠ empty ≠ zero`
discipline the Unchecked panel applies to `None` versus `()`. **A restricted pass rendered as a pass is
the whole failure this gate exists to prevent, one level up.**

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_library.py::test_library__kr_renders_six_integers_and_the_vector` | a `KillRateCell` rendered without **all six** of `G · U · I · O · R · K`, without `U/G`, or without the per-fault-class vector raises. Criterion A9, NC-Q05b's surface twin, **and `I` beside `U/G` every time either renders** |
| unit | `tests/unit/test_library.py::test_library__indeterminate_cells_are_named` | `I > 0` with an empty `indeterminate_cells` raises. An integer without the cells behind it is an apology, not a measurement |
| unit | `tests/unit/test_library.py::test_library__both_kill_rates_render_or_neither_does` | a row carrying `kr_claimed` and not `kr_all_classes` (or the reverse) raises `UnpairedKillRate`. **The gap between them is the number a reviewer wants** |
| unit | `tests/unit/test_library.py::test_library__claims_are_non_empty_and_content_addressed` | `claims_fault_classes` is non-empty and its hash participates in the row's `code_sha256`; a row whose claim set is not inside the envelope digest does not render |
| unit | `tests/unit/test_library.py::test_library__kill_rate_carries_its_instrument_label` | `instrument_label` is read from `ci/GATES.md`, never from a constant; when G-EVAL is `PASSED — NOT INDEPENDENT`, the literal `SAME-AUTHOR — a weaker instrument` renders **in the same block as** the rate, asserted by ancestor distance ≤ 2, the same structural test as NC-A05 |
| unit | `tests/unit/test_library.py::test_library__three_corpus_outcomes_render_distinctly` | `PASS` / `RESTRICTED` / `FAIL` produce different DOM text; only the first two contain a digit |
| unit | `tests/unit/test_library.py::test_library__flag_everything_column_is_present_on_every_row` | no row may omit it. Without it a kill rate is reach, not quality |
| unit | `tests/unit/test_funnel.py::test_funnel__stages_are_the_gate_order` | `FUNNEL_STAGES` equals `qualify`'s pipeline order, read from the pipeline, not from a literal |
| unit | `tests/unit/test_funnel.py::test_funnel__stage_arithmetic_closes` | `entered == skipped + survived + len(rejections)` at **every** stage. A skip cannot be laundered into a survival by omission |
| unit | `tests/unit/test_funnel.py::test_funnel__a_wholly_skipped_stage_does_not_render_as_a_pass` | a stage with `skipped == entered` renders `NOT APPLICABLE — 0 evaluated`, not a full-width bar. **G0 over the 280 clause-less harvested candidates is the live instance** |
| unit | `tests/unit/test_funnel.py::test_funnel__every_rejection_carries_its_measured_number` | a rejection row with `measured_json` empty does not render |
| unit | `tests/unit/test_history.py::test_history__step_down_without_a_cause_raises` | `UnlabelledStepDown` |
| unit | `tests/unit/test_history.py::test_history__can_step_down` | a sequence that decreases renders, with its cause label. **The step-downs are the most credible thing on the chart** |
| golden | `tests/golden/test_golden__library__alr.py::test_golden__alr_five_vacuous_bounds_appear_in_rejected` | `ALR_V2_3` (`a414d8d3…`): the five `≥ −1e17` bounds over **1,428 cells** appear in the **Rejected** tab with gate `G3`, their measured number, and the cells they would have covered. This is the gate's one demonstrated rejection and the library must show it |
| golden | `tests/golden/test_golden__library__fme.py::test_golden__fme_real_bounds_appear_in_admitted` | FME: **19 of its 24 bounds are a real `≥ 0`** and appear in the admitted tab. The admission-side twin, without which the surface is indistinguishable from a reject-everything display |
| golden | `tests/golden/test_golden__library__fme.py::test_golden__library_states_its_own_evidence_size` | the library renders the caution verbatim: the gate has exactly one demonstrated rejection, on one workbook, in one predicate class, and whether it rejects anything on FME is **unmeasured** |
| perf | `tests/perf/test_perf__PERF-LIB` | 280 rows render in **under 200 ms** with no virtualisation library; ≤ 515 rows is the ceiling. New budget `PERF-LIB`, fail above 400 ms |

**Negative controls.** *Existing and load-bearing here:* **NC-Q08** (all five tests: `uninformative` with no
digit; API `null`; no FFR without provenance/`n`/interval; `n` is filings not cells; a synthetic rate
carries the word `synthetic`), **NC-Q09** (severity keyed on the Wilson **upper** bound — `(0,4) → 0.490 →
NOT ADMITTED`; `(2,96) → [0.006, 0.074] → ADVISORY`; `(0,185) → BLOCKING`; and `test_nc__Q09b` asserting
that on the current corpus the BLOCKING count is **0** and the report says so), **NC-Q03** (a degenerate
predicate is admitted), **NC-Q05** (the kill rate over the wrong denominator), **NC-A05** (the headline
without the admission state). *New:*

```yaml
- id: NC-A15
  component: surface
  break: "the settled-fraction chart cannot step down — a decrease is dropped, smoothed, or clamped"
  measured_instance: null
  injector: history_monotone
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_history.py::test_history__can_step_down
      flips: true
    - path: tests/unit/test_history.py::test_history__step_down_without_a_cause_raises
      flips: true
    - path: tests/e2e/test_e2e__churn.py::test_e2e__template_bump_lowers_the_chart      # P15-B2
      flips: true
    - path: tests/unit/test_history.py::test_history__monotone_series_renders_unchanged
      flips: false
  positive_control: tests/unit/test_history.py::test_history__monotone_series_renders_unchanged
  status: ACTIVE

- id: NC-A31
  component: surface
  break: >
    a kill rate renders with a denominator the predicate chose for itself, or without the
    indeterminate-observability count, or without its instrument-independence label
  measured_instance: "M1 and M2 arriving at the surface that publishes them: the registry bar's claimed-class denominator, and U inflated by cells the evaluator cannot compute"
  injector: kr_renders_claimed_only
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_library.py::test_library__both_kill_rates_render_or_neither_does
      flips: true
    - path: tests/unit/test_library.py::test_library__kr_renders_six_integers_and_the_vector
      flips: true
    - path: tests/unit/test_library.py::test_library__kill_rate_carries_its_instrument_label
      flips: true
    - path: tests/unit/test_library.py::test_library__flag_everything_column_is_present_on_every_row
      flips: false
  positive_control: tests/golden/test_golden__library__fme.py::test_golden__fme_real_bounds_appear_in_admitted
  status: ACTIVE

- id: NC-A32
  component: surface
  break: "a candidate a gate did not evaluate is rendered as a survivor, so a stage that computed nothing reports a pass"
  measured_instance: "G0 over the 280 harvested FME candidates, every one of which carries clause: None"
  injector: funnel_skipped_counts_as_survived
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_funnel.py::test_funnel__stage_arithmetic_closes
      flips: true
    - path: tests/unit/test_funnel.py::test_funnel__a_wholly_skipped_stage_does_not_render_as_a_pass
      flips: true
    - path: tests/unit/test_funnel.py::test_funnel__stages_are_the_gate_order
      flips: false
  positive_control: tests/golden/test_golden__library__alr.py::test_golden__alr_five_vacuous_bounds_appear_in_rejected
  status: ACTIVE
```

`injectors/history_monotone.py` applies `running_max` to the series. It must turn all three `flips: true`
guards red — including the P15-B2 e2e test, which is why NC-A15's guard list spans two phases and is
recorded as a **cross-phase entry** in the catalogue.
`injectors/kr_renders_claimed_only.py` renders `kr_claimed` alone, drops `I` from the census, and returns
`instrument_label=None` — three defects in one injector because they are three faces of one belief, *that a
kill rate is a property of the predicate rather than of the apparatus that measured it*.
`injectors/funnel_skipped_counts_as_survived.py` folds `skipped` into `survived`, which is how a `280 → 280`
first row gets printed and read as attrition.

**The admission-side twins matter more than usual for these two.** NC-A31's positive control is FME's 19
real `≥ 0` bounds appearing in the admitted tab, and NC-A32's is ALR's five vacuous bounds appearing in the
rejected tab: without them, a library that renders nothing and a funnel that survives nothing both score
perfectly on the negative controls alone.

---

## P14 · The four surface gates, and how they run in CI

| Gate | What it proves | Where it runs | Blocking |
|---|---|---|---|
| **SG1 — copy** | No banned glyph or phrase reaches a surface, **in source and in the rendered DOM**. `ci/no-green-tick.sh` (source; extended to read `BANNED_GLYPHS`/`BANNED_PHRASES` from `labels.py` so the gate and the renderer cannot disagree) plus `ci/surface_audit.py --gate=sg1`, which reads `page.inner_text("body")` **after JS runs** and every `getComputedStyle(el, "::before"/"::after").content` value | stage 2 (source) + stage 12 (DOM) | yes |
| **SG2 — provenance** | No FFR renders without `corpus_id`, `corpus_provenance`, `n` and a Wilson interval; `SELF-AUTHORED` renders `uninformative` and no digit | stage 3 + stage 8 | yes |
| **SG3 — admission** | No settled count renders without the admission state **in the same block** — `PRE-GATE` and the count share an ancestor within 2 levels, not merely the same page | stage 8 (NC-A05) + stage 12 | yes |
| **SG4 — weight and ink** | Rendered and measured, never read off the stylesheet: the two hero counts resolve to the **same computed `font-size`, `font-weight`, `color`**; the unchecked band segment is **hatched, not muted** (`background-image` is a repeating pattern, `opacity == 1`, fill colour equals the settled segment's ink); **no computed colour anywhere falls in `GREEN_HUE_BAND` with saturation > 0.15 and lightness in [0.2, 0.8]**; the band's terminal segments have non-zero width | stage 12 | yes |

**CI wiring.** `make surface-audit` runs inside **stage 12 (end-to-end, offline)** because it needs a
rendered artifact from a real run and stage 12 is the only stage where one exists. Stage 12's wall clock
moves **2 min → 3 min**, recorded in `ci/GATES.md`. The PR budget stays under 12 minutes.

**The gate's own scan-set hazard, closed — and there were three scan sets, which was the hazard.**
`plan/01-validation-methodology.md` §5.4 gave `ci/no-green-tick.sh` the roots `src/ templates/ locales/
static/`; P0-B1 creates none of the last three, and `02` §1 R5 makes a **missing scan root a non-zero
exit** — so the gate fails from the first commit and gets "fixed" by narrowing to `src/`, which is NC-D01's
mechanism applied to the honesty gate on day one. This document then derived a *third* set from
`render.TEMPLATE_DIR`, which does not exist until P14. **Three lists of directories, two of which are
wrong, guarding the commitment the whole product rests on.**

**Ruling: one source of truth, `cdfc.surface.labels.SCAN_ROOTS`.** It ships as a stub at **P0** containing
`("src/cdfc",)`; **P14-B1 extends it**; and `ci/no-green-tick.sh`, SG1's source arm and SG4's rendered arm
all read it. `tests/negative/test_nc_ci.py::test_nc__CI01c_scan_root_list_is_not_a_literal` asserts the
script contains no directory literal, and `SCAN_ROOTS` is one of R-DENOM-1's append-only registries
(`01` §5.1), so it cannot shrink without a dated argument in `ci/GATES.md`. **The narrowing from four names
to the real tree is recorded there with its reason** — a scan set that shrinks silently is the defect; a
scan set that shrinks with a diff is housekeeping.

`test_nc__A02b` (existing) proves the template scan set covers every template `render.py` references;
**NC-A10** proves the *surface registry* covers every module that renders user-visible text; **NC-A30**
(new) proves the registry cannot be made smaller to fit the gate. They are the same defect at three levels,
and all three are needed.

---

## P14 · The measurement this phase produces

> **`surfaces_passing_all_four_gates / len(SURFACES)`** — two integers, printed together, never as a
> percentage. Denominator: the surface registry in `src/cdfc/surface/labels.py`. Warrant **MEASURED**.

Published to `docs/measurements/P14-surface-audit.md` and appended to `reports/validation-ledger.jsonl`:

```json
{"row_id":"P14.4-surfaces.passing_all_four_gates",
 "phase":"P14","build":"P14.4","metric":"surfaces.passing_all_four_gates",
 "numerator":"<written by the run>","denominator":"<written by the run>",
 "denominator_source":"len(cdfc.surface.labels.SURFACES) — the machine-maintained APPEND-ONLY surface registry; its cardinality per commit is in docs/measurements/P14-surface-audit.md",
 "warrant":"MEASURED","measures":"CENSUS","positive_control_count":null,
 "produced_by":"ci/surface_audit.py",
 "command":"make surface-audit",
 "caveat":"licenses one sentence: k of n enumerated rendering surfaces passed SG1-SG4 on this commit. It says nothing about a surface nobody registered — see NC-A10 and NC-N09 — and nothing about whether any rendered number is correct.",
 "date":"<written by the run>"}
```

**The denominator has a floor, and that is this phase's own repair of M1.** `len(SURFACES)` is written by
the same build the gate scores, so *a surface that cannot pass SG1–SG4 could be removed to make the gate
green* — the numerator choosing its own denominator, arriving at the gate built to audit honesty.
`docs/measurements/P14-surface-audit.md` therefore carries `|SURFACES|` and `|REQUIRED_NUMBERS|` **as time
series, one row per commit**, and `tests/surface/test_registry.py::test_surface__gate_floor_is_the_logged_cardinality`
asserts the current denominator is **≥ the maximum ever logged**, unless a retirement row with a dated
argument accounts for the difference exactly. NC-A30 is its negative control. **A registry that shrinks the
day before a gate is read is now visible in the artifact the gate is read from.**

**The two count fields are shown as placeholders on purpose, and `0` was the wrong placeholder.** This is
the row's *shape*, not a reading; `ci/surface_audit.py` writes the integers. A template carrying `0/0` is a
well-formed statement that nothing passed out of nothing, and it would be copied into a document by someone
who did not run the audit. `tests/test_validation_ledger.py` already requires `numerator` and `denominator`
to be integers, so the placeholder form cannot be committed as a real row — it fails schema validation,
which is the correct behaviour and is why this shape is safe to print in a plan and unsafe to print in
`reports/`.

**Three subordinate numbers this phase also produces, each new:**

1. **`len(REQUIRED_NUMBERS)` and `rendered / required`** — the denominator of the claim *"the report renders
   every number"*, which has never had one.
2. **`|SURFACES|` by `renders` class** — how many surfaces can display a settled count, an FFR, a verdict
   name. This is the blast radius of any future copy change, and nobody has it.
3. **`PERF-SIZE`** — the byte size of the self-contained report. The emailability claim currently rests on
   an adjective.

**The registry at first ship** (indicative; the count is whatever `len(SURFACES)` returns and the gate
prints both integers — this list is not a measured count and must not be quoted as one):

`S01.drop` · `S02.report-hero` · `S03.report-band` · `S04.report-failure-item` · `S05.report-strapline` ·
`S06.unchecked-panel` · `S07.unchecked-remedy` · `S08.residue-exhibit` · `S09.report-invalid` ·
`S10.report-openitems` · `S11.library-admitted` · `S12.library-rejected` · `S13.attrition-funnel` ·
`S14.settled-history` · `S15.api-runs` · `S16.api-checks` · `S17.api-cells` · `S18.api-predicates` ·
`S19.api-rejections` · `S20.api-templates` · `S21.api-settled-fraction-history` · `S22.openapi-doc` ·
`S23.cli-run-stdout` · `S24.readme` — plus, **registered by P11 and audited by these gates**,
`S25.oscal-projection` · `S26.rocrate-projection` · `S27.attestation-json`.

**Cross-document obligation:** `plan/05-phases-probes-attestation.md` specifies P11's three surfaces; this
document specifies the registry and the gates they must pass. Neither restates the other's numbers.

---

## P14 · Exit gate

A boolean, evaluable by someone who did not do the work, by reading `reports/` after a green CI run:

1. `surfaces_passing_all_four_gates == len(SURFACES)`, both integers printed in
   `docs/measurements/P14-surface-audit.md` — **and `len(SURFACES)` is ≥ every value in that file's own
   `|SURFACES|` time series**, or the shortfall is accounted for exactly by retirement rows carrying dated
   arguments (`test_surface__gate_floor_is_the_logged_cardinality`). **A gate whose denominator this build
   writes is not passed by shrinking the denominator**, and until this criterion had a floor it could be.
   The same floor applies to criterion 2's `len(REQUIRED_NUMBERS)`.
2. `test_e2e__A10_file_url_offline_renders_every_number` green: **zero network requests attempted**, and
   `rendered == len(REQUIRED_NUMBERS)`.
3. `PERF-LIB` green: 280 rows under 200 ms with no virtualisation library. `PERF-SIZE` under 2 MB.
4. Every new catalogue entry (**NC-A06 – NC-A15, NC-A30 – NC-A32, NC-CI10 – NC-CI11**) has been **observed
   red under its injector**, and `make nc-sweep` reports **all four integers**: `entries_caught ==
   entries_active` **and `guards_flipped == guards_expected_to_flip`** — the second pair is the one this
   criterion is really about, because an entry is `caught` on one red guard while its other guards may
   never have been exercised. Evidence for DoD line C4 is the sweep report's rows at the merge commit
   (`assertion_text` non-empty for every flipped guard), **not a pasted line**. The stage-2 greps have their
   planted controls green *and observed red*: `test_nc__CI10_locale_format_is_caught` and
   `test_nc__CI11_imported_prior_is_caught` (§0.4(d)). `ci/GATES.md` records the stage-2 and stage-12 clock
   movements against `plan/01-validation-methodology.md` §5.3's budget table
   (`test_ci__stage_clocks_match_gates_md` green), and the registry deltas of §0.4(a)–(c) are entered in
   `plan/01-validation-methodology.md` §0.4/§3.5 and in `docs/MUTATION-THRESHOLDS.md`. **An addition that is
   not entered is an unscanned surface.** `ci/catalogue-ids.sh` is green: every id this document defines
   resolves to a row in `01` §2's canonical registry (`test_nc_meta__ids_are_defined_in_the_registry`) and is not a RETIRED id (`test_nc_meta__no_dangling_reference`).
5. `surface/labels.py`, `surface/admission.py`, **`surface/library.py` and `surface/funnel.py`** meet the
   Tier-V floor `K/V ≥ 0.90`, reported with the equivalent-mutant caveat in the §3.5 form (§0.4(c)).
6. The verdict enum contains `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` and **no shorter synonym**
   (`test_nc__A02d`), and the report's title string is a function of the verdict state.
7. `K` and `T` render the literal string `PLACEHOLDER` on every surface and in every example
   (`tests/unit/test_render.py::test_render__pervasiveness_placeholders_are_literal`). This is spec §III.7
   C22 and it **does not block the phase**.
8. If E1 or E1b is unanswered, `S10.report-openitems` renders the standing absence with its age
   (`test_openitems__unanswered_renders_its_age`). **A dropped question is worse than either answer.**
9. **No settled count renders without its denominator's generating rule in the same block**
   (`test_labels__settled_count_never_renders_without_its_denominator_rule`), and **no kill rate renders
   without its six-integer census, its two denominators and its instrument label**
   (`test_library__kr_renders_six_integers_and_the_vector`,
   `test_library__both_kill_rates_render_or_neither_does`,
   `test_library__kill_rate_carries_its_instrument_label`). The funnel's stage arithmetic closes and no
   wholly-skipped stage renders as a pass (`test_funnel__stage_arithmetic_closes`,
   `test_funnel__a_wholly_skipped_stage_does_not_render_as_a_pass`), and
   **both** obligation-coverage numbers are published together (C2) —
   `predicates_with_a_STATUTE_obligation / 280 = 0 / 280` **and**
   `predicates_with_a_TEMPLATE_obligation / 280 = 280 / 280`,
   `test_surface__both_obligation_counts_render_or_neither_does` green. **`0 / 280` is the honest reading
   today for the STATUTE count and it must render as one — beside the TEMPLATE count, never instead of
   it.**
10. **Every integer literal this phase added to `tests/golden/` traces to `plan/01-validation-methodology.md`
    §0.3 or to a `reports/validation-ledger.jsonl` row**, and `ci/golden-literals-are-traceable.sh` is
    green (rule R-GOLD-3). `2,373` and `1,374` are **not** pinned as literals; they live in
    `docs/HARVEST-DELTA.md` and the hero golden asserts them relationally. Every ledger row this phase
    writes carries `measures ∈ {REACH, DISCRIMINATION, CENSUS}` (§0.5), and every `REACH` row renders with
    its admission state and no verb of verification.

## P14 · What it kills if it fails

**A surface that cannot be made to obey the gates is removed, not excepted.** An exception in the honesty
gate is how the gate dies — the same argument that fixed the package name in `plan/00-decomposition.md` §1.

| Failure | Consequence, honestly |
|---|---|
| **SG4 cannot be run reproducibly** (the browser cannot be pinned across runner images) | Fall back to `--engine=cssom` and **carry `WEAKER INSTRUMENT` on the gate output forever**. The equal-weight claim becomes a claim about the stylesheet, not about the pixels, and the surfaces say so |
| **The report cannot be made self-contained** (e.g. a needed asset cannot be inlined within `PERF-SIZE`) | The attestation loses its subject and the product loses its emailable artifact. **Fallback: a signed JSON with a printable projection** — weaker, still shippable, and labelled weaker on the surface. This is the fallback `plan/00-decomposition.md` P14 already names |
| **A number in `REQUIRED_NUMBERS` cannot be rendered on any surface** | It is **retired**, never deleted — the row stays with `retired_on` and `retired_because`, an appended entry in `docs/measurements/P14-surface-audit.md` gives the id and the argument, and the cardinality time series shows the step. `test_surface__registry_is_append_only` enforces it. **The denominator may shrink; it may not shrink silently, and it may never shrink below the logged floor without an argument that accounts for the difference exactly** |
| **A surface cannot be made to pass SG1–SG4** | Same rule, same test, and this is the one that would have been taken quietly: the cheapest way to pass criterion 1 is to delete the failing row. **NC-A30 is its negative control**, and a retired surface **is still scanned by SG1** — we may give up auditing a surface's weight and ink; we do not give up prohibiting a green tick on it |
| **`len(SURFACES)` cannot be made complete** (a surface renders outside the registry and cannot be brought in) | The gate's denominator is self-referential and this document must say what that costs: see **NC-N09** below. The audit becomes *"k of the n surfaces we knew about"*, and that sentence renders on the audit page. **NC-N09 is about incompleteness and NC-A30 is about shrinkage; they are different failures and only the second is mechanisable** |
| **The whole build fails** | Nothing upstream is affected. P0–P13 are unchanged; the product loses its screens and keeps its `run.jsonl`, its attestation and its CLI. That is a research instrument with no product surface — smaller, honest, still publishable |

---

# P15 — TRANSFER (COST ARM), VERSION CHURN, OPERATIONS, DEPLOYMENT

**Effort: 10 engineer-days** · B1 3 · B2 3 · B3 2 · B4 2
*Plus, and never added to the engineer's total:* **4–6 hours of a second person's stopwatch time** in B1
(the transfer/authoring sessions and the inter-operator reliability re-run).

## P15 · What it settles

**Whether this is a product or a paper about one workbook — and whether the settled fraction actually falls
when the world moves.**

Three sub-questions:

1. **Transfer cost.** Is carrying a predicate to a second prescribed workbook materially cheaper than
   authoring one from scratch? Pre-registered threshold: **≤ 0.5×** the median from-scratch authoring time,
   over **≥ 10** predicates.
2. **Churn.** When the template hash bumps, do affected predicates move to `PROVISIONAL`, keep running,
   hide their numbers, leave the settled numerator — and does the chart **step down**?
3. **Operations.** Can a published report be re-derived, and can the register snapshot policy be stated
   with a staleness bound — with IFSCA's terms of use **read** before any scheduled polling?

## P15 · Entry criteria

| Build | Requires | Why |
|---|---|---|
| **B1** | **P7** (re-qualification machinery: G0–G3, the registry, admission) and **P8** (cost is measured *over qualification*, so G4 must exist even if its answer is "nothing is admissible"). **P4-B4** for the mechanical arm's output | Measuring "human minutes to carry a predicate" before the carrying machinery exists measures typing, not transfer |
| **B1** | **`cdfc.measure.paths.P4_HARVEST_DISTRIBUTION` published** — i.e. `docs/measurements/P4-harvest-distribution.md` | The mechanical arm (E4 arm 1) belongs to P4-B4 per conflict 3 of the decomposition. B1 measures the *cost* arm and must not restate P4's numbers. **DECIDED: one file, one name.** This criterion previously named `docs/measurements/P4-transfer-mechanical.md`, which `03` P4-B4 does not create — it creates `P4-harvest-distribution.md`, and that same file now also carries the harvest/`2,373` reconciliation (R-GOLD-3). *The alternative it beat:* two files, one per arm — rejected because the mechanical transfer arm **is** a cut of the harvest distribution, and a second file would have to restate the first's denominator. **The name is referenced through a module constant, never a literal**, per `06` §0.9's rule, and `tests/unit/test_paths.py::test_paths__every_entry_criterion_document_exists` walks every entry-criteria table in `plan/` and asserts each named path resolves — an entry criterion naming a file no build creates is a phase that cannot start and nobody finds out until it does |
| **B2** | **P7** (the `qualification` table, `qualified_against`, liveness witnesses) and **P14-B4** (the history chart, which is where a step-down becomes visible) | A settled fraction that falls with nothing rendering the fall is not a system property |
| **B3** | **P4** (the host-function registry, `reg_resolves` tri-state) | The staleness bound degrades a host function; the host function must exist |
| **B4** | **P0** (the container, the Makefile) for the deployment sub-gate; **P11-B2** (`verify`) for the reproducibility sub-gate — see §0.3 | Split acceptance, with the deferral recorded rather than passed |

---

### BUILD P15-B1 — THE TRANSFER MEASUREMENT, COST ARM (E4 ARM 2) · 3 days

**What it produces.** The number that decides *product or paper*: **human minutes per transferred predicate
against the from-scratch authoring baseline**, over ≥ 10 predicates on a second prescribed workbook — plus
the **per-template settled fraction table for all nine, including the zeroes and the `null`s, never
averaged.**

#### Files created

```
src/cdfc/transfer/__init__.py
src/cdfc/transfer/rekey.py             mechanical key re-resolution across templates
src/cdfc/transfer/session.py           the stopwatch: a timed, pre-registered, recorded work session
src/cdfc/transfer/report.py            the per-template settled-fraction table and its never-average guard
src/cdfc/transfer/d17.py               the COUNTIF-defect recurrence probe (see below)
experiments/E4/PREREGISTRATION.md      committed and hashed BEFORE the first session
reports/transfer/sessions.jsonl        append-only, one row per timed session
docs/measurements/P15-transfer-cost.md
```

#### Public interface

```python
# src/cdfc/transfer/rekey.py
def rekey(pred: Predicate, src: TemplateSchema, dst: TemplateSchema) -> RekeyResult: ...
    # RekeyResult(state: Literal["RESOLVED","AMBIGUOUS","UNRESOLVED"],
    #             mapping: dict[str, str], candidates: dict[str, tuple[str, ...]], notes: str)
    # AMBIGUOUS and UNRESOLVED are the human's work. RESOLVED is free.
    # Keys are LABEL-anchored (sheet_name, merged_header_path, row_label) + row ordinal,
    # never coordinate-anchored: a version bump is a re-resolution, not a rewrite.

# src/cdfc/transfer/session.py
def start_session(kind: Literal["CARRY","AUTHOR"], subject_id: str, operator: str) -> Session: ...
def end_session(s: Session, *, outcome: Literal["ADMITTED","REJECTED","ABANDONED"],
                rejecting_gate: str | None) -> SessionRecord: ...
    # SessionRecord(kind, subject_id, operator, started_at, ended_at, minutes,
    #               interruptions_minutes, outcome, rejecting_gate, arm_order_index)
    # `minutes` is wall clock MINUS declared interruptions. Interruptions are declared
    # at the time, not reconstructed afterwards.

# src/cdfc/transfer/report.py
def per_template_settled(templates: Sequence[str]) -> tuple[TemplateSettledRow, ...]: ...
def render_table(rows) -> str: ...
    # Raises AverageAttempted if any caller reduces the rows to a single figure.
    # The settled fraction is a PER-TEMPLATE property. There is no mean.
```

#### The measurement protocol, pre-registered before the stopwatch starts

This is the one measurement in the plan whose instrument is a human, and it is defeated by three things:
learning, selection and reconstruction. All three are handled *ex ante*, in
`experiments/E4/PREREGISTRATION.md`, committed and hashed **before the first session**:

- **The predicate draw.** The ≥ 10 predicates are drawn from the FME admitted (or, at `k=0` for G-CORPUS,
  the FME *harvested*) set by a PRNG seeded from the pre-registration file, ordered by `predicate_id`,
  without replacement. **Not chosen by the engineer after looking at the target workbook.**
- **The target workbook.** `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries`
  (`82dd291f…`, 18 sheets, 17 protected, 33 formula cells, 142 validations, field surface **2,255**) is the
  second workbook. *Reason it beats the alternatives:* it is the only other workbook in the corpus with a
  protection mask **and** a substantial validation population, so both the membership class and the
  arithmetic class have somewhere to land. `ALR_V2_3` is the runner-up and is reserved for the
  degeneracy-side control, since it is the workbook whose five `≥ −1e17` bounds the gate already rejects.
- **Counterbalancing, because learning is the dominant confound.** Sessions run in **ABBA** order —
  `CARRY, AUTHOR, AUTHOR, CARRY, …` — with the assignment fixed in the pre-registration and
  `arm_order_index` recorded on every row. Comparing arm medians without counterbalancing measures how much
  the operator learned about the CMI workbook, not how much the method transferred.
- **The comparison statistic.** Median minutes per **admitted-or-rejected** predicate (an abandoned session
  is recorded and excluded, with its count published), reported as `CARRY_median / AUTHOR_median` with both
  medians, both `n`s, and the full per-session table. **No mean, no percentage without both integers.**
- **The commitment to publish either way**, and the arguments that will not be accepted as grounds for
  changing the threshold afterwards — hashed in, per the same discipline as `experiments/E6`.

#### A cheap sub-measurement folded in, because it is twenty minutes and it converts a finding into a pattern

`src/cdfc/transfer/d17.py::countif_vocabulary_gap(template) -> tuple[Gap, ...]` — for every `COUNTIF`/
`COUNTIFS` in a template, resolve its criteria against the controlled vocabulary the template's own
validations wire to that column, and report the vocabulary members **no criterion matches**. On FME this
reproduces the `D17` defect: *"Total No. of Schemes of the FME authorised by IFSCA"* is computed with three
COUNTIFs that between them miss **two of the nine** scheme types the template's own validation permits.
Spec §III.7 lists *"whether the `D17` COUNTIF defect recurs in the other prescribed workbooks"* as an open
measurement; this build closes it. `docs/measurements/P15-countif-gaps.md`, denominator 9 workbooks.

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_rekey.py::test_rekey__label_anchored_survives_row_insertion` | over `fixtures/synthetic/row-inserted__portfolio-r7.xlsx`: every key resolves correctly **or** returns `UNRESOLVED`; **zero** keys resolve to a different label pair. Reuses NC-D04's statement at the transfer boundary |
| unit | `tests/unit/test_rekey.py::test_rekey__ambiguous_is_not_a_guess` | `AMBIGUOUS` returns its candidate set and **blocks**; it never picks the first candidate |
| unit | `tests/unit/test_session.py::test_session__interruptions_are_declared_not_reconstructed` | `end_session` refuses a record whose `interruptions_minutes` was set after `ended_at` |
| unit | `tests/unit/test_report.py::test_report__average_across_templates_raises` | `AverageAttempted`. Criterion from the decomposition's negative-control list, mechanised |
| golden | `tests/golden/test_golden__per_template_settled.py::test_golden__nine_rows_including_the_nulls_and_the_zero` | all nine rows render: field surfaces **3,747 / 2,255 / 1,599 / 3,537 / n-a / 459 / 481 / 162 / n-a**, with `Draft_ACAC_Format` and `IFSCA_Annual_Reporting_Format` as `settledFraction: null` and `denominator.source = "not derivable — template ships no protection mask"`, and `EDR_1` (zero formula cells) as **0%, published anyway** |
| property | `tests/property/test_prop_rekey.py::test_prop__rekey_is_injective_or_unresolved` | for random label-preserving transforms of the FME blank, `rekey` never maps two source keys to one destination key |
| e2e | `tests/e2e/test_e2e__transfer.py::test_e2e__TRANSFER_over_the_nine` | `cdfc transfer --all`: per-template settled fractions **including the two `null` cases and the 0% case**, never averaged. This is the methodology's `E2E-TRANSFER` flow |

#### Negative controls — and one that is impossible, stated with its cost

*Existing:* **NC-D04** (coordinate-anchored keys silently rebind) — `rekey` is where that defect would
re-enter, and `test_rekey__label_anchored_survives_row_insertion` is its transfer-side guard.
**NC-D03** (a denominator for a template with no mask) — the per-template table is where it renders.

*New:*

```yaml
- id: NC-X08
  component: transfer
  break: "a settled fraction is averaged across templates, or a single cross-template figure is quoted"
  measured_instance: "the corpus contains two null-denominator templates and one 0% template; any mean over them is meaningless"
  injector: average_settled_fractions
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_report.py::test_report__average_across_templates_raises
      flips: true
    - path: tests/e2e/test_e2e__transfer.py::test_e2e__TRANSFER_over_the_nine
      flips: true
    - path: tests/golden/test_golden__per_template_settled.py::test_golden__nine_rows_including_the_nulls_and_the_zero
      flips: false
  positive_control: tests/golden/test_golden__per_template_settled.py::test_golden__nine_rows_including_the_nulls_and_the_zero
  status: ACTIVE

- id: NC-N08
  component: transfer
  break: "the transfer-cost measurement itself — a stopwatch over a human cannot be broken by an injector"
  measured_instance: null
  injector: NONE
  why_impossible: >
    The instrument is a person's elapsed time. A wrong reading is produced by learning, selection or
    reconstruction, none of which is a code path. Injecting a false duration proves nothing about the
    real one.
  guard_tests: []
  positive_control: null
  substitute_measurement: >
    A second operator re-runs 3 of the 10 carry sessions and 3 of the 10 authoring sessions; both
    operators' medians and their ratio are published in docs/measurements/P15-transfer-cost.md. If the
    operator effect exceeds the arm effect being claimed, the gate is NOT INTERPRETABLE, not passed.
  status: ACTIVE
```

**`substitute_measurement` is a required field on every `injector: NONE` entry**, per the DoD's line C6 as
repaired in `plan/01-validation-methodology.md` §4 — *"impossible" without a substitute is a skipped line.*
`test_nc_meta__every_entry_has_an_injector_or_a_reason` asserts it is non-empty wherever `why_impossible`
is. The three `injector: NONE` entries in §3 of this document (NC-N40, NC-N09, NC-N10) carry theirs in the
prose beneath them and it moves into the field verbatim.

**What NC-N08 costs, and the substitute measurement, because "impossible" is not an excuse to skip it.**
The transfer-cost figure carries an unquantified operator effect. The substitute, required and budgeted in
this build's person-hours: **a second operator re-runs 3 of the 10 carry sessions and 3 of the 10 authoring
sessions**, and `docs/measurements/P15-transfer-cost.md` publishes both operators' medians and their ratio.
If the two operators' medians differ by more than the CARRY/AUTHOR effect being claimed, **the threshold
comparison is not interpretable and the phase says so** rather than reporting the point estimate. This is
the same treatment §2.8 NC-N02 gives the INNOCUOUS/WRONG adjudication (re-adjudicate 20%, publish κ).

---

### BUILD P15-B2 — VERSION CHURN AND RE-QUALIFICATION · 3 days

**What it produces.** The seven rules V1–V7 as code, and the demonstration that **the settled fraction
falls when the template changes** — criterion A8.

#### Files created

```
src/cdfc/churn/__init__.py
src/cdfc/churn/identity.py         qualified_against as part of the predicate's identity
src/cdfc/churn/requalify.py        on_template_change: the PROVISIONAL sweep
src/cdfc/churn/quarantine.py       liveness-witness replay; a kill_case that stops dying
src/cdfc/churn/withdraw.py         withdrawn_on / withdrawn_reason
src/cdfc/ops/watcher.py            (interface only here; the model-free diff-and-flag body is P13-B4)
fixtures/synthetic/template-bumped__fy2029-30.xlsx
```

#### Public interface

```python
# src/cdfc/churn/identity.py
def predicate_identity(p: Predicate) -> str: ...
    # sha256 over RFC 8785 canonicalisation of (envelope, qualified_against).
    # CHANGING qualified_against CHANGES THE IDENTITY. There is no in-place edit;
    # supersession is a new row (registry rule R5).

# src/cdfc/churn/requalify.py
def on_template_change(old: str, new: str) -> ChurnReport: ...
    # ChurnReport(moved_to_provisional: tuple[str,...], still_running: tuple[str,...],
    #             numbers_hidden: tuple[str,...], numerator_delta: int, new_settled: int)
    # INVARIANT: moved_to_provisional == still_running == numbers_hidden.
    # A PROVISIONAL predicate STILL RUNS -- detection is not lost -- and does NOT count
    # in the settled numerator. Therefore numerator_delta <= 0, strictly < 0 when the
    # bump touches any settling predicate.

# src/cdfc/churn/quarantine.py
def replay_liveness(registry_root: str, template: str) -> QuarantineReport: ...
    # A predicate whose stored kill_case no longer dies is QUARANTINED automatically.
    # Nothing re-admits automatically; only a human clears it.
```

#### The fixture that makes this real rather than synthetic

`Dropdown!$E$3:$E$6 = {2025-26, 2026-27, 2027-28, 2028-29}` — **the FME workbook cannot express FY2029-30.**
That is a version event already on the calendar, and it is the honest churn fixture:
`fixtures/synthetic/template-bumped__fy2029-30.xlsx` is built by **raw-zip surgery** — copy every zip entry
byte-for-byte, rewrite exactly one worksheet XML (the `Dropdown` sheet) to add `2029-30`, and **never an
openpyxl round-trip**, per NC-P04. It bumps `template_sha256`, it bumps the structural fingerprint, and it
moves every membership predicate reading that vocabulary to `PROVISIONAL`.

**Warrants, separated, because one half of this is measured and the other half is a procedure that has not
run yet.** MEASURED (11 Aug 2026, `zipfile` over `7d9a1960…`): the workbook's largest part is
`xl/model/item.data` at **3,551,232 bytes = 3.55 MB of a 3,663,391-byte file — 96.9% of the archive is the
embedded data model**, which is precisely why an openpyxl round-trip collapses it to 65,877 bytes and why
the surgery must be at zip level. NOT a measurement, and asserted by a test instead: that the surgery
touches exactly one part. `tests/unit/test_fixtures.py::test_fixture__fy2029_differs_in_exactly_one_part`
diffs the two archives entry by entry and asserts `len(differing) == 1`, that the differing entry is the
`Dropdown` worksheet, and that all 19 `x14` validations survive — **a byte-identity claim about a fixture
is worth exactly as much as the diff that checks it, and the fixture is an input to criterion A8.**

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_identity.py::test_identity__qualified_against_is_part_of_identity` | changing any element of `qualified_against` changes `predicate_identity`. Rule V2 |
| unit | `tests/unit/test_requalify.py::test_requalify__provisional_still_runs` | a `PROVISIONAL` predicate appears in `run_check` with a state, and its cells are **not** in `settled`. Rule V3 — detection is not lost |
| unit | `tests/unit/test_requalify.py::test_requalify__numerator_falls` | `numerator_delta < 0` on the FY2029-30 bump. **Rule V4, criterion A8** |
| unit | `tests/unit/test_quarantine.py::test_quarantine__dead_kill_case_quarantines_automatically` | rule V5 |
| unit | `tests/unit/test_quarantine.py::test_quarantine__nothing_re_admits_automatically` | the sweep has no code path that sets `ACTIVE`; asserted structurally by an AST walk over `churn/` |
| golden | `tests/golden/test_golden__churn__fy2029.py::test_golden__fy2029_bump_moves_the_membership_set` | the named predicate ids that move, and the exact `new_settled` figure. R-GOLD-2: a **value** assertion on one moved predicate's `state` and `qualified_against.template_sha256`, not only on the count |
| e2e | `tests/e2e/test_e2e__churn.py::test_e2e__template_bump_lowers_the_chart` | end to end: bump → sweep → re-run → **`reports/settled-history.jsonl` gains a point whose `settled` is lower than the previous point and whose `cause` is non-empty** → the P14-B4 chart renders the step-down |

#### Negative controls

*Existing and central:* **NC-X05**, all three tests —
`test_nc__X05a_template_bump_moves_predicates_to_PROVISIONAL` (the settled fraction **falls**),
`test_nc__X05b_watch_gap_is_not_no_change` (a fetch failure writes `gap_since`, never `changed = false`;
**an unobserved day is not a quiet day**), and `test_nc__X05c_V5_alone_does_not_catch_a_rule_change` — the
test that documents a limit, built against the 24 July 2026 Authority-meeting change (close-ended
Restricted Schemes may move NAV periodicity from semi-annual to annual with 75% investor approval by value,
**a fact the workbook does not collect**), asserting the canary **still passes** because the mutant and the
predicate moved together, and therefore that V6 (the watcher) is doing the work.
*Also existing:* **NC-A15** (the chart cannot step down) — B2's e2e test is one of its three guards.

*New:*

```yaml
- id: NC-X06
  component: churn
  break: "a PROVISIONAL predicate stops running, so a template bump silently loses detection instead of losing a number"
  measured_instance: null
  injector: provisional_deactivates
  why_impossible: null
  guard_tests:
    - path: tests/unit/test_requalify.py::test_requalify__provisional_still_runs
      flips: true
    - path: tests/unit/test_requalify.py::test_requalify__numerator_falls
      flips: true
    - path: tests/golden/test_golden__churn__fy2029.py::test_golden__fy2029_bump_moves_the_membership_set
      flips: false
  positive_control: tests/golden/test_golden__churn__fy2029.py::test_golden__fy2029_bump_moves_the_membership_set
  status: ACTIVE
```

`injectors/provisional_deactivates.py` filters `PROVISIONAL` out of the active set. It must turn both
guards red — the first because detection is lost, the second because the numerator would fall *for the
wrong reason*, which is the subtler half and the reason both guards are named.

---

### BUILD P15-B3 — REGISTER SNAPSHOT POLICY, STALENESS, AND THE TERMS OF USE · 2 days

**What it produces.** A content-addressed register snapshot with a stated staleness bound, a fetch plan
quoted in its **form**, and a build gate that makes reading IFSCA's terms of use a precondition of any
scheduled polling.

#### Files created

```
src/cdfc/ops/register_snapshot.py
src/cdfc/ops/staleness.py
src/cdfc/ops/manifest.py
docs/TERMS-OF-USE.md
ci/no-scheduled-polling.sh              NEW stage-2 grep — §0.4(d)
ci/no-remembered-integer.sh             NEW stage-2 grep, with its planted control — §0.4(d)
docs/SCALE-TRIGGERS.md
```

#### Public interface

```python
# src/cdfc/ops/register_snapshot.py
def fetch_snapshot(endpoint: str, *, out: Path) -> SnapshotRecord: ...
    # SnapshotRecord(snapshot_sha256, endpoint, fetched_at, n_records, n_requests,
    #                list_response_sha256, detail_response_shas)
    # n_requests is RECORDED BY THIS RUN. It is never carried forward from memory.
    # Refuses to run unless docs/TERMS-OF-USE.md records read: true. See ci/no-scheduled-polling.sh.

def load_snapshot(sha256: str) -> Snapshot: ...
    # The ONLY way a host function sees the register. There is no live path at verdict time.

# src/cdfc/ops/staleness.py
STALENESS_BOUND_DAYS: Final[int]      # OPEN — see the decision rule below
def is_stale(snap: Snapshot, at: datetime) -> bool: ...
    # A stale snapshot degrades reg_resolves to NOT_RUN(not_run.input_unavailable.register).
    # It is NEVER silently used, and it is NEVER a FAIL.
```

#### The fetch plan, quoted correctly

**`1 list request + N detail requests, where N = |records|`** — the **form**, never an integer. The drafts'
figure of 2,235 is **withdrawn to UNRECONCILED** (audit §V.7.4): it matches neither `1 + 650 = 651` nor
`1 + 2,005 = 2,006`, no document states its `N`, and the run cannot be re-executed from the artifacts on
disk. `tests/unit/test_manifest.py::test_manifest__n_requests_comes_from_this_run` asserts the manifest's
`n_requests` was written by the fetch that produced the snapshot, and `ci/no-bare-absence.sh`'s sibling
`ci/no-remembered-integer.sh` (new, stage 2) greps `src/` and `docs/` for the literal `2235`/`2,235` in a
sentence that also names the register.

#### `STALENESS_BOUND_DAYS` is genuinely open. Here is the decision rule rather than an invented answer.

The spec gives no argued basis for a bound, and inventing one would be the `K`/`T` mistake repeated. **Until
an argument exists, `STALENESS_BOUND_DAYS = None`, `is_stale` returns `True` for any snapshot older than
the current run's `template.fetched_at`, and every register-dependent item renders
`NOT_RUN(not_run.input_unavailable.register)` with the reason string
`staleness bound not yet argued — see docs/OPEN-ITEMS.md#staleness`.** That is the conservative branch: it
loses coverage rather than gaining unwarranted coverage, which is the direction this system is built to
fail in.

**The decision rule that closes it.** The bound is set to the measured interval at which the register's
content hash changes, floored at one day: snapshot daily for **30 consecutive days**, record
`instrument_watch.content_sha256`, and set the bound to the **5th percentile of the observed inter-change
interval**. Denominator: 30 observations. Warrant will be **MEASURED**. Until those 30 days exist the bound
is `None` and the report says so. **Any number written before that measurement is a `PLACEHOLDER`, and it
renders as the literal string, exactly like `K` and `T`.**

#### The terms of use — a gap in conduct, turned into a code gate

`docs/TERMS-OF-USE.md` carries one row per external endpoint:
`{endpoint, terms_uri, read: true|false, read_by, read_at, polling_permitted: true|false|UNKNOWN, notes}`.

`ci/no-scheduled-polling.sh` (new, **stage 2, blocking**) fails the build if **any** of the following exists
while the matching row has `read: false` or `polling_permitted: UNKNOWN`: a cron entry, a systemd timer, a
GitHub Actions `schedule:` trigger, a `fly.toml` `[[schedules]]` block, or a call to
`ops.register_snapshot.fetch_snapshot` from anything under `src/cdfc/ops/watcher.py`. **This is the same
manoeuvre as NC-X02** — a conduct control turned into a code control, because a conduct control that lives
only in prose is the one that gets skipped under time pressure.

Today the IFSCA register row reads `read: false`, and the manual one-shot fetch that produced the 10 Aug
2026 snapshot is recorded as `manual, one-shot, pre-dating this gate` in the notes. **The gate blocks
*scheduled* polling, not the recorded one-shot** — and it says which.

#### Validation

| Class | Test | Asserts |
|---|---|---|
| unit | `tests/unit/test_staleness.py::test_staleness__unargued_bound_degrades_not_guesses` | with `STALENESS_BOUND_DAYS is None`, every register item is `NOT_RUN(input_unavailable.register)` and **no digit** renders in the bound's place |
| unit | `tests/unit/test_manifest.py::test_manifest__pins_eight_things_and_no_libreoffice` | the eight pins, and `libreoffice` **absent**. This is NC-A03c's P15-side twin |
| contract | `tests/contract/test_contract__terms_of_use_rows.py::test_contract__every_external_endpoint_has_a_row` | every host reachable from `src/cdfc/ops/` appears in `docs/TERMS-OF-USE.md` |
| e2e | `tests/e2e/test_e2e__no_live_register.py::test_e2e__verdict_runs_with_the_socket_blocked` | monkeypatch `socket.socket` to raise; a full FME run completes `VALID` reading the snapshot only. Shares NC-X01's statement and NC-A04b's mechanism |

**Negative controls.** *Existing:* **NC-X01** (`test_nc__X01_host_fn_reads_the_snapshot_only` — under a
blocked socket the function resolves from `register_snapshot_sha256`; two runs at different wall-clock times
return the same tri-state answer; a snapshot older than the bound degrades rather than being silently used),
**NC-X03** (raw **and** normalised both stored — the `U+2011 NON-BREAKING HYPHEN` record must stay
byte-distinguishable from a `U+002D` record; and membership-not-format, whose worked example is the
**87 of 228 = 38.2%** regex false-failure rate), **NC-X02** (an absence reported from the wrong field —
`EncryptDId` null on 2,005 of 2,005 while `EncryptedId` is populated on 2,005 of 2,005). *New:*

```yaml
- id: NC-X07
  component: ops
  break: "scheduled polling of an external endpoint exists while its terms of use are unread"
  measured_instance: "IFSCA's terms of use for the register API have not been read — spec §III.7, open"
  injector: add_scheduled_poll
  why_impossible: null
  guard_tests:
    - path: tests/negative/test_nc_ci.py::test_nc__X07_no_scheduled_polling_without_terms
      flips: true
    - path: tests/contract/test_contract__terms_of_use_rows.py::test_contract__every_external_endpoint_has_a_row
      flips: false     # adding a schedule does not remove a row; this guard cannot see the break,
                       # and its own injector is `injectors/drop_terms_row.py` under the same entry's
                       # sibling NC-CI12 family. Declaring it false is what stops NC-X07 from being
                       # recorded `caught` on a guard that was never exercised.
    - path: tests/negative/test_nc_ci.py::test_nc__X07b_manual_one_shot_is_permitted
      flips: false
  positive_control: tests/negative/test_nc_ci.py::test_nc__X07b_manual_one_shot_is_permitted
  status: ACTIVE

- id: NC-CI12
  component: ops
  break: "a withdrawn integer is quoted from memory — the 2,235 register GETs that reconcile with no stated N and cannot be re-executed from the artifacts on disk"
  measured_instance: "audit §V.7.4 withdrew 2,235 to UNRECONCILED: it matches neither 1 + 650 nor 1 + 2,005"
  injector: quote_2235
  why_impossible: null
  guard_tests:
    - path: tests/negative/test_nc_ci.py::test_nc__CI12_withdrawn_integer_is_caught
      flips: true
    - path: tests/unit/test_manifest.py::test_manifest__n_requests_comes_from_this_run
      flips: false     # the manifest is still written by the fetch; the injector plants prose
  positive_control: tests/unit/test_manifest.py::test_manifest__n_requests_comes_from_this_run
  status: ACTIVE
```

`injectors/add_scheduled_poll.py` writes a `schedule:` trigger into `.github/workflows/ci.yml` calling
`cdfc watch`. `ci/no-scheduled-polling.sh` must exit non-zero. The positive control matters as much: the
gate must **not** block the recorded manual one-shot, or it becomes a gate people disable.
`injectors/quote_2235.py` writes *"the register was fetched in 2,235 requests"* into a `docs/` line naming
the register; `ci/no-remembered-integer.sh` must exit non-zero.

---

### BUILD P15-B4 — DEPLOYMENT AND THE REPRODUCIBILITY OF A PUBLISHED REPORT · 2 days

**What it produces.** One Docker container, the mandatory laptop fallback, and the proof that a report
served from a deployment re-derives byte-identically from a clean clone.

#### Files created

```
Dockerfile
fly.toml
Makefile                     targets: demo, deploy, verify-published, transfer, churn, surface-audit
docs/SCALE-TRIGGERS.md
docs/DEPLOY.md
tests/e2e/test_e2e__published_report.py
```

#### Interface, as commands

```
make demo              ingest -> induce -> harvest -> run, offline after the fetch, on a laptop
make deploy            build, push, and release the single container
make verify-published  fetch the published report ONCE, then run `cdfc verify` OFFLINE against it
```

**The laptop is the demo path and is mandatory as the fallback.** `make demo` must complete with the
network namespace closed. `tests/e2e/test_e2e__demo_offline.py` is the methodology's `E2E-DEMO` flow and it
additionally asserts **every number quoted in `README.md` is reproduced from program output**, matched by a
registry (`docs/README-NUMBERS.md`, one row per quoted figure with the command that produces it) rather
than by a hand-written list — the same denominator discipline as `REQUIRED_NUMBERS`.

#### Deployment shape and cost, stated with warrants

One container, `shared-cpu-1x` / 512 MB, **$3.32/month ≈ ₹290/month (VERIFIED-AT-SOURCE)**; storage
~3.4 GB/yr; **≈ $240 ≈ ₹21,000 a year all in**. No queue, no broker, no worker pool: the deterministic core
is ~30 ms (MEASURED) and the whole 19,782-mutant campaign is 2.5 s (MEASURED). At the modelled population of
**868 filings/yr** — 3.4 per working day, about **1.5 seconds of compute per day** — this deployment is
absurdly over-engineered as a *deployment*, and `docs/DEPLOY.md` says so in those words. It is not
over-engineered as a research instrument.

#### `docs/SCALE-TRIGGERS.md` — what breaks first at 100×, in order, with the trigger for each

| # | Breaks | Trigger — **not** volume in the abstract | The move, and what it costs |
|---|---|---|---|
| 1 | **Blob storage** | disk, at 3.66 MB × 86,800 ≈ **320 GB/yr** | Object storage on the **identical `sha256` path**. The content-addressing scheme is unchanged, which is the point of choosing it |
| 2 | **SQLite's single writer** | **concurrent uploads, not row count** | Postgres — and it **loses content-addressability**, so the run manifest must then name a logical snapshot id instead of a file hash. §7.11 applies from that day: every determinism and closure guarantee must be re-derived and none of the current tests will notice they no longer hold |
| 3 | **The register snapshot** | the `1 + N` fetch plan against a staleness bound and unread terms of use | Snapshot daily, cite the hash **and its age**, degrade past the bound. Blocked on B3's terms-of-use row |
| 4 | **The qualification corpus** | **it does not scale with filings at all — it scales with templates** | This is the real one, and it is P15-B1's question |

#### Validation

| Class | Test | Asserts |
|---|---|---|
| e2e | `tests/e2e/test_e2e__demo_offline.py::test_e2e__DEMO_from_a_clean_clone_offline` | clean clone, network namespace closed, `make demo` completes; every `docs/README-NUMBERS.md` row reproduced from program output; the report opens from `file://` |
| e2e | `tests/e2e/test_e2e__published_report.py::test_e2e__published_report_reproduces_byte_for_byte` | fetch once, verify offline, `REPRODUCED`, zero differing bytes. **Deferred with its reason if P11-B2 has not landed** (§0.3) |
| e2e | `tests/e2e/test_e2e__published_report.py::test_e2e__tampered_published_report_reports_a_diff` | flip one byte; `verify` reports a diff, not `REPRODUCED`. The methodology's `E2E-TAMPER` |
| determinism | `tests/determinism/test_det__container_and_laptop_agree` | the container's `report.html` and the laptop's are byte-identical for the FME reference run |
| unit | `tests/unit/test_deploy.py::test_deploy__no_queue_no_broker_no_worker` | an import-closure walk over the deployed package asserting `celery`, `redis`, `rq`, `kombu`, `arq` are unreachable — do-not-build row 12, mechanised |

*Existing negative controls this build leans on:* **NC-A03** (all five determinism injectors), **NC-A04**
(`test_nc__A04a` import closure, `test_nc__A04b` blocked socket, `test_no_libreoffice_online`,
`test_no_tlog`), **NC-L01** (registered to `01` by C9, which found it referenced here and defined nowhere — the licence gate against the research venv, which still contains `formulas`
1.3.4 EUPL 1.1+ and `pycel` 1.0b30 GPL-3.0, both denylisted — a negative control that requires no injection
because it is on disk right now).

---

## P15 · The measurement this phase produces

> **Human minutes per transferred predicate, against the from-scratch authoring baseline.**
> Reported as `CARRY_median / AUTHOR_median` with both medians, both `n`s (≥ 10 predicates), the
> abandoned-session count, the ABBA order index per session, and the second operator's re-run of 3 + 3.
> Denominator: ≥ 10 predicates on the CMI workbook (`82dd291f…`). Warrant **MEASURED**.

> **And the per-template settled-fraction table for all nine, never averaged** — including
> `Draft_ACAC_Format` and `IFSCA_Annual_Reporting_Format` as `null` (no protection mask; the latter's naive
> unlocked-cell count of **8** is the dangerous case, NC-D03) and `EDR_1` at **0%** (zero formula cells).
> Denominator: 9 templates. Warrant **MEASURED**.

Two further numbers, both new and both cheap:

3. **`numerator_delta` on the FY2029-30 bump** — how far the settled count falls when one vocabulary gains
   one member. Nobody has this, and it is the quantitative form of criterion A8.
4. **COUNTIF vocabulary gaps per workbook** — denominator 9. On FME this is the `D17` defect (three
   COUNTIFs missing two of nine legal scheme types); whether it recurs elsewhere converts one finding into
   a pattern, and the spec lists it as open.

All four rows go to `reports/validation-ledger.jsonl` with `denominator_source`, `warrant`, `produced_by`
and a `caveat` sentence stating exactly what each licenses.

---

## P15 · Exit gate — this is gate **G-TRANSFER (cost arm)**

1. **Pre-registered threshold met:** human minutes per transferred predicate ≤ **0.5×** the median
   from-scratch authoring time, over **≥ 10** predicates on the CMI workbook, with
   `experiments/E4/PREREGISTRATION.md` committed and hashed **before** the first session and the hash in
   the README. **The threshold is stated as arithmetic the deciding function consumes**, not as prose:
   `beats_authoring := carry_median <= 0.5 * author_median and n_carry >= 10 and n_author >= 10 and
   abandoned_declared`. `test_contract__preregistration_criterion_is_machine_evaluable`
   (`plan/01-validation-methodology.md` §1.9) makes the lock **refuse to write** a criterion `decide()`
   cannot evaluate. A criterion whose reading is chosen after the numbers arrive is not a criterion, and
   the whole epistemic value of this file is that it was fixed before the stopwatch started.
2. **The inter-operator re-run is published**, and if the two operators' medians differ by more than the
   effect being claimed, the gate is recorded **NOT INTERPRETABLE** rather than passed or failed.
3. **Bumping the template hash demonstrably makes the settled count decrease** —
   `test_requalify__numerator_falls` and `test_e2e__template_bump_lowers_the_chart` green, and the history
   chart renders a labelled step-down.
4. **A deployed report re-derives byte-identically from a clean clone** — or the sub-gate is recorded
   `DEFERRED — pending P11-B2` and rendered as such (§0.3). **Never recorded as a pass.**
5. `docs/TERMS-OF-USE.md` exists with a row per external endpoint, and `ci/no-scheduled-polling.sh` has been
   **observed red** under `injectors/add_scheduled_poll.py` **and green under the recorded manual one-shot**
   (`test_nc__X07b`) — a gate that also blocks the lawful case is a gate people disable.
   `ci/no-remembered-integer.sh` has been observed red under `injectors/quote_2235.py`
   (**`test_nc__CI12_withdrawn_integer_is_caught`**, entry **NC-CI12**).
6. `docs/measurements/P15-transfer-cost.md`, `P15-per-template-settled.md` and `P15-countif-gaps.md`
   published; `reports/validation-ledger.jsonl` has grown by ≥ 4 rows, **each carrying `measures`**
   (§0.5): the transfer-cost ratio is `DISCRIMINATION` over its stated instrument, the per-template
   settled-fraction table is **nine `REACH` rows and never one number**, `numerator_delta` is `CENSUS`,
   and the COUNTIF vocabulary gaps are `CENSUS` over denominator 9. **No row in this phase may be
   captioned with a verb of verification** — `test_ledger__reach_rows_carry_no_quality_claim`.
7. `churn/` meets its mutation tier (Tier Q, `K/V ≥ 0.85` — it decides whether a number is hidden, which is
   qualification behaviour); `transfer/` and `ops/` meet Tier S (`K/V ≥ 0.70`), all with the
   equivalent-mutant caveat in the §3.5 form.
8. **`make nc-sweep` reports all four integers** and `guards_flipped == guards_expected_to_flip` for every
   entry this phase adds (NC-X06, NC-X07, NC-X08, NC-CI12, NC-N08, NC-N10). Evidence for DoD line C4 is
   the sweep report's rows at the merge commit, not a pasted line. `ci/catalogue-ids.sh` green: every id
   this phase defines lies in this document's allocated block.

## P15 · What it kills if it fails

| Failure | Consequence, honestly |
|---|---|
| **Transfer is not materially cheaper than authoring** | **The product claim narrows from "a method for prescribed regulatory returns" to "an instrument for the FME quarterly return".** The negative result is published, `P15-B1` becomes the paper's central table, and the multi-template surfaces are dropped. The research contribution — the gate, the coverage declaration, the residue set — is unaffected. **Smaller, not stalled** |
| **The gate is NOT INTERPRETABLE** (operator effect swamps the arm effect) | Worse than a negative result and must be reported as worse: the measurement is repeated with a third operator, or the claim is withdrawn entirely. **It is never rounded into a pass** |
| **The settled fraction does not fall on a template bump** | Criterion A8 fails and **the version-churn story is false**. `PROVISIONAL` is not doing its job, and a system whose coverage silently persists across a version boundary is lying. This is a hard failure: the churn machinery is rebuilt, not documented around |
| **Byte identity of a published report cannot be achieved** | Inherits P11's failure branch: name the non-determinism; if it cannot be removed, the attestation drops byte-identity for a **field-level re-derivation claim**, labelled weaker on the surface |
| **The terms of use cannot be obtained or forbid polling** | `polling_permitted: false` is a valid answer. The watcher becomes manual, `instrument_watch` records the manual cadence with its gaps, and the register host function's staleness bound is set by the manual cadence. **The gate does not become an exception; the product's behaviour changes** |
| **The whole phase fails** | Nothing upstream is affected. What ships is the single-template instrument with its surfaces, its gate, its closure, its canaries, its residue set and its attestation — and a published measurement saying transfer was not demonstrated |

---

## §3 — WHAT THESE TWO PHASES CANNOT ESTABLISH

Required by the methodology's own standard (§7), and by rule R1's clause about impossible negative
controls. Three new entries, each with what it costs.

```yaml
- id: NC-N40
  component: surface
  break: "an all-clear mark drawn as vector paths, a raster image, or a font ligature"
  injector: NONE
  why_impossible: >
    SG1 scans source text and rendered DOM text including ::before/::after content values. A tick
    hand-drawn as an SVG <path> in a template, embedded as a data: URI image, or delivered by a
    ligature in an inlined font is not text at any stage and no test we can write detects it
    soundly. Optical detection of a checkmark in a rasterised page is a classifier, and a
    classifier with an unmeasured error rate is exactly what this product refuses to ship.
  guard_tests: []
  positive_control: null
  substitute_measurement: >
    Review, made countable: the template set is small, every template addition requires a DoD line
    naming the surface, and `git log --stat -- src/cdfc/surface/templates/` is the review surface.
    docs/measurements/P14-surface-audit.md publishes the count of template-touching commits reviewed
    against the count made, so an unreviewed template addition is visible as a gap.
  status: ACTIVE

- id: NC-N09
  component: surface
  break: "the surface registry is incomplete — a surface nobody registered is scanned by nothing"
  injector: NONE
  why_impossible: >
    NC-A10 catches a surface that renders through the known render paths. It cannot catch a surface
    produced by a path nobody thought of. The gate's denominator is written by the same people who
    wrote the surfaces, which is §7.6's self-referential denominator applied to the surface audit.
    NOTE the boundary: NC-N09 is about the registry being INCOMPLETE, which cannot be mechanised.
    NC-A30 is about the registry SHRINKING, which can be and now is.
  guard_tests: []
  positive_control: null
  substitute_measurement: >
    |SURFACES| is published as a per-commit time series in docs/measurements/P14-surface-audit.md.
    If new surfaces keep being discovered late, the registry is incomplete and the RATE is visible.
    Report it; do not claim it converges.
  status: ACTIVE

- id: NC-N10
  component: transfer
  break: "that the transfer measurement generalises past the second workbook"
  injector: NONE
  why_impossible: >
    E4 arm 2 measures one source template, one target template, one or two operators, ten
    predicates. There is no sampling frame over prescribed regulatory workbooks and there will not
    be one. The result licenses a statement about FME -> CMI and nothing wider.
  guard_tests: []
  positive_control: null
  substitute_measurement: >
    docs/measurements/P15-transfer-cost.md's header carries the licensed sentence verbatim, in the
    may_be_quoted_as form of methodology §6.4, and the ledger row's `measures` is DISCRIMINATION over
    one operator pair on one template pair -- stated in the caveat, not inferred from the number.
  status: ACTIVE
```

**Both sides renumbered, and the contested id is retired (arbitration C9).** `02` P0-B4 independently
allocated `NC-N07` for *a field observation quietly dropped* while this document allocated `NC-N07` for
*an all-clear mark drawn as vector paths*. Each document then instructed the other to move — which is how a
collision survives its own repair. Under C9 **neither keeps it**: `02`'s entry became **`NC-N16`**, this
document's became **`NC-N40`**, and **`NC-N07` is RETIRED PERMANENTLY**, never reassigned, with
`test_nc_meta__no_dangling_reference` failing the build on any reference to it. Two entries sharing an id
is not a bookkeeping nit: **the catalogue loads into a dict keyed by `id`, and the later document's row
silently replaces the earlier one** while the sweep still prints `caught == active`.

**What NC-N40 costs.** The no-all-clear commitment is a system property for *text* and a *review* property
for *marks*. The mitigation is not a test: the template set is small, every template addition requires a
DoD line naming the surface, and `git log --stat -- src/cdfc/surface/templates/` is the review surface. Say
"no all-clear glyph or phrase, enforced in source and in the rendered DOM"; **never** say "the product
cannot display a tick".

**What NC-N09 costs.** The phase's headline number is *"k of the n surfaces we enumerated"*, and that exact
sentence renders on `docs/measurements/P14-surface-audit.md`. The only available instrument is the
registry's append-only growth log: if new surfaces keep being discovered late, the registry is incomplete
and the rate is visible. Report it; do not claim it converges.

**What NC-N10 costs.** G-TRANSFER's PASS branch licenses *"carrying a predicate from the FME return to the
CMI return cost 0.4× authoring one, over 10 predicates, one operator, with a second-operator check"*. It
does not license *"the method transfers"*. The `docs/measurements/P15-transfer-cost.md` header carries the
licensed sentence verbatim, in the `may_be_quoted_as` form of §6.4.

Four residues from the methodology carry through unchanged and are restated only by reference:
**§7.4** (deception — a coherent liar passes every check; the sentence stays on the report surface, and
`S02.report-hero`'s template makes it non-dismissible), **§7.6** (the catalogue's self-referential
denominator), **§7.10** (performance measured at one scale, on one machine class — `SCALE-TRIGGERS.md`
enumerates what breaks but measures none of it), **§7.11** (no concurrency coverage at all, by
construction — which is item 2 of `SCALE-TRIGGERS.md`, so this document names the day these tests stop
being valid before that day arrives).

---

## §4 — WHAT IS GENUINELY OPEN IN THESE TWO PHASES, WITH ITS DECISION RULE

Five items. None is invented an answer here; each gets the rule that closes it.

| # | Open | Decision rule |
|---|---|---|
| **O1** | **`K` and `T` in `pervasiveness-policy-v1.json`** — the pervasiveness thresholds that decide `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` versus `SETTLEMENT_INSUFFICIENT`. No argued basis anywhere in the corpus | They render the literal string `PLACEHOLDER` on **every** surface and in **every** example until an argument exists (spec §III.7 C22). The argument must be a written one about *pervasiveness*, not a number chosen because it makes the reference filing look better. **This does not block P14** |
| **O2** | **`STALENESS_BOUND_DAYS`** | `None` until 30 consecutive daily snapshots exist; then the 5th percentile of the observed inter-change interval, floored at 1 day, denominator 30, warrant MEASURED. Until then every register item degrades to `NOT_RUN(input_unavailable.register)` — the conservative direction |
| **O3** | **IFSCA's terms of use for the register API** — a gap in conduct, not code | `docs/TERMS-OF-USE.md` row with `read: false` today. `ci/no-scheduled-polling.sh` blocks scheduled polling while it stays false. If the terms forbid polling, `polling_permitted: false` is a valid answer and the watcher becomes manual with its gaps recorded — the product changes, the gate does not acquire an exception |
| **O4** | **Whether the report ships a dark rendering** | Not decided in any spec. **Rule: one look until a user asks.** If a second rendering is added, SG4 runs against **both** and the gate's denominator doubles — an added rendering that is not audited is an unregistered surface (NC-A10) |
| **O5** | **Who Person A is** (spec §7 Q3 / G10) — gates every FFR digit on every P14-B4 surface | Not a P14 decision and P14 must not wait on it. B4 ships with `render_ffr` returning `uninformative`; if the audited second-model-instance fallback fires, `person_a_kind: "model-instance"` renders **wherever the FFR renders**, and the record says the fallback is weaker than a human (methodology §6.3 item 4) |

---

## §5 — THE DEFINITION-OF-DONE DELTAS FOR THESE PHASES

`docs/DOD-TEMPLATE.md` is filled once per **build** — six times across P14 and P15. Four lines carry
phase-specific content that a reviewer should look for first:

- **C3 / C4 (guards observed red, and the *right* guards).** C3 carries **all four integers**, and the pair
  that matters for these phases is `guards_flipped / guards_expected_to_flip`: several entries here name
  three or four guards and an injector reaches only some of them, which is precisely why every
  `guard_tests` row in this document declares `flips: true|false`. C4's evidence is **a path, not a
  paste** — `reports/negative-control-sweep.json`'s rows for the entry at the merge commit, whose
  `assertion_text` and `node_id` are non-empty for every flipped guard. For P14 the rows to look at first
  are `ci/surface_audit.py` under `injectors/plant_glyph.py`, under `injectors/band_fills.py`, and under
  `injectors/delete_failing_surface.py`. **An engineer who cannot show the row that went red has written a
  second test, not a negative control — and a reviewer who cannot resolve it has not checked one.**
- **C6 (impossible controls).** P14 must name **NC-N40** and **NC-N09** with their costs; P15 must name
  **NC-N08** and **NC-N10** with theirs, and P15-B1's must include the second-operator substitute
  measurement, because "impossible" without a substitute is a skipped line.
- **D7 (rates).** Every P15-B1 figure is a **median with both `n`s**, never a mean and never a bare ratio.
  Every P14-B4 FFR carries `corpus_id`, `corpus_provenance`, `n` and a Wilson interval, or renders
  `uninformative`.
- **H1 (what this build does not establish).** For P14-B1 the required sentence is that the report renders
  every number **in `REQUIRED_NUMBERS`**, which is a registry we wrote. For P15-B1 it is that the result
  licenses a statement about FME → CMI and nothing wider (NC-N10).

---

## §6 — THE CLOSING CHECK ON THESE TWO PHASES

Four properties to verify if this document drifts.

**One. Every gate here has a denominator that a machine maintains — and every such denominator is
append-only with a growth log.** `SURFACES`, `REQUIRED_NUMBERS`, `FUNNEL_STAGES`, `PERMITTED_BOOLEANS`,
`SCAN_ROOTS`, `docs/README-NUMBERS.md`, `docs/TERMS-OF-USE.md`. A gate whose denominator is a hand-written
list in a test file has already started to rot, and this project's own corpus contains five instances of
exactly that rot going unnoticed. **The second half of the sentence is new and it is the half the adversary
pass had to supply**: a machine-maintained denominator that the same build may *shrink* is not better than a
hand-written one — it is worse, because it looks rigorous. Every registry above obeys R-DENOM-1
(`plan/01-validation-methodology.md` §5.1), publishes its cardinality as a time series, and needs a dated
argument to lose a row (`test_surface__registry_is_append_only`, NC-A30). If a revision replaces a registry
with a literal, **or removes a row without an argument**, that revision has weakened a gate and should say
so.

**Two. Every prohibition here is structural before it is tested.** `Hero` has no default for `admission`.
`render_ffr` has no code path that formats a digit for `SELF-AUTHORED`. `SettledFractionOut` refuses to
validate a bare fraction. `band_segments` always emits its two hatched terminal segments. `history_points`
raises on an unlabelled step-down. The tests exist to prove the structure exists — not to substitute for it.
A revision that converts any of these into a check is a downgrade.

**Three. The one thing P14 can be tricked into.** A surface that passes all four gates and says nothing
true. Every gate in this phase is a *prohibition*; not one of them establishes that a rendered number is
correct. The correctness of the numbers is P2's, P3's, P5's, P7's and P8's problem, and the surface phase
inherits whatever they produced. **If the settled count is wrong, this phase will render it beautifully,
in equal weight, with its admission state, and no gate will fire.** That is stated here so nobody reads a
green surface audit as evidence about the filing.

**Four. A golden test is where an illustrative number becomes a measured one, and this document already
made that mistake once.** A draft of this file pinned the hero as the literal triple `12 / 2,373 / 1,374`
and captioned it MEASURED. Only **one** of those is measured against the published file; `12` is the spec's
own *illustrative* pass/fail split (§II.5.1 says so in the same JSON block), and the same draft labelled the
per-sheet **field surface** decomposition — `1,698 · 897 · 480 · 371 · 231 · 25 · 23 · 22`, which sums to
**3,747** — as the per-sheet *unchecked* split, whose total is **1,374**. Both were well-formed, confident
and wrong, in the phase built to stop exactly that, written by someone who had just read the rule.
**The mechanism is specific and worth naming: a golden test launders a warrant.** An illustrative figure
that is pinned becomes a figure that CI defends, and a figure CI defends gets quoted. Hence the standing
rule for every golden test in these two phases: *a literal in a golden assertion must trace to a row of
`plan/01-validation-methodology.md` §0.3 or to `reports/validation-ledger.jsonl`; everything else is
asserted relationally.*

**And the draft made the mistake a third time, in the sentence that corrected the first two.** Having
refused to pin the illustrative `12`, it pinned `S = 2,373` and `U = 1,374` as literals labelled MEASURED —
and those two are properties of *our harvest over the pinned blank*, not of the published file. G3's first
rejection lowers `S`, so the literal fails on correct behaviour and gets quietly updated; and the claim that
2,329 of them come from *53 validation predicates* does not reconcile with the **20** membership predicates
FME's 54 validations actually yield. Both are now asserted relationally, the literals live in
`docs/HARVEST-DELTA.md`, and `docs/measurements/P4-harvest-distribution.md` must reconcile the computed
figure against 2,373 in writing.

**The rule is no longer a review obligation.** This section previously concluded that
`ci/golden-asserts-values.sh` (R-GOLD-2) checks *that* a golden asserts values but not *where the value came
from*, that nothing could, and that this was *"the fourth impossible control of these phases in all but
name."* **That was wrong, and the error is worth keeping visible: it is not impossible — it is a grep over a
ledger.** `ci/golden-literals-are-traceable.sh` (rule R-GOLD-3, `plan/01-validation-methodology.md` §1.3 and
§5.4, stage 2) extracts every integer literal appearing in a comparison under `tests/golden/` and resolves
it against §0.3's fixture table or a `reports/validation-ledger.jsonl` row, failing the build on an
untraceable one. It walks the same files R-GOLD-2's script already walks. **The impossible control was three
lines of shell and an artifact the plan already required**, and the general lesson is the one this document
keeps re-learning at its own expense: *before recording a control as impossible, name the artifact that
would have to exist — and then check whether it already does.*

---

## REPAIRS APPLIED (adversary pass)

Compiled against `plan/08-adversary.md`. One line per finding: the finding, the change, the location.
The full catalogue-id mapping this pass produced lives in `plan/01-validation-methodology.md`'s
REPAIRS APPLIED section; only this document's own ids are restated here.

### Findings closed in this document

| Finding | Sev | In one line | What changed, and where |
|---|---|---|---|
| **F11** | SERIOUS | P14's exit gate compares a registry against itself — a surface that cannot pass SG1–SG4 can be deleted to make the gate green | New block in **P14-B1**, *"`SURFACES` and `REQUIRED_NUMBERS` are append-only"*: both obey R-DENOM-1 (`01` §5.1), retirement replaces deletion, a retirement needs a dated argument in `docs/measurements/P14-surface-audit.md`, **both cardinalities publish as per-commit time series**, and `test_surface__registry_is_append_only` + `test_surface__gate_floor_is_the_logged_cardinality` enforce it. **Exit criterion 1 gains a floor.** New entry **NC-A30** with injector `delete_failing_surface`. `test_surface__retired_rows_are_still_scanned`: a retired surface leaves the *denominator*, never the *scan*. "What it kills" gains the shrinkage row, distinguished from NC-N09's incompleteness |
| **F22** | SERIOUS | `S = 2,373` / `U = 1,374` pinned as MEASURED literals in `test_golden__report_hero__fme`, and they do not reconcile with the harvest | The hero warrant note is rewritten: **`cellsTotal = 3,747` is the only pinned literal** (it is in `01` §0.3); `S`, `U` and `F` are asserted **relationally** (`S == len(static_settled_cells(...))`, `S + U == inScope`, `F + pass == S`); `2,373`/`1,374` move into `docs/HARVEST-DELTA.md`; `docs/measurements/P4-harvest-distribution.md` must reconcile the computed figure against 2,373 **in writing, and a divergence is a finding**. The golden table row and exit criterion 10 restated. Enforced by `ci/golden-literals-are-traceable.sh` (R-GOLD-3, `01` §1.3) rather than by care. §6 item Four corrected — it had called this *"the fourth impossible control"* |
| **F28** | SERIOUS | three different scan sets guard the copy commitment, two of them naming directories P0 never creates | **`labels.SCAN_ROOTS` is the single source of truth**, added to P14-B1's public interface, shipped as a P0 stub `("src/cdfc",)` and extended by P14-B1; `ci/no-green-tick.sh`, SG1's source arm and SG4's rendered arm all read it; `test_nc__CI01c_scan_root_list_is_not_a_literal`; `SCAN_ROOTS` is an R-DENOM-1 registry so it cannot shrink without a dated `ci/GATES.md` argument. The *"gate's own scan-set hazard, closed"* paragraph is rewritten to say what the hazard actually was |
| **F29** | MINOR | P15-B1's entry criterion names `docs/measurements/P4-transfer-mechanical.md`, which P4-B4 does not create | **DECIDED: one file, `docs/measurements/P4-harvest-distribution.md`**, referenced through the module constant `cdfc.measure.paths.P4_HARVEST_DISTRIBUTION` (created at `02` P0-B1; `03` obligation X6), never a literal (`06` §0.9's rule). *Alternative it beat:* two files, one per transfer arm — rejected because the mechanical arm is a cut of the harvest distribution and a second file would restate the first's denominator. New `test_paths__every_entry_criterion_document_exists` walks every entry-criteria table in `plan/` and asserts each named path resolves |
| **F1** | FATAL (surface half) | G2's registry bar computes `K/O` over a denominator the predicate chooses after the campaign | `LibraryRow` gains `claims_fault_classes` (non-empty, inside `code_sha256`) and **two** kill rates — `kr_claimed` and `kr_all_classes` — which **render together or not at all** (`test_library__both_kill_rates_render_or_neither_does`, raising `UnpairedKillRate`). `test_library__claims_are_non_empty_and_content_addressed`. **The gap between the two is the number a reviewer wants**, and the surface's job is to make the selection legible |
| **F18** | FATAL (surface half) | `U/G` measures the evaluator's coverage, not our operator mix, and each exclusion raises `K/O` | New `KillRateCell` with **six integers `G · U · I · O · R · K`**, `O == G − U − I`, plus `indeterminate_cells` naming the cells that made `I` non-zero. `test_library__kr_renders_six_integers_and_the_vector` and `test_library__indeterminate_cells_are_named`. `I` publishes beside `U/G` **every time either renders**, so `U/G` reads as a property of our apparatus |
| **F19** | FATAL (surface half) | the flagship F11 class is discarded from `O`, so `TEMPLATE_DIFF` can never clear G2 | Carried by the same six-integer census: an `O` that lost a whole fault class is visible as `U` or `I`, and the per-fault-class vector shows `O = 0` for F11 rather than hiding it. The contract fix (`formula_source: TEMPLATE \| FILING`) is `02`/`04`'s |
| **F3** | FATAL (surface half) | G-EVAL arm 2 may be a self-check, and the label never reaches the surfaces that quote the rate | `KillRateCell.instrument_label`, **read from `ci/GATES.md` and never from a constant**; `test_library__kill_rate_carries_its_instrument_label` asserts the literal `SAME-AUTHOR — a weaker instrument` renders **in the same block** as the rate (ancestor distance ≤ 2, the NC-A05 technique). Exit criterion 9 |
| **F9** | FATAL (surface half) | G0's disposition of the 280 clause-less harvested candidates is undefined, and P7's headline funnel depends on it | `FunnelStage` gains **`skipped`** — three integers per stage, `entered == skipped + survived + len(rejections)` asserted (`test_funnel__stage_arithmetic_closes`); a wholly-skipped stage renders `NOT APPLICABLE — 0 evaluated`, never a full-width bar; **both obligation-coverage numbers are published together** (arbitration **C2**): `predicates_with_a_STATUTE_obligation / 280`, today `0 / 280`, **and** `predicates_with_a_TEMPLATE_obligation / 280`, today `280 / 280` — `test_surface__both_obligation_counts_render_or_neither_does` raises `UnpairedObligationCount` on either alone. *The unqualified single figure this row originally published was wrong by 280 under the arbitrated mechanism.* New entry **NC-A32**, injector `funnel_skipped_counts_as_survived` |
| **F2 / F12** | FATAL / SERIOUS (surface half) | a corpus the product computed can license an FFR, and G-CORPUS's `n ≥ 30` is satisfiable from it | `render_ffr` now returns `uninformative` in **three** cases, the third being the **computed** `clean_corpus_independent_of_predicate` (`01` §6.3 item 6), with the admission-side twin `test_render_ffr__register_derived_membership_prints_digits`. **G-CORPUS gains a third outcome, `RESTRICTED`**, rendered distinctly with the literal string in the column header; B4's entry criterion re-reads *"any of its three ways"* and **must never treat `RESTRICTED` as `PASS`**; `test_library__three_corpus_outcomes_render_distinctly` |
| **F15** | SERIOUS (surface half) | nothing can falsify the protection-resolution rule, and every fraction is a fraction of it | New label `hero.denominator_rule`, bound to `settledFraction.denominator.generator_rule`, **required in the same block as any settled count**; `test_labels__settled_count_never_renders_without_its_denominator_rule` asserts ancestor distance ≤ 2. Exit criterion 9. The external falsifier itself is `01` §6.3 item 8 |
| **F4** | FATAL (this document's share) | the sweep asserts "at least one guard fails" | **Every `guard_tests` list in this document is rewritten into the `01` §2 shape with a `flips:` value per guard** — NC-A06–A15, NC-A30–A32, NC-A09, NC-CI10–CI12, NC-X06–X08, NC-N08. Two injectors were widened so they reach every guard they are paired with (`unregistered_surface` now adds **both** a template and a response model; `generic_remedy_fallback` installs a remedy that is **both** generic and wildcard) rather than leaving a guard permanently unobserved. Where a guard genuinely cannot be reached it is declared `flips: false` **and says why** — NC-A07's registry guard, NC-X07's terms-row guard. Exit criteria 4 and 8 require `guards_flipped == guards_expected_to_flip` |
| **F31** | SERIOUS (this document's share) | DoD C4 is a paste only its author can verify | §5's C4 bullet rewritten: evidence is **`reports/negative-control-sweep.json`'s rows at the merge commit**, not a pasted line; C3 carries all four integers. Exit criteria 4 and 8 restated |
| **F27** | SERIOUS (this document's share) | id collisions, including this document's `NC-N40` against `02`'s | **superseded by arbitration C9**: there is one registry, in `01` §2, and this document allocates nothing. The contested `NC-N07` is **RETIRED**; this document's entry became **`NC-N40`** and `02`'s became **`NC-N16`** — *both* moved, because a rename that lets one side keep the contested id hides the collision instead of repairing it. §0.4(d)'s four greps get **real catalogue ids** — `NC-CI10`, `NC-CI11`, `NC-CI12` — with full entry shapes in B1, B2 and B3, closing three orphan guards (`test_nc__CI1/CI2/CI3` belonged to no entry and sat one character from `02`'s `NC-CI01`). Exit criteria 4 and 8 require `ci/catalogue-ids.sh` green |
| **F30** | SERIOUS (E4's share) | a pre-registered criterion that must be interpreted after the result is not a criterion | P15's exit criterion 1 states `beats_authoring` **as arithmetic**, and `test_contract__preregistration_criterion_is_machine_evaluable` (`01` §1.9) makes the lock refuse a criterion `decide()` cannot consume |

### Decisions taken here that the plan did not contain

- **DECIDED — the P4 measurement file is `docs/measurements/P4-harvest-distribution.md`**, one file, both
  arms, referenced by module constant. Beat: two files, one per arm. (F29)
- **DECIDED — `labels.SCAN_ROOTS` ships at P0 as `("src/cdfc",)` and is extended by P14-B1**, and it is the
  only scan set. Beat: leaving `01` §5.4's four directory names and creating empty `templates/`,
  `locales/`, `static/` at P0 to satisfy the grep — rejected because a scan root that exists only to
  satisfy a scan root is a gate scanning nothing. (F28)
- **DECIDED — `surface/library.py` and `surface/funnel.py` are promoted to mutation Tier V (`K/V ≥ 0.90`)**,
  §0.4(c), with the argument §3.5 requires. It is a raise, so §3.5's lowering rule is not engaged. (F1,
  F9, F18)
- **DECIDED — `substitute_measurement` becomes a required catalogue field on every `injector: NONE` entry**,
  and the three in §3 plus NC-N08 are filled in. Beat: leaving the substitute in prose beneath the entry —
  rejected because DoD line C6 is checked against the catalogue, not against the document. (F31's discipline
  applied to C6)

### Ids this document references, after the pass

> **THE BLOCK TABLE THAT STOOD HERE IS DELETED, AND SO IS THE WORD *DEFINES*. Arbitration C9.** It was one
> of four mutually inconsistent band tables (`02` R5a, `04` §0.8, `05` §4, this one), and the block it
> claimed — `N07–N10` — **collided with `02`'s `NC-N07`**, each document instructing the other to move.
> **The single allocation now lives in `plan/01-validation-methodology.md` §2, THE CANONICAL NC- REGISTRY**,
> which is the sole place an `NC-` id may be *defined*. This document *references* ids.
>
> **What C9 renumbered here:** this document's `NC-N07` (an all-clear mark drawn as vector paths, a raster
> image or a ligature) → **`NC-N40`**. `02`'s entry of the same number (a field observation quietly
> dropped) → **`NC-N16`**. **`NC-N07` is RETIRED PERMANENTLY and is never reassigned** — neither side keeps
> it, which is why the old instruction *"`02` renumbers, this document keeps `N07`"* is gone rather than
> reversed.

Ids whose detail lives in this document: `NC-A06`–`A15`, `NC-A30`–`A32` · `NC-X06`–`X08` ·
`NC-CI10`–`CI12` · `NC-N08`–`N10`, **`NC-N40`**. Every one has a row in `01`'s registry;
`ci/catalogue-ids.sh` and `test_nc_meta__ids_are_defined_in_the_registry` assert it, and
`test_nc_meta__no_dangling_reference` fails the build on any reference to a RETIRED id.

### Not repaired here, and why

**F5**, **F13**, **F16**, **F17**, **F23**, **F24**, **F25**, **F36**, **F38** are closed in
`plan/01-validation-methodology.md`, which this document owns jointly; they are recorded there.
**F6**, **F8**, **F10**, **F14**, **F20**, **F21**, **F26**, **F32**, **F34**, **F35**, **F37**,
**F39**–**F44** are attributed to `00`, `02`–`06`. Where their repair reaches a surface defined here the
hook exists and is named above — F1's `claims_fault_classes`, F18's `I`, F9's `skipped`, F3's
`instrument_label`, F12's `RESTRICTED`, F15's `denominator_rule` are all **surface obligations that assume
the upstream repair lands**, and each will render as a missing field rather than as a wrong number if it
does not. **F33** is not repaired anywhere, by agreement with the finding.

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C2** — F9's disposition | the **unqualified** `harvested_predicates_with_an_obligation / 280 = 0/280` — *wrong by 280* under the arbitrated mechanism — is replaced by the **pair**, rendered together or not at all (`test_surface__both_obligation_counts_render_or_neither_does`, `UnpairedObligationCount`), with the honest sentence rendered verbatim beside them | P14-B3 funnel item 3 · P14 exit criterion 9 · F9 row |
| **C9** — the catalogue | **this document's block table is deleted, and so is the word *defines*.** `NC-N07` → **`NC-N40`** (`02`'s → `NC-N16`; `NC-N07` **RETIRED**) — *both* sides moved, so the old "`02` renumbers, this document keeps `N07`" instruction is gone rather than reversed. `NC-L01`, referenced here and defined nowhere, is now registered in `01`. Band-conformance criteria repointed to the registry meta-tests | §0.4(d) · P15-B3 §3 · P14 exit criterion 8 · §ids-this-document-references · F27 row |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
