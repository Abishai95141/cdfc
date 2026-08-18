# experiments/E6/DECISION.md

**status: PENDING — the run has not been taken.**
**Publication date for the final record: on the day the run is taken. Dated 15 Aug 2026.**

**Lock hash `h0`:** recorded in `experiments/E6/preregistration.lock.json`.
Recompute with `shasum -a 256 experiments/E6/PREREGISTRATION.md`.

---

## The headline sentence, and why there is not yet a number in it

> **Of the 600 candidate regulatory checks this experiment would propose, `k` is UNMEASURED. No
> model call has been made, no money has been spent, and the criterion that will decide what `k`
> means is locked, hashed and committed.**

`plan/06` commits this document to being published **either way**, and `NC-M17` fails the build if
`runlog.jsonl` exists without it. There is no runlog. This record exists at `PENDING` anyway,
because the alternative — no document until there is a number — is how a publication commitment
lapses quietly, and the failure mode this project is most alert to is not a wrong answer but a
result that quietly never appears.

> **CORRECTION, 18 Aug 2026 — the paragraph below is out of date and is left standing as written.**
> This record was published on 15 Aug 2026. On 16 Aug 2026, S1 pinned the first STATUTE instrument:
> `statute-fm-regulations-2025`, from `corpus/instruments/fm-regulations-2025.pdf`, 1,218
> addressable units read by two INDEPENDENT external extractors (pdfplumber and pypdfium2), of
> which 1,189 are AGREED, 28 DISPUTED and 1 SINGLE_PARTY. So two sentences below are now false:
> `corpus/instruments/MANIFEST.json` carries TEN instruments, not nine, and `statute_instruments`
> is `["statute-fm-regulations-2025"]`, not `[]`. *"There is no statutory instrument in this
> repository, there never has been one in its git history"* was true when written and is false now
> — the git history contains the pin.
>
> **The pool still cannot be built, and the reason has moved rather than lifted.** `make pool` now
> reaches the instrument and exits **3**: the pre-registered chapter titles in
> `PREREGISTRATION.md` do not match the headings the extraction actually produced (the text reads
> `CHAPTER II REGISTRATION OF FUND MANAGEMENT ENTITY (FME) …`, and 25 heading units are
> undeclared), so `enumerate_shall` raises `UndeclaredHeading` rather than matching loosely. The
> chapter list is part of the HASHED pool construction and may not be relaxed to fit the text, so
> either the list or the extraction is wrong, and which of the two is itself a finding. The
> refusal chain below therefore still holds at every link — only its FIRST link has a new cause.
> Two further things are unchanged: no statutory obligation has been authored, and
> `provisos.assert_measured_for_statute` would refuse one at G0 anyway while
> `fixtures/predicates/proviso-labels.json` carries `labeller: null` and zero spans.
>
> **`status:` stays `PENDING`.** No run has been taken, no money has been spent, and this
> correction records a changed blocker rather than a result.

## Why the run has not been taken — the pool, not the permission

**The pool cannot be built, and it is structural rather than configurational.**
`corpus/instruments/MANIFEST.json` carries nine instruments, **every one `kind: TEMPLATE`**, and
`statute_instruments: []`. There is no statutory instrument in this repository, there never has
been one in its git history, and `docs/decisions/D-P7-01-no-statutory-instrument.md` records that
**synthesising one was rejected**: every G0 figure is `source_text.find(quote)` at a character
span, and against an invented text `quote_not_located` becomes a statement about our own
fabrication while the funnel's first stage measures nothing.

`plan/06` §P12 pre-committed a branch for a pool that cannot be built — *"`PoolExhausted` fires, no
model call is made, no money is spent, and the published result is `|A| < 20` with the
disputed-region count and its page numbers, a measurement of the instrument."* **The case here is
that branch's limiting form:** the extractions do not disagree, because there is nothing to
extract.

**The refusal chain is enforced by code at every link, and each was observed:**

