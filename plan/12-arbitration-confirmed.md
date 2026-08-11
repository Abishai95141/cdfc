# 12 — ARBITRATION CONFIRMED

**Mechanical re-verification of `plan/11-arbitration.md` against the repaired corpus.
Compiled 11 Aug 2026. Every claim below was re-derived from the documents; nothing is accepted on the
repair pass's own word.**

**Result: 8 PASS · 1 FAIL.** The failing check is **C5**, and it fails in the one document that never
recorded C5 at all. Three further findings are recorded that no ruling covers; one is a live contradiction
of exactly the class C9 was written to end.

**Instrument.** `plan/scripts/catalogue_check.py`, written for this pass and run against
`plan/*.md`. Verbatim output in §C9. It is the *third* instrument over this catalogue, and the second and
third disagree — see §C9.0, because that disagreement is itself the finding that matters most about how
this corpus gets checked.

---

## SUMMARY

| # | Check | Verdict |
|---:|---|---|
| 1 | **C1** — `d` is a frozen integer, derivation retained, retired value gone | **PASS** |
| 2 | **C2** — `source` discriminator, G0 failable, every count in two-number form | **PASS** |
| 3 | **C3** — one normative retention rule; `scope_kind` written *and* read | **PASS** |
| 4 | **C4** — deleted test name gone; enumeration closes | **PASS** *(one caveat, §C4)* |
| 5 | **C5** — no gate, tier or rate cites `TEMPLATE-COMPUTED` | **FAIL** |
| 6 | **C6** — `~114` does not survive as a critical-path number | **PASS** |
| 7 | **C7 / C8** — one name each, no orphan guard, deleted doc path gone | **PASS** |
| 8 | **C9** — the catalogue closes | **PASS** *(after one repair applied here, §CHANGES)* |
| 9 | **NUL / encoding scan with a positive control** | **PASS** |

---

## C1 — the frozen deviation threshold · **PASS**

**Ruling.** `d = 11`, an integer; the formula is retained as the *derivation*, never as the rule; `05`'s
bare `d = 25` is deleted.

**Checks run.**

```
grep -nE 'd *= *max\(' plan/*.md      -> 3 hits, all in 10 and 11 (the records of the defect)
grep -nE 'd *= *25'   plan/*.md      -> 4 hits: 10, 11 (records) and 05 L2718, L2849 (deletion records)
grep -nE '`?d`? *= *11' plan/*.md    -> 11 hits across 00, 01, 02, 05
```

- **No document states the threshold as a live formula.** `d = max(3, ceil(0.05 × …))` survives only in
  `10` L118/L371 and `11` L20 — the two documents whose job is to record the contradiction.
- **The retired value is not asserted anywhere.** `05` L2718 reads *"A bare `d = 25` was previously
  asserted here with no stated basis; it is deleted, not softened"*, and `05` L2849 is the repair-log row.
  Both are deletion records, not values.
- **The frozen integer carries all four required parts** in `02` L2787: `(a) d = 11`; `(b)` the formula
  `max(3, ceil(0.05 × |non-trivial cells|))`; `(c)` **the content hash of the corpus it was evaluated
  against**; `(d)` the date — in `experiments/G-EVAL/PREREGISTRATION.md`, written before
  `make_discriminating.py` runs. `00` L604 and `01` L372 carry the same four parts.
- **The derivation is arithmetically checkable and checks:** `max(3, ceil(0.05 × 204)) = max(3, 11) = 11`,
  against the 204 non-trivial cells `02` §0.2 N1 measured.
- **Arm 1's separate 25-of-505 rule is not the retired `d`.** `00` L1566 reads *"> 25, or > `d` engine
  disagreements"* — two thresholds, two denominators, correctly distinguished.

**Not a defect, recorded anyway:** see **Residual R1**, the guard test for this constant has two names.

---

## C2 — F9's disposition · **PASS**

**Ruling.** `source: STATUTE | TEMPLATE`; `04`'s mechanism; G0 runs for real; `03`'s honesty requirement
grafted on as two published numbers.

**1. The discriminator exists and is named `source`.** `00` L881, `03` L294, `04` L2488. `04` L952 shows
the collision it forced and how it was resolved rather than papered over:

> `# ^ renamed from `source` by C2, which needs that name for the STATUTE|TEMPLATE discriminator.`

The pre-existing provenance field became `ingest_source` (`hand | l1b | harvest`). Two distinct questions,
two distinct fields — the failure that made F9 irreconcilable is undone at the naming level, not just in
prose.

