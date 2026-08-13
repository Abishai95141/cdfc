#!/usr/bin/env python
"""Regenerate `docs/FAULT-MODEL-v3.md` from `src/cdfc/qualify/fault_model.py`.

The code is the source and the document is generated: an OPERATOR is executable and cannot live in
a markdown table. `test_contract__fault_model_doc_is_generated` regenerates and asserts
byte-identity, so a hand edit fails the build.

    make fault-model
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.qualify.fault_model import (  # noqa: E402
    CLASS_COUNT,
    FAULT_CLASSES,
    FAULT_MODEL_VERSION,
    canonical_table,
    model_digest,
    operators,
)

DOC = REPO / "docs" / "FAULT-MODEL-v3.md"
BASELINE = REPO / "fixtures" / "baselines" / "fault-model-v3.json"


def render() -> str:
    rows = []
    for c in FAULT_CLASSES:
        dtypes = ", ".join(sorted(str(d) for d in c.applies_to))
        ops = " · ".join(f"`{o.id}` {o.name}" for o in c.operators)
        rows.append(
            f"| **{c.id}** | {c.name} | {ops} | {dtypes} | {c.arity} | {c.source} |"
        )
    why = "\n".join(f"- **{c.id} {c.name}** — {c.rationale}" for c in FAULT_CLASSES)
    cites = "\n".join(
        f"- **{c.id}** — {c.citation}" for c in FAULT_CLASSES if c.source != "cdfc"
    )
    ours = ", ".join(f"`{c.id}`" for c in FAULT_CLASSES if c.source == "cdfc")
    pair_ops = [o.id for o in operators() if o.is_pair]

    return f"""# docs/FAULT-MODEL-v3.md — the pinned fault taxonomy, version `{FAULT_MODEL_VERSION}`

**GENERATED from `src/cdfc/qualify/fault_model.py`. Never hand-edited.** Run `make fault-model` to
regenerate; `test_contract__fault_model_doc_is_generated` asserts byte-identity, so an edit here
without a change to the code fails the build.

**The arrangement was inverted at P6, and the reason is worth stating.** At P4 this document was
hand-written and a parser read the class ids out of it. That was right while the taxonomy was a
list of ids. It stops being right once an operator is **executable**: `mutate()` cannot live in a
markdown table, and a table beside the code is a second list — and the one that drifts is the one
nobody is reading.

**`model_digest` = `{model_digest()}`**

It is a sha256 over the RFC 8785 canonical serialisation of the operator table, **including a
digest of each operator's own source**. A version pinned in name only lets a silently edited
operator keep its `{FAULT_MODEL_VERSION}` label, and every kill rate ever quoted is then qualified
against a model that no longer exists (NC-Q33). The digest enters every qualification record and
every campaign manifest.

## The table — {CLASS_COUNT} classes, {len(operators())} operators

| id | class | operators | dtypes | arity | source |
|---|---|---|---|---|---|
{chr(10).join(rows)}

**Pair operators: {", ".join(f"`{o}`" for o in pair_ops)}.** A pair edits a second cell so the
artifact stays **self-consistent** — the inconsistency a single-cell edit leaves behind is exactly
what the template's own relations would have caught, and the pair deletes it with the formula.

## Why this artifact has each class

{why}

## Provenance

Classes populated from the published suite carry a verbatim citation with a page reference:

{cites}

Ours: {ours}. These carry no citation and a rationale instead, and the rationale names the MEASURED
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
"""


def main() -> int:
    text = render()
    changed = not DOC.is_file() or DOC.read_text(encoding="utf-8") != text
    DOC.write_text(text, encoding="utf-8")

    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    baseline = {"version": FAULT_MODEL_VERSION, "digest": model_digest(), "table": canonical_table()}
    BASELINE.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{'wrote' if changed else 'unchanged'} {DOC.relative_to(REPO)}  digest {model_digest()[:16]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
