# P5 — the runtime closure partition, on a real filing

**Warrant: MEASURED.** Produced by `make run-fme`. Nobody has this number: the static figure is
computed before any evaluation, and the runtime figure is what a filing actually produces.

## The filing the claim is made on

`clean__independently-computed__fme-q1.xlsx`

> INDEPENDENTLY-COMPUTED (LibreOffice). Its derived cells were computed by an implementation this project did not write — NOT by a person, and NOT by Excel. It is the plan's E6 substitute and it is weaker than E6 in two named ways: LibreOffice is not Excel, so a disagreement is a third answer rather than a verdict against us; and it is a spreadsheet engine, not a reader of the regulation, so it cannot notice that a formula is wrong.

## The seven terms, and they sum to the field surface

    outOfScope 0  +  informational 0  +  settled 2320  +  indeterminate 0  +  notRun 0  +  noPredicate 1427  +  error 0
      ==  3747   (cellsTotal 3747)

    of which retained: outOfScope 0   informational 0
    inScope            3747
    fraction           0.6192   =  settled 2320 / inScope 3747

`fraction` never renders without `cellsTotal` and `inScope` beside it. A shrinking denominator
must be visible on the page, not merely correct in the object.

| field | value |
|---|---:|
| field surface (denominator) | **3747** |
| denominator validation state | `PROVISIONAL-UNVALIDATED` |
| admission state | `PRE-GATE` |
| keys pre-flighted | 1725 |
| keys **type**-checked | 77 |
| cells lowered by roll-up | 0 |

**`keys_type_checked` is published beside `keys_preflighted` because a type check that did not
happen is never reported as one** (D-P5-03). Where the AST cannot decide a key's type, the key is
presence-checked only and the difference between these two numbers is how much.

## Static against runtime

| number | value | what it counts |
|---|---:|---|
| `static_settled_cells` | **2794** | cells reachable by >= 1 harvested predicate, before any evaluation |
| `runtime_settled_cells` | **2320** | cells whose ROLLED-UP state is PASS or FAIL on this filing |
| delta | **-474** | — |

### The delta, decomposed

| part | cells | what it is |
|---|---:|---|
| statically bound but **outside the field surface** | 474 | a predicate binds a LOCKED or FORMULA cell. It is checked; it is not part of the denominator, which is what a filer fills in |
| in the surface, bound, and **not settled** | 0 | the part the roll-up is responsible for |

**Most of the delta is the first row, and saying so matters**: an undecomposed delta reads as
roll-up lowering when most of it is a difference of populations.

**Under the binding precedence order the runtime figure CAN be lower**, because a cell read by one
passing and one not-run predicate is unsettled — *the settled fraction falls, it does not silently
succeed.* On this filing 0 cell(s) were lowered by roll-up.

## One seeded fault, and the predicates are named rather than counted

Seeded at `1. Introduction!C54` by raw-zip surgery: one worksheet part differs and nothing else.

| | |
|---|---|
| predicates reading that cell | `P-0021`, `P-0051` |
| predicates that FAILED | `P-0021`, `P-0051` |

The clean filing produced **zero** failures. Without that control the seeded number would carry no
information.

## The smoke filing, and why its number is not on this page as a claim

`clean__template-computed__fme-q1.xlsx` — run state `INVALID`, 349 checks.

> SMOKE ONLY — NON-GATING — NON-DISCRIMINATING (arithmetic). src/cdfc/calc/ wrote this filing's derived cells, and the arithmetic predicates assert exactly the identities calc/ enforced when it did. The oracle and the system under test are the same function, so a zero here is x == x. It may not be cited in a gate, in a severity tier, or in any published rate.

**Its result does not enter P5's exit gate.** The gate is TRUE or FALSE without consulting it, and
a red there is a defect report rather than a gate failure.

## What this measurement does not license

That any of these predicates is right. `admissionState` is `PRE-GATE`: none of them is admitted
under G4, and the number says how much of the denominator a check ran over — not that any check
encodes the rule it is named for. The denominator itself is `PROVISIONAL-UNVALIDATED`: nobody
outside this repository has checked the unlocked mask against a person filling the form in.
