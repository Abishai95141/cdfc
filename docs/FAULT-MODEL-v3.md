# docs/FAULT-MODEL-v3.md — the pinned fault taxonomy, version `v3`

**This file is the single source of the class ids.** `src/cdfc/predicates/fault_model.py` parses the
table below; no Python module re-types the list. Two lists drift, and the one that drifts is the one
nobody is reading.

**Provenance.** Classes `F01`–`F11` are populated by Abraham & Erwig's seventeen spreadsheet mutation
operators (*IEEE Transactions on Software Engineering* 35(1):94–108, 2009), several of which map onto the
same class — which is why seventeen operators yield eleven classes. `F12`, `F13` and `F14` are ours, and
each was added because a MEASURED instance in this corpus fell outside the published taxonomy.

**Why it is pinned at P4 and not at P6.** `Candidate.claims_fault_classes` is required from the moment the
envelope exists, and it is inside `code_sha256`. A claim resolving against a taxonomy that had not been
written yet would be a claim against nothing. P6 builds the *executable* model (`src/cdfc/fault/model.py`,
one operator module per class); it reads its ids from here.

**Why the commit date matters.** `test_g2_denominator_is_declared_before_the_campaign` asserts the commit
introducing a predicate's `claims_fault_classes` is a git-ancestor of the campaign it is scored against.
This file and `docs/FAULT-CLAIMS.md` are committed in P4, four phases before the first campaign, so that
test is satisfied by construction rather than by discipline.

## The table

| id | name | operator | applies_to | scope | why this class exists |
|---|---|---|---|---|---|
| F01 | sign flip | `v → −v` | MONEY, COUNT | cell | Kills a `≥ 0` bound and does **not** kill a `≥ −1e17` bound |
| F02 | scale error | `×10`, `÷10`, `×1000` | MONEY | cell | The sheet's unit is USD Million; a filer entering USD is the modal unit slip |
| F03 | off-by-one | `±1` unit `MILLI_USD_MILLION`; `±1` on a count | MONEY, COUNT | cell | Boundary. Counts get zero tolerance — a person is not a rounded quantity |
| F04 | digit transposition | `12340 → 13240` | MONEY | cell | Keying error; survives a magnitude check |
| F05 | zero-out / blank | `v → 0`, and separately `v → <empty cell>` | ALL | cell | Two operators, not one. `0` and blank are different facts, and `sum([]) == 0` |
| F06 | round to integer | drop the 2-dp quantum | MONEY | cell | The `τ(n) = 5n` straddle generator, and the source of `indeterminate.tolerance_straddle` |
| F07 | row omission | delete one data row from a table body | ALL | range | Where a missing investor or holding hides |
| F08 | row duplication | duplicate one data row | ALL | range | Double count; the tally identities exist for this |
| F09 | date shift | `±1 day`, `±1 quarter`, `DD↔MM` swap | DATE | cell | FME carries six date bounds |
| F10 | enum substitution | one **legal** vocabulary term for another | ENUM | cell | A membership predicate cannot see this, by construction. A designed miss; it belongs in the residue |
| F11 | formula override | a cell the pinned blank declares a formula carries a literal | MONEY, COUNT | cell and pair | The flagship. The pair form leaves the filing perfectly self-consistent because the inconsistency was deleted with the formula |
| F12 | vocabulary drift | a term outside the pinned vocabulary; **and** a homoglyph or whitespace variant of a legal one | ENUM, TEXT | cell | MEASURED: a live regulated entity's registration number carries `U+2011 NON-BREAKING HYPHEN` — visually identical, byte-wise different |
| F13 | carry desync | a cross-sheet carry target changed while its source is untouched, or the reverse | MONEY, COUNT | cell and pair | 181 cross-sheet equalities on FME; the pair form is the coordinated-misstatement seed |
| F14 | vocabulary-gap exploitation | a value legal under the template's **own defective logic** but outside the regulation | ENUM | cell | MEASURED: the regulator's template computes a scheme total with three COUNTIFs that between them miss two of its nine legal Type-of-Scheme values |

**Fourteen classes.** `src/cdfc/predicates/fault_model.py` asserts the parsed count, so a row silently
lost to a bad edit is a build failure rather than a smaller denominator.

## The one hard constraint on the numbering

`F11` is the formula-override class. P9's exit gate and experiment E3 both name a seeded `F11` pair by id.
If the mapping from the seventeen published operators is ever revised and the class count changes, the
other ids may shift; **`F11` may not.**
