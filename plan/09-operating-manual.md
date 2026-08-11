# 09 — THE OPERATING MANUAL
## Front matter for the build plan · how to use it, where it stands, where it starts · compiled 11 August 2026

**This document is the front matter and the operating manual for the plan in `plan/00`–`plan/07`.** It
adds no phase, moves no gate, and decides nothing that a binding document already decided. What it does is
make the plan *operable*: the loop an engineer runs, the honest state of the world on the day the first
line is written, the first three builds with their commands, the full list of every number this programme
will produce, the log that records why each decision was taken, the questions that block a phase, and the
directory tree that exists when it is finished.

**Binding order, unchanged.** `00-decomposition.md` fixes phase ids, ordering, the dependency graph, the
gates and the one number per phase, and **may not be re-decomposed**. `01-validation-methodology.md` fixes
the test taxonomy, the negative-control catalogue, the mutation regime, the Definition of Done, the CI
pipeline and the test-data strategy. `02`–`07` specify the phases in full. `spec/00`–`05` say what the
system is, with `spec/05-audit.md §V.7` treated as binding and recent. **Where two of them name the same
thing differently:** `01` §0.4 wins for *file* names, `00` §5 wins for *package* names (`plan/02` R1).
Where a detail document decides something the spec left open, that decision governs its own phase and gets
a one-page record under `docs/decisions/`.

**No dates anywhere in this document.** Order, dependency and trigger only. Two things in the plan are
bound by a human calendar rather than a compiler, and they are named in §3 and §6.

---

# §1 — HOW TO USE THIS PLAN

## 1.1 The unit of work is the BUILD, not the phase

A phase is a question. A build is a day to four days of work with a named module, a named test set, a
named negative control and a filled Definition of Done. There are sixteen phases and roughly sixty builds.
**One filled `docs/DOD-TEMPLATE.md` per build, pasted into the pull request description** — not per phase,
not per sprint, not per module (`01` §4).

## 1.2 Picking up a build

1. **Read the phase's entry criteria** in its detail document, and check them against the repository rather
   than against memory. An entry criterion that names another phase's *published measurement* is satisfied
   by the file existing in `docs/measurements/`, not by the code existing.
2. **Check the barriers.** Five points in this plan mark work that is *forbidden*, not inadvisable
   (`00` §4.2): no fraction before the denominator has been computed twice by independent code paths; no
   kill rate, no observability filter and no `TEMPLATE_DIFF` before the evaluator reproduces the cached
   values; no predicate evaluated against a filing unless it loaded from the registry with a
   `qualification` block; no FFR digit on any surface, API response or attestation before a
   non-`SELF-AUTHORED` corpus exists; and no line of L3 before `experiments/E6/DECISION.md` exists. Each is
   enforced by a test or by CI, so a barrier violation is a red build, not a conversation — **but knowing
   which barrier you are near tells you which of your instincts to distrust today.**
3. **Copy `docs/DOD-TEMPLATE.md` into the PR description before writing code.** Sections A, D and H are
   answerable at the start and get worse the later they are attempted. If you cannot state in section D
   what number this build will produce and what its denominator is, you have not understood the build.

## 1.3 The per-build loop

This is `01`'s appendix, expanded with where each step's artifact lands.

| # | Step | Artifact it produces |
|---:|---|---|
| 1 | Write the code and the tests | `src/cdfc/…`, `tests/…` |
| 2 | For **each** test ask: *what specific broken build would make this go red?* If you cannot name one, the test is not evidence — go back to 1 | (nothing; this is the step that saves the rest) |
| 3 | Add the break to `tests/negative/catalogue.yaml` with an injector under `tests/negative/injectors/` | catalogue row + injector |
| 4 | `make nc-sweep`; **paste the failing assertion line into DoD line C4** | `reports/negative-control-sweep.json` |
| 5 | Give every rejection-side control an **admission-side positive control**, or the gate is reject-everything and scores perfectly on the negative control alone | a second test, named `…b` |
| 6 | Emit one number that did not exist before, with its denominator, its warrant label and the command to re-run it | a row in `reports/validation-ledger.jsonl` |
| 7 | `make mutation-pr`. Report `K/V` **first** — it needs no equivalence judgment — then `K/(V−E)` with `E` and its published arguments. **Never a bare percentage** | `docs/EQUIVALENT-MUTANTS.md` entry per survivor |
| 8 | Fill the DoD. Any line whose evidence is a *claim* rather than a path or pasted command output is not done | the PR description |
| 9 | In DoD §H write, in your own words, what this build does **not** establish | the PR description |
| 10 | Push. CI runs the thirteen stages of `01` §5.3 in order, under a 12-minute budget | `reports/` |

**Step 2 is the whole method and step 9 is the whole culture.** A build that cannot name its own residue
has not been understood by the person who built it.

Three DoD deltas apply to particular phases and a reviewer should look for them first: **§J** (four extra
lines) for P9–P11, per `plan/05` §6 — and inside it **J3**, that a *ceiling* is published **before** its
delta on the same page, because a bound published after its delta reads as an excuse and the same bound
published before it reads as a measurement. And for P14/P15, `plan/07` §5 puts the load on **C4** (the
pasted red assertion, not a screenshot), **C6** (an "impossible" control with no substitute is a skipped
line), **D7** (a median with both `n`s, never a mean and never a bare ratio) and **H1**.

## 1.4 The daily loop

| When | Command | Budget |
|---|---|---|
| Before touching anything | `make lint licence greps contract` | under 1 minute — this is why the stages are ordered free-before-cheap-before-expensive |
| While building | the loop in §1.3 | — |
| Before pushing | `make unit property golden differential nc-sweep determinism` | ~10 minutes |
| On the PR | the thirteen CI stages | under 12 minutes |
| Nightly, unattended | `make nightly` — deep property at 1000 examples, full mutation, the D4 LibreOffice differential, the transfer sweep over the nine, the instrument-watcher diff | ≤ 90 minutes |
| Weekly, by hand | the corpus lane's filled count; the standing absences in `docs/FIELD-OBSERVATIONS.md`; the growth log of `tests/negative/catalogue.yaml` | 10 minutes |

The weekly item is not administration. The corpus lane's count is the plan's actual critical path (§3.4).
A standing absence that stops being looked at has become silence, which is the one failure mode this
project exists to refuse. And the *rate at which negative-control entries are added late* is the only
instrument we have on the catalogue's own completeness (`01` §7.6) — **report it; never claim it
converges.**

## 1.5 Closing a build, and closing a phase

**A build closes** when the DoD is filled, every line's evidence is a path or a pasted command output, CI
is green, and a reviewer who did not do the work has read it. **The reviewer's rule is one sentence:** any
line whose evidence is a claim rather than a path or a pasted command output is not done. **C4 is the
load-bearing line** — an engineer who cannot paste the assertion that went red has not built a negative
control, they have written a second test.

**A phase closes** when its exit gate evaluates TRUE. Two properties of that gate, and both matter:

- **The gate is a boolean, and it is evaluated by reading `reports/` and `docs/measurements/` after a green
  CI run — never by reading a diff** (`01` §5.1: *the pipeline is the phase gate*). Every phase's exit gate
  in `02`–`07` is written as a numbered list of conditions each of which names a command or a file.
- **The person who evaluates it is not the person who built it.** Every exit gate in the detail documents
  carries the phrase *"evaluable by someone who did not do the work"*, and that is a staffing requirement,
  not a style note. Where the plan is run by one engineer, the evaluation is done against the written
  conditions on a different day, with the conditions read first and the artifacts read second — and
  `docs/OWNERS.md` records who did it.

On phase close: publish the phase's measurement document under `docs/measurements/`, append its rows to
`reports/validation-ledger.jsonl`, update `ci/GATES.md` and `docs/GATE-LIVENESS.md` if a gate moved
(`docs/GATE-CHANGES.md` records why), and tag. `tests/test_validation_ledger.py` asserts the ledger grew by
at least one row since the previous phase tag — **a phase that produced no new number has not met the
standard, and under rule R3 it was not a phase.**

## 1.6 What to do when a gate fails

Every gate in `00` §6 has a pre-registered failure branch, and **every branch produces a smaller system
that still ships.** There is no gate in this plan whose failure produces a stall. When a gate fails:
take the named branch, write the downgrade into the phase's measurement document *in the words the gate
specifies*, and make the downgrade render on the surface it affects. Do not renegotiate the threshold. **A
criterion revised after seeing the result is not a criterion**, and for the one gate where this temptation
is strongest — G-SETTLE — the arguments that will not be accepted as grounds for changing it are hashed
into the pre-registration file before the first API call.

