# D-P4-06 — `claims_fault_classes`, the field that stops a predicate choosing its own denominator

**The defect.** Every binding document repeats that G2's registry bar is *`K/O >= 0.80` on the
fault classes the predicate **claims** to cover*. **No field of the envelope held such a claim.**
The only place a fault class appeared was `FaultWitness.fault_class` — and the witness set is
selected by `qualify/g2_kill.py` **at admission, from mutants that already killed**. The numerator
was choosing its denominator, at the gate that exists to catch exactly that.

**Concretely.** A `sum_identity` predicate over `'3. Portfolio'!O7` runs against a 14-class
campaign. It kills F01 and F03 on its own read set; it is structurally blind to F10, F12, F13 and
F14. Overall `K/O = 0.21`. G2 selects three witnesses from the mutants that died — all F01/F03 —
stamps `fault_class: F01` on them, and evaluates the bar over `{F01, F03}`, where `K/O = 0.97`.
**The predicate is admitted `BLOCKING`, the library prints `0.97`, the attestation signs it, and
nothing is red.** NC-Q05 checks the arithmetic (`K <= O <= G`) and NC-Q06 the site universe; both
are satisfied. The defect is in the *class partition*, and no control reached it.

**Decision. `claims_fault_classes: tuple[str, ...]` is a required, non-empty field of
`Candidate`.** Four properties, each with the artifact that enforces it:

1. **On `Candidate`, not on `Predicate`.** The claim must exist *before* qualification, because a
   field only `Predicate` carries is a field written after the campaign.
   `test_envelope__claims_fault_classes_is_required_and_non_empty`.
2. **Inside `envelope_projection()`, therefore inside `code_sha256`.** Narrowing the claim after a
   campaign produces a **new digest, i.e. a different predicate**, which the registry treats as a
   new admission needing a new qualification record.
   `test_envelope__narrowing_a_claim_changes_the_digest`, and
   `test_prop__every_envelope_field_is_covered_by_the_digest` covers it automatically because that
   property reads the field list from `dataclasses.fields()` at runtime.
3. **Every claimed class must be exercised on the campaign.** `g2_kill.check()` raises if any
   claimed class has `O == 0` — *an unexercised claim is not a claim*. This also makes
   over-claiming self-punishing in the honest direction: **a wider claim is a harder bar, never a
   softer one.** (P7-B3.)
4. **The claim must predate the campaign, and git is the evidence.**
   `test_g2_denominator_is_declared_before_the_campaign` asserts the commit introducing a
   predicate's claim is a git-ancestor of the campaign it is scored against. `docs/FAULT-CLAIMS.md`
   is committed at P4, four phases before the first campaign, so this holds by construction.

**And the number a reviewer actually wants.** The predicate library renders `K/O` over the claimed
set **and** `K/O` over all fourteen classes, side by side. **The gap between them is the
measurement.**

**Claims resolve against `docs/FAULT-MODEL-v3.md`**, parsed by `src/cdfc/predicates/fault_model.py`.
A claim naming a class nobody defined raises: `test_envelope__claims_are_drawn_from_the_pinned_fault_model`.
