# A2 — Path M: the product executes rules a regulator wrote

*Built and measured 20 Aug 2026. `cdfc rules` produces this. **Zero model calls**, proven as a
property of the import graph.*

```
of 12925 rules published at 2026-06-23, we executed 10453.

the typed reason for each of the other 2472:
  deactivated_by_publisher       1869 of 12925
  banned_construct_clock            4 of 12925
  banned_construct_regex            6 of 12925
  needs_range_binding             513 of 12925
  unparseable_expression           80 of 12925

data points addressed by executed rules  31904
```

**N is the publisher's number, not ours.** `eba_validation_rules_4.3_2026_06_23.xlsx`,
sha256 `9997374c8f60f555…`, 1,071,753 bytes — re-fetched and **byte-identical to what `W0-B`
measured months earlier**. The date comes from the file's own name; nothing here reads a clock.

## What reproduces, independently

`W0-B` measured this file with a different reader. Every one of its figures reproduces:

| | W0-B | this build |
|---|---:|---:|
| data rows | 12,925 | **12,925** |
| Active / Inactive | 11,056 / 1,869 | **11,056 / 1,869** |
| rows carrying an Expression | 12,925 | **12,925** |
| rules whose `Tables` cell is `NULL` | 1 | **1** |

And `E1`'s vocabulary census: **14 distinct function-like tokens**, with `isnull` 514, `abs` 383,
`max` 52, `min` 25, `time_shift` 62, `match` 13 — every count identical.

## THE DEFECT THIS BUILD HAD, THREE TIMES, AND WHAT IT COST

The first declaration read **9,723 executed, 1,323 unparseable**. All three of the following were
rules the regulator wrote perfectly well and this parser could not read — **and each one was
reported under a reason that was not true of it**, which is precisely the defect
`docs/OPEN-ITEMS.md` records as under-reporting honestly and still being wrong.

| the construct | rules | what the parser did |
|---|---:|---|
| `{(r0100, r0110, r0200), c0010}` — a parenthesised row LIST | **696** | split on the comma, so `(r0100` matched no axis and the whole point was dropped |
| `{r*, c0020, s*}` — a THIRD axis | **114** | refused the point over one unrecognised atom |
| `{r0850-0860}` — an axis RANGE | 513 | genuinely not bound — but it is not *unparseable* |

`E2` had already established both of the first two: *"row and column may be a LIST … or a
wildcard"* and *"it must tolerate **extra axes** it does not understand."* `Anchor` was built for
them. The Path M parser was not, and **10% of the corpus carried a false label until the bucket
was opened and read.**

The range gets its own reason rather than a fix: expanding `{r0850-0860}` would **invent axis
members the table may not have**, which is how a read set comes to contain data points the rule
never addressed.

## Zero model calls, as a property rather than a promise

`cdfc.pathm` is now a `VERDICT_ROOT` in `tests/negative/importgraph.py`, alongside `cdfc.evidence`.

    cdfc.pathm      closure  42 modules   banned reachable: NONE
    cdfc.evidence   closure 407 modules   banned reachable: NONE

The walk asserts a closure over 20 modules first, so an empty walk cannot pass as a clean one.

## What A2 does NOT yet establish

* **No rule has been executed against a filed instance.** `E2` proved the addresses resolve
  against each rule's *own declared scope*; it did not prove a filed artifact carries a fact at
  that address, and no COREP/FINREP/Solvency II instance is held. **This remains A2's open entry
  criterion**, and it gates the claim that a *finding* is produced — not the claim measured here,
  which is about the rule set.
* **The CEL is compiled, not conformance-tested against Arelle.** `W2-5` is the differential arm
  and needs the external oracle.
* **513 range rules and 80 unparsed** are named, not solved.
