# docs/DEMO-SCRIPT.md — the end-to-end walkthrough, shot by shot

**Every number in this file is measured and current as of 16 Aug 2026.** If one moves, the script
is wrong and the product changed — re-run the commands in §0 before filming rather than trusting
the page.

Total running time **6:30**. Eight acts. One take per act is fine; they cut together.

---

## §0 — Before you press record

```bash
make history          # produces the run, the report, the churn sweep and the history series
make attrition        # produces the qualification artifact the three gate screens read
make serve            # http://127.0.0.1:8765
```

Confirm these four, because every caption below quotes them:

| what | value | where |
|---|---|---|
| settled | **1,898 of 3,747** | `/runs/f5eb385a8888c55b` |
| not checked | **1,849**, split **422 / 1,427** | `/runs/{id}/unchecked` |
| field surface vs recorded | **3,747 of 6,757** | same screen, §"Is the field surface the whole form?" |
| refusals | **348**, all at G2 | `/rejections` |

Browser at **1280×860**, zoom 100%. Hide bookmarks. The rail is the only chrome on screen.

---

## ACT 1 · The job — 0:00–0:30

**No screen. Title card or talking head.**

> An FME files a quarterly return to IFSCA. The workbook has three and a half thousand fields a
> filer can write. Somebody checks it before it goes — and afterwards, nobody can say what was
> checked and what was skipped.
>
> That second sentence is the product.

**Graphic:** the two-panel opener from the deck — *blank form* → *filled form*, with the caption
**"the difference is what we can say about the gap."**

---

## ACT 2 · Check a filing — 0:30–1:15

**Screen:** `http://127.0.0.1:8765/`

Drag `fixtures/synthetic/clean__independently-computed__fme-q1.xlsx` onto the target.

> One control. There is no strict mode, no sheet selector, no skip-empty-rows box.

**Caption (hold 4s):**
> **Every setting here would change what gets checked — without changing what the report says was
> checked.**

Let the upload progress bar run. It is real; the file is 3.6 MB.

---

## ACT 3 · The declaration — 1:15–2:30

**Screen:** `/runs/f5eb385a8888c55b`

**Beat 1 — the hero.** Hold on the two lines without speaking for two seconds.

```
1,898 of 3,747 cells settled
1,849 of 3,747 fields NOT checked
```

> Same size. Same weight. Same ink. The moment one of those is bigger than the other, the reader
> has been told which one matters — and the one they'd be told to ignore is the count of fields
> nobody checked.

**Beat 2 — scroll to the band.** Point at the two hatched slivers on the right.

> The band never fills. Those last two terms are drawn at a floor and they carry **no digit**,
> because neither has been measured. A bar that reaches its own far edge would be this tool saying
> the form is fully accounted for.

**Beat 3 — THE DIFFERENTIATOR. Scroll to "Is the field surface the whole form?"**

This section exists because somebody will ask it, and the answer is no.

```
3,747 of 6,757 cells are the field surface
    505  formula cells — the template computes them
  2,505  locked cells — a filer cannot write them
  3,747  the field surface
```

**Caption (hold 5s):**
> **A denominator that does not declare its own exclusions is a coverage lie. This one declares
> them.**

---

## ACT 4 · What was not checked — 2:30–3:30

**Screen:** `/runs/f5eb385a8888c55b/unchecked`

> This page is the product. It is not an appendix and it does not live behind a tab.

```
  422  no_predicate.failed_qualification   a check exists — the kill gate refused it
1,427  no_predicate.not_yet_synthesised    no candidate binds this cell at all
```

Read one remedy aloud, in full. The `failed_qualification` one:

> *"a candidate that clears the gate that rejected this one, and the attrition row says which…
> A rejected candidate is not a missing check — it is a check we declined to ship, and the number
> that declined it is on the record."*

**Caption:**
> **Two different gaps. One is our authoring backlog. The other is a check we built, measured, and
> refused to ship.**

Scroll to the residue block and hold:

> Residue has not been measured. It renders **no digit** — because a measured zero and an
> unmeasured one are different facts, and a zero here would be the worse news of the two.

---

## ACT 5 · The evidence — 3:30–4:45

**Screen:** `/rejections`