---

# §2 — THE STATE OF THE WORLD RIGHT NOW

Stated under the spec's own ruling: every number carries its warrant, and *"we looked and could not settle
it"* is a legitimate and required answer.

## 2.1 What is BUILT — seven harnesses, all on disk, all runnable

Interpreter for every one of them: `/Users/abishaikc/Gift/.venv/bin/python`.

| Harness | What it produces, on disk | Warrant |
|---|---|---|
| `/Users/abishaikc/Gift/research/scripts/wb_probe.py` | `probe_out.json` (102 KB), `probe_full.txt` — the structural probe and a partial L1 induction | MEASURED |
| `/Users/abishaikc/Gift/research/scripts/predicate_harvest.py` | `predicates.json` (164 KB) — **280 FME / 515 across nine**, in nine classes, **no model** | MEASURED, harvest **v0** |
| `/Users/abishaikc/Gift/research/scripts/l4_mutation_harness.py` | `l4_result.json` — **19,782 mutants, 3,574 killed, 22 equivalent, 2.5 s, 7,946 mutants/s** | MEASURED |
| `/Users/abishaikc/Gift/research/scripts/true_coverage.py` | the settled-fraction **denominator**: field surface **3,747** on the FME workbook | MEASURED |
| `/Users/abishaikc/Gift/research/scripts/foundation_probe.py` | §0 of `plan/02` — the reproduction table and the eight new measurements N1–N8, four of which change a gate | MEASURED, 11 Aug 2026 |
| `/Users/abishaikc/Gift/research/scripts/e6_power.py` | the exact binomial power table for the settling experiment; corrects the spec's `P(X ≤ 2 \| n=20, p=0.30) = 0.036` to **0.035** | MEASURED, exact integer arithmetic |
| `/Users/abishaikc/Gift/tools/probes/` — `p9_precedents.py`, `p9_fn_census.py`, `p9_unlocked_formulas.py`, `p9_d17_defect.py` | **957** field-surface cells feeding ≥1 template formula (`TEMPLATE_DIFF`'s ceiling), **2,790** recompute-blind, **8** formula cells overwritable without stripping protection, function vocabulary **9 not 8** (`_xlfn.SINGLE`), and the `D17` defect located exactly | MEASURED, 11 Aug 2026 |

One negative result already on disk and load-bearing: inside `l4_mutation_harness.py`, **five ALR bounds
asserting only `≥ −1e17` over 1,428 cells were refused.** It is the gate's one demonstrated rejection, on a
workbook that is not the FME workbook, in one predicate class.

## 2.2 What is BUILT of the product itself

**Nothing.** There is no `src/`, no `tests/`, no `ci/`, no `Makefile`, no `pyproject.toml`, no `LICENSE`.
The git repository at `/Users/abishaikc/Gift` has **zero commits** — verified, `git log` returns *"your
current branch 'main' does not have any commits yet"*.

## 2.3 What exists as environment and input

- **The nine prescribed workbooks**, at `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx`
  — **not yet vendored into the repository.** P0-B2 copies them byte-for-byte into `fixtures/prescribed/`
  with a manifest that fails on drift.
- **`/Users/abishaikc/Gift/.venv`** — the research interpreter: `lxml` 6.1.1, `openpyxl` 3.1.5, and
  **`formulas` 1.3.4 (EUPL 1.1+)** and **`pycel` 1.0b30 (GPL-3.0)**, *both on the licence denylist*. This
  venv is a **FIXTURE** (`plan/02` R8): it is the licence gate's live negative control and requires no
  injector. **Do not clean it.** If it is ever cleaned, the control switches to the committed
  `site-packages` listing at `fixtures/licences/`.
- **`spec/`** (six parts, 435 KB) and **`plan/`** (this document plus `00`–`07`, ~1.0 MB) — the written
  system. `research/lanes/`, `research/synthesis/` and `research/scripts/` carry the evidence beneath them.

## 2.4 What is SPECIFIED AND NOT BUILT

Container guard · dual-reader agreement · template binding · predicate selection · pre-flight key check ·
the eight-state / thirty-code verdict model · closure · the CEL substrate · the five gates as a pipeline ·
the registry · the clean corpus · differential probes · run-time canaries · the residue set · attestation ·
`verify` · L1b · L3 · L2b · the watcher · every surface.

## 2.5 What is MEASURED — and the ruling on it

**Of the sixteen numbers this plan exists to produce, zero exist.** Every MEASURED number in the spec and
in `plan/02`–`07` is a property of *the regulator's blank template* or of *research-grade scripts run
against it*. **No number in this programme has been produced against a filing, because no filing exists in
the corpus** — the first non-synthetic input arrives in the corpus lane, not in the engineering lane
(`plan/02` §Z.5).

Five statements must never be restated without their real warrant:

| Statement | Its real status |
|---|---|
| *"L1→L5 runs end-to-end"* | **Dead.** On the ban list |
| *"Zero model calls in the verdict path"* | A **design property with a build gate specified and not yet written.** It becomes a system property the day `test_no_model_in_verdict_path` exists (P13-B0), and not before. Even then it licenses only *zero model calls on the verdict path per filing* — never *no model influenced this verdict* (`01` §7.13) |
| *"2,235 register GETs (MEASURED)"* | **Withdrawn to UNRECONCILED** (audit §V.7.4). The fetch plan is quoted in its form — `1 list request + N detail requests` — never as an integer, until a re-fetch records one in the manifest |
| *"63.3% settled"* / any settled-fraction headline | **PRE-GATE.** It is computed from 280 predicates of which **none is admissible** under our own gate, because no false-failure rate has been measured for any of them. **The currently defensible settled fraction is 0%, and we say so on stage** |
| *`MS = 18.09%` from `l4_result.json`* | Computed as `K/(G − equivalent)`, which is **the wrong denominator under this specification**. Every arithmetic operator killed at exactly 18.1% — identical to the fraction of sites inside the field graph — so for identity predicates that figure is measuring predicate **reach**, not predicate **quality**. P6 replaces it with `K/O` and says which it is showing |

---

# §3 — THE FIRST WEEK, CONCRETELY

Development starts at **P0-B1**, and there is no ambiguity about it: P0's entry criteria are *"none, this
is the root."* Three builds run in dependency order in the engineering lane. Two zero-code items launch on
the same day in their own lanes and never enter the engineer's day count.

## 3.1 Why this order and not another

B3 (the commitment gates) is the substantive build and the temptation is to start there. It cannot start
first: nine of the sixteen gate rows are **greps over directories**, and a grep over a missing directory
passes trivially — which is exactly NC-D01's mechanism applied to CI. B1 creates the scan roots so the
missing-root rule (`plan/02` R5) has something to be tested against, and creates the lockfile the licence
gate resolves. B2 must precede B3 because B3's negative-control machinery is exercised against real
artifacts and because the licence gate's live control is asserted through a committed fallback listing that
B2 records.

## 3.2 BUILD P0-B1 — repository skeleton, licence, pinned toolchain · 1.0 day

```bash
cd /Users/abishaikc/Gift
git status                       # expect: on branch main, no commits yet

# LICENSE is Apache-2.0, verbatim, and it is THE FIRST FILE COMMITTED (spec G9).
# It carries a patent grant and every core dependency chosen is compatible with it.
git add LICENSE NOTICE && git commit -m "LICENSE: Apache-2.0"

# the build interpreter is NOT the research venv; .venv-cdfc/ is gitignored, .venv/ is a fixture
python3.12 -m venv .venv-cdfc
.venv-cdfc/bin/python -m pip install uv
.venv-cdfc/bin/uv pip compile pyproject.toml --generate-hashes -o requirements.lock
.venv-cdfc/bin/uv pip install --require-hashes -r requirements.lock

make lint licence greps          # the first three CI stages, under 40 s total
```

Then the four checks that make the build real:

```bash
.venv-cdfc/bin/cdfc --version    # -> "cdfc 0.0.1 (schema <sha8>, gates 16)"
.venv-cdfc/bin/cdfc harvest      # -> exit 2, "not implemented at phase P0"; a stub that exits 0 is an all-clear
.venv-cdfc/bin/pytest tests/unit/test_cli.py tests/contract -q
.venv-cdfc/bin/pytest tests/determinism/test_det__lockfile_is_hash_pinned.py -q
```

The `pyproject.toml` block that is non-negotiable — `xfail_strict = true` and
`filterwarnings = ["error"]` — is one line of configuration standing between this project and the exact
signal that produced its flagship finding: *openpyxl's "Data Validation extension is not supported and will
be removed"*. `NC-CI02` proves it, by loading the FME workbook through `openpyxl` and asserting the
`UserWarning` **raises**.

## 3.3 BUILD P0-B2 — the nine real artifacts, vendored and content-addressed · 0.5 day

```bash
cd /Users/abishaikc/Gift

# 1. prove the probe still reproduces, on the research interpreter, before anything moves
.venv/bin/python research/scripts/foundation_probe.py
#    expect 505 / 294 / 211, 35 + 19 = 54, 252 merged ranges, field surface 3,747,
#    and N1-N8 including: 505 cached values that are 301 numeric zeros and 204 copies of "NA",
#    with not one non-zero numeric value among them

# 2. vendor the corpus, byte for byte
mkdir -p fixtures/prescribed fixtures/licences tools/measure
cp /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx fixtures/prescribed/
shasum -a 256 fixtures/prescribed/*.xlsx     # nine values; compare against methodology §0.3

# 3. record the licence-gate fallback fixture BEFORE anyone can clean the research venv (R8)
.venv/bin/python -m pip list --format=freeze \
  > fixtures/licences/research-venv-sitepackages__20260811.txt

# 4. promote the probe and freeze its output
cp research/scripts/foundation_probe.py tools/measure/foundation_probe.py
make measure-foundation          # rewrites docs/measurements/P0-foundation-probe.md;
                                 # exit 1 if it differs from the committed copy without --update
make corpus-verify               # re-hashes all nine against MANIFEST.json; exit 1 on any drift

.venv-cdfc/bin/pytest tests/golden/test_fixture_integrity.py tests/determinism -q
```

`test_fixture_integrity` asserts every `sha256` **and** every byte count **and** — rule R-GOLD-2 — at least
one *value* per file: for FME, `'3. Portfolio'!O3` materialises to `SUM(C3:N3)` with `ref="O3:O12"`; for
`ALR_V2_3`, one of the five `≥ −1e17` bound formulas verbatim. **A golden test asserts values, not only
counts**, because a defective matcher already produced a correct count and wrong bodies in this project's
own corpus.

## 3.4 BUILD P0-B3 — the commitment gates, written first and demonstrated to fail · 2.0 days

```bash
cd /Users/abishaikc/Gift

make greps                       # must pass CLEAN on a near-empty tree, and NC-CI01 proves that a
                                 # MISSING scan root fails while an EMPTY one passes

# the licence gate's live negative control: no injector needed, two denylisted packages are installed.
# The canonical form is the guard test; it resolves the gate against the research interpreter and
# falls back to the committed site-packages listing if the venv is ever cleaned (R8).
.venv-cdfc/bin/pytest \
  tests/negative/test_nc_licence.py::test_nc__L01_gate_fails_against_the_research_venv -q
#   asserts a NON-ZERO exit that NAMES both `formulas` and `pycel`

make nc-sweep                    # -> reports/negative-control-sweep.json
                                 #    caught / active / none_count as THREE INTEGERS, never a percentage
.venv-cdfc/bin/pytest tests/negative -q
make mutation-pr                 # src/cdfc/measure/absence.py, Tier S, K/V >= 0.70, four census terms

cat docs/GATE-LIVENESS.md        # one row per gate: date, injector, and the PASTED failing assertion
```

**The number this produces is `gates_live / gates_written = 15 / 15`, with **3** of the **18** rows of
`ci/GATES.md` `PENDING` and each naming the phase that makes it demonstrable** (row 14 → P2, row 15 → P11,
row 16 → P13-B0). Denominator **18**. Warrant **MEASURED**. The pre-registered sets are
`LIVE = {1…13, 17, 18}` and `PENDING = {14, 15, 16}`, both literals in
**`test_contract__live_set_is_pre_registered`** (`plan/02` R5, arbitration **C4** — this line previously
read `12 / 12` over 16 rows with 4 pending, which counted the predicate-loader admission twin that R5 rules
is not a row).
**This quantity does not exist anywhere today: the specification lists the gates; not one of them has ever
been observed to fail.**

## 3.5 The two lanes that start the same day and are not builds

**P0-B4 — the field observations (0.5 day, no code on the critical path).** Two questions asked by a
**named** human on a recorded date: **E1** to IFSCA's Division of Investment Funds (*are these checks run
on receipt; how often is an FME return sent back; are filed returns obtainable?*) and **E1b** to
KFin / CAMS / Basiz (the written house NAV-tolerance question, verbatim from spec §IV.1.2). Plus
`docs/ABSENCE-SCOPE.md`, the written inclusion rule that closes risk R13 — **no absence claim ships with a
count before that file exists.**

