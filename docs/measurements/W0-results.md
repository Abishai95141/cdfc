# Wave 0 — results

Run 18 Aug 2026 against `/Users/abishaikc/Gift`. Pre-registered criteria taken from
`docs/EXPERIMENT-PROGRAMME.md` §3 **before** the run. Every figure below was produced by running
code in this session. Experiments ran against a copy at `/tmp/w0/repo` so that uncommitted work in
the working tree could not be disturbed.

---

## W0-D — DENOMINATOR CONTAMINATION · **PASS**

| criterion (pre-registered) | measured | |
|---|---|---|
| (envelope files differing, envelope files) | **(0, 571)** | PASS |
| (candidates whose `cells_bound` moved, candidates) | **(0, 348)** | PASS |
| `sum(cells_bound)` | 3,530 → **3,530** | PASS |
| (cells added by the `evidence` and `rule` roots, field surface) | **(0, 3,747)** | PASS |
| `assert_closed` arity | **7** terms, unchanged | PASS |

`BOUND_ROOTS` was widened to `{filing, template, evidence, rule}` and the `ARCHITECTURE §4.3`
cross-root expression compiles, reading all three roots.

**The two zeros above would have been VACUOUS on their own** — no harvested predicate uses the new
roots, so nothing exercised them. The experiment is only meaningful because of two controls:

* **positive control** — a real candidate spiked with `evidence.fin_stmt.net_worth.v` and
  `rule.reg8.threshold.v` adds **0** cells to `bound_cells`;
* **negative control** — the same candidate spiked with a *filing* key moves `bound_cells` **1 → 2**,
  so the instrument is not simply blind.

Cause, and it is structural rather than lucky: `ast_walker.bound_cells` filters on
`KeyRef.parse(key).root != "filing"` — a **whitelist**. New roots cannot enter the denominator
without editing that line.

**A control re-harvest with NO change produced 0 of 571 differing files**, establishing that the
emitter is byte-stable before anything was measured against it.

---

## W0-E — THE ANCHOR HAZARD INSTRUMENT · **PASS**

| criterion | measured | |
|---|---|---|
| (published artefacts stable across `PYTHONHASHSEED` 0/1/2, artefacts) | **(4, 4)** | PASS |
| (hazard surfaces instrumented, surfaces named) | **(4, 4)** | PASS |
| instrument can distinguish a seeded set-ordering perturbation | **yes** | NOT KILLED |

`manifest.json`, `report.html`, `run.db` and `run.jsonl` are byte-identical across three hash seeds.

**The premise the experiment exists to test is CONFIRMED:** `Sheet!REF` occurs in **571 of 571**
envelope files but **only** in `rationale` and `reason_if_inapplicable` — prose. No structural field
carries a cell string. So the proposed instrument ("assert 0 of 571 envelopes differ") tests
*rendering* and would have returned green while exercising none of the ordering hazards.

**The hazard is live, and the tripwire sees it.** Order-sensitive projections give three distinct
hashes across three seeds:

    cells_bound INTEGERS            8b20c40e…  8b20c40e…  8b20c40e…   stable
    cell sets SORTED                f36ca01b…  f36ca01b…  f36ca01b…   stable
    cell sets in ITERATION order    82f18ca4…  0e96d8ab…  b32855e3…   MOVES
    campaign sites, iteration order ed0f0b63…  07e8dd56…  47469ddc…   MOVES
    schema-key union, iteration     3edf8b36…  bfc849cb…  2c57a9f0…   MOVES

The published artefacts are stable **because sorting discipline is applied**, not because the hazard
is absent. The Anchor substitution must be measured against the order-sensitive projections above.

---

## W0-C — MANUFACTURED SUPPORT · **KILL for similarity matching · PASS for exact matching**

Population measured before drawing, as required. Rubric hashed first (`90cdebf211e32b59`):
**54 money occurrences / 30 distinct** in the pinned statute text; the programme's own figure of
25 distinct came from a rubric that truncated `USD 3 Million` to `USD 3`.

Corpus: the 196-page statute PDF via Docling 2.120.3 → 3,328 text items. Draw n=20, seed 20260818,
restricted to tokens Docling also carries (**26 of 30**) so the present arm measures the matcher and
not extractor disagreement.

