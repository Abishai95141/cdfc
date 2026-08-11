export const meta = {
  name: 'gift-clean-verdict-rnd',
  description: 'Deep research, claim validation, and architecture design for the GIFT IFIH clean-verdict verification system',
  phases: [
    { title: 'Survey', detail: '14 parallel research lanes: papers, OSS, regulatory rules-as-code, oracle-free testing, stacks' },
    { title: 'Verify', detail: 'adversarial refutation of load-bearing claims at primary source' },
    { title: 'Synthesis', detail: 'problem+architecture, technology stack, build path' },
    { title: 'Reconcile', detail: 'contradiction hunt across all lanes and drafts' },
  ],
}

const LDIR = '/Users/abishaikc/Gift/research/lanes'
const SDIR = '/Users/abishaikc/Gift/research/synthesis'
const BRIEF = '/Users/abishaikc/Thinking/gift-ifsc-ground/RND-BRIEF.md'
const ARCH = '/Users/abishaikc/Thinking/gift-ifsc-ground/ARCHITECTURE.md'

const PRE = `You are one research lane in a deep R&D program.

FIRST, use the Read tool on these two files (they are the authoritative context; do not proceed without reading them):
- ${BRIEF}  (the R&D brief: problem, evidence base, proposed 8-layer solution, what has been killed, the experiment queue)
- ${ARCH}   (the 8-layer architecture in full)

The program is building a system that can say "this regulated financial filing is CLEAN" while DECLARING the boundary of what it actually checked - instead of returning a silent all-clear. Primary artifact class: IFSCA (GIFT City) prescribed reporting workbooks for Fund Management Entities. Real copies are on disk at /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/ and a python env with openpyxl+lxml is at /Users/abishaikc/Gift/.venv/bin/python .

Today is 10 August 2026. Your training data ends earlier, so ANYTHING dated after early 2026 must be checked live. Load web tools FIRST with ToolSearch, query: "select:WebSearch,WebFetch". Use them heavily - 15-30 searches/fetches is a normal lane.

NON-NEGOTIABLE RULES:
1. Never invent a URL, an arXiv ID, a star count, a version number, a licence, or a statistic. If you cannot confirm it, output NOT-FOUND or UNVERIFIED. "Could not check" is a legitimate and required answer.
2. Before reporting an absence ("nobody does X"), run a positive control and state exactly which corpus/interface you searched. A search box is not the corpus it searches.
3. Label every claim: VERIFIED-AT-SOURCE (you opened the primary source) / SECONDARY (a credible source describes it) / UNVERIFIED.
4. Quote numbers with their denominators. A derived number never claims a stronger warrant than its weakest input.
5. Prefer primary sources: the paper PDF, the GitHub repo, the regulator's own page, the licence file.

YOUR LANE:
`

const POST = (key) => `

DELIVERABLE - two parts, both required:
(a) Write your COMPLETE findings to ${LDIR}/${key}.md with the Write tool. Long and detailed: URLs, exact quotes, numbers with denominators, code sketches where useful, and for every asset an explicit "where this fits in the L0-L7 architecture" note plus "where it stops". Include a short section titled "## What this changes about the design".
(b) Return the structured summary object. The FILE is the real output; the summary is only the index.`

const LANE_SCHEMA = {
  type: 'object',
  required: ['lane', 'file', 'headline', 'corrections', 'reusable', 'open_questions'],
  properties: {
    lane: { type: 'string' },
    file: { type: 'string' },
    headline: {
      type: 'array',
      description: '5-12 most important findings',
      items: {
        type: 'object',
        required: ['claim', 'warrant', 'impact'],
        properties: {
          claim: { type: 'string' },
          warrant: { type: 'string', enum: ['VERIFIED-AT-SOURCE', 'SECONDARY', 'UNVERIFIED'] },
          source: { type: 'string' },
          impact: { type: 'string', description: 'what it changes about the design' },
        },
      },
    },
    corrections: {
      type: 'array',
      description: 'claims in the brief or architecture that your research confirms, qualifies or refutes',
      items: {
        type: 'object',
        required: ['brief_claim', 'status', 'evidence'],
        properties: {
          brief_claim: { type: 'string' },
          status: { type: 'string', enum: ['CONFIRMED', 'QUALIFIED', 'REFUTED', 'UNVERIFIABLE'] },
          evidence: { type: 'string' },
          restatement: { type: 'string', description: 'the strongest defensible restatement' },
        },
      },
    },
    reusable: {
      type: 'array',
      description: 'concrete assets we can leverage: repos, standards, datasets, papers-with-code',
      items: {
        type: 'object',
        required: ['name', 'fits', 'verdict', 'why'],
        properties: {
          name: { type: 'string' },
          url: { type: 'string' },
          license: { type: 'string' },
          activity: { type: 'string' },
          fits: { type: 'string', description: 'which layer L0-L7 or which build task' },
          verdict: { type: 'string', enum: ['ADOPT', 'EVALUATE', 'REJECT'] },
          why: { type: 'string' },
        },
      },
    },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
}

const VERIFY_SCHEMA = {
  type: 'object',
  required: ['lane', 'verdicts'],
  properties: {
    lane: { type: 'string' },
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        required: ['claim', 'verdict', 'evidence'],
        properties: {
          claim: { type: 'string' },
          verdict: { type: 'string', enum: ['CONFIRMED', 'QUALIFIED', 'REFUTED', 'UNVERIFIABLE'] },
          evidence: { type: 'string' },
          correction: { type: 'string' },
        },
      },
    },
    damage_assessment: { type: 'string', description: 'if the refuted claims are true, what breaks in the design' },
  },
}

