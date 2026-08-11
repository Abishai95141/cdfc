# 01 — THE VALIDATION METHODOLOGY

**The standard every phase specification in this plan is written against.**
Compiled 11 August 2026 · binds `/Users/abishaikc/Gift/spec/00`–`05` · no dates, no hackathon

---

## §0 — WHY THIS DOCUMENT EXISTS, AND THE ONE RULE THAT GENERATES ALL THE OTHERS

The product exists because **a silent pass is not information**. The research corpus contains five
instances of clean, confident, well-formed, wrong output from **deterministic programs** — three committed
by this project's own team, one by the harness built to detect the others, and one by the ecosystem
default spreadsheet library. All five under-reported. All five under-reported *in the direction that
supported the thesis*. None of them raised, logged, or looked wrong.

Therefore:

> **A green test suite is not evidence. A test that has never been observed to fail is not evidence.
> Every acceptance test in this plan ships with a named, mechanically injectable, deliberately broken
> build or input that the test MUST reject — and CI proves the rejection happens by injecting the break
> and watching the test go red.**

That is the negative-control rule, and §2 is its catalogue. Everything else in this document exists to
support it, to measure the tests themselves (§3), to make a build's compliance checkable by someone who
did not do the work (§4), to run it (§5), to feed it (§6), and to declare what it still cannot catch (§7).

### 0.1 Warrant labels, used in this document exactly as in the spec

`MEASURED` — computed first-hand against an artifact on disk, script and date named ·
`VERIFIED-AT-SOURCE` — the primary document was opened and the clause read ·
`SECONDARY` — a credible source states it, the primary was not opened ·
`DERIVED` — arithmetic on stated inputs, carrying the warrant of its weakest input ·
`MODELED` — an assumption with its arithmetic shown ·
`NOT-FOUND` — we looked and could not settle it.

**Every licence in this document is `SECONDARY` unless explicitly marked otherwise, because no LICENSE
file was opened in the session that produced this document.** The one exception recorded in the spec is
in-toto / DSSE, **Apache-2.0, VERIFIED-AT-SOURCE**. §5.2 makes opening the rest a blocking Phase-0 gate
with a test that tracks the ledger.

### 0.2 Measurements taken while writing this document

Re-run so this document rests on artifacts rather than on the spec's summary of them.
Script: ad-hoc `lxml` + `openpyxl` probes, `/Users/abishaikc/Gift/.venv/bin/python`, 11 Aug 2026.
These are the fixture facts §6 pins and §2 breaks.

| Quantity | Value | Warrant |
|---|---|---|
| Formula-bearing cells across the nine prescribed workbooks | **1,495** | MEASURED |
| Of those, empty-text shared dependents (`<f t="shared" si="N"/>`) | **825 = 55.2%** | MEASURED — reproduces the spec's figure exactly |
| FME workbook (`sha256 7d9a1960…`) formula cells / authored / shared | **505 / 294 / 211** | MEASURED — reproduces `test_schema_constants` |
| FME data validations, main + `x14` | **35 + 19 = 54** | MEASURED |
| FME `7. AML-CFT` validations: openpyxl 3.1.5 vs truth | **0 vs 5** (all five are `x14`) | MEASURED |
| **openpyxl undercount instances across the nine workbooks** | **three, not one**: FME 35 of 54 · `AL_monthly_report` **1 of 10** · `ITFS_Monthly_report` **7 of 16** | MEASURED — new |
| Workbooks shipping **no** sheet-protection mask | **two**: `Draft_ACAC_Format` (0 of 13 sheets protected, 0 unlocked style ids) and `IFSCA_Annual_Reporting_Format` (0 of 9 protected, **1 unlocked style id → a plausible-looking field surface of 8**) | MEASURED — new, and see NC-D03 |
| Workbooks with zero formula cells | **two**: `EDR_1`, `IFSCA_Annual_Reporting_Format` | MEASURED |
| `re.findall(r"<f[ >][^>]*>")` over FME sheet XML | **count equals the true formula-cell count on every sheet, and 50 of 50 matches on `2. Summary` swallowed the closing `</f>` tag** | MEASURED — new, and it generates rule R-GOLD-2 below |

**The last row is the most useful thing measured for this document.** A defective matcher produced a
*correct count* and *wrong bodies*. A golden test asserting only `n_formula_cells == 505` passes against
it. Hence:

> **R-GOLD-2 — a golden test asserts values, not only counts.** Every count assertion is paired with at
> least one value assertion drawn from the same extraction. Enforced by `ci/golden-asserts-values.sh`
> (§5.3 stage 6) and by the reviewer checklist item D6 (§4).

### 0.3 The nine fixture workbooks, pinned

`fixtures/prescribed/` — committed byte-for-byte, `origin_uri` and `retrieved_at` in
`fixtures/prescribed/MANIFEST.json`, integrity asserted by `tests/golden/test_fixture_integrity.py`.

| File | sha256 | bytes | sheets (hidden) | protected | formula cells | validations (main + x14) | field surface |
|---|---|---:|---:|---:|---:|---:|---:|
| `Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx` | `7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39` | 3,663,391 | 10 (1) | 9 | 505 | 35 + 19 | **3,747** |
| `Updated___Quarterly_Reporting_Format_for_Capital_Market_Intermediaries_20260409_1019.xlsx` | `82dd291f5a7d6667f10b39ffb8770b4eae589bc03d31869e6d5e2f6564452671` | 3,720,205 | 18 (0) | 17 | 33 | 142 + 0 | 2,255 |
| `ALR_V2_3_20250808_1024.xlsx` | `a414d8d3300d884e06c89eff92cf9f9857bad5690fd38266375979b784c8b998` | 55,501 | 9 (0) | 9 | 645 | 7 + 0 | 1,599 |
| `AL_monthly_report_updated_final_20260717_0257.xlsx` | `79e43a7fdbbec9d993fb983c1bcbfc3162be13c2fe3a40ffb3a28abead87c6a9` | 41,181 | 4 (1) | 3 | 161 | 1 + **9** | 3,537 |
| `Draft_ACAC_Format_20260605_0631.xlsx` | `74ba7b894b429bbe939a296cacf39196ad9f5b93ec238037f2c47c277dd79e5e` | 83,409 | 13 (0) | **0** | 112 | 0 + 0 | **n/a** |
| `IBU_Operations_Report_V2_3_20250808_1033.xlsx` | `bf6bbf6b810f8afc571232e9b72c070a5f6a04519b13b8676d72a36682803556` | 34,577 | 8 (0) | 8 | 7 | 4 + 0 | 459 |
| `ITFS_Monthly_report201220241626.xlsx` | `446b811a2b06922c8f18f5a15af47ef803fe0f0f6b9963e381cf6a414dec8c16` | 23,079 | 2 (1) | 1 | 32 | 7 + **9** | 481 |
| `EDR_1__Exposure_Data_Report_1__V2_3_20250808_1030.xlsx` | `230a6f0c7f1bfad504167e52002e4dfb5f0014bf2c2968787b4e6f785f5774c1` | 24,124 | 3 (0) | 3 | **0** | 1 + 0 | 162 |
| `IFSCA_Annual_Reporting_Format_30April_2026_Approved_20260504_1247.xlsx` | `4b2d4a2bb0416ae22048c7cf1fcbb5c581c19933ca85663ab69f311a8846395d` | 33,299 | 9 (0) | **0** | **0** | 0 + 0 | **n/a** |

All MEASURED, 11 Aug 2026. Two workbooks have `field surface = n/a` because they ship no protection mask;
per §III.4.3 their `settledFraction` is `null` and their denominator source string is
`"not derivable — template ships no protection mask"`. **`IFSCA_Annual_Reporting_Format` is the dangerous
one: a naive unlocked-cell count returns 8, which looks like a small answer rather than like no answer.**
It is the flagship fixture for NC-D03.

### 0.4 Repository layout this document assumes

Every phase specification names paths inside it. Package `cdfc` (coverage-declaring filing checker).

```
/Users/abishaikc/Gift/
  LICENSE                                Apache-2.0 (spec G9)
  Makefile                               every command in §5 is a make target
  pyproject.toml                         pinned deps, pytest config, tool config
  EVALUATION-CONTRACT.md                 GENERATED from spec §II.3.4 (spec G5); never hand-edited
  docs/
    LICENCES.md                          per-dependency licence + warrant ledger (§5.2)
    ABSENCE-SCOPE.md                     the inclusion rule for any absence claim
    DOD-TEMPLATE.md                      §4 of this document, as a fillable checklist
    HARVEST-DELTA.md                     append-only log of every movement of test_harvest_count
    EQUIVALENT-MUTANTS.md                the adjudication ledger index (§3.4)
    GATE-CHANGES.md                      append-only; every gate threshold, scan set or clock that moved
    CATALOGUE-CORRECTIONS.md             append-only; every superseded mechanism, and the documents amended
    MEASUREMENT-CLASS.md                 the REACH / DISCRIMINATION / CENSUS ruling per published number (§0.5)
  src/cdfc/
    ingest/       receipt.py container_guard.py reader_lxml.py reader_openpyxl.py agreement.py
    schema/       induce.py styles_mask.py styles_mask_b.py stable_keys.py vocabularies.py manifest.py
    facts/        fact_table.py units.py
    predicates/   envelope.py harvest.py ast_walker.py registry.py host_fns/
    evaluate/     preflight.py contract.py celrt.py rollup.py
    verdict/      states.py reasons.py closure.py settled_fraction.py aggregate.py
    probes/       relations.py template_diff.py
    selfcheck/    canaries.py residue.py
    attest/       statement.py dsse.py verify.py schema/attestation.schema.json
    report/       render.py labels.py templates/
    qualify/      g0_scope.py g1_binds.py g2_kill.py g3_degeneracy.py g4_ffr.py
                  mutants.py observability.py wilson.py ilp.py
    measure/      absence.py ledger.py
    cli.py
  tests/
    unit/ property/ golden/ differential/ determinism/ relational/ perf/ contract/ e2e/
    negative/
      catalogue.yaml                     THE machine-readable negative-control catalogue (§2)
      injectors/__init__.py              INJECTORS: dict[str, Injector]
      broken_builds/                     the deliberately-wrong modules
      test_nc_ingest.py test_nc_schema.py test_nc_predicate.py test_nc_evaluate.py
      test_nc_selfcheck.py test_nc_attest.py test_nc_external.py test_nc_meta.py
    test_suite_census.py                 the suite may not silently shrink
  fixtures/
    prescribed/                          the nine, byte-identical, + MANIFEST.json
    adversarial/ synthetic/ predicates/ baselines/ corpus_manifest.json
  ci/                                    the shell gates named in §5
  perf/baseline.json  perf/baseline.ci.json
  reports/                               CI artifacts; validation-ledger.jsonl lives here
```

### 0.5 REACH IS NOT QUALITY — the classification every published number carries

**Repairs the class of error `09` §2.5 records for `MS = 18.09%`.** That figure was computed on the wrong
denominator, and the deeper defect is that *every arithmetic operator killed at exactly 18.1% — identical
to the fraction of seeded sites lying inside the field graph.* A number that equals the fraction of the
world a check can see is a measurement of **how far the check reaches**, not of **how well it
discriminates**. Both are legitimate; quoting one as the other is not, and nothing in this document
previously stopped it.

**Every row of `reports/validation-ledger.jsonl` carries a required `measures` field, from a closed set:**

| `measures` | What the number is | The one sentence it licenses | What it may never be called |
|---|---|---|---|
| `REACH` | how much of the field surface / fault population a check or a check-set can touch at all | *"N of M cells (or sites) lie inside the read set of at least one check."* | coverage that was *verified*; a quality, accuracy or kill rate |
| `DISCRIMINATION` | how a check behaves on the population it reaches, **with a control arm** | *"rejects K of O observable defects under fault model v_n, with U discarded and a control-arm spurious-fire count of S."* | a statement about defects outside the fault model (§7.2) |
| `CENSUS` | a count of artifacts, entries, sites or rows | *"there are N of these, enumerated by <command>."* | evidence that the N is complete |

**The two reach numbers live in this plan right now, and neither is a quality measure. Both are quotable
only in the forms below, and both are `REACH`:**

- **`2,373 of 3,747` field-surface cells** (settled / `cellsTotal`, FME). Quotable as *"2,373 of the 3,747
  cells a filer may fill are bound by at least one harvested predicate, **PRE-GATE** — none of those
  predicates is admissible under G4 because no false-failure rate has been measured for any of them."*
  Never as *"63.3% checked"*, *"63.3% verified"* or *"63.3% coverage"*. The denominator's generating rule
  renders beside it (§2.2 NC-D02, and the protection-resolution ruling).
- **`511 of 2,826` numeric fault sites** (the sites the harvested predicate set can observe, of the sites
  the campaign seeds). Quotable as *"the admitted set's read closure intersects 511 of the 2,826 numeric
  sites the fault model seeds."* **This number is the ceiling on the kill rate, not the kill rate**, and a
  document that prints it beside a `K/O` without the word `REACH` has invited exactly the `18.09%`
  confusion.

**The rule, and it is a gate, not a preference:**