```bash
$EDITOR docs/FIELD-OBSERVATIONS.md docs/ABSENCE-SCOPE.md
.venv-cdfc/bin/pytest tests/unit/test_field_observations.py -q
#   every row carries replied_on OR standing_absence_since; a row with neither fails the build,
#   and a standing absence renders "asked <date>, unanswered for N days" — never as silence
```

**P8-B1 — the blind-fill corpus lane. It starts now, and this is the single most consequential scheduling
fact in the plan.** It has **zero code dependencies**: it needs the blank template (on disk), the
regulation (public), and a person who has never seen the predicate set. It costs **15–25 person-days of a
different person**, it is bound by a human calendar rather than by a compiler, and **it becomes the
critical path the moment it is deferred past roughly day 70.**

```bash
# corpus/ is A SEPARATE GIT REPOSITORY. Nothing under src/ or tests/ reads it except through
# fixtures/corpus_manifest.json, and tests/test_corpus_firewall.py asserts it is not importable.
# No binding document fixes WHERE it lives; only that it is separate. `../gift-corpus` is this
# manual's choice and the only thing that must be true of it is that it is outside this tree.
git init ../gift-corpus
#   corpus/FILL-BRIEF.md   hashed and published BEFORE the first workbook is filled
#   corpus/SLICES.md       the held-out slice, DECLARED BEFORE the corpus exists — a slice chosen
#                          afterwards is a subgroup analysis and is labelled one on every surface
```

Starting it late is not a schedule error, it is an **evidence** error: the firewall is easier to hold the
earlier it starts, because there is less predicate set in existence to leak. **The longest pole in this
plan is not the code. It is the corpus.**

## 3.6 Closing P0

```bash
make lint licence greps contract unit property golden differential nc-sweep determinism perf mutation-pr e2e
cat reports/validation-ledger.jsonl
```

The exit gate is TRUE iff all seven of P0's conditions hold: `gates_live == gates_written`; every `PENDING`
row names a phase and none is permanently pending; `ci/licence-gate.sh` exits non-zero against the research
venv naming both packages; `make corpus-verify` green on all nine with one value assertion per workbook;
`docs/ABSENCE-SCOPE.md` exists and is non-empty; `docs/FIELD-OBSERVATIONS.md` carries E1 and E1b with a
named sender and a date sent; and gVisor's licence is either opened and recorded or the fallback boundary
is recorded in `docs/LICENCES.md` **and** flagged for the deployment surface.

---

# §4 — THE MEASUREMENT LEDGER

Rule R3 says a phase that produces no number is not a phase. This table is that rule made auditable: every
number this plan will produce, in phase order, with its denominator, the warrant it will carry once
produced, and the build that produces it. Each becomes one nine-field row in
`reports/validation-ledger.jsonl` (`01` §5.5), and `tests/test_validation_ledger.py` fails the build if the
ledger has not grown since the previous phase tag.

**PRI** = the phase's primary number under R3. **SUP** = a supporting number the detail documents added
because the primary alone would be quotable in a misleading form. **CEI** = a ceiling, which by DoD line J3
must be published *before* the delta it bounds, on the same page.