**2. G0 is a real, failable check.** `04` L1014–L1020 states the question it asks (*does this predicate
faithfully implement the relation it claims to implement?*) against a content-addressed template
instrument, with `UnsourcedObligationError` at L1134. **The losing branch is deleted, not softened:**
`03` L301 — *"This document's previous ruling — `obligation_id` stays `None`, candidates take
`SKIPPED_NOT_APPLICABLE` at G0 — **is deleted.**"* `03` L2010 rewrites obligation **X2**, which previously
instructed `04` to build the branch C2 deleted. Every surviving `SKIPPED_NOT_APPLICABLE` occurrence in
`00`–`07` is inside a sentence recording its deletion.

**3. Every published harvest-obligation count is in the two-number form.** Ten publication sites checked —
`00` L889/L922/L939, `03` L305/L798/L873/L910, `04` L1035/L1550/L1572, `07` L1106/L1395 — all render the
pair, all with `test_surface__both_obligation_counts_render_or_neither_does` /
`test_p7__both_obligation_counts_render_or_neither_does` and `UnpairedObligationCount`.

**The bare single-number grep, and the disposition of every hit:**

```
grep -nE 'harvested_predicates_with_a(n|_REGULATORY)' plan/*.md
  07 L1113   labelled *"This entry previously published the single, unqualified … which under the
             arbitrated mechanism is wrong by 280"*                          -> deletion record
  07 L2284   repair-log row: *"the **unqualified** … is replaced by the pair"* -> deletion record
  08 L352, L1196   the adversary's original proposal                          -> historical record
  10 L201–202      the verification pass quoting the defect                   -> historical record
```

**No live site publishes one number.** `04` L1557 states the symmetry explicitly — *"`0/280` alone is
wrong by 280 …, and `280/280` alone conceals that"* — which is the property the ruling wanted and neither
branch had.

---

## C3 — F13's retention mechanism · **PASS**

**Ruling.** `05`'s `scope_kind` field, which `03` must read; only `DECLARED_CHARACTERISTIC` leaves the
denominator.

**1. One normative home, and it says so.** `05` L620 — *"THE RETENTION RULE (arbitration C3), and it is
binding on `plan/03` as well as on this document"*. `03` L1230 answers in the same words from the other
side, in code:

> `# scope_kind, imported -- NOT redefined here.  Its home is plan/05 P9-B1 (src/cdfc/probes/relations.py).`

**2. The two statements are byte-identical.** `05` L623–625 and `03` L1518–1520 differ only in the
position of a final full stop, and both match `11` L77–78. There is no second version of the rule to drift.

**3. The field is written AND read — which is the half F13 survived on last time.**

- **Written:** `05` L2799 — `applicable()` returns `ScopeKind` instead of `bool`; `05` L658 fixes the
  vocabulary `IN_SCOPE | DECLARED_CHARACTERISTIC | PREDICATE_PRECONDITION`; unit test
  `test_td__scope_kind_distinguishes_declared_from_precondition` at L794 asserts both branches **and**
  that an `OUT_OF_SCOPE(not_applicable)` with no `scope_kind` fails to construct.
- **Read:** `03` L1257 `in_scope(state, reason, scope_kind)`; L1264 `return scope_kind !=
  "DECLARED_CHARACTERISTIC"`; L1267 `requalification_flag()`; `MissingScopeKindError` on absence at L1638;
  and **`test_contract__scope_kind_is_read_not_ignored`** (L1374), an **AST scan** asserting
  `settled_fraction.py` and `closure.py` reach `scope_kind` on every `OOS_NOT_APPLICABLE` path.

  An AST scan rather than a behavioural test is the right instrument here and `05` L2834 says why: a
  behavioural test passes on a build that ignores the field whenever the fixture happens not to exercise
  the branch. This is the single most important line in the C3 repair.

**4. Every document that removes an item from the denominator obeys it.** Only two do.
`grep -nE 'cellsTotal *[−-] *outOfScope|inScope *=|in_scope\('` returns `03`, `05` and the two historical
documents. `05` L627 gives the corrected formula
`inScope = cellsTotal − outOfScope[DECLARED_CHARACTERISTIC] − informational`; the two remaining
old-form occurrences (`05` L608, L902) are the statement of the defect and the `measured_instance` of
NC-R01. No third document computes the denominator.

**5. The 31st reason code is deleted, not softened.** `03` L1299 — *"C3: there is NO
`out_of_scope.precondition_degenerate`"* — vocabulary stays at 30, and `01` L2431 confirms the 8 × 31
exhaustive product it pinned does not move. `03` L1882 records that C3 *"already refused this once"* and
uses it as precedent, which is the corpus learning from its own ruling.

