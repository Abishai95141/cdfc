# cdfc — a coverage declaration for regulatory filings

> **This is a prototype.** It is built and measured against **one workbook family** — the IFSCA
> Fund Management quarterly return — and the scope of what it does and does not do is stated
> exactly, below and on every screen it renders. It is not an audit tool, it is not an assurance
> product, and nothing in it has been through a regulator's hands.

<video
  src="https://github.com/Abishai95141/cdfc/raw/main/docs/demo/cdfc-walkthrough.mp4"
  poster="https://github.com/Abishai95141/cdfc/raw/main/docs/demo/poster.jpg"
  controls muted playsinline width="100%"></video>

▶ **[Watch the walkthrough (2:33)](https://github.com/Abishai95141/cdfc/raw/main/docs/demo/cdfc-walkthrough.mp4)**
 · [subtitles](docs/demo/cdfc-walkthrough.srt) · [shooting script](docs/DEMO-SCRIPT.md)

The video is recorded by driving the running server, not by capturing a screen. Every figure in it
is read live from the API, and `make demo-verify` fails the build if a caption quotes a number the
product no longer produces.

---

## What it does

Every tool that checks a regulatory filing reports what it **found**. None reports what it never
**examined** — so a field nobody looked at is indistinguishable from a field reviewed and found
correct.

This one derives its rules from the filing template rather than from a maintained schema: the
formulas, data validations, protection mask and cross-sheet references the regulator already wrote
into the artifact. What it returns is a coverage declaration in which every field lands in exactly
one state, and every unchecked field carries a reason from a closed thirty-code vocabulary plus the
specific instrument that would make it checkable.

On the reference filing:

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

---

## THE SCOPE OF THIS PROTOTYPE — read this before drawing conclusions

Three claims it would be easy to make from the video, all of them false.

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

Also absent: operational staleness policy, deployment packaging, and the instrument-stream watcher.
`docs/OPEN-ITEMS.md` carries the standing list and the report renders it.

---

## Run it

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

`make verify` runs 1,573 tests and a sweep of 141 negative-control entries against 230 guards under
exact-set semantics: every guard expected to go red must go red, every guard expected to stay green
must stay green. Not *at least one*.

---

## How it is put together

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

Checks are written in a constrained expression language, walked by AST rather than matched by
pattern. A check must demonstrate it can catch a seeded fault before it may contribute to coverage.
Reports are deterministic and re-derivable, so a published claim can be verified by whoever
receives it rather than trusted.

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

*This states what was checked and what was not. It does not state that a filing is correct.*