const LANES = [
  {
    key: 'L01-arxiv-2026-ids',
    verify: true,
    label: 'papers:2026-ids',
    body: `Verify four arXiv identifiers that reached the brief from an unverified research agent and have never been personally opened. Several carry 2026 IDs. Treat them as suspect until resolved.

- arXiv:2606.09863 - attributed: 45-48% of agent failures in single-control domains are FALSE SUCCESSES; 75.8% on AppWorld; an LLM judge detects false success at AUROC <=0.65 with 13% recall at a 10% flag rate; TF-IDF + XGBoost over the same trajectories gets 0.825-0.953 AUROC, 72% recall, 3,300x faster.
- arXiv:2606.03031 - attributed: "AUDITFLOW", 82.09% -> 17.91% on ablation of the deterministic layer, n=67.
- arXiv:2605.18812 - attributed: "PASC: Pipeline-Aware Conformal Prediction", joint coverage guarantees for multi-stage information-extraction pipelines, names financial documents as a target.
- arXiv:2603.21172 - attributed: "Entropy Alone is Insufficient for Safe Selective Prediction".

For EACH: (1) does the identifier resolve on arxiv.org - fetch https://arxiv.org/abs/<id> and report the ACTUAL title, authors, date, abstract; (2) do the attributed numbers appear in the actual paper, with what denominators; (3) verdict VERIFIED / MISMATCHED-ID / NOT-FOUND.
For every NOT-FOUND or MISMATCHED: search independently for the CLAIMED RESULT (by its distinctive numbers and phrasing) and find the closest REAL published work that supports or contradicts it, so the brief can be repaired rather than merely emptied. For false-success/silent-failure detection in agents look for real work on agent trajectory failure attribution and LLM-judge reliability; for deterministic-checker ablations in audit look for real audit-agent papers; for conformal-in-pipelines look for real multi-stage conformal work.
Also sanity-check the arXiv ID grammar itself: is a 2606.xxxxx identifier even possible given today's date, and does arXiv numbering support the specific sequence numbers quoted?`,
  },
  {
    key: 'L02-papers-and-benchmarks',
    verify: true,
    label: 'papers:benchmarks',
    body: `Verify the rest of the evidence base - identifiers, titles, numbers and denominators.

Numbered, claimed VERIFIED by the operator (re-check anyway, cheaply): arXiv:2401.03038 (SPADE), arXiv:2406.12045 (tau-bench pass^k about 60% at k=1 to about 25% at k=8), arXiv:2102.11378 (Practical Mutation Testing at Scale, Google), arXiv:2202.01602 (Krishna et al., Disagreement Problem in Explainable ML).

Named but UNNUMBERED - find the actual paper or declare NOT-FOUND. These carry load:
- "9 of 14 complete frontier-model runs raise an error on at least 95.3% of 43 CLEAN financial statements" - find the study, the model list, the definition of clean, the denominator.
- The contract-discrepancy benchmark: best model F1 65.4 on a roughly 49.5%-positive set, no constant baseline reported. Find it; verify the flag-everything baseline arithmetic (a constant-positive classifier on a 49.5%-positive set has precision 0.495, recall 1.0, F1 = 2*0.495/1.495 = 0.662). State whether that arithmetic is right.
- "FinVerBench" - rule verifier, 0% false alarms, misses 47%.
- "FinBalance" - ledger feedback WORSENED inconsistency detection by 13-52pp.
- "AgentAbstain" - best paired accuracy 59.5% across 263 pairs / 42 environments / 17 models; reasoning fine-tuning makes abstention 24% worse.
- The checklist to 100% FPR result; the deterministic-rules 0% FPR at 53% recall result; the rounding-tolerance 21-point recall loss.
- "Adding memory made all 10 models worse at long horizons."
- CMU TheAgentCompany (175 tasks, best agent 30% autonomous, Finance lowest category).
- Vals AI Finance Agent v2 (927 questions, 26 models, 58.63% accuracy, 47.71% all-pass, Financial Modeling 34.14%).
- MIT NANDA GenAI Divide (60% investigated, 20% piloted, 5% implemented).
- Cambridge CCAF 2026 (628 respondents, 151 jurisdictions, 52%/23%/55%/43%/53%).
- PCAOB 2024 inspection: 20% of inspected Big Four audits lacked sufficient appropriate evidence (down from 26%).
- The airline benchmark found to contain 75+ task defects.

For each: real or not, exact numbers, exact denominators, and whether the brief's paraphrase is faithful. Flag any number the brief states more strongly than its source supports.`,
  },
  {
    key: 'L03-assertion-oracle-synthesis',
    verify: false,
    label: 'lit:assertion-synthesis',
    body: `The literature on getting a machine to WRITE a correct executable check. This decides whether layer L3 (model synthesises executable predicates from statutory text) is supported by anything measured, or is pure hope.

Cover thoroughly, with real numbers:
- SPADE (Shankar/Parameswaran et al., arXiv:2401.03038, PVLDB 17). Read the actual paper. What is the algorithm exactly? How does it generate candidate assertions, how does it select a minimal set, how does it model false-failure-rate interaction? Is there open-source code (search github for spade assertions and for the LangSmith integration)? What did it NOT solve?
- EvalGen / "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences" (Shankar et al., UIST 2024) - the criteria-drift finding. This is the direct successor and it matters: it says assertion criteria are not stable even for humans. Get the finding exactly.
- DocETL, LOTUS, Palimpzest, Aryn - LLM-powered data processing with validation/optimisation. Which are open source, which have agentic rewrite plus validation loops we can reuse.
- LLM test-oracle generation, the closest measured analogue to L3: TOGA (Dinella et al., ICSE 2022) AND its critique ("Assessing Evaluation Metrics for Neural Test Oracle Generation" / "On the Evaluation of Neural Test Oracle Generation" - reported TOGA's real bug-finding was tiny, get the exact number); TOGLL (2024); nl2postcond, i.e. "Can Large Language Models Transform Natural Language Intent into Formal Method Postconditions?" (Endres, Fakhoury, Chakraborty, Lahiri - FSE 2024) - this is the single closest published analogue to "model writes a formal check from prose", get its measured correctness AND bug-catching rates and its evaluation methodology (it uses bug-catching as the metric, exactly like our L4 test 1); SpecGen; AutoSpec; ClassInvGen; AssertLLM (hardware assertion generation from spec documents - a strong transferable pattern, get its numbers); work on whether LLMs can write formal specifications generally.
- Invariant MINING with no model at all: Daikon (dynamic invariant detection) - how it works, what it would give us if pointed at a corpus of correctly-filled workbooks, its false-invariant problem, whether it is maintained, its licence. Also DIG, and modern learned-invariant work.
- Anything on generating validation rules from REGULATORY text specifically (search: LLM regulatory rule extraction, compliance rule generation, regulation to code with LLMs, RegNLP, chain of rules).

DELIVER: a defensible answer to "what success rate should we PRE-REGISTER for experiment 9.1 (10 obligations to executable checks, at least 3 must survive)?" grounded in the published rates for the closest analogous tasks - and the best published METHODOLOGY to copy for scoring generated checks.`,
  },
  {
    key: 'L04-regulatory-rules-as-code',
    verify: true,
    label: 'reg:rules-as-code',
    body: `THE HIGHEST-STAKES LANE. The brief asserts: "Regulation-as-code as a going concern - DEAD FOR FINANCE... zero financial regulations encoded anywhere" (Part 7), based on Catala, OpenFisca, Blawx and finos/open-reg-tech-us-lcr being tiny and stale. Test that assertion hard, because a large body of executable financial-regulatory validation rules may already exist and the brief may be badly wrong.

Investigate each, with licence, size (number of rules), activity, and whether PER-RULE error/deactivation data is published:
- EBA (European Banking Authority) validation rules: the published rule lists for supervisory reporting, the DPM (Data Point Model) and DPM Refit / DPM 2.0, and CRITICALLY the EBA's published lists of DEACTIVATED validation rules (rules withdrawn because they misfired). How many rules, how many deactivated, is a reason given? This is a real-world analogue of our per-predicate false-failure rate.
- EIOPA validation rules (Solvency II), and its published rule set and errata.
- ESMA ESEF: the ESEF Conformance Suite, ESEF validation rules and reporting manual.
- XBRL: the Formula 1.0 specification and Assertion Sets; XBRL US Data Quality Committee (DQC) rules - open source on GitHub, count the rules, get the licence, look for their published false-positive handling and rule-approval governance.
- Arelle - the open-source XBRL processor (licence, activity, plugins, DQC plugin, validation plugin architecture). Can it execute a formula linkbase? Could we emit our predicates as XBRL formula assertions?
- SDMX plus VTL (Validation and Transformation Language): the standard itself (version, who maintains it), and OPEN-SOURCE ENGINES - Trevas (INSEE, Java) and the Python vtl-engine (MeaningfulData / Bank of Spain). Is VTL a serious candidate as the language our predicates compile to? Who actually uses it (ECB, BIS, Banco de Espana)?
- ISDA CDM (Common Domain Model) and Digital Regulatory Reporting (DRR) - Rosetta / Rune DSL by REGnosys, FINOS-hosted. This literally encodes reporting regulation as executable, testable code with expectations. Licence, activity, size. Also the FCA/BoE DRR pilot outcome.
- FIRE (Financial Regulatory data standard) by Suade Labs - open source data standard; and Suade's open-source rule work.
- FINOS projects generally: which are alive, which are dead (get commit dates).
- US: FFIEC/Federal Reserve FR Y-9C and Call Report EDIT CHECKS and the MDRM dictionary - are the edit checks published? FDIC/FFIEC CDR validation criteria.
- Bank of England: BEEDS, statistical reporting validations, the Transforming Data Collection programme and its phase outcomes.
- India: RBI ADF/CIMS returns and any published validation rules; SEBI/AMFI reporting validations.

THEN answer precisely:
(a) Which part of "zero financial regulations encoded anywhere" survives? Give the strongest defensible restatement.
(b) Does any of this make our idea unoriginal? Specifically: do ANY of them (i) publish a measured false-failure rate per rule, (ii) declare what the rule set does NOT cover as a first-class output, (iii) synthesise rules with a model under a qualification gate? Show your positive control for these absence claims.
(c) What can we literally reuse - a rule corpus to benchmark against, a DSL to compile to, an engine to execute in, a governance model to copy?`,
  },
  {
    key: 'L05-spreadsheet-errors-oracle-free',
    verify: true,
    label: 'sheet:errors+corpora',
    body: `Two things: (i) the empirical literature on spreadsheet errors, (ii) tools that find spreadsheet errors WITHOUT an oracle - which is the exact problem this program claims is open.

- Ray Panko's spreadsheet error-rate research and EuSpRIG: the actual measured cell error rates, the sample sizes, and the well-known CRITICISMS of those numbers. Get denominators; do not repeat the folklore "88% of spreadsheets have errors" without its source and its caveats.
- Oracle-free spreadsheet error detection - read these properly and report method plus measured precision/recall:
  * ExceLint (Barowy, Berger, Zorn) - finds formula errors with no oracle, using information-theoretic analysis of the spatial layout of formulas. Exact venue, numbers, GitHub repo, licence.
  * CheckCell (Barowy et al., OOPSLA 2014) - data debugging: finds INPUT cells with unusual impact on outputs. Directly relevant: it finds suspicious data without knowing the right answer.
  * CUSTODES (ICSE 2017) - clustering-based smell and error detection.
  * Melford (neural detection of spreadsheet errors), and any newer LLM-era work on spreadsheet error detection (search 2024-2026: LLM spreadsheet error, SheetCopilot, SpreadsheetBench, SheetAgent, TableBench).
- PUBLIC SPREADSHEET CORPORA - this attacks the brief's largest stated weakness (section 9.2: no clean corpus exists, filed returns are not public): the ENRON spreadsheet corpus (roughly 15,000 real spreadsheets), FUSE corpus (roughly 250k from Common Crawl), VEnron/VEnron2, EUSES corpus. Sizes, licences, download locations, and an honest assessment of whether a corpus of generic business spreadsheets is any use for calibrating false-failure rates on a fund reporting template (it probably is not for FFR, but may be for testing L1 schema induction robustness - say which).
- TOOLING for L1 schema induction from xlsx: openpyxl (does it read formulas from a PROTECTED workbook? merged cells? dataValidation? defined names?), python-calamine, xlsx2csv, the raw OOXML route (zipfile plus lxml over xl/worksheets/sheetN.xml), formula parsers and evaluators (the formulas package on PyPI, pycel, koala2, openpyxl's tokenizer), LibreOffice headless conversion, and formula dependency-graph extraction. VERIFY by actually running code with /Users/abishaikc/Gift/.venv/bin/python against /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx - confirm you can extract: sheet list, protection state, merged ranges, all formulas, all dataValidations, defined names. Report exactly what worked and what did not, with the code you ran.

Also: does the operator's own section 4.3 count reproduce? (294 formulas, 181 cross-sheet carries, 35 SUM, 3 COUNTIF, 35 data validations, 3 list-type, 9 of 10 sheets protected, 6,757 cells). Report agreement or disagreement with your own independent extraction.`,
  },
  {
    key: 'L06-metamorphic-testing',
    verify: false,
    label: 'lit:metamorphic',
    body: `Layer L6 - checking relations between runs when no oracle exists - is described in the brief as the most novel component and the most likely to produce a publishable result. Make it real.

- Foundations: Chen et al.'s original metamorphic testing technical report (HKUST-CS98-01); the survey "A Survey on Metamorphic Testing" (Segura et al., IEEE TSE 2016) and "Metamorphic Testing: A Review of Challenges and Opportunities" (Chen et al., ACM CSUR 2018). Verify "The Oracle Problem in Software Testing: A Survey" (Barr, Harman, McMinn, Shahbaz, Yoo) volume, issue, pages and year exactly.
- HOW ARE METAMORPHIC RELATIONS OBTAINED? This is the crux for us. Cover: MR patterns, METRIC, MR templates, automated MR inference and mining (search: automatic identification of metamorphic relations, MR-Scout mining MRs from open-source test code, LLM-generated metamorphic relations), and any measured results on LLM-generated MRs.
- MT applied to data-heavy domains: databases and SQL engines, spreadsheets specifically (search metamorphic testing spreadsheet), machine learning models, scientific and numerical code, financial software and accounting systems (search hard; report honestly if empty, with your positive control).
- Property-based testing as the execution vehicle: Hypothesis (Python) - strategies, stateful testing, shrinking, explicit examples, and how to drive it over a structured artifact like a workbook; schemathesis; the older QuickCheck lineage. Also differential and back-to-back testing.

THEN THE REAL WORK - critique and extend the brief's proposed MRs for a fund return. The brief proposes: (1) reordering portfolio rows must not change NAV; (2) adding a zero-value holding must not change NAV; (3) consolidating two identical positions must not change NAV; (4) scaling the reporting unit must scale every derived total proportionally; (5) currency round-trip within tolerance.
For each, state: is it actually sound in fund accounting, or does it have real exceptions (lot-level cost basis and FIFO/average-cost ordering, rounding and half-even accumulation, fee accrual and performance-fee crystallisation, minimum-lot and unit-rounding, FX rate sourcing and triangulation, look-through aggregation)? Which of the five would produce FALSE alarms on a correct filing?
Then propose a LARGER, sharper MR set (aim for 15-25) specific to a fund-management regulatory reporting workbook, organised by the invariant class they test (permutation, identity element, idempotence, scaling/homogeneity, additivity/partition, round-trip, monotonicity, temporal consistency across filing periods, cross-report consistency between the FME quarterly and the annual format). For each MR give: the transformation, the expected relation, the tolerance model, the mechanical test procedure, and the failure interpretation. Mark which MRs need NO ground truth at all - those are the ones that grow coverage past the 17/24 boundary.`,
  },
  {
    key: 'L07-conformal-abstention',
    verify: false,
    label: 'lit:conformal',
    body: `Layer L2 abstention. Make it concrete and defensible, and repair it if the paper it rests on does not exist.

- Split/inductive conformal prediction: foundations (Vovk, Gammerman, Shafer; Angelopoulos and Bates, "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification"). State the exchangeability assumption precisely and the finite-sample coverage guarantee it buys.
- Classification variants: APS, RAPS, Mondrian/class-conditional conformal, conformal risk control (Angelopoulos et al.), and Learn-then-Test.
- Conformal for LLMs and for structured/IE outputs: "Conformal Language Modeling" (Quach et al.), conformal factuality (Mohri and Hashimoto), conformal for NER, relation extraction and entity linking, and conformal for multi-stage or compositional pipelines - find the REAL work that gives joint coverage across a pipeline (Bonferroni/union bound, conformal risk control, nested conformal). Note: the brief cites "PASC, arXiv:2605.18812" which lane L01 is verifying; assume it may not exist and build the design on what definitely does.
- Libraries: MAPIE, crepes, TorchCP, puncc, nonconformist, Fortuna, venn-abers. Licence, activity, which supports set-valued classification with a custom nonconformity score.
- Selective prediction and abstention without conformal: semantic entropy (Farquhar et al., Nature 2024), self-consistency, P(True), verbalised confidence and its measured miscalibration, and any work showing entropy alone is insufficient.

DELIVER an implementable design for L2 key-binding abstention: the nonconformity score, what the calibration set is, what "abstain unless the prediction set is a singleton" costs in coverage, and - most important - an HONEST section on what happens to the guarantee when the calibration set is SYNTHETIC (constructed by our own team) rather than a sample of real filings. Exchangeability with what population? If the guarantee is void, say so and give the fallback that is still worth building.`,
  },
  {
    key: 'L08-docai-constrained-decoding',
    verify: false,
    label: 'stack:docai+decoding',
    body: `The extraction stack. Note a design fact the brief under-weights: the PRIMARY artifact is a native xlsx, so no OCR is needed for it - document AI is for (a) the regulation and circular PDFs and (b) any scanned or PDF-form filing. Evaluate accordingly.

- Document parsers: Docling (IBM), Marker, MinerU (v2), Surya, unstructured, olmOCR, Nougat, LlamaParse, PaddleOCR-VL, dots.ocr, and any 2026 entrants. For each: licence, activity, model size and runtime cost, table handling, and whether it emits CITATION ANCHORS (page and bounding box) - anchors matter more than accuracy for us, because provenance pointers are a hard requirement.
- Benchmarks: OmniDocBench, and the TEDS versus TEDS-S distinction. VERIFY the brief's claim "TEDS-S exceeds TEDS on all 32 leaderboard rows" - find the actual leaderboard, state the denominator, confirm or correct. Then answer: does ANY published document-AI benchmark bound PER-CELL NUMERIC error (as opposed to structure similarity)? Positive control required.
- The regulation-text path: turning a 102-page regulations PDF and 399 circulars into citable clause units. Look at layout-aware chunking, legal document structure parsing, Akoma Ntoso / LegalDocML, and any open tooling for statutory citation resolution and amendment-chain following. The operator measured 8,866 shall-occurrences, 866 dated cross-references, and 76 of 82 amending circulars citing a resolvable target - so amendment-chain resolution is a real, mechanisable sub-problem. Find prior art.
- Constrained decoding and structured output: outlines, XGrammar, llguidance, guidance, LM Format Enforcer, and provider-native structured outputs. Plus the higher-level libraries: Instructor, BAML, PydanticAI, LangChain structured output.
- The cost of format restriction: "Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models" (EMNLP 2024 industry track) and the published rebuttals (the dottxt "Say What You Mean" post). Report BOTH sides and give a defensible position, because the brief asserts the cost as settled.

DELIVER: a specific recommended extraction stack for each of the three source classes (xlsx filing, regulation PDF, live register), with the reason each choice beats the alternative, and the exact provenance-pointer format we should standardise on.`,
  },
  {
    key: 'L09-execution-substrate',
    verify: false,
    label: 'stack:predicate-runtime',
    body: `Where do the predicates actually RUN, in what language are they written, and how do we mutate and qualify them? This is the single most consequential engineering decision in the system and the brief leaves it open.

(A) CANDIDATE LANGUAGES for a predicate. Compare on: expressiveness for the 17 decidable predicates listed in brief section 4.3; SAFETY of executing model-generated code; determinism and reproducibility; whether the predicate itself is human-readable to an auditor; whether we can mechanically MUTATE it; and whether we can compute coverage over the rule set.
  1. Plain Python plus a data-validation framework: Great Expectations, pandera, Soda Core (SodaCL), dbt tests, Deequ/PyDeequ, Frictionless, Cerberus, Pointblank. For each: licence, activity, whether expectations are declarative and serialisable, and whether the framework supports a per-check result object rich enough to carry PASS/FAIL/UNCHECKED(reason).
  2. Restricted, non-Turing-complete expression languages: CEL (Common Expression Language) - get the spec, the implementations (cel-go, cel-cpp, cel-python/celpy), the termination guarantee, and who uses it (Kubernetes admission policy is a strong precedent: model-free policy over structured data); Rego/OPA; Starlark; JSONLogic; JMESPath; SpEL.
  3. Formal: Z3/SMT (for arithmetic relations and for proving a predicate non-degenerate), Souffle/Datalog, and constraint solvers.
  4. Rule engines: Drools, GoRules ZEN, json-rules-engine, Nools.
  5. VTL, if lane L04 finds it real.
Recommend ONE primary predicate language with a concrete grammar sketch and a worked encoding of at least 5 of the 17 decidable predicates, and justify explicitly against the runners-up. Also state the escape hatch for predicates the restricted language cannot express.

(B) SANDBOXING generated code, if any generated Python survives: RestrictedPython, Pyodide/WASM, wasmtime, gVisor, Firecracker, E2B, Docker with seccomp. Recommend one, with the threat model stated (the adversary here is a confused model, not a hostile one - say what that changes).

(C) FAULT SEEDING - and correct a probable methodological error in the brief. Brief layer L4 test 1 calls itself "mutation testing" and cites mutmut/PIT/Stryker, but those mutate CODE; the brief actually needs to mutate the DATA (seed faults into a filed artifact and see whether the predicate catches them). Find the right literature and tooling for that: fault injection into data, data mutation testing, mutation testing for data pipelines and for SQL (search MutaSQL, mutation testing SQL queries, mutation testing for data quality rules, mutation analysis for spreadsheets - there IS spreadsheet mutation work, find it), chaos and fault injection for datasets, and the software-testing concept of mutation testing to evaluate a test suite reframed as fault seeding to evaluate a rule set. Also cover code mutation tooling properly for the parts where we DO mutate code (mutmut, cosmic-ray, mutpy, PIT, Stryker) and the equivalent-mutant problem's practical handling.
DELIVER a precise specification of the fault-seeding harness: a fault taxonomy for a financial reporting workbook (transposition, sign flip, off-by-one row shift, unit confusion lakh/crore/million, stale carry-forward, duplicated row, dropped row, date off-by-period, currency mislabel, rounding drift, formula overwritten by a constant), how each is generated, and how kill rate is computed and reported.`,
  },
  {
    key: 'L10-attestation-coverage-assurance',
    verify: false,
    label: 'std:attestation+coverage',
    body: `Layer L7 and the central intellectual claim: DECLARING what you could not check. The brief says the only prior art is the CycloneDX compositions aggregate field. Test that and find better.

- Software supply chain: in-toto (attestation spec, layouts, licence), Sigstore/cosign (keyless signing, Rekor transparency log), SLSA provenance levels, SPDX 3.0, CycloneDX - verify the compositions aggregate field, its enumerated states (the brief says ten), which spec version introduced it, and the exact semantics of each state. Also OpenSSF Scorecard, and Rekor as a model for a public append-only registry of attestations.
- Provenance models: W3C PROV-O, RO-Crate, C2PA content credentials (a strong analogue: assertions plus a claim signature plus a declared set of what was and was not asserted).
- NIST OSCAL - go deep. Its Assessment Plan, Assessment Results, Plan of Action and Milestones, and Component Definition models. OSCAL already formalises "these controls were assessed, by these methods, with these findings, and these were not assessed." Licence, maturity, tooling (oscal-cli, compliance-trestle). Assess seriously whether our report schema should BE an OSCAL assessment-results document or a profile of one. This could be a major, defensible reuse.
- THE ASSURANCE-PROFESSION ANALOGUES the brief misses entirely, and they are strong:
  * ISRS 4400 (Revised) Agreed-Upon Procedures Engagements - a standardised professional report that lists exactly the procedures performed and the factual findings, and expressly EXPRESSES NO OPINION beyond them. This is, almost exactly, the shape of our verdict. Get the standard's actual requirements for the AUP report.
  * ISAE 3402 / SSAE 18 SOC 1: the carve-out versus inclusive method for subservice organisations - a standardised way of declaring what the report does NOT cover.
  * ISA 200/315/330 sufficient appropriate audit evidence; ISA 600 (Revised) group audit component scoping; scope limitation and the qualified/disclaimer opinion mechanics; ISA 320 materiality; PCAOB AS 1215 audit documentation.
  * XBRL and regulatory validation-report output formats, and any machine-readable audit-evidence format.
DELIVER: (a) a verdict on whether "no analogue exists for a financial assertion" survives - with the strongest defensible restatement; (b) a concrete report schema recommendation (fields, states, signing envelope) that borrows the best of OSCAL plus ISRS 4400 plus in-toto; (c) the exact closed vocabulary for UNCHECKED reasons, improved on the brief's six.`,
  },
  {
    key: 'L11-nav-error-materiality',
    verify: true,
    label: 'domain:nav-error',
    body: `Ground the DOMAIN. The recommended entry is a NAV-error and filing-verification regime for GIFT IFSC funds, and the operator measured ZERO IFSCA circulars mentioning NAV error, materiality thresholds, incorrect NAV, valuation error or swing pricing across 389 readable circular bodies. Establish what the rest of the world does, so the gap can be stated precisely and defensibly.

- Luxembourg: CSSF Circular 02/77 on the protection of investors in case of NAV calculation error and non-compliance with investment rules - get the ACTUAL materiality thresholds by fund type (verify the percentages; commonly cited as money market, bond, equity and mixed tiers) and the compensation mechanics. Then check whether it has been replaced or supplemented - search for CSSF Circular 24/856 (protection of investors in case of NAV calculation error, investment breach and other errors, applicable from 1 January 2025) and report exactly what changed, including thresholds and reporting obligations.
- Ireland: Central Bank of Ireland guidance on NAV errors and pricing errors, the CBI UCITS/AIF rulebook provisions, and Irish Funds industry guidance.
- UK: FCA COLL 6.3 (pricing), the de minimis threshold for box and pricing errors, and FCA guidance on unit pricing errors.
- US: SEC Rule 2a-4, the penny-per-share convention, ICI/AICPA practice on NAV error correction and the half-cent and 1% thresholds, ASC 946.
- India (onshore, for contrast): SEBI Mutual Funds Regulations on NAV, AMFI Best Practice Guidelines on NAV errors and rectification, SEBI's swing pricing framework (2021 circular), and any SEBI circular on standardised handling of NAV errors and investor compensation.
- International: IOSCO principles for the valuation of collective investment schemes; ESMA guidance on NAV errors and liquidity.
- GIFT IFSC / IFSCA: read what the IFSCA (Fund Management) Regulations 2025 actually require - Third Schedule Part A(g), Sixth Schedule (g) true and fair NAV, regs 26(2)/38(2)/50(2) independent valuer, regs 27(1)/39(1)/51(1) NAV frequency. Confirm or correct the operator's finding that no threshold or compensation regime is specified. Check the FM FAQ dated 3 August 2026 too.
- Operational reality: fund administrators serving GIFT IFSC (KFin Technologies, CAMS, Basiz Fund Services, Apex, Vistra, Orbis) - do any publish house NAV tolerances or error policies? What does NAV oversight, shadow NAV and independent price verification actually involve, and what software does it (FundGuard, Milestone Group pControl, Confluence, SS&C)? Is there measured data on NAV error frequency anywhere?

DELIVER: (a) a precise, sourced statement of the international standard of practice; (b) a precise, sourced statement of what IFSCA specifies and does not; (c) a judgement on which wedge is sharper for the hackathon - a NAV-error regime, or prescribed-return verification with declared coverage - and why; (d) the exact question to put to a fund administrator to settle the remaining unknown.`,
  },
  {
    key: 'L12-competitive-novelty',
    verify: true,
    label: 'market:novelty',
    body: `Who already sells something adjacent, and what precisely is unoccupied? The point is NOT to kill the idea - it is to find the defensible claim and to protect the innovation from being restated as something that already exists.

Survey, with sources:
- Regulatory reporting quality and controls: Suade Labs, Regnology (including Vizor on the supervisory side), AxiomSL/Adenza (Nasdaq), Vermeg, Wolters Kluwer OneSumX, Confluence (Unity NXT regulatory reporting for funds), FundApps, Corlytics, Ascent, Clausematch, Hexanika, Gresham.
- Fund and NAV specific: FundGuard, Milestone Group pControl, SS&C, Clearwater Analytics, Northern Trust and BNY oversight tooling.
- Audit and assurance AI: MindBridge, DataSnipper, Trullion, Fieldguide, Caseware IDEA, Numeric, Klarity, AuditBoard, Basis, Bluecopa, and the Big Four's own tools where documented.
- LLM evaluation and assertion tooling: LangSmith (SPADE shipped there - verify), Braintrust, Patronus AI, Guardrails AI, Arize Phoenix, DeepEval, promptfoo, Evidently, Giskard, Ragas.
- Data quality: Great Expectations and GX Cloud, Monte Carlo, Soda, Anomalo, Sifflet, Bigeye, dbt.
- Indian RegTech and anything already at GIFT City or in the IFSCA sandbox doing compliance verification.

For EVERY category answer the same two questions, and show the positive control for any absence claim:
 Q1. Does the product publish, PER RULE, the measured rate at which that rule fires on known-clean inputs?
 Q2. Does the product declare, as a first-class output, what it could NOT check and why?

Then search directly for the specific combinations we claim: LLM-synthesised validation rules for regulatory returns; metamorphic testing applied to financial reports or fund NAV; per-rule false-positive publication in a compliance product; coverage declaration for a compliance verdict; measured false-failure rate as a shipped product feature.

DELIVER: (a) a competitive map; (b) an exact statement of the unoccupied claim, in one sentence, that survives an adversarial reading; (c) a list of what is genuinely NEW versus what is assembly of known parts - and argue why the assembly is itself the contribution, if it is; (d) the three strongest "this already exists" objections a judge could raise, and the exact rebuttal to each, with sources.`,
  },
  {
    key: 'L13-architecture-adversary',
    verify: false,
    label: 'adv:architecture',
    effort: 'xhigh',
    body: `You are THE ADVERSARY. Attack the design in the architecture document and the brief as a senior distributed-systems engineer, a testing researcher, and a skeptical supervisor would - then repair what you break. You may use web tools but the work here is analytical.

Attack at least these, each in the strongest form you can construct, followed by the strongest available repair and an honest label of whether the repair is MEASURED or HOPED-FOR:
1. Section 2.4 says the machine-verifiable predicates and the valuable predicates are "very nearly disjoint" - yet section 4.3 celebrates 17/24 = 71% as a passed threshold. Are these consistent? If the 17 decidable predicates are the boring ones, does the product have a customer? Does L6 actually move the boundary, or does it only add more boring checks?
2. L4 test 1 is called "mutation testing" but it seeds faults into DATA, not code. Name the correct methodology and say what changes (the mutation score denominator, the equivalent-mutant analogue for data, the fault-model coverage claim).
3. "Two model calls, both short." Does that survive contact with reality - clause segmentation, retrieval over 399 circulars and a 102-page regulation, amendment-chain resolution, provenance anchoring, re-synthesis on template version change? Count the model calls an honest implementation needs and say whether the claim must be rewritten.
4. The corpus problem. FFR measured on a clean corpus that the TEAM constructs measures the team's own filling behaviour, not real filings. How badly does that undermine every FFR number the product displays? Enumerate every available repair and rank them: public spreadsheet corpora, the template's own 294 native formulas as a cross-check, held-out fault seeding, cross-template transfer, sampling real filings via an FME partner, differential testing between the annual and quarterly formats, using the regulator's own published aggregates. Is there any construction under which a quoted FFR is honest?
5. "No green tick anywhere" versus the fact that a 100% coverage fraction IS a green tick, and a coverage meter reading 71% is itself a summary statistic that can be wrong. Resolve, concretely, at the level of pixels and copy.
6. Version churn: the workbook is versioned and 23.1% of circulars amend an earlier instrument. What happens to the predicate registry, to admitted mutation scores and to FFRs when the template changes? Design the versioning and re-qualification policy, including the case where a predicate silently becomes untestable.
7. Scale: 217 FMEs, 360 schemes, about 868 filings a year. That is TINY. Is the supervisor user real? Is the filer user real? What is the honest unit of value, and does the architecture over-engineer for a volume that does not exist? What would have to be true for this to matter beyond one regulator?
8. The honest answer to "why does this need an LLM at all". If the answer is "mostly it does not", what happens to the pitch, and is there a stronger framing in which the model's role is small but load-bearing?
9. Failure modes of the system ITSELF. The operator's own section 4.4 documents two silent false negatives from DETERMINISTIC programs (a regex that could not match a formula element with no attributes). Our system is a deterministic program. What is our analogue of that failure, and what in the architecture would catch it? If nothing would, that is the most important hole in the design - propose the self-check.
10. Anything else you find that is wrong, circular, unfalsifiable, or unbuildable.

DELIVER a prioritised list: the attacks that must be answered before the design is defensible, the ones that can be answered later, and the ones that are fatal if unanswered. Then write the REVISED architecture in outline form, showing exactly what you changed and why.`,
  },
  {
    key: 'L14-build-path-and-stack',
    verify: false,
    label: 'build:path+stack',
    body: `The build plan and the application-layer technology decisions. Be concrete, dated and boring where boring wins.

Deadlines from brief Part 1: applications close 16 August 2026; two-day ideation hackathon 21-22 August 2026 at GIFT City; residency 1 September to 30 October 2026; up to Rs 1,00,000 milestone-linked; judging on problem relevance, innovation and creativity, solution feasibility, team capability, and presentation and pitch quality.

(1) GROUND IT IN THE REAL ARTIFACTS - do not speculate, RUN CODE. Use /Users/abishaikc/Gift/.venv/bin/python (openpyxl and lxml installed) against every workbook in /Users/abishaikc/Thinking/gift-ifsc-ground/scratchpad-oracle/ . For each workbook report: sheets, protection, merged ranges, formula count and classification (cross-sheet carry versus SUM versus IF versus IFERROR versus COUNTIF), data validations and which are list-type with a real vocabulary, defined names, and the count of labelled fields. Then state precisely what a demo can compute TODAY with zero model involvement. Confirm or correct the operator's numbers in brief section 4.3. Write the scripts you use into /Users/abishaikc/Gift/research/scripts/ .
(2) THE 16 AUGUST DELIVERABLE - what artifact backs the application link (the form takes one URL: demo video, prototype, Figma, GitHub, website or deck). Recommend exactly one and say why.
(3) THE 21-22 AUGUST TWO-DAY BUILD - a scoped, achievable end-to-end demo. A dependency-ordered task list with a hard cut line.
(4) THE RESIDENCY PLAN, 1 September to 30 October - milestones aligned to milestone-linked funding, each with a measurable acceptance test.
(5) APPLICATION STACK, each choice justified against its runner-up, not asserted:
   - Backend language. Python looks near-forced (openpyxl, pandera, conformal libraries, mutation tooling) - confirm or refute, and consider a Python core with a thin TypeScript edge.
   - API framework: FastAPI versus Litestar versus Django-ninja. Job execution: is any queue needed for a sub-60-second job, or is synchronous plus SSE enough? If a queue is needed, which.
   - Storage: SQLite versus Postgres; content-addressed blob store; how the predicate registry is versioned and how a report is made exactly re-derivable.
   - Frontend: Next.js versus SvelteKit versus Remix versus a Python-native option (Reflex, Streamlit, NiceGUI). The screens are: Drop, Report (test-run shaped, expandable failures, coverage meter), Unchecked panel, Predicate library, Coverage-over-time. Which stack renders these fastest without becoming the project? Consider shadcn/ui, Tailwind, TanStack Table, and a diff or DAG view for the field graph.
   - Deployment: single container versus Fly.io versus Vercel plus Railway versus nothing-but-a-laptop for the demo. Consider that judges may open it on a phone.
   - Observability and reproducibility: run manifests, content addressing, and how to prove a report re-derives.
(6) MODEL CHOICE. Check the CURRENT Claude model line-up, context windows and pricing via the web (do not answer from memory), and compare against open-weight options for the predicate-synthesis loop where many candidates are generated. Recommend a model per model-bearing step (L2 extraction, L3 synthesis) with a cost estimate per filing.
(7) An explicit DO-NOT-BUILD list, and a statement of what the final prototype must be able to DO on stage, in one paragraph, unambiguously.`,
  },
]