---

## C4 — P0's pre-registered gate set · **PASS** *(one caveat)*

**The deleted test name appears in no normative document as a live guard.**

```
grep -n 'pending_set_is_exactly_the_four_named_rows' plan/*.md
  00 L438    *"This box previously read … guarded by test_p0__… The old guard is DELETED, not renamed"*
  00 L1816, L1854   repair-log rows recording the deletion
  11 L90, L96 · 10 L356, L374    the ruling and the verification
  08 L311, L1251                 the adversary's original proposal  <- see caveat
```

**The surviving enumeration closes arithmetically.** `LIVE = {1…13, 17, 18}` = 15 rows;
`PENDING = {14, 15, 16}` = 3 rows; **15 + 3 = 18**. Carried identically in `00` L429/L1753, `02` L3224 and
`09` L312. The ratio is `15 / 15 of 18` in all three; the retired `12 / 12 over 16 rows with 4 pending`
survives only in `02` L1057, `09` L314 and `09` L769, each as a correction record.

**CAVEAT, recorded rather than waved through.** `08-adversary.md` L311 and L1251 still name
`test_p0__pending_set_is_exactly_the_four_named_rows` **as a live instruction** — L1251 is item 10 of
"THE TEN TESTS", which `10` §2 tracks as a build obligation. `08` carries no arbitration annotations at
all (`grep -c 'arbitration|REPAIRS APPLIED' 08-adversary.md` → **0**) and its mtime predates the repair.
**I did not edit it**, because `08` is the adversary's own record and rewriting a finding to match its
resolution destroys the evidence trail the corpus is built on — but a builder working from `08` §10 will
write a test whose name asserts a count that is wrong. The right repair is a superseded-by note, and it
is the owner's to write, not a verifier's.

---

## C5 — `TEMPLATE-COMPUTED` in a gate · **FAIL**

**Ruling (`11` L101–110), quoted in full because the failure is against its general clause, not its
example:** *"`TEMPLATE-COMPUTED` is a **smoke test only**: it may not be cited in a gate, in a severity
tier, or in any published rate. `03`'s exit criterion 1a is downgraded to a non-gating smoke check…"*

**`03` complied, completely.** L1808 — *"SMOKE CHECK — NON-GATING. NOT AN EXIT CRITERION.
`TEMPLATE-COMPUTED` MAY NOT BE CITED IN A GATE."* `05`, `06` and `07` are clean: `05` L979 has the
exit-gate evaluator **refuse a `TEMPLATE-COMPUTED` corpus id**; `06` L187 makes it `comparable = False`;
`07` L1144 caps the `RESTRICTED` branch at the licensed classes.

**`04` does not comply, and never recorded the ruling.**

> **`04` L1367**, G3's empirical arm, first row:
> `| Clean-corpus firing | flags `≤ 50%` of the clean corpus | Against the `TEMPLATE-COMPUTED` corpus at P7; re-run against `BLIND-FILLED` at P8 |`

That is a **gate threshold evaluated against the synthetic corpus class**. It is licensed by four further
lines: `04` L98 (*"Using `TEMPLATE-COMPUTED` at G1 and G3ᵉ is using it as an **execution substrate**, which
is legitimate"*), L853 (entry criterion E7.5), L1653 (E8.3) and L1832 (*"it is an **execution substrate**
for G1 and G3ᵉ, which is all §0.3 ever needed"*). `09` L522 carries the same decision forward into the
operating manual.

**Why the "execution substrate" defence does not hold for G3ᵉ.** At G1 the corpus is a substrate: binding
is structural and the derived values do not decide the outcome. At G3ᵉ the measured quantity **is** a
false-firing rate, and `04` §0.3 itself proves the objection two paragraphs earlier: on a
`TEMPLATE-COMPUTED` filing the 277 arithmetic predicates *"assert exactly the identities `calc/` enforced
when it wrote the file, so their false-failure rate on that corpus is zero by construction, at expected
value zero **regardless of predicate quality**"*. A gate whose threshold is `≤ 50%` and whose measured
value is structurally `0%` is not a gate. **`04` states the reasoning that condemns its own G3ᵉ row and
does not apply it there.** That is F2 in its original costume, inside the document that closed F2.

**The mechanism of the miss, which is the general lesson.** `11` C5's operative sentence names `03`;
`04`'s arbitration table (L2487–2490) records **C2, C6 and C9 only**. A ruling written as *"X's criterion
1a is downgraded"* was read as a ruling *about X*, so the document that had the second instance never
opened the file. Per-document coverage of the nine rulings:

```
00: C1 C2 C4 C6 C8a C9      03: C2 C3 C5 C9        06: C6 C8a C9
01: C1 C3 C9                04: C2 C6 C9   <-- no C5
02: C1 C4 C6 C7 C8b C9      05: C1 C3 C6 C9        07: C2 C9      09: C4
```

**Not repaired here.** Moving G3ᵉ's clean-corpus arm onto the `HAND-COMPUTED` filing (`03` E6, built at
`02` P3-B4, available before P7) or declaring the P7 measurement non-gating with the P8 `BLIND-FILLED`
re-run as the gate are both defensible, and choosing between them changes when a phase can exit. That is a
gate-semantics decision and belongs to `04`'s owner. A verifier who silently re-founds a gate has done the
thing this corpus exists to prevent.

