# docs/FAULT-CLAIMS.md — what each harvest class CLAIMS to cover

**Committed at P4-B4, four phases before the first campaign runs.** That is the point of the file:
`test_g2_denominator_is_declared_before_the_campaign` asserts the commit introducing a predicate's
`claims_fault_classes` is a **git-ancestor** of the campaign id it is scored against, and a claim
declared here is satisfied by construction rather than by discipline.

**Why a claim has to exist at all** (D-P4-06). G2's registry bar is `K/O >= 0.80` *on the fault
classes the predicate claims to cover*. Before this field, the only place a fault class appeared
was the witness set **G2 itself selects, after the campaign, from mutants that already killed** —
the numerator choosing its denominator, at the gate that exists to catch exactly that.

**Two properties that make the incentive run the right way.**

- **Over-claiming is self-punishing.** A wider claim is a HARDER bar: more classes in the
  denominator, and every one of them has to be killed.
- **Under-claiming is caught.** Any claimed class with `O == 0` on the campaign **raises** at G2 —
  an unexercised claim is not a claim — and the predicate library renders `K/O` over the claimed
  set beside `K/O` over all fourteen classes. **The gap between them is the measurement.**

Each class declares its claim ONCE, as a module-level constant in
`src/cdfc/predicates/harvest_classes/<name>.py`. The harvest cannot invent a claim per predicate,
so `test_harvest__claims_are_a_pure_function_of_the_class` is mechanical: two harvests of one
template emit identical claims, and a claim tuned after a campaign changes `code_sha256` and is
therefore a different predicate.

## The claims

| harvest class | `claims_fault_classes` | why exactly these |
|---|---|---|
| `conditional_required` | `F05` | it detects the blank-and-zero pair and nothing else. The custom condition is deliberately NOT translated, which is why the claim is this narrow |
| `cross_sheet_equality` | `F01 F02 F03 F04 F05 F13` | 181 of these on FME; F13 (carry desync) is the class they exist for, and any single-sided perturbation of either end breaks the equality |
| `date_bound` | `F09` | FME's date bounds; nothing else in the taxonomy moves a date |
| `integer_bound` | `F01 F03 F06` | as `numeric_bound`, plus the rounding class, because an integrality bound is exactly what F06 perturbs |
| `membership` | `F12` | vocabulary drift, including the homoglyph and whitespace forms. **NOT F10** — a *legal* enum substituted for another legal enum is invisible to a membership test **by construction**; claiming it would be the exact lie this field exists to prevent |
| `numeric_bound` | `F01 F03` | a sign flip crosses a `>= 0` bound; an off-by-one crosses a boundary. **Not F02** — a x10 on a positive value stays above a `>= 0` bound |
| `same_sheet_equality` | `F01 F02 F03 F04 F05` | as `cross_sheet_equality` minus the cross-sheet carry — there is no carry to desynchronise when both ends are on one sheet |
| `sum_identity` | `F01 F02 F03 F04 F05 F07 F08` | a row omission or duplication moves the sum; a transposition, scale slip, sign flip, off-by-one or zero-out in a summand does too |
| `tally_identity` | `F05 F07 F08` | counts against a table body. It sees rows appearing and disappearing and **nothing about value magnitude** |

## `fault_classes_claimed_by_no_harvested_candidate`

**{F10, F11, F14}** — 3 of 14. *A fault class nobody claims is the most useful thing on
the page, and before this file no document in the corpus contained the list.*

| class | name | why it is unclaimed |
|---|---|---|
| **F10** | enum substitution | legal enum substitution. A membership test cannot see one legal vocabulary term substituted for another BY CONSTRUCTION — the value is in the vocabulary. A designed miss, and P10's residue feedstock. |
| **F11** | formula override | formula override. Claimed by TEMPLATE_DIFF, which is a RELATION and is built at P9-B1, not by any harvested class. No relation the template encodes can detect the deletion of the formula that encodes it. |
| **F14** | vocabulary-gap exploitation | vocabulary-gap exploitation — a value legal under the template's own defective logic but outside the regulation. MEASURED: the FME template computes a scheme total with three COUNTIFs that between them miss two of its nine legal Type-of-Scheme values. No relation derived from that template can see a filing exploiting it. |

Ids resolve against `docs/FAULT-MODEL-v3.md`, parsed by `src/cdfc/predicates/fault_model.py`. A
claim naming a class nobody defined raises at load time.