phase('Survey')
log(`Running ${LANES.length} research lanes with adversarial verification on the load-bearing ones`)

const laneResults = await pipeline(
  LANES,
  (lane) =>
    agent(PRE + lane.body + POST(lane.key), {
      label: lane.label,
      phase: 'Survey',
      schema: LANE_SCHEMA,
      effort: lane.effort,
    }),
  (res, lane) => {
    if (!res || !lane.verify) return res
    return agent(
      `You are an ADVERSARIAL VERIFIER. Your job is to REFUTE, not to agree.

Use the Read tool on ${LDIR}/${lane.key}.md - a research lane's findings for a regulated-finance verification system. Also Read ${BRIEF} for what the findings are supposed to support.

Load web tools first: ToolSearch with query "select:WebSearch,WebFetch".

Pick the 5-8 claims in that file whose FALSITY would most damage the design, and independently check each one at primary source - open the arXiv abstract page, the GitHub repo, the regulator's own PDF, the licence file. Do not accept the lane's own citation as evidence; re-derive it.

Default to REFUTED or UNVERIFIABLE when you cannot confirm. An identifier that does not resolve is NOT-FOUND, not "probably fine". A number quoted without its denominator is UNVERIFIABLE.

Today is 10 August 2026; your training data is older, so live checking is mandatory for anything recent.

Then APPEND a section titled "## Adversarial verification (independent pass)" to ${LDIR}/${lane.key}.md - Read the file, then Write it back with your section appended verbatim at the end. Do not delete or rewrite the lane's own content.

Return the structured verdicts.`,
      { label: `verify:${lane.key.slice(0, 3)}`, phase: 'Verify', schema: VERIFY_SCHEMA, effort: 'high' },
    ).then((v) => ({ ...res, verification: v }))
  },
)