> **R-REACH-1 — no hero number is claimed until a false-failure rate exists.** A `REACH` row may not be
> rendered on any surface as the product's headline, may not be captioned with a verb of verification, and
> renders with its **admission state** (`PRE-GATE` until a G4 result exists over a corpus the product did
> not compute — §6.3, and `07` P14's `admission_state`). A `DISCRIMINATION` row may not render without its
> control-arm count (§2.3 NC-Q06c) and its observability census (`G · U · I · O · R · K`, six integers).

Mechanised in three places, none of them prose:
1. `tests/test_validation_ledger.py::test_ledger__every_row_declares_its_measurement_class` — `measures`
   is required and from the closed set of three.
2. `test_ledger__reach_rows_carry_no_quality_claim` — a `REACH` row whose `caveat` contains any of
   `verified | checked | correct | accurate | quality | kill rate | pass rate` fails the build. The
   `caveat` sentence is already required (§5.5); this constrains what it may say.
3. `docs/MEASUREMENT-CLASS.md` — one row per published number, `{metric, measures, argued_by, date}`,
   append-only. A metric whose class changes requires an appended argument, the same discipline as
   `docs/HARVEST-DELTA.md`. **A number that is quietly reclassified from `REACH` to `DISCRIMINATION` is
   the `18.09%` failure repeating with better manners.**

---

## §1 — THE TEST TAXONOMY

Ten classes. For each: **what it establishes**, **what it cannot establish** (stated because a class used
outside its warrant is how a suite goes green while the system is wrong), when it is required, the tool
with its licence warrant, naming, location, and CI stage.

### 1.0 Global conventions

- `pyproject.toml` sets `xfail_strict = true`, `--strict-markers`, `--strict-config`,
  `filterwarnings = ["error"]`. **A warning is an error.** openpyxl's
  `UserWarning: Data Validation extension is not supported and will be removed` is exactly the class of
  signal this project exists to stop discarding; it must fail a test, not scroll past.
- **A skipped test is a failed test.** `--runxfail` is never used; a `@pytest.mark.skip` requires a
  `reason=` naming a tracking id and is counted in the census (§5.3 stage 4).
- **Line coverage is reported and never gated.** It is precisely the shape of metric this project argues
  against — a number that rises by adding code that does nothing. `coverage.py` (Apache-2.0, SECONDARY)
  writes `reports/coverage.xml` as an artifact. The gates are the negative-control sweep (§2) and the
  mutation score (§3).
- Every test class has one entry point in the `Makefile`, so a phase gate can be evaluated by running a
  command rather than by reading a diff.

### 1.1 Unit

**Establishes**: that one function, given stated inputs, returns stated outputs — including its error
behaviour. **Cannot establish**: that the function is called, that it is called with real inputs, that
the composition of correct units is correct, or that the stated expectation is itself right. Every one
of the corpus's five silent false negatives would have passed a unit suite written by their authors,
because the author's expectation was the defect.

Required for: every public function in `src/cdfc/`, and **mandatorily** for every host function
(spec §II.4.2 — host functions are hand-authored, versioned, and carry their own test vectors and their
own kill rates).

Tool: **pytest 8.x** (MIT — SECONDARY). Naming: `tests/unit/test_<module>.py::test_<callable>__<behaviour>`
— e.g. `tests/unit/test_wilson.py::test_wilson__zero_of_four_upper_bound_is_0490`.
CI stage 4. Budget: whole class under 30 s.

### 1.2 Property-based

**Establishes**: that a stated invariant holds over a generated input space, with shrinking to a minimal
counterexample, and that every historical counterexample stays pinned. **Cannot establish**: anything
about inputs the generator does not produce. Hypothesis at `max_examples = 50` (spec's decided budget —
55% of mutations are found at n = 1, 76% within 20) explores a small fixed space; a property that holds
on all 50 and fails on a filing shape nobody generated is not caught. Mitigated only by `@example`
pinning of every real defect, which is required, not optional.

Required wherever a property exists. The mandatory ones, each with its generator:

| Property | Generator | Module |
|---|---|---|
| Closure: `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface` | random assignment of the 8 states over `N ∈ [1, 5000]` cells | `verdict/closure.py` |
| Roll-up precedence is a total order and `max` is associative and commutative | random multisets of the 8 states | `evaluate/rollup.py` |
| Money round-trip: `USD Million (2 dp) → MILLI_USD_MILLION → USD Million` is exact | `Decimal` with 2 dp over the representable `int64` range | `facts/units.py` |
| Wilson: `lo ≤ k/n ≤ hi` for all `0 ≤ k ≤ n ≤ 10⁶`; width strictly decreasing in `n` at fixed `k/n` | integer pairs | `qualify/wilson.py` |
| Set-FFR sub-additivity: `max(FFR(S), FFR(f)) ≤ FFR(S ∪ {f}) ≤ FFR(S) + FFR(f)` | random predicate fire-vectors over a corpus of `n` filings | `qualify/g4_ffr.py` |
| Kill-rate arithmetic: `K ≤ O ≤ G`, `U = G − O`, `KR = K/O ∈ [0,1]` — **never > 1** | random campaign tallies incl. degenerate ones | `qualify/g2_kill.py` |
| Stable-key resolution: for any row insertion, every key resolves to the correct ref **or** to `UNRESOLVED` — never to a different label pair | row-insertion transforms over the FME blank | `schema/stable_keys.py` |
| A reason code is present iff the state is not `PASS`/`FAIL` | the 8 × 31 product | `verdict/reasons.py` |
| RFC 8785 canonicalisation is order-invariant: shuffling a dict's insertion order does not change the digest | random JSON trees | `attest/statement.py` |
| **`test_prop__fraction_does_not_rise_as_the_filing_empties`** — for every filing `F` and every value-deletion transform `d`, `fraction(d(F)) ≤ fraction(F)` | value-deletion transforms over the reference fill (the generator `05` P9-B2 specifies for precondition monotonicity) | `verdict/settled_fraction.py` |

**The fraction-monotonicity row is new, is mandatory, and it is the one property the product's central
claim actually needs.** The plan already had the special case
(`test_prop__settled_is_monotone_non_increasing_in_not_run`); this is the general form. Its necessity: the
defence against the empty filing is a *non-degeneracy precondition* returning `OUT_OF_SCOPE`, and
`OUT_OF_SCOPE` is **removed from `inScope`**, which is the fraction's denominator — so the defence shrinks
the denominator and `settled / inScope` can **rise as a filer fills less**. `INFORMATIONAL` leaves
`inScope` by the same door, so an appended row of `template_defects.yaml` can raise the headline; the
companion property is `test_defect_table_cannot_raise_the_settled_fraction` (owned by `05` P9-B1).

**If the property fails — and by inspection it will — the repair is a design decision, not a tolerance.**
Exactly one of the following is taken and recorded in `docs/GATE-CHANGES.md`: (a) `OUT_OF_SCOPE` arising
from a *non-degeneracy precondition* stays in `inScope`, because it is a statement about the filing and
not about applicability; or (b) every surface rendering the fraction renders `inScope` and `cellsTotal`
side by side, so a shrinking denominator is visible in the same block (`07` P14, `REQUIRED_NUMBERS`).
**Both are defensible. Silently doing neither is the product's own failure mode.** The property is
BLOCKING at the phase that ships `settled_fraction.py`; a build may not ship with it `xfail`.

Tool: **Hypothesis** — **reported MPL-2.0, LICENSE not opened (SECONDARY)**. The spec's ban list forbids
writing "Hypothesis (MPL-2.0)" as a bare fact; this document obeys it. File-level copyleft is acceptable
for an unmodified dev-time dependency; open the LICENSE before shipping (§5.2).
Naming: `tests/property/test_prop_<module>.py::test_prop__<invariant>`.
Profiles: `fast` (`max_examples=50`, CI stage 5), `deep` (`max_examples=1000`, nightly, advisory).
Budget: fast profile under 60 s.

### 1.3 Golden / snapshot against the nine real workbooks

**Establishes**: that the pipeline's output over a *real regulator artifact* has not moved. This is the
only class that touches ground truth the project did not author. **Cannot establish**: that the pinned
value is right. `test_schema_constants` pins 505 — if the induction were wrong on day one, the golden
would pin the wrong number forever. The mitigation is not another test; it is that these particular
constants were derived independently by four research lanes and one adversarial pass, and that the
paired negative controls (NC-P01, NC-P02) prove the specific undercounting mechanisms are caught.

**The split is normative** (spec G8) and a phase may not merge it:

- `tests/golden/test_schema_constants.py` — **properties of the published file**, which must never move:
  `505 / 294 / 211 / 54 / 22 / 20 / 252 / 3747` for FME, plus the per-workbook table in §0.3.
  A change here is a parser regression, full stop.
- `tests/golden/test_harvest_count.py` — **properties of our code**: `280` (FME) and `515` (nine, always
  with the per-workbook distribution attached). Allowed to move **with a recorded reason**: the test reads
  the expected value from `docs/HARVEST-DELTA.md`'s last entry and asserts the entry's `reason` is
  non-empty and its `date` is set. Moving the number without appending an entry fails the build. The first
  time G3 rejects a harvested predicate, this number falls — which is correct behaviour, and a regression
  test that fails on correct behaviour gets deleted, which is why the split exists.

> **R-GOLD-3 — every integer literal compared in `tests/golden/` must be traceable to a warrant.** It must
> appear either in §0.3's fixture table (a property of the published file) or as a row of
> `reports/validation-ledger.jsonl` (a number this programme measured, with its denominator, warrant and
> re-run command). Enforced by **`ci/golden-literals-are-traceable.sh`** (§5.3 stage 2, §5.4), which
> extracts every integer literal appearing in a comparison inside `tests/golden/` and resolves it against
> those two sources; an untraceable literal fails the build. Planted control: a golden asserting a literal
> that appears in neither.
>
> **Why this is a gate and not a review item.** `07` §6 names the mechanism exactly — *a golden test
> launders a warrant*. An illustrative figure that gets pinned becomes a figure CI defends, and a figure CI
> defends gets quoted as measured. It happened twice in the drafts of `07` alone (the illustrative `12`;
> the per-sheet field surface relabelled as the unchecked split), and `07` §6 concludes that catching it is
> *"a review obligation ... the fourth impossible control"*. **It is not impossible. It is a grep over a
> ledger**, and R-GOLD-2's script already walks the same files.
>
> Two corollaries, both load-bearing:
> - **`2,373` and `1,374` are not exempt.** `07` P14-B1 pins them as literals labelled MEASURED. They are
>   properties of *our harvest over the pinned blank*, not of the published file, so under the normative
>   split they belong in `test_harvest_count`'s regime: they move into `docs/HARVEST-DELTA.md`, and the
>   golden asserts them **relationally** — `S == len(static_settled_cells(schema, registry))` and
>   `S + U == inScope`. G3's first rejection lowers `S`, so a pinned literal fails on correct behaviour and
>   gets quietly updated, which is the exact rot the split exists to prevent.
> - **A literal that cannot be traced is a finding, not a lint error.** The remedy is to produce the
>   measurement and its ledger row, or to assert relationally. Adding the literal to the ledger *without*
>   the command that reproduces it fails `tests/test_validation_ledger.py`.

**Which workbook, and why that one**, for each golden:

| Golden | Workbook | Why that one |
|---|---|---|
| `test_schema_constants` | FME `7d9a1960…` | The only one with all five features live at once: hidden sheet, `x14` validations, shared formulas, protection mask, cross-sheet carries |
| `test_x14_blindness_positive_control` | FME + `AL_monthly_report` + `ITFS_Monthly_report` | The **three** measured undercount instances. `AL_monthly_report` is the extreme: 1 of 10 |
| `test_no_protection_mask_yields_null` | `IFSCA_Annual_Reporting_Format` + `Draft_ACAC_Format` | The only two with no protection mask; the former produces a plausible 8 |
| `test_zero_formula_template` | `EDR_1` | Zero formulas ⇒ mechanically derivable settled fraction 0%; publish it anyway |
| `test_shared_formula_materialisation` | FME (211 of 505) and `ALR` (399 of 645, the highest share) | `ALR` has the worst text-matching loss in the corpus |
| `test_cross_workbook_harvest_distribution` | all nine | 515 is a sum over a concentrated distribution; publishing it alone is banned |
| `test_vacuous_bound_rejection` | `ALR` | Its five `≥ −1e17` bounds over 1,428 cells are the gate's one demonstrated rejection |
| `test_real_bound_admission` | FME | 19 of its 24 bounds are a real `≥ 0` — the positive control that stops G3 being a reject-everything baseline |

Tool: **none.** Goldens are plain files under `tests/golden/expected/` compared with `==`, plus a
`--update-goldens` flag implemented in ~20 lines in `tests/conftest.py`. A snapshot library is rejected
for the same reason the spec rejects a 2.3k-star dependency to save 200 lines: the part of the suite that
pins the project's headline constants must have no unmeasured dependency in it.
Naming: `tests/golden/test_<subject>.py::test_golden__<subject>__<workbook_slug>`.
CI stage 6. Budget: under 40 s across all nine.

### 1.4 Differential (two implementations must agree)

**Establishes**: that two independently written implementations of the same reading or computation
produce the same answer — and, when they disagree, that the disagreement is *escalated* rather than
resolved by preference. **Cannot establish**: correctness when both are wrong the same way. Two
implementations reaching the identical wrong number by the identical mechanism is not hypothetical here:
a hand-written regex and openpyxl 3.1.5 both report 35 validations, by the same namespace blindness, with
no error reaching a log (spec §II.1.2). Differential testing is defeated by a shared misconception, and
§7 carries that residue.

The **five** required differentials:

| # | A | B | Disagreement means | Blocking? |
|---|---|---|---|---|
| D1 | `ingest/reader_lxml.py` | `ingest/reader_openpyxl.py` | On `{n_sheets, sheet_names, hidden_sheets}` ⇒ run `INVALID(invalid.reader_structural_disagreement)`. Elsewhere ⇒ those fields `NOT_RUN(not_run.extractor_disagreement)` | Yes |
| D2 | `schema/styles_mask.py` (path A: `styles.xml` `cellXfs → protection@locked`) | `schema/styles_mask_b.py` (path B: per-sheet `<sheetProtection>` + per-cell `s` resolved by a **separately written** style resolver) | ⇒ `INVALID(invalid.denominator_disagreement)`. **The two paths must not share a module** — asserted structurally by NC-D02c and behaviourally by NC-D02d | Yes |
| D3 | our topological formula evaluator (8 functions) | the template's own **cached values**, present on 505 of 505 FME formula cells (MEASURED) | Per-cell mismatch. **Positive control required before any kill rate is quoted: `_xlfn.AGGREGATE` at `'1. Introduction'!C92:E101`** (spec E11) | Yes |
| D4 | our evaluator | LibreOffice headless, **pinned by container digest, offline only** | Writes to the `engine_disagreement` table, per template version. Never a live call; `INDETERMINATE(engine_disagreement)` is read from that table | **The verdict path is unaffected** (spec G12) — but the *disagreement count carries a pre-registered threshold `d` that is blocking on G-EVAL's label*, below |
| D5 | PDF extraction A over the pinned regulation | PDF extraction B, independently written | Normalised-sentence disagreement ⇒ the region is **excluded with its page numbers** and recorded in the `ExtractionManifest`; a quote whose span falls in a disputed region cannot clear G0 | Yes. The build that owns it is fixed in `04`/`06`; **this table is where it is required from**, because G0's `source_text.find(quote)` has no meaning without an authoritative normalised text with stable offsets |

**D4 is where a published disagreement was going to change nothing, and that is repaired here.**
G-EVAL's arm 2 threshold is *"100% against a human-authored expectation file; disagreements against the
digest-pinned LibreOffice engine are published, never silently resolved."* Publishing is not a failing
condition, and **LibreOffice is the only independent instrument in the pair** — so a build whose evaluator
disagreed with it on every non-trivial cell passed arm 2 provided it agreed with an expectation file its
own author wrote. Three rules close that, and all three are pre-registered, not judged afterwards:

1. **`d = 11`, a frozen integer, chosen before the first run** (arbitration C1) and pre-registered in
   `experiments/G-EVAL/PREREGISTRATION.md` together with its derivation
   `max(3, ceil(0.05 × |non-trivial cells|))`, the content hash of the corpus it was evaluated against, and
   the date: the maximum number of non-trivial cells on which our evaluator may disagree with the pinned
   LibreOffice engine. Disagreement on more than `d` cells **downgrades G2 to a `REACH` measurement** (§0.5)
   on the same branch as arm 1's 25-cell rule. A number chosen after seeing the disagreement set is not a
   threshold — **and neither is a formula that re-evaluates against whichever corpus it is handed**, which
   is why what is pre-registered is the integer and not the generator.
   `test_e_eval__d_is_preregistered` asserts the constant's commit is a git-ancestor of the first
   `engine_disagreement` row's.
2. **The arm-2 oracle's author is checked, not assumed.**
   `test_arm_two_author_is_not_the_evaluator_author` reads a declared `authored_by` field on the
   expectation file and on `calc/`, cross-checked against `git blame`. If they resolve to the same person,
   the test asserts that `docs/measurements/P3-evaluator.md`, `ci/GATES.md` **and every surface that quotes
   a kill rate** carry the literal string **`SAME-AUTHOR — a weaker instrument`**, and that `ci/GATES.md`
   records G-EVAL as **`PASSED — NOT INDEPENDENT`**. There is no third option and no silent one; this test
   is what makes the third option unreachable. The surface-side half is `07` P14-B4's obligation.
3. **The same rule governs every same-author differential in this document.** D1's `A`/`A′`, D2's mask
   path B and the arm-2 expectation file are the only three places where a second *person* buys evidence
   rather than throughput (§7.5). Where the staffing model does not supply one,
   `test_diff__same_author_differentials_are_labelled` asserts the `SAME-AUTHOR` string renders beside
   every number derived from that differential. **A same-author differential is admissible; an unlabelled
   one is not.**

Tool: ours. `tests/differential/` with a shared `assert_agree(a, b, on=[...], escalate=...)` helper that
asserts *both* the values and the escalation behaviour.
Naming: `tests/differential/test_diff__<a>_vs_<b>.py`. CI stage 7.

### 1.5 Determinism / reproducibility

**Establishes**: that the same inputs produce byte-identical outputs across process, machine, clock,
locale, hash seed and working directory — which is what makes `verify` (F14) the programme's acceptance
test. **Cannot establish**: that the reproduced answer is right. A deterministically wrong pipeline
reproduces perfectly.

The **five** sources of non-determinism the spec removes rather than tolerates, each with a test and an
injector. **The fifth was missing and it would have failed `E2E-VERIFY` permanently on the first green
run**: a duration this system measured about itself, sitting inside a structure whose digest a property
test asserts to be order-invariant.

| Source | Removal | Test | Injector that must break it |
|---|---|---|---|
| Mutable register | `register_snapshot_sha256`; the host function never resolves live | `test_det__register_from_snapshot_only` | `injectors/live_register.py` |
| Wall-clock | every timestamp is an input in the manifest; CEL binds no clock | `test_det__no_clock_in_verdict` | `injectors/now_in_renderer.py` |
| Iteration order | RFC 8785 for hashes, explicit sort keys everywhere | `test_det__hash_seed_invariant` | `injectors/unsorted_rollup.py` |
| Floating point | there is none — money is `int64 MILLI_USD_MILLION`, tolerances are integers | `test_det__no_float_on_verdict_path` | `injectors/float_money.py` |
| **Self-measured durations** | **no duration reaches a hashed payload.** Timings are written to `reports/perf/<run_id>.jsonl`, outside `run.jsonl` and outside anything `canonical_json` touches; the perf budgets read them there | `test_contract__no_duration_field_in_a_hashed_object` (§1.9) | `injectors/duration_in_hashed_payload.py` — re-adds `elapsed_us` to a canonicalised record |

**The dangerous repair, named so nobody takes it.** The obvious fix for `CanaryRow.elapsed_us` is to drop
the field from the hash. That silently removes the evidence that the canary loop *executed* rather than
being replayed from a cache — which is death D5's whole concern. **Keep the evidence, move the timing:**
`CanaryRow` retains `witness_digest`, `observable`, `intersects_read_set` and `fired`, all deterministic,
and `canariesRun == len(rows)` remains the assertion of D5. The timing goes to `reports/perf/`, where
`PERF-CANARY2` reads it. The removal is only sound *because* the non-timing evidence stays inside the hash.

Mechanics: `make determinism` runs the FME pipeline twice under
`TZ=Pacific/Kiritimati` vs `TZ=UTC`, `PYTHONHASHSEED=0` vs `1`, `LC_ALL=C` vs `en_IN.UTF-8`, two different
working directories, and asserts byte-identical `report.html`, `attestation.json` and `run.jsonl`. CI then
runs `cdfc verify` on a **second runner image** (spec A7).
Naming: `tests/determinism/test_det__<subject>`. CI stage 9. Budget: 90 s.

### 1.6 Negative control

**Establishes**: that a specific guard fires against a specific break — i.e. that a passing test is
carrying information rather than being vacuously true. This is the only class that produces evidence
*about the suite*. **Cannot establish**: that a guard fires against a break nobody imagined. Its
denominator is the catalogue, and the catalogue is written by the same people who wrote the code — a
self-referential denominator, which is the exact error this project warns about elsewhere and cannot
escape here. §7.6 states what that costs.

Required: **for every acceptance test in every phase.** Where impossible, the catalogue entry carries
`injector: NONE`, a mandatory `why_impossible` string **and a mandatory `substitute_measurement`** — the
instrument that stands in for the test we cannot write, named as an artifact and a command. The sweep
reports those entries separately rather than silently. **"Impossible" without a substitute is a skipped
line**, and `test_nc_meta__every_entry_has_an_injector_or_a_reason` asserts both fields are non-empty
together. DoD line C6 is checked against the catalogue, not against the phase document's prose.

Tool: ours — `tests/negative/injectors/`, driven by `tests/negative/catalogue.yaml`.
Naming: `tests/negative/test_nc_<component>.py::test_nc__<ID>_<slug>`. CI stage 8. Budget: 6 min.
Full specification in §2.

### 1.7 Metamorphic / relational

**Establishes**: that a stated relation between an input transformation and an output holds. Note the
spec's global rename: **`METAMORPHIC` is retired as a `method` value in favour of `DIFFERENTIAL`**, because
metamorphic testing requires a re-executable system under test and a filed workbook is a record. What we
have is the **workbook-as-program**: all 505 formula cells carry cached values, so a baseline exists.

**Cannot establish**: that a violated relation means the artifact is wrong. It means *the artifact is
wrong* **or** *our relation is wrong*, which is why every relation passes the same five L4 gates as any
other predicate, and why relations are authored by a human reading the artifact's own formula graph —
model-generated relations score "markedly low" on novelty and produced, in an earlier version of this
design, five relations of which four false-alarm on a correct filing and the fifth is vacuous.

Two rules the class must obey, both of which are how it silently goes green:
1. **Every partition relation carries a non-degeneracy precondition** and returns `OUT_OF_SCOPE`, never
   `PASS`, when it is unmet. An all-zero filing satisfies every partition identity trivially; without the
   precondition an empty filing scores 100% through this door.
2. **No relation may combine a 3.x quantity with a 5.6 quantity** — Portfolio note 7 puts Tables 3.1/3.2
   on a direct-investment basis while the PMS note puts 5.6 on a look-through basis. Asserted by
   `tests/relational/test_rel__basis_contamination_guard`.

The relation that pays for the layer and is tested first: **`TEMPLATE_DIFF`, the formula-override
detector** — for every cell the pinned blank declares to be a formula, compare the filed value against
the value obtained by evaluating the template's formula over the filed inputs. It needs no corpus; its
oracle is the regulator's published blank.

Tool: **Hypothesis** `RuleBasedStateMachine` — `@invariant` for *necessary* relations (violation ⇒ FAIL),
in-rule assertions for *expected* (violation ⇒ `INFORMATIONAL`), so the split is enforced by the library
rather than by our convention. `max_examples = 50`. Every real defect pinned as `@example`.
Naming: `tests/relational/test_rel__<relation_id>.py`. CI stage 5 (fast) + nightly (deep).

### 1.8 Performance regression

**Establishes**: that a measured budget has not been blown against a baseline recorded on the same
machine class. **Cannot establish**: behaviour at a scale never run. The pipeline is ~30 ms at 3.4
filings/day; a regression that only manifests at 100× is invisible to this class by construction.

Budgets, each traced to a MEASURED baseline in the spec:

| Budget id | Subject | MEASURED baseline | Fail above | Warn above |
|---|---|---:|---:|---:|
| `PERF-L1` | `schema/induce.py`, FME, cold | 28–44 ms | 90 ms | 60 ms |
| `PERF-RB` | `reader_openpyxl.py` load | 202 ms | 300 ms | 250 ms |
| `PERF-FT` | fact-table build | 1 ms | 5 ms | 3 ms |
| `PERF-EV` | evaluation, 280 predicates | sub-ms (227 arith) | 10 ms | 5 ms |
| `PERF-CORE` | deterministic core end-to-end | ~30 ms | 60 ms | 45 ms |
| `PERF-ONLINE` | full online run, readers agreeing, no attachments | ≈450 ms (DERIVED) | 900 ms | 700 ms |
| `PERF-MUT` | fault-seeding harness throughput | 7,946 mutants/s | below 5,000/s | below 6,500/s |
| `PERF-CANARY` | 280 canaries over the in-memory fact table | ~35 ms (DERIVED from the measured rate) | 80 ms | 55 ms |

**The honest treatment of machines**: `perf/baseline.json` records `{machine, cpu, python, date}` and is
the developer baseline; `perf/baseline.ci.json` is recorded on the CI runner image and is the only
baseline CI compares against. Cross-machine comparison is advisory and is labelled as such in the report.
A budget may be raised only by an entry in `perf/BUDGET-CHANGES.md` with a reason and a date.

Tool: **pytest-benchmark** (BSD-2 — SECONDARY), `--benchmark-compare-fail=mean:20%`.
Naming: `tests/perf/test_perf__<budget_id>`. CI stage 10.

### 1.9 Contract / schema

**Establishes**: that a serialised object conforms to a schema, that an enum is closed at the stated
cardinality, and that a generated document equals its generator's source. **Cannot establish**: that the
schema encodes the right thing. A schema can be valid and mean nothing — an OSCAL assessment result with
zero findings is schema-valid and means nothing in particular (spec §II.5.3).

The required contracts:

| Contract | Assertion | Test |
|---|---|---|
| Item states | exactly 8, closed | `test_contract__eight_item_states` |
| Reason codes | exactly 30, namespaced, five families, code required iff state ∉ {PASS, FAIL} | `test_contract__thirty_reason_codes` |
| Run-level `invalid.*` causes | exactly 8, a **separate** vocabulary from the item-level 8 × 30 (audit V.7.3) | `test_contract__eight_invalid_causes` |
| `method` | exactly 9, includes `TEMPLATE_DIFF`, excludes `METAMORPHIC` | `test_contract__nine_methods` |
| `corpus_provenance` | exactly 6, register value spelled `REGISTER-DERIVED` | `test_contract__six_corpus_provenances` |
| Attestation schema | **no `result`, `status` or `pass` property at any depth**, `additionalProperties: false` on every object, top-level object is `scope`, the four statement fields are `required` | `test_contract__attestation_cannot_express_a_pass` (NC-A01) |
| `NONE ≠ NOASSERTION ≠ absent` | `[]` = we determined there are none; `null` = we make no claim; omitted = schema violation | `test_contract__absent_empty_null_are_distinct` |
| Evaluation contract | the evaluator's transition table **equals** the table parsed from `EVALUATION-CONTRACT.md` | `test_contract__evaluation_contract_matches_evaluator` (spec G5) |
| Write-time constraint | `method='MODEL_EXTRACT' AND state='PASS'` is rejected at write time | `test_contract__model_extract_cannot_pass` |
| **`settledFraction` on an `INVALID` run** | **present and `null`** — one rule, stated once. JSON Schema: `{"if": {"properties": {"runState": {"const": "INVALID"}}}, "then": {"properties": {"settledFraction": {"const": null}}, "required": ["settledFraction"]}}` | `test_contract__invalid_carries_a_null_not_an_absence` |
| **No duration in a hashed object** | walk every dataclass reaching `canonical_json`; **no field name matches `(elapsed\|duration\|_us\|_ms\|_ns\|seconds)`** and no field's value derives from `time.perf_counter`, `time.monotonic` or `time.process_time` | `test_contract__no_duration_field_in_a_hashed_object` |
| **A pre-registered criterion is machine-evaluable** | every threshold in an `experiments/*/PREREGISTRATION.md` is **arithmetic that the deciding function can consume**, not prose a human interprets after the result. The lock **refuses to write** a criterion `decide()` cannot evaluate | `test_contract__preregistration_criterion_is_machine_evaluable` |

**The pre-registration row applies to every hashed-before-the-run artifact in this plan** — `E4`'s transfer
threshold (`07` P15-B1) and `E6`'s `beats_baselines` among them. A criterion whose reading has to be chosen
after the numbers arrive is not a criterion, and the whole epistemic value of these files is that they were
specified, locked and hashed **before** the run. Prose in a locked file is prose.

**Why the `INVALID` row exists at all.** Three contracts for one field in one state were live across the
binding documents: `compute() -> SettledFraction \| None` (i.e. the property is present and `null`), a
schema `if/then` that **forbids** the property, and this document's own rule that an omitted property is a
violation. `null`, `forbidden` and `omitted` are three different things; each phase passed its own contract
test and the composition produced an attestation that either fails validation or drops the `null` that
`E2E-INVALID` exists to assert. **The rule is: present and `null`.** `null` means *we make no claim*, which
is precisely what an `INVALID` run has to say, and it is the only one of the three that a consumer can
distinguish from `0`.

Tool: **jsonschema** (MIT — SECONDARY) for instance validation; a hand-written recursive walker
(`tests/contract/schema_walk.py`, ~40 lines) for the structural prohibitions, because the prohibition is
"no property named X **at any depth including inside `$defs`, `allOf`, `oneOf`, `patternProperties` and
`additionalProperties` subschemas**", which no off-the-shelf validator expresses.
Naming: `tests/contract/test_contract__<subject>`. CI stage 3.

### 1.10 End-to-end

**Establishes**: that the composition runs on the real artifact, offline, from a clean clone, and
produces the artifacts the demo shows. **Cannot establish**: anything about a filing shape not in the
fixture set — and no real filed FME return is public, so the e2e corpus is synthetic or blind-filled by
construction and must be labelled (§6.4).

The required e2e flows:

| Flow | Command | Asserts |
|---|---|---|
| `E2E-DEMO` | `make demo` on a clean clone, network namespace closed | `ingest → induce → harvest → run` completes; every README number is reproduced from program output; the report opens from `file://` |
| `E2E-VERIFY` | `cdfc verify reports/report.html` on a **second runner image** | `REPRODUCED`, byte-identical |
| `E2E-TAMPER` | flip one byte of the filing, re-verify | a diff, not `REPRODUCED` |
| `E2E-INVALID` | `cdfc demo --break-parser` (renames a sheet) | `INVALID` with run-level cause **`invalid.template_unbound`**; **`settledFraction` is present and `null`** — not 0, not omitted; **`dead_predicates` is `[]` and the report says why**: no predicate ran, so none can be named |
| `E2E-CANARY-SILENT` | a filing that binds, run against a registry holding a predicate whose stored `kill_case` no longer dies (fixture owned by `05`) | `INVALID` with cause **`error.canary_silent`**, **`dead_predicates[]` populated with the specific ids**, `settledFraction` present and `null` |
| `E2E-TRANSFER` | `cdfc transfer --all` over the nine | per-template settled fractions **including the two `null` cases and the 0% case**, never averaged |

**`E2E-INVALID`'s assertion was unsatisfiable as written, and this is the correction.** `05` §0.5 proves —
correctly, by reading the pipeline rather than by running it — that a renamed sheet terminates at **F3**
with `invalid.template_unbound`, five steps before the canary loop. A `template_unbound` run has **no dead
predicates to name**, because no predicate was ever bound, let alone run. The original row therefore
demanded evidence the fixture cannot produce, and `05` fixed it inside `05` while this document — the one
CI is written against — was left asserting the superseded mechanism. **A correction that does not propagate
to the binding document is this plan's own version-churn failure.** Two mechanisms close it:

- Every superseded mechanism gets a row in **`docs/CATALOGUE-CORRECTIONS.md`**:
  `{superseded_assertion, corrected_by_document, corrected_at, documents_amended[], commit}`. The row for
  this one names `01` §1.10, `01` §2.5 NC-C01a and `00` P10, all amended in the same commit as `05`'s
  correction.
- **`test_plan__no_binding_document_asserts_a_superseded_mechanism`** — for every row of
  `CATALOGUE-CORRECTIONS.md`, grep `plan/`, `docs/` and `tests/` for the superseded assertion string; a hit
  outside `CATALOGUE-CORRECTIONS.md` itself fails the build. One grep over a file the plan already needed.

Naming: `tests/e2e/test_e2e__<flow_id>`. CI stage 12. Budget: 2 min.

### 1.11 Which class is required when

| Situation | Mandatory classes |
|---|---|
| A new parser or reader | unit, golden, differential (D1/D2), negative control (NC-P*) |
| A new predicate class in the harvest | unit, golden (harvest count with delta entry), negative control (NC-Q*) |
| Anything writing to the verdict path | unit, property, contract, negative control, determinism |
| A new host function | unit **with published test vectors**, property, mutation (§3, Tier V threshold), negative control for its third value |
| A new relation | relational, plus the five L4 gates like any predicate, plus a non-degeneracy precondition test |
| A new user-facing surface | negative control (NC-A02 glyph scan **and** the scan-set coverage test), contract |
| A change to the attestation | contract (recursive walk), determinism, e2e verify |
| Any change at all | census, licence gate, design-commitment greps |

---

## §2 — THE NEGATIVE CONTROL CATALOGUE

**This is the heart of the document.** Each entry is a row in `tests/negative/catalogue.yaml` with this
shape, and the schema is enforced by `test_nc_meta__catalogue_schema`:

```yaml
- id: NC-P01
  component: ingest
  break: "the authoritative reader is namespace-blind and cannot see <x14:dataValidation>"
  measured_instance: "openpyxl 3.1.5 on FME (35/54), AL_monthly_report (1/10), ITFS (7/16)"
  injector: reader_nsblind          # a key in tests/negative/injectors/INJECTORS, or NONE
  why_impossible: null              # required and non-empty iff injector is NONE
  substitute_measurement: null      # required and non-empty iff injector is NONE (§1.6, §2.8)
  closes_at_phase: null             # required iff positive_control is null -- the PROVISIONAL column
  guard_tests:                      # EVERY entry declares, per guard, what the injector must do to it
    - path: tests/golden/test_schema_constants.py::test_golden__validations__fme
      flips: true                   # MUST go red under the injector
    - path: tests/negative/test_nc_ingest.py::test_nc__P01_namespace_blind_reader_rejected
      flips: true
    - path: tests/golden/test_x14_blindness_positive_control.py::test_golden__openpyxl_still_undercounts
      flips: false                  # a positive control: it must STAY GREEN under the injector
  positive_control: tests/golden/test_x14_blindness_positive_control.py
  status: ACTIVE                    # ACTIVE | PENDING (phase not yet reached) | RETIRED (with reason)
```

**The `flips:` field is required on every guard and it is what makes the sweep an instrument** — see §2.0
step 3, which previously asserted only that *at least one* guard went red. `flips: false` on **every**
guard of an entry is a schema error (`test_nc_meta__catalogue_schema`): an entry no injector can turn red
is not a negative control.

---

## THE CANONICAL `NC-` REGISTRY — arbitration **C9**

**This section is the sole registry. No other document may *define* an `NC-` id; every other document
*references* one.** That is not a style rule, it is the repair: the catalogue is one file keyed by `id`,
append-only, and every meta-test assumes uniqueness — and it did not have it. Six documents allocated ids
independently, and then, in the repair *for* id collisions, **five collided id-groups became ten colliding
definitions and four mutually inconsistent band tables**, two of the new collisions (`NC-Q45`, `NC-Q46`)
created inside the fix by two owners writing the same range on the same afternoon. **If `catalogue.yaml`
loads into a dict keyed by `id`, the later document's entry silently replaces the earlier one**, the sweep
still reports `caught == active`, `test_nc_meta__no_orphan_guard` is still satisfied because *an* entry
names the guard, and the row that was supposed to keep G-EVAL arm 2 from being deleted as redundant is no
longer in the register anybody reads. That is a green build lying about its own instrument.

**The lesson, stated once because it is the pass's own:** four owners editing disjoint files were not
editing disjoint contracts. *A coupled specification admits exactly one writer at a time* — and an id space
is the most coupled contract in the plan.

---

### 2.1 THE BAND TABLE — one allocation, one home, a reserved range per band

**This is the only band table in the corpus.** The four that competed with it — `02` R5a (which declared
itself normative), `04` §0.8, `05` §4 and `07` §3 — **are deleted**, and each carries a note saying so.
Every band gives each document a **reserved unallocated range**, so a future writer never has to invent
one, and `ci/catalogue-ids.sh` fails the build on an id defined outside the owner's allocation.

| Band | Component | `01` | `02` | `03` | `04` | `05` | `06` | `07` | **Reserved (unallocated)** |
|---|---|---|---|---|---|---|---|---|---|
| `P` | ingest / parsing | P01–P06 | P07–P11 | — | — | — | — | — | `01` P20–P24 · `02` P12–P19 · others P25–P49 |
| `D` | schema / denominator | D01–D04 | D05–D08 | — | — | — | — | — | `01` D20–D24 · `02` D09–D19 · others D25–D49 |
| `Q` | predicates / qualification | Q01–Q11 | — | **Q70–Q75** | Q30–Q39 · Q47 · Q48 · **Q55–Q61** | — | — | — | `01` Q17–Q21 · `03` Q76–Q79 · `04` Q62–Q69 · `05` Q80–Q84 · `06` Q85–Q89 · `07` Q90–Q94 |
| `E` | evaluation / verdict | E01–E08 | E10–E14 | E20–E25 | — | — | — | — | `01` E09 · `02` E15–E19 · `03` E26–E29 · `04` E30–E39 · `05` E40–E49 · `06` E50–E59 · `07` E60–E69 |
| `C` | self-check / canaries | C01, C02 | — | — | — | C03–C11 | — | — | `01` C20–C24 · `05` C12–C19 · others C25–C49 |
| `A` | attestation / report / surface | A01–A05 | — | — | — | A16–A20 | — | A06–A15 · A30–A32 | `01` A21–A25 · `05` A26–A29 · `07` A33–A39 · others A40–A59 |
| `X` | external sources / host fns | X01–X05 | — | — | — | — | — | X06–X08 | `01` X20–X24 · `07` X09–X19 · others X25–X49 |
| `R` | relational | — | — | — | — | R01–R10 | — | — | `05` R11–R19 · others R20–R49 |
| `M` | model lane | — | — | — | — | — | M01–M34 | — | `06` M35–M49 · others M50–M69 |
| `F` | fixtures | — | F01 | — | — | — | — | — | `02` F02–F09 · others F10–F29 |
| `L` | licence | **L01** | — | — | — | — | — | — | `01` L02–L09 · others L10–L29 |
| `CI` | CI gates | — | CI01–CI08 | — | — | — | — | CI10–CI12 | `02` CI09 · `07` CI13–CI19 · `01` CI20–CI24 · others CI25–CI49 |
| `N` | **impossible** (`injector: NONE`) | N01–N06 | **N16** | — | **N50, N51** | N11–N14 · N22–N24 · **N25, N26** | N30–N34 | N08–N10 · **N40** | `01` N60–N64 · `02` N17–N19 · `03` N65–N69 · `04` N52–N59 · `05` N27–N29 · `06` N35–N39 · `07` N41–N49 |

**Bold entries are the ids C9 minted.** Everything else is unchanged from where it already was, because
**the ruling is to renumber mechanically, never by judgement** — and moving an id that was not contested is
judgement.

---

### 2.2 THE RETIRED LIST — permanent, never reassigned

> **Where two documents defined the same id with different content, BOTH got new ids. Neither kept the
> contested one, and the contested one is retired permanently rather than reassigned.** *A retired id that
> later resolves to something is how a stale reference becomes a silent wrong reference* — which is worse
> than a dangling one, because a dangling reference fails a build and a wrongly-resolving one does not.

`test_nc_meta__no_dangling_reference` **fails the build on any reference to any id below.**

| Retired id | Why retired | Where its content went |
|---|---|---|
| **`NC-Q40`** | defined twice, different content, `03` and `04` | `03`'s → `NC-Q70` · `04`'s → `NC-Q55` |
| **`NC-Q41`** | defined twice, different content, `03` and `04` | `03`'s → `NC-Q71` · `04`'s → `NC-Q56` |
| **`NC-Q42`** | defined twice, different content, `03` and `04` | `03`'s → `NC-Q72` · `04`'s → `NC-Q57` |
| **`NC-Q43`** | defined twice, different content, `03` and `04` | `03`'s → `NC-Q73` · `04`'s → `NC-Q58` |
| **`NC-Q44`** | defined twice, different content, `03` and `04` | `03`'s → `NC-Q74` · `04`'s → `NC-Q59` |
| **`NC-Q45`** | **a collision the repair itself created**, `03` and `04`, same commit | `03`'s → **merged into `NC-Q57`** (same break, same injector) · `04`'s → `NC-Q60` |
| **`NC-Q46`** | **a collision the repair itself created**, `03` and `04`, same commit | `03`'s → `NC-Q75` · `04`'s → `NC-Q61` |
| **`NC-N07`** | defined twice, different content, `02` and `07`, **each instructing the other to move** | `02`'s → `NC-N16` · `07`'s → `NC-N40` |
| **`NC-N20`** | defined twice, different content, `04` and `05` | `04`'s → `NC-N50` · `05`'s → `NC-N25` |
| **`NC-N21`** | defined twice, different content, `04` and `05` | `04`'s → `NC-N51` · `05`'s → `NC-N26` |
| **`NC-Q12`–`NC-Q16`** | historical ids of `03`'s entries, vacated twice and pointed at two different targets by two different mapping tables (`Q40–Q44` in `03`, `Q50–Q54` in this document) | `03`'s content is at `NC-Q70`–`NC-Q74` |
| **`NC-Q22`** | historical id of `04`'s entry, vacated by the earlier pass's `Q22 → Q40` and again by C9's `Q40 → Q55`; §2.1 nevertheless re-allocated the vacated number to `04` and `04` §0.8 claimed it, while **no document defines an entry under it** — a live allocation pointing at a number whose content left twice. *Added by the confirmation pass (`plan/12`), under C9.3: a vacated id is retired, never re-issued* | `04`'s content is at **`NC-Q55`** |
| **`NC-Q22b`** | a break with its own injector wearing a guard suffix (F17); it was also assigned two ids (`NC-Q27` here, `NC-Q41` in `04`) | → **`NC-Q56`** |
| **`NC-Q23`–`NC-Q29`** | this document's "reserved for the repairs this pass creates" list — **a reservation two documents ignored is not a reservation**, and these seven named the same seven breaks `04` implemented as `Q40`–`Q46` | → `NC-Q55`–`NC-Q61` |
| **`NC-Q49`–`NC-Q54`** | targets of a mapping table that pointed at ids `03` never took | `03`'s content is at `NC-Q70`–`NC-Q75` |
| **`NC-N15`** | a rename target that the document expected to define it (`02`) declined, instructing `07` to move instead | `02`'s content is at `NC-N16` |
| **`NC-A21`** | reserved by the deleted reservation paragraph for an entry `05` had already catalogued as `NC-C10` | → `NC-C10` |
| **`NC-E09`** | historical id of `03`'s `cells_bound`-after-`expr` entry, vacated to `NC-E20`; retained in a mapping table afterwards | → `NC-E20` |
| *(`NC-L01` is **not** retired)* | it was an **orphan** — referenced by `07` P15-B1 with no entry anywhere in the corpus — and orphans are errors, not debris (C9.5) | **registered here, to `01`**: *the licence gate against the research venv, which still carries two denylisted packages on disk, so it is a negative control that needs no injector.* `07` now references a real row |

---

### 2.3 THE OLD → NEW MAPPING, COMPLETE

Every renumbering C9 performed, in one table, so a reader holding an old document can resolve any id they
find. **Guard-test slugs move with their entries** (`test_nc__Q40_…` → `test_nc__Q70_…`, `test_nc__Q42a…c` →
`test_nc__Q72a…c`, and so on), and the letter-suffixed guards travel with their parent.

| Band | Old id | Held by | **New id** | Entry, in one line |
|---|---|---|---|---|
| Q | `NC-Q40` | `03` | **`NC-Q70`** | a field is dropped from the canonical serialisation, so two predicates share a digest |
| Q | `NC-Q41` | `03` | **`NC-Q71`** | the admitted-subset CEL walker is permissive |
| Q | `NC-Q42` | `03` | **`NC-Q72`** | `schema_keys` extracted lexically instead of from the parsed AST |
| Q | `NC-Q43` | `03` | **`NC-Q73`** | the cross-workbook total renders without its per-workbook distribution |
| Q | `NC-Q44` | `03` | **`NC-Q74`** | the harvest drops what it cannot express |
| Q | `NC-Q45` | `03` | **`NC-Q57`** *(merged)* | `claims_fault_classes` derived from the kill vector (**F1**) — **the same break, same injector, as `04`'s former `NC-Q42`. One break, one entry, one id** |
| Q | `NC-Q46` | `03` | **`NC-Q75`** | a candidate whose obligation is `source: TEMPLATE` declares no reason (**F9**, and see C2) |
| Q | `NC-Q40` | `04` | **`NC-Q55`** | an admission batch is written without a human signature |
| Q | `NC-Q41` | `04` | **`NC-Q56`** | the Wilson bound is computed in `float` (**F17**; the former `NC-Q22b`) |
| Q | `NC-Q42` | `04` | **`NC-Q57`** | `claims_fault_classes` derived from the kill vector (**F1**) |
| Q | `NC-Q43` | `04` | **`NC-Q58`** | `TEMPLATE-COMPUTED` licenses an arithmetic FFR (**F2**) |
| Q | `NC-Q44` | `04` | **`NC-Q59`** | independence hand-set instead of computed (**F5**) |
| Q | `NC-Q45` | `04` | **`NC-Q60`** | a `not_run` cell banked as unobservable (**F18**) |
| Q | `NC-Q46` | `04` | **`NC-Q61`** | observability recalculates with template formulas (**F19**) |
| N | `NC-N07` | `02` | **`NC-N16`** | *impossible:* a field observation is quietly dropped |
| N | `NC-N07` | `07` | **`NC-N40`** | *impossible:* an all-clear mark drawn as vector paths, a raster image or a ligature |
| N | `NC-N20` | `04` | **`NC-N50`** | *impossible:* the fault taxonomy is complete |
| N | `NC-N21` | `04` | **`NC-N51`** | *impossible:* `domain-policy-v1.json`'s magnitude bound is right |
| N | `NC-N20` | `05` | **`NC-N25`** | *impossible:* the fact table holds this filing's values |
| N | `NC-N21` | `05` | **`NC-N26`** | *impossible:* a relation encodes its author's intent |

**Renumberings from the previous pass that C9 leaves standing**, listed so the mapping is complete rather
than only recent: `03`'s `E09→E20`, `E10→E21`, `E11→E22`, `E12→E23`; `04`'s `Q12→Q30` … `Q21→Q39`;
`05`'s `N11→N20` … `N14→N23` (and `N20`, `N21` moved again here, to `N25`, `N26`); `06`'s `N11→N30` …
`N14→N33`. `02` keeps `E10`–`E14`.

**Two sentences stay deleted rather than corrected, because they assert the id space away instead of
checking it:** `03` §6's *"`NC-Q11` and `NC-E08` are the current maxima"* and `04` §0.8(e)'s *"the Q family
is free from `NC-Q12`"*. **A third joins them:** `06` P13-B2's *"continuing … past `07`'s `NC-N07`…`N10`"* —
ids are not allocated by continuing past somebody else's block, and `NC-N07` is now retired.

---

### 2.4 THE FOUR RULES, EACH MECHANISED

1. **`test_nc_meta__ids_are_unique`** — load `catalogue.yaml`, assert `len(ids) == len(set(ids))` **before**
   any dict is built from it, and assert the file's own row order is the order the ids sort in. It is four
   lines and it **must exist before the first entry is written, at P0-B3** — a uniqueness test added after
   the collisions exist reports history, not health.
2. **`test_nc_meta__ids_are_defined_in_the_registry`** — every `NC-` id appearing in **any** `plan/*.md` or
   `tests/` path resolves to exactly one row of §2.1's allocation, and **every id defined outside this
   document fails**. This is the rule that makes "one registry" checkable rather than promised; without it,
   "`01` is the sole registry" is a sentence, and sentences are what produced four band tables.
3. **`test_nc_meta__no_orphan_guard`** — every test function under `tests/negative/` appears in the
   catalogue **and appears with a `flips` value**; a guard named without one is an orphan in the new shape.
   **A letter suffix names a guard test inside an entry, never a second break** — `NC-Q08a`…`NC-Q08e` are
   the five guards of entry `NC-Q08`, and `NC-D02c`/`NC-D02d` are the structural and behavioural guards of
   `NC-D02`. **A break with its own injector needs its own row**, whatever it is called in prose; the live
   instance was `NC-Q22b`, and it now has one (`NC-Q56`).
4. **`test_nc_meta__no_dangling_reference`** — no reference anywhere resolves to a **RETIRED** id (§2.2) or
   to no id at all. **Orphans are errors, not debris**; this test and rule 3 both fail the build.

   **Two exemptions, and they are narrow enough to be checkable.** A retired id may appear (a) inside §2.2
   and §2.3 of this document, and (b) inside a block a document marks as a **retirement or history note** —
   the `> **… is RETIRED …**` / *"the id then called"* form used in `02` R5a, `03` §6, `04` §0.8, `05` §4 and
   `07` §3. Everywhere else a retired id is a build failure. *The exemption exists because a retirement
   record has to name what it retired; it is scoped to a marked block precisely so it cannot become the
   loophole through which a live reference re-enters.*

**`ci/catalogue-ids.sh`** (§5.3 stage 2, §5.4) is the grep form of rules 2 and 4 over `plan/*.md`, and it
must **assert `file --mime-encoding` is `utf-8` for every scanned path, or use `grep -a`, before grepping
it.** One raw NUL byte in `03` made GNU/BSD `grep` skip the whole document silently, and this gate — the one
written to catch id collisions — would have run green over the largest instance of them in the repository.
*A scan set that silently drops a file is the same defect as a scan set that shrinks.*

**The reservation paragraph that stood here is deleted.** It reserved `NC-Q23`–`NC-Q29` "so the next writer
does not collide with them"; two documents ignored it and implemented the same seven breaks under other
ids. **A reservation two documents ignored is not a reservation** — §2.1's reserved ranges are enforced by
a gate instead of announced in prose.

---

### 2.0 The sweep — how the catalogue proves itself

`make nc-sweep` → `reports/negative-control-sweep.json`. For every `ACTIVE` entry:

1. Assert the named guard tests **pass** with no injector applied.
2. Apply the injector (an `Injector` is a context manager that either monkeypatches a symbol, swaps a
   module in `sys.modules` for its `broken_builds/` twin, or writes a corrupted fixture to a temp path).
3. Re-run **only** the named guard tests, and assert the **exact set**: every guard declared `flips: true`
   is **red**, every guard declared `flips: false` is **green**. The sweep fails if either set differs, and
   it records, per guard, the pytest node id and **the captured assertion text**.
4. Remove the injector. Assert the guard tests pass again — a guard that stays red is a leaked injector,
   which is itself a defect.

**Step 3 previously read *"assert at least one fails"*, and that is the M4 failure — a count that is right
while the bodies are wrong.** Entries routinely name three to five guards; `NC-Q08` names five, `NC-C01`
three, `NC-P01` three including a positive control. Under the old rule, applying
`injectors/render_self_authored_ffr.py` and watching `test_nc__Q08c_no_ffr_without_provenance_and_n` go red
recorded `NC-Q08` as `caught` and printed `caught = 47 of 47` — while
**`test_nc__Q08a_renders_uninformative`, the assertion that no digit reaches the FFR element, criterion A4,
the one the whole provenance story rests on, was never exercised and could have been deleted three commits
earlier.** `test_nc_meta__no_orphan_guard` cannot see it: the test still exists and is still named. It is
simply never observed red. **This document's own thesis, applied to this document's own instrument: a guard
that has never been observed to fail is not evidence, and the sweep as written could not tell you which
guards those were.**

**Eight** meta-tests make the catalogue non-decorative. **The four `NC-`-id meta-tests named by arbitration
C9 are the first four, and all four must exist at P0-B3, before the first entry is written** — a uniqueness
test added after the collisions exist reports history, not health:

- **`test_nc_meta__ids_are_unique`** (C9) — **runs first, and at P0-B3 before the first entry exists.** See
  §2.1. A catalogue whose ids collide silently drops rows, and every phase document references it by id.
- **`test_nc_meta__ids_are_defined_in_the_registry`** (C9) — every `NC-` id appearing anywhere resolves to
  exactly one row of §2.1's allocation, **and an id defined outside this document fails the build.** This is
  what makes "`01` is the sole registry" checkable instead of promised.
- **`test_nc_meta__no_orphan_guard`** (C9) — every test function under `tests/negative/` appears in the
  catalogue, **and appears with a `flips` value**; a guard named without one is an orphan in the new shape.
  A letter suffix names a guard inside an entry, never a second break (§2.4 rule 3).
- **`test_nc_meta__no_dangling_reference`** (C9) — no reference anywhere resolves to a **RETIRED** id (§2.2)
  or to no id at all. **Orphans are errors, not debris:** this test and the one above both fail the build.
- `test_nc_meta__every_entry_has_an_injector_or_a_reason` — `injector: NONE` requires a non-empty
  `why_impossible`.
- **`test_nc_meta__every_expected_guard_flipped`** — the sweep, run as a test, in its real form: the
  `flips: true` set is exactly the red set and the `flips: false` set is exactly the green set, per entry.
  This supersedes `test_nc_meta__every_injector_flips_its_guard`, which asserted the weaker "at least one"
  and is retired with its reason recorded in `docs/CATALOGUE-CORRECTIONS.md`.
- `test_nc_meta__catalogue_is_append_only` — entries are append-only; a `RETIRED` entry keeps its row and
  carries a reason; **removing a row requires a dated argument in `docs/GATE-CHANGES.md`.** The catalogue
  publishes `|catalogue|` as a time series for the same reason `SURFACES` does (`07` P14): *a denominator
  that shrinks the day before a gate is read must be visible.*
- `test_nc_meta__catalogue_growth_is_logged` — the growth log is the only visible signal of the rate at
  which new failure *mechanisms* are discovered, which is the number §7.6 says we cannot otherwise obtain.

**The sweep's output is four integers and a fifth count, never a percentage:**

```
entries_caught / entries_active          <- what the plan used to report, and it counts ENTRIES
guards_flipped / guards_expected_to_flip <- THE number DoD line C4 is really about
entries with injector: NONE                        (reported separately, never inside caught)
entries PROVISIONAL — no admission-side twin yet   (reported separately, never inside caught)
```

**The second pair is new and nothing previously computed it.** `caught / active` counts entries; an entry
is `caught` when any one guard goes red; so the headline could read `47 of 47` over a catalogue in which
the guards that mattered were never observed red. `guards_flipped / guards_expected_to_flip` is the count
of *bodies*, and it is the one that carries information about the suite.

**The `PROVISIONAL` column, and why it is not a fourth kind of green.** `02` §1 R5 ships
`registry.py::load_or_refuse()` refusing **unconditionally** at P0, so
`test_nc__Q02_unqualified_predicate_does_not_load` is green from P0 to P4 while proving nothing — its
admission-side twin is impossible until a predicate can be admitted at all. The plan declares this
honestly, and the declaration is right; what was wrong is that the entry sat inside `caught` for four
phases carrying no information. An entry whose `positive_control` is `null` **because the twin is not yet
buildable** is reported `PROVISIONAL` with the phase that closes it, and
`test_nc_meta__provisional_entries_name_their_closing_phase` fails on one that does not.

---

### 2.1 INGEST AND PARSING (L0)

#### NC-P01 — a parser that silently under-reports · **REAL, ON DISK**

**The break.** The authoritative reader matches `dataValidation` only in the main OOXML namespace, so the
19 `x14` extension validations vanish. openpyxl 3.1.5 does exactly this and emits only
`UserWarning: Data Validation extension is not supported and will be removed`. **MEASURED, three
instances**: FME **35 of 54** (`7. AML-CFT` reports **0** where there are **5**, all of them `x14`);
`AL_monthly_report` **1 of 10**; `ITFS_Monthly_report` **7 of 16**.

**Injection.** `tests/negative/injectors/reader_nsblind.py` swaps `ingest/reader_lxml.py`'s validation
scan for `root.iter(M + "dataValidation")` — main namespace only. One line, identical mechanism.
Additionally, the *live* instance needs no injection at all: openpyxl 3.1.5 is a pinned dependency and
already does it.

**The tests that must reject it.**
- `tests/golden/test_schema_constants.py::test_golden__validations__fme` — asserts `54 = 35 + 19`, and
  asserts per-sheet `{'7. AML-CFT': 5}`. Under injection it reads 35 and 0.
- `tests/negative/test_nc_ingest.py::test_nc__P01_namespace_blind_reader_rejected` — asserts the D1
  agreement check flags `n_validations` disagreement and that every predicate reading a validated field
  returns `NOT_RUN(not_run.extractor_disagreement)`, **not** a silent absence.
- **Positive control, permanently pinned**:
  `tests/golden/test_x14_blindness_positive_control.py::test_golden__openpyxl_still_undercounts` asserts
  openpyxl returns `{FME: 35, AL_monthly: 1, ITFS: 7}` today. If openpyxl is ever fixed, this test fails
  and we learn it — with a `HARVEST-DELTA.md`-style recorded reason. **An absence claim about the
  ecosystem must be re-measured, not remembered.**

**Where.** `tests/negative/test_nc_ingest.py`, `tests/golden/test_schema_constants.py`.

#### NC-P02 — shared-formula invisibility

**The break.** A pass that keys on formula *text* loses every `<f t="shared" si="N"/>` dependent — an
element with no text. **MEASURED: 211 of 505 on FME (41.8%); 825 of 1,495 across the nine (55.2%); worst
case `ALR` at 399 of 645.** The loss concentrates on row and column totals, so **the measurement error is
correlated with the quantity being measured, in the direction that supports the thesis** — the most
dangerous shape a parser error can take.

**Injection.** `injectors/reader_textonly.py` — count a cell as formula-bearing only if
`(f.text or "").strip()`.

**The tests.**
- `test_golden__formula_cells__fme` asserts `505 == 294 + 211` and, per R-GOLD-2, asserts the *materialised
  text* of a named dependent: `'3. Portfolio'!O4 == "=SUM(C4:N4)"` (the row-shifted translation openpyxl
  gets right and a hand-rolled reader gets wrong).
- `test_nc__P02_shared_dependents_materialised` asserts the corpus-wide `1,495 / 825` split.
- `test_nc__P02b_encoding_is_recorded` asserts every formula cell's anchor carries
  `formula.encoding ∈ {TEXT, SHARED_MASTER, SHARED_DEPENDENT, ARRAY, NONE}` — recording the encoding is
  what makes the 294-versus-505 undercount impossible to repeat silently.

**Where.** `tests/negative/test_nc_ingest.py`, `tests/golden/test_schema_constants.py`.

#### NC-P03 — a matcher that cannot handle a valid form of the thing it matches · **REAL**

**The break.** A lexical rule over XML that does not cover every legal encoding of the element. The
corpus records `<f[ >][^>]*>` failing on the attributeless `<f>SUM(...)</f>`.

**A refinement measured for this document, and it changes the test design.** Re-running
`re.findall(r"<f[ >][^>]*>")` over the FME sheet XML returns a count **equal to the true formula-cell
count on every sheet** — while on `2. Summary` **50 of 50 matches swallowed the closing `</f>` tag**
(example match: `<f>'1. Introduction'!C54</f>`). The count is right and every extracted body is wrong.
**A count-only golden test passes against this defect.** Hence R-GOLD-2, and hence this control tests
*values*, not counts.

**Injection.** `injectors/formula_regex.py` replaces the element walk with the lexical rule.

**The tests.**
- `test_nc__P03_element_encodings_table` — table-driven over
  `{"<f>x</f>", "<f t=\"shared\" si=\"3\">x</f>", "<f t=\"shared\" si=\"3\"/>", "<f t=\"array\" ref=\"A1:A3\">x</f>", "<f/>"}`,
  asserting each is classified to the right `encoding` **and** that the extracted body is exactly `x` or
  `None`. The spanning-match defect fails on the body, not the count.
- **Standing structural rule**: `ci/no-regex-over-xml.sh` greps `src/cdfc/ingest/` and `src/cdfc/schema/`
  for `re.compile(r?["']<` and `findall(r?["']<` and fails the build. A lexical matcher over XML is a
  build error in this project, not a code-review comment.

**Where.** `tests/negative/test_nc_ingest.py`, `ci/no-regex-over-xml.sh`.

#### NC-P04 — the artifact is re-serialised

**The break.** Any code path that writes the received workbook back. openpyxl's round-trip takes the FME
file from **3,663,391 → 65,877 bytes**, deletes 24 parts including a 3.55 MB data model that is 96.9% of
the workbook, and removes all 19 `x14` validations (MEASURED). **If the pipeline ever re-serialises, the
hash we attest is a hash of something that is not the filing.**

**Injection.** `injectors/openpyxl_save.py` inserts `wb.save(tmp)` into `reader_openpyxl.py`.

**The tests.** `test_nc__P04_artifact_never_reserialised` — three teeth, because each catches what the
others cannot:
1. **Static**: an import-closure walk (`tests/negative/importgraph.py`) asserting `Workbook.save`,
   `zipfile.ZipFile(..., 'w')` and `open(..., 'wb')` are unreachable from
   `cdfc.{ingest,schema,facts,evaluate,verdict,probes,selfcheck,report}`.
2. **Runtime**: after a full run, `sha256(filing_path)` equals the receipt digest.
3. **Filesystem**: the run executes with the blob directory bind-mounted read-only; a write raises.
Plus `tests/golden/test_roundtrip_destruction.py` which pins **3,663,391 → 65,877** as a re-runnable
source for the README claim, so the number in the pitch has a script behind it.

**Where.** `tests/negative/test_nc_ingest.py`, `tests/golden/test_roundtrip_destruction.py`.

#### NC-P05 — the container guard runs after the parser

**The break.** Guard and parse in the wrong order, so a zip bomb or an XXE payload is parsed before it is
refused. An `.xlsx` is a zip of XML supplied by a hostile-capable party; **the parser, not the predicate,
is the exposed surface.**

**Injection.** `injectors/guard_after_parse.py` reorders F1 and F2 in the pipeline.

**The tests.**
- `test_nc__P05a_guard_precedes_parse` — feed `fixtures/adversarial/zipbomb-ratio__x1000.xlsx`; assert the
  outcome is `REJECTED` or `INVALID(invalid.container_guard_tripped)` **and that `lxml.etree.fromstring`
  was never called**, asserted by a spy installed in `conftest.py`.
- `test_nc__P05b_no_external_entities` — `fixtures/adversarial/xxe-entity__passwd.xlsx`; assert the parse
  raises and no file outside the fixture tree was opened (`resolve_entities=False`, no DTD, no network).
- `test_nc__P05c_guard_trip_is_not_a_FAIL` — assert the emitted cause is from the **run-level `invalid.*`
  vocabulary**, not a per-cell reason code (audit V.7.3). *A filing we could not safely open is not a
  filing that failed a check.*

**Where.** `tests/negative/test_nc_ingest.py`.

#### NC-P06 — the agreement check is partial

**The break.** D1 compares only the fields that are easy to compare, so a disagreement on
`hidden_sheets` passes. Scope truncation then enters through the door built to stop it.

**Injection.** `injectors/agreement_partial.py` — compare `n_sheets` only.

**The test.** `test_nc__P06_hidden_state_disagreement_is_INVALID` — a crafted fixture where the readers
agree on sheet count and names and disagree on hidden state; assert `INVALID` (spec A14), loudly, with the
run-level cause named.

---

### 2.2 SCHEMA INDUCTION AND THE DENOMINATOR (L1)

#### NC-D01 — scope truncation drops a hidden sheet from the denominator

**The break.** Iterate visible sheets only. `Dropdown` is `state="hidden"` **and the only unprotected
sheet**, and it holds all 15 controlled vocabularies. Its loss produces an *empty vocabulary set*, and
then `all(v in vocab for v in values)` passes vacuously over every membership predicate — **the vacuous
pass, arriving through the denominator rather than through the predicate.**

**Injection.** `injectors/induce_visible_only.py`.

**The tests.**
- `test_nc__D01a_hidden_sheet_in_schema` — `Dropdown` present with `state='hidden'`; 15 vocabularies
  non-empty; the FME denominator is 3,747 with the per-sheet split
  `{Portfolio 1698, Investors 897, PMS 480, Introduction 371, Summary 231, Complaints 25, Compliance Status 23, AML-CFT 22}`.
- `test_nc__D01b_empty_vocabulary_is_never_a_pass` — force a vocabulary to `[]` and assert the membership
  predicate binds zero cells ⇒ `ERROR(error.cells_bound_zero)` ⇒ run `INVALID`. **Two independent teeth:
  the count, and the vacuity path.**
- `test_nc__D01c_vocabulary_resolves_from_the_blank` — assert the vocabulary source is the pinned template
  digest and **never the filed artifact**. `Dropdown` is unprotected, so a predicate resolving from the
  filing validates the filer's data against a list the filer can edit. Injection:
  `injectors/vocab_from_filing.py`.

#### NC-D02 — the denominator computed from the same wrong parser as the numerator · **REAL, TWICE**

**The break, and it is the subtlest one in this document.** When numerator and denominator come from the
same reader, the ratio stays plausible and the error is invisible by construction. The corpus records this
committed **twice in one afternoon by the person who knew about it**: once by sampling mutation sites only
from cells the predicates already read (kill rate 100.0%), and once by computing 99.2% settled from a
denominator built out of the numerator.

**Injection — three separate injectors, because they are three different mistakes.**
- `injectors/denominator_from_predicates.py` — `fieldSurface := |cells any predicate reads|`. The 99.2%
  bug, verbatim.
- `injectors/denominator_single_path.py` — path B calls path A.
- `injectors/denominator_offbyone.py` — path B drops one cell, to exercise the escalation.

**The tests, four of them, and the fourth is the one that matters.**
1. `test_nc__D02a_denominator_provenance` — a structural assertion that `settledFraction.denominator` is
   produced by `schema/styles_mask.py::field_surface()` and that the import closure of `field_surface`
   **does not reach `cdfc.predicates`**. Spec A3.
2. `test_nc__D02b_disagreement_is_INVALID` — under `denominator_offbyone`, the run is
   `INVALID(invalid.denominator_disagreement)`.
3. `test_nc__D02c_paths_are_structurally_independent` — the import closures of `styles_mask.py` and
   `styles_mask_b.py` share no module inside `cdfc` except `cdfc.ingest.reader_lxml` (declared) — and the
   declaration is itself an assertion, so widening it is a visible diff.
4. **`test_nc__D02d_mutating_path_A_moves_only_path_A`** — mutate the shared reader's unlocked-mask
   extraction; assert path A's number changes and path B's does not. **This is the only test that
   distinguishes two implementations from one implementation called twice**, and it is the strongest single
   test in this document. Structural independence (3) can be satisfied by two copies of the same mistake;
   (4) cannot be satisfied by a shared dependency at all.

#### NC-D03 — a denominator returned for a template that has no protection mask · **REAL, ON DISK**

**The break.** Compute "unlocked, non-formula cells" unconditionally. On
`IFSCA_Annual_Reporting_Format` (**0 of 9 sheets protected, 1 unlocked style id**) that returns **8** — a
small, plausible, confident, wrong denominator. On `Draft_ACAC_Format` (0 of 13 protected, 0 unlocked ids)
it returns **0**, and `0/0` is the next defect. The correct answer for both is **`settledFraction: null`**
with `denominator.source = "not derivable — template ships no protection mask"`.

**Injection.** `injectors/mask_unconditional.py` removes the protection precondition.

**The tests.**
- `test_nc__D03a_no_mask_yields_null` over both workbooks — `settledFraction is None`, the source string
  exact, and **no digit renders anywhere in the settled-fraction block** (asserted by a regex over the
  rendered HTML fragment, the same technique as NC-Q08).
- `test_nc__D03b_null_is_not_zero` — assert the API returns `settled_fraction_ceiling: null`, distinct
  from `0`, per the absent≠empty≠zero rule.
- Positive control: `test_nc__D03c_masked_template_yields_a_number` on FME (3,747), so the guard is not
  simply refusing everything.

#### NC-D04 — coordinate-anchored keys silently rebind

**The break.** `key = (sheet, "O7")`. A row inserted upstream re-points every key below it, silently, at
a different row of the same table. Under a naive `(sheet, label-above, label-left)` key, **1,749 of 1,953
cells are ambiguous (89.6%)** because 100-row tables repeat the label pair; the row ordinal disambiguates
completely.

**Injection.** `injectors/keys_coordinate.py`.

**The tests.**
- `test_nc__D04a_row_insertion_does_not_rebind` — insert a row above a known FME table by raw-zip surgery;
  re-induce; assert **every** stable key resolves to the correct new ref **or** enters `UNRESOLVED` and
  **blocks** its predicates. Zero keys may point at a different label pair.
- `test_prop__stable_key_resolution` (property, §1.2) — the same statement over a generator of random row
  insertions.
- `test_nc__D04b_unresolved_blocks` — an `UNRESOLVED` key must block, not degrade to a guess.

---

### 2.3 PREDICATES AND QUALIFICATION (L3, L4)

#### NC-Q01 — a predicate binds zero cells and returns a vacuous pass

**The break.** `all([])` is `True`. `sum([]) == 0` passes a `len(rows) == declared` check as `0 == 0`. A
selector that missed a renamed sheet returns `PASS` with nothing checked and nothing logged. **This is the
failure mode the whole design exists to catch.**

**Injection.** `fixtures/predicates/broken/P-NC01__zero-bind.yaml` — a predicate whose `expr` iterates a
sheet named `'3. Portfolio '` (trailing space).

**The tests.**
- `test_nc__Q01a_zero_bind_is_ERROR` — `ERROR(error.cells_bound_zero)`, run `INVALID`. Never `PASS`, and
  **never `NOT_RUN`**, which would file the vacuous pass beside a rate-limited register. Spec A5.
- `test_nc__Q01b_empty_group_arithmetic` — a partition predicate whose group selector returns `[]` must
  not return `PASS`.
- `test_nc__Q01c_G1_rejects_at_admission` — the same envelope offered to the registry is rejected at G1
  with `cells_bound = 0`, so it never reaches a run.

#### NC-Q02 — a predicate with no qualification record loads

**The break.** The loader tolerates a missing `qualification` block, and the settled-fraction claim
silently becomes an assertion.

**Injection.** `fixtures/predicates/broken/P-NC02__no-qualification.yaml`.

**The test.** `test_nc__Q02_unqualified_predicate_does_not_load` — attempt admission; assert it raises;
assert the predicate is absent from the computed registry root; assert the root is unchanged. Spec §III.3.6
R7 requires exactly this test to exist.

#### NC-Q03 — a degenerate predicate is admitted · **REAL, ON DISK**

**The break.** A bound that asserts only "this is a number". `ALR_V2_3` ships **five** numeric-bound
validations of the form `≥ −100000000000000000` covering **1,428 cells**. Admitting them inflates the
settled fraction with checks that cannot fail.

**Injection.** `injectors/g3_disabled.py` — G3 returns `non_degenerate` unconditionally.

**The tests, and the pair is the point.**
- `test_nc__Q03a_alr_vacuous_bounds_rejected` — golden on `ALR` (`a414d8d3…`): exactly 5 of its 6 bound
  predicates rejected at G3, each producing a `rejection` row with `no_predicate.failed_qualification`,
  the measured number, and the cells it would have covered.
- **`test_nc__Q03b_fme_real_bounds_admitted`** — golden on FME: **19 of its 24 bounds are a real `≥ 0`**
  and must be admitted. **Without this positive control the gate is indistinguishable from a
  reject-everything baseline, which would score perfectly on the negative control alone.** Every
  rejection-side control in this catalogue carries an admission-side twin for the same reason.
- `test_nc__Q03c_settled_fraction_falls_on_rejection` — after the ALR rejections, ALR's settled fraction
  recomputes **downward**, and the `HARVEST-DELTA.md` entry exists.

#### NC-Q04 — declared keys diverge from the AST

**The break.** `schema_keys` is declared rather than derived, so the pre-flight set is wrong and rule 2 of
the evaluation contract is guarding the wrong keys. **The settled fraction stops being derivable and
becomes an estimate** — the single property that made CEL win over Python.

**Injection.** Two envelopes: `P-NC04a__reads-undeclared.yaml` (reads `filing.x`, declares `["filing.y"]`)
and `P-NC04b__declares-unread.yaml`.

**The test.** `test_nc__Q04_ast_checked_both_ways` — both rejected, with **distinct** rejection reasons, at
admission (R1). A single "keys mismatch" reason is a failure of the test: the two have different remedies.

#### NC-Q05 — the kill rate is computed over the wrong denominator · **REAL: MS = 100.1%**

**The break.** `MS = killed / (mutants − equivalent)` where equivalent mutants were excluded from *both*
numerator and denominator. The harness v1 printed **100.1%** — an arithmetically impossible number —
cleanly and confidently. The correct form is `KR = K/O` where `O = G − U` and `U` (unobservable) is a
**diff measured by recalculation**, never an equivalence theorem.

**Injection.** `injectors/kr_over_generated.py` (report `K/G`) and
`injectors/kr_double_exclusion.py` (the historical bug, verbatim).

**The tests.**
- `test_prop__kill_rate_arithmetic` (property) — `K ≤ O ≤ G` and `KR ≤ 1.0` for all campaign tallies.
- `test_nc__Q05a_impossible_score_raises` — feed the harness the historical tallies; assert it **raises**
  rather than printing a number above 1.0. The v1 output is a fixture:
  `fixtures/baselines/harness-v1-impossible.json`.
- `test_nc__Q05b_never_a_bare_percentage` — the renderer refuses a `KR` that is not accompanied by both
  integers, `U/G`, and the per-fault-class vector. Spec A9.
- `test_nc__Q05c_observability_filter_reports_its_own_rate` — `U/G` is computed per run and never assumed
  from the literature's 3,512 of 7,500 (46.8%); it is a property of *our* operator mix.

#### NC-Q06 — mutation sites sampled from the predicates' read set · **REAL: 100.0% on 3,574 mutants**

**The break.** `sites = {p.target} ∪ {p.srcs}`. Mutating only cells the checks read cannot do anything but
pass. **This is the degenerate-baseline failure, committed by the harness built to detect it.** The
current harness (`research/scripts/l4_mutation_harness.py`) records the bug and its fix in a comment; the
fix must become a test before the code moves into `src/`.

**Injection.** `injectors/sites_from_read_set.py`.

**The tests.**
- `test_nc__Q06a_site_set_is_the_field_surface` — `sites ⊇ field_surface`, asserted structurally against
  `schema/styles_mask.py`, **not** against the predicate graph. Spec T8.
- `test_nc__Q06b_control_arm_exists` — at least 10% of seeded sites lie outside every admitted predicate's
  read set (G3 empirical arm), and the count is reported.
- `test_nc__Q06c_flag_everything_fails_the_control_arm` — a predicate with `expr: "false"` scores
  perfectly on the kill rate and must be rejected by the control arm's spurious-fire count. **A kill rate
  without a control arm measures reach, not quality, and the report must say which it is showing.**

#### NC-Q07 — a degenerate or always-flagging predicate passes the proof arm

**The break.** G3's Z3 arm returns `unknown` (e.g. because a host function is uninterpreted) and the code
treats `unknown` as `non_degenerate`.

**Injection.** `injectors/z3_unknown_is_ok.py`.

**The tests.**
- `test_nc__Q07a_trivially_true_rejected` — `expr: "true"`: `¬P` UNSAT ⇒ reject.
- `test_nc__Q07b_always_flag_rejected` — `expr: "false"`: `P` UNSAT ⇒ reject.
- `test_nc__Q07c_unknown_is_unproven` — a predicate whose `expr` calls
  `nav_interval(...)` (uninterpreted) ⇒ Z3 `unknown` ⇒ the verdict recorded is `unknown`, the predicate
  does **not** clear G3 on the proof arm, and the empirical arm must decide. `unknown` is *unproven*,
  never *non-degenerate*.
- `test_nc__Q07d_subsumption` — `P₁ ∧ ¬P₂` UNSAT ⇒ `P₂` is redundant and the ILP removes it; assert the
  removal is recorded, not silent.

#### NC-Q08 — a `SELF-AUTHORED` false-failure rate renders as a number

**The break.** Printing `0.0% false failures across 340 clean filings` when the authors of the corpus also
wrote the predicates. **Expected value zero regardless of predicate quality — worse than printing nothing,
because it has the shape of evidence.**

**Injection.** `injectors/render_self_authored_ffr.py` formats the rate anyway.

**The tests.**
- `test_nc__Q08a_renders_uninformative` — render a predicate with
  `corpus_provenance: SELF-AUTHORED`; assert the output contains the word `uninformative` and **contains
  no digit within the FFR element** (`re.search(r"\d", ffr_fragment) is None`). Spec A4.
- `test_nc__Q08b_api_returns_null` — `GET /v1/predicates` returns `ffr: null` with
  `g4_corpus_provenance: "SELF-AUTHORED"`, so a client cannot display it either.
- `test_nc__Q08c_no_ffr_without_provenance_and_n` — any FFR lacking `corpus_id`, `corpus_provenance` or
  `n` fails render. Spec M2 acceptance.

#### NC-Q09 — severity keyed on the point estimate instead of the Wilson upper bound

**The break.** `0 fires / 4 filings` has a point estimate of 0.000 and an interval of `[0.000, 0.490]`. A
rule keyed on the point estimate lets a sample of four buy `BLOCKING`.

**Injection.** `injectors/severity_point_estimate.py`.

**The test.** `test_nc__Q09_severity_uses_wilson_upper` — table-driven:
`(0,4) → upper 0.490 → NOT ADMITTED`; `(2,96) → [0.006, 0.074] → ADVISORY`;
`(0,185) → upper ≤ 0.02 → BLOCKING`. Plus the pre-registered thresholds asserted as constants:
`≤0.02 BLOCKING · 0.02–0.10 ADVISORY · >0.10 not admitted`. Plus the consequence stated as a test:
`test_nc__Q09b_day_one_has_almost_nothing_blocking` — over the current corpus, assert the BLOCKING count is
0 and that the report says so, so nobody is surprised on stage.

#### NC-Q10 — set-level FFR ignored, and the registry drifts to flag-everything

**The break.** Admitting checks one at a time, each individually under budget. **FFR is monotone
non-decreasing under union**: in two of SPADE's nine pipelines, sets whose every member individually met
the constraint reached composite FFR of **88%** and **53%**.

**Injection.** `injectors/set_ffr_is_mean.py`.

**The tests.**
- `test_prop__set_ffr_subadditivity` — the bound `max(FFR(S),FFR(f)) ≤ FFR(S∪{f}) ≤ FFR(S)+FFR(f)` holds
  for the computed set FFR over random fire-vectors. The mean implementation violates the lower bound on a
  crafted pair.
- `test_nc__Q10_marginal_ffr_is_recorded` — every admitted predicate carries `marginal_ffr` and
  `conditioned_on[]`; a predicate admitted without them fails to load.

#### NC-Q11 — G0 lets a proviso through

**The break.** A candidate implements the main rule and silently drops the exception. Frontier models
ground clause spans well (SpanFaith 0.77–0.79) and wire exception structure badly (Edge-F1 0.215–0.246
over 2,290 provisions), and **the empirical gates cannot see a dropped proviso** — that is why G0 exists
and why it runs first.

**Injection.** `fixtures/predicates/broken/P-NC11a__undeclared-proviso.yaml` (span contains
"Provided that…", envelope has neither branch nor declaration) and
`P-NC11b__quote-not-verbatim.yaml` (one character changed — specifically `U+002D → U+2011`, the homoglyph
the register actually contains).

**The tests.**
- `test_nc__Q11a_undeclared_proviso_rejected` — reject at G0; a predicate that neither implements nor
  declares is refused.
- `test_nc__Q11b_verbatim_quote_required` — `source.find(quote)` must succeed deterministically; the
  homoglyph variant is rejected. Zero model cost, at the boundary.
- `test_nc__Q11c_declared_proviso_emits_a_record` — a declared proviso caps the predicate at `ADVISORY`,
  stamps `scopeIncomplete[]` on every item it settles, and emits one
  `NO_PREDICATE(no_predicate.not_yet_synthesised)` into `scopeCaveats[]` carrying the verbatim text and
  character span. Positive control for the same gate.

---

### 2.4 EVALUATION AND VERDICT (L5)

#### NC-E01 — an evaluator swallows an exception into a clean state

**The break.** `except Exception: state = NOT_RUN` — **a crash that looks like a limit.** The two states
have opposite remedies: `ERROR(error.predicate_raised)` means fix the code and makes the run `INVALID`;
`NOT_RUN(not_run.source_unreadable)` means retry and leaves the run valid. Great Expectations ships the
even worse version — with `catch_exceptions=True`, an expectation that *could not be evaluated* returns
`success = False`, the same value it returns when it evaluated and the data was wrong.

**Injection.** `injectors/evaluate_swallow.py`.

**The tests.**
- `test_nc__E01a_predicate_raise_is_ERROR_and_INVALID` — a host function that raises ⇒
  `ERROR(error.predicate_raised)` ⇒ `run_state = INVALID`. Assert it is **not** `NOT_RUN`.
- `ci/no-bare-except.sh` — a bare `except:` or an `except Exception:` without a re-raise anywhere under
  `src/cdfc/{evaluate,verdict,selfcheck,probes}` fails the build.
- `test_nc__E01b_budget_is_not_a_failure` — budget exhaustion ⇒ `NOT_RUN(not_run.budget_exhausted)`, never
  `FAIL`. A check that ran out of time has told us nothing about the filing.

#### NC-E02 — CEL's own error absorption manufactures a pass

**The break, and it is manufactured by the language.** The CEL specification states that for `||` and
`&&`, if one operand determines the result, a **runtime error in the other operand "will be ignored."**
So `true || <error>` evaluates to `true`, and an unguarded predicate returns `PASS` while silently
swallowing an operand that could not be evaluated at all. The structural mitigation is rule 2 of the
evaluation contract: **pre-flight every declared key before `expr` is evaluated at all**, which makes the
guard independent of how the predicate was written. Because `schema_keys` is machine-checked against the
AST, the pre-flight set is exact rather than an estimate.

**Injection.** `injectors/preflight_disabled.py`.

**The tests.**
- `test_nc__E02a_absorption_cannot_manufacture_a_pass` (spec A13) — the predicate
  `expr: "size(filing.intro.tbl15.rows) >= 0 || filing.MISSING.key == 1"` returns
  `NOT_RUN(not_run.source_unreadable: filing.MISSING.key)`.
- **`test_nc__E02b_the_guard_is_load_bearing`** — under `preflight_disabled`, the *same* predicate returns
  `PASS`. The meta-sweep asserts this flip occurs. **This is the exemplar of the whole document: without
  the injector, E02a is a test that has never been observed to fail, and therefore not evidence.**
- `test_nc__E02c_conformance_on_error_semantics` — run the CEL conformance suite against both `celpy` and
  `cel-expr-python` and record which runtime the registry root was qualified against. If they diverge *on
  error semantics specifically*, the rule-2 guard behaves differently between them, and the divergence
  must be recorded in `qualified_against.evaluator_version`.

#### NC-E03 — the evaluator drifts from the evaluation contract

**The break.** `EVALUATION-CONTRACT.md` and `evaluate/contract.py` disagree. Three different versions of
the five rules were live at once in the drafts; a build cannot satisfy two fives.

**Injection.** `injectors/contract_table_edit.py` changes one cell of the generated table.

**The test.** `test_contract__evaluation_contract_matches_evaluator` — parse the markdown transition table
out of `EVALUATION-CONTRACT.md`, compare **set-equal** to `evaluate/contract.py::TRANSITIONS`. Plus
`test_nc__E03b_contract_is_generated_not_edited` — regenerate from spec §II.3.4 and assert byte-identity,
so a hand edit to the contract file fails the build.

#### NC-E04 — the roll-up precedence is inverted

**The break.** `PASS ≻ INDETERMINATE ≻ NOT_RUN` — the order withdrawn by audit V.7.1. Under it, a cell
read by one passing and one not-run predicate is *settled*, so **a passing predicate absorbs the un-run
one and the settled fraction holds** in exactly the case the design was written for: reader disagreement,
where the fraction must fall and not silently succeed.

**Injection.** `injectors/rollup_pass_wins.py` swaps the precedence tuple.

**The tests.**
- `test_nc__E04a_notrun_absorbs_pass` — a cell with one `PASS` and one `NOT_RUN` evaluation is **unsettled**.
- `test_nc__E04b_precedence_is_normative` — assert the tuple equals
  `(ERROR, FAIL, INDETERMINATE, NOT_RUN, PASS, INFORMATIONAL, OUT_OF_SCOPE)` and that `NO_PREDICATE` is
  **not** in the order (it is the state of a cell with an empty evaluation set).
- `test_nc__E04c_extractor_disagreement_lowers_the_fraction` — the end-to-end statement: inject a D1
  field-level disagreement and assert the settled fraction **falls**.

#### NC-E05 — closure has a hole

**The break.** The five-term closure that was in circulation has no bucket for `INFORMATIONAL` or `ERROR`,
so every informational item aborts the report — or, worse, a cell lands in no bucket and the arithmetic
still balances because two errors cancel. The in-toto specification names the hazard in its own text: an
implicit open world *"could allow artifacts to sneak into the step or inspection undetected."*

**Injection.** `injectors/closure_five_term.py`.

**The tests.**
- `test_prop__closure_seven_terms` (property) — for every random assignment of the 8 states over N cells,
  `outOfScope + informational + settled + indeterminate + notRun + noPredicate + error == fieldSurface`.
  Spec A12.
- `test_nc__E05a_unbucketed_cell_aborts_the_report` — plant a cell with a state outside the 8; assert
  report generation **aborts**. There is no degraded report.
- `test_nc__E05b_informational_run_does_not_abort` — the positive control: a run containing
  `INFORMATIONAL` items completes under the seven-term form and aborts under the five-term injection.

#### NC-E06 — reason-code discipline inverts

**The break.** A reason code present on a `PASS`, or absent on a `NOT_RUN`.

**The test.** `test_contract__reason_code_required_iff_state_not_pass_or_fail` — exhaustive over the
8 × 31 product (30 codes plus `null`). Injection: `injectors/reason_optional.py`.

#### NC-E07 — floating-point money

**The break.** A `float` anywhere on the verdict path. CEL has no decimal type; guidance C111 fixes 2 dp
on USD Million, so the quantum is USD 10,000 and lawful per-cell slack is USD 5,000. As `double`, **every
arithmetic predicate acquires a false-failure rate we did not choose and cannot attribute.**

**Injection.** `injectors/float_money.py` casts through `float` in `facts/units.py`.

**The tests.**
- `test_prop__money_roundtrip_exact` — `12.34 → 12340 → 12.34` for every 2-dp value in the `int64` range.
  The float cast breaks it at `12.34 → 12.339999999999999`.
- `test_nc__E07_no_float_in_fact_table` — every money-typed fact `isinstance(v, int)`.
- `ci/no-float-money.sh` — `float(`, `/ ` on a money-typed symbol, and `math.` imports under
  `src/cdfc/{facts,evaluate,verdict}` fail the build.

#### NC-E08 — tolerance applied to counts

**The break.** `τ(n) = 5n` applied to a `COUNT`-typed cell. **A person is not a rounded quantity, and
slack there is how a missing investor hides.**

**Injection.** `injectors/tolerance_on_counts.py`.

**The test.** `test_nc__E08_counts_get_zero_tolerance` — a mutant that changes an investor count by 1 must
be **killed**; under injection it survives and the test goes red. Positive control:
`test_nc__E08b_money_gets_tau` — a mutant inside `τ(n)` on a money cell must **not** fire, so the guard is
not simply zero-tolerance everywhere.

---

### 2.5 SELF-CHECK, CANARIES AND RESIDUE (L6.5)

#### NC-C01 — a canary has gone silent

**The break, in two forms.** (a) A predicate's stored `kill_case` no longer dies — parser drift, a renamed
sheet, hidden-sheet truncation, an encoding change — and the run still issues a verdict. (b) The canary
*loop itself* is broken and reports `canaries_passed == canaries_run` unconditionally, which is the same
silent pass one level up.

**Injection.** `injectors/canaries_noop.py` (the loop returns success unconditionally) and the fixture
`fixtures/synthetic/renamed-sheet__portfolio.xlsx`, plus the CLI path `cdfc demo --break-parser`.

**The tests.**
- `test_nc__C01a_renamed_sheet_yields_INVALID` — `run_state == INVALID`, cause `error.canary_silent`,
  `dead_predicates[]` populated with the specific ids, **and `settledFraction is None`** — not zero, not
  omitted, `null`. The report renders the reason and no fraction of any kind. Spec T10.
- `test_nc__C01b_noop_loop_is_detected` — a **seeded dead predicate** (one whose `expr` is `true`, so its
  `kill_case` cannot kill it) is injected into every canary run under `CDFC_CANARY_SELFTEST=1`; the run
  must go `INVALID` naming it. Under `canaries_noop` it does not, and the test goes red.
  **This is the canary for the canary loop**, and §7.7 states plainly where that recursion stops.
- `test_nc__C01c_canary_never_touches_the_file` — canaries operate on the in-memory fact table; assert no
  filesystem write and no re-serialisation occurs during the loop (ties to NC-P04).

#### NC-C02 — the residue set comes back empty

**The break.** A residue computation that returns zero survivors, which would look like completeness and
is in fact either a construction error or a bug. **The class is non-empty by construction**: a coordinated
misstatement propagated through all 181 cross-sheet carries and all 35 SUM identities is internally perfect
under every relation the template encodes and every relation we have added.

**Injection.** `injectors/residue_short_circuit.py`.

**The test.** `test_nc__C02_coordinated_misstatement_survives` — construct the survivor (scale every
quantity in a connected component of the carry graph by the same factor), run the full admitted set **and**
every admitted relation, assert **no** rejection. **The failure message must not say "assertion failed";
it must say: either the construction is wrong or a relation is stronger than we believed — investigate
which, because both are findings.** The survivor is content-addressed and rendered in the Unchecked panel
as an exhibit, not as a reason.

Companion, because the residue's only human step must be auditable:
`test_nc__C02b_adjudication_record_is_content_addressed` — `|RESIDUE|` is reproducible only given the
published fault model **and** the published adjudication record; a residue reported without the
adjudication record's hash fails to render.

---

### 2.6 ATTESTATION, REPORT AND SURFACES (L7)

#### NC-A01 — the attestation can be made to express a pass

**The break.** A `result`, `status` or `pass` property anywhere in the schema. **A surface that can render
all-clear will eventually render it wrongly**, and prohibiting it in the schema is the only version of that
commitment that is a system property rather than a preference.

**Injection — and the injector is designed to defeat the naive checker.**
`injectors/schema_status_deep.py` adds `{"status": {"type": "string"}}` **inside a `$defs` entry
referenced from an `allOf` two levels down**. A top-level property scan misses it entirely.

**The tests.**
- `test_contract__attestation_cannot_express_a_pass` — a recursive walker
  (`tests/contract/schema_walk.py`) descends `properties`, `$defs`, `definitions`, `allOf`, `anyOf`,
  `oneOf`, `not`, `items`, `prefixItems`, `patternProperties`, `additionalProperties` and
  `propertyNames`, asserting no property named
  `result | status | pass | passed | passing | compliant | conformant | ok | success | clean` at any
  depth, case-insensitive. Spec A2.
- `test_nc__A01b_additional_properties_false_everywhere` — every object schema sets
  `additionalProperties: false`, so a consumer cannot write one in at runtime either.
- `test_nc__A01c_instance_with_status_is_rejected` — the data-side twin: serialise an attestation with an
  extra `status` key and assert the validator rejects it.
- `test_nc__A01d_top_level_is_scope` and `test_nc__A01e_four_statements_required` — bounded silence,
  purpose, `summaryIsNotSubstitute`, and the deception boundary are `required` by schema, not template
  strings.

#### NC-A02 — an all-clear glyph or phrase reaches a user surface

**The break.** `✓ ✔ ✅ 🟢 ✔️ 👍`, or `all clear / no issues / looks good / verified clean / compliant /
passed all / fully checked`, anywhere a user can see.

**Injection.** `injectors/plant_glyph.py` writes `✅` into a file under `src/cdfc/report/templates/`.

**The tests.**
- `test_nc__A02a_grep_catches_a_planted_glyph` — `ci/no-green-tick.sh` exits non-zero under injection.
  Spec A1.
- **`test_nc__A02b_scan_set_covers_every_rendered_surface`** — enumerate every Jinja template and static
  asset actually referenced by `report/render.py` and by the FastAPI app, and assert each path lies inside
  the script's scan set (`src/ templates/ locales/ static/`). **This closes the hole where the grep passes
  because it stopped scanning the right directory — scope truncation applied to our own CI, which is the
  same defect as NC-D01 one level up.**
- `test_nc__A02c_ban_list_prose_is_outside_the_scan_set` — the spec's ban list quotes the banned phrases,
  so it lives in `docs/`, deliberately outside the scan set, and a test asserts `docs/` is excluded *and
  that the exclusion is exactly `docs/`* rather than a wildcard.
- `test_nc__A02d_no_state_name_means_clean` — assert the verdict enum contains
  `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_SCOPE` and no shorter synonym; assert the report title string is a
  function of the verdict state.

#### NC-A03 — the report does not re-derive

**The break, in five named forms**, each with its own injector because each is a different mistake:
`now_in_renderer` · `unsorted_rollup` (dict/set iteration without an explicit sort key) ·
`live_register` · `float_money` · `locale_number_format`.

**The tests.**
- `test_e2e__verify_byte_identical` — two runs under different TZ, `PYTHONHASHSEED`, locale and cwd, then
  `cdfc verify` on a **second runner image**. Byte-identical `report.html`, `attestation.json`,
  `run.jsonl`. Spec A7.
- `test_nc__A03a_each_injector_breaks_determinism` — the sweep asserts all five injectors turn the
  determinism test red. An injector that does **not** break it means the pipeline has an untested
  dependency on that source, which is also a finding.
- `test_nc__A03b_tamper_changes_the_hash` — flip one byte of the filing; `verify` reports a diff, not
  `REPRODUCED`.
- `test_nc__A03c_manifest_pins_eight_things` —
  `{template_sha256, filing_sha256, registry_root, register_snapshot_sha256, code_git_sha,
  evaluator_version, fault_model_version, tool_versions{python, lxml, openpyxl, celpy, z3}}`, and
  **`libreoffice` is asserted absent** from the pin.

#### NC-A04 — a model client is importable from the verdict path

**The break.** Any route from L5/L6/L7 to a model endpoint. The spec lists
`test_no_model_in_verdict_path` as a build gate and records it as **not yet written**; *this entry is where
it gets written*, and the claim moves from "specified" to "a property of a running system" the day it
lands.

**Injection.** `injectors/import_model_client.py` (a static `import anthropic` at the top of
`verdict/aggregate.py`) and `injectors/dynamic_http_in_host_fn.py` (a runtime `httpx.get` inside a host
function — invisible to the static check).

**The tests, and neither is sufficient alone.**
- `test_nc__A04a_no_model_import_reachable` — build the AST import closure of `cdfc.evaluate`,
  `cdfc.verdict`, `cdfc.probes`, `cdfc.selfcheck`, `cdfc.attest`, `cdfc.report`; assert
  `{anthropic, openai, httpx, requests, urllib.request, http.client, socket}` are absent. Catches the
  static import that no test input happens to exercise.
- `test_nc__A04b_verdict_runs_with_no_network` — monkeypatch `socket.socket` to raise, run a full FME
  filing, assert `run_state == VALID`. Catches the dynamic call the static walk cannot see.
- `test_no_libreoffice_online` — `subprocess` absent from the online closure and no `soffice` string under
  the online packages. Spec G12.
- `test_no_tlog` — the signing call carries `--tlog-upload=false` and the keyless code path is unreachable.
  Injection: remove the flag.

#### NC-A05 — the headline renders without the admission state

**The break.** Printing `2,373 of 3,747` without `PRE-GATE`. **None of the 280 predicates is admitted
under gate G4**, and a surface that prints the number without the label is shipping exactly what the gate
is designed to refuse.

**Injection.** `injectors/move_pregate_to_footer.py`.

**The test.** `test_nc__A05_pre_gate_in_the_same_block` — parse the rendered HTML; assert the `PRE-GATE`
string and the settled count share an ancestor element within 2 levels, **not merely that both appear on
the page**. Spec A11. Companion: `test_nc__A05b_two_counts_equal_weight` — the failing-cell count and the
unchecked-cell count resolve to the same computed font-size, colour and ink in the rendered CSS, and the
unchecked segment is **hatched, not muted**.

---

### 2.7 EXTERNAL SOURCES AND HOST FUNCTIONS

#### NC-X01 — a host function resolves live at verdict time

**The break.** `reg_resolves(kind, number)` hits the register during a run. The register is **live and
undated**; a verdict citing "the register" without a snapshot hash is not reproducible and cannot be
signed.

**Injection.** `injectors/live_register.py`.

**The test.** `test_nc__X01_host_fn_reads_the_snapshot_only` — under a blocked socket the function returns
from `register_snapshot_sha256`; two runs at different wall-clock times return the same tri-state answer;
a run whose snapshot is older than the staleness bound degrades to
`NOT_RUN(not_run.input_unavailable.register)` rather than silently using it.

#### NC-X02 — an absence is reported from the wrong field · **REAL**

**The break.** `EncryptDId` is null in **2,005 of 2,005** records while `EncryptedId` is populated in
2,005 of 2,005. Keying on the first returns HTTP 302 on every record forever and yields an
honest-looking absence. **The positive-control rule would have caught it and was not run.**

**Injection and mechanisation — this one is a conduct control turned into a code control.**
`src/cdfc/measure/absence.py::assert_absent(query, positive_control, corpus)` is the **only** sanctioned way
to record an absence anywhere in this project: it refuses to return unless `positive_control` returns a
non-zero count over the same corpus through the same interface, and it writes both counts to
`reports/validation-ledger.jsonl`.

**The tests.**
- `test_nc__X02a_absence_without_a_positive_control_raises` — calling `assert_absent` with
  `positive_control=None` raises at call time.
- `test_nc__X02b_dead_control_raises` — a positive control that itself returns zero raises; a broken
  interface must not be reported as an empty world.
- `ci/no-bare-absence.sh` — greps `src/`, `tests/` and `docs/` for the strings
  `"does not occur"`, `"zero hits"`, `"not present in"`, `"no occurrences"`, and requires the line to carry
  a **resolvable reference**, not a phrase: `ledger:<row_id>` naming a row of
  `reports/validation-ledger.jsonl`, which the gate **resolves** and whose `positive_control_count` it
  asserts is `> 0`. The corpus's `NAV` absence claim (`Scheme` 123, `USD Million` 31, `Portfolio` 25,
  `valuation` 6 as controls) is the model row.
