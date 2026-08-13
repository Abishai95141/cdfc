# docs/FAULT-MODEL-v3.md — the pinned fault taxonomy, version `v3`

**GENERATED from `src/cdfc/qualify/fault_model.py`. Never hand-edited.** Run `make fault-model` to
regenerate; `test_contract__fault_model_doc_is_generated` asserts byte-identity, so an edit here
without a change to the code fails the build.

**The arrangement was inverted at P6, and the reason is worth stating.** At P4 this document was
hand-written and a parser read the class ids out of it. That was right while the taxonomy was a
list of ids. It stops being right once an operator is **executable**: `mutate()` cannot live in a
markdown table, and a table beside the code is a second list — and the one that drifts is the one
nobody is reading.

**`model_digest` = `4b14132ef9add6c2ef9158a90082360c9a6d69471efcd1a75d6c7aab684ab372`**

It is a sha256 over the RFC 8785 canonical serialisation of the operator table, **including a
digest of each operator's own source**. A version pinned in name only lets a silently edited
operator keep its `v3` label, and every kill rate ever quoted is then qualified
against a model that no longer exists (NC-Q33). The digest enters every qualification record and
every campaign manifest.

## The table — 14 classes, 24 operators

| id | class | operators | dtypes | arity | source |
|---|---|---|---|---|---|
| **F01** | sign_flip | `F01.a` negate | COUNT, MILLI_USD_MILLION | cell | abraham_erwig_2009 |
| **F02** | scale_error | `F02.a` times_ten · `F02.b` divide_ten · `F02.c` times_thousand | MILLI_USD_MILLION | cell | abraham_erwig_2009 |
| **F03** | off_by_one | `F03.a` plus_one · `F03.b` minus_one | COUNT, MILLI_USD_MILLION | cell | abraham_erwig_2009 |
| **F04** | digit_transposition | `F04.a` swap_adjacent_digits | MILLI_USD_MILLION | cell | abraham_erwig_2009 |
| **F05** | zero_out_or_blank | `F05.a` zero · `F05.b` blank | COUNT, DATE, ENUM, MILLI_USD_MILLION, TEXT | cell | abraham_erwig_2009 |
| **F06** | round_to_integer | `F06.a` round_to_usd_million | MILLI_USD_MILLION | cell | abraham_erwig_2009 |
| **F07** | row_omission | `F07.a` delete_row_values | COUNT, DATE, ENUM, MILLI_USD_MILLION, TEXT | range | abraham_erwig_2009 |
| **F08** | row_duplication | `F08.a` duplicate_the_value_above | COUNT, DATE, ENUM, MILLI_USD_MILLION, TEXT | range | abraham_erwig_2009 |
| **F09** | date_shift | `F09.a` plus_one_day · `F09.b` minus_one_quarter · `F09.c` swap_day_and_month | DATE | cell | abraham_erwig_2009 |
| **F10** | enum_substitution | `F10.a` another_legal_member | ENUM | cell | abraham_erwig_2009 |
| **F11** | formula_override | `F11.a` literal_over_formula · `F11.b` literal_over_formula_pair | COUNT, MILLI_USD_MILLION | pair | cdfc |
| **F12** | vocabulary_drift | `F12.a` outside_vocabulary · `F12.b` homoglyph · `F12.c` trailing_whitespace | ENUM, TEXT | cell | cdfc |
| **F13** | carry_desync | `F13.a` move_the_target · `F13.b` move_both_ends | COUNT, MILLI_USD_MILLION | pair | cdfc |
| **F14** | vocabulary_gap_exploitation | `F14.a` legal_but_uncounted | ENUM | cell | cdfc |

**Pair operators: `F11.b`, `F13.b`.** A pair edits a second cell so the
artifact stays **self-consistent** — the inconsistency a single-cell edit leaves behind is exactly
what the template's own relations would have caught, and the pair deletes it with the formula.

## Why this artifact has each class