const ok = laneResults.filter(Boolean)
log(`${ok.length} of ${LANES.length} lanes complete. Synthesising.`)

phase('Synthesis')

const SYN_PRE = `You are writing one section of the AUTHORITATIVE build specification for a regulated-finance verification system.

Read, with the Read tool, in this order:
1. ${BRIEF}
2. ${ARCH}
3. EVERY file in ${LDIR}/ (list it first with Bash ls, then Read each one - there are 14, several with an appended adversarial-verification section). These lane files supersede the brief wherever they contradict it, PROVIDED the lane cites a primary source and the adversarial pass did not refute it.

Rules for what you write:
- No ambiguity. Every decision is stated as a decision, with the alternative it beat and the reason.
- Every number carries its warrant and its denominator. Anything the lanes marked REFUTED or NOT-FOUND must be removed or restated, never repeated.
- Do not lose the innovation in the name of defensibility: where something is genuinely novel, say so plainly and say exactly what makes it novel and what would falsify the novelty claim.
- Write for an engineer who will build it and a judge who will challenge it, in the same document.

YOUR SECTION:
`

const synth = await parallel([
  () =>
    agent(
      SYN_PRE +
        `THE PROBLEM AND THE ARCHITECTURE.

Write these parts, in full, to ${SDIR}/A-problem-and-architecture.md :
(1) The problem, restated so that it is unambiguous, falsifiable, and survives the lanes' corrections. Who has it, what it costs them, how it is handled today, and what specifically is missing. Include the domain grounding from the NAV-error lane: what the rest of the world specifies and what IFSCA does not.
(2) What we are actually building - in one paragraph a non-specialist understands, then in one paragraph an engineer can implement against.
(3) THE ARCHITECTURE, revised. Take the eight layers as a starting point, apply every repair the adversary lane L13 established, and every substitution the research lanes justified. For each layer: its exact input and output types, whether it contains a model, its failure modes, its self-check, and the named open-source component it reuses with the reason that component beat its alternative. Show the corrected data flow as an ASCII diagram.
(4) THE PREDICATE MODEL, specified precisely: what a predicate IS as a data structure, the language it is written in (take the recommendation from the execution-substrate lane), how it is qualified, what it carries permanently, how it is versioned against a changing template, and the exact semantics of PASS / FAIL / UNCHECKED with the improved closed vocabulary of reasons.
(5) THE REPORT - the output object schema, its signing envelope, and its relationship to any standard the lanes found (OSCAL, ISRS 4400 agreed-upon procedures, in-toto, CycloneDX).
(6) A section "WHAT IS GENUINELY NOVEL" - the defensible claim, the three strongest objections, and the rebuttal to each.
Be long and complete. This is the spine of the document.`,
      { label: 'syn:architecture', phase: 'Synthesis', effort: 'xhigh' },
    ),
  () =>
    agent(
      SYN_PRE +
        `THE TECHNOLOGY STACK AND THE BACKEND FLOW.

Write to ${SDIR}/B-stack-and-flow.md :
(1) A decision table: every technology choice, the layer it serves, the runner-up it beat, the evidence for the choice, and the condition under which we would switch. Cover: workbook parsing, schema induction, regulation-text parsing and clause citation, predicate language and runtime, sandboxing, fault-seeding harness, metamorphic-relation execution, conformal and abstention library, model provider and model per step, data validation substrate, storage and content addressing, attestation and signing, API framework, frontend, deployment.
(2) For each ADOPTED open-source project: what exactly we use it for, what we do NOT use it for, its licence and licence implications for a commercial product, its maintenance risk, and the fallback if it is abandoned.
(3) THE BACKEND FLOW, end to end, as a precise sequence: a filing arrives, then what, until a signed report exists. Name every step, its inputs, its outputs, its determinism, its failure handling, and where a human is required. Include the OFFLINE flows too: predicate synthesis, qualification, registry admission, and re-qualification on template version change.
(4) Data model: the tables and collections, the content-addressing scheme, the registry schema, and how a report is proven to re-derive exactly.
(5) Performance and cost: expected runtime per filing, model token cost per filing, and what happens at 868 filings a year and at 100 times that.
(6) The interfaces: the API surface and the screens, described precisely enough to build without further questions.
Be concrete. Version numbers where you have them, honest gaps where you do not.`,
      { label: 'syn:stack', phase: 'Synthesis', effort: 'xhigh' },
    ),
  () =>
    agent(
      SYN_PRE +
        `THE DEVELOPMENT PATH AND THE DELIVERABLE.

Write to ${SDIR}/C-build-path.md :
(1) THE SETTLING EXPERIMENT FIRST. Brief section 9.1 says: 10 obligations to executable checks, scored by the qualification gate, and if fewer than 3 of 10 survive, layer L3 is deleted. Using what lane L03 found about published success rates on the closest analogous tasks (LLM postcondition generation, test-oracle generation, assertion generation from specs), state whether 3 of 10 is the right pre-registered threshold or whether the evidence justifies a different one - and give the exact experimental protocol: the 10 obligations, the prompt, the scoring, the fault set, what counts as survival, and what gets written down before the run.
(2) The full experiment queue, re-ordered by what actually decides the design, with each experiment's cost, its pre-registered threshold, and what it kills if it fails.
(3) THE DATED BUILD PLAN: by 16 August (application plus the one link it needs), 21-22 August (two-day hackathon build with a hard cut line), 1 September to 30 October (residency, milestone by milestone with an acceptance test each). Dependency-ordered.
(4) THE DO-NOT-BUILD LIST, with the reason for each exclusion.
(5) WHAT THE FINAL PROTOTYPE DELIVERS - unambiguous. Write it as: the exact demo script (what is on screen, in order, and what the operator says), the acceptance criteria that make the demo honest, the numbers that will be on screen and where each one comes from, and the single sentence a judge should be able to repeat afterwards.
(6) RISK REGISTER: every risk, its probability, its blast radius, its early-warning signal, and its mitigation. Mark which risks are already retired by the lanes' findings.
(7) The team-capability and feasibility story the application needs, given judging on problem relevance, innovation and creativity, solution feasibility, team capability, and presentation quality.`,
      { label: 'syn:buildpath', phase: 'Synthesis', effort: 'xhigh' },
    ),
])

