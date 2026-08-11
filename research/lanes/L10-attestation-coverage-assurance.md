# L10 — Attestation, Coverage Declaration, and the Assurance-Profession Analogues

**Lane:** L7 (attestation) and the central intellectual claim — *declaring what you could not check.*
**Compiled:** 10 August 2026.
**Method:** primary-source-first. Where a file is on disk in the scratchpad, I read the raw bytes. Where
I only have a WebFetch summariser's paraphrase, that is labelled SECONDARY even though the URL is
primary. WebSearch was unavailable for this lane (session-wide budget of 200/200 was already consumed
before I started), so **every finding below was obtained by `curl` against a primary host or by
WebFetch against a named URL.** No finding in this file came from a search-results snippet.

---

## PART 0 — THE HEADLINE, STATED ONCE

The brief says, in ARCHITECTURE.md §L7 and RND-BRIEF §5.2:

> *Prior art for the coverage declaration: CycloneDX `compositions.aggregate`, a ten-state completeness
> enum — no analogue exists for a financial assertion.*

**Both halves are wrong, and the second is badly wrong.** The ten-state enum is real but is not the
best prior art in software supply chain, is not the oldest, and is not per-item. And the financial
analogue is not merely present — it is a **mandatory paragraph of a global professional standard that
has been in force since 1 January 2022**, plus a second standard that supplies the *aggregation rule*
the architecture currently lacks entirely.

Five independent systems already implement a per-item "I could not check this" state. Three of them
also specify how it affects the denominator. One of them makes emitting it a `shall`.

This does not kill the project. **It relocates the novelty**, and it hands us a large amount of
free, license-clean design we were about to reinvent badly. §6 states the surviving claim.

---

## PART 1 — CORRECTING THE CYCLONEDX CLAIM (all VERIFIED-AT-SOURCE)

### 1.1 The enum is real, has ten states in 1.5/1.6/1.7, but did **not** exist in 1.2

Method: downloaded the canonical JSON schemas from
`https://raw.githubusercontent.com/CycloneDX/specification/master/schema/bom-<V>.schema.json`
for V ∈ {1.2, 1.3, 1.4, 1.5, 1.6, 1.7} and inspected `definitions.aggregateType.enum` programmatically.

| Spec version | `compositions` present? | `aggregateType` enum size | Notes |
|---|---|---:|---|
| **1.2** | **NO** — zero occurrences of the string `composition` in the schema | — | ARCHITECTURE.md's "has existed since 1.2" is **false** |
| 1.3 | yes | **6** | `complete, incomplete, incomplete_first_party_only, incomplete_third_party_only, unknown, not_specified` |
| 1.4 | yes | 6 | unchanged |
| **1.5** | yes | **10** | the six proprietary/opensource splits added here |
| 1.6 | yes | 10 | `meta:enum` descriptions **not** yet present |
| **1.7** | yes | 10 | **`meta:enum` prose descriptions added** |

**Correction for the brief:** the field first appeared in **1.3 with six states**; the ten-state form
arrived in **1.5**. Releases (from the GitHub releases API on `CycloneDX/specification`): **1.7
published 2025-10-21**, patch **1.7.1 on 2026-06-02**. Repo is Apache-2.0, 534 stars, last push
2026-08-09.

### 1.2 The ten states, verbatim from `bom-1.7.schema.json` `meta:enum`

```
complete                                 The relationship is complete. No further relationships
                                         including constituent components, services, or dependencies
                                         are known to exist.
incomplete                               The relationship is incomplete. Additional relationships
                                         exist and may include constituent components, services, or
                                         dependencies.
incomplete_first_party_only              ... Only relationships for first-party components, services,
                                         or their dependencies are represented.
incomplete_first_party_proprietary_only  ... limited specifically to those that are proprietary.
incomplete_first_party_opensource_only   ... limited specifically to those that are opensource.
incomplete_third_party_only              ... Only relationships for third-party ...
incomplete_third_party_proprietary_only  ... limited specifically to those that are proprietary.
incomplete_third_party_opensource_only   ... limited specifically to those that are opensource.
unknown                                  The relationship may be complete or incomplete. This usually
                                         signifies a 'best-effort' to obtain constituent components,
                                         services, or dependencies but the completeness is
                                         inconclusive.
not_specified                            The relationship completeness is not specified.
```
Default value: `not_specified`. `aggregate` is the **only required property** of a `compositions`
object.

### 1.3 Why it is weak prior art for us — read the enum structurally

Eight of the ten states are **one binary axis crossed with one three-valued axis**: {first-party,
third-party} × {all, proprietary-only, opensource-only}. That is not ten reasons; it is **a taxonomy of
one domain-specific partition of the artifact space.** The genuinely general states are exactly
three: `complete`, `unknown`, `not_specified` — plus `incomplete` as a bare marker.

More importantly it is **aggregate, not per-item.** It tells you the *set* is incomplete. It cannot
tell you *which* component was not examined, or why. Our L5 emits a verdict per (field × predicate);
`compositions.aggregate` has no vocabulary at that granularity.

- **Where this fits (L0–L7):** L7 only, and only as a coarse roll-up field. Genuinely useful as *one*
  header field on our report: a single enum saying how complete the predicate set is relative to the
  template's field graph.
- **Where it stops:** no per-item state, no reason codes, no denominator semantics, no effect on
  scoring, and the partition it encodes (first/third party, proprietary/opensource) has no financial
  meaning.

### 1.4 The far better CycloneDX prior art the brief missed: `declarations` (CDXA), added in 1.6

`bom-1.6.schema.json` has a top-level `declarations` object the brief never mentions:
*"The list of declarations which describe the conformance to standards. Each declaration may include
attestations, claims, and evidence."*

Structure, from the schema:

- `assessors[]` — each with `thirdParty` (boolean): *"The boolean indicating if the assessor is outside
  the organization generating claims. **A value of false indicates a self assessor.**"*
- `attestations[]` — `summary`, `assessor` ref, and `map[]` of
  `{requirement, claims[], counterClaims[], conformance{score 0..1, rationale, mitigationStrategies[]},
  confidence{score 0..1, rationale}}`, plus a per-attestation `signature`.
- `claims[]` — `{target, predicate, evidence[], counterEvidence[], reasoning, mitigationStrategies[],
  signature}`. Note the field is literally called **`predicate`**: *"The specific statement or
  assertion about the target."*
- `evidence[]` — `{propertyName, description, data[], created, **expires**, author, reviewer,
  signature}`.
- `targets{organizations[], components[], services[]}`.
- `affirmation{statement, signatories[]}` — *"A concise statement affirmed by an individual regarding
  all declarations, often used for third-party auditor acceptance or recipient acknowledgment."*
  Schema example string: `"I certify, to the best of my knowledge, that all information is correct."`

And `definitions.standards[]` → `standard{name, version, owner, requirements[]}` where each
`requirement` has `{identifier, title, text, descriptions[], openCre[], parent, ...}` —
*"regulations, industry or organizational-specific standards, maturity models, best practices, or any
other requirements which can be evaluated against or attested to."* **Regulations are explicitly in
scope of `standard`.**

This is, structurally, an OSCAL-lite embedded in an SBOM format, and it is a much closer analogue to
what we are building than `compositions.aggregate`.

- **Where this fits:** L7 envelope design, and L3/L4 vocabulary. `counterClaims` / `counterEvidence`
  is a field we did not have and should. `evidence.expires` is a field we did not have and must have.
  `assessor.thirdParty: false` is an honesty field we are obliged to set.
- **Where it stops:** conformance is a **continuous score in [0,1] with a free-text rationale.** There
  is no discrete "not assessed" state, and a `conformance.score` of 0 is indistinguishable from
  "we never looked." A float plus prose is exactly the interface we are arguing against.

### 1.5 CycloneDX 1.7 `citation` — a per-field attribution mechanism worth stealing

New in 1.7 (`definitions.citation`): *"Details a specific attribution of data within the BOM to a
contributing entity or process."* It carries `pointers[]` (RFC 6901 **JSON Pointers** into the
document) or `expressions[]` (RFC 9535 JSONPath / XPath), plus `timestamp` and `attributedTo`.

- **Where this fits:** L5. This is the right mechanical idiom for our `provenance_pointer` — address a
  verdict to an exact location in the report document by JSON Pointer, and record *which process*
  produced it (deterministic predicate vs model extraction). It solves "weakest-input provenance
  composition" addressing without inventing a scheme.
- **Where it stops:** it attributes *data*, not *verdicts*, and has no notion of a missing datum.

---

## PART 2 — THE PRIOR ART THAT ACTUALLY MATTERS: XCCDF (NIST, 2012)

**This is the most important finding in the lane.**

### 2.1 How I found it (the trail is worth recording)

Reading the OSCAL schema I noticed `finding-target.status.state` is a **closed two-value enum**. Before
reporting that as a limitation I ran a positive control against the OSCAL issue tracker via the GitHub
search API (`repo:usnistgov/OSCAL "not-satisfied"` → `total_count: 5`, control passed, real issues
returned). Issue **#841, "AssessmentResults findings with flexible results values"** (opened
2021-03-05, closed 2021-06-08) opens:

> *"As an OSCAL tool developer, I would like AssessmentResults `findings` to have results values beyond
> the `target.status` allowed values `{ satisfied, not satisfied }`."*

and points at **XCCDF Table 26**. So the reference chain is: our problem → OSCAL's own users had it →
they cited a 2012 NIST standard that had already solved it.

### 2.2 The primary source

**NISTIR 7275 Rev 4, *Specification for the Extensible Configuration Checklist Description Format
(XCCDF) Version 1.2*** (Waltermire, Schmidt, Scarfone, Ziring), updated March 2012.
PDF: `https://csrc.nist.gov/CSRC/media/Publications/nistir/7275/rev-4/final/documents/nistir-7275r4_updated-march-2012_clean.pdf`
(1,846,809 bytes; extracted with `pdftotext -layout` to 290,487 bytes). **Table 26, §6.6.4.2, page 43.**
Nine values, verbatim:

| Value | XCCDF's own definition (verbatim, abridged only where marked …) |
|---|---|
| `pass` [P] | "The target system or system component satisfied all the conditions of the `<xccdf:Rule>`." |
| `fail` [F] | "…did not satisfy all the conditions of the `<xccdf:Rule>`." |
| `error` [E] | "The checking engine could not complete the evaluation, therefore the status of the target's compliance with the `<xccdf:Rule>` is not certain. This could happen, for example, if a testing tool was run with insufficient privileges and could not gather all of the necessary information." |
| `unknown` [U] | "The testing tool encountered some problem and the result is unknown. For example… the testing tool was unable to interpret the output of the checking engine (the output has no meaning to the testing tool)." |
| `notapplicable` [N] | "The `<xccdf:Rule>` was not applicable to the target of the test. For example, the `<xccdf:Rule>` might have been specific to a different version of the target OS, or it might have been a test against a platform feature that was not installed." |
| `notchecked` [K] | "The `<xccdf:Rule>` was not evaluated by the checking engine. This status is designed for `<xccdf:Rule>` elements that have no `<xccdf:check>` elements or that correspond to an unsupported checking system. It may also correspond to a status returned by a checking engine if the checking engine does not support the indicated check code." |
| `notselected` [S] | "The `<xccdf:Rule>` was not selected in the benchmark." |
| `informational` [I] | "The `<xccdf:Rule>` was checked, but the output from the checking engine is simply information for auditors or administrators; it is not a compliance category. This status value is designed for `<xccdf:Rule>` elements whose main purpose is to extract information from the target rather than test the target." |
| `fixed` [X] | "The `<xccdf:Rule>` had failed, but was then fixed…" |

