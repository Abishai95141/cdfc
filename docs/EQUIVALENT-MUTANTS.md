# docs/EQUIVALENT-MUTANTS.md

**Every mutant that survived a campaign and was argued to be equivalent, with the argument.**
Append-only. A row is never deleted; if an argument turns out to be wrong, a later row says so and
the score moves.

**Why this file exists rather than a `--exclude` flag.** A surviving mutant is either a hole in the
tests or a genuinely equivalent program, and only reading it tells you which. A tool that quietly
excluded survivors would raise every score by exactly the amount nobody was allowed to see. So the
published score has **two denominators** — `killed / generated` and `killed / (generated −
declared_equivalent)` — and this file is the only thing that may move the second one.

**The bar for a row here:** an argument that the mutant cannot change any observable behaviour, not
an argument that the current vectors happen not to reach it. *"No vector covers this"* is a hole,
and its remedy is a vector.

## The rows

| id | subject | mutant | argument | dated |
|---|---|---|---|---|
| EQ-001 | `src/cdfc/predicates/host_fns/template_current.py` | `@lru_cache(maxsize=1)` → `maxsize=2` | The cache is keyed on a zero-argument call, so it holds exactly one entry at any size ≥ 1. No call sequence distinguishes the two. This is a memoisation parameter, not a decision. | 12 Aug 2026 |

## What was NOT declared equivalent, and became a vector instead

Three survivors from P4-B3's first run were **holes in the published vectors**, not equivalent
mutants. They are recorded here because a reader comparing the first score to the final one is
entitled to know which way each survivor was resolved.

| survivor | resolution |
|---|---|
| `gstin_valid`: `product // 36` → `// 37` | A vector was added whose position-3 character has alphabet index 18 at weight 2, so the product is **exactly 36** — the only value in this alphabet's range at which the two differ. |
| `gstin_valid`: `(36 - total % 36) % 36` → `% 37` | A vector was added whose weighted total is congruent to 0 mod 36, so the check character is `'0'`. Under the mutant that row indexes past the end of the alphabet. No previous vector reached it. |
| `sum`: `isinstance(v, bool) or isinstance(v, float)` → `and` | Not a vector but a **code change**. The guard named two types and fell through to `int(v)` for everything else, so `sum(["12"])` silently coerced a string in a numeric column. The guard is now `not isinstance(v, int)`, and the coercion is gone. |
| `nav_interval`: `st == "RESTRICTED"` → `!=` | Also a code change, and the most interesting of the four. The branch was **behaviourally redundant**: the lookup table returned the same token for that combination anyway, so flipping the comparison changed nothing observable. Splitting the return vocabulary into `UNDERSPECIFIED` (*the regulator did not determine it*) and `UNKNOWN_COMBINATION` (*we have no row*) made the branch load-bearing — and those were always two different facts. The test did not get stronger; the code got more truthful. |

**Note the ratio.** Of five survivors in the first measured run, **one** was equivalent and four
were defects — two in the vectors and two in the code. That is the argument for reading survivors
rather than excluding them.