| # | Phase | Kind | The number | Denominator | Warrant when produced | Build |
|---:|---|:--:|---|---|---|---|
| 1 | P0 | PRI | CI commitment gates demonstrated **red** against a named broken build | **18** rows of `ci/GATES.md`, of which 15 `LIVE` (C4) | MEASURED | P0-B3 |
| 2 | P0 | SUP | Negative-control sweep: `caught`, `active`, `none_count` — three integers, never a percentage | active catalogue entries | MEASURED | P0-B3 |
| 3 | P1 | PRI | The reader-agreement matrix, each disagreement classified **definitional or instrumental** with its mechanism named | 8 fields × 9 workbooks = **72** | MEASURED | P1-B3 |
| 4 | P1 | SUP | `PERF-RECEIPT` and `PERF-GUARD` baselines | ms on the named machine | MEASURED | P1-B1/B2 |
| 5 | P2 | PRI | Field surface per workbook, with `computedTwiceAgreed` per workbook | **9** workbooks | MEASURED | P2-B2 |
| 6 | P2 | SUP | Templates for which **no** protection mask is derivable — converting the spec's assertion of "two" into a measurement | 9 workbooks | MEASURED | P2-B2 |
| 7 | P2 | SUP | Ambiguity rate of the naive `(sheet, label-above, label-left)` key | cells in the used ranges | MEASURED | P2-B3 |
| 8 | P3 | PRI | Cached-value reproduction, **arm 1**, published with the label `NON-DISCRIMINATING` and the 301-zeros / 204-`"NA"` / **0 non-zero** census attached | **505** (FME) and **1,495** (nine) | MEASURED | P3-B4 |
| 9 | P3 | PRI | Cached-value reproduction, **arm 2** — the discriminating rate, with its disagreement set beside it | \|non-trivial cells\| | MEASURED | P3-B4 |
| 10 | P3 | SUP | Formula cells per workbook that actually carry a cached value — the audit of arm 1's own 1,495 denominator | 9 workbooks | MEASURED | P3-B4 |
| 11 | P4 | PRI | **`schema_keys` both-ways agreement** — candidates whose declared key set equals their AST-read key set | **280** FME candidates | MEASURED | P4-B2 |
| 12 | P4 | PRI | **The per-workbook distribution of the 515 figure**, with the skip counts beside it | **9** workbooks | MEASURED | P4-B4 |
| 13 | P4 | SUP | CEL agreement on the admitted subset, and **separately** on the error-semantics slice, per runtime | expressions in the suite / harness | MEASURED, labelled `CONFORMANCE` **or** `DIFFERENTIAL` | P4-B3 |
| 14 | P5 | PRI | The **runtime** seven-term closure partition, and the runtime settled count's **delta from the static 2,373** | **3,747** cells | MEASURED | P5-B4 |
| 15 | P5 | SUP | `keys_type_checked / keys_preflighted` per run — a type check that did not happen is never reported as one | keys pre-flighted | MEASURED | P5-B1 |
| 16 | P5 | SUP | Cells whose state was **lowered by roll-up** — the audit §V.7.1 resolution's effect size | cells with ≥1 `PASS` and ≥1 non-`PASS` | MEASURED | P5-B4 |
| 17 | P6 | PRI | **`U/G` for our own operator mix**, and `K/O` per fault class | generated mutants `G`, per class and total | MEASURED | P6-B3 |
| 18 | P6 | SUP | Throughput against the **7,946 mutants/s** baseline; must not regress by more than 2× | mutants/s | MEASURED | P6-B2 |
| 19 | P7 | PRI | **The five-gate attrition funnel**, stage by stage, every rejection with its gate and its measured number | **280** harvested FME predicates (19 for ALR, published beside it) | MEASURED | P7-B4 |
| 20 | P7 | SUP | Disposition of the **five non-`0` FME bounds** covering 68 cells, with a measured `K/O` — unclassified anywhere in the corpus today | 5 bounds / 68 cells | MEASURED | P7-B3 |
| 21 | P8 | PRI | **The first FFR measured on a corpus its authors did not write**, per predicate as `(fired, n, wilson_lo, wilson_hi, corpus_id, corpus_provenance)` | **`n` filings — never cells** | MEASURED | P8-B3 |
| 22 | P8 | PRI | The **post-gate** settled count against the pre-gate 2,373, with the admitted count by severity tier | 3,747 cells / 280 predicates | MEASURED | P8-B3 |
| 23 | P8 | SUP | The exact `BLOCKING` threshold at zero fires — **`n = 189`**, correcting the spec's *"roughly 185"* | Wilson upper bound at `z = 1.959963984540054` | **DERIVED** (exact arithmetic) | P8-B4 |
| 24 | P9 | **CEI** | Field-surface cells feeding ≥1 template formula — **`TEMPLATE_DIFF`'s ceiling = 957** | 3,747 | MEASURED, 11 Aug 2026 | pre-measured, `tools/probes/` |
| 25 | P9 | SUP | Field-surface cells feeding **no** template formula — the recompute-blind set = **2,790** | 3,747 | MEASURED, 11 Aug 2026 | pre-measured |
| 26 | P9 | SUP | Formula cells a filer can overwrite **without stripping protection** = **8** | 505 formula cells | MEASURED, 11 Aug 2026 | pre-measured |
| 27 | P9 | SUP | Function vocabulary of the FME workbook = **9, not 8** (`_xlfn.SINGLE` at `'1. Introduction'!D92`) | 505 formula cells | MEASURED, 11 Aug 2026 | pre-measured |
| 28 | P9 | SUP | Relations structurally un-runnable on any obtainable filing | **25** relations | MEASURED at catalogue time | P9-B2 |
| 29 | P9 | PRI | **Per-relation before/after settled-count delta**, including the relations that moved nothing, reported as moving nothing | 25 relations / 3,747 cells | MEASURED | P9-B4 |
| 30 | P10 | PRI | **`\|RESIDUE\|`** — WRONG mutants no admitted predicate and no admitted relation rejects — with its fault-model version, its adjudication-record hash, and each survivor's class of falsehood | WRONG mutants generated | MEASURED | P10-B2 |
| 31 | P10 | SUP | **Deaths caught / deaths injected** — the number the whole liveness claim rests on | **6** injected deaths | MEASURED | P10-B1 |
| 32 | P10 | SUP | Cohen's κ between two adjudicators on a pre-seeded 20% sample | mutants re-rated | MEASURED | P10-B3 |
| 33 | P10 | SUP | Canary + anti-canary wall clock on the reference run, **replacing the ≈70 ms DERIVED figure** | ms against a ~30 ms core | MEASURED | P10-B1 |
| 34 | P10 | SUP | Canary **inapplicability** rate on the reference template-computed clean filing | canaries attempted | MEASURED — expected **0**, and any other value is evidence about us | P10-B1 |
| 35 | P11 | PRI | **Byte-identity on a second machine** (bytes differing / bytes in the report, target 0), plus non-determinism sources **enumerated vs removed** — now five and five | bytes in the report | MEASURED | P11-B2 |
| 36 | P11 | SUP | Schema property names that trip the **advisory** substring scan, and how many are allowlisted with an argument | all property names at any depth | MEASURED | P11-B1 |
| 37 | P11 | SUP | Item states representable in the OSCAL projection — **the declared loss, as a count** | 8 item states | MEASURED | P11-B3 |
| 38 | P11 | SUP | Manifest pins checked by `verify` | 8 pins + 2 run-level inputs | MEASURED | P11-B2 |
| 39 | P12 | PRI | **`k of 20`** — Stratum-A obligations for which at least one candidate passes all five gates — **with its Wilson interval. The interval goes on the slide; the point estimate never** | **20** Stratum-A obligations | MEASURED | P12-B4 |
| 40 | P12 | PRI | **`\|A\| / \|drawn\|`** — the **decidable fraction of the instrument**, which nobody has, reported as two integers with both estimators under the inverse-sampling label | `\|drawn\|`, the full draw including all Stratum B | MEASURED | P12-B1 |
| 41 | P12 | SUP | The five-gate attrition funnel over the candidate set, **discards included** — the first published attrition funnel for model-proposed regulatory checks | **600** candidates | MEASURED | P12-B4 |
| 42 | P12 | SUP | Marginal kill over **each baseline separately** and over the union, at the equal-FFR comparability precondition | the shared observable set `O` | MEASURED | P12-B2 |
| 43 | P12 | SUP | The stratification's discriminative value, `k_A/20` vs `k_B/10` against a pre-registered expectation of 0–1 of 10 | 20 and 10 | MEASURED | P12-B4 |
| 44 | P13 | PRI | **Admitted predicates per 100 candidates, and per rupee, by model.** At `k = 0` this is `0 per 100` and `0 per rupee`, **and it is published** | 600 candidates | MEASURED | P13-B1 |
| 45 | P13 | PRI | **`μ`**, key-binding accuracy, with its forced-abstention floor `(μ−α)/(1−α)` | **`n = F` filings — never `3,755·F`** | MEASURED, **or `NOT_MEASURABLE`** with the reason and what would fix it | P13-B3 |
| 46 | P13 | SUP | Promoter **`shall` recall** against the recomputed denominator, with the reconciliation to the prior 8,866 / 361 figure | `<n>` circulars of 399 | MEASURED | P13-B2 |
| 47 | P13 | SUP | **Watch coverage** — observed days / elapsed days, with each gap's duration. *An unobserved day is not a quiet day* | elapsed days since watch start | MEASURED | P13-B4 |
| 48 | P14 | PRI | `surfaces_passing_all_four_gates / len(SURFACES)` — two integers, printed together, never as a percentage | the surface registry in `src/cdfc/surface/labels.py` | MEASURED | P14-B1…B4 |
| 49 | P15 | PRI | **Human minutes per transferred predicate**, against the from-scratch authoring baseline — a **median with both `n`s**, never a mean | ≥ **10** predicates on the CMI workbook `82dd291f…` | MEASURED | P15-B1 |
| 50 | P15 | PRI | The **per-template settled fraction for all nine, never averaged**, including the zeroes | **9** templates | MEASURED | P15-B1 |