- **F01 sign_flip** — The operator that kills a `>= 0` bound and does NOT kill a `>= -1e17` bound — which is how ALR's five vacuous bounds become visible as a per-class zero rather than as an opinion.
- **F02 scale_error** — The sheet's unit is USD Million; a filer entering USD is the modal unit slip.
- **F03 off_by_one** — Boundary. Counts get ZERO tolerance — a person is not a rounded quantity.
- **F04 digit_transposition** — Keying error; survives a magnitude check, which is why a bound predicate cannot see it.
- **F05 zero_out_or_blank** — TWO operators, not one. `0` and blank are different facts, and `sum([]) == 0` is NC-Q01. A class that carried only one of them would make the two indistinguishable in the vector.
- **F06 round_to_integer** — The `tau(n) = 5n` straddle generator, and the source of `indeterminate.tolerance_straddle`. It produced all 22 of v0's 'equivalents'. COUNT is deliberately absent: rounding a count is not a rounding error, it is a different count.
- **F07 row_omission** — Where a missing investor or holding hides. A RANGE operator: it edits every cell of one table row, which is still exactly one worksheet part.
- **F08 row_duplication** — Double count; the tally identities exist for this.
- **F09 date_shift** — FME carries six date bounds. `DD<->MM` is the one a reader cannot see in a rendered date.
- **F10 enum_substitution** — One LEGAL vocabulary term for another. A membership predicate CANNOT see this, by construction — it is a DESIGNED MISS and it belongs in the residue. A non-zero kill rate here would be evidence that something is wrong with the campaign, not that we are good.
- **F11 formula_override** — THE FLAGSHIP. A cell the pinned blank declares a formula for carries a literal. The pair form leaves the filing perfectly self-consistent because the inconsistency was deleted with the formula, and TEMPLATE_DIFF is the only thing in the design that detects it.
- **F12 vocabulary_drift** — MEASURED: one live regulated entity's registration number carries `U+2011 NON-BREAKING HYPHEN` — visually identical, byte-wise different, invisible in any screenshot.
- **F13 carry_desync** — 181 cross-sheet equalities on FME. This is the class they exist for, and the pair form is the coordinated-misstatement seed.
- **F14 vocabulary_gap_exploitation** — MEASURED: the regulator's template computes a scheme total with three COUNTIFs that between them MISS TWO of its nine legal Type-of-Scheme values. A filing exploiting that gap is undetectable by any relation the template encodes — P10's residue feedstock.

## Provenance

Classes populated from the published suite carry a verbatim citation with a page reference:

- **F01** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F02** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F03** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F04** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F05** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F06** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F07** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F08** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F09** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100
- **F10** — R. Abraham and M. Erwig, 'Mutation Operators for Spreadsheets', IEEE Transactions on Software Engineering 35(1):94-108, 2009, pp. 97-100

Ours: `F11`, `F12`, `F13`, `F14`. These carry no citation and a rationale instead, and the rationale names the MEASURED
instance in this corpus that produced the class.

## The one hard constraint on the numbering

**`F11` is the formula-override class.** P9's exit gate and experiment E3 both name a seeded `F11`
pair by id. The other ids are illustrative and may shift; `F11` may not.

## What this taxonomy does not claim

**NC-N50, and no negative control is possible for it.** Completeness of a fault taxonomy is a claim
about the population of real filing errors, and **no filed FME return is public — the denominator
does not exist.** Every `K/O` computed over this model is therefore a statement about *our operator
mix* and nothing else. The bridge from seeded faults to real ones is the coupling effect, and
**there is no coupling study for financial filing data.** The only instrument available is the
catalogue's append-only growth log.

**Three classes are DESIGNED MISSES.** `F10` (a legal enum substituted for another legal one),
`F12`'s homoglyph form and `F14` (a value legal under the template's own defective logic) are
classes our own predicates cannot catch by construction. A per-class kill vector with no zeroes in
it would be evidence that the model is too weak — **not** that the predicates are good.