**XCCDF separates, at the per-rule level, four distinct causes of non-settlement that the brief's
six-reason vocabulary conflates or omits entirely:**
- `notchecked` — *no check exists for this rule* (our "predicate not yet synthesised")
- `notselected` — *the check exists but this run's profile excluded it*
- `notapplicable` — *the rule does not apply to this target*
- `error` vs `unknown` — *the check started and could not finish* vs *the check finished and the output
  is uninterpretable*

The brief's vocabulary has **no** state for `notselected`, `notapplicable`, `error`, or
`informational`. On our actual artifact those are not edge cases: the FME workbook has 10 sheets and
217 FMEs / 360 schemes, and a given filer will legitimately not populate whole sheets. Without
`notapplicable` **the coverage fraction is computed against the wrong denominator.**

### 2.3 XCCDF also specifies the denominator rule — §7.3.2.2 Table 40 and §7.3.2.3 Table 41

This is the part nobody quotes and it is the part we need most. In both the Default and Flat scoring
models the algorithm is, verbatim:

> "- if the rule-result's result is not a member of the set {notapplicable, notchecked, informational,
> notselected}, then add 1 to `rule_count`.
> - if the rule-result's result is "pass", add 1 to `rule_score`."

So the formal rule is:

- **Removed from the denominator:** `notapplicable`, `notchecked`, `informational`, `notselected`
- **Kept in the denominator (and therefore counted against you):** `error`, `unknown`, `fail`
- `fixed` is treated as `pass` for scoring, in all four models.

That asymmetry is a deliberate and correct design: *"there is no check for this"* and *"this doesn't
apply"* are removed; *"I tried to check and couldn't"* is **not** removed, because otherwise a tool
could raise its score by failing.

And XCCDF states its own limitation, verbatim from §7.3.2.3: the flat model *"is simple and easy to
compute, but scores between different target systems may not be directly comparable because the
maximum score can vary."*

**That sentence is a direct warning about our UX.** ARCHITECTURE.md §PART 4 makes the headline
*"71% of predicates settled"* — a single fraction whose denominator moves between filings. XCCDF's
authors hit this in 2012 and wrote the caveat into the normative text.

### 2.4 XCCDF `<xccdf:override>`, Table 27 — the human-override trail

`{old-result, new-result, remark, time}`, and *"If the `<xccdf:override>` element is present, the
`<xccdf:result>` element SHALL be changed to match…"*. The spec's own rationale: overrides are
*"necessary when checking a rule requires reviewing manual procedures or other non-IT conditions,
and/or when a check gives an inaccurate result on a particular target system."*

- **Where this fits:** L5 and L7. Our compliance-officer user *will* disagree with a FAIL. XCCDF's
  answer — keep both results, require a rationale and a timestamp, and make the override itself part
  of the signed record — is exactly right and costs us one small object.
- **Where it stops:** XCCDF is XML/SCAP-shaped, tied to `<xccdf:check>` → OVAL, and its target model is
  a host, not a document. We take the vocabulary and the scoring rule, not the format.

### 2.5 What OSCAL actually did with the request — and it is a cautionary tale

Issue #841 was resolved by **PR #944** ("Adds `reason` field to Target", merged 2021-06-07) and **PR
#951** ("Added remarks to AR/finding/target/status", merged 2021-06-07). Net effect, confirmed by
reading `oscal_assessment-results_schema.json` from release **v1.2.3 (published 2026-08-07)**:

```jsonc
"status": {
  "state":  { "allOf": [TokenDatatype, {"enum": ["satisfied","not-satisfied"]}] },   // CLOSED, 2 values
  "reason": { "anyOf": [TokenDatatype, {"enum": ["pass","fail","other"]}] },         // OPEN token
  "remarks": ...
}
```

`state` uses `allOf` (closed). `reason` uses `anyOf` with a `TokenDatatype` branch (**open** — any
token validates; the three listed are suggestions). So OSCAL, asked for nine states, shipped **two
states plus a free-text escape hatch**. Five years and one major version later that is still the model.

**This is the single most useful negative result in the lane.** The most mature, best-funded,
government-backed assessment-reporting standard in existence looked directly at a nine-state vocabulary
in 2021 and declined to adopt it. If we adopt one, we should expect to have to defend it — and the
defence is XCCDF, C2PA and Scorecard, not novelty.

---

## PART 3 — NIST OSCAL, ASSESSED SERIOUSLY

**Repo:** `usnistgov/OSCAL` — 937 stars, 252 forks, last push **2026-08-07**, not archived.
**Latest release: v1.2.3, published 2026-08-07** (three days before this file). Patch release.
**Licence: worldwide public domain / CC0 1.0.** From `LICENSE.md`, verbatim: *"As a work of the United
States government, the work in this repository is in the public domain within the United States"* and
*"the work in this repository is made available in the public domain worldwide using the CC0 1.0
Universal public domain dedication."* **There is no licence obstacle to profiling, forking, or
embedding OSCAL.** (GitHub reports `NOASSERTION` because CC0 is expressed in a non-standard file — a
false negative from the API, not a real ambiguity.)

The v1.2.3 release ships 4 model schemas relevant to us as separate JSON Schema assets:
`oscal_assessment-plan_schema.json` (144,952 B), `oscal_assessment-results_schema.json` (152,214 B),
`oscal_poam_schema.json` (148,253 B), `oscal_component_schema.json` (82,323 B).

### 3.1 What OSCAL gets right and we should take

**(a) `reviewed-controls` — a first-class scope declaration.** Each `control-selection` is either
`{include-all, exclude-controls[], remarks}` or `{include-controls[], exclude-controls[], remarks}`,
and there is a parallel `control-objective-selections` with `exclude-objectives[]`. The schema
description is explicit that it is *not* just a plan: *"In the assessment plan, these are the planned
controls. In the assessment results, these are the actual controls, and reflects any changes from the
plan."*

That is a genuinely good idea we do not have: **the report carries both the planned and the actual
scope, and the delta is visible.** It is the machine-readable form of ISRS 4400 ¶A56 (§4.2 below).

**(b) `observation.methods` — a closed-ish vocabulary for *how* a thing was checked**, enum
`["EXAMINE","INTERVIEW","TEST","UNKNOWN"]` (open via `anyOf`), inherited from NIST SP 800-53A.
`observation` requires `{uuid, description, methods, collected}` and optionally carries `expires`:
*"Date/time identifying when the finding information is out-of-date and no longer valid. Typically used
with continuous assessment scenarios."*

**(c) `origin-actor.type` — enum `["tool","assessment-platform","party"]`**, described as *"The actor
that produces an observation, a finding, or a risk. One or more actor type can be used to specify a
person that is using a tool."* OSCAL can say *a machine asserted this*, and can distinguish that from
*a human asserted this*. We need exactly that at L2/L5.

**(d) `assessment-assets`** — *"Identifies the assets used to perform this assessment, such as the
assessment team, scanning tools, and assumptions"*, with `assessment-platforms[]` → `uses-components[]`.
This is the slot for "predicate registry v3.2.1, sha256:…".

**(e) `relevant-evidence[]` with `href` + `description`, and `collected`/`expires` timestamps.**

**(f) The POA&M model is a near-exact fit for the "Unchecked panel".** `plan-of-action-and-milestones`
requires `{uuid, metadata, poam-items}` and each `poam-item` carries `{title, description, origins[]
(with tool/party actors), related-findings[], related-observations[], related-risks[]}`. The associated
`risk` model carries `response` with `lifecycle` enum `["recommendation","planned","completed"]` and
tasks with milestones. ARCHITECTURE.md §PART 4 asks for an Unchecked panel where each entry carries
"its reason and *what would make it checkable*". **That is a POA&M item.** Reuse rather than invent.

### 3.2 Where OSCAL stops — three hard stops, each load-bearing

**Stop 1 — the verdict model is binary and closed.** `finding-target.status.state ∈ {satisfied,
not-satisfied}`. Our third state cannot be expressed without pushing it into the open `reason` token,
at which point schema validation no longer protects the thing the whole product is about. A validator
would accept `{"state":"satisfied","reason":"actually-we-never-checked"}`.