> Three hundred and forty-eight candidate checks. Every one refused, and every row carries the
> number that refused it.

Point at a `kr_claimed = 0/68`.

**Caption:**
> **A rejection without the number that decided it is an opinion with a gate's name on it.**

**Screen:** `/funnel`

> Gate order. Three integers per stage. Everything survives G0, G1 and G3-proof, and everything
> dies at G2 — the kill gate.

Point at the last two rows.

> G3-empirical and G4 say **NOT RUN**. Not "passed everyone." A gate that never executed made no
> determination about anybody, and rendering it as a pass is the vacuous pass this whole design
> exists to refuse.

**Screen:** `/predicates`

> Zero predicates admitted. And the sentence under it is the one that matters:

**Caption:**
> **29 predicates produced the settled count. 0 are admitted through the five gates. These are
> different populations — and no settled count in this product rests on a gate-admitted predicate.**

---

## ACT 6 · The number can go down — 4:45–5:30

**Screen:** `/history`

> A coverage number that can only rise is a marketing chart.

Hover the second point.

```
1,898  →  1,862      ▼ −36
cause: template 7d9a1960 → a1ea1afc: n_1_introduction_d3 changed,
       9 predicates moved to PROVISIONAL and stopped settling.
```

**Screen:** `/churn`

> Nine predicates stopped settling. **They did not stop running.** That distinction is the whole
> panel — the wrong implementation lowers the number by exactly the same amount and loses detection
> silently, and a chart cannot tell you which one you're looking at. This page can.

---

## ACT 7 · Does it actually catch anything — 5:30–6:10

Two drops, back to back.

**Drop 1:** `fixtures/synthetic/mutant__f11-formula-override__portfolio-O7.xlsx`

> One FAIL. A seeded formula override, caught as a finding.

**Drop 2:** `fixtures/synthetic/formula-overwritten__portfolio-O7.xlsx`

> Same class of problem. No failure — instead the settled count **collapses from 1,898 to 1,557**.

**Caption — say this one, do not skip it:**
> **Of five seeded defects, one surfaces as a finding. The rest surface as coverage falling, or as
> the run refusing to start. Catching a problem as loss of coverage is not the same as catching it
> as "this is wrong," and we don't describe it as if it were.**

---

## ACT 8 · What it does not claim — 6:10–6:30

**Screen:** `/open-items`

> Three things this tool does not do, on the record and on the screen.

1. **It does not read the regulation.** The IFSCA Fund Management Regulations are pinned — 1,218
   units, two independent extraction arms. **No predicate implements a clause from them.**
   `predicates_with_a_STATUTE_obligation = 0 / 348`. Every check here is derived from the
   *workbook's own* formulas and dropdowns.
2. **It is not an audit opinion.** It states what was checked and what was not.
3. **Nothing here is admitted under G4.** Every number is PRE-GATE, and the caveat travels with
   every count that renders.

**Closing card:**
> **It tells you what it did not check. In writing. With the reason.**

---

## THE THREE SENTENCES THAT MUST NOT BE SAID

Each is false, and each is the obvious thing to say.

| do not say | say instead |
|---|---|
| *"it reads the regulation and finds breaches"* | *"it induces the form's own rules and reports the gap"* |
| *"it catches defects"* (unqualified) | *"one of five seeded defects surfaces as a finding; the rest as coverage collapse"* |
| *"50% coverage"* / any bare percentage | *"1,898 of 3,747"* — the UI will not render a rate, and neither should the voiceover |

---

## IF SOMEBODY ASKS, ON CAMERA

**"Is 3,747 the whole form?"** — No. Act 3 beat 3 answers it: 6,757 recorded, 505 computed by the
template, 2,505 locked.

**"Why is nothing admitted?"** — G-CORPUS is RESTRICTED. `n = 40` filings, `n_non_synthetic = 0`.
Every severity tier is capped at ADVISORY until a corpus this project did not author exists.

**"Why did 319 predicates not run?"** — They never killed a mutant in the pinned campaign, so G2
refused them. The 422 cells they bind are reported as `failed_qualification`, not as *no check
exists*.

**"Can I verify the report you just showed me?"** — `/verify`. The comparison is over bytes, not
over the numbers: a report that renders the same figures but differs in one byte is a report the
attestation does not cover.
