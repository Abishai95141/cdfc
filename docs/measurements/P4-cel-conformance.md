# P4-B3 — CEL runtime agreement

## DIFFERENTIAL, not CONFORMANCE

This number is produced by D-P4-04's fallback harness, not by the official CEL
conformance suite. **Two implementations wrong the same way are invisible to a**
**differential**, and that is not hypothetical in this project. Every surface quoting this
figure carries the same label.

What makes it worth running: the second runtime is **`cel-expr-python`, Google's own CEL
runtime with the C++ core** — the reference implementation, not a second port. Agreement
with it is stronger evidence than agreement between two third-party interpretations.

| runtime | version |
|---|---|
| `cel-python` (celpy) — **the runtime the registry root is qualified against** | 0.5.0 |
| `cel-expr-python` (reference, test-only) | 0.1.3 |

## The two slices, reported separately

| slice | agreement | what it covers |
|---|---|---|
| admitted subset | **35/35** | every operator, macro and literal form the profile admits |
| error semantics | **12/12** | operand errors under `&&` and `||`, both sides |

**Why the split is not cosmetic.** The CEL specification says an operand error in `&&`/`||`
*"will be ignored"* when the other operand determines the result. If the two runtimes
differ THERE, the pre-flight guard's necessity argument behaves differently between them —
so a single blended percentage would hide the one disagreement that changes a design
decision.

## Gate G-CELPY

**The registry root is qualified against `cel-python`**, recorded in
`qualified_against.evaluator_version` on every predicate envelope. The reference runtime is
a check on it, not the thing predicates run on: it is a native extension whose availability
is a platform question, and a verdict path that depends on a wheel building is a verdict
path that can vanish.

## Every row

| slice | expression | celpy | reference | agree | note |
|---|---|---|---|---|---|
| subset | `filing.a.b == 1` | `True` | `True` | yes |  |
| subset | `filing.a.b != 2` | `True` | `True` | yes |  |
| subset | `filing.n > 0` | `True` | `True` | yes |  |
| subset | `filing.n >= 7` | `True` | `True` | yes |  |
| subset | `filing.n < 8` | `True` | `True` | yes |  |
| subset | `filing.n <= 7` | `True` | `True` | yes |  |
| subset | `filing.s == "AIF"` | `True` | `True` | yes |  |
| subset | `filing.blank == ""` | `True` | `True` | yes |  |
| subset | `filing.flag` | `True` | `True` | yes |  |
| subset | `!filing.flag` | `False` | `False` | yes |  |
| subset | `filing.n + 1 == 8` | `True` | `True` | yes |  |
| subset | `filing.n - 1 == 6` | `True` | `True` | yes |  |
| subset | `filing.n * 2 == 14` | `True` | `True` | yes |  |
| subset | `filing.n / 7 == 1` | `True` | `True` | yes |  |
| subset | `filing.n % 2 == 1` | `True` | `True` | yes |  |
| subset | `-filing.n == -7` | `True` | `True` | yes |  |
| subset | `filing.s in template.v.k` | `True` | `True` | yes |  |
| subset | `filing.s in ["AIF", "PMS"]` | `True` | `True` | yes |  |
| subset | `filing.n == template.n` | `True` | `True` | yes |  |
| subset | `filing.flag ? filing.n == 7 : filing.n == 0` | `True` | `True` | yes | ternary |
| subset | `has(filing.a.b)` | `True` | `True` | yes |  |
| subset | `has(filing.a.zzz)` | `False` | `False` | yes |  |
| subset | `size(filing.rows) == 3` | `True` | `True` | yes |  |
| subset | `size(filing.empty) == 0` | `True` | `True` | yes |  |
| subset | `filing.rows.all(r, r.x >= -2)` | `True` | `True` | yes |  |
| subset | `filing.rows.exists(r, r.x < 0)` | `True` | `True` | yes |  |
| subset | `filing.rows.exists_one(r, r.x == 0)` | `True` | `True` | yes |  |
| subset | `filing.empty.all(r, r.x > 0)` | `True` | `True` | yes | all([]) is true — NC-Q01's shape |
| subset | `filing.empty.exists(r, r.x > 0)` | `False` | `False` | yes |  |
| subset | `filing.rows.filter(r, r.x < 0).size() == 1` | `True` | `True` | yes |  |
| subset | `filing.rows.map(r, r.c).size() == 3` | `True` | `True` | yes |  |
| subset | `filing.rows.map(r, r.x)` | `[1, -2, 0]` | `[1, -2, 0]` | yes |  |
| subset | `filing.rows.filter(r, r.x <= 0).map(r, r.c)` | `['S!A2', 'S!A3']` | `['S!A2', 'S!A3']` | yes |  |
| subset | `filing.rows.all(r, r.c != "")` | `True` | `True` | yes |  |
| subset | `filing["a"]["b"] == 1` | `True` | `True` | yes | index syntax |
| errors | `true || (1/0 == 1)` | `True` | `True` | yes | error on the right of ||, absorbed |
| errors | `(1/0 == 1) || true` | `True` | `True` | yes | error on the LEFT of || — the discriminating case |
| errors | `false && (1/0 == 1)` | `False` | `False` | yes | error on the right of &&, absorbed |
| errors | `(1/0 == 1) && false` | `False` | `False` | yes | error on the LEFT of && |
| errors | `(1/0 == 1) || false` | `<ERROR>` | `<ERROR>` | yes | no absorbing operand: the error must survive |
| errors | `(1/0 == 1) && true` | `<ERROR>` | `<ERROR>` | yes | no absorbing operand |
| errors | `1/0 == 1` | `<ERROR>` | `<ERROR>` | yes | the bare error |
| errors | `filing.missing.x == 1` | `<ERROR>` | `<ERROR>` | yes | absent key |
| errors | `true || (filing.missing.x == 1)` | `True` | `True` | yes | absent key absorbed by || |
| errors | `(filing.missing.x == 1) || true` | `True` | `True` | yes | absent key on the left |
| errors | `filing.rows.all(r, r.zzz > 0)` | `<ERROR>` | `<ERROR>` | yes | absent field inside a comprehension |
| errors | `filing.empty.all(r, 1/0 == 1)` | `True` | `True` | yes | vacuous over an empty list |

## Disagreements

None on this coverage set. That is not a conformance claim; see the label above.