---

## C6 — the `k = 0` critical path · **PASS**

**`~118` is the number of record, and the arithmetic closes.** `00` L1603–1604:

```
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P12 → P13
 4    8    10   12   14   12  10.5  16   9.5    6     16    =  118 working days
```

Re-added independently: `4+8+10+12+14+12+10.5+16+9.5+6+16 = 118`. ✓ The `k = 0` re-route
(`P7 ends 86 → P9 ends 100 → P10 ends ~106 → P11 ends ~116`) is tied by, not longer than, the spine, so
`~118` is correct for both branches — `00` L1635, `05` L1490 and `06` L2374 now agree on both the chain and
the total.

**The retired figure does not survive as a critical-path number anywhere.** All ten `~114` occurrences in
`00`–`07` and `09` are explicit retirements: `02` L548 (*"the pre-revision `~114` is retired and must not
be re-quoted from this document or any other"*), `05` L1490/L2810/L2851, `06` L2376/L2611. `08` L899–918
is the adversary's original computation, which is where the number came from.

**The stale-number-by-instruction is deleted, not corrected** — `06` L2611: *"the instruction telling `00`
to carry `~114` is **deleted rather than corrected** — a stale number propagated by instruction is worse
than one held alone"*. That is the right shape: correcting the instruction leaves a second writer for a
number with one owner.

**`04`'s third value is gone too.** `04` L2489 repoints §5 O5's `~116` at `00` §7's `~118`; L2319 now
reads `~118`.

---

## C7 and C8 — one name each, no orphan guards, the deleted path · **PASS**

| Split | Winner | Occurrences of the winner | Occurrences of the loser |
|---|---|---|---|
| **C7** arm-2 author test | `test_arm_two_author_is_not_the_evaluator_author` | `00`×2 `01`×3 `02`×6 `05`×2 | `02` L3274 only (the rename record) |
| **C8(a)** prereg test | `test_contract__preregistration_criterion_is_machine_evaluable` | `00`×2 `01`×3 `06`×7 `07`×2 | `06` L2612 only (the rename record) |
| **C8(b)** doc path | `docs/EVALUATION-CONTRACT.md` | `00` `02` `04` `05` | — |

`docs/RECALCULATION-SOURCE.md` survives at `02` L2604, L2666, L3020 and L3215 — every one a deletion
record, and L3020 is the repointed cross-reference the ruling asked for: *"(not a separate
`docs/RECALCULATION-SOURCE.md`)"*. `02` L3215 states the reason the ruling gave — the rule is a *generated
section* of `EVALUATION-CONTRACT.md`, so P5's byte-identity gate survives the merge. **No orphan guard
remains on either loser.** Both losers appear in `08` as originally proposed; see the C4 caveat, same
disposition, same reason.

---

## C9 — THE CATALOGUE · **PASS** *(after one repair, recorded in §CHANGES)*

### C9.0 — the instruments disagree, and that is the finding

Three instruments have now enumerated this catalogue. **`scripts/nc_audit.py`, run today against the
repaired corpus, reports 24 duplicate definitions, 2 orphans and 62 dangling references — and the corpus
is clean.** The reason is structural and worth stating, because it is the same failure as the NUL byte:

`nc_audit.py` counts any table row whose first cell is an id as a *definition*. `01` §2.2 (the RETIRED
list) and `01` §2.3 (the old→new mapping) are **required by C9.2 and C9.4** to be tables whose first cell
is a retired id. So the ruling's own audit trail is read as 24 live definitions, and **the better the
repair documents itself, the worse the instrument scores it.** An instrument that cannot distinguish a
retirement record from a definition cannot certify a repair whose entire content is retirement records.