## 4.1 This project's coverage declaration, applied to itself

**Denominator: 50 — the rows of the table above.** Six rows carry a value today: **957**, **2,790**, **8**
and **9** from `tools/probes/` (MEASURED, 11 Aug 2026); **`n = 189`** from the exact Wilson arithmetic in
`plan/04` §0.9 (DERIVED); and the **7,946 mutants/s** throughput baseline from `l4_result.json`
(MEASURED). **Six of fifty.**

**Of the sixteen phase-primary numbers, zero exist.** That is the honest statement of where this programme
stands, and it is exactly the kind of statement the product exists to make about someone else's filing.

Three properties of the table that are load-bearing and easy to erode:

- **Nine rows are rates, and a rate here never renders bare.** Rows 21, 39, 44, 45, 47, 48, 49 and 50 carry
  `corpus_id`, `corpus_provenance`, `n` and an interval, or they render `uninformative` (DoD lines D7/D8).
  `0 fires / 340 self-authored` and `0 fires / 4 real` must not be allowed to look alike: the Wilson
  intervals are `[0.000, 0.011]` and `[0.000, 0.490]`.
- **Four rows can legitimately come back as zero, and a zero is a result, not a failure:** row 19 (the gates
  may reject nothing on the FME workbook — that is a publishable measurement); row 29 (relations that moved
  nothing, reported as moving nothing); row 39 (`k = 0`); row 44 (`0 per 100` at `k = 0`).
- **Row 30 is the one that cannot come back empty without meaning something about us.** `|RESIDUE| = 0`
  contradicts a structural argument; the response is that the fault model is too weak, and the report says
  the residue is `0` **under fault model v3** with the operator list attached.

---

# §5 — THE DECISION LOG

## 5.1 The template

One page per decision, at `docs/decisions/D-<SCOPE>-<nn>-<slug>.md`. The log below is the **index**; each
record carries the argument.

```markdown
# D-<SCOPE>-<nn> — <one-line decision, in the imperative>

| field | value |
|---|---|
| **id**            | D-<SCOPE>-<nn> |
| **status**        | TAKEN | OPEN-WITH-RULE | SUPERSEDED-BY <id> | REOPENED-BY <evidence> |
| **taken**         | <date>, by <name> |
| **question**      | <the question in one sentence, as it was actually asked> |
| **decision**      | <imperative; what a reader must do differently> |
| **it beat**       | <the named alternative(s), each with the observation that beat it> |
| **because**       | <the argument, or the measurement, that settles it> |
| **blast radius**  | <what changes if this is reversed — files, gates, numbers> |
| **enforced by**   | <test path | gate id | grep script>; "nothing" is a valid and alarming answer |
| **re-open rule**  | <the SPECIFIC evidence that would re-open it. "None" is a valid answer only for
                      a decision that is a barrier; for anything else, "none" means it is a preference> |
```

**Two rules on the log itself.** A decision with no re-open rule is a preference, and must be labelled one.
A decision reversed with no new evidence is a **renegotiation**, and the log records it as one — with the
argument that was accepted, so that the next reader can see whether the criterion moved because the world
did or because we did.

## 5.2 Initial entries — the six load-bearing decisions

| id | Decision | It beat | Because | Enforced by | Re-open rule |
|---|---|---|---|---|---|
| **D-SPEC-01** | **The unit of the denominator, of closure and of the settled fraction is the CELL** — the filer-editable, unlocked, non-formula cell | the `(field × obligation)` pair | Every quantity actually measured is a cell count. The pair model's `obligationsTotal` and `pairsTotal` had **no derivation anywhere in the corpus** and appeared with **three mutually incompatible values** | the seven-term closure invariant as one `GROUP BY` over `run_cell` (P5-B4); `test_denominator_provenance` (P2) | A load-bearing surface quantity that is provably not expressible as a cell count |
| **D-SPEC-02** | **The predicate language is CEL, admitted subset only, inside a three-slot envelope** (`applicable` / `expr` / `witness`) | generated Python · Rego · VTL · Great Expectations | Non-Turing-complete and terminating, so a confused model cannot write a predicate that hangs or reaches the filesystem; readable by an auditor; mechanically mutable; **and the sandbox problem disappears rather than being contained** | `predicates/cel_profile.py`, `predicates/ast_walker.py` (both-ways check), gate **G-CELPY** | G-CELPY fails on **both** runtimes on error semantics *and* the narrowed grammar (banning `&&`/`\|\|` at the top level of `expr`) proves insufficient; **or** the both-ways check cannot be made exact, which relabels the settled fraction an *estimate* and re-opens the language decision with the measurement attached |
| **D-SPEC-03** | **L3 — the model — runs at build time, per template version, never per filing** | a model in the request path | Per-filing model cost is $0.00 and the report re-derives byte-identically; `pass^k` decay cannot apply to the verdict path by construction | `test_no_model_in_verdict_path` (P13-B0) — **until that test exists this is SPECIFIED, not a property** | None. A per-filing model call forfeits G-REPRO |
| **D-SPEC-04** | **A predicate with no qualification record does not load** | admitting hand-authored checks and measuring later | The settled-fraction claim is then true to the extent the admission measurements are valid, and each predicate carries the provenance of its own measurement. **It is also why the currently defensible settled fraction is 0% and we say so on stage** | `predicates/registry.py::load_or_refuse()` — raises unconditionally at P0-B3, gains its other branch at P4-B1; `test_unmeasured_predicate_rejected` | **None — this is barrier 3** |
| **D-SPEC-05** | **Eight closed item states, thirty namespaced reason codes; `cells_bound == 0` is an `ERROR` that makes the run `INVALID`, never a `PASS`** | the brief's single `UNCHECKED` token | A predicate that bound to nothing is the vacuous-pass failure the whole design exists to catch. Collapsing it into "unchecked" puts it in the same bucket as a rate-limited register | `verdict/states.py`, `verdict/reasons.py`; **D-P5-01** makes binding *precede* evaluation so the vacuous pass is **unreachable, not repaired** | None |
| **D-SPEC-06** | **The attestation's top-level object is `scope`; the schema has no `result`, `status` or `pass` field at any depth** | signing a verdict | A surface that can render all-clear will eventually render it wrongly. Prohibiting it **in the schema**, and grepping for it in CI, is the only version of that commitment that is a system property rather than a preference | `test_attestation_has_no_status_field` (recursive walk); JSON Schema `additionalProperties: false`; `ci/no-green-tick.sh` | None |

## 5.3 Initial entries — the post-audit resolutions (`spec/05-audit.md` §V.7)