- **`test_nc__X02c_the_gate_requires_a_resolvable_row_not_a_phrase`** — the gate's own negative control,
  in two halves because they are two different defeats. (a) A line asserting an absence and containing the
  literal words *"positive control"* and no row id **fails** — the old rule was a lexical co-occurrence and
  any author who had read the gate could satisfy it in four words. (b) A line citing a ledger row whose
  `positive_control_count` is `0` **fails** — a dead control is the `EncryptDId` defect itself, and
  `assert_absent` already writes both counts, so the grep should read them rather than trust a phrase.

#### NC-X03 — normalisation destroys the evidence that normalisation was load-bearing

**The break.** Storing only the normalised value. One live regulated entity's registration number contains
`U+2011 NON-BREAKING HYPHEN` rather than `U+002D` — visually identical, byte-wise different, invisible in
any log or screenshot.

**Injection.** `injectors/store_normalised_only.py`.

**The test.** `test_nc__X03_raw_and_normalised_both_stored` — a `register_record` anchor carries
`raw_value`, `normalised_value` **and** the ordered transformation list (`NFKC`, `U+2011 → U+002D`, strip,
case-fold); assert the `U+2011` record is byte-distinguishable from a `U+002D` record after storage.
Companion: `test_nc__X03b_membership_not_format` — the admitted identity predicate is **set membership
against the snapshot under the declared normalisation**, never a format grammar; the format regex
`^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$` fires on **87 of 228 live FMEs (38.2%, MEASURED)** and is the
worked example in `counterEvidence[]` of why the FFR column exists.

