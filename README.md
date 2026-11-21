# cdfc — Coverage Declaration for Filed Compliance

**A checker for regulatory filings that reports what it never examined, not only what it found.**

Every tool that checks a regulatory filing reports what it *found*. None reports what it never
*examined* — so a field nobody looked at is indistinguishable from a field reviewed and found
correct. `cdfc` derives its rules from the filing template itself and returns a **coverage
declaration**: every field lands in exactly one state, and every unchecked field carries a reason
from a closed vocabulary and the specific instrument that would make it checkable.

> **This is a prototype.** It is built and measured against **one workbook family** — the IFSCA
> Fund Management quarterly return — and the scope of what it does and does not do is stated
> exactly below and on every screen it renders. It is not an audit tool, it is not an assurance
> product, and nothing in it has been through a regulator's hands.

<video
  src="https://github.com/Abishai95141/cdfc/raw/main/docs/demo/cdfc-walkthrough.mp4"
  poster="https://github.com/Abishai95141/cdfc/raw/main/docs/demo/poster.jpg"
  controls muted playsinline width="100%"></video>

▶ **[Watch the walkthrough (2:33)](https://github.com/Abishai95141/cdfc/raw/main/docs/demo/cdfc-walkthrough.mp4)**
 · [subtitles](docs/demo/cdfc-walkthrough.srt) · [shooting script](docs/DEMO-SCRIPT.md)

**Contents:** [The idea](#the-idea-in-one-minute) · [Results](#what-it-returns-on-the-reference-filing) ·
[GIFT City hackathon](#where-it-came-from-the-gift-city-hackathon) · [Run it](#run-it) ·
[Architecture](#how-it-is-put-together) · [Scope and limits](#the-scope-of-this-prototype--read-this-before-drawing-conclusions) ·
[Design rules](#the-rules-the-surface-is-built-under) · [Docs](#where-to-read-more)

---

## The idea in one minute

A regulator publishes a **blank Excel form**. A company downloads it, fills in thousands of boxes,
and sends it back. Both files already exist; nothing about the pairing is invented here.

**The blank form is not empty.** The regulator has already written part of the rulebook into the
spreadsheet — formulas that compute totals, dropdowns that restrict values, numeric and date
bounds, protection masks, cross-sheet references. `cdfc` extracts those rules **mechanically**:
nobody types them and no model guesses them.

Excel's own rules are advisory, not enforcing — validation fires only on *typed* entry, formulas are
editable, protection is removable — which is why filings still go wrong. So the product's claim is
not "we find more errors". It is:

> **We can tell you what we did *not* check, and prove the number.**

That makes it a liability product rather than a productivity one: the unchecked count is published
at the same weight as the checked one, and the coverage number is **allowed to fall** when a
template changes under it.

---

## What it returns on the reference filing

| | |
|---|---:|
| settled — a check ran and decided | **1,898** of 3,747 |
| **not checked** | **1,849** of 3,747 |
| — a check exists and the kill gate refused it | 422 |
| — no candidate binds the cell at all | 1,427 |

And because a denominator that will not say what it excluded is itself a coverage lie:

| | |
|---|---:|
| cells the workbook records | **6,757** |
| excluded — formula cells the template computes | 505 |
| excluded — locked cells a filer cannot write | 2,505 |
| **the field surface**, the denominator of every count above | **3,747** |

**Mechanics worth knowing:** 348 candidate checks are harvested from the FME form's own structure
(571 across nine pinned blanks); a check must demonstrate it can catch a seeded fault before it may
contribute to coverage; the verdict path makes **zero model calls**, and that is a property of the
import graph, not a promise.

---

## Where it came from: the GIFT City hackathon

`cdfc` was built for the **two-day hackathon at GIFT City (21–22 August 2026)**, which the author
attended. The problem it targets is specific to that setting: each quarter, every fund manager
licensed at GIFT City files a spreadsheet the regulator publishes, and the review that follows
reports findings but never the denominator.

The submission text written for that event is in [`docs/PITCH.md`](docs/PITCH.md) (title, elevator
pitch, problem statement, proposed solution). The project has continued since as a measured,
gated build; [`docs/PLAN.md`](docs/PLAN.md) is the plan of record.

---

## Run it

Python 3.12.

```bash
make history      # produce a run, its report, the churn sweep and the history series
make attrition    # produce the qualification artifact the gate screens read
make serve        # http://127.0.0.1:8765
```

Thirteen screens, server-rendered. Loopback by default — a coverage tool that listens on `0.0.0.0`
the first time somebody runs it is a coverage tool that ends up on a network nobody meant to put it
on.

```bash
make verify       # every gate, the full suite, and the negative-control sweep
make demo-video   # re-record the walkthrough (needs `make serve` in another shell)
```

`make verify` runs the full suite and a sweep of 141 negative-control entries against 230 guards
under exact-set semantics: every guard expected to go red must go red, every guard expected to stay
green must stay green. Not *at least one*.

**Checking a filing over HTTP.** `POST /v1/filings` binds an uploaded workbook against the pinned
catalogue, checks it over the blank it bound to, and returns `201` with the coverage declaration —
measured on two real files: the reference FME filing settles **1,898 of 3,747**, and the ALR return
settles **848 of its own 1,599**. A filing whose template is not pinned gets
`422 template_unbound` carrying its computed fingerprint.

---

## How it is put together

```
LAYER 1  DETERMINISTIC  corpus -> provisions (eId + exact span) · template -> fields (declared type)
LAYER 2  THE MODEL      proposes rule -> field bindings AS DATA. It decides nothing.
LAYER 3  DETERMINISTIC  five gates: quote · field · type · vocabulary · cross-reference
                        only admitted proposals become nodes
LAYER 4  DETERMINISTIC  graph + coverage, over a denominator that is not arguable
LAYER 5  MIXED          precedence in Python before any engine; then chaining
```

`src/cdfc/evidence/run.py` is the single driver — the one place layer order is decided. The model
writes its proposals to a **file** and the driver reads it, so the model is never called from the
verdict path because it is not called at all.

| | |
|---|---|
| `src/cdfc/predicates/` | induces checks from the template's formulas and validations |
| `src/cdfc/qualify/` | the five gates — scope, binding, degeneracy, kill rate, false-failure rate |
| `src/cdfc/evaluate/` | binds checks to a filing and rolls cells up to a closure that must sum |
| `src/cdfc/verdict/` | the state and reason vocabularies, both closed |
| `src/cdfc/churn/` | what happens to coverage when the template moves under it |
| `src/cdfc/surface/` | the report, the screens, and the design tokens they render from |
| `src/cdfc/attest/` | signs a statement over a run and re-derives it byte for byte |
| `tests/negative/` | the injectors — each breaks one property on purpose to prove a guard sees it |

**Stack.** Python 3.12 · `lxml` and `openpyxl` for ingest · CEL (`celpy`) with `lark` for the
constrained check language, walked by AST rather than matched by pattern · `z3` · YAML. That is the
**measured** runtime closure of the verdict path — six third-party packages — and anything absent
from the list is refused by default. Build-time and measurement-time tools (Docling, LangExtract,
networkx, rdflib, splink) live outside it.

The attestation payload is deterministic and re-derivable byte for byte — **0 bytes differing of
1,569,451** across four environment variations. Read what that covers before relying on it: in
this prototype it is a 4,015-byte summary statement, not the per-cell record and not the rendered
report, and it is signed with a demo key published in this repository under the id
`cdfc-demo-key-do-not-trust`. The mechanism is real; the trust root is not there yet.

---

## THE SCOPE OF THIS PROTOTYPE — read this before drawing conclusions

Four claims it would be easy to make from the video, all of them false.

**It does not read the regulation.** The IFSCA (Fund Management) Regulations 2025 are pinned in the
corpus — 1,218 text units, extracted by two independent parsers requiring unanimity — and **no
predicate implements a clause from them**: `predicates_with_a_STATUTE_obligation = 0 / 348`. Every
check is derived from the workbook's own structure. The text-to-rules half is pinned and unbuilt.

**Nothing is admitted.** All 348 harvested candidates were refused at the kill gate — 315 for never
catching a seeded fault, 33 for adding nothing over free baselines. The predicate library is
empty, deliberately, and the 29 predicates that produce the settled count are a **disjoint**
population running under `PRE-GATE`. No number here rests on a gate-admitted check.

**It catches defects unevenly.** Of five seeded defects, **one** surfaces as a finding; three
surface as the coverage number collapsing; one is refused outright as `template_unbound`. Catching
a problem as loss of coverage is a real signal and is not the same as catching it as *this is
wrong*.

**It checks the form it is handed, and it refuses the ones it cannot recognise exactly.** A filing
binds by exact structural hash to one of nine pinned blanks, and the checks, the field surface and
the denominator then come from *that* blank: the pinned ALR return is scored over its own **1,599**
cells, and handing it the wrong blank is `INVALID` with `invalid.denominator_disagreement` rather
than a VALID verdict over somebody else's denominator.

The limit that remains is the **exactness** of that bind. A filer who inserts a row has the whole
filing refused as `invalid.template_unbound` — not partially checked, refused. A graded bind was
built to soften that and **reverted after it was measured**: a row insertion renumbers every cell
below it, so of 3,747 addresses 3,544 appear in both files and **1,451 of those hold a different
field**, and scoring those against each other is the wrong-form failure that strict binding exists
to prevent. Until a real field *correspondence* exists, exact-or-refuse is the only safe bind, and
[`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md) carries what the correct design needs.

**What the claim is, and is not.** The claim is **provenance, not correctness**. Nothing bounds
*recall* — the product measures the rules that were proposed, never the ones nobody proposed. No
real filed return has been tested; none are public, so every filing here is synthetic. Also absent:
operational staleness policy, deployment packaging, and the instrument-stream watcher.

<details>
<summary><strong>About the walkthrough video — what is a product screen and what is a title card</strong></summary>

The video is recorded by driving the running server, not by capturing a screen. **Every figure on
a product screen is read live from the API**, and `make demo-verify` fails the build if a caption
quotes a number the product no longer produces.

**Two beats are title graphics, not product screens, and one of them is a real gap.** Both are
static HTML authored in `tools/demo/record.mjs` and make no API call. The *denominator* card's
figures are typed but every one is asserted against `/v1/runs/{id}.surfaceExclusions` by
`tools/demo/verify.mjs`, so a moved number still fails the build. The *detection* card is the gap:
of its four values only `1,898` is covered, and the other three are read from no endpoint, asserted
by no claim, and served by no `/v1` route — **they would survive unchanged in the video if the
product stopped producing them.** Found by an adversarial audit of this file.

**Which half of it is the browser, and which half is the command line.** Every screen in the video
is the running server, and every number on those screens is real. The video predates the intake:
the *run* those screens display was produced on the command line by `make history`, and the
walkthrough never uploads a file. `POST /v1/filings` now binds the workbook and checks it, but
**the run is not stored** (`"persisted": false`): there is no queue, no worker and no run store
behind the endpoint, so the *report screens* are still reached through a command-line run.

</details>

---

## The rules the surface is built under

Five, each enforced by a build gate that has been observed failing.

1. **No affirmative verdict.** No checkmark, no green, no "all clear". The palette contains no
   green and a gate reads the generated bytes, because the fastest way to reintroduce an
   affirmative colour is to add it under a name nobody would grep for.
2. **No bare rate.** Every percentage renders with both integers of its fraction or does not
   render. A percentage carries no evidence of its own arithmetic.
3. **No settled count without its admission state**, within two DOM ancestors of it.
4. **No total row on any cross-template view.** Counts aggregate; fractions do not. A mean over two
   workbooks' masks is a number with no denominator.
5. **Absent ≠ empty ≠ zero.** Three distinct renderings, and the not-measured one carries no digit
   at all.

---

## Where to read more

| question | the one place |
|---|---|
| what are we building, and what is next? | [`docs/PLAN.md`](docs/PLAN.md) |
| what is the architecture, actually? | [`docs/ARCHITECTURE-measured.md`](docs/ARCHITECTURE-measured.md) — from the import graph |
| what changed, and what was found wrong? | [`docs/AUDIT-TRAIL.md`](docs/AUDIT-TRAIL.md) |
| what is still open? | [`docs/OPEN-ITEMS.md`](docs/OPEN-ITEMS.md) |
| the hackathon submission text | [`docs/PITCH.md`](docs/PITCH.md) |
| how to work in this repository | [`CLAUDE.md`](CLAUDE.md) |

Licensed under Apache 2.0 — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

---

*This states what was checked and what was not. It does not state that a filing is correct.*