| id | Resolves | Decision | Why it is *determined* rather than chosen | Blast radius | Enforced by |
|---|---|---|---|---|---|
| **D-AUDIT-01** | V.5.1 — cell-state precedence | **§II's order is normative:** `ERROR ≻ FAIL ≻ INDETERMINATE ≻ NOT_RUN ≻ PASS ≻ INFORMATIONAL ≻ OUT_OF_SCOPE`, and **a cell is clean only if every predicate binding it passed.** §III's `PASS ≻ INDETERMINATE ≻ NOT_RUN` is withdrawn | Both parts state that on reader disagreement every predicate reading the field returns `NOT_RUN(extractor_disagreement)` and *"the settled fraction falls, it does not silently succeed."* Under `PASS ≻ NOT_RUN` that sentence is **false in exactly the case it was written for.** A check that did not run must never be absorbed by one that did — that is the product, not a tie-break | The **runtime** settled count can now fall below the static figure: intended. The harvest figure **2,373 of 3,747** is unaffected — it counts cells reachable by ≥1 harvested predicate, computed before any evaluation | `evaluate/rollup.py`; `test_settled_fraction_falls_on_not_run`; ledger row 16 is its measured effect size |
| **D-AUDIT-02** | V.5.2 — the two different "five rules" | **The five rules are §II.3.4's:** `applicable` · pre-flight · `expr` · warrant composition · `cells_bound` | `EVALUATION-CONTRACT.md` is **generated** from §II.3.4 and a CI test asserts the evaluator's transition table **equals** it. §IV's alternative five was not wrong, but **a build cannot satisfy two fives** | The three rulings the drafts disagreed about now sit *inside* rules 1, 3 and 5; budget exhaustion is a sub-case of rule 2 | `tools/gen_contract.py` + the contract test at CI stage 3. **D-P5-01** records evaluation *order* as a separate explicit field, because the spec's numbering is conceptual |
| **D-AUDIT-03** | V.5.3 — the container guard's reason code | **Neither of the audit's two options: a category correction.** The 8 × 30 vocabulary is **per item, and an item is a cell.** Run-level `INVALID` causes become their own closed `invalid.*` vocabulary with exactly eight causes | A container-guard trip, a reader disagreement, an unbound template and a denominator disagreement are **not properties of any cell.** Forcing them into a per-cell code was the error, not the missing code | **The item-level count stays pinned at 8 × 30 in all four places**, so nothing pinned moves. Where a run-level cause has an item-level analogue (`.cells_bound_zero`, `.predicate_raised`) **both are carried; they are not alternatives** | `src/cdfc/verdict/invalid.py` — an addition to methodology §0.4 required by this resolution |
| **D-AUDIT-04** | V.6 — warrant discipline | **"2,235 register GETs (MEASURED)" is withdrawn to UNRECONCILED.** The fetch plan is quoted in its **form** — `1 list request + N detail requests` — never as an integer until a re-fetch records one in the manifest. **"Zero model calls in the verdict path"** is stated as *specified, with the CI gate listed and not yet written* — never in the present tense | It matches neither `1 + 650 = 651` nor `1 + 2,005 = 2,006`, no document states its `N`, and the run cannot be re-executed from the artifacts on disk. **This is the same rule the system applies to a filer, applied to the system** | Two numbers leave every surface and every README | `ci/no-bare-absence.sh`, `src/cdfc/measure/absence.py`, the ban list, and P13-B0 |
| **D-AUDIT-05** | V.7.5 — what remained open | **OPEN-WITH-RULE, three residuals, one of them now closed.** The `REJECTED` predicate state is **closed by D-P4-01: No** — `PredicateState` stays four-valued and a rejected candidate becomes a `rejection` row keyed by `candidate_sha256` with `predicate_id NULL`. **Still open:** the undefined *"511 cells"* in spec §III.5, and *"44.4% of raw candidates"* / *"68.9% of TOGA's bugs"* carried without their denominators | — | — | **Rule:** the two denominator-less figures may not appear on any surface or in any README until the denominator is recovered from the primary; `ci/no-bare-absence.sh` does not catch them (they are rates, not absences), so the guard is the `docs/README-NUMBERS.md` registry at P14. **"511 cells" resolves to one of {3,747 · 3,755 · 505} or it is struck; P2-B2 decides and records which** |

## 5.4 Decisions already recorded inside the plan documents

The log is an index, not a second copy of the argument. These sets are already taken and each acquires its
`docs/decisions/` page at the build that implements it:

| Where | What it decides |
|---|---|
| `plan/02` §1, **R1–R11** | Document precedence for file vs package names · the two manifests · the clock as a parameter everywhere · `calc/` in the `no-float-money` scan set · `ci/GATES.md` as the gate registry and P0's denominator · SQLite with one schema file and no migration framework · gVisor as a **deselect, never a skip** · the research venv as a fixture · the reader-competence matrix as code · effort assumptions |
| `plan/03` §0.3, **D-P4-01…05, D-P5-01…04** | No `REJECTED` state · the `schema_keys` grammar with the root restored · `matches()` banned from the admitted subset · the conformance fallback labelled `DIFFERENTIAL` · four mutation tiers · binding precedes evaluation · `INFORMATIONAL` carries no reason code but a mandatory note · pre-flight type inference with `type_checked: false` recorded · the two different nulls of `verdict` |
| `plan/04` §0.1–0.8 | `src/cdfc/qualify/` canonical · baselines built at P7-B3 and run at P12-B2 · `TEMPLATE-COMPUTED` as an entry criterion of P7-B3 · site universe vs primary arm vs control arm as three sets · mutants written by raw-zip surgery only · Z3 under a deterministic resource limit, never a wall clock · an unobservable mutant excluded from `O` and **retained on disk** |
| `plan/05` §0.1–0.4 | What cell a `TEMPLATE_DIFF` finding settles · the `kill_case` as a replayable witness, not a stored workbook · witness inapplicability is not a silent canary · the `pass_case` is replayed too and proves a different thing |
| `plan/06` §0.1–0.9 | `experiments/E6/` · the power table recomputed exactly with one published figure corrected · "one extension" means a **pooled** 40 · the Stratum-B cap is on generation, never on the denominator · the retain condition is a **conjunction** and its failure at `k ≥ 6` is DELETE · "equal FFR" is a comparability precondition, not a tuning knob · the watcher at `src/cdfc/watch/` · the extension's cost quoted in its form |
| `plan/07` §0.1–0.4 | `src/cdfc/surface/` as the rendering package · the pixel-level audit uses a real browser · P15-B4's dependency on P11 **surfaced rather than silently fixed** |

---

# §6 — THE OPEN QUESTIONS THAT BLOCK PHASES

Every row carries the phase it blocks and the decision rule that fires if no answer arrives. **A rule that
fires automatically is the point**: the failure mode this section exists to prevent is not a wrong answer,
it is a question quietly dropped because nothing depended on it.

## 6.1 The one question that blocks a phase

| Question | Blocks | Decision rule if no answer arrives |
|---|---|---|
| **Who is Person A?** *(spec §7 Q3 / G10; `plan/04` O4; `plan/07` O5.)* A named human, not on the build team, who will fill ≥ 30 FME workbooks from the template and the regulation alone, having **never seen the predicate set** | **P8 (gate G-CORPUS)** — and through it **P14-B4** and **every FFR digit on every surface, API response and attestation** (barrier 4) | **The audited second-model-instance route fires**, with the predicate-free fill prompt **hashed and published before the first workbook is filled**, `person_a_kind: "model-instance"` rendering **wherever the FFR renders**, and the record stating in writing that the fallback is **weaker than a human**. If neither is available: **G-CORPUS's fail branch, which ships** — no predicate is admitted, every FFR renders `uninformative`, `severity_tier` is undefined, `settledFraction: null` with an explicit statement that the admissible predicate set is empty. What still ships: the harvest, the verdict model, the closure invariant, the Unchecked panel, the canaries, the residue set, `verify` and the attestation. **The trigger is a start, not a deadline: the lane must begin on day 0 or it becomes the critical path past roughly day 70** |

## 6.2 The questions that block no phase but must never go silent

| Question | Blocks | Decision rule |
|---|---|---|
| **E1 — does IFSCA already run these checks on receipt?** *(spec §7 Q2; P0-B4)* | Nothing. It changes **phase priority** — P9, P10 and P11 rise; P14 and P15 fall — and not one line of architecture | If unanswered when P14 starts, **the non-answer ships as a visible open item on the report surface and in the claim register — never as silence.** `docs/FIELD-OBSERVATIONS.md` renders *"asked `<date>`, unanswered for N days"*, which is the watcher's `gap_since` rule applied to a human channel |
| **E1b — does a fund administrator serving GIFT IFSC have a written house NAV tolerance?** *(spec §7 Q5; P0-B4)* | Nothing | *Yes, written* → one paragraph of framing improves (*the threshold is private, uncomparable across administrators, and invisible to the supervisor*). *No* → nothing changes. **Either way it is no longer a killer** — the valuation wedge was deleted for five independent measured reasons and this question was demoted with it |
| **If `k = 0`, is the programme still run as specified?** *(spec §7 Q6)* | **P13** — and it must be answered **before P12's pre-registration hash is published**, not after | The plan is already written for it: `plan/06` §2 is the `k = 0` system in full. If the answer is *no*, P13 is re-planned **before** the pre-registration is hashed, because **a commitment made after seeing the result is not a commitment**, and a pre-registration whose consequence is renegotiable is not one |
| **Is anyone prepared to sign the attestation?** *(spec §7 Q7)* | Nothing in P11 — its acceptance test is byte-identical re-derivation, not legal effect | *No* → **the demo signs nothing real and says so on screen**; the attestation is exercised against a self-filled workbook and labelled a self-assessment exercise |
| **Q1 — the application portal** *(spec §7 Q1; E0)* | **RETIRED.** The deadline that made it the only programme-ending item no longer exists | Removed from the queue rather than deferred, **so nobody spends ten minutes on it out of habit** |