#### NC-X04 — a host function cannot return its third value

**The break.** `nav_interval(scheme_type, open_closed, tenure)` resolving reg 51(1)'s delegation —
*"in such manner as specified by the Authority"* — into a concrete interval. **A system that resolves that
delegation is asserting something the regulation does not say.**

**Injection.** `injectors/nav_interval_resolves.py`.

**The tests.**
- `test_nc__X04a_underspecified_is_returnable` — for the delegated input the function returns
  `UNDERSPECIFIED`, and the item becomes `NO_PREDICATE(no_predicate.no_obligation_specified)` — **never**
  `.not_yet_synthesised`. Conflating "the regulator did not legislate this" with "we haven't got round to
  it" would be the most misleading thing the report could do.
- `test_nc__X04b_host_registry_is_closed` — an unregistered host function reference is rejected at
  admission (R2), and the set is closed at evaluation time.
- `test_nc__X04c_every_host_fn_has_test_vectors_and_a_mutation_score` — a `host_function` row lacking
  `test_vector_sha256` or `mutation_score_json` does not load.

#### NC-X05 — a version event passes unnoticed

**The break.** A predicate keeps computing a date difference against a rule that no longer exists. **This
is realised, not hypothetical**: the 29th IFSCA Authority Meeting of 24 July 2026 let close-ended
Restricted Schemes move NAV periodicity from semi-annual to annual with 75% investor approval by value —
**a fact the workbook does not collect.** The predicate neither errors nor abstains. A filer who lawfully
moved gets a false failure; a filer who moved without approval gets a silent pass. Both outputs are clean,
confident and well-formed.