| arm | exact | fuzzy (`partial_ratio`) |
|---|---|---|
| PRESENT — expect high | **20 of 20** | 20 of 20 |
| WRONG-DOCUMENT — expect (0, 20) | **0 of 20** PASS | **20 of 20** KILL |
| deleted: all occurrences blanked | **0 of 20** PASS | **20 of 20** KILL |
| deleted: all bearing items dropped | **0 of 20** PASS | **20 of 20** KILL |

**Similarity matching manufactures support for everything, at every threshold from 85 to 100.**
A short needle always finds a perfect substring window in a long document, so this is structural and
no threshold repairs it.

**A methodology defect in the programme's own stratum design, found and corrected here.** Deleting a
*single* occurrence gave a spurious 5–7 of 20 under exact matching. Cause: **7 of the 20 drawn values
recur** in the document (`USD 30 Million` ×6, `USD 150,000` ×4). A deletion stratum must remove
**every** occurrence or it measures repetition rather than manufacturing.

---

## W0-B — PATH M STRUCTURAL READ · **PASS, and it is the decisive result of Wave 0**

`eba_validation_rules_4.3_2026_06_23.xlsx`, HTTP 200, **1,071,753 bytes**,
sha256 `9997374c8f60f555…`. Opened with the raw-zip + lxml reader, never Docling.

**One sheet, 12,925 data rows, 15 columns, and column 6 is `Expression`.**

    data rows                       12,925
    rows carrying an Expression     12,925      ← every rule has a machine-parseable expression
    distinct VR codes                8,052
    distinct (code, module) pairs   12,913
    distinct modules                    92
    distinct frameworks                 29
    Active / Inactive        11,056 / 1,869
    Severity: warning / error 12,125 / 800

`N` is recoverable as published integers, and **`rows ≠ N` is DETECTED, not assumed**: a naive row
count would over-report the rule population by 4,873, because a code recurs per module version.
Deactivated rules are present with a status column, exactly as the programme predicted.

**THE INTEGRATION FINDING, and it decides the Anchor design.** The expressions address a
**data-point model**, not spreadsheet cells:

    {tXXX} table refs   23,259
    {rNNNN} row refs    16,054
    {cNNNN} column refs  5,012
    A1-style cell refs      11

e.g. `with {default: 0, interval: true}: {tC_25.01.a, r0010, c0060} * 12.5 = {tC_02.00.a, r0675, c0010}`

So a published rule binds `(table, row-code, column-code)` and **a `CellAnchor` cannot hold it**.
This is direct evidence FOR the `Anchor` abstraction: it must admit a DPM data point as well as a
spreadsheet cell. The expression vocabulary is small and tractable — `with` 12,448, `interval`
13,144, `sum` 3,852, `where` 2,427, `isnull` 1,263, `not` 1,111, `and` 920, `abs` 883, `if/then` 825,
`or` 308, `filter` 159, `max` 67, **`time_shift` 62**. That last one is temporal, and
`cel_profile.py` currently bans the clock — a measured instance of what would have to widen.

---

## W0-A — FIELD-SURFACE DERIVABILITY · **NOT KILLED**

Twenty blanks were planned across four format families. **Sixteen were obtained**; the DOCX family
could not be filled beyond one artifact from public sources in the time available. Per the
programme's own instruction the census is published over the number actually classified and the
criterion is restated over it — never reported as zero, never as a pass by default.

### The census — 16 blanks, 4 families

| family | n | DERIVED | STRUCTURAL | UNDERIVABLE |
|---|---:|---:|---:|---:|
| XLSX (OOXML) | 9 | **7** | 0 | 2 |
| PDF (AcroForm) | 4 | **4** | 0 | 0 |
| XBRL (ESEF packages) | 2 | **2** | 0 | 0 |
| DOCX | 1 | 0 | 0 | **1** |
| **total** | **16** | **13** | **0** | **3** |

**Criterion restated over 16: KILL at more than 8 of 16 not DERIVED. Measured: 3 of 16. NOT KILLED.**