## 6.3 Licence and conduct items — two of these genuinely block

| Item | Blocks | Decision rule |
|---|---|---|
| **gVisor's licence is `NOT-FOUND`, and it is a runtime dependency** | **The one licence item that can block P1** | Open it, **or** record the `seccomp` + namespaces fallback in `docs/LICENCES.md` and print the weaker boundary on the deployment surface. **P1 proceeds either way — the guard's *checks* are not the guard's *confinement*** |
| **`SECONDARY`-warrant runtime licences: Z3 (MIT), Hypothesis (MPL-2.0 reported), cosign (Apache-2.0)** — none opened | **Advisory in P0–P1, BLOCKING from P2** | `docs/LICENCES.md` names who must open each. Unopened at P2, `ci/licence-gate.sh` fails the build. There are no permanent advisories: every advisory gate carries the phase at which it becomes blocking, in `ci/GATES.md` |
| **IFSCA's terms of use for the register API** — a gap in **conduct**, not code | Scheduled polling only: **P13-B4's automation and P15-B3** | `docs/TERMS-OF-USE.md` carries the row with `read: false`; `ci/no-scheduled-polling.sh` blocks scheduled polling while it stays false. **If the terms forbid polling, `polling_permitted: false` is a valid answer**: the watcher becomes manual with its gaps recorded — the product changes, **the gate does not acquire an exception** |

## 6.4 Constants with no argued basis — each renders a literal placeholder rather than a number

None blocks a phase. Every one of them is the same discipline: **we would rather print nothing than print a
number whose shape is evidence and whose content is zero.**

| Constant | Rule until an argument exists |
|---|---|
| `K` and `T` in `pervasiveness-policy-v1.json` *(spec §III.7 C22; `plan/07` O1)* | Render the literal string **`PLACEHOLDER`** on **every** surface and in **every** example. `verdict.state` is `null` with `stateWithheldBecause: "policy_placeholder"` (D-P5-04). The argument, when it comes, must be a written one about *pervasiveness* — **not a number chosen because it makes the reference filing look better** |
| `MAX_WITNESSES` *(`plan/05` §5.1)* | Run P10-B1 at `{1, 3, 5}` over the template-computed clean corpus, measure the **inapplicability rate** at each, take the smallest value at which it is 0 on the reference fill, publish the curve. Until then the code reads `MAX_WITNESSES = 3  # PROVISIONAL` and **the number is quoted nowhere else** |
| `POLICY_VALIDITY_DAYS = 92` *(`plan/05` §5.2)* | Renders `PROVISIONAL — no argued basis` in the attestation. An attestation expires when the thing it is a claim about can have moved; the two movers are the **template** and the **instrument stream**, and until the watcher exists there is no instrument event to read |
| `STALENESS_BOUND_DAYS` *(`plan/07` O2)* | `None` until **30** consecutive daily snapshots exist; then the 5th percentile of the observed inter-change interval, floored at 1 day, denominator 30, warrant MEASURED. Until then every register item degrades to `NOT_RUN(input_unavailable.register)` — **the conservative direction** |
| `implausible_magnitude` per dtype in `domain-policy-v1.json` *(`plan/04` O1)* | Renders `PLACEHOLDER`; while it does, G3's `proof_arm` returns `UNKNOWN` for every pure-bound predicate and routes it to the empirical arm. **It blocks nothing** |

## 6.5 Method-level items with a rule, carried so they are not rediscovered

- **`_xlfn.SINGLE`** *(`plan/02`)* — implement iff ≤ 20 lines with a passing unit vector; otherwise the
  affected cells are `NOT_RUN` and the count is published.
- **Arm-2 author independence** *(`plan/02`)* — if the human expectation author is a different person from
  the evaluator's author, arm 2 is a differential; if not, `docs/measurements/P3-evaluator.md` says
  **`SAME-AUTHOR — a weaker instrument`** in those words. **There is no third option and no silent one.**
- **The `1,495` corpus-wide denominator** *(`plan/02`)* assumes every formula cell in all nine workbooks
  carries a cached value. P3-B4 **measures it per workbook before quoting the ratio**; a workbook with
  uncached formula cells contributes only the cells that have an oracle, and the shortfall is published
  (ledger row 10).
- **The disposition of the five non-`0` FME bounds** *(`plan/04` O2)* — the phase measures rather than
  assumes: `test_golden__fme_nonzero_bounds_disposed` asserts a disposition **exists** with a measured
  `K/O`, not what it is.
- **Fault-class id numbering** *(`plan/04` O3)* — ids may shift, `F11` stays the formula-override class,
  and `docs/FAULT-MODEL-v3.md` carries a migration table from every id quoted anywhere in the corpus.
- **`docs/OWNERS.md`** *(spec §6 G11)* — one table, milestone × person × hours. Three items each need a
  **named human who is not the engineer**: Person A (P8-B1), the second adjudicator (P10-B3), the stratum
  assigner (P12-B1). **Rule:** the table exists before P8-B1's brief is hashed, before P10-B3 and before
  P12-B1's pre-registration. Absent a name, the human-latency item is recorded as `UNSTAFFED` with its
  duration and the number it would have produced renders **`UNMEASURED`, never absent.**

## 6.6 One conflict this document surfaces rather than silently resolves

**The database schema has two paths in two binding documents.** `plan/02` R6 says one `db/schema.sql`
applied by `cdfc init`, its `sha256` written to a one-row `meta` table and into the run manifest;
`plan/03` §0.2 adds `src/cdfc/store/` carrying `schema.sql` and `db.py`. `01` §0.4 names neither, so R1's
precedence rule does not decide it.

**Rule — `D-OPS-01`, decided at P1-B1, before P5 depends on it.** The phase that *creates* the file owns
the path, and P1 creates `blob` and `run`; therefore `db/schema.sql` is the file and `src/cdfc/store/db.py`
is the accessor module. Whichever is chosen, the invariant that matters is unchanged and is what the record
must assert: **`cdfc init` applies exactly one file, its `sha256` goes into the run manifest, and
`cdfc verify` fails on a schema-digest mismatch rather than attempting to adapt.**

---

# §7 — REPOSITORY LAYOUT AT PLAN COMPLETION

One line of purpose per top-level entry. This is `01` §0.4 with the additions each detail document made,
reconciled once, here.

