"""Path M — rules a REGULATOR WROTE, executed as data. **No model is involved at any point.**

The distinction from Path Q is the whole reason this package exists. On Path Q a model proposes a
binding from prose and five gates adjudicate it. Here there is nothing to propose: the regulator
published the rule AND the data point it addresses, in one machine-readable expression:

    with {tC_25.01.a, default: 0, interval: true}: {r0010, c0060} * 12.5 = {tC_02.00.a, r0675, c0010}

`docs/PLAN.md §5` calls this the first of the three doors meaning arrives through, and the cheapest:
**there is no semantics to infer.** `E2` measured 18,826 of 18,827 addresses resolving against each
rule's own declared scope.

    reader.py      the published rule set, off the raw zip
    statement.py   PublishedRule and the closed reason vocabulary
    dpmxl.py       the DPM-XL parser -- context header, expression, data points
    compile.py     DPM-XL -> CEL, refusing with a NAMED reason rather than guessing
    coverage.py    the declaration: of N published at date D, we executed M, and here is why not

**Nothing here imports a model client, and `tests/negative/importgraph.py` walks the closure to
say so.** The claim "zero model calls" is not a promise about intent; it is a property of the
import graph.
"""