**Stop 2 — non-coverage is expressed by omission plus a scope statement.** OSCAL's only mechanisms for
"we didn't assess this" are (i) `exclude-controls` / `exclude-objectives` in `reviewed-controls`, which
carry **no reason code — only free-text `remarks`**, and (ii) simply not emitting a `finding`. And
`findings` was made **optional** in 2021 (issue #918, closed 2021-05-20, via PR #931). The discussion
on that issue is worth quoting because the maintainer saw the exact hazard:

> David Waltermire, 2021-05-04: *"In your view do the OSCAL schemas represent: 1. any valid interim
> state of information… a less than complete assessment is ok, 2. A complete set of information… an
> assessment without a finding is not a completed assessment. I believe item 1 is at odds with item 2."*

> Lou Degenaro, 2021-05-04: *"For example, say you have 1 observation which is 'not applicable'. There
> would be no finding in that case, **since neither satisfied nor not satisfied is known**."*

That is the silent all-clear, described precisely, by an OSCAL implementer, in the OSCAL issue tracker,
and resolved by *making the findings list optional* rather than by adding a third state. **An OSCAL AR
with zero findings is schema-valid and means nothing in particular.**

**Stop 3 — the ontology is security-control-shaped.** `select-control-by-id`, `statement-id`,
`objective-id`, `implementation-status ∈ {implemented, partial, planned, alternative, not-applicable}`,
`system-component`, `inventory-item`, `port-range`, `protocol`. Mapping "IFSCA FM Regulations reg 27(1),
NAV frequency owed" onto an OSCAL control catalog is *possible* — OSCAL's catalog model is generic
(`group`/`control`/`part`/`param`) — but our unit of assessment is a **cell in a workbook bound to a
clause**, and OSCAL has no cell.

### 3.3 Verdict: **profile it, do not be it** — a specific recommendation

> **Recommendation:** the normative artifact is our own schema (§7). We additionally emit an **OSCAL
> Assessment Results projection** as a declared-lossy export, and an **OSCAL POA&M** as the Unchecked
> panel's interchange format. We do **not** make OSCAL AR the primary representation.

Rationale, in one line each:
1. The one field that carries the entire product thesis — the third verdict state — is the one field
   OSCAL closes at two values.
2. Encoding it in the open `reason` token gets us OSCAL's syntax without OSCAL's validation, which is
   the worst of both.
3. The lossy projection is still worth emitting, because it is what a supervisor's GRC stack can
   already ingest, and because `compliance-trestle` gives us the writer for free.

**The projection rule, stated so the loss is explicit and auditable:**

| Our state | OSCAL AR encoding | What is lost |
|---|---|---|
| PASS | `finding` with `status.state = "satisfied"` | nothing |
| FAIL | `finding` with `status.state = "not-satisfied"` | nothing |
| INDETERMINATE / NOT_RUN / NO_PREDICATE | **`observation`** with `methods:["TEST"]`, `types:["control-objective"]`, our reason as a `prop` in namespace `https://<ns>/oscal`, **and no `finding`**, **and** a matching `reviewed-controls.control-selections[].exclude-controls[]` entry | the state is demoted from a verdict to an observation; a naive OSCAL consumer sees only "no finding" |
| OUT_OF_SCOPE | `exclude-controls[]` entry only | reason code survives only as a `prop` |

Any downstream party reading only the OSCAL projection **will** see a smaller, cleaner report than the
truth. The projection must therefore carry a mandatory `metadata.prop` flagging that it is a lossy
projection and naming the URI of the normative artifact. Say it in the file, not in a README.

### 3.4 OSCAL tooling — maturity, checked

| Tool | Licence | Signal (from GitHub API, 10 Aug 2026) | Verdict |
|---|---|---|---|
| **`oscal-compass/compliance-trestle`** | **Apache-2.0** | 265★, 103 forks, **Python**, created 2020-08-30, pushed **2026-08-10**, latest release **v5.0.0 published 2026-08-07** | **ADOPT** |
| `usnistgov/oscal-cli` | NOASSERTION (NIST public domain) | 69★, repo pushed 2026-08-07 but **latest release v1.0.3 published 2024-02-02** — releases lag the repo by 2.5 years | EVALUATE — use from source or via trestle |
| `metaschema-framework/oscal-cli` | NOASSERTION | 15★, pushed 2026-06-16 | REJECT — too thin to depend on |

`compliance-trestle` ships pydantic models for exactly the models we need — confirmed by listing
`trestle/oscal/`: `assessment_plan.py` (4,997 B), `assessment_results.py` (10,002 B), `poam.py`
(6,065 B), `component.py`, `catalog.py`, `profile.py`, `ssp.py`, `mapping.py`, `common.py` (114,686 B).
Its README claims, verbatim: *"Detached signing and verification for JSON artifacts."*

- **Where this fits:** L7 directly. Python, Apache-2.0, actively released, already does OSCAL
  serialisation **and** detached JSON signing. This is the single highest-value reuse in the lane and
  it removes a week of L7 work.
- **Where it stops:** it is opinionated toward a git-based CI/CD compliance workflow with markdown
  authoring and drawio governance — we want the object model and the signer, not the workflow. And it
  inherits OSCAL's binary verdict, so it cannot represent our third state natively either.

---

## PART 4 — THE ASSURANCE-PROFESSION ANALOGUES (the brief's blind spot)

### 4.1 ISRS 4400 (Revised) — this alone refutes "no analogue exists for a financial assertion"

**Primary source obtained and read in full:** *International Standard on Related Services 4400
(Revised), Agreed-Upon Procedures Engagements*, IAASB Final Pronouncement, April 2020, 33 pages.
PDF: `https://www.irba.co.za/upload/ISRS-4400-Revised-Agreed-Upon-Procedures.pdf` (425,798 bytes;
`pdftotext -layout` → 95,277 bytes). **Effective for AUP engagements for which the terms of engagement
are agreed on or after 1 January 2022.**

*Copyright note: IAASB/IFAC text is copyrighted. Below I cite paragraph numbers and paraphrase, with
one short verbatim quotation of the sentence that is the crux of this lane.*

**¶30 is an eighteen-element mandatory report structure, (a)–(r).** The elements that matter here:

- **¶30(e)(ii)** — the report must state that findings are the factual results of the procedures
  performed.
- **¶30(h)** — the practitioner must state that they make no representation regarding the
  *appropriateness* of the procedures. **The adequacy of the check-set is explicitly disclaimed.**
- **¶30(i)** — the report must state the engagement is not an assurance engagement and that the
  practitioner does not express an opinion or an assurance conclusion. *(This is "no green tick",
  mandated.)*
- **¶30(j)** — the crux. The report must contain a statement that, verbatim from the illustrative
  report in Appendix 2:
  > "Had we performed additional procedures, other matters might have come to our attention that would have been reported."
- **¶30(n)** — a description of the procedures performed detailing the **nature and extent, and if
  applicable, the timing, of each procedure.**
- **¶30(o)** — the findings from **each** procedure performed, including details on exceptions found.
- **¶32(b)** — if a summary of findings is provided, the report must state that **reading the summary
  is not a substitute for reading the complete report.**

**¶13(f), the definition of "Findings":** findings are the factual results of the procedures; findings
are **capable of being objectively verified**; and the term expressly excludes opinions, conclusions in
any form, and recommendations.

> **That definition is ISA-land's version of RND-BRIEF §2.4.** The brief treats "17 of 24 predicates
> are script-settleable" as a discovery about the boundary between machine-checkable and not. ISRS 4400
> makes **objective verifiability a definitional precondition of being a reportable finding at all.**
> The profession did not discover the boundary; it made it a membership rule for the report.

**¶A56 — the not-performed declaration**, which is the closest existing thing to our UNCHECKED panel:
where previously-agreed procedures were not performed or were modified, the practitioner *may* identify
in the report the procedures agreed in the original engagement terms which could not be performed or
were modified, **and why that has arisen** — and A56 notes this matters particularly where the
procedures are set out in law or regulation.

**¶A52** — the practitioner may clarify that the report does not extend beyond the subject matters on
which the procedures were performed, giving the worked example of a report on accounts receivable and
inventory that *"does not extend to the entity's financial statements taken as a whole."*

**Appendix 2, Illustration 1** is a literal **two-column `Procedures | Findings` table** with
denominators written into the finding text — e.g. of 125 contracts on the listing, 37 were identified
as valued over $25,000; all 37 were subject to bidding by at least 3 contractors; amounts paid were
within $100 of agreed amounts in all 37, with no exceptions noted.

**Appendix 2, Illustration 2** assumes, among its stated circumstances, that *"the regulator is the
intended user and the entity overseen by the regulator is the engaging party and responsible party."*

> **That is our exact two-user model** — RND-BRIEF §5.4: "the filer's compliance officer
> pre-submission; a supervisor triaging ~868 filings/year." ISRS 4400 already contemplates it, names
> the parties, and gives the report template.

- **Where this fits:** L5 verdict semantics and L7 report structure, and — more importantly — the
  **pitch**. It gives an internationally-recognised, regulator-facing, financial report form whose
  entire design principle is *list the procedures, list the factual findings, express no conclusion,
  and state that more procedures might have found more.*
- **Where it stops:** ¶A56 is a **may**, not a **shall** — the not-performed declaration is optional
  and free-text. The report is human prose in a two-column table; there is no schema, no closed
  vocabulary, no machine-readable form, no coverage fraction, and no per-procedure error rate. And
  every procedure is *agreed with the engaging party in advance* — the procedure set is negotiated, not
  derived from the artifact, and its adequacy is expressly disclaimed (¶30(h)).

**That last sentence is where our novelty actually lives. See §6.**

### 4.2 ISA 705 (Revised) — the aggregation rule the architecture is missing

**Primary source obtained and read:** *ISA 705 (Revised), Modifications to the Opinion in the
Independent Auditor's Report*, `https://www.irba.co.za/upload/ISA-705-Revised.pdf` (`pdftotext` →
72,127 bytes).

ARCHITECTURE.md L5 emits PASS / FAIL / UNCHECKED per (field × predicate) and then… stops. There is **no
stated rule for turning that vector into a filing-level verdict.** ISA 705 is that rule, and it is a
2×2 that has been the global standard for decades.

**¶6** — the opinion is modified when either (a) the evidence obtained shows the statements are not
free from material misstatement, or (b) **the auditor is unable to obtain sufficient appropriate audit
evidence.** Two causes, kept separate.

**¶5(a)** defines **pervasive** — effects that in the auditor's judgment are not confined to specific
elements/accounts/items; or if so confined, represent or could represent a substantial proportion of
the financial statements; or, for disclosures, are fundamental to users' understanding.

The 2×2 (¶¶7, 8, 9):

| | material but **not pervasive** | material **and pervasive** |
|---|---|---|
| **(a) evidence obtained, misstatement found** | **Qualified** opinion (¶7(a)) | **Adverse** opinion (¶8) |
| **(b) unable to obtain sufficient appropriate evidence** | **Qualified** opinion (¶7(b)) | **Disclaimer** of opinion (¶9) |

And the language is *engineered* to keep the two causes distinguishable in the sentence itself (¶17):
a misstatement-driven qualification says "except for the **effects** of the matter(s)…"; an
evidence-driven qualification uses the corresponding phrase "except for the **possible effects** of the
matter(s)…". **One word — "possible" — carries the entire distinction between a known defect and an
unexamined region.**

**¶24 is the one to put on a slide:**
> If the modification results from an inability to obtain sufficient appropriate audit evidence, the
> auditor **shall** include in the Basis for Opinion section **the reasons for that inability.**

**That is a mandatory requirement to state the reason you could not check something, in an audit report
on financial statements, applied worldwide.** The brief's "no analogue exists for a financial
assertion" cannot survive it.

Two more mechanics worth copying:
- **¶19(c)** — when disclaiming, the auditor must amend the ISA 700 statement that the financial
  statements *have been audited* to say the auditor *was engaged to audit* them. **The report is
  forbidden from even implying the work was completed.**
- **¶20(a)/(b)** — the "Basis for Opinion" heading must be renamed to "Basis for Qualified/Adverse/
  Disclaimer of Opinion", and must contain a description of the matter giving rise to the modification.
  **The headline changes shape when the coverage changes.** Compare ARCHITECTURE.md's fixed coverage
  meter.
- **¶21** — where a misstatement relates to specific amounts, quantify the financial effects **unless
  impracticable, and if impracticable, say so in that section.** A mandated "we could not even size
  this" statement.

- **Where this fits:** L5 → L7. Gives us (i) the aggregation function from per-item states to a
  document-level verdict, (ii) the *pervasiveness* criterion that decides which aggregate state you
  land in, and (iii) the rule that the aggregate verdict's **name and heading** must change with the
  residue rather than a number moving on a fixed dial.