**Injection.** `injectors/watcher_reports_no_change.py` (a fetch failure recorded as "no change") and
`injectors/qualified_against_not_identity.py` (a template hash bump that does not move the predicate).

**The tests.**
- `test_nc__X05a_template_bump_moves_predicates_to_PROVISIONAL` — bump `template_sha256`; assert affected
  predicates go `PROVISIONAL`, **still run** (detection is not lost), have their numbers hidden, and are
  **excluded from the settled numerator**; assert the settled fraction **falls**. Spec A8.
- `test_nc__X05b_watch_gap_is_not_no_change` — a fetch failure writes a `gap_since` row to
  `instrument_watch`, never `changed = false`. **An unobserved day is not a quiet day.**
- `test_nc__X05c_V5_alone_does_not_catch_a_rule_change` — the honest limit, asserted: build the
  NAV-frequency predicate's `kill_case` against the semi-annual rule, apply the July 2026 rule change, and
  assert the canary **still passes** — because the mutant and the predicate moved together. The test's
  purpose is to prove V5 is insufficient and that V6 (the instrument watcher) is doing the work. A test
  that documents a limit is worth more than a test that hides it.

---

### 2.8 Entries where a negative control is impossible

Recorded with `injector: NONE`, a mandatory `why_impossible` **and a mandatory `substitute_measurement`**.
The sweep reports them separately and the count appears in every phase gate. **The "What it costs" column
below is the argument; the `substitute_measurement` field is the artifact**, and where the column names a
substitute (NC-N02's re-adjudicated 20% and its κ; NC-N03's brief hash, commit-order test and contamination
probe; NC-N06's `constructs_not_understood` list) that substitute moves into the field verbatim, with its
command. Where a row's column names **no** substitute — NC-N01, NC-N04, NC-N05 — the field records that
fact in those words, because *"there is no substitute instrument for this"* is a finding and an empty field
is an oversight, and the two must not look alike.

| id | The thing we cannot break mechanically | What it costs |
|---|---|---|
| NC-N01 | **That a predicate encodes the obligation it claims to.** G0 proves the quote locates and the provisos are declared; nothing proves the CEL *means* the clause. The only published study of statute→executable-model generation tops out at **51–53% outcome equivalence** | A predicate can pass all five gates and implement a rule that does not exist. Partial mitigation only: G2's kill vector by fault class, and human review at R7 |
| NC-N02 | **The INNOCUOUS/WRONG adjudication.** It is a human judgment; injecting a wrong label is trivial but the correct label is the human's | `\|RESIDUE\|` inherits an unquantified adjudication error. Substitute measurement, not a test: re-adjudicate a random 20% by a second human and publish Cohen's κ with `n` |
| NC-N03 | **That the blind-fill corpus is genuinely blind.** Blindness is a property of a person's history, not of an artifact | Every `BLIND-FILLED` FFR rests on a procedure, not a test. Substitutes in §6.3: the pre-published fill-brief hash, the commit-order test, and a weak post-hoc contamination probe |
| NC-N04 | **That the regulator's template is correct.** It is not: its own scheme total uses three COUNTIFs that between them miss two of its nine legal scheme types (the `D17` defect) | The criterion source is authoritative but not correct. We can cite, version and watch it; we cannot validate it |
| NC-N05 | **Deception.** Every check is a consistency check over a self-reported document | *A coherent liar passes all of them.* Permanent, on the report surface |
| NC-N06 | **That the two "independent" readers do not share a misconception.** Both were written by people reading the same OOXML spec | See §7.5. Only the extraction manifest's `constructs_not_understood` list mitigates, and it lists only what we knew to look for |

---

## §3 — MUTATION TESTING OF OUR OWN TEST SUITE

### 3.1 The distinction, stated first because it is constantly conflated

**Two activities exist in this system. They share a word and nothing else.**

| | **Mutating CODE** | **Seeding faults into DATA** |
|---|---|---|
| Subject under evaluation | **our test suite** | **the admitted predicate set** |
| Artifact mutated | `src/cdfc/**/*.py` | a filed `.xlsx`, by raw-zip surgery |
| A mutant is | source with one edit | a filing with one cell perturbed |
| "Killed" means | a test fails | a predicate returns `FAIL` |
| Nuisance class | the **equivalent mutant** — undecidable in general, a *theorem* | the **unobservable mutant** — measurable by recalculation, a *diff*; and the **INNOCUOUS** mutant, a human judgment |
| Denominator | `V − E`, where `E` is adjudicated | `O = G − U`, where `U` is measured |
| Tool | **mutmut 3.7.0** | **ours** — `src/cdfc/qualify/mutants.py`, 7,946 mutants/s (MEASURED) |
| Gate | CI stage 11 | qualification gate **G2** |
| Reported in | `reports/mutation/<module>.json` and the phase gate | the predicate's `qualification.g2` block |

**A document that quotes "mutation score" without saying which of these it means has quoted an ambiguous
number**, and a phase gate that reports one while claiming the other has committed the error this project
exists to make impossible. Every phase gate prints both, labelled.

`mutmut`/PIT/Stryker are a **category error** for G2 — they mutate source code and ask whether *your
tests* fail. They are exactly right one level up, which is this section.

### 3.2 The tool decision

**DECIDED: `mutmut` 3.7.0.** Licence **BSD-3 — SECONDARY** (PyPI metadata; **LICENSE not opened**; §5.2
makes opening it a Phase-0 gate). It is a **dev-time tool, not a runtime dependency**, so the licence
exposure is confined to the build.

*Reasons:* the spec's ledger already pins it (row 42, "retained for mutating **our own** code"); its
trampoline-based rewriting in 3.x needs no separate session database for the common case; and it runs
under pytest without a plugin layer of its own.

*Runner-up: `cosmic-ray` (MIT — SECONDARY; the comparative study favouring it was **not opened —
UNVERIFIED**, and this document does not lean on it).* **Switch trigger, stated in advance:** if mutmut's
rewriting cannot handle `predicates/ast_walker.py` or `evaluate/celrt.py`, **or** if mutant identifiers are
not stable across runs, switch to cosmic-ray, whose explicit session database makes each mutant addressable.

*Rejected: `mutpy`* — no release since 2019, no declared Python 3.12 support, and adopting an unmaintained
tool to measure our own discipline is self-refuting.

**The decoupling that makes the switch cheap and the ledger durable.** Whichever tool runs, our wrapper
(`tools/mutation/run.py`) rewrites results into our own record keyed by a **stable mutant id** we compute:

```
mutant_id = sha256(f"{repo_relative_path}\n{line_no}\n{original_line}\n{mutated_line}\n{operator}")
```

so `docs/EQUIVALENT-MUTANTS.md` and `reports/mutation/*.ledger.jsonl` survive a tool change. Tool ids are
never persisted.

### 3.3 The operator set

mutmut's operator families, all enabled: numeric literals (including `0 ↔ 1` and off-by-one), string
literals, comparison operators (`< ↔ <=`, `== ↔ !=`), boolean operators (`and ↔ or`), `not` insertion and
deletion, arithmetic operators, `break ↔ continue`, argument defaults, `return None` insertion, and
decorator removal.

**No operator is disabled to raise a score.** Disabling operators is the manipulation this project bans;
what we do instead is *adjudicate survivors* (§3.4). Files are excluded only via
`tools/mutation/exclude.toml`, and `test_mutation__every_exclusion_has_a_reason` asserts each entry
carries a non-empty `reason`. The sanctioned exclusions are: generated files (`EVALUATION-CONTRACT.md`'s
generator output), `__init__.py` re-export shims, and CLI argument wiring in `cli.py`.

Three operators deserve a note because they interact with this domain:
- **String-literal mutation on reason codes is kept.** Mutating `"not_run.budget_exhausted"` to a
  neighbour must be killed — if it is not, the code path is untested, and that is exactly the gap we want
  to see. It is *not* noise here.
- **Comparison-boundary mutation on tolerances is kept and is high-value.** `abs(d) <= τ` → `abs(d) < τ`
  must be killed by a straddle test; if it survives, the `indeterminate.tolerance_straddle` path is
  untested.
- **`and ↔ or` mutation on `evaluate/preflight.py` is the single most important mutant in the
  repository**, because it is the code-level analogue of NC-E02. It must be killed.

### 3.4 The equivalent-mutant problem, handled rather than hidden

For **code** mutation, equivalence is undecidable in general — unlike the data case, where `U` is a
measured diff. The treatment:

1. Every survivor is triaged into exactly one of: `KILLED-LATE` (a test was missing; write it),
   `EQUIVALENT` (with a written argument), or `SURVIVOR` (a real, accepted gap with a tracking id).
2. `EQUIVALENT` requires a row in `reports/mutation/<module>.ledger.jsonl`:
   `{mutant_id, path, line, operator, argument, adjudicated_by, date}` — the argument is prose, and it is
   published. An adjudication without an argument is refused by the loader.
3. **The headline is the number that needs no adjudication.** Report both:

```
CODE MUTATION, per module
  G  generated
  I  incompetent   (does not import / syntax-invalid)     — excluded, counted, listed
  T  timed out     (indistinguishable from a hang)        — excluded, counted, LISTED BY ID
  V  viable = G − I − T
  K  killed
  E  adjudicated equivalent, each with a published argument

  FLOOR   K/V        <- THE HEADLINE. Requires no equivalence judgment at all.
  ADJ     K/(V − E)  <- reported beside it, with E printed and every argument linked.
```

Always as **two integers plus the four census terms**, never as a naive percentage — the same rule as
`KR = K/O` with `U/G`. The floor `K/V` is to code mutation what `K/O` is to data mutation: the number that
is a measurement rather than a theorem. If `E` is doing heavy lifting, the gap between `FLOOR` and `ADJ`
makes it visible, which is the point.

4. `T` (timeouts) are **listed by mutant id**, never silently dropped. A timeout can hide an infinite loop
   the tests would have caught.

### 3.5 Module tiers and per-phase thresholds

| Tier | Modules | Threshold on **`K/V`** | Blocking from |
|---|---|---:|---|
| **V — verdict-critical** | `evaluate/`, `verdict/`, `schema/styles_mask*.py`, `selfcheck/`, `facts/units.py`, `predicates/ast_walker.py` | **≥ 0.90** | the phase that first ships the module |
| **Q — qualification** | `qualify/`, `predicates/registry.py`, `predicates/host_fns/` | **≥ 0.85** | the phase that first ships the module |
| **I — ingest & schema** | `ingest/`, `schema/` (rest) | **≥ 0.80** | one phase after first ship |
| **S — support** | `report/`, `attest/render`, `cli.py`, `measure/` | **≥ 0.70** | two phases after first ship, then blocking forever |

**Rules that keep the threshold honest**, and they are the same rules the project applies to its own
pre-registered criteria:
- A threshold may be **lowered** only by an argument that the old one was wrong, recorded with its date in
  `docs/MUTATION-THRESHOLDS.md`. Never by the discovery that it cannot be met.
- **The negative-control tests are inside the scored suite.** Mutation testing that excluded them would be
  measuring the wrong suite.
- **The phase gate reports the score with the equivalent-mutant caveat attached**, in this exact form:
  `evaluate/: K/V = 118/127 (floor) · K/(V−E) = 118/121 with E = 6 adjudicated, arguments in
  reports/mutation/evaluate.ledger.jsonl · I = 3, T = 1 (ids listed)`. **A phase gate quoting a bare
  percentage fails its own review.**

### 3.6 Cost and scheduling

Full-repo mutation is minutes-to-an-hour, so: **PR runs Tier V only, and only for modules the diff
touches** (`mutmut run --paths-to-mutate $(git diff --name-only origin/main)` filtered to Tier V), target
under 5 minutes, **blocking**. The full sweep runs nightly, target under 60 minutes, **advisory except for
Tier V**, whose nightly regression opens a blocking issue on the next PR.

---

## §4 — THE DEFINITION OF DONE

`docs/DOD-TEMPLATE.md`. One filled copy per **build** (not per phase), pasted into the PR description.
Every line names an artifact path or a command whose output a reviewer can read **without having done the
work**. An unchecked line with no written reason blocks the merge.

```markdown
# DEFINITION OF DONE — Phase <P>, Build <P.n> "<name>"

## A. Scope and interface
- [ ] A1  Files created/changed, exhaustively: <paths>
- [ ] A2  Public interface, verbatim: <signatures | CLI usage | endpoint + request/response>
- [ ] A3  Data produced, with its path and its schema: <paths>
- [ ] A4  Nothing on the do-not-build list (spec §IV.3) was built. If it was, name the row and the argument.

## B. Functionality validation — the test set
- [ ] B1  Unit tests, named, each with what it asserts:            <file::test list>
- [ ] B2  Property tests: the PROPERTY stated in one sentence, and the GENERATOR named. If no property
          exists, say so and say why:                              <file::test list | "none, because ...">
- [ ] B3  Golden tests: WHICH workbook, and WHY that one:          <file::test list + justification>
- [ ] B4  Differential: which two implementations, and what happens on disagreement:  <D1|D2|D3|D4>
- [ ] B5  Determinism: the command run, and the varied dimensions (TZ, hash seed, locale, cwd, machine)
- [ ] B6  Contract/schema tests:                                   <file::test list>
- [ ] B7  Relational tests + the non-degeneracy precondition for each: <file::test list | "n/a because ...">
- [ ] B8  End-to-end flow exercised:                               <E2E-* id>

## C. Negative controls — BLOCKING, no exceptions
- [ ] C1  Catalogue entries added to tests/negative/catalogue.yaml: <NC-ids>, each inside this document's
          allocated block (§2's id space); `ci/catalogue-ids.sh` green
- [ ] C2  For each: the BREAK in one sentence, the INJECTOR path, the GUARD tests **with their `flips:`
          values** — at least one `flips: true`, and every positive control `flips: false`
- [ ] C3  `make nc-sweep` output pasted, ALL FOUR INTEGERS: entries_caught = <k> of <n> active ·
          guards_flipped = <g> of <e> expected · <m> injector:NONE · <p> PROVISIONAL
- [ ] C4  Each new guard was OBSERVED RED (or, for `flips: false`, OBSERVED GREEN) under its injector.
          **Evidence is a path, not a paste:** `reports/negative-control-sweep.json` rows for <NC-ids> at
          commit <sha>, whose `assertion_text` and `node_id` fields are non-empty for every flipped guard
- [ ] C5  Every rejection-side control has an admission-side POSITIVE control (the reject-everything trap).
          If the twin is not yet buildable, the entry is PROVISIONAL and names the phase that closes it
- [ ] C6  Where a negative control is impossible: the NC-N id, the why_impossible text, WHAT IT COSTS, and
          **the substitute measurement** — "impossible" without a substitute is a skipped line

## D. Measurement — the phase must emit a number that did not exist before
- [ ] D1  The number:                       <value>
- [ ] D2  Its denominator:                  <value, and where the denominator came from>
- [ ] D3  Its warrant label:                MEASURED | VERIFIED-AT-SOURCE | DERIVED | MODELED | SECONDARY
- [ ] D4  The script that produced it, and the command to re-run it:   <path + command>
- [ ] D5  Appended to reports/validation-ledger.jsonl (one row)         <row pasted>
- [ ] D6  If it is a count, at least one VALUE assertion accompanies it (rule R-GOLD-2)
- [ ] D7  If it is a rate: corpus_id, corpus_provenance, n, and a Wilson interval. No bare percentage.
- [ ] D8  If corpus_provenance is SELF-AUTHORED, **or the corpus generator's import closure intersects the
          predicate's evaluation closure**: it renders as "uninformative", not as a number (§6.3 item 6).
- [ ] D9  Its measurement class (§0.5):  REACH | DISCRIMINATION | CENSUS — and the `caveat` sentence is
          the one that class licenses. A REACH row carries its admission state and no verb of verification.
- [ ] D10 Every integer literal this build added to `tests/golden/` traces to §0.3 or to a ledger row
          (R-GOLD-3); `ci/golden-literals-are-traceable.sh` green.

## E. Mutation score of the tests over the code they claim to cover
- [ ] E1  Tier and threshold:               <V|Q|I|S> / <threshold>
- [ ] E2  K/V (floor):                      <K>/<V>
- [ ] E3  K/(V−E) with E:                   <K>/<V−E>, E = <n>, arguments at <ledger path>
- [ ] E4  I and T, with T's mutant ids listed
- [ ] E5  Every survivor triaged KILLED-LATE | EQUIVALENT (with argument) | SURVIVOR (with tracking id)

## F. Performance
- [ ] F1  Budget id and measured value:     <PERF-*> = <value> against baseline <value> on <machine>
- [ ] F2  If a budget moved: the entry in perf/BUDGET-CHANGES.md

## G. Design commitments (greps and structural gates)
- [ ] G1  ci/no-green-tick.sh              pass          - [ ] G5  ci/no-regex-over-xml.sh    pass
- [ ] G2  ci/no-float-money.sh             pass          - [ ] G6  ci/no-bare-except.sh       pass
- [ ] G3  ci/no-bare-absence.sh            pass          - [ ] G7  ci/licence-gate.sh         pass
- [ ] G4  test_no_model_in_verdict_path    pass          - [ ] G8  test_attestation_has_no_status_field  pass
- [ ] G9  ci/golden-literals-are-traceable.sh  pass      - [ ] G11 ci/no-clock-in-core.sh     pass
- [ ] G10 ci/catalogue-ids.sh              pass          - [ ] G12 ci/no-libreoffice-online.sh pass

## H. Honesty ledger
- [ ] H1  What this build does NOT establish, in the author's own words: <prose>
- [ ] H2  Any number in the build's output that must never be quoted without a qualifier, and the qualifier
- [ ] H3  Any spec claim this build moves from SPECIFIED to BUILT — say which, exactly
- [ ] H4  Any claim this build WEAKENS or withdraws, and why (a withdrawal is a result, not a failure)

## I. Exit gate
- [ ] I1  The phase's boolean exit gate, restated, and evaluated: <TRUE|FALSE> because <evidence>
```

**Reviewer's rule:** any line whose evidence is a claim rather than a path or a pasted command output is
not done. **C4 is the load-bearing line** — an engineer who cannot show the assertion that went red has
not built a negative control, they have written a second test.

**And C4 is the line this document most nearly failed its own standard on.** As originally written it was a
*pasted prose line in a PR description*: nothing re-derived it, and a reviewer who did not do the work could
not distinguish a real paste from a plausible one — which is not the standard this section sets for every
other line (*"an artifact path or a command whose output a reviewer can read without having done the
work"*). The repair is not more discipline; it is that **the sweep already produces the evidence and now
persists it.** `tools/nc_sweep.py` writes, per entry per guard, `{node_id, flips_expected, flips_observed,
assertion_text, commit}` into `reports/negative-control-sweep.json`, and
**`test_sweep__records_the_failing_assertion_text`** asserts `assertion_text` is non-empty for every guard
that flipped. C4 then cites the row, and a reviewer resolves it. **The load-bearing line is now the one
line in the DoD a reviewer can check mechanically.**

---

## §5 — THE CI PIPELINE

### 5.1 Principles

- **Free before cheap before expensive**, the same discipline as the G0→G4 gate order. A gate that costs
  five seconds and rejects a class the expensive gates cannot see runs first.
- **Advisory is temporary and dated.** Every advisory gate carries the phase at which it becomes blocking,
  in `ci/GATES.md`. There are no permanent advisories.
- **The pipeline is the phase gate.** A phase's exit gate is evaluated by reading `reports/` after a green
  run, not by reading a diff.
- **R-DENOM-1 — a gate of the form `k of n` where we also write `n` requires `n` to be append-only with a
  growth log.** Every such registry — `tests/negative/catalogue.yaml`, `ci/GATES.md`'s row set,
  `labels.SURFACES`, `labels.REQUIRED_NUMBERS`, `docs/README-NUMBERS.md`, `docs/TERMS-OF-USE.md`,
  `labels.SCAN_ROOTS` — **publishes its cardinality as a time series**, and a removal requires a dated
  argument in `docs/GATE-CHANGES.md` beside the measurement that quotes it. **Every gate in this plan whose
  form is `k of n` and whose `n` we maintain is one refactor away from being `n of n`**: the thing that
  cannot pass the gate gets deleted from the denominator and the gate goes green. The plan mechanises this
  discipline beautifully for `docs/HARVEST-DELTA.md` and applies it nowhere else; R-DENOM-1 applies it
  everywhere, and `test_registry__append_only[<registry>]` is parametrised over the list above.

### 5.2 The licence gate, and its real negative control

`ci/licence-gate.sh` resolves the installed dependency set and compares against `docs/LICENCES.md`, which
carries per dependency: `{name, version, licence, warrant, opened_by, opened_at}`. Rules:

- A dependency with **licence `NOT-FOUND`** fails the build.
- A **runtime** dependency whose warrant is `SECONDARY` is advisory in Phase 0–1 and **blocking from
  Phase 2**, with `docs/LICENCES.md` naming who must open it. The outstanding list today is: **gVisor
  (NOT-FOUND)**, **Z3 (MIT, SECONDARY)**, **Hypothesis (reported MPL-2.0, not opened)**, **cosign
  (Apache-2.0, SECONDARY)**, **`cobalt`/`indigo` (NOASSERTION)**, **`xbrl.us/dqc-license`**, and
  **IFSCA's terms of use for the register API** — the last being a gap in conduct rather than code, and
  it must be read before any scheduled polling.
- The denylist is hard: **`bluebell` (GPL-3.0, VERIFIED)**, **`pycel` (GPL-3.0)**, **`formulas`
  (EUPL 1.1+)**, **Soda Core (Elastic 2.0 — "You may not provide the software to third parties as a hosted
  or managed service", VERIFIED-AT-SOURCE, and our product *is* that)**, **TorchCP (LGPL-3.0)**,
  **CheckCell/DataDebug (GPL-2.0)**.

**The negative control is on disk right now and requires no injection.** `/Users/abishaikc/Gift/.venv`
currently contains **`formulas` 1.3.4 (EUPL 1.1+)** and **`pycel` 1.0b30 (GPL-3.0)** — both on the
denylist. `tests/negative/test_nc_licence.py::test_nc__L01_gate_fails_against_the_research_venv` runs the
gate against that interpreter and asserts a non-zero exit naming both packages. If someone later cleans the
venv, the test switches to a recorded fixture of its `site-packages` listing, and the fixture is committed
so the control survives the cleanup.

### 5.3 The stages, in order

| # | Stage | Command | Blocking | Wall clock | Fails on |
|---:|---|---|:--:|---:|---|
| 0 | Lint, format, types | `make lint` — ruff (MIT, SECONDARY) + mypy (MIT, SECONDARY) `--strict` on `src/cdfc/` | **yes** | 20 s | any diagnostic |
| 1 | **Licence gate** | `make licence` → `ci/licence-gate.sh` | **yes** | 10 s | denylist hit; `NOT-FOUND`; from Phase 2, a `SECONDARY` runtime dep |
| 2 | **Design-commitment greps** | `make greps` → `ci/no-green-tick.sh`, `no-regex-over-xml.sh`, `no-bare-except.sh`, `no-float-money.sh`, `no-bare-absence.sh`, `no-libreoffice-online.sh`, `golden-asserts-values.sh`, **`golden-literals-are-traceable.sh`**, **`catalogue-ids.sh`**, **`no-clock-in-core.sh`** — plus the four `07` §0.4(d) adds | **yes** | 20 s | any hit |
| 3 | **Contract & schema** | `make contract` → `pytest tests/contract -q` | **yes** | 12 s | enum cardinality drift; a `status`/`result`/`pass` property at any depth; evaluator ≠ `EVALUATION-CONTRACT.md` |
| 4 | Unit + census | `make unit` → `pytest tests/unit tests/test_suite_census.py -q` | **yes** | 35 s | any failure; **a fall in the collected-test count without a recorded reason** |
| 5 | Property + relational (fast) | `make property` → `pytest tests/property tests/relational -q` (`HYPOTHESIS_PROFILE=fast`) | **yes** | 70 s | any falsifying example |
| 6 | **Golden, nine workbooks** | `make golden` → `pytest tests/golden -q` | **yes** | 45 s | `test_schema_constants` drift (a parser regression); `test_harvest_count` drift **without** a `HARVEST-DELTA.md` entry |
| 7 | Differential | `make differential` → `pytest tests/differential -q` (D1–D3) | **yes** (D4 nightly, advisory) | 90 s | reader disagreement not escalated; evaluator ≠ cached values; **`_xlfn.AGGREGATE` positive control not passing** |
| 8 | **Negative-control sweep** | `make nc-sweep` → `pytest tests/negative -q` then the sweep | **yes** | 6 min | **any `flips: true` guard that stays green, or any `flips: false` guard that goes red** — the exact set, not "at least one"; a colliding id; an orphan guard; a guard with no `flips` value; an entry with `injector: NONE` and no `why_impossible`; a `PROVISIONAL` entry naming no closing phase; **`assertion_text` empty on a flipped guard** |
| 9 | Determinism + `verify` | `make determinism` then `cdfc verify` on the **second runner image** | **yes** | 2 min | any byte difference |
| 10 | Performance | `make perf` → `pytest tests/perf --benchmark-compare-fail=mean:20%` against `perf/baseline.ci.json` | **yes** above +20%, warn above +10% | 70 s | budget blown |
| 11 | **Mutation (Tier V, diff-scoped)** | `make mutation-pr` | **yes** for Tier V modules the diff touches | 5 min | `K/V` below tier threshold; a survivor with no triage |
| 12 | End-to-end, offline | `make e2e` — clean clone, network namespace closed | **yes** | 2 min | `make demo` not reproducing a README number; report not opening from `file://`; `E2E-INVALID` returning a fraction |
| 13 | Nightly: deep property (1000), full mutation, D4 LibreOffice, transfer sweep over the nine, instrument-watcher diff | `make nightly` | advisory, except Tier V mutation regression which opens a blocking issue | ≤ 90 min | — |

**PR budget: under 12 minutes.** Stages 0–3 fail in under a minute, which is the point of the ordering.

**The wall-clock column is a budget, and a budget that drifts silently is not one.** Each stage's figure is
the sum over that stage's rows in `ci/GATES.md`, and **`test_ci__stage_clocks_match_gates_md`** asserts the
table above and `ci/GATES.md` agree, row for row. A stage whose clock moves requires an appended, dated
reason in `ci/GATES.md` — the same discipline as `perf/BUDGET-CHANGES.md`. Stage 2's movement from the P0
baseline of 8 s to 20 s is the first such entry and covers both the three gates added by §5.4's repairs
below and the four added by `07` §0.4(d).

### 5.4 The greps, exactly

Each is short, each mechanises a commitment the spec makes into a system property, and each has a planted
negative control in `tests/negative/test_nc_ci.py` asserting the script exits non-zero when the thing it
forbids is present.

| Script | Scans | Forbids | Planted control |
|---|---|---|---|
| `ci/no-green-tick.sh` | **`cdfc.surface.labels.SCAN_ROOTS`** — never a directory literal. `("src/cdfc",)` at P0; `07` P14 extends it | `✓ ✔ ✅ 🟢 ✔️ 👍` and `all clear / no issues / looks good / verified clean / compliant / passed all / fully checked` (read from `labels.BANNED_GLYPHS`/`BANNED_PHRASES`, so gate and renderer cannot disagree) | `injectors/plant_glyph.py`, **plus** `test_nc__A02b` (the scan set covers every rendered surface) **and `test_nc__CI01c_scan_root_list_is_not_a_literal`** |
| `ci/no-regex-over-xml.sh` | `src/cdfc/ingest/ src/cdfc/schema/` | `re.compile(r?["']<`, `findall(r?["']<`, `search(r?["']<` | `injectors/formula_regex.py` |
| `ci/no-bare-except.sh` | `src/cdfc/{evaluate,verdict,selfcheck,probes}/` | bare `except:`; `except Exception:` without a `raise` in the handler | `injectors/evaluate_swallow.py` |
| `ci/no-float-money.sh` | `src/cdfc/{facts,evaluate,verdict}/` | `float(`, `import math`, `/` applied to a money-typed symbol | `injectors/float_money.py` |
| `ci/no-bare-absence.sh` | `src/ tests/ docs/` | `does not occur`, `zero hits`, `not present in`, `no occurrences` on a line carrying no **resolvable** `ledger:<row_id>` whose row has `positive_control_count > 0` | `test_nc__X02c` — both halves: the four-word "positive control" phrase, and a cited row whose control count is zero |
| `ci/no-libreoffice-online.sh` | the online packages | `soffice`, `libreoffice`, `subprocess` | `injectors/soffice_online.py` |
| `ci/golden-asserts-values.sh` | `tests/golden/` | a test function containing a count assertion and **no** value assertion (rule R-GOLD-2) | a count-only golden |
| **`ci/golden-literals-are-traceable.sh`** | `tests/golden/` | an integer literal in a comparison that resolves to neither §0.3's fixture table nor a `reports/validation-ledger.jsonl` row (rule R-GOLD-3) | a golden pinning an untraceable literal — the live instance is `07` P14-B1's `2,373`/`1,374` |
| **`ci/catalogue-ids.sh`** | `plan/*.md`, `tests/negative/catalogue.yaml` | an `NC-` id defined in more than one document, or defined outside that document's block in §2's id table | a second document defining `NC-E11` — the collision this pass found, replayed as a planted control |
| **`ci/no-clock-in-core.sh`** | `src/cdfc/{evaluate,verdict,selfcheck,probes,attest}/` | `datetime.now()`, `time.time()`, `TZ`, **`perf_counter`, `monotonic`, `process_time`** | `injectors/duration_in_hashed_payload.py`, and `injectors/now_in_renderer.py` |
| `ci/licence-gate.sh` | the resolved dependency set | the denylist; `NOT-FOUND`; `SECONDARY` runtime deps from Phase 2 | **the live `formulas`/`pycel` install** |

**One scan set, from P0, and the reason is that the honesty gate was the first thing scope truncation was
going to reach.** `ci/no-green-tick.sh`'s roots were written here as `src/ templates/ locales/ static/`;
P0-B1 creates `src/cdfc/**` and no top-level `templates/`, `locales/` or `static/`, and `02` §1 R5 makes a
**missing scan root a non-zero exit**. So the gate would have failed from the first commit and been "fixed"
the only cheap way — by narrowing the scan set to `src/` — which is **NC-D01's mechanism applied to the
honesty gate itself, on day one, in the phase that exists to prevent it.** Meanwhile `07` P14 SG1 derived a
*third* scan set from `render.TEMPLATE_DIR`. The repair is one source of truth:
`cdfc.surface.labels.SCAN_ROOTS`, a stub containing `("src/cdfc",)` at P0 that `07` P14 extends, read by
the script, by SG1 and by SG4. `test_nc__CI01c_scan_root_list_is_not_a_literal` asserts the script contains
no directory literal. **The narrowing from four names to the real tree is recorded in `ci/GATES.md` with its
reason and its date — a scan set that shrinks silently is the defect; a scan set that shrinks with a diff
is housekeeping.**

Plus the three structural gates that are Python rather than grep, because grep cannot express them:
`test_no_model_in_verdict_path` (import closure + blocked socket, §2.6 NC-A04),
`test_attestation_has_no_status_field` (recursive schema walk, §2.6 NC-A01),
`test_nc__D02d_mutating_path_A_moves_only_path_A` (denominator independence, §2.2 NC-D02).

### 5.5 The validation ledger

Every phase must emit at least one number that did not exist before. Mechanised:
`reports/validation-ledger.jsonl`, append-only, one row per measurement:

```json
{"row_id":"P3.2-kill_rate.fme.f11","phase":"P3","build":"P3.2","metric":"kill_rate.fme.f11",
 "numerator":41,"denominator":44,
 "denominator_source":"observable mutants after recalculation filter","warrant":"MEASURED",
 "measures":"DISCRIMINATION",
 "positive_control_count":null,
 "produced_by":"src/cdfc/qualify/g2_kill.py","command":"cdfc seed --template 7d9a1960 --fault-model v3",
 "caveat":"licenses one sentence: rejects 41 of 44 observable defects seeded under fault model v3",
 "date":"2026-__-__"}
```

`tests/test_validation_ledger.py` asserts: every row has all **twelve** fields; `row_id` is unique and is
the string `ci/no-bare-absence.sh` resolves; `warrant` is from the closed set; **`measures` is from the
closed set of three (§0.5)**; a rate row carries `corpus_provenance` and `n`; an **absence** row carries
`positive_control_count > 0` (written by `measure/absence.py::assert_absent`, never by hand); `numerator`
and `denominator` are integers, so a placeholder row cannot be committed as a real one; **and the ledger
grew by ≥ 1 row since the previous phase tag** — a phase that produced no new number has not met the
standard. Plus `test_ledger__reach_rows_carry_no_quality_claim` (§0.5).

---

## §6 — THE TEST-DATA STRATEGY

### 6.1 What exists

- **The nine prescribed workbooks**, at
  `/Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/*.xlsx`. **Action: copy byte-for-byte into
  `fixtures/prescribed/`** with `MANIFEST.json` recording `{filename, sha256, bytes, origin_uri,
  retrieved_at}` — the hashes are in §0.3 and `tests/golden/test_fixture_integrity.py` asserts them on
  every run. A fixture that drifts is caught the same way a filing that drifts is caught.
- **The working harnesses**: `research/scripts/{wb_probe.py, predicate_harvest.py, l4_mutation_harness.py,
  true_coverage.py, verify_brief_43.py}` and their outputs `predicates.json` (515 predicates across the
  nine) and `l4_result.json` (19,782 mutants, 3,574 killed, 22 equivalent, MS 18.09%). **These become
  frozen baselines at `fixtures/baselines/harvest-v0.json` and `fixtures/baselines/l4-v0.json`**, with a
  `README` recording that v0 of the harness had two known defects (site-set sampled from the read set;
  equivalents excluded from both terms) and that both are now negative controls NC-Q06 and NC-Q05. **The
  baseline is kept because it is the evidence, not because it is right.**
- **The superseded probe script** that reports `xsheet=0` on all ten sheets: **delete it, do not patch
  around it.** A wrong script sitting beside a corrected one with nothing marking which is authoritative is
  how a wrong number gets quoted. `tests/test_suite_census.py::test_no_superseded_probes` asserts it is
  gone.

### 6.2 What must be created

| Directory | Contents | Notes |
|---|---|---|
| `fixtures/adversarial/` | `zipbomb-entrycount__x100000.xlsx`, `zipbomb-ratio__x1000.xlsx`, `zipbomb-entrysize__1gb.xlsx`, `xxe-entity__passwd.xlsx`, `not-a-zip__renamed.xlsx`, `missing-part__no-workbook.xlsx`, `oversized__over-cap.xlsx` | Generated by `tools/fixtures/make_adversarial.py`, deterministic from a seed; **never opened by a normal test run**, only by NC-P05 |
| `fixtures/synthetic/` | `renamed-sheet__portfolio.xlsx`, `row-inserted__portfolio-r7.xlsx`, `formula-overwritten__portfolio-O7.xlsx` (the `TEMPLATE_DIFF` flagship), `unprotected__derived-from-fme.xlsx` | Built by **raw-zip surgery** — copy every part byte-for-byte, rewrite one worksheet XML. MEASURED: one part differs, the 3.55 MB data model and all 19 `x14` validations survive byte-identical. **Never openpyxl round-trip** |
| `fixtures/predicates/broken/` | `P-NC01__zero-bind.yaml`, `P-NC02__no-qualification.yaml`, `P-NC04a__reads-undeclared.yaml`, `P-NC04b__declares-unread.yaml`, `P-NC11a__undeclared-proviso.yaml`, `P-NC11b__quote-not-verbatim.yaml`, `P-NC07a__trivially-true.yaml`, `P-NC07b__always-flag.yaml` | Hand-written envelopes, each named in the catalogue |
| `fixtures/predicates/good/` | The admission-side positive controls: FME's 19 real `≥ 0` bounds, one membership predicate, one `TEMPLATE_DIFF` | **Without these the gate is indistinguishable from reject-everything** |
| `fixtures/mutants/` | **Not committed except** the `kill_case`/`pass_case` referenced by an admitted predicate, which are content-addressed and required for F10 replay | Everything else is regenerated deterministically from `{seed, fault_model_version, harness_version}` |
| `corpus/` | The blind-fill corpus (§6.3) | **A separate repository.** Referenced from the main repo only by `fixtures/corpus_manifest.json` |

### 6.3 The blind-fill corpus, produced without contaminating it

`BLIND-FILLED` is **the minimum bar below which no FFR may be printed anywhere in the product**. The
firewall is procedural, so it is mechanised wherever a procedure leaves a trace:

1. **Two repositories, and the firewall's two halves run in two CIs.** `corpus/` is its own git
   repository. The main repo references it by `{repo_url, commit_sha, manifest_sha256,
   contamination_scan_sha256}` in `fixtures/corpus_manifest.json`.
   `tests/test_corpus_firewall.py::test_corpus_is_not_importable` asserts nothing under `tests/` or
   `src/` reads `corpus/` except through that manifest — **and that assertion requires the corpus tree to
   be absent from the working directory.** The contamination check asserts the opposite: it *greps the
   corpus repo's tree* for any predicate id, CEL fragment or gate output string, which requires the corpus
   tree to be present. **The two cannot both hold in one CI job, and as written they were both specified in
   the main repo's.** Ruling: **the contamination grep runs in the corpus repository's own CI, over its own
   tree, and publishes a signed result whose hash enters `fixtures/corpus_manifest.json`; the main repo
   asserts the hash and never checks the corpus out.** `test_corpus__contamination_scan_hash_is_fresh`
   asserts the scan's commit is the manifest's `commit_sha`. This also removes the standing temptation to
   check the corpus out beside the predicate set, **which is the contamination the firewall exists to
   stop** — a firewall whose own test requires the wall to be down is not a firewall.
2. **What Person A receives**: the blank template, the regulation PDF, and the fill brief. **What Person A
   never receives**: `src/cdfc/predicates/`, `predicates.json`, any report, any list of checks, and any
   member of this document.
3. **The fill brief is hashed and published before the first workbook is filled.**
   `corpus/FILL-BRIEF.md`; its sha256 is recorded in the main repo's README and in
   `fixtures/corpus_manifest.json`. `test_corpus__brief_hash_matches` asserts the recorded hash equals the
   file, and `test_corpus__brief_predates_first_workbook` asserts, from the corpus repo's commit
   timestamps, that the brief commit is an ancestor of the first workbook commit. **A commitment made
   after seeing the result is not a commitment**, and here the git history is the evidence.
4. **If the fallback fires** (no human Person A; the decided fallback is an audited second-model-instance),
   the fill prompt is hashed and published **before** the first workbook, `corpus_provenance` remains
   `BLIND-FILLED` **only if** the instance was never shown the predicate set, and the record carries
   `person_a_kind: "model-instance"` — which renders wherever the FFR renders. **The fallback is weaker
   than a human and the record says so.**
5. **The contamination probe, and its weakness stated.** After the fact,
   `tools/corpus/contamination_probe.py` compares the value-distribution entropy of cells the predicate
   set reads against cells it does not, across A's workbooks, and reports the difference with a
   permutation p-value. **This is advisory and weak**: it can detect a gross correlation, it cannot detect
   a subtle one, and a null result is not evidence of blindness. It exists so that a gross contamination is
   not invisible, and it is labelled `ADVISORY — cannot establish blindness` in its own output.
6. **Every FFR record carries** `corpus_id`, `corpus_provenance`, `n`,
   `clean_corpus_independent_of_predicate`, the Wilson interval, and the held-out slice.
   **`clean_corpus_independent_of_predicate` is DERIVED, never declared** — it is a property computed at
   G4 time, not a constructor argument and not a string in a YAML file:

   ```
   independent := (corpus.generator_import_closure ∩ predicate.evaluation_import_closure == ∅)
                  and (read_keys(predicate) ∩ corpus.computed_cells == ∅)
                  and corpus.provenance != SELF-AUTHORED
   ```

   `g4_ffr.check()` **raises `UninformativeCorpusError`** when it is false — the same exception, the same
   fail-closed shape, in the same function as the `SELF-AUTHORED` refusal, so there is no second code path
   to forget. `test_nc__Q25_independence_is_computed_not_declared` asserts the field cannot be hand-set,
   with `injectors/independence_hardcoded.py` as its break.

   **Why this was the plan's most expensive one-line defect.** Every admitted predicate was to carry
   `clean_corpus_independent_of_predicate: true`, and **no build computed it, no test asserted it, no
   negative control broke it and no gate read it.** It is the field that catches a clean corpus generated
   by the code under test — a corpus whose *inputs* are filled and whose *derived cells are computed by the
   same evaluator the arithmetic predicates re-check*. On such a corpus an arithmetic predicate's expected
   false-failure rate is **zero regardless of its quality**, which is this document's own definition of an
   uninformative rate; and because the generator is deterministic from a seed, `n ≥ 189` — the Wilson
   threshold for `BLOCKING` — costs one command. **A severity tier could have been bought in an afternoon
   from a corpus the product generated about itself.** The narrow residual licence is stated narrowly: such
   a corpus remains admissible for predicates that read **only input cells** (membership, bounds, dates,
   `conditional_required`), and `test_nc__Q24b_template_computed_licenses_a_membership_ffr` is the
   admission-side twin that stops this from being reject-everything.
7. **The exchangeable unit is the FILING.** `n = F`, never `n = 3,755 · F`. Asserted by
   `test_nc__Q08d_n_is_filings_not_cells`.
8. **The corpus is also the only external instrument that can falsify the denominator, and it must be used
   as one.** The field surface (3,747 on FME) is produced by two code paths implementing **one rule we
   wrote**, before either path was coded. NC-D02c/d prove the paths are two implementations rather than one
   called twice; NC-D05 proves one specific misreading is caught; **nothing can falsify the rule itself**,
   and every fraction the product will ever print is a fraction of that number. The first external artifact
   that could falsify it arrives here: **the set of cells Person A actually wrote into** is a direct,
   independent measurement of *"the cells a filer may fill"* — the exact thing the protection mask is a
   proxy for. `corpus_manifest.json` therefore records `cells_written[]` per workbook (not only
   `cells_left_blank[]`), and **`test_mask_matches_what_a_competent_filler_filled`** publishes two
   integers, denominator 3,747, warrant MEASURED:
   - **cells written that lie OUTSIDE the mask** — the mask is too small, and this is the dangerous
     direction: it would make every settled fraction an *overstatement* of coverage;
   - **cells inside the mask that no filler in the corpus ever wrote** — the mask is too large, which
     understates it.

   It costs one script over data the corpus lane already produces, and it is the only instrument in this
   methodology that could falsify the number underneath every other number. Neither integer is a pass/fail
   on its own; a non-zero first integer is a **finding** and opens a `docs/GATE-CHANGES.md` row against the
   protection-resolution rule. Until it runs, every settled fraction renders `denominator.generator_rule`
   beside it (`07` P14's `REQUIRED_NUMBERS`).

### 6.4 Labelling synthetic data so it can never be quoted as real

Three layers, because a sidecar file gets lost and a filename gets renamed:

1. **A sidecar**: `<name>.prov.json` = `{corpus_provenance, generator, generator_version, seed,
   created_at, may_be_quoted_as}`, where `may_be_quoted_as` is a **sentence**, e.g.
   *"rejects N of M observable defects seeded under fault model v3 — not a measurement of real filings."*
2. **Inside the file**: every generated `.xlsx` carries a custom document property in
   `/docProps/custom.xml`: `CDFC_SYNTHETIC = true` and `CDFC_PROVENANCE = <corpus_provenance>`.
   **The label travels inside the artifact and survives copying, emailing and renaming.**
   `test_data__every_synthetic_artifact_is_labelled` asserts it for every file under `fixtures/synthetic/`
   and every generated mutant.
3. **In the renderer**: `report/render.py` refuses to print a rate whose corpus contains any file carrying
   `CDFC_SYNTHETIC = true` unless the rendered string contains the word `synthetic`.
   `test_nc__Q08e_synthetic_rate_carries_the_word` is the negative control; the injector removes the check.

The harness already prints its caveat by construction (`l4_mutation_harness.py` prints *"this clean corpus
is SYNTHETIC. No false-failure rate quoted from it is a measurement of real filings"*); this makes it a
schema property rather than a print statement.

### 6.5 The fixture naming scheme

```
<class>__<source-or-defect>__<variant>__<seed-or-sha8>.<ext>
```

`class ∈ {clean, mutant, adversarial, broken, prescribed, synthetic}`.
**The corpus-provenance token appears in the filename of every corpus member**, so a screenshot of a
directory listing carries the provenance — the same principle as the verdict state name that cannot be
quoted without its own qualifier.

Examples:
`clean__template-computed__fme-q1__a41c9d3f.xlsx` ·
`clean__blind-filled__fme-017__7c1e0b22.xlsx` ·
`mutant__f11-formula-override__portfolio-O7__seed20260810.xlsx` ·
`adversarial__zipbomb-ratio__x1000.xlsx` ·
`broken__reader-nsblind__v1.py` ·
`prescribed__ifsca-fme__02012026__7d9a1960.xlsx`.

`tests/test_fixture_naming.py` asserts every file under `fixtures/` matches the grammar and that its
`class` token agrees with its directory and with its `CDFC_PROVENANCE` property.

---

## §7 — WHAT THIS METHODOLOGY CANNOT ESTABLISH

The project's own standard demands the residue be declared. These are classes of defect that survive this
entire regime — every gate green, every negative control caught, mutation score at threshold.

**7.1 A predicate that is perfectly implemented and encodes the wrong obligation.** G0 proves the quote
locates deterministically and every proviso is implemented or declared. Nothing here proves the CEL
*means* what the clause means. The only published study of statute→executable-model generation reaches
51–53% outcome equivalence, and its own caveat is that structural similarity does not guarantee outcome
equivalence or the reverse. **A predicate can clear all five gates and enforce a rule that does not
exist.** No test in this document addresses it; only human review at R7 and the attrition funnel do, and
neither is a measurement of correctness.

**7.2 Any defect the fault model does not contain.** `KR = 0.82` licenses exactly one sentence: *"rejects
82% of the N defects I seeded, under fault model v3, of which U were discarded as unobservable."* In code
mutation testing the bridge from seeded to real faults is the coupling effect. **There is no coupling
study for financial filing data.** The bridge does not exist and must not be walked across. Every kill
rate this methodology produces is a statement about our operator mix and nothing else.

**7.3 The coordinated misstatement — and this one is a theorem, not a gap.** A prescribed return is a
closed arithmetic system. A family of filings exists that is internally perfect under every relation the
regulator's template encodes and every relation we add, and materially false. In code mutation a mutant
that changes behaviour is in principle killable by *some* test; here a mutant can change the **truth** of
the artifact and be **provably unkillable by any predicate over the artifact alone.** The methodology's
only response is to measure the family's size (NC-C02) and exhibit a member.

**7.4 Deception.** Every check is a consistency check over a self-reported document. **A coherent liar
passes all of them.** No test class in §1 changes this, and the sentence stays on the report surface.

**7.5 A misconception shared by the two "independent" implementations.** Differential testing (D1, D2) is
defeated when both sides are wrong the same way — and this is not hypothetical: a hand-written regex and
openpyxl 3.1.5 reached the identical wrong 35 by the identical mechanism, in the same directory, on the
same day, undetected. Both of our readers will be written by people reading the same OOXML specification
with the same mental model. The extraction manifest's `constructs_not_understood` list is the only
mitigation, and **it lists only what we knew to look for.** NC-D02d raises the bar for the denominator
specifically — it distinguishes two implementations from one called twice — but it cannot distinguish two
implementations from two copies of the same misunderstanding.

**7.6 A break arriving by a mechanism nobody imagined.** The negative-control sweep proves each guard
fires when the code is broken *in the way we imagined breaking it*. **Its denominator is the catalogue,
and the catalogue is written by the same people who wrote the code.** This is a self-referential
denominator — precisely the error §2.2 NC-D02 exists to catch, applied to the methodology itself, and we
cannot escape it from the inside. The only available instrument is the catalogue's append-only growth log:
if new *mechanisms* (not new instances) keep being discovered late, the catalogue is incomplete and the
rate is visible. Report it; do not claim it converges.

**7.7 The recursion stops.** NC-C01b is the canary for the canary loop — a seeded dead predicate that must
be reported. **Nothing watches that.** If the seeding of the self-test predicate itself breaks, the run
goes green. One more layer would move the problem one layer, and we stop here deliberately and say so,
rather than adding a layer and implying the regress is closed.

**7.8 Equivalent-mutant adjudication is a judgment.** `E` in the code-mutation score is prose written by
the person whose tests are being scored. The `K/V` floor is the mitigation and is the headline for exactly
that reason, but `K/(V−E)` is reported beside it and a reader who quotes only the second has quoted a
number that contains an opinion.

**7.9 Property tests find what the generator generates.** At `max_examples = 50` over a small fixed space,
a property that holds on every generated input and fails on a real filing shape nobody thought to generate
is not caught. `@example` pinning of every real defect is required and closes only the past.

**7.10 Performance is measured at one scale, on one machine class.** A regression visible only at 100× —
the point at which blob storage (320 GB/yr) and SQLite's single writer break first — is invisible to
stage 10 by construction.

**7.11 There is no concurrency coverage at all, by construction.** The pipeline is single-process and
synchronous, so this methodology has nothing to say about the day a second concurrent writer exists —
which is the spec's own named trigger for Postgres. On that day, every determinism and closure guarantee
in this document must be re-derived, and none of these tests will notice that they no longer hold.

**7.12 The blind-fill corpus's blindness is procedural.** §6.3 mechanises everything that leaves a trace —
the pre-published brief hash, the commit-order test, the manifest firewall — and none of it establishes
that Person A never saw a predicate. Every `BLIND-FILLED` FFR in the product rests on that. It is the
single largest unverifiable input to the product's headline claim, and it is why `SELF-AUTHORED` renders
as the word `uninformative` rather than as a number: **we would rather print nothing than print a number
whose shape is evidence and whose content is zero.**

**7.13 And the boundary of the model-free claim.** `test_no_model_in_verdict_path` establishes that no
model is called *during a verdict*. It does **not** establish that the verdict is model-free: the
predicates were proposed by a model at build time, and the gate — not the test — is the boundary. Anyone
quoting "zero model calls" must quote it as *zero model calls on the verdict path per filing*, and never
as *no model influenced this verdict*.

---

## APPENDIX — THE ONE-PAGE VERSION, FOR THE ENGINEER STARTING A BUILD

1. Write the code and the tests. Then ask, for each test: **what specific broken build would make this go
   red?** If you cannot name one, the test is not evidence — go back.
2. Add the break to `tests/negative/catalogue.yaml` with an injector under
   `tests/negative/injectors/`, an id **inside your document's block** (§2), and a `flips: true|false` on
   **every** guard you name. Run `make nc-sweep`. **Cite the sweep report's row in the DoD's line C4** —
   not a paste, a path, and the row carries the assertion text the sweep captured. If your entry is
   `caught` while a guard you named never flipped, you have not tested that guard; say so with
   `flips: false` and say why. Nobody is going to take your word for any of it, and that is the design.
3. Every rejection-side control needs an admission-side positive control, or your gate is
   reject-everything and scores perfectly on the negative control alone.
4. Emit one number that did not exist before, with its denominator, its warrant label, **its measurement
   class (`REACH` / `DISCRIMINATION` / `CENSUS`, §0.5)** and the command to re-run it. Append it to
   `reports/validation-ledger.jsonl`. **If it is `REACH`, it is not a quality number and no surface may
   caption it with a verb of verification** — and no hero number is claimed until a false-failure rate
   exists.
5. Run `make mutation-pr`. Report `K/V` first — it needs no equivalence judgment — then `K/(V−E)` with `E`
   and its published arguments. **Never a bare percentage.**
6. Fill `docs/DOD-TEMPLATE.md`. If a line's evidence is a claim rather than a path or a pasted command
   output, it is not done.
7. In §H of the DoD, write what your build does **not** establish. A build that cannot name its own
   residue has not been understood by the person who built it.

---

## REPAIRS APPLIED (adversary pass)

Compiled against `plan/08-adversary.md`. One line per finding: the finding, the change, the location.
A reviewer should be able to check each row without re-deriving the finding.

### The four catalogue-id collisions, and the full old-to-new mapping

**F27 is repaired here and the other three document owners must apply the renames below.** The catalogue is
one file keyed by `id`; six documents allocated independently; a colliding id means the later document's
entry **silently replaces** the earlier one on load, after which the sweep still reports `caught == active`
and `test_nc_meta__no_orphan_guard` is still satisfied. One of the two `NC-E11` entries is the row
recording that G-EVAL arm 1 cannot fail.

> **THE MAPPING TABLE THAT STOOD HERE IS DELETED AND SUPERSEDED BY §2.3. Arbitration C9.**
>
> It was written from *its own parallel scheme* rather than from what the other documents actually did, and
> it was wrong in every place it mattered: it pointed `03`'s `Q12`–`Q16` at `Q50`–`Q54` while `03` had
> renumbered them to `Q40`–`Q44`; it assigned `NC-Q27` to `04`'s `Q22b` while `04` had already given it
> `NC-Q41`, closing **F17 under two different ids**; it let `07` keep `NC-N07` and told `02` to move, while
> `02` was writing that it keeps `NC-N07` and `07` moves; and it recorded `04`'s `NC-N11`/`NC-N12` as
> "unchanged" while `04` had renumbered them to `NC-N20`/`NC-N21`, straight into `05`'s block.
>
> **The tie-break rule that generated it is also deleted:** *"the document whose renumbering costs the
> fewest downstream edits keeps the id."* That rule is judgement, and judgement is what produced a mapping
> table nobody could apply. **C9 replaces it: where two documents define the same id with different
> content, BOTH get new ids and the contested id is retired permanently.** Nobody keeps a contested id, so
> nobody has to be judged the winner, and no stale reference can silently resolve to the wrong entry.
>
> **The complete old→new mapping and the RETIRED list are §2.2 and §2.3 of this document.** They are there
> and not here because §2 is the registry, and a mapping kept at a distance from the allocation it maps is
> the shape this defect keeps coming back in.

### Findings closed in this document

| Finding | Sev | In one line | What changed, and where |
|---|---|---|---|
| **F4** | FATAL | the sweep asserts "at least one guard fails", so an entry is caught by its weakest guard | §2 catalogue shape: `guard_tests` becomes a list of `{path, flips}`; `flips: false` on every guard is a schema error. §2.0 step 3 asserts the **exact set**. §2.0 output is four integers incl. **`guards_flipped / guards_expected_to_flip`**. New meta-test `test_nc_meta__every_expected_guard_flipped` supersedes `…every_injector_flips_its_guard` (retired, with a `CATALOGUE-CORRECTIONS.md` row). §5.3 stage 8's fail list rewritten. DoD C2/C3 |
| **F27** | SERIOUS (FATAL-class) | four id collisions across six documents; a colliding id silently drops a row. **The first repair made it worse: 5 colliding groups became 10, two of the new collisions created inside the fix, plus four mutually inconsistent band tables** | **CLOSED BY ARBITRATION C9.** §2 is rewritten as **THE CANONICAL `NC-` REGISTRY** — the *sole* place an id may be defined: **one** band table with a **reserved unallocated range per band** (§2.1); a **RETIRED list, permanent and never reassigned** (§2.2); the **complete old→new mapping** (§2.3); and four mechanised rules (§2.4). The four competing band tables in `02`, `04`, `05` and `07` are **deleted**, and this document's own parallel mapping table and reserved-id paragraph with them. Ten contested ids retired, **both** sides renumbered in every case. Meta-tests `test_nc_meta__ids_are_unique`, `test_nc_meta__ids_are_defined_in_the_registry`, `test_nc_meta__no_orphan_guard`, `test_nc_meta__no_dangling_reference`, all required **before the first entry**, at P0-B3; `ci/catalogue-ids.sh` gains the UTF-8 assertion. §5.4 gains the gate row | §2.1–§2.4 |
| **F13** | FATAL | nothing tests that the settled fraction cannot rise as a filing carries less information | §1.2's mandatory property table gains **`test_prop__fraction_does_not_rise_as_the_filing_empties`**, BLOCKING at the phase that ships `settled_fraction.py`, with the generator named, the mechanism stated (`OUT_OF_SCOPE`/`INFORMATIONAL` leave `inScope`, so the defence shrinks the denominator), and the **two admissible design repairs** if it fails — recorded in `docs/GATE-CHANGES.md`. Companion `test_defect_table_cannot_raise_the_settled_fraction` named as `05`'s |
| **F23** | FATAL | a self-measured duration sits inside the canonicalised evidence, so `E2E-VERIFY` can never hold | §1.5's table gains a **fifth** non-determinism source with its injector; §1.9 gains `test_contract__no_duration_field_in_a_hashed_object`; §5.4 gains `ci/no-clock-in-core.sh` extended to `perf_counter`/`monotonic`/`process_time`. **The dangerous repair is named and refused**: timings move to `reports/perf/<run_id>.jsonl`; `CanaryRow` keeps `witness_digest`, `observable`, `intersects_read_set`, `fired`, so `canariesRun == len(rows)` still proves D5 |
| **F3** | FATAL (01 half) | G-EVAL arm 2 has no failing condition against its only independent instrument | §1.4's D4 row is no longer "advisory, nightly" in the sense that mattered: a **pre-registered `d`** on the LibreOffice disagreement set downgrades G2 to a `REACH` measurement, with `test_e_eval__d_is_preregistered`; `test_arm_two_author_is_not_the_evaluator_author` forces `SAME-AUTHOR — a weaker instrument` and `PASSED — NOT INDEPENDENT` where the author is the same; rule 3 generalises the label to **every** same-author differential (`test_diff__same_author_differentials_are_labelled`) |
| **F2 / F5** | FATAL / SERIOUS | the clean corpus is produced by the code under test; independence is a declared boolean nothing computes | §6.3 item 6 rewritten: `clean_corpus_independent_of_predicate` is **DERIVED** by a stated formula (import-closure disjointness **and** `read_keys ∩ computed_cells == ∅` **and** provenance), `g4_ffr.check()` raises `UninformativeCorpusError` in the same function as the `SELF-AUTHORED` refusal, `test_nc__Q25` proves it cannot be hand-set, and the narrow residual licence (input-cell-only predicates) is stated with its admission-side twin `test_nc__Q24b`. DoD line D8 widened |
| **F22** | SERIOUS (01 half) | a golden test launders a warrant; `2,373`/`1,374` pinned as MEASURED literals | §1.3 gains **R-GOLD-3** and `ci/golden-literals-are-traceable.sh` (§5.3 stage 2, §5.4, DoD D10): every integer literal compared in `tests/golden/` resolves to §0.3's fixture table or a ledger row. `07` §6 called this *"the fourth impossible control"*; **it is a grep over a ledger** and R-GOLD-2's script already walks the same files |
| **F28** | SERIOUS (01 half) | the copy gate's scan set names three directories P0 never creates, so it would be "fixed" by narrowing | §5.4: `ci/no-green-tick.sh` reads **`cdfc.surface.labels.SCAN_ROOTS`**, never a literal; `test_nc__CI01c_scan_root_list_is_not_a_literal`; the narrowing is recorded in `ci/GATES.md` with its reason. The banned glyph/phrase sets are read from `labels.py` so gate and renderer cannot disagree |
| **F7** | SERIOUS | `ci/no-bare-absence.sh` is defeated by writing the words "positive control" | §2.7 NC-X02 and §5.4: the gate now requires a **resolvable** `ledger:<row_id>` and asserts that row's `positive_control_count > 0`. `test_nc__X02c` has two halves — the four-word phrase, and a cited row whose control count is zero |
| **F16** | SERIOUS | the corpus firewall test cannot run under the firewall it tests | §6.3 item 1: the contamination grep runs **in the corpus repository's own CI**, publishes a signed result, and its hash enters `fixtures/corpus_manifest.json`; the main repo asserts the hash and never checks the corpus out. `test_corpus__contamination_scan_hash_is_fresh` |
| **F36** | SERIOUS | the denominator ships at day 22 and nothing ever validates it, though the plan buys the data | §6.3 gains **item 8**: `corpus_manifest.json` records `cells_written[]`; `test_mask_matches_what_a_competent_filler_filled` publishes two integers against denominator 3,747, warrant MEASURED; a non-zero "outside the mask" count is a **finding** and opens a `GATE-CHANGES.md` row |
| **F24** | SERIOUS | three contracts for `settledFraction` on an `INVALID` run — `null`, forbidden, omitted | §1.9 gains one normative row: **present and `null`**, with the exact JSON Schema `if/then`, and `test_contract__invalid_carries_a_null_not_an_absence`. §1.10's `E2E-INVALID` restated to match |
| **F25** | SERIOUS | `E2E-INVALID` asserts "dead predicates named" on a fixture that never reaches the predicate layer | §1.10's `E2E-INVALID` row corrected to `invalid.template_unbound`, `dead_predicates == []`; a new `E2E-CANARY-SILENT` flow carries the `error.canary_silent` + populated-`dead_predicates` assertion so nothing is lost. `docs/CATALOGUE-CORRECTIONS.md` and `test_plan__no_binding_document_asserts_a_superseded_mechanism` make the propagation failure itself detectable |
| **F31** | SERIOUS | DoD line C4 is the plan's load-bearing evidence and is verifiable only by its author | §4: C4's evidence becomes **a path, not a paste** — the sweep persists `{node_id, flips_expected, flips_observed, assertion_text, commit}` per guard, and `test_sweep__records_the_failing_assertion_text` asserts it is non-empty for every flipped guard. C3 requires all four integers; C5 and C6 tightened |
| **F38** | MINOR | NC-Q02 is green for four phases while proving nothing | §2.0: the sweep reports a **`PROVISIONAL — no admission-side twin yet`** count as its own column, never inside `caught`, with `test_nc_meta__provisional_entries_name_their_closing_phase` |
| **F17** | MINOR | `NC-Q22b` has no catalogue id of its own — and was then **closed under two different ids**, `NC-Q27` here and `NC-Q41` in `04` | §2.4 rule 3 states the general form (a letter suffix is a guard, never a second break); **arbitration C9 assigns the single id `NC-Q56`** and retires both `NC-Q22b` and `NC-Q27`. *The bookkeeping is now repaired as well as the break* |
| **F35 / F41** | SERIOUS | the D5 dual-extraction differential is required by G0 and is listed nowhere | §1.4's table is now **five** differentials; D5 is stated with its disagreement behaviour (disputed regions excluded with page numbers; a quote landing in one cannot clear G0). Which build owns it stays `04`/`06`'s call — this table is where it is *required from* |
| **F30** | SERIOUS (methodology half) | a pre-registered criterion that has to be interpreted after the result is not a criterion | §1.9 gains `test_contract__preregistration_criterion_is_machine_evaluable` — the lock refuses to write a criterion the deciding function cannot consume. Applies to `E4` (`07` P15-B1) and `E6` (`06`) alike. The specific arithmetic for `beats_baselines` remains `06`'s |
| **F8 / F11** | SERIOUS (general form) | a gate of the form `k of n` where we also write `n` is one refactor from `n of n` | §5.1 gains **R-DENOM-1**: every such registry is append-only with a growth log, publishes its cardinality as a **time series**, and a removal requires a dated `GATE-CHANGES.md` argument. `test_registry__append_only[…]` is parametrised over the seven registries. `ci/GATES.md`'s own row set is one of them (F8's half is `02`'s to gate) |
| **F33** | MINOR | equivalent-mutant adjudication is prose by the person being scored | **Not repaired, by agreement with the finding.** §7.8 already declares it and the `K/V` floor is already the headline. The finding proposes no repair beyond keeping `E` visible, which §3.4 does |

### Cross-cutting: reach versus discrimination

New **§0.5**. Every ledger row carries a required `measures ∈ {REACH, DISCRIMINATION, CENSUS}`;
`test_ledger__every_row_declares_its_measurement_class` and `test_ledger__reach_rows_carry_no_quality_claim`
enforce it; `docs/MEASUREMENT-CLASS.md` is append-only. **Both live reach numbers are classified and their
quotable forms fixed**: `2,373 of 3,747` field-surface cells and `511 of 2,826` numeric fault sites — the
second is *the ceiling on the kill rate, not the kill rate*. **R-REACH-1: no hero number is claimed until a
false-failure rate exists**; a `REACH` row renders with its admission state (`PRE-GATE`) and never with a
verb of verification. This is the generalisation of `09` §2.5's ruling on `MS = 18.09%`, where every
arithmetic operator killed at exactly the fraction of sites inside the field graph — a reach number wearing
a quality label.

### Not repaired here, and why

**F6** (`05`), **F9** (`03`/`04`), **F10** (`00`/`02`), **F12** (`00`/`04`), **F14** (`05`), **F15**
(`02`), **F18**, **F19** (`04`), **F20** (`02`), **F21** (`05`), **F26** (`00`/`06`), **F32** (`05`),
**F34**, **F37**, **F43** (`00`), **F39**–**F42**, **F44** (effort tables in their own documents) are
attributed to documents this pass does not own. Where their repair reaches a surface or a registry defined
here, the hook exists: §1.4's `SAME-AUTHOR` rule (F20, F43), §5.1's R-DENOM-1 (F8), §2's reserved ids
(F1, F2, F5, F18, F19), §0.5's classification (F18's `I` integer, F21's marginal-kill figure).

---

## ARBITRATION APPLIED (C1–C9)

Compiled against `plan/11-arbitration.md`. **One writer, serially, document by document** — the previous
repair ran four owners in parallel over a coupled specification and produced eight new contradictions plus
two fresh id collisions inside the repair for id collisions. Every ruling below is applied here, not
summarised; where a ruling took a side, the losing text is deleted rather than softened.

| Ruling | What it did to this document | Where |
|---|---|---|
| **C1** — `d` is a frozen integer | §1.4 rule 1 states `d = 11` and says why the *generator* is not what is pre-registered | §1.4 D4 rules |
| **C3** — F13's retention | `scope_kind` is the adopted mechanism corpus-wide; the 31st reason code is refused; the 8 × 31 exhaustive product is the one this document already pinned and it does not move | §1.9 vocabulary rows (unchanged, and now correct) |
| **C7 / C8(a)** — test names | this document already carried both winners (`test_arm_two_author_is_not_the_evaluator_author`, `test_contract__preregistration_criterion_is_machine_evaluable`); the other documents were brought to it | §1.4 · §1.9 |
| **C9** — the catalogue · **this document is the sole registry** | §2 rewritten as **THE CANONICAL `NC-` REGISTRY**: §2.1 one band table with a reserved unallocated range per band · §2.2 the **RETIRED list**, permanent, never reassigned · §2.3 the complete **old→new mapping** · §2.4 four mechanised rules. **The parallel mapping table and the tie-break rule that generated it are deleted**, and so is the reserved-id paragraph two documents ignored. The four meta-tests are added to the meta-test list, all required at **P0-B3**. `NC-L01`, an orphan referenced by `07` and defined nowhere, is registered here | §2.1–§2.4 · §2.0 meta-tests · F27 row · F17 row · the deleted §mapping |

**What this pass did not touch, stated because the ruling requires it.** **F27** remains the one SERIOUS finding not closed by the adversary pass; the id space is now repaired but the finding's own residue stands. **F37** and **F43** keep their explicit `OPEN — USER DECISION` — those decisions are the user's and are listed in the operating manual. The **`K` and `T` pervasiveness-policy constants still render the literal string `PLACEHOLDER`** and still have no argued basis anywhere in the corpus; that is correct and must not be quietly filled in.
