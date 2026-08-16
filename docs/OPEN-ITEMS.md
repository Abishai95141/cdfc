# docs/OPEN-ITEMS.md — standing unanswered questions, rendered with their age

`cdfc.surface.openitems` reads this file and `docs/FIELD-OBSERVATIONS.md`. An item with a sent date
and no reply renders as *"asked <date>, no reply after <n> days"* — **never as absence**. A question
nobody answered gets louder as it ages.

- [OPEN] The clean corpus is not funded, so no predicate is admitted under G4 and every severity is capped at ADVISORY. n >= 189 would be needed for BLOCKING.
- [OPEN] A statutory instrument IS pinned since 16 Aug 2026 — the IFSCA (Fund Management) Regulations 2025, 1,218 units, two external extraction arms. No harvested predicate implements a clause from it, so predicates_with_a_STATUTE_obligation still reads 0 of N. The blocker moved from the corpus to the authoring.
- [OPEN] Cohen's kappa for the stratum assignment is unmeasured; it needs a second named adjudicator and has no mechanical substitute.
- [OPEN] 319 of 348 harvested predicates produce no record in the reference run. `1. Introduction!D3` is in the field-surface mask and `P-0002` binds it, yet the cell falls into the 1,849 no-predicate bucket — so that bucket is counted under a reason code that says no predicate exists when one does. It under-reports coverage, which is the honest direction, but the reason is wrong.
- [OPEN] Every candidate is refused at G2 — 315 for no kill, 33 for no margin over the free baselines — so the predicate library is empty and every settled count in this product rests on predicates that were never gate-admitted. The two populations are disjoint and the surface says so.
- [OPEN] The churn sweep's precise signal moved nobody in the reference run: `P-0002` carries the year vocabulary and does not appear in that run, so the measured step-down comes from the conservative sheet-level signal instead.
