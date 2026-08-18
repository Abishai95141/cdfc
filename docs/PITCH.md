# docs/PITCH.md — the submission text

**Written 16 Aug 2026.** Deliberately scoped to the GENERAL case, not to this prototype: the
schema-free induction and the coverage declaration are the product, and one workbook family is the
evidence base. Word limits are the submission's, and each section is inside them.

---

## Title

**Coverage Declaration for Filed Compliance**

---

## Elevator pitch — 148 words

Regulated entities file structured returns continuously: fund reports, exposure data, capital
adequacy, AML statements. Every tool that checks them reports what it found. None reports what it
never examined — so a field nobody looked at is indistinguishable from a field reviewed and found
correct.

This system induces a form's rules from the form itself — the formulas, dropdowns, protection masks
and cross-sheet references the regulator already wrote into the artifact. No rules project to
commission, no schema to maintain, no lag when a version changes.

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

## Proposed solution — 248 words

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
Static analysis of the artifact — formula graph, data validations, protection mask, cross-sheet
references — induces the constraints the form already encodes, so a new or revised form becomes
checkable without an authoring project. Checks are expressed in a constrained, machine-checkable
language. Each is put through seeded-fault testing before it may count: a check that cannot be shown
to catch anything contributes nothing to coverage. Reports are deterministic and re-derivable byte
for byte, so a published claim can be verified by whoever receives it.

**Expected impact on users**
A reviewer can state what was checked and what was not. An auditor can verify that statement
independently. A supervisor can see the scope behind a submission instead of inferring it.