`scripts/catalogue_check.py` classifies each region structurally before counting: ENTRY tables, MAPPING
tables (header names `old id` / `new id` / `retired id` / `held by`), the BAND table, and history-note
blocks — matching `01` §2.4 rule 4's two written exemptions rather than guessing. Two calibration
decisions are load-bearing and both were made against evidence:

- **Block-level, not line-level, history marking.** `02` R5a carries `RETIRED permanently` two lines below
  the id it retires; a line-scoped instrument reports the retirement record itself as a dangling
  reference.
- **A retirement *signal*, not the word "retired".** A first attempt matched the bare substring and
  swallowed `07`'s `NC-A30` entry — which is *about* retiring a surface row — then reported `NC-A30` as
  dangling at six sites. **An over-broad exemption is the same failure as none, pointed the other way: it
  hides what the check exists to find.** A block containing a `- id: NC-…` line is now a definition,
  whatever words appear inside it.

The instrument's own positive controls sit at the top of its output and it **aborts rather than reporting
clean** if they fail. They caught a refactor bug in this pass, on the run before the one reported below.

### C9.1 — verbatim output of `plan/scripts/catalogue_check.py`

```
=== NC CATALOGUE CHECK (arbitration C9) — 13 documents in /Users/abishaikc/Gift/plan ===

POSITIVE CONTROLS
  definition parser sees a synthetic entry row  : True   (expect True)
  NUL detector on a file WITHOUT a NUL          : 0      (expect 0)
  NUL detector on a file WITH one real NUL      : 1      (expect 1)
  instrument trustworthy                        : True

NUL-BYTE AND ENCODING SCAN (binary read; a shell cannot pass NUL as argv)
  00-decomposition.md                  167814 B  NUL=0  enc=utf-8
  01-validation-methodology.md         189396 B  NUL=0  enc=utf-8
  02-phases-foundation.md              225296 B  NUL=0  enc=utf-8
  03-phases-verdict.md                 167103 B  NUL=0  enc=utf-8
  04-phases-qualification.md           212707 B  NUL=0  enc=utf-8
  05-phases-probes-attestation.md      219324 B  NUL=0  enc=utf-8
  06-phases-model-and-clause.md        183862 B  NUL=0  enc=utf-8
  07-phases-surface-and-transfer.md    171949 B  NUL=0  enc=utf-8
  08-adversary.md                       80685 B  NUL=0  enc=utf-8
  09-operating-manual.md                71884 B  NUL=0  enc=utf-8
  10-repair-verification.md             42247 B  NUL=0  enc=utf-8
  11-arbitration.md                     10188 B  NUL=0  enc=utf-8
  12-arbitration-confirmed.md           34797 B  NUL=0  enc=utf-8
  files containing NUL: 0 of 13   (must be 0)

RETIRED IDS read from `01` §2.2: 33
  NC-A21, NC-E09, NC-N07, NC-N15, NC-N20, NC-N21, NC-Q12, NC-Q13, NC-Q14, NC-Q15, NC-Q16, NC-Q22, NC-Q22b, NC-Q23, NC-Q24, NC-Q25, NC-Q26, NC-Q27, NC-Q28, NC-Q29, NC-Q40, NC-Q41, NC-Q42, NC-Q43, NC-Q44, NC-Q45, NC-Q46, NC-Q49, NC-Q50, NC-Q51, NC-Q52, NC-Q53, NC-Q54

COUNTS
  distinct ids DEFINED            : 196
  total definition sites          : 199
  distinct ids REFERENCED (live)  : 171
  total live reference sites      : 617
  distinct ids in history/exempt  : 129
  DUPLICATE definitions (2+ docs) : 0     (must be 0)
  same-doc index restatements     : 64    (informational)
  cross-doc amendments (*amended*): 1    (informational)
  DANGLING (ref'd, never defined) : 0     (must be 0)  <- C9.5
  entries with no prose cross-ref : 25    (informational, NOT an error)
      `10` §4.3 and C9.5 define an ORPHAN as *referenced, defined nowhere* —
      the DANGLING line above.  `01` §2.4 rule 3 defines the orphan GUARD test
      over `tests/negative/` functions, which do not exist yet.  A catalogue
      entry that no prose sentence happens to cite is the normal, healthy state
      of a catalogue and is reported here only so the number is not hidden.
  RETIRED ids REDEFINED           : 0     (must be 0)
  RETIRED ids in a LIVE reference : 0     (must be 0)
  BAND TABLES in the corpus       : 1     (must be 1)
      01-validation-methodology.md:664

ENTRIES WITH NO PROSE CROSS-REFERENCE (informational)
  NC-A08  defined at 07-phases-surface-and-transfer.md:550
  NC-A11  defined at 07-phases-surface-and-transfer.md:582
  NC-A12  defined at 07-phases-surface-and-transfer.md:598
  NC-A14  defined at 07-phases-surface-and-transfer.md:808
  NC-A16  defined at 05-phases-probes-attestation.md:2291
  NC-A17  defined at 05-phases-probes-attestation.md:2303
  NC-A18  defined at 05-phases-probes-attestation.md:2315
  NC-A19  defined at 05-phases-probes-attestation.md:2418
  NC-A20  defined at 05-phases-probes-attestation.md:2481
  NC-C05  defined at 05-phases-probes-attestation.md:1956
  NC-C06  defined at 05-phases-probes-attestation.md:1968
  NC-C07  defined at 05-phases-probes-attestation.md:1797
  NC-C08  defined at 05-phases-probes-attestation.md:1980
  NC-C09  defined at 05-phases-probes-attestation.md:1992
  NC-N16  defined at 02-phases-foundation.md:3072
  NC-N22  defined at 05-phases-probes-attestation.md:2654
  NC-N23  defined at 05-phases-probes-attestation.md:2655
  NC-N25  defined at 05-phases-probes-attestation.md:2652
  NC-N26  defined at 05-phases-probes-attestation.md:2653
  NC-N33  defined at 06-phases-model-and-clause.md:2465
  NC-R02  defined at 05-phases-probes-attestation.md:851
  NC-R04  defined at 05-phases-probes-attestation.md:874
  NC-R05  defined at 05-phases-probes-attestation.md:1189
  NC-R06  defined at 05-phases-probes-attestation.md:1253
  NC-R07  defined at 05-phases-probes-attestation.md:1359

VERDICT: CLEAN
wrote /Users/abishaikc/Gift/plan/scripts/catalogue_check_result.json
```