| blank | family | tier | fillable fields | declared construct |
|---|---|---|---:|---|
| Reporting_Format_for_Fund_Management_Entities | XLSX | DERIVED | 3,747 | protection mask + formulas + DV |
| AL_monthly_report | XLSX | DERIVED | 3,537 | protection mask |
| Updated Quarterly Capital Market Intermediaries | XLSX | DERIVED | 2,255 | protection mask |
| ALR_V2_3 | XLSX | DERIVED | 1,599 | protection mask |
| ITFS_Monthly_report | XLSX | DERIVED | 481 | protection mask |
| IBU_Operations_Report | XLSX | DERIVED | 459 | protection mask |
| EDR_1 Exposure Data Report | XLSX | DERIVED | 162 | protection mask |
| Draft_ACAC_Format | XLSX | **UNDERIVABLE** | 0 | no mask |
| IFSCA_Annual_Reporting_Format | XLSX | **UNDERIVABLE** | 0 | no mask |
| IRS f1065 | PDF | DERIVED | **389** | AcroForm |
| IRS f8949 | PDF | DERIVED | **200** | AcroForm |
| IRS f1040 | PDF | DERIVED | **199** | AcroForm |
| IRS fw9 | PDF | DERIVED | **23** | AcroForm |
| ESEF 213800Q5GWTVIW6KJW33 | XBRL | DERIVED | 8 | `xs:element` |
| ESEF Cloetta | XBRL | DERIVED | 6 | `xs:element` |
| IFSCA Compliance Report | DOCX | **UNDERIVABLE** | 0 | sdt=0 ffData=0 FORMTEXT=0 checkBox=0 **emptyCells=0** |

Integration probe: **(DERIVED xlsx surfaces whose every field yields a lawful `cel_path`, DERIVED) =
(7, 7)**, none containing `!`. `schema/fingerprint.structural_fingerprint`, which had **zero callers
in `src/`**, was exercised on all nine and returns a distinct digest for each.

### Three findings that change how the census must be counted

**1. The naive AcroForm count over-reports the fillable surface, and it is the failure mode the
programme named.** `get_fields()` returns container nodes and read-only fields alongside real ones:

    form     get_fields()   terminal /FT   read-only   FILLABLE
    f1040        229            199            0          199
    f1065        500            440           51          389
    f8949        229            202            2          200
    fw9           27             23            0           23

f1065 inflates by 111 fields if containers and read-only entries are counted. A denominator built on
`get_fields()` would tell a filer to complete 51 fields the form computes for them.

**2. f1040 and f8949 both report 229 from `get_fields()` and are NOT the same field set** — 9 shared
names, 220 distinct each. Checked because two equal counts on different artifacts is the
count-vs-contents tell; here the count is honest and the coincidence is real.

**3. The XBRL field counts are NOT field surfaces.** An ESEF package carries the entity's *extension*
taxonomy, which declares only its custom concepts (6 and 8). The filing's real field surface lives in
the core ESEF/IFRS taxonomy, which is thousands of concepts and was not resolved here. The **tier**
is sound — the structure is declared — but these two counts must not be read as denominators.

### The limitation that must be carried, not buried

**The DOCX family has n = 1 and it is the negative case.** One artifact cannot decide a family. What
is established is narrower and still useful: a real regulatory DOCX blank exists that declares
**nothing** — 0 content controls, 0 legacy form fields, 0 checkboxes, and **0 empty table cells**, so
it is not even STRUCTURAL. Its slots are ellipsis runs and the literal string `Yes/No`. Three more
DOCX blanks are needed before the family may be characterised, and no image-only/scanned tier was
sourced at all — that tier is **ABSENT**, with the reason named.

---

# The three experiments selected before development

Wave 1 was cut from six experiments to three: the ones that shape the ARCHITECTURE rather than the
schedule. `W1-3` (the Anchor substitution measurement) was reclassified as **build work** — `W0-E`
already qualified its instrument, so the substitution is measured as it is made, not rehearsed.

## E1 — DPM-XL COMPILABILITY CENSUS · **PASS**

All 12,925 EBA expressions classified against the admitted CEL subset in `cel_profile.py`.
**Fourteen distinct function-like tokens in the entire corpus. Zero unknown constructs.**

| tier | count |
|---|---:|
| **COMPILABLE TODAY** — every token maps to an admitted operator, macro or host fn | **11,886 of 12,925** |
| needs a NEW HOST FN (`isnull` 514, `abs` 383, `max` 52, `min` 25) | 964 of 12,925 |
| **BLOCKED by a deliberate ban** (`time_shift` 62 = the clock, `match` 13 = regex) | **75 of 12,925** |
| UNKNOWN construct | **0 of 12,925** |