- **Where it stops:** "material" and "pervasive" are matters of professional judgment (¶5 says "in the
  auditor's judgment"). We cannot compute them. We can, however, define a **declared, published,
  versioned pervasiveness policy** and apply it deterministically — which is strictly more inspectable
  than judgment, and is the honest form of the borrowing. Do not claim we have implemented ISA 705;
  claim we have implemented a *declared policy in its shape*.

### 4.3 PCAOB AS 1215, *Audit Documentation*

Read from the PCAOB's own page, HTML fetched and stripped to text
(`https://pcaobus.org/oversight/standards/auditing-standards/details/AS1215`, 106,289 B → 31,580 B text).

- **.06** — the auditor must document the procedures performed, evidence obtained, and conclusions
  reached with respect to relevant financial statement assertions; documentation must clearly
  demonstrate that the work was in fact performed, who performed it, who reviewed it, and the date of
  review.
- **.06A — the experienced-auditor test.** Documentation must contain sufficient information to enable
  *"an experienced auditor, having no previous connection with the engagement"* to understand the
  nature, timing, extent and results of the procedures, the evidence obtained, and the conclusions
  reached — and to determine who did the work and when.
- **.08 — the counter-evidence requirement.** In addition to documentation supporting the final
  conclusions, documentation **must include information the auditor has identified relating to
  significant findings or issues that is inconsistent with or contradicts the auditor's final
  conclusions**, including procedures performed in response and records of resolutions of differences
  in professional judgment.
- **.07** — the required extent of documentation scales with, among other things, *the extent of
  judgment required* — estimates require more.
- **.14/.15** — seven-year retention from report release date; complete and final documentation
  assembled for retention no more than 14 days after report release.

- **Where this fits:** L7 and the Predicate Library screen. **.06A is the design test for the whole
  product**: our report is adequate iff an experienced reviewer with no connection to the run can
  reconstruct what was checked, how, by what version, and what was not. And **.08 tells us to record
  the predicates that were synthesised and *rejected* by L4, and the mutation-testing near-misses** —
  the evidence that argues against our own verdict. We were going to throw that away.
- **Where it stops:** AS 1215 is a documentation-retention standard for a US public-company audit. It
  has no schema, no vocabulary, and no coverage concept. And its 7-year retention is a real,
  non-trivial operational obligation if we ever position the output as audit documentation — **we
  should explicitly position it as an input to the auditor's work, not as audit documentation.**

### 4.4 ISAE 3402 / SSAE 18 SOC 1 carve-out vs inclusive — **UNVERIFIED, and I am declaring it**

This was on my task list and I **could not open a primary source.** Attempts, all recorded:

| Attempt | Result |
|---|---|
| `iaasb.org/publications/...isae-3402...` (2 URL forms) | HTTP 404 |
| `ifac.org/_flysystem/azure-private/publications/files/ISAE 3402.pdf` and `ISAE-3402.pdf` | HTTP 404 |
| `irba.co.za/upload/ISAE 3402.pdf`, `ISAE3402.pdf`, `ISAE-3402.pdf` | HTTP 301 → HTML, and 404 |
| `hkicpa.org.hk/.../isae3402.pdf` | 200 but `text/html`, not the PDF |
| ICAI SAE 3402 (Indian equivalent) — 2 CDN paths | HTTP 404 / `application/xml` |
| AICPA AT-C §320 PDF | 301 redirect to a marketing download page |
| IFAC Handbook Vol. 2, 3 URL forms | HTTP 404 |

**Positive control:** the ISRS 4400 fetch from the *same* IRBA host succeeded (425,798 bytes of real
PDF), so the host and my method work; the failures are wrong paths, not a claim that the documents do
not exist. **I therefore report nothing about ISAE 3402's or AT-C 320's exact wording.**

What I can say from the structure of the task without a source: the carve-out/inclusive distinction is
a named, standardised way for a service-organisation assurance report to declare that a subservice
organisation's controls are **excluded from the scope** (carve-out) or **included** (inclusive). If
that is accurate, it is a *third* independent financial-assurance mechanism for declaring
non-coverage — and it would be worth one hour to confirm at source, because it is the analogue for our
"requires counterparty data" reason. **Marked UNVERIFIED. Do not put it on a slide until someone opens
the standard.** (§9, open question 1.)

### 4.5 ISA 200 / 315 / 330 / 320 / 600 (Revised) — **NOT CHECKED, and declared as such**

I probed IRBA for `ISA-200`, `ISA-320`, `ISA-330`, `ISA-315-Revised-2019`, `ISA-600-Revised` under the
naming pattern that worked for ISA 705 — all HTTP 404. I did not pursue them further because ISA 705
already supplies the load-bearing mechanism (the 2×2 and ¶24) and budget was better spent on C2PA and
XCCDF. **ISA 600 (Revised) component scoping is the notable gap** — it is the standard's answer to
"which parts of a group did we actually do work on, and to what depth", which is structurally our
coverage problem at the portfolio level. §9, open question 2.

*This section is itself a worked example of the product's thesis: the honest output is a declared,
reasoned NOT-CHECKED with the exact remedy attached, not a silent omission.*

---

## PART 5 — THE SOFTWARE SUPPLY CHAIN, AND WHAT EACH ONE ACTUALLY CONTRIBUTES

All repo metrics below are from the GitHub API on **10 August 2026**.

### 5.1 C2PA — the strongest technical analogue found, and it makes it a `shall`

**Spec:** C2PA Technical Specification **2.4** (`https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html`;
1,065,169 bytes HTML → 621,430 bytes text, read locally). Versions 2.1–2.4 exist; 2.5 returns 404.
Implementation `contentauth/c2pa-rs`: 381★, 176 forks, pushed 2026-08-10.

**Result structure (§15.2.1, CDDL):**
```cddl
status-map = {
  "code": $status-code,          ; label-formatted string describing the status
  ? "url": jumbf-uri-type,       ; JUMBF URI pointing at the exact box this code applies to
  ? "explanation": tstr,         ; human readable
  ? "success": bool              ; DEPRECATED. Does the code reflect success (true) or failure (false)
}
status-codes-map = {
  "success":       [* $status-map],   ; May be empty.
  "informational": [* $status-map],   ; May be empty.
  "failure":       [* $status-map]    ; May be empty.
}
validation-results-map = {
  ? "activeManifest": $status-codes-map,
  ? "ingredientDeltas": [* $ingredient-delta-validation-result-map],
  ? "specVersion": semver-string,     ; version of the spec the validation was performed against
  ? "trustListUri": tstr              ; the trust list used to validate certificates
}
```

**Note `"success": bool` is marked DEPRECATED.** The 2.1 change log records, verbatim: *"LOTS of new
validation status codes, including a new 'informational' code type."* **C2PA shipped a binary
success/failure model, found it insufficient in production, and replaced it with a three-way
classification.** That is direct empirical support for our design, from a shipping ecosystem.

I extracted 94 distinct status codes from the 2.4 text. The **informational** bucket, from the CDDL
around §15.2.2.2 and Table 3, contains precisely the "could not / did not check" codes:

| Code | Spec's definition, verbatim |
|---|---|
| `signingCredential.ocsp.inaccessible` | "The validator attempted to perform an online OCSP check, but did not receive a response." |
| `signingCredential.ocsp.skipped` | "The validator chose not to perform an online OCSP check." |
| `signingCredential.ocsp.unknown` | "The OCSP response contains an `unknown` status for the signing credential" |
| `ingredient.unknownProvenance` | "The ingredient does not have a C2PA Manifest." |
| `algorithm.deprecated` | (informational; validator proceeds but flags) |
| `assertion.{dataHash,boxesHash,bmffHash}.additionalExclusionsPresent` | "A data hash specified exclusion ranges other than the C2PA Manifest Store." |

And the failure bucket contains `algorithm.unsupported`, `manifest.inaccessible`,
`assertion.inaccessible`, `signingCredential.ocsp.revoked`, `signingCredential.invalid`.

**Look at the five OCSP outcomes together — one check, five distinguishable results:**

| Outcome | Meaning | Bucket |
|---|---|---|
| `ocsp.notRevoked` | checked, clean | success |
| `ocsp.revoked` | checked, dirty | failure |
| `ocsp.unknown` | checked, the oracle itself returned "don't know" | informational |
| `ocsp.inaccessible` | tried to reach the oracle, no response | informational |
| `ocsp.skipped` | **deliberately did not perform the check** | informational |

**§15.9.2 makes it mandatory**, verbatim: *"If the validator chooses not to perform an online OCSP
check, it shall issue a `signingCredential.ocsp.skipped` informational code. If the validator attempts
to query the OCSP responder but is unable to receive a response, the validator shall issue a
`signingCredential.ocsp.inaccessible` informational code."*

And the *reason* the state exists is instructive: §15.9.2 notes that *"Querying the credential status
method can reveal to an observer the identity of the asset being validated, and so this query is
optional."* **The unchecked state was forced into existence because skipping was legitimate and
common.** That is the general law: a not-checked state becomes necessary exactly where not checking is
a defensible choice rather than a failure. On our artifact, the same pressure exists — a filer's
register lookup may be rate-limited, a look-through may be commercially unavailable.

C2PA's governing principle, §1, verbatim:
> "C2PA specifications SHOULD NOT provide value judgments about whether a given set of provenance data is 'good' or 'bad,' merely whether the assertions included within can be validated."

That is ARCHITECTURE.md's "no green tick" commitment, written as a spec principle by a consortium.

One more idea to steal: C2PA distinguishes **`created_assertions`** (made by the signer) from
**`gathered_assertions`** (collected at claim-generation time from elsewhere). That is exactly our
distinction between *what the system computed* and *what the filer declared or what a register
returned*, and it is a cleaner encoding than a `provenance_pointer` string.

- **Where this fits:** L5 (per-item state vocabulary, three-bucket classification, per-item pointer via
  `url`) and L7 (`specVersion` + `trustListUri` = "which version of the checking apparatus ran").
- **Where it stops:** C2PA validates *bindings and signatures* — hashes, certificates, timestamps. Every
  status code is about cryptographic or structural integrity. **Not one code concerns whether an
  asserted fact is true.** It answers "was this manifest tampered with", never "is this number right".
  That is the entire remaining distance, and it is our distance.

### 5.2 in-toto — the closed-world lesson, which is architectural not cosmetic

`in-toto/attestation`: 361★, **Apache-2.0** (`LICENSE`: "Copyright 2021 in-toto Developers… Apache
License, Version 2.0"), pushed 2026-08-04. `in-toto/in-toto`: 1,026★, pushed 2026-08-05.
Spec read from `in-toto/docs/in-toto-spec.md` (93,385 bytes).

**The layout (§4.3)** is signed by a trusted key and declares *"which keys are authorized for signing
the link metadata, as well as the required steps to perform in this supply chain"* —
`{_type:"layout", expires, readme, keys, steps[], inspect[]}`. Each step carries `threshold` —
*"an integer value indicating how many pieces of link metadata must be provided to verify this step."*
**A step with no link metadata meeting its threshold fails verification.** in-toto's answer to "how do
you know a step was skipped" is: *enumerate the required steps in a signed policy, and make absence a
failure.*

**§4.3.3.1, and this is the sentence that matters most in the whole supply-chain section:**
> "There is an implicit `"ALLOW *"` at the end of each rule list. By explicitly specifying
> `"DISALLOW *"`, in-toto verification fails if an artifact was not consumed by an earlier rule. Not
> including `"DISALLOW *"` at the end of a rule list could allow artifacts to sneak into the step or
> inspection **undetected**. As such, it is generally recommended that all rule lists include a
> `"DISALLOW *"` at the end."

in-toto's own default is **open-world**, the spec names the resulting hazard in its own text, and the
recommended fix is an explicit terminal deny that converts unaccounted-for residue into a hard failure.

- **Where this fits:** **L1 → L5 → L7, and it is the deepest borrowing in this file.** L1 already
  induces the complete field graph from the blank template — 854 label instances, 6,757 cells, 294
  formulas (RND-BRIEF §4.3). **That induced schema is our layout.** It is an authoritative, complete
  enumeration of the universe, derived deterministically from the regulator's own published artifact.
  Therefore: every (field × obligation) pair that is neither settled nor explicitly classified into a
  declared UNCHECKED reason is a **`DISALLOW *` hit — a hard error in report generation, not a gap in
  the report.** The coverage claim then becomes true by construction, in the same way L4 makes the
  error-rate claim true by construction.
- **Where it stops:** in-toto's subject is a build pipeline; steps are commands and artifacts are files.
  It has no notion of a partially-verified artifact, no reason codes, and its DSSE envelope carries no
  coverage semantics. We take the closed-world principle and the envelope, not the model.

**Predicate types inspected** (`spec/predicates/`, 17 files):
- **`test-result` v0.1** — `{result: "PASSED|WARNED|FAILED", configuration[], url, passedTests[],
  warnedTests[], failedTests[]}`. It states its use case as verifying *"that all tests were in fact
  run"* — but **there is no `skippedTests[]` or `notRunTests[]` array.** The "were they all run" check
  is performed by an external policy that names the expected tests out of band. **Direct negative
  finding: the standard test-result attestation cannot express a test that did not run.**
- **`svr` v0.2 (Simple Verification Result)** — `{verifier{id, policies[]}, timeCreated, properties[]}`
  where `properties` is defined as *"the **passing** properties verified for the artifact."*
  `verifier.policies` is **required even when empty** — producers *"MUST include this field even when no
  policy can be referenced; in that case, the value MUST be an empty array."* Positive-only list:
  a property that failed and a property never checked are **both simply absent.**
  Its virtue is the inverted default — only what is listed is verified, everything else is unverified
  by construction — which is a legitimate and cheap design. Its vice is that failure and non-coverage
  are indistinguishable.
- **`scai` v0.3** — `{attributes[{attribute, target?, conditions?, evidence?}], producer?}`. Deliberately
  unopinionated: *"this predicate does not dictate the types of attributes that can be attested, nor
  does it prescribe any format to the evidence."* Useful as a generic evidence-binding envelope; carries
  no coverage semantics.

### 5.3 SLSA VSA — `UNEVALUATED`, and the absent-vs-empty rule

Spec read raw from `https://raw.githubusercontent.com/slsa-framework/slsa/main/spec/verification_summary.md`
(16,495 bytes). `slsa-framework/slsa`: 1,906★, pushed 2026-08-09. **v1.1 is retired; v1.2 is current
(status "Approved").**

Schema: `{verifier{id, version}, timeVerified?, resourceUri, policy{uri, digest}, inputAttestations[]?,
verificationResult: "PASSED|FAILED", verifiedLevels[], dependencyLevels?, slsaVersion?}`.

**`SlsaResult` (§ *SlsaResult (String)*), verbatim:** the value SHOULD be
> "- The [SLSA Track](#tracks) level the referenced artifact qualifies for as `SLSA_<TRACK_NAME>_LEVEL_<LEVEL_NUMBER>`, or
> - `SLSA_<TRACK NAME>_LEVEL_UNEVALUATED` **if the VSA issuer does not want to make a claim about the track level an artifact meets**, or
> - The SLSA verified property the referenced artifact qualifies for."

Plus `FAILED` ("Indicates policy evaluation failed"). Custom values are permitted but MUST NOT start
with `SLSA_`.

**And the absent-vs-empty rule, `dependencyLevels`, verbatim:**
> "Absence of a given level of SlsaResult MUST be interpreted as reporting *0* dependencies at that
> level. A set but empty `dependencyLevels` object means that the artifact has **no** dependency at all,
> while **an unset or null `dependencyLevels` means that the verifier makes no claims about the
> artifact's dependencies.**"

**Three-way distinction between zero, empty and absent, specified normatively.** This is the same idea
as SPDX's NONE/NOASSERTION (§5.4) and it is a rule we must adopt or we will get it wrong: in our
report, `[]` and `null` must not mean the same thing, and the schema must say which is which.

Also, honestly: *"A VSA does not protect against compromise of the verifier, such as by a malicious
insider."* We inherit that limit exactly.

- **Where this fits:** L7. `verifier.id` (with the explicit recommendation to version the identifier
  when verification logic changes materially), `policy{uri,digest}`, `inputAttestations[]`, and the
  absent-vs-empty rule all map onto our envelope one-for-one.
- **Where it stops:** `UNEVALUATED` is **per-track** — one of two or three coarse buckets. There is no
  per-check granularity and no reason code. `verificationResult` itself remains binary PASSED|FAILED.

### 5.4 SPDX 3.0 — NOASSERTION, and a documented conflation we can improve on

Read raw from `spdx/spdx-3-model` (103★, pushed 2026-08-07; model files carry
`SPDX-License-Identifier: Community-Spec-1.0`). `spdx/spdx-spec` latest release tag **3.0.1, published
2024-12-17**.

**`model/Core/Vocabularies/RelationshipCompleteness.md`, verbatim entries:**
- `incomplete`: "The relationship is known not to be exhaustive."
- `complete`: "The relationship is known to be exhaustive."
- `noAssertion`: "No assertion can be made about the completeness of the relationship."

**`model/Core/Individuals/NoneElement.md`** — "represents a set of Elements with cardinality
(number/count) of **zero**… should be used if the SPDX creator desires to assert that there are NO
elements for the given context of use." Property value `"NONE"`.

**`model/Core/Individuals/NoAssertionElement.md`** — and this is the useful part, verbatim:
> "NoAssertionElement should be used if
> - the SPDX creator has attempted to but cannot reach a reasonable objective determination;
> - the SPDX creator has made no attempt to determine this field; or
> - the SPDX creator has intentionally provided no information (no meaning should be implied by doing so)."
Property value `"NOASSERTION"`.

**SPDX names three distinct causes and then deliberately collapses them into one token.** That is not a
gap in SPDX's thinking — it is a documented decision — but it is precisely the collapse our product
exists to refuse. This is the cleanest single citation for "the state of the art names the distinction
and then throws it away."

- **Where this fits:** L5/L7 vocabulary design. Adopt the NONE-vs-NOASSERTION distinction verbatim in
  spirit; **split** SPDX's three NOASSERTION causes into three of our reason codes (§8:
  `indeterminate.*`, `not_run.*`, and a withheld state).
- **Where it stops:** it is a package/licence data model. There is no verdict, no evidence, no scoring.

### 5.5 OpenSSF Scorecard — the third independent implementation of the same idea

`ossf/scorecard`: 5,624★, 697 forks, **Apache-2.0**, pushed 2026-08-10.

From `checker/check_result.go`, verbatim:
```go
const (
	// MaxResultScore is the best score that can be given by a check.
	MaxResultScore = 10
	// MinResultScore is the worst score that can be given by a check.
	MinResultScore = 0
	// InconclusiveResultScore is returned when no reliable information can be retrieved by a check.
	InconclusiveResultScore = -1
```

From `pkg/scorecard/scorecard_result.go`:
```go
func scoreToString(s float64) string {
	if s == checker.InconclusiveResultScore {
		return "?"          // rendered distinctly in the UI, never as a number
	}
	return fmt.Sprintf("%.1f", s)
}
// ... inside GetAggregateScore:
	// This indicates an inconclusive score.
	if check.Score < checker.MinResultScore {
		continue            // EXCLUDED FROM THE AGGREGATE DENOMINATOR
	}
	total += rs
	score += rs * float64(check.Score)
```

Three properties, all three of which we need: a **distinct sentinel** for "no reliable information can
be retrieved", **exclusion from the aggregate denominator**, and a **distinct rendering (`"?"`)** so it
can never be mistaken for a low score. `docs/checks.md` shows the intended usage in prose too: for
Code-Review, *"If recent changes are solely bot activity… the check returns inconclusively."*

- **Where this fits:** L5 scoring and L7/UX. Together with XCCDF §7.3.2.2 this is the second independent
  confirmation of the denominator rule, and the first confirmation of the rendering rule.
- **Where it stops:** one sentinel value, no reason codes, no per-finding provenance, and — the hazard —
  **silent denominator shrinkage.** Nothing in Scorecard's aggregate tells you how many checks were
  inconclusive. A repo where 8 of 19 checks returned `-1` and a repo where 0 did can print the same
  aggregate. **That failure mode is the exact thing our product must not reproduce**, and it is the
  reason §7's schema requires the residue counts to travel with the fraction.

### 5.6 Sigstore / Rekor — usable, with one privacy landmine

`sigstore/cosign`: 6,198★, Apache-2.0, pushed 2026-08-07. `sigstore/rekor`: 1,189★, Apache-2.0, pushed
2026-08-10, **latest release v1.5.3 published 2026-07-02**. `sigstore/rekor-tiles` (Rekor v2 — *"Signature
Transparency Log designed for ease of use, low cost, and minimal maintenance"*): 47★, Apache-2.0, pushed
2026-08-10. Both actively developed; Rekor v2 is real and moving.

- **Where this fits:** L7 signing and, more interestingly, the **append-only public registry of
  coverage attestations** — the thing that would make "coverage over time" (ARCHITECTURE.md Screen 4)
  a claim a third party can audit rather than a chart we draw.
- **Where it stops, and this is a real design constraint, not a footnote:** Sigstore keyless signing
  binds a **workload/human identity into a public certificate that is published to a public
  transparency log, permanently.** For filings by named FMEs that is a disclosure surface: the *fact*
  and *timing* of a named entity running a pre-submission compliance check becomes world-readable, and
  can be correlated. **Recommendation: do not use the Sigstore public-good instance for filer-side
  attestations.** Use (i) detached key signing over the report (compliance-trestle already implements
  detached signing for JSON), and (ii) if a transparency log is wanted, a **private rekor-tiles
  instance operated by the supervisor**, where the log's audience is already the regulator. Publish
  only salted hashes of filing identifiers. *(This is a design assertion by me, labelled as such; the
  transparency-log-is-public property is a documented Sigstore design property, but I did not open the
  public-good-instance policy page for this file — §9, open question 3.)*

### 5.7 W3C PROV-O and RO-Crate — necessary background, low direct yield

**PROV-O:** *PROV-O: The PROV Ontology*, **W3C Recommendation, 30 April 2013**
(`https://www.w3.org/TR/prov-o/`). Starting-point classes `prov:Entity`, `prov:Activity`, `prov:Agent`;
starting-point properties `wasGeneratedBy`, `wasDerivedFrom`, `wasAttributedTo`, `startedAtTime`,
`used`, `wasInformedBy`, `endedAtTime`, `wasAssociatedWith`, `actedOnBehalfOf`. **On negative or absent
provenance the fetch reports: no such vocabulary exists** — no negation operators, no absence
indicators, no completeness or coverage terms. *(SECONDARY — this is a WebFetch summariser's reading of
the Recommendation, not my own scan of the RDF. It matches my prior understanding of PROV-O, but the
absence claim in particular should be re-run against the OWL file before being quoted adversarially.)*

- **Where this fits:** L0/L2 provenance graph shape, if we ever need RDF interop.
- **Where it stops:** PROV-O describes **what did happen**. It is structurally incapable of expressing
  what did not, except by omission — which is the disease. It is the wrong tool for L7.

**RO-Crate:** `ResearchObject/ro-crate` — 156★, Apache-2.0, pushed 2026-08-10; spec tags up to
**1.3.0** (also 1.2.0, 1.1.x). A JSON-LD packaging convention for describing a directory of data plus
its metadata.
- **Where this fits:** L0 — packaging the evidence bundle (blank template + circular PDFs + register
  snapshots + the filing) as one addressable, described crate.
- **Where it stops:** it is a *packaging and description* convention. No verdicts, no coverage, no
  signing model. I did not open the 1.3.0 spec text for this lane; the version list is from repo tags.

---

## PART 6 — (a) THE VERDICT ON "NO ANALOGUE EXISTS FOR A FINANCIAL ASSERTION"

### 6.1 The claim as written: **REFUTED**

Six independent counter-examples, five of them opened at source:

| # | Prior art | What it declares | Warrant |
|---|---|---|---|
| 1 | **ISA 705 (Revised) ¶24** | Auditor **shall** state the reasons for an inability to obtain sufficient appropriate audit evidence, in an audit report on financial statements | VERIFIED-AT-SOURCE |
| 2 | **ISA 705 ¶¶7(b), 9, 17** | A whole verdict state (**disclaimer**) reserved for "could not check", and the word *possible* distinguishing unexamined from known-bad | VERIFIED-AT-SOURCE |
| 3 | **ISRS 4400 (Revised) ¶30(j)** | Mandatory statement that further procedures might have surfaced further matters — the bounded-silence sentence | VERIFIED-AT-SOURCE |
| 4 | **ISRS 4400 ¶¶30(h),(i), 13(f)** | Explicit disclaimer of the *appropriateness* of the procedure set; no opinion expressed; findings must be objectively verifiable to count | VERIFIED-AT-SOURCE |
| 5 | **XCCDF Table 26 (NISTIR 7275r4, 2012)** | Nine per-item result states incl. `notchecked`, `notselected`, `notapplicable`, `error`, `unknown` — plus §7.3.2.2 denominator rules | VERIFIED-AT-SOURCE |
| 6 | **C2PA 2.4 §15.9.2** | `shall` issue `signingCredential.ocsp.skipped` when a check is deliberately not performed | VERIFIED-AT-SOURCE |

Items 1–4 are *financial*. Items 5–6 are per-item and machine-readable. The claim fails on both axes it
asserts.

### 6.2 The strongest defensible restatement

Write this in place of the current sentence, and it is stronger because it is survivable:

> **The assurance profession already knows how to declare the boundary of what was examined — ISRS 4400
> (Revised) ¶30(j) requires the statement in every agreed-upon-procedures report, and ISA 705 (Revised)
> ¶24 requires the auditor to state the reasons for any inability to obtain evidence. What does not
> exist is a version of that declaration that is (i) *per-item* rather than per-report, (ii)
> *machine-readable* against a closed vocabulary rather than prose, (iii) computed from an
> independently-induced schema rather than negotiated in advance with the engaging party, and (iv)
> carried alongside a *measured error rate for each individual check*. ISRS 4400 ¶30(h) makes the point
> for us: the practitioner expressly makes no representation about whether the procedures were the
> right ones. Our L4 qualification gate is a machine-checked answer to exactly that disclaimed
> question.**

### 6.3 The three things that survive as genuinely novel — and they are enough

1. **The procedure set is derived, not agreed.** In ISRS 4400 the procedures come from the engaging
   party and their adequacy is disclaimed (¶30(h)). Our procedures are synthesised (L3) from the
   regulator's own text and the template's own 294 native formulas, and then qualified (L4). Nothing in
   the assurance standards, and nothing in XCCDF/C2PA/OSCAL, derives the check set from the artifact
   and then measures it.
2. **Each check ships its own measured false-failure rate.** XCCDF has severity; C2PA has
   success/informational/failure; OSCAL has a `confidence` score with a free-text rationale; CycloneDX
   1.6 has `conformance.score` and `confidence.score` in [0,1] with prose. **None of them carries a
   measured error rate for the individual rule, computed against a named corpus with a stated
   denominator.** The L4 admission record (mutation score, degenerate baseline, FFR-on-n-clean) is the
   novel object.
3. **The denominator is induced from the regulator's own published artifact.** XCCDF's denominator is a
   benchmark someone wrote. OSCAL's is a control catalog someone wrote. ISRS 4400's is a list someone
   agreed. Ours is **mechanically recoverable from the blank template** — 6,757 cells, 854 label
   instances, 294 formulas, extracted deterministically (RND-BRIEF §4.3). That is why a `DISALLOW *`
   closure is possible for us and is not possible for any of them.

**The pitch sentence changes from "nobody declares coverage" (false, and a judge may know it) to
"the profession declares it in prose, once, per report, about a procedure set whose adequacy it
disclaims — we declare it per field, in a closed vocabulary, against a denominator we derive from the
regulator's own workbook, with a measured error rate on every check."** That is both true and better.

---

## PART 7 — (b) THE REPORT SCHEMA RECOMMENDATION

Design rule used throughout: **borrow the field, keep the citation.** Every element below traces to a
source in §§1–5. Where I invented something, it says so.

### 7.1 Envelope: DSSE + in-toto Statement, our own predicate type

```jsonc
// DSSE envelope (in-toto Attestation Framework, Apache-2.0) — payloadType "application/vnd.in-toto+json"
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    { "name": "filing",   "digest": { "sha256": "<hash of the filed workbook as received>" } },
    { "name": "template", "digest": { "sha256": "<hash of the published blank template>" } }
  ],
  "predicateType": "https://<ns>/filing-coverage-attestation/v1",
  "predicate": { /* §7.2 */ }
}
```
Why in-toto/DSSE rather than JSF (CycloneDX) or bare JWS: it is Apache-2.0, it is what cosign,
SLSA VSA and the whole attestation ecosystem already speak, and `subject[]` naturally carries the
**two** hashes we must bind — the filing *and* the template it was judged against. Binding the template
hash is not optional: a verdict against template v3 is meaningless if the entity filed on v4.

### 7.2 The predicate body

```jsonc
{
  // ── WHO AND WITH WHAT ────────────────────────────────────────────────────
  // from SLSA VSA verifier{} + CycloneDX 1.6 declarations.assessors[]
  "assessor": {
    "id": "https://<ns>/verifier/v3.2.1",     // SLSA: version the id when logic changes materially
    "thirdParty": false,                       // CycloneDX: false == self-assessor. Mandatory honesty.
    "components": {                            // OSCAL assessment-assets
      "predicateSetVersion": "3.2.1",
      "predicateSetDigest": { "sha256": "..." },
      "schemaInducerVersion": "1.4.0",
      "extractorModel": "…@2026-07-11"         // null when no model ran (the 2-day build: always null)
    }
  },
  "timeVerified": "2026-08-10T09:12:44Z",
  "expires": "2026-11-10T00:00:00Z",           // OSCAL observation.expires / CycloneDX evidence.expires
  "specVersion": "1.0.0",                      // C2PA: version of the checking apparatus's contract

  // ── WHAT WAS IN SCOPE, AND WHAT WAS TAKEN OUT ────────────────────────────
  // from OSCAL reviewed-controls (include-all/include/exclude, planned vs actual)
  "scope": {
    "denominator": {
      "source": "induced-from-template",       // NOT negotiated. This is the novelty (§6.3.3).
      "fieldsTotal": 854,
      "obligationsTotal": 41,
      "pairsTotal": 1187                       // the closed universe; DISALLOW * applies to it
    },
    "plannedSelection": { "includeAll": true, "exclude": [ /* selector + reason code */ ] },
    "actualSelection":  { "includeAll": true, "exclude": [ /* … */ ] },
    "selectionDelta": [ /* OSCAL: results must show changes from the plan */ ]
  },

  // ── THE ITEMS ────────────────────────────────────────────────────────────
  "items": [
    {
      "id": "sheet2!C14×reg27(1)",
      "pointer": "/report/sheets/2/cells/C14",  // CycloneDX 1.7 citation: RFC 6901 JSON Pointer
      "obligation": {                            // CycloneDX definitions.standard.requirement
        "standard": "IFSCA (Fund Management) Regulations 2025 (as amended to 30 Jan 2026)",
        "identifier": "reg 27(1)",
        "sourceDigest": { "sha256": "..." }      // the exact PDF the clause was read from
      },
      "predicate": { "id": "P-0117", "version": "2", "digest": { "sha256": "..." } },
      "method": "RECOMPUTE",                     // §7.4 — extends OSCAL observation.methods
      "state": "PASS",                           // §8.1 — closed, 7 values
      "reason": null,                            // §8.2 — closed, required iff state != PASS/FAIL
      "provenance": "COMPUTED",                  // C2PA created_ vs gathered_ assertions
      "warrant": "MEASURED",                     // the operator's own label discipline, per item
      "qualification": {                         // ← the genuinely novel object (§6.3.2)
        "mutationScore": { "killed": 31, "mutants": 40, "equivalent": 3, "value": 0.8378 },
        "falseFailureRate": { "fired": 7, "cleanCorpusN": 340, "value": 0.0206,
                              "corpusId": "synthetic-clean-v2",
                              "corpusIsSynthetic": true },     // ARCHITECTURE.md risk 2, in the schema
        "degenerateBaselineBeaten": true,
        "admittedOn": "2026-07-02"
      },
      "override": null                           // XCCDF Table 27, §7.5
    }
  ],

  // ── WHAT ARGUES AGAINST US ───────────────────────────────────────────────
  // PCAOB AS 1215 .08 + CycloneDX counterClaims/counterEvidence. New to this design.
  "counterEvidence": [
    { "kind": "rejected-predicate", "obligation": "reg 51(1)", "predicateId": "P-0203",
      "rejectedBy": "L4-test-3", "measured": { "ffr": 0.41, "cleanCorpusN": 340 },
      "note": "would have covered 6 further pairs; rejected on false-failure rate" }
  ],

  // ── THE ARITHMETIC, WITH ITS DENOMINATORS ────────────────────────────────
  "coverage": { /* §7.3 */ },

  // ── THE AGGREGATE VERDICT ────────────────────────────────────────────────
  "verdict": { /* §7.6 */ },

  // ── THE SENTENCE THAT MAY NOT BE REMOVED ─────────────────────────────────
  // ISRS 4400 (Revised) ¶30(j), made a required schema field rather than a report convention
  "boundedSilenceStatement":
    "Had additional predicates been executed, other matters might have been reported. This report
     states only the results of the predicates listed, and makes no representation that the predicate
     set is sufficient for any purpose.",
  "purposeStatement":                            // ISRS 4400 ¶30(d) + ¶A52
    "This report relates only to the fields enumerated in scope.denominator and does not extend to the
     filing taken as a whole.",
  "summaryIsNotSubstitute": true                 // ISRS 4400 ¶32(b)
}
```

`boundedSilenceStatement`, `purposeStatement` and `summaryIsNotSubstitute` are **required by schema**.
Making the disclaimer a mandatory field rather than a template string is the cheapest possible way to
guarantee it survives contact with a marketing page.

### 7.3 The coverage object — never a bare fraction

```jsonc
"coverage": {
  "pairsTotal": 1187,
  "outOfScope": 214,                 // removed from denominator (XCCDF §7.3.2.2)
  "inScope": 973,                    // = pairsTotal - outOfScope   ← THE denominator
  "settled":  { "pass": 611, "fail": 12, "total": 623 },
  "unsettled": {                     // KEPT in the denominator
    "indeterminate": 41,
    "notRun":        88,
    "noPredicate":   221
  },
  "coverageFraction": 0.6402,        // 623 / 973 — meaningless without the four counts above
  "aggregate": "incomplete",         // CycloneDX compositions.aggregate, as a roll-up header
  "denominatorWarning":              // XCCDF §7.3.2.3, in the payload
    "The denominator varies between filings because out-of-scope determinations are filing-specific.
     Coverage fractions are not directly comparable across filings."
}
```

**Divergence from XCCDF, stated deliberately.** XCCDF removes `notchecked` (no check exists) from its
denominator. **We keep `noPredicate` in.** Reason: XCCDF's denominator is a benchmark a human authored,
so "no check exists" means the author chose not to have one. **Our denominator is induced from the
regulator's own template, which is authoritative and complete — so "no predicate exists" is a gap in
*us*, not in the specification.** Removing it would let the product's coverage rise by doing nothing.
This divergence is the single most important scoring decision in the design and it should be written
into the spec text with this justification attached.

Anti-gaming invariant, enforced at report-generation time:
```
outOfScope + settled.total + indeterminate + notRun + noPredicate == pairsTotal
```
This is the in-toto `DISALLOW *`. Any pair that does not land in exactly one bucket is a **hard error**,
not a silent omission. (§5.2.)

Absent-vs-empty rule, adopted verbatim in spirit from SLSA and SPDX: **`[]` means "we determined there
are none"; `null`/absent means "we make no claim."** The schema must never allow both to be omitted
interchangeably.

### 7.4 `method` — extending OSCAL's observation methods to document verification

OSCAL gives `["EXAMINE","INTERVIEW","TEST","UNKNOWN"]` (open via `anyOf`). Neither `EXAMINE` nor `TEST`
distinguishes the things that matter to us. Proposed closed extension, each value naming a distinct
epistemic basis:

| Method | Meaning | Maps to |
|---|---|---|
| `RECOMPUTE` | the value was recomputed from other cells in the filing and compared | the 35 SUM identities + 3 COUNTIFs |
| `TIE_OUT` | a cross-sheet carry was compared against its source cell | the 181 carry-forward formulas |
| `SCHEMA_BIND` | the value conforms to the induced schema (type, vocabulary, format) | 35 data validations, 3 list-type |
| `REGISTER_LOOKUP` | resolved against a live external register | reg no. / scheme no. resolution |
| `CLAUSE_TEST` | an L3-synthesised predicate implementing a specific clause | the L3/L4 output |
| `METAMORPHIC` | a relation between two runs was checked; no absolute oracle used | L6 |
| `MODEL_EXTRACT` | a value was bound to a key by a model, then schema-validated | L2 (never alone) |
| `UNKNOWN` | retained from OSCAL for projection fidelity | — |

Rule: **`MODEL_EXTRACT` may never be the sole method on a `PASS`.** Encoding ARCHITECTURE.md fact #3
("a model may never be the final judge") as a schema constraint rather than a coding convention.

### 7.5 `override` — XCCDF Table 27, adopted unchanged

```jsonc
"override": { "oldState": "FAIL", "newState": "PASS",
              "remark": "Rounding convention agreed with IFSCA on 2026-05-04; see letter <digest>.",
              "actor": { "type": "party", "id": "..." }, "time": "2026-08-10T10:02:00Z" }
```
Both states are retained; the override is inside the signed payload. An overridden item is counted
under its **new** state in `coverage`, and the override count is reported separately. Overrides are a
first-class number a supervisor will want.

### 7.6 The aggregate verdict — ISA 705's 2×2, made deterministic

The architecture currently has no aggregation rule. Proposed, and explicitly a **declared policy in the
shape of ISA 705**, not a claim to implement it:

```
residueIsConfined  :=  (unsettled pairs touch ≤ K distinct sheets)
                       AND (no unsettled pair is flagged material-by-policy)
                       AND (unsettled / inScope ≤ T)
```
`K`, `T` and the material-by-policy field list are **published, versioned parameters**, carried in the
attestation, not constants in code.

| | residue confined | residue pervasive |
|---|---|---|
| **failures present** (settled.fail > 0) | `EXCEPTIONS_NOTED` *(≈ qualified)* | `ADVERSE` |
| **no failures, unsettled residue** | `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` *(≈ qualified for scope)* | **`COVERAGE_INSUFFICIENT`** *(≈ disclaimer)* |

Three consequences taken directly from ISA 705, and all three matter:
- **There is no state whose name means "clean."** The best available verdict is
  `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE` — which cannot be quoted out of context without
  carrying its own qualifier. This delivers ARCHITECTURE.md's "no green tick" by **naming**, which is
  far more robust than by **iconography**. An icon can be screenshotted; a name travels.
- **The heading changes with the residue** (¶20(a)): the report's own title string is a function of the
  verdict state, not a fixed "Coverage Report".
- **When `COVERAGE_INSUFFICIENT`, the report must not describe itself as having verified the filing**
  (¶19(c)) — the wording flips from "this filing was checked against N predicates" to "this filing was
  *submitted for* checking against N predicates; coverage was insufficient to report."

### 7.7 What we emit, in what order

| Artifact | Format | Normative? | Why |
|---|---|---|---|
| Coverage attestation | DSSE + in-toto Statement, §7.2 | **yes** | the only complete representation |
| OSCAL Assessment Results projection | OSCAL AR v1.2.3 JSON | no — **declared lossy** (§3.3) | GRC interop; free via `compliance-trestle` |
| OSCAL POA&M | OSCAL POA&M v1.2.3 JSON | no | the Unchecked panel + "what would make it checkable" |
| Human report | HTML | no | the two screens; must render §7.3's four counts, never the fraction alone |
| Evidence crate | RO-Crate 1.3.0 | no | template + circulars + register snapshots, addressable |

---

## PART 8 — (c) THE CLOSED VOCABULARY, IMPROVED ON THE BRIEF'S SIX

### 8.1 First, split one axis into two

ARCHITECTURE.md L5 has one axis: `PASS / FAIL / UNCHECKED(reason)` with six reasons —
*no oracle exists · requires counterparty data · requires judgment · source unreadable · rule ambiguous ·
predicate not yet synthesised.*

Four defects, each traceable to a source above:
1. **No `notapplicable`.** On a 10-sheet workbook filed by 217 heterogeneous FMEs, whole sheets
   legitimately do not apply. Without this the denominator is wrong on every real filing. (XCCDF)
2. **No `notselected`.** A supervisor triaging 868 filings/year will run targeted subsets. Excluded-by-
   profile is not the same as no-predicate-exists. (XCCDF)
3. **No runtime-error state.** "The register was down" and "no predicate exists for this clause" have
   opposite remedies — retry vs write code — and the brief's vocabulary cannot distinguish them.
   (XCCDF `error`; C2PA `inaccessible`)
4. **"no oracle exists" and "requires judgment" overlap almost totally** — both describe RND-BRIEF
   §4.3's seven undecidables — while the operationally distinct case, *a predicate was written and L4
   rejected it*, has no state at all. That is the most honest state the system can emit and the
   vocabulary omits it.

**Proposed state axis — 7 values, closed:**

| State | Meaning | In coverage denominator? | Source |
|---|---|:--:|---|
| `PASS` | predicate ran, condition held | ✅ settled | XCCDF `pass` |
| `FAIL` | predicate ran, condition did not hold | ✅ settled | XCCDF `fail` |
| `INDETERMINATE` | predicate ran to completion, result not decidable | ✅ | XCCDF `unknown` |
| `NOT_RUN` | predicate is admitted and in scope, but did not execute | ✅ | XCCDF `error`; C2PA `inaccessible`/`skipped` |
| `NO_PREDICATE` | field×obligation in scope, no admitted predicate covers it | ✅ *(divergence, §7.3)* | XCCDF `notchecked` |
| `OUT_OF_SCOPE` | does not apply to this filing, or excluded by this run's profile | ❌ removed | XCCDF `notapplicable`/`notselected` |
| `INFORMATIONAL` | predicate ran; output is a value for the reader, not a verdict | ❌ removed | XCCDF `informational` |

Orthogonal, not a state: **`override`** (§7.5). XCCDF got this right — an override changes the result
and is recorded beside it; it is not a seventh result value.

### 8.2 The reason vocabulary — closed, namespaced, 19 codes

**Admission test for a reason code, and it should be written into the spec:**
> *Two reasons are distinct if and only if they imply different remedies.* If the operator's next action
> is the same, the codes merge.

That test is why 19 beats 6 and also why it is not 40.

**`NO_PREDICATE.*` — we have no check. The honest core; this is the backlog.**

| Code | Meaning | Remedy |
|---|---|---|
| `no_predicate.undecidable_by_construction` | "correct" is not defined for this obligation (Third Schedule Part A(g) valuation appropriateness; whether a scheme is properly classified "infrastructure") | none — this is the permanent floor; report it forever |
| `no_predicate.requires_judgment` | a competent human can decide; no program can (reg 119(3)(e) rationale adequacy; complaint resolved satisfactorily) | route to a human; never auto-close |
| `no_predicate.not_yet_synthesised` | decidable in principle, nobody has written it | **L3 backlog — the growable set; this is the coverage-over-time story** |
| `no_predicate.failed_qualification` | a predicate **was** written and **L4 rejected it** — carry the rejecting test and the measured number | improve the predicate, or accept the gap knowingly |
| `no_predicate.rule_ambiguous` | the obligation text does not determine a testable condition (e.g. reg 51(1) ends "in such manner as specified by the Authority" — a live delegation hook with nothing yet specified) | ask the regulator; §9.6 of the brief |

`no_predicate.failed_qualification` is new, and it is the state that makes the Predicate Library screen
honest: it is where L4's rejections become visible instead of being discarded. It is also the natural
home for PCAOB AS 1215 .08 counter-evidence.

**`NOT_RUN.*` — we have a check; it did not run. Every one of these is an ops or data problem.**

| Code | Meaning |
|---|---|
| `not_run.input_unavailable.counterparty` | needs data held by a party who is not the filer (look-through into schemes the FME does not manage) |
| `not_run.input_unavailable.register` | live register unreachable, rate-limited, or ambiguous at run time |
| `not_run.input_unavailable.prior_period` | needs a filing we do not hold |
| `not_run.source_unreadable` | the artifact or a region of it could not be parsed (scanned image, corruption, protection) |
| `not_run.template_unbound` | L1 could not bind the filing to a published template hash — **the whole run is suspect; this should escalate** |
| `not_run.predicate_error` | the predicate raised at runtime (XCCDF `error`) |
| `not_run.deactivated` | an admitted predicate deliberately switched off for this run, with a pointer to the decision record (C2PA `ocsp.skipped`) |
| `not_run.budget_exhausted` | time or cost limit hit before this pair was reached |

`not_run.deactivated` is the C2PA lesson: skipping is sometimes legitimate, and the moment it is
legitimate the report **must** be able to say so, or the skip becomes silent. Ours will arise the first
time a predicate's FFR is found unacceptable in production and someone switches it off mid-quarter.

**`INDETERMINATE.*` — the check ran and could not decide.**

| Code | Meaning |
|---|---|
| `indeterminate.extraction_abstained` | L2 conformal prediction set was not a singleton — the designed abstention |
| `indeterminate.tolerance_straddle` | the result falls inside the rounding/tolerance band where both answers are admissible (RND-BRIEF §3.2: the 21-point recall loss lives here — **now it has a name instead of being absorbed into a threshold**) |
| `indeterminate.conflicting_sources` | two admitted sources disagree and no tie-break rule is published |

**`OUT_OF_SCOPE.*` — removed from the denominator, therefore the most abusable; require a machine-checkable justification for each.**

| Code | Meaning | Justification required |
|---|---|---|
| `out_of_scope.not_applicable` | field/sheet does not apply to this entity or scheme type | a pointer to the schema condition that makes it inapplicable |
| `out_of_scope.not_selected` | excluded by this run's profile | a pointer to the named profile and its digest |
| `out_of_scope.withheld` | the operator intentionally provides no information (SPDX's third NOASSERTION cause) | an actor + rationale; **counted and displayed separately, never folded into `not_applicable`** |

Total: 5 + 8 + 3 + 3 = **19 codes across 4 non-settled states**, versus the brief's 6 flat reasons.
Mapping from the brief so nothing is lost:

| Brief's reason | Becomes |
|---|---|
| no oracle exists | `no_predicate.undecidable_by_construction` |
| requires counterparty data | `not_run.input_unavailable.counterparty` |
| requires judgment | `no_predicate.requires_judgment` |
| source unreadable | `not_run.source_unreadable` |
| rule ambiguous | `no_predicate.rule_ambiguous` |
| predicate not yet synthesised | `no_predicate.not_yet_synthesised` |

The other 13 are new, and 12 of the 13 come straight out of XCCDF, C2PA, SPDX or SLSA rather than
being invented here.

### 8.3 Two structural rules that come with the vocabulary

1. **NONE ≠ NOASSERTION ≠ absent** (SPDX; SLSA `dependencyLevels`). `[]` = "we determined there are
   none". `null` = "we make no claim". Field omitted = **schema violation**. All three must be
   distinguishable in the JSON Schema, and the third must be rejected by the validator.
2. **Closure is enforced, not documented** (in-toto `DISALLOW *`). The invariant in §7.3 runs at report
   generation. A pair that lands in no bucket aborts the report. Coverage is then true by construction —
   the same move L4 makes for error rates, applied to the state space.

---

## PART 9 — WHAT I COULD NOT CHECK

Stated in the form the product itself would use.

| # | Item | State | Reason code (using §8.2) | What would settle it |
|---|---|---|---|---|
| 1 | ISAE 3402 / SSAE 18 AT-C 320 carve-out vs inclusive method — exact definitions and reporting requirements | UNVERIFIED | `not_run.input_unavailable.register` | Open the IAASB Handbook Vol. 2 or a purchased AICPA Professional Standards copy. 8 URL patterns tried and logged in §4.4; positive control (ISRS 4400 from the same host) passed, so the failures are wrong paths, **not evidence of absence** |
| 2 | ISA 600 (Revised) component scoping; ISA 320 materiality; ISA 200/315/330 sufficient appropriate evidence | NOT CHECKED | `not_run.budget_exhausted` | IRBA hosts ISA 705 under `ISA-705-Revised.pdf`; find the equivalent filenames. ISA 600's component-scoping mechanics are the closest analogue to portfolio-level coverage and are the highest-value remaining gap |
| 3 | Sigstore public-good-instance policy on what may be logged, retention, and identity disclosure | UNVERIFIED | `not_run.input_unavailable.register` | Open `docs.sigstore.dev` public-good-instance policy. My §5.6 recommendation against using it for filer-side attestations rests on the general transparency-log design property, not on that page |
| 4 | Whether EBA / ESMA / EIOPA publish a list of **deactivated** validation rules | UNVERIFIED | `not_run.input_unavailable.register` | `eba.europa.eu` root returns 200; the two specific paths I tried returned 404 (site restructured). **I searched the wrong paths; I did not search the corpus.** No absence may be claimed. This is the single most on-point regulatory-reporting precedent still unchecked, because a published deactivated-rule list is literally `not_run.deactivated` at supervisory scale |
| 5 | PROV-O's absence of negative-provenance vocabulary | SECONDARY | `indeterminate.extraction_abstained` | Scan the OWL file directly rather than relying on the WebFetch summariser |
| 6 | RO-Crate 1.3.0 spec text | NOT CHECKED | `not_run.budget_exhausted` | Version list is from repo tags only; I did not open the spec |
| 7 | Whether IFSCA already runs these checks on receipt | NOT CHECKED | — | RND-BRIEF §9.6 already queues this. It also determines whether §7.7's OSCAL projection has a consumer |

---

## What this changes about the design

**1. The L7 sentence must be rewritten today.** "No analogue exists for a financial assertion" is
refuted by ISA 705 ¶24 and ISRS 4400 ¶30(j), both of which a judge with an audit background may know.
Replace with §6.2. The replacement is stronger, not weaker: it names four specific properties nobody
has, instead of one general absence that is false.

**2. `compositions.aggregate` is demoted from "the prior art" to "one header field."** The real
per-item prior art is **XCCDF Table 26 (NIST, 2012, nine states)**, and the real evidence that binary is
insufficient in production is **C2PA deprecating its own `success: bool` in favour of
success/informational/failure in v2.1**. Cite those. Also correct the factual error: the enum appeared
in CycloneDX **1.3 with six states**, not 1.2 with ten.

**3. L5 gains a state axis and loses a flat reason list.** 7 states (§8.1) × 19 namespaced reasons
(§8.2), replacing PASS/FAIL/UNCHECKED × 6. The four states this adds that the brief cannot express —
`OUT_OF_SCOPE`, `INFORMATIONAL`, `INDETERMINATE`, and the `no_predicate.failed_qualification` reason —
are not refinements. Without `OUT_OF_SCOPE` **the coverage fraction is computed against the wrong
denominator on every real filing**, because 217 heterogeneous FMEs will not populate all 10 sheets.

**4. L5 gains the aggregation rule it did not have.** ISA 705's 2×2 (§7.6). Per-item states were never
composed into a document-level verdict anywhere in ARCHITECTURE.md. Now they are, by a **published,
versioned, deterministic pervasiveness policy** carried inside the attestation.

**5. "No green tick" is implemented by naming, not by iconography.** The best available verdict is
literally called `EXCEPTIONS_NOT_NOTED_WITHIN_STATED_COVERAGE`. A missing icon can be worked around by
a screenshot; a name travels with the claim. This is a strictly stronger version of the same commitment
and it costs nothing.

**6. The coverage meter must never ship as a single number.** XCCDF wrote the warning into its own
normative text in 2012 (*"scores… may not be directly comparable because the maximum score can vary"*),
and OpenSSF Scorecard demonstrates the failure mode live — its aggregate silently drops inconclusive
checks, so 8-of-19-inconclusive and 0-of-19-inconclusive print the same score. **Screen 2's headline
becomes the four residue counts plus the fraction, with the fraction subordinate.** And Scorecard's
`"?"` rendering is the right precedent: an inconclusive result must never render as a number.

**7. Closure becomes an enforced invariant, not a discipline.** in-toto's `DISALLOW *` warning is the
architectural insight of the lane: our L1-induced schema *is* a signed layout enumerating the universe,
so any pair not landing in exactly one bucket must **abort report generation**. This makes the coverage
claim true by construction in the same way L4 makes the error-rate claim true by construction — and it
is the second load-bearing use of the same move, which is a good sign about the design.

**8. Three fields we did not have and now must:** `expires` (evidence goes stale — OSCAL, CycloneDX
1.6, C2PA all have it), `counterEvidence` (PCAOB AS 1215 .08 makes documenting what contradicts your
conclusion **mandatory** — we were going to discard L4's rejected predicates, which is exactly that
information), and `assessor.thirdParty: false` (CycloneDX — we are a self-assessment tool and saying so
is required honesty, especially to a supervisor).

**9. The two-day build gets a report format for free, and a licence-clean one.** OSCAL is **CC0 1.0 /
worldwide public domain**, v1.2.3 released 2026-08-07, and `compliance-trestle` (Apache-2.0, Python,
v5.0.0 released 2026-08-07) already ships pydantic models for assessment-results, assessment-plan,
POA&M and component **plus detached JSON signing**. Adopt for the projection and the signer. Do **not**
adopt OSCAL as the normative model: its `finding-target.status.state` is a closed two-value enum, which
is precisely the one field the entire product exists to add a third value to. §3.3 gives the projection
rule and states the loss.

**10. The Unchecked panel is an OSCAL POA&M.** "Reason + what would make it checkable" is exactly
`poam-item` + `risk.response.lifecycle ∈ {recommendation, planned, completed}`. Do not invent a data
model for Screen 2's differentiator; there is a public-domain one with a Python writer.

**11. Sigstore keyless is the wrong default for filer-side attestations.** Signing identity lands in a
permanent public transparency log; the *fact* that a named FME ran a pre-submission check becomes
world-readable and correlatable. Use detached key signing (trestle has it) plus, if a log is wanted, a
**private rekor-tiles instance operated by the supervisor** — whose audience is already the regulator.
(§9 item 3: my justification is the general design property, not a policy page I opened.)

**12. Where the novelty actually is, and it is defensible.** ISRS 4400 ¶30(h) requires the practitioner
to state that they **make no representation regarding the appropriateness of the agreed-upon
procedures.** The profession's most coverage-honest report form disclaims the one question our L4
qualification gate answers with a number. **That single sentence is the best framing available for this
project**, it comes from the standard that is otherwise our closest competitor, and it should be on the
slide: *the profession declares which procedures it ran and disclaims whether they were the right ones;
we declare which predicates ran, and publish a measured error rate for each.*
