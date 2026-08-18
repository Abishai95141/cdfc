# docs/PITCH.md — the submission text

**Written 16 Aug 2026.** Deliberately scoped to the GENERAL case, not to this prototype: the
schema-free induction and the coverage declaration are the product, and one workbook family is the
evidence base. Word counts are the submission's.

**Two sections have since grown past the length they were submitted at, and the word counts below
say so.** The elevator pitch went out at 148 words and the proposed solution at 248; an audit on 18
Aug 2026 found that four sentences claimed for the product what is only true of the engine, and
qualifying them cost words. The counts in the headings are what these sections are now, not what
was submitted, because a heading that keeps quoting the submitted figure while the text underneath
it has changed is the same class of stale claim the qualifications were added to remove.

---

## Title

**Coverage Declaration for Filed Compliance**

---

## Elevator pitch — 171 words (submitted at 148)

Regulated entities file structured returns continuously: fund reports, exposure data, capital
adequacy, AML statements. Every tool that checks them reports what it found. None reports what it
never examined — so a field nobody looked at is indistinguishable from a field reviewed and found
correct.

This system induces a form's rules from the form itself — the formulas, dropdowns, protection masks
and cross-sheet references the regulator already wrote into the artifact. No rules project to
commission, no schema to maintain, no lag when a version changes — shown for the induction engine
on workbooks outside this corpus, not yet for the shipped runner, which is pinned to one blank.

What it returns is a coverage declaration. Every field is accounted for: checked and settled,
checked and failed, or not checked with a reason from a closed vocabulary and a statement of what
would make it checkable. The unchecked count is published at the same weight as the checked one.

And the coverage number is allowed to fall. That is the point.

---

## Problem statement — 231 words

**What problem are you solving?**
Structured regulatory filings get checked, but coverage is never declared. Tools and reviewers
report findings; none reports the denominator. There is no way to distinguish a field examined and
found correct from a field nobody examined — and the second is where undetected error lives.

**Who experiences this problem?**
Compliance officers and internal audit at regulated entities; the fund administrators, accountants
and consultants who prepare filings on their behalf; and the supervisors who receive those filings
and must judge how much assurance a submission actually carries.

**Why does the problem matter?**
Forms change every cycle. A rule set written for last year's version silently stops applying to the
fields that moved, and nothing in the output says so. Reviewers sign off on work whose scope they
cannot state. A regulator querying a specific field months later has no record of whether it was
ever looked at. Accountability rests on a denominator nobody wrote down.

**How is it currently being addressed today?**
Three ways, each incomplete. Manual review against checklists — does not scale, leaves no
machine-readable trace of what was covered. Bespoke rule engines — every form needs a hand-written
rule set, expensive to build and stale the moment the form is reissued. General-purpose document
review — fluent output with no denominator at all, which cannot be audited for what it skipped and
is most confident where it is least grounded.

---

## Proposed solution — 292 words (submitted at 248)

**The solution**
A checker that derives its rules from the filing template rather than from a maintained schema, and
returns an auditable coverage declaration rather than a findings list. Every field lands in exactly
one state — checked and settled, checked and failed, or not checked — and every unchecked field
carries a reason from a closed vocabulary plus the specific instrument that would make it checkable.

**What makes it unique**
The unchecked count is a first-class published figure, given the same weight as the checked one,
with its own reasons and remedies attached. And the coverage number is permitted to fall: when a
template changes, affected checks stop counting toward it, and the decrease is published with its
cause. A number that can only rise is a marketing figure.

**How technology enables it**
Static analysis of the artifact — data validations, protection mask, cross-sheet references, and a
formula graph built but not yet on the path that checks a filing — induces the constraints the form
already encodes, so a new or revised form becomes checkable without an authoring project. Checks
are expressed in a constrained, machine-checkable language. Each is put through seeded-fault
testing before it may count: a check that cannot be shown to catch anything contributes nothing to
coverage, and here 348 of 348 candidates were refused at that gate, leaving 0 admitted. The
attestation payload is deterministic and re-derivable byte for byte — over a 4,015-byte summary
statement, not the per-cell record or the rendered report, signed with a demo key published here.

**Expected impact on users**
A reviewer can state what was checked and what was not. An auditor can verify that statement
independently. A supervisor can see the scope behind a submission instead of inferring it.