```
/Users/abishaikc/Gift/
  LICENSE                  Apache-2.0, verbatim — THE FIRST FILE COMMITTED (spec G9); carries a patent grant
  NOTICE                   attribution stub for the vendored and depended-upon work
  README.md                the pitch; every number in it is registered in docs/README-NUMBERS.md or it fails CI
  Makefile                 every command in methodology §5 is a target; nothing in this project is run another way
  pyproject.toml           deps, pytest (xfail_strict, filterwarnings=["error"]), ruff, mypy --strict, mutmut
  requirements.lock        fully resolved, --require-hashes; every line carries at least one sha256
  EVALUATION-CONTRACT.md   GENERATED by tools/gen_contract.py from spec §II.3.4 — never hand-edited (D-AUDIT-02)
  db/schema.sql            the one SQLite schema, applied by `cdfc init`; its sha256 is a run-manifest pin
  .gitignore               .venv-cdfc/ reports/ blobs/ *.db — never fixtures/

  spec/                    the authoritative build specification, parts 00–05. Read-only input to this plan
  plan/                    this build plan: 00 decomposition · 01 methodology · 02–07 phase detail · 09 this manual
  research/                the fifteen lanes, the superseded drafts, and the harnesses that produced every
                           MEASURED number the plan starts from. Read-only after P0-B2 promotes foundation_probe.py

  src/cdfc/                the package (coverage-declaring filing checker) — the CI scan roots
    ingest/                L0: receipt, container guard, the three readers, the competence matrix, agreement
    schema/               L1: induction, the unlocked mask computed TWICE, stable keys, vocabularies, fingerprint
    facts/                 the two-document fact model, units (int64 milli-USD-million), provenance anchors
    calc/                  the formula evaluator — topological, Decimal, nine functions; there is no float below here
    predicates/            the envelope, the admitted CEL profile, the both-ways AST walker, the harvest, host_fns/
    evaluate/              pre-flight, the generated contract's transition table, the CEL runtime, roll-up
    verdict/               8 item states · 30 reason codes · the 8 run-level invalid.* causes · closure · settled
    store/                 db.py — the SQLite file IS the artifact, so it hashes and names itself in the manifest
    qualify/               the five gates, the fault model, raw-zip surgery, observability, Wilson, ILP, corpus/
    probes/                L6: TEMPLATE_DIFF, the 25 human-authored relations, the Hypothesis driver, their gates
    selfcheck/             L6.5: the canary loop, the anti-canary, the residue procedure, the adjudication record
    attest/                L7: in-toto Statement v1, DSSE, verify, the declared-lossy OSCAL and RO-Crate projections
    surface/              the report, the Unchecked panel, the drop screen, the API, the FFR-bearing library
    measure/               absence.py — the ONLY sanctioned way to record an absence anywhere in this project
    experiment/            the draw, the exact power table, the pre-registration, the baselines, the decision record
    model/                 the two offline model touchpoints — proposal (gated on G-SETTLE) and extraction — and nothing else
    clause/                L1b: the deterministic Akoma Ntoso promoter, the FRBR grammar, the obligations table
    watch/                 the instrument-stream watcher: diff-and-flag, never NLP; a fetch failure is a logged GAP
    transfer/ churn/ ops/  P15: re-keying and the stopwatch · re-qualification and quarantine · snapshots and staleness
    cli.py                 every unimplemented subcommand EXITS 2 — a stub that exits 0 is an all-clear

  tests/
    unit/ property/ golden/ differential/ determinism/ relational/ perf/ contract/ e2e/   the ten test classes
    negative/              catalogue.yaml (THE machine-readable catalogue) · injectors/ · broken_builds/ · the guards
    test_suite_census.py   the suite may not silently shrink; two expected counts, one per platform
    test_validation_ledger.py   nine fields per row, and the ledger must have GROWN since the previous phase tag
    test_corpus_firewall.py     asserts corpus/ is not importable from src/ or tests/

  fixtures/
    prescribed/            the nine regulator workbooks, byte-identical, + MANIFEST.json — the golden corpus
    adversarial/           the crafted hostile containers the guard must trip on
    synthetic/             generated filings, labelled SYNTHETIC in three places so they can never be quoted as real
    predicates/ baselines/ pinned envelopes and the B0/B1/B2 baseline outputs
    licences/              the research venv's site-packages listing, so the licence control survives a cleanup
    corpus_manifest.json   the main repo's ONLY reference to the blind-fill corpus: {repo_url, commit_sha, brief_sha256, …}

  ci/
    GATES.md               the sixteen-row gate registry — append-only, and P0's denominator
    no-green-tick.sh no-regex-over-xml.sh no-bare-except.sh no-float-money.sh no-bare-absence.sh
    no-libreoffice-online.sh golden-asserts-values.sh no-clock-in-core.sh licence-gate.sh
    barrier5.sh            propose.py without a decision record fails the build
    no-scheduled-polling.sh blocks polling while docs/TERMS-OF-USE.md says read: false
    surface_audit.py       the four surface gates, run against a real browser rather than against the stylesheet

  tools/
    measure/               foundation_probe.py and its successors — every published measurement re-runnable
    probes/                the P9 probes already on disk: precedents, function census, unlocked formulas, D17
    mutation/              run.py + exclude.toml — mutmut over src/cdfc/, reported as four census terms
    corpus/                contamination_probe.py — ADVISORY; it cannot establish blindness and says so
    nc_sweep.py            the negative-control sweep -> reports/negative-control-sweep.json
    gen_contract.py        generates EVALUATION-CONTRACT.md; a CI test asserts the evaluator equals it

  docs/
    decisions/             one page per decision, indexed by §5 of this manual
    measurements/          one document per phase number — P0-foundation-probe.md … P15-transfer.md
    LICENCES.md            per-dependency {name, version, licence, warrant, opened_by, opened_at}
    GATE-LIVENESS.md       for each gate: the date, the injector, and the PASTED failing assertion
    GATE-CHANGES.md        why a gate moved. A gate that moves without a row here is a renegotiation
    ABSENCE-SCOPE.md       the written inclusion rule; no absence claim ships with a count before it exists
    DOD-TEMPLATE.md        methodology §4, as a fillable checklist — one filled copy per BUILD
    OPEN-ITEMS.md          every item in §6 of this manual, with its rule and its current state
    OWNERS.md              milestone × person × hours; the three human-latency items must be visible in it
    FIELD-OBSERVATIONS.md  E1 and E1b: question verbatim, sender, date, reply — or the standing absence and its age
    TERMS-OF-USE.md        the register API row, with read: true|false. It gates the polling script
    HARVEST-DELTA.md       append-only log of every movement of test_harvest_count, with its reason
    EQUIVALENT-MUTANTS.md  the adjudication ledger — the one place a survivor's equivalence argument lives
    MUTATION-THRESHOLDS.md the module tier table (V/Q/I/S) with its per-phase thresholds
    READER-COMPETENCE.md   which reader is authoritative for which field, and why widening it needs a reason
    PROTECTION-RESOLUTION.md  how the unlocked mask is resolved, and the 3,747-vs-3,755 disclosure
    RELATION-REVIEW.md     per relation: its evidence sentence, its necessity class, two reviewer signatures
    README-NUMBERS.md      every number the README is allowed to print, with its ledger row
    FAULT-MODEL-v3.md      the operator list and the id migration table
    SELFCHECK-THRESHOLDS.md  MAX_WITNESSES and the inapplicability curve that sets it
    NAME-ALLOWLIST.md      attestation property names that trip the advisory scan, each with its argument

  experiments/E6/
    PREREGISTRATION.md     content-addressed and published BEFORE the first API call; nothing added afterwards
    DECISION.md            published either way, on the date it is taken. Its absence blocks all of L3 (barrier 5)

  predicates/harvested/<template_sha8>/   the harvested envelopes, per template, content-addressed
  perf/                    baseline.json · baseline.ci.json · BUDGET-CHANGES.md (a moved budget needs a row)
  reports/                 CI artifacts. validation-ledger.jsonl lives here and is the only one that is committed
  blobs/sha256/<aa>/<rest> received bytes, content-addressed, never re-serialised (gitignored)

  .venv/                   THE RESEARCH VENV — A FIXTURE (R8). It holds formulas 1.3.4 and pycel 1.0b30, both
                           denylisted, and it is the licence gate's LIVE negative control. DO NOT CLEAN
  .venv-cdfc/              the build interpreter, installed --require-hashes from requirements.lock (gitignored)

/Users/abishaikc/gift-corpus/     A SEPARATE GIT REPOSITORY, deliberately outside this tree
  FILL-BRIEF.md            hashed and published BEFORE the first workbook is filled
  SLICES.md                the held-out slice, DECLARED BEFORE the corpus exists
  filled/                  clean__blind-filled__fme-001__<sha8>.xlsx …
  MANIFEST.json            per workbook: sha256, filler_id, elapsed_minutes, provenance
```

---

# §8 — THE CLOSING CHECK ON THIS MANUAL

Four properties to verify if this document drifts.

**One. Every number in §4 has a denominator and a build.** A row that acquires a value without acquiring a
ledger entry has escaped the mechanism, and the mechanism is the product. If a future revision adds a row
with an empty denominator column, that revision has added an assertion, not a measurement.

**Two. §2 gets worse over time only by being rewritten.** It is a snapshot with six values in fifty slots.
The temptation, once phases start closing, is to describe the plan rather than the repository. **The test
is whether every claim in §2 can be checked by running a command in §3.**

**Three. §6 must never shrink silently.** An item leaves that table in exactly two ways: an answer arrives
and becomes a decision-log entry, or the rule fires and the consequence is written into the phase's
measurement document. **An item that simply stops appearing has been dropped**, which is the specific
failure mode P0-B4 exists to prevent, applied to this document.

**Four. The loop in §1.3 has ten steps and step 2 is the only one that cannot be automated.** Steps 3
through 10 are all mechanised — the sweep, the ledger, the mutation run, the DoD, CI. Step 2 —
*what specific broken build would make this test go red?* — is a question a person asks themselves. If a
revision of this manual makes the loop shorter, check first that it did not remove step 2, because
everything else in this plan is downstream of an honest answer to it.

---

*Ends. The plan's skeleton is `plan/00-decomposition.md`; its validation regime is
`plan/01-validation-methodology.md`; the sixteen phases are specified in full across `plan/02`–`plan/07`.
Development starts at P0-B1, and the corpus lane starts the same day.*

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C4** — P0's gate set | `gates_live / gates_written` corrected from **`12 / 12` over 16 rows with 4 pending** to **`15 / 15` over 18 rows with 3 pending**, with the pre-registered sets and `test_contract__live_set_is_pre_registered` named; the claim-register row takes the same denominator | §3.4 · §10 claim register row 1 |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