```
no statute        →  enumerate_shall raises NotAStatute            (make pool, exit 2)
no pool           →  no draw, therefore no draw_sha256
no draw hash      →  prereg.append would refuse it anyway:
                     PoolNotYetFixed while the pool hashes are absent   (NC-M34)
a partial lock    →  run.assert_ready raises ArtefactHashesMissing,
                     naming all five missing fields                     (make e6-status)
```

Two further steps are outside what a build can do, and both are recorded rather than worked around:

- **The run spends money.** ≈ $13 modelled, $51 including the extension reserve. `anthropic` is
  deliberately absent from `requirements.lock` — nothing on the verdict path may import a model
  client — so installing it is part of taking the run, not part of building the harness.
- **The stratification needs two named humans**, and κ needs the second. κ is the one blocker in
  this programme with **no mechanical substitute at all**; `TableOracle` raises on an unassigned
  obligation rather than defaulting, because defaulting would turn the single human judgment the
  whole `n = 20` rests on into a fallback.

## What IS settled, and it is the phase's actual epistemic content

`plan/06`'s own opening states it:

> *"the epistemic content of P12 is that a five-gate criterion was specified, locked and hashed
> **before a model was called**."*

That is delivered and it is complete:

| | |
|---|---|
| `PREREGISTRATION.md` | generated from the module constants, hashed, locked |
| the criterion | **arithmetic, not prose** — `lock()` refuses to write a lock for a criterion `decide()` cannot consume, and the refusal precedes the write |
| `beats_baselines` | a pure function, integer arithmetic, exhaustively pinned over the `MarginalKill` tuple space including the union floor's exact boundary |
| `decide()` | pinned at **all 164 points** of `(k, stage, beats)`; its signature admits `(result, lock)` and nothing else |
| the four inadmissible arguments | hashed into the pre-registration and **unrepresentable** in the signature |
| the ordering | `textsource → exclusion_rule → draw`, enforced by `append()` and by git ancestry |

**Nothing about the criterion can now be changed by the result, because the result does not exist
and the criterion is committed.** That is the whole property, and it is the one thing a
pre-registration can actually deliver.

## The per-baseline position, stated now so it cannot be discovered later

`plan/06` P12-B2 wrote the switch trigger before the fact: *if Daikon cannot be pinned or licensed,
B1 does not run and `beats_baselines` evaluates its B1 term as `False`; it does not fall back to a
weaker detector, because a fallback that moves the result in the direction we would like is not a
fallback.*

**B1 in this repository is not Daikon and says so.**
`cdfc.qualify.baselines.b1_invariants.NOT_DAIKON` travels with every figure it produces: four
single-variable templates at confidence 1.0, no inter-variable relations, recall against Daikon
unmeasured and unmeasurable here. **A candidate's marginal kill over it OVERSTATES its marginal
kill over Daikon** — the direction that flatters us.

So whatever `k` turns out to be, the headline sentence of the final record must read *"beats
B0 ∪ B2; declines to claim it beats B1, which did not run at its specified strength."* **The claim
narrows; it does not soften.**

## What this document will contain when the run is taken

Unchanged from the pre-registration's commitment, and identical in shape on a `DELETE`:

the input hashes · the five-gate funnel with every stage's integers · **every candidate including
discards** · the Wilson interval at the realised `(k, n)` · the per-stratum split and `k_A/20`
against `k_B/10` · the per-regime split · **the marginal kill over each baseline separately and
over the union, with `beats_baselines` evaluated term by term so a reader can recompute the
boolean** · **the campaign's six integers `G · U · I · O · R · K`, with `I` printed beside `U/G`
wherever either appears** · **the pool's construction and its excluded-obligation count with page
numbers** · both attrition numbers — the experiment's bar (`K/O > 0` plus marginal) and the
registry's (`K/O ≥ 0.80`), which are **different tests** · the decision, the date, the named person
who ran it · and the sentence *"this result is one model, on one instrument, at one date."*

**On a `DELETE` the document is identical in shape. Nothing about the failure branch is thinner:**
the funnel is the deliverable, and it is more informative when nothing survives, because it says
*where* the candidates died.
