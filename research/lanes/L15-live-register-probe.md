# L15 — LIVE PROBE OF THE IFSCA PUBLIC REGISTER

> ## ⚠ CORRECTION, 10 Aug 2026 — §3's central conclusion is WRONG. Read this first.
>
> **This lane concluded that the register "resolves names, not registration numbers." That is false,
> and the error is mine.** Lane L08 §C.1 found the working path and I have re-verified it at source:
>
> The list payload carries **two** near-identical id fields — `EncryptDId` and `EncryptedId`.
> I tested `EncryptDId`, found it null in 650 of 650 rows, got HTTP 302 from the detail endpoint, and
> concluded the field was unreachable. **`EncryptedId` is populated in 650 of 650 rows.** Re-verified
> by me just now: `EncryptedId=NWNKjh5jBkU=` →
> `GET /DirectoryList/DirectoryDetailGet` → **HTTP 200, 1,874 bytes**,
> `RegistrationNumber: "IFSC/Retail/2025-26/007"`, `DateOfRegistration: "21/11/2025"`.
> L08 ran this across the whole FME population: **228 of 228 live FMEs return a non-empty
> `RegistrationNumber` and a `DateOfRegistration`** (1 fetch error, coverage 99.6%).
>
> **So predicates 9 and 10 ARE exactly implementable**, as a two-call pattern: one list request for
> membership, then one detail request per entity for the number. §4's claim that they degrade to fuzzy
> name matching is withdrawn.
>
> **Why this is left standing rather than deleted.** I picked the first plausible field, got a
> well-formed null, and reported an absence — the exact failure this program exists to catch, committed
> by the agent writing the spec for it, one hour after writing §4 about someone else committing it.
> It is the corpus's fourth silent false negative and the only one produced by the design team while
> designing. **The `positive control` rule ("before reporting an absence, prove the instrument would
> have found the thing if it were there") would have caught it and I did not run one on the id field.**
>
> **What survives from this lane, and it is worth more than what it lost:** §2's endpoint and type
> vocabulary (MEASURED, unaffected); §4's architectural consequences 1–4 in §6, which hold for a
> different reason — the register is *mutable, undated and paginated*, so it must still be snapshotted
> and content-addressed, and `external_source_unavailable` is still a required UNCHECKED reason.
> `external_source_lacks_field` survives as a **reason code** but this is **not** an instance of it.
>
> **The much stronger finding is L08's, not mine:** of the 228 resolved registration numbers,
> **141 (61.8%) use the legacy `IFSCA/FME/<I|II|III>/<FY>/<n>` scheme and 84 (36.8%) the new
> `FDM<YYYY><AAA><NNNN>` scheme — two incompatible identifier schemes live in the same register on the
> same day — and 3 match neither**, including one whose hyphen is `U+2011 NON-BREAKING HYPHEN`
> (verified at codepoint level; visually identical, byte-wise different, invisible in any screenshot).
> A format predicate over that register has a **measured 38.2% false-failure rate**. That is a better
> demonstration of why the FFR column exists than anything I claimed, and it is real.
>
> Sections 1, 2, 5, 6 and 7 below stand. **Section 3's conclusion and Section 4 are withdrawn.**

**Run by the primary operator agent, 10 Aug 2026, directly against ifsca.gov.in. Every number below is
MEASURED at source today.** This lane was not in the original fan-out; it exists because two of the
seventeen "decidable" predicates in `measurements/oracle-check.md` depend on an external register
resolving, and that dependency had been recorded as *"directory API, verified working"* without the
resolution itself being tested.

Raw artifacts: `/Users/abishaikc/Gift/research/probe/` (`fme.json`, `t24.json`, `t3.json`,
`t23.json`, `dirlist.html`).

---

## 1. WHAT WAS TESTED

Predicates 9 and 10 of the 24-predicate classification:

| # | Predicate as written | Basis as written |
|---|---|---|
| 9 | Registration number resolves in IFSCA's live register | "directory API, verified working" |
| 10 | Scheme authorisation number resolves in IFSCA's scheme register | "same" |

Both require the register to expose a **registration number**. That is the thing tested.

## 2. METHOD AND COVERAGE DENOMINATOR

- `GET https://ifsca.gov.in/DirectoryList` → HTTP 200, 78,784 bytes. The page carries a category
  `<select>` whose options give the full type vocabulary and their `ParentTypeId` values.
- `GET https://ifsca.gov.in/DirectoryList/DirectoryGetList?ParentTypeId={7,24,3,23}&PageSize={200,1000}`
  with `X-Requested-With: XMLHttpRequest` → HTTP 200, JSON.
- **Positive control:** the endpoint is live and returns real, current, non-empty data — 650 records
  for Fund Management, 63 for Fintech Sandbox Entities, 200 (page-capped) for Capital Market
  Intermediaries, 6 for Market Infrastructure Institutions. The absence reported below is therefore an
  absence *in a working response*, not a failed request.

**Type vocabulary recovered from the page (MEASURED, complete):** Banking=1, Finance Company=2,
Capital Market Intermediaries=3, IFSC Insurance Office=4, IFSC Insurance Intermediary Office=5,
**Fund Management=7**, Ancillary Service Provider=9, Global In-House Centres=10, Metals & Commodities=11,
KYC Registration Agency=19, Qualified Jewellers=21, Payment System Provider=22,
Market Infrastructure Institutions=23, **Fintech Sandbox Entities=24**, Payment Service Provider=26,
BATF Service Providers=27, TAS Service Provider=28, Foreign Universities=29,
Surrendered/Cancelled CoRs=30.

## 3. THE FINDING

The JSON row schema **declares** the fields the predicates need:

```
PaginationRequest, SrNo, EncryptDId, DfID, DFTypeId, DfType, Title, TitleInGujarati, Email,
Description, DescriptionInGujarati, PublishDate, IsActive, IsElectionMode, CreatedOn, CreatedBy,
ModifiedOn, ModifiedBy, IsDeleted, RegistrationNumber, DateOfRegistration, ValidityFromDate,
ValidityToDate, RegisteredAddress, NameofContactPerson
```

**Every one of them is null in every row returned, on every type tested.** Fill rates over the 650
Fund Management records:

| Field | Non-null | Rate |
|---|---:|---:|
| `Title` | 650 / 650 | **100.0%** |
| `RegistrationNumber` | 0 / 650 | **0.0%** |
| `DateOfRegistration` | 0 / 650 | 0.0% |
| `ValidityFromDate` / `ValidityToDate` | 0 / 650 | 0.0% |
| `RegisteredAddress` | 0 / 650 | 0.0% |
| `Email`, `NameofContactPerson`, `IsActive`, `DfType` | 0 / 650 | 0.0% |
| `EncryptDId`, `DfID`, `DFTypeId` | 0 / 650 | 0.0% |

Replicated on ParentTypeId 24 (63 rows), 3 (200 rows) and 23 (6 rows): **non-null fields beyond
`Title`: none, in all four populations.**

Because `EncryptDId` is null, the per-entity detail endpoint is **unreachable from the list**:
`GET /DirectoryList/DirectoryDetailGet?EncryptedId=None` → **HTTP 302** (redirect to the page, i.e.
rejected). A `POST` to `DirectoryGetList` → **HTTP 400**; the endpoint is GET-only.

The rendered table confirms the design rather than contradicting it — the public register's columns are
**Category · Sub Category · Sr.No. · Name of Entity**. The strings "Date of Registration",
"Registered Address" and "Validity" appear in the page markup but are not populated by this endpoint.

> **The IFSCA public register, as exposed today, is a NAME LIST. It resolves names. It does not resolve
> registration numbers.**

## 4. CONSEQUENCE FOR THE PREDICATE SET — this is the load-bearing part

Predicates 9 and 10 **cannot be implemented as written**. They must be restated, and the restatement is
strictly weaker:

| Was | Becomes | Class |
|---|---|---|
| "Registration number resolves in IFSCA's live register" | "The declared entity **name** appears in the live register for the declared entity type" | fuzzy string match against a live list |
| "Scheme authorisation number resolves in the scheme register" | "The declared scheme **name** appears in the Fund Management register" | same |

This matters more than losing two checks, and in three distinct ways:

1. **It converts two exact predicates into two approximate ones.** A name match needs normalisation
   (case, punctuation, `Ltd`/`Limited`, `(IFSC Branch)`, `(IFSC)`, leading whitespace — the first record
   returned is literally `" Baroda BNP Paribas Gift Multicap Fund"`, with a leading space). Any
   name-matching predicate therefore has a **non-zero false-failure rate by construction**, and under
   the L4 gate it must carry that measured FFR or not be admitted. It is the first predicate in the set
   that is *inherently* fuzzy — which makes it the best possible worked example of why the FFR column
   exists at all. **Use it in the demo.**
2. **It is a live instance of the corpus's own documented failure mode.** The note "directory API,
   verified working" was true of the *API* and false of the *predicate*. The endpoint answered 200; the
   field was null. A checker built on that note would have returned a clean, confident, well-formed
   PASS for a check it never performed — the third silent false negative in this corpus, and the first
   one found in the design rather than in the measurement.
3. **It is the strongest available argument for the UNCHECKED vocabulary being a first-class output.**
   The honest verdict here is not FAIL and not PASS. It is
   `UNCHECKED(external_source_lacks_field)` — a reason the brief's six-item vocabulary does not
   currently contain, and which the report schema must add.

## 5. A DENOMINATOR WARNING FOR THE PITCH

The live Fund Management register returns **650 records today**. Splitting titles crudely on
`fund|scheme|trust|AIF|VCC`: **365 scheme-like, 285 entity-like** (MEASURED; the split is a regex, so
treat the split as INDICATIVE and the 650 as MEASURED).

The brief's population is **217 FMEs / 360 schemes = 577**, taken from the IFSCA bulletin. Schemes
reconcile closely (360 vs ~365). Entities do not (217 vs ~285) — most likely because the register
carries branch and multi-capacity registrations that the bulletin counts once, and because the bulletin
figure is a stock at a quarter end while the register is live.

**Do not mix the two denominators in the same sentence.** Say "217 FMEs and 360 schemes as at the
bulletin date" or "650 current Fund Management register entries as at 10 Aug 2026", never a blend. The
same discipline that produced §4.1 of the brief applies to the system's own inputs.

## 6. WHAT THIS CHANGES ABOUT THE DESIGN

1. **Add `external_source_lacks_field` to the closed UNCHECKED vocabulary.** Also add
   `external_source_unavailable` (the register may be down at filing time) — a predicate whose oracle is
   a live third-party endpoint has an availability failure mode that a purely local predicate does not.
2. **Every predicate that depends on an external source must declare that dependency in its data
   structure**, with the field it reads and the endpoint it reads it from, so that a schema change at
   the source degrades the predicate to UNCHECKED loudly instead of silently. This is the direct
   architectural answer to the failure found here.
3. **L0 must snapshot and content-address the register response** at run time, exactly as it does the
   template and the filing. Otherwise a report cannot be re-derived: the register is mutable and
   undated. The snapshot hash belongs in the attestation.
4. **The name-matching predicate is the reference implementation for the fuzzy tier.** Build it first
   in the demo, measure its FFR against deliberately perturbed names, and put that number on screen. It
   is the cheapest honest demonstration of the whole thesis.
5. **17/24 is now, strictly, 15 exact + 2 approximate.** The headline should be stated that way. The
   threshold in §4.3 was 50% and still passes, but the composition changed and the composition is the
   product.

## 7. WHAT THIS DOES NOT ESTABLISH

- Whether a **different** IFSCA endpoint or a published register download exposes registration numbers.
  Only the four `DirectoryGetList` populations above were tested. **UNCHECKED.**
- Whether the nulls are a deliberate privacy posture, a defect, or an artifact of the anonymous
  (unauthenticated) call. **UNCHECKED** — and worth one question to IFSCA alongside the §9.6 email.
- Whether filed returns even carry a registration number in a field that could be matched. The blank
  template's field list would settle this and was not re-examined in this probe.
