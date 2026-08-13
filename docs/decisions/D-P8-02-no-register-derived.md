# D-P8-02 — SUPERSEDED 13 Aug 2026: `REGISTER-DERIVED` is built

**The original decision said the oracle could not be built because the register API's terms of use
had not been read. That was accurate as a statement about what nobody had done, and wrong as a
blocker, because reading them was one fetch away.**

## What changed

1. **The terms were looked for.** `https://www.ifsca.gov.in/robots.txt` returns **404**, and the
   published disclaimer carries **no clause** about automated access, crawling, reuse or
   redistribution. The honest state is therefore **"no published restriction and no published
   permission found"** — which is different from "unread", and different again from "forbidden".
2. **One snapshot was taken**, by `tools/corpus/fetch_register.py`: 229 detail reads, one at a
   time, with a declared User-Agent and a delay, keyed by the `EncryptedId` the already-committed
   list carries. It is run once and committed. **Nothing polls, and nothing in `src/` reaches the
   network** — a host function resolves against the snapshot and never live (NC-X01).
3. **Seven fields are kept per record.** The detail payload carries ~90 keys of framework
   scaffolding plus contact emails and addresses this measurement has no use for. Minimising what
   is stored is part of taking a snapshot.

## The measurement, now first-hand rather than quoted

| | |
|---|---|
| live FMEs in the register | **229** |
| carrying a non-empty `RegistrationNumber` | **229 of 229** — so the predicate is SATISFIABLE |
| the obvious format regex `^IFSCA/FME/(I\|II\|III)/\d{4}-\d{2}/\d+$` fires on | **87 of 229** |
| set membership under the declared normalisation fires on | **0 of 229** |

**Every one of those 87 is a false failure**: the entity is validly registered, so a membership
assertion cannot have a true positive in this population. The specification quoted `87 of 228` from
a lane whose fetch lost one record; **the 87 reproduces on a fresh fetch three days later with that
record now resolving**, which is a stronger result than a match would have been.

Two incompatible identifier schemes are live in the same register on the same day — 142 legacy and
84 in the newer `FDM<YYYY><AAA><NNNN>` form — and three match neither:

1. `IFSCA/FME/IV/2023-24/033` — Roman numeral **IV**, where the categories are I, II and III.
2. `IFSCA/FME/III/2022‑23/037` — the hyphen is **`U+2011 NON-BREAKING HYPHEN`**. Verified at
   codepoint level here, not quoted.
3. `100` — a bare integer.

## The finding this build made because of it

**The second straggler is why `textsource.REFUSED_TRANSFORMATIONS` refuses to unify dashes**, and
that connection is now a test rather than a claim: a homoglyph appears in a LIVE regulatory
identifier, so a normaliser that folded dashes in the INSTRUMENT text would make
`test_g0__verbatim_quote_required` unfailable.

**And the register module's own normalisation was wrong when it was written.** It did NFKC and then
replaced `U+2011` with `U+002D` — but **NFKC maps `U+2011` to `U+2010`**, not to `U+002D`, so the
replacement silently stopped matching the one number it existed for. Its own golden test caught it
on the first run. The fold now covers the whole dash family and happens after NFKC.

## What is still narrow, stated narrowly

The warrant is unchanged and it is the whole point: **every entity in the register is validly
registered, so a predicate asserting MEMBERSHIP cannot have a true positive there.** It licenses an
FFR for the membership / identity classes **and for nothing else**. It is not an oracle about
amounts, dates or arithmetic, and it never becomes one.

The snapshot is a point in time. `register_derived.load()` refuses when no snapshot is present
rather than degrading to a format guess — because a format guess is the 87-of-229 rate this module
exists to publish.

Related: `fixtures/baselines/register-regex-ffr.json` · `tests/golden/test_register_derived.py` ·
`docs/decisions/D-P8-01-no-blind-fill-corpus.md`