phase('Reconcile')

const reconcile = await agent(
  `You are the RECONCILER. Find every contradiction and every gap before this specification is presented.

Read, with the Read tool:
- ${SDIR}/A-problem-and-architecture.md
- ${SDIR}/B-stack-and-flow.md
- ${SDIR}/C-build-path.md
- every file in ${LDIR}/ (list it with Bash ls first)
- ${BRIEF}

Produce, and write to ${SDIR}/D-reconciliation.md :
1. CONTRADICTIONS - every place where the three synthesis sections disagree with each other, or with a lane finding, or with the brief. For each: quote both sides, say which is right and on what evidence, and give the single sentence that should replace both.
2. SURVIVING FALSEHOODS - any number, identifier, licence, star count or claim that a lane marked REFUTED, NOT-FOUND or UNVERIFIABLE but which still appears asserted anywhere in the synthesis. List them for deletion. Be exhaustive; this is the most important part.
3. UNWARRANTED CONFIDENCE - claims stated more strongly than their warrant supports, with the corrected phrasing.
4. GAPS - decisions the specification still leaves open that an engineer would be blocked by on day one, and questions only the user can answer.
5. THE INNOVATION CHECK - has anything genuinely novel been sanded off in the name of defensibility? Name each and say whether it should be restored, and how to state it so it is both bold and true.
6. A one-page EXECUTIVE VERDICT: what the problem is, what we are building, why it works, what could kill it, and what to do first - in under 500 words, with no hedging and no unwarranted certainty.

Return a compact summary: the count of contradictions, the list of surviving falsehoods to delete, the list of blocking gaps, and the executive verdict verbatim.`,
  { label: 'reconcile', phase: 'Reconcile', effort: 'xhigh' },
)

return {
  lanes: ok.map((l) => ({ lane: l.lane, file: l.file, findings: (l.headline || []).length, corrections: l.corrections || [] })),
  laneCount: ok.length,
  synthesisFiles: [SDIR + '/A-problem-and-architecture.md', SDIR + '/B-stack-and-flow.md', SDIR + '/C-build-path.md', SDIR + '/D-reconciliation.md'],
  reconciliation: reconcile,
}