### C9.2 — the statistics against C9's five sub-rulings

| Statistic | Value | Required | Verdict |
|---|---:|---|---|
| distinct ids **defined** | **196** | — | — |
| definition **sites** | **199** | — | 3 registry rows for ids also entered elsewhere |
| distinct ids **referenced** (live) | **171** | — | — |
| live reference **sites** | **617** | — | — |
| **duplicates** (defined in ≥ 2 documents) | **0** | 0 | **PASS** — was 10 at `10` §4.2 |
| **orphans** — *C9.5 / `10` §4.3 sense:* referenced, defined nowhere | **0** | 0 | **PASS** — was 13 |
| **dangling** — referenced but never defined | **0** | 0 | **PASS** |
| **retired ids redefined** | **0** | 0 | **PASS** — 33 ids retired, none reassigned |
| **retired ids in a live (non-history) reference** | **0** | 0 | **PASS** |
| **band tables** | **1** | 1 | **PASS** — was 4 (`02` R5a, `04` §0.8, `05` §4, `07` §3), all deleted with notes |
| entries with no prose cross-reference | 25 | — | informational; not an error under any rule |

**Definition sites by document** (`01` allocates; the entries' shapes live where they are built):

```
01  47      02  24      03  12      04  21      05  29      06  39      07  23      = 195 + 1 registry-only row
```

**The two brand-new collisions the repair created are both gone.** `NC-Q45` and `NC-Q46` are retired;
`03`'s `Q45` was **merged into `NC-Q57`** rather than renumbered, because it was the same break with the
same injector as `04`'s former `NC-Q42` — one break, one entry, one id. That is the right call and it is
the only place C9 exercised judgement instead of mechanism, with the reason written down.

**Renumbering was mechanical.** Every contested id went to a *new* number on both sides — `NC-Q40`–`Q46` →
`Q70`–`Q75` (`03`) and `Q55`–`Q61` (`04`); `NC-N20`/`N21` → `N50`/`N51` (`04`) and `N25`/`N26` (`05`);
`NC-N07` → `N16` (`02`) and `N40` (`07`) — and **no side kept the contested number.**

**`NC-L01` — placement wart, not a defect, recorded.** C9 found it orphaned in `07` and registered it, but
its only registry row sits **inside the RETIRED list table** (`01` L714), distinguished from a retirement
only by the parenthetical *"(`NC-L01` is **not** retired)"*. It resolves, and `07` L1920 now points at a
real row. A reader — or a parser — scanning §2.2 for retired ids will read it as retired unless it handles
that one negation. It belongs in §2.7 beside the other `01` entries.

---

## 9. NUL-BYTE AND ENCODING SCAN, WITH THE POSITIVE CONTROL · **PASS**

**Result: 0 NUL bytes across all 12 documents; all 12 decode as UTF-8** (see the scan block in §C9.1;
`raw.decode("utf-8")` with no `errors=` fallback, so a bad byte raises rather than being replaced).

**The positive control, and it is worse than the brief anticipated.** Two synthetic files, one containing
a real `\x00`:

```
$ od -c ctl_nul.md
0000000   #  d i r t y   c o n t r o l \n
0000020   t h i s   l i n e   h a s   a
0000040  \0     n u l \n

--- THE NAIVE SHELL TEST: grep -l $'\0' over 14 files ---
matched: ctl_clean.md 00-… 01-… 02-… 03-… 04-… 05-… 06-… 07-… 08-… 09-… 10-… 11-…   (13 files)
clean control matched?          YES — FALSE POSITIVE
grep -c $'\0' ctl_clean.md      2      (the file has 2 lines; every line "matches")
grep -l $'\0' ctl_nul.md        exit=1 — NO MATCH
file --mime-encoding ctl_nul.md binary
grep -ac $'\0' ctl_nul.md       2      (with -a, it is found)
```

**The naive test is not merely wrong, it is inverted.** The shell truncates the argument at the NUL, so
the pattern degenerates to the empty string and matches **every line of every clean file** — 13 false
positives — while the one file that actually contains a NUL is classified `binary` and **skipped
entirely**, exit 1, silently. A person who writes the obvious check gets a wall of hits that do not
matter and a miss on the only thing that does.

That is precisely the failure `01` §2.4 records — *"One raw NUL byte in `03` made GNU/BSD `grep` skip the
whole document silently, and this gate — the one written to catch id collisions — would have run green
over the largest instance of them in the repository"* — and it confirms that `01`'s mandated fix is the
right one and is not optional: **`ci/catalogue-ids.sh` must assert `file --mime-encoding` is `utf-8` for
every scanned path, or use `grep -a`, before grepping it.** Both branches are demonstrated above.
`catalogue_check.py` reads binary and never depends on either.

---

## CHANGES I MADE

One repair, applied because its target is unambiguous under C9.3.

**`NC-Q22` was a live allocation pointing at an id whose content had left twice, defined nowhere.**

- Found by: `catalogue_check.py` reported `NC-Q22` referenced at `04` L2028 and defined nowhere, while
  `01` §2.1's band table allocated `Q22` to `04` and `04` §0.8 L257 claimed it in *"Allocated to this
  document in total"*.
- Established: `04` §0.8 L237–238 records the earlier pass's `Q22 → Q40`, and C9 then moved `Q40 → Q55`.
  So `NC-Q22`'s content is at `NC-Q55`, and the number was vacated twice while still being allocated.
  `08` L507 confirms it once held an entry (*"`NC-Q22b` (new, under `NC-Q22`'s entry)"*).
- **Why the target is unambiguous:** this is the identical shape to `NC-Q12`–`NC-Q16`, which `01` §2.2
  already retires as *"historical ids … vacated"*. C9.3 states that a vacated id is retired permanently
  rather than reassigned; re-issuing it to `04` is the mechanism C9.3 exists to stop.

| File | Line | Change |
|---|---|---|
| `01-validation-methodology.md` | §2.2 L708 | **added** a RETIRED row for `NC-Q22`, with its two-step vacation and its content's home (`NC-Q55`), marked as added by this pass |
| `01-validation-methodology.md` | §2.1 L668 | **removed** `Q22` from the `Q`-band's `04` allocation |
| `04-phases-qualification.md` | §0.8 L257 | **removed** `NC-Q22` from *"Allocated to this document in total"*, with a dated note giving the reason and preserving the one surviving history mention inside `NC-Q56`'s entry |

After the change: dangling **0**, retired-in-live-reference **0**, duplicates **0**, band tables **1**.

**Files added:** `plan/scripts/catalogue_check.py` (the instrument), `plan/scripts/catalogue_check_output.txt`
(this run, verbatim), `plan/scripts/catalogue_check_result.json` (machine-readable).

**Nothing else was edited.** In particular I did **not** repair C5, and I did not touch `08-adversary.md` —
reasons in §C5 and the §C4 caveat.

---

## RESIDUAL FINDINGS — no ruling covers these

### R1 — the guard test for C1's frozen constant has two names · SMALL, SAME SHAPE AS C7

| Name | Document | What it asserts |
|---|---|---|
| `test_gate__d_predates_the_first_fixture` | `02` L2791, L3011, L3212 | the `PREREGISTRATION.md` commit is a git-ancestor of the first fixture's |
| `test_e_eval__d_is_preregistered` | `01` L380, L2382 | the constant's commit is a git-ancestor of the first `engine_disagreement` row's |

Same property, two names, two owners — `02` owns the constant, `01` owns the taxonomy. This is C7's defect
on C1's constant, and it did not exist in `10` §2's list, so it is either new in the repair or was never
checked. `05` adds a third, `test_geval__disagreement_above_d_downgrades_g2`, which is a genuinely
different assertion and is fine. **Under `test_nc_meta__no_orphan_guard` one of the first two is an orphan.**

### R2 — `ci/catalogue-ids.sh` has two incompatible specifications, in the C9 repair itself · **SERIOUS**

> **`02` L436:** *"asserting that each `NC-` id appears as a definition in **`plan/01` only**"*
> **`05` L2647:** *"asserting every `NC-` id appears as a definition in **exactly one document**, and that
> each id falls inside its owning document's declared range"*
> **`01` §2.4 rule 2:** *"… and **every id defined outside this document fails**"*

`01`'s own §2.1 allocates ranges to `02`–`07` and `02` R5a confirms *"`02` still owns its ids … their
detail lives in this document's §X catalogue tables."* **148 of the 196 entries are defined outside
`plan/01`.** Under `02`'s and `01` rule 2's literal reading the gate fails on all 148 on its first run;
under `05`'s reading it passes. One CI script, two specifications, and whichever a builder implements the
other document says is wrong.

This is the same class of defect as the four band tables — *one contract, more than one writer* — recreated
inside the ruling that ended them, three documents apart. The fix is a sentence, and it should be `05`'s
wording, because `05`'s is the one that matches the band table `01` actually wrote: **an id is *registered*
in `01` and *entered* in its owning document; the gate checks that every id resolves to exactly one registry
row and lies inside its owner's allocation.**

### R3 — `08-adversary.md` is unannotated and still issues superseded instructions

`grep -c 'arbitration|REPAIRS APPLIED' 08-adversary.md` → **0**. It still names
`test_p0__pending_set_is_exactly_the_four_named_rows` (§10, item 10 of "THE TEN TESTS"),
`test_arm_two_oracle_is_a_different_author` (§9) and `test_e6__preregistration_criterion_is_machine_evaluable`
(L843) — all three C4/C7/C8 losers — as things to build. `10` §2 correctly tracks them as losers, but a
builder reading `08` §"THE TEN TESTS" directly gets the retired names. A header line pointing at `11` and
`12` would close it without touching a single finding.

---

## WHAT THIS CONFIRMATION DOES NOT SETTLE

Unchanged from `11`, and re-verified as still correctly open:

- **F27** remains the one SERIOUS finding not closed. Every one of `00`–`07` restates this in its
  arbitration section, in the same words, which is the correct behaviour for a finding whose residue
  outlives its repair.
- **F37 and F43** keep their explicit `OPEN — USER DECISION`, listed in the operating manual.
- **`K` and `T`** still render the literal string `PLACEHOLDER` with no argued basis. Verified: still
  `PLACEHOLDER`, still unargued, still correct.

---

## VERDICT

**The plan is internally consistent enough to build from, with one blocking exception.**

Eight of nine checks pass on evidence, and the two things that had failed twice — the catalogue and the
NUL-blinded scan — are now closed and *mechanically re-checkable*, which is the part that matters more than
today's zero. `plan/scripts/catalogue_check.py` reproduces the enumeration, carries its own positive
controls, and aborts rather than reporting clean when they fail.

**Do not start P7 until C5 is closed in `04`.** `04` L1367 gates G3ᵉ on a corpus that makes 277 of 515
predicates pass by construction, and `04` §0.3 contains the argument for why that is wrong. It is a
one-row decision with a phase-timing consequence and it belongs to `04`'s owner.

**R2 should be closed before P0-B3**, because `ci/catalogue-ids.sh` is required to exist *before the first
catalogue entry is written*, and a gate with two specifications is not a gate. R1 and R3 are cheap and can
ride along.

**The process lesson from `11` held, and is worth stating as evidence rather than as advice.** The repair
was run serially, one writer at a time, and produced **zero** new cross-document contradictions on the nine
ruled seams — against eight from the parallel pass. The two residues that did survive (C5 unapplied in
`04`, R2's two gate specifications) are both the *same* failure in a milder form: a ruling addressed to one
document was not read by the document that had the second instance. **One writer at a time fixed the
collisions; it did not fix the reading.** The next pass wants a per-document checklist of all nine rulings,
signed off as applied-or-not-applicable, rather than each owner deciding which rulings were addressed to
them.