**12,850 of 12,925 are reachable with four bounded host-fn registrations and NOT ONE BAN WEAKENED.**
The 75 that are blocked are blocked by exactly the two bans that exist to stop them.

**The real compiler work is one structural construct, not a vocabulary.** 12,448 of 12,925
expressions open with a `with {…}` context header and 12,909 declare `interval:`. CEL has no
equivalent binding form. It must be compiled away into an explicit binding — once, for 12,448
expressions — rather than translated token by token.

## E3 — PATH M GENERALISATION · **PASS, (2, 3)**

Criterion: `(sheets carrying a per-rule expression column, sources opened) ≥ (1, 3)`.

| source | bytes | what it publishes |
|---|---:|---|
| EBA validation rules 4.3 | 1,071,753 | **12,925 DPM-XL expressions**, `{tC_25.01.a, r0010, c0060}` |
| EIOPA Solvency II 2.10.0 | 8,821,323 | **6,768 rows with an `Expression` column**, `{t: S.05.01.13.01, r: R1300, c: C0200, z: Z0001}`, plus a `Deactivated` column |
| ESMA AIFMD rev-6 | 463,932 | **NOT rules.** A 427-row field dictionary: `Id, Field Name, XSD element name, XML type, Format, Type, M/C/O/F, Repetition` |

**Two of three regulators publish executable rules, in DIFFERENT SYNTAX over the SAME
`{table, row, column}` data-point shape.** That is the Anchor requirement confirmed a second time,
independently — it must be a dialect-agnostic data point, not a cell and not one vendor's notation.

**The third source is not a failure, it is a different input.** ESMA publishes a declared field
surface with `M/C/O/F` requiredness — that feeds the **denominator**, not the rule set. A regulator
that publishes no rules may still publish a field surface, and the coverage declaration can consume
one without the other.

## E2 — DPM ANCHOR BINDING · **PASS, both dialects**

### EBA arm — addresses resolve against each rule's own declared scope

    table addresses seen in expressions              18,827
      RESOLVED to the rule's declared Tables column  18,826
      unresolved                                          1
    row coordinates parsed                           54,675
    column coordinates parsed                        45,942
    rules with an empty Tables column                     0

**The single failure is a data defect in the publication, not a parser limit.** `v3695_s` is an
**Inactive** rule whose `Tables` cell holds the literal four-character string `NULL` — not an empty
cell — while its expression reads `with {tC_05.02, c0010, …}`. **Excluding inactive rules the
resolution is 18,826 of 18,826.** A concrete parser requirement falls out: the literal `NULL` means
absent and must never be read as a table name.

### EIOPA arm — a different syntax over the same shape

    rows carrying an Expression        6,767 of 6,767
    table addresses parsed            30,987
    full {t:, r:, c:} triples parsed  23,843

    EBA    with {tC_25.01.a, r0010, c0060}
    EIOPA  {t: S.05.01.13.01, r: R1300, c: C0200, z: Z0001, seq: False, id: v1}

**Two regulators, two notations, one structure.** The Anchor is now specified by evidence rather
than by argument:

1. it carries a **(table, row, column)** triple, and a spreadsheet cell is the degenerate case;
2. **row and column may be a LIST** — `r: R0010; R0030; R0110; …` — or a wildcard `r*` / `c*`;
3. it must tolerate **extra axes** it does not understand — EIOPA adds `z:`, `f:`, `fv:`, `seq:`, `id:`;
4. the **dialect is not part of the identity** — the same data point reached from either notation is
   one anchor, or a rule set cannot be merged with another;
5. `NULL` is absent.

### What E2 did NOT establish, stated plainly

It resolved addresses against the **publishers' own declared scopes**, not against a **filed
instance**. No COREP, FINREP or Solvency II filing is held in this repository and supervisory
filings are largely non-public. So *"the address is well-formed and binds to a declared table"* is
proven; *"a filed artifact carries a fact at that address"* is **not**, and needs one real instance
to close. That is a Phase-2 entry criterion, not a blocker on writing the Anchor type.
