#!/usr/bin/env bash
# Registry row 37. A rate never renders without both integers of its fraction.
#
# WHY IT EXISTS. The v0 harness printed `MS = 18.09%`. That number had a denominator nobody could
# reconstruct — `|mutants| - |equivalent|`, where `equivalent` is a THEOREM that was asserted
# rather than proved — and a later harness printed **100.1%**, which is arithmetically impossible
# and went unnoticed because a percentage carries no evidence of its own arithmetic.
#
# The rule: a `%` on a line must also carry `n/d`, or be inside a code fence / a URL / a
# threshold expressed as a bound. `K/O = 3574/19760` is admissible; `18.09%` alone is not.
set -euo pipefail
cd "$(dirname "$0")/.."
source ci/_roots.sh
assert_roots_exist cdfc_roots || { echo "GATE FAIL: refusing to report success over a missing root" >&2; exit 1; }

# `$PY` is DISCOVERED by ci/_roots.sh, which refuses when no interpreter can import cdfc.
"$PY" - <<'PYEOF'
import pathlib, re, sys

# The surfaces a rate can reach a reader from. Plan documents are excluded: they are the design
# record and quote the literature's figures, which is a different act from this build printing one.
#
# **`tools/` WAS MISSING, AND IT IS THE ONLY ONE THAT REACHES A READER TODAY.** `cdfc run` exits 2
# and the report template has no renderer, so the programs that actually print a coverage
# declaration to a human are `tools/demo_*.py` and `tools/measure/*.py`. Demonstrated: a bare rate
# `print()`-ed from `tools/demo_template_diff.py` was invisible to this gate, while the same text
# as a DEAD COMMENT inside `src/cdfc` made it red. The gate fired on what nobody sees and stayed
# silent on what everybody does.
ROOTS = ["src/cdfc", "tools", "docs/measurements", "reports"]
# **`%` IS ALSO PYTHON'S MODULO, and RFC 8032 is written in it.** `x = x * _SQRT_M1 % _p` was
# read as the rate `1 %` and made this gate red on a correct implementation of a published
# standard. A percent SIGN in prose or a format string is followed by a space, a quote, a closing
# brace or the end of a line; a modulo is followed by an operand. The negative lookahead below is
# what separates them, and it is narrow on purpose: widening it to `%\s*\w` would also admit
# `50% coverage`, which is exactly what this gate exists to catch.
BARE = re.compile(r"(?<![\d/])\d+(?:\.\d+)?\s*%(?!\s*[_A-Za-z(])|\}\s*%(?!\s*[_A-Za-z(])|:\s*\.\d+[fg]\}%")
HAS_FRACTION = re.compile(r"\d[\d,]*\s*(?:/|of|out of)\s*\d")
ALLOW = re.compile(r"(https?://|%s|%d|%r|width:|# *noqa)")

# A DECLARED exception, and it must carry a reason. Two things legitimately print a bare
# percentage: a REGULATORY THRESHOLD quoted from a rule (75% by value is not a rate we computed),
# and a HISTORICAL figure named as the defect it was (v0's 18.09%, v1's impossible 100.1%). Both
# are quotations, not measurements. The marker is greppable, so widening it is a visible diff.
RATE_OK = re.compile(r"rate-ok: *[^ ]")

offenders = []
for root in ROOTS:
    p = pathlib.Path(root)
    if not p.exists():
        print(f"GATE FAIL: {root} does not exist; a scan over it would report success", file=sys.stderr)
        sys.exit(1)
    for f in sorted(p.rglob("*")):
        if f.suffix not in (".py", ".md", ".json", ".jsonl", ".txt") or not f.is_file():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not BARE.search(line) or HAS_FRACTION.search(line) or ALLOW.search(line):
                continue
            if RATE_OK.search(line):
                continue
            offenders.append(f"{f}:{i}: {line.strip()[:100]}")

if offenders:
    print("GATE FAIL: a rate rendered without both integers of its fraction:", file=sys.stderr)
    for o in offenders[:20]:
        print(f"  {o}", file=sys.stderr)
    print("  A percentage carries no evidence of its own arithmetic. The v0 harness printed",
          file=sys.stderr)
    print("  18.09% over a denominator nobody could reconstruct, and a later one printed 100.1%.",
          file=sys.stderr)
    sys.exit(1)
print("no-bare-rate: OK")
PYEOF
