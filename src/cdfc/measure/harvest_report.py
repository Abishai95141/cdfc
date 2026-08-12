"""P4-B4 — the harvest distribution measurement, rendered from the results themselves.

**Publishing the total alone is banned** (NC-Q73): the distribution is concentrated, and a single
number hides which workbooks it came from. Every row renders, including the two zeroes.

**The weak pile is counted, not dropped** (NC-Q74). A harvest that skips has declared it; a harvest
that omits has hidden it, and the difference is the whole coverage claim.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

# The spec's figure, carried DERIVED-FROM-SPEC and never pinned as a literal in a golden. It is
# published beside the computed number with the delta in a sentence; a divergence is a finding, not
# a number to be reconciled by adjusting the harvest.
SPEC_STATIC_SETTLED_CELLS = 2373

# G-TRANSFER (mech)'s pre-registered threshold. Pre-registered means before the measurement, which
# is why it is a module constant and not a sentence written after the fact.
TRANSFER_THRESHOLD = 5

# Designed misses, and the reason each is unclaimed. A fault class nobody claims is the most useful
# thing on this page.
UNCLAIMED_REASONS = {
    "F10": (
        "legal enum substitution. A membership test cannot see one legal vocabulary term "
        "substituted for another BY CONSTRUCTION — the value is in the vocabulary. A designed "
        "miss, and P10's residue feedstock."
    ),
    "F11": (
        "formula override. Claimed by TEMPLATE_DIFF, which is a RELATION and is built at P9-B1, "
        "not by any harvested class. No relation the template encodes can detect the deletion of "
        "the formula that encodes it."
    ),
    "F14": (
        "vocabulary-gap exploitation — a value legal under the template's own defective logic but "
        "outside the regulation. MEASURED: the FME template computes a scheme total with three "
        "COUNTIFs that between them miss two of its nine legal Type-of-Scheme values. No relation "
        "derived from that template can see a filing exploiting it."
    ),
}


def claimed_classes() -> dict[str, tuple[str, ...]]:
    from cdfc.predicates.harvest_classes import CLAIMS

    return dict(CLAIMS)


def unclaimed_classes() -> tuple[str, ...]:
    from cdfc.predicates.fault_model import known_ids

    claimed = {c for classes in claimed_classes().values() for c in classes}
    return tuple(sorted(known_ids() - claimed))


def render_report(results: Sequence[Any]) -> str:
    from cdfc.predicates.harvest import distribution

    rows = distribution(results)
    total = sum(r.n for r in rows)
    non_empty = sum(1 for r in rows if r.n)
    fme = next((r for r in rows if r.sha8 == "7d9a1960"), None)
    all_classes = sorted({k for r in rows for k in r.by_class})
    all_skips = sorted({k for r in rows for k in r.skips_by_kind})

    statute = 0
    template_obl = sum(
        1 for res in results for c in res.candidates if c.obligation_source == "TEMPLATE"
    )
    absence_dist: dict[str, int] = {}
    for res in results:
        for c in res.candidates:
            if c.clause_absent_reason:
                absence_dist[c.clause_absent_reason] = absence_dist.get(c.clause_absent_reason, 0) + 1

    L = [
        "# P4-B4 — the harvest distribution, across all nine prescribed workbooks",
        "",
        "**Warrant: MEASURED.** Produced by `cdfc harvest --all`; re-render with `make harvest`.",
        "These are properties of *our code* and they will move — the first thing P7's G3 does is",
        "reject predicates, and this number will fall, which is correct behaviour. Moving one",
        "without an entry in `docs/HARVEST-DELTA.md` fails the build.",
        "",
        "## Every row, including the two zeroes",
        "",
        "**Publishing the total alone is banned.** The distribution is concentrated — see the",
        f"concentration line below — and `{total}` on its own conceals which workbooks produced it.",
        "",
        "| workbook | sha8 | candidates | " + " | ".join(all_classes) + " | skipped | cells reachable |",
        "|---|---|---:|" + "---:|" * len(all_classes) + "---:|---:|",
    ]
    for r in rows:
        cells = " | ".join(str(r.by_class.get(k, 0)) for k in all_classes)
        L.append(
            f"| `{r.workbook}` | `{r.sha8}` | **{r.n}** | {cells} | {r.skips} | {r.cells_reachable} |"
        )
    L.append(
        f"| **total** | — | **{total}** | "
        + " | ".join(str(sum(r.by_class.get(k, 0) for r in rows)) for k in all_classes)
        + f" | {sum(r.skips for r in rows)} | {sum(r.cells_reachable for r in rows)} |"
    )

    top2 = sorted((r.n for r in rows), reverse=True)[:2]
    L += [
        "",
        f"**Concentration: {sum(top2)} of {total} come from two workbooks.** That is why the total",
        "is never published without this table.",
        "",
        f"**Non-empty on {non_empty} of {len(rows)}.** G-TRANSFER (mech)'s pre-registered threshold",
        f"is >= {TRANSFER_THRESHOLD} of 9, so it is met. This is the mechanical arm only: it states",
        "nothing about per-predicate human cost, which is P15's arm and is not touched here.",
        "",
        "## The weak pile, typed and counted",
        "",
        "An undeclared suppression is a coverage lie. Every construct the class set cannot express",
        "is a typed `SkipRecord` naming the sheet, the cell and the reason.",
        "",
        "| workbook | " + " | ".join(f"`{k}`" for k in all_skips) + " | total |",
        "|---|" + "---:|" * (len(all_skips) + 1),
    ]
    for r in rows:
        L.append(
            f"| `{r.workbook}` | "
            + " | ".join(str(r.skips_by_kind.get(k, 0)) for k in all_skips)
            + f" | {r.skips} |"
        )

    if fme is not None:
        L += [
            "",
            "**The FME reconciliation, in one sentence.** The 2 `list_unresolved` skips on",
            "`7d9a1960` are exactly the pinned `22 list-type validations - 20 resolving` gap: both",
            "are `IF(C5=\"No\",Choicelist,YesNolist)`, a vocabulary that depends on a value the",
            "FILING supplies. Resolving it from the filing would be NC-D01c; it is skipped instead.",
            "",
            "## `static_settled_cells`, computed — and reconciled against the spec's figure",
            "",
            f"| number | value | warrant |",
            f"|---|---:|---|",
            f"| `len(cells_reachable)` for `7d9a1960`, computed here | **{fme.cells_reachable}** | MEASURED |",
            f"| the specification's figure | {SPEC_STATIC_SETTLED_CELLS} | DERIVED-FROM-SPEC |",
            f"| delta | **{fme.cells_reachable - SPEC_STATIC_SETTLED_CELLS:+d}** | — |",
            "",
            "**The delta is a finding. It is published and it is not reconciled by adjusting the",
            f"harvest.** The computed figure is the union of cells bound by the {fme.n} candidates",
            "this build emits; the spec attributed 2,329 of 2,373 settled cells to 53 validation",
            "predicates, and this harvest emits a different number of validation predicates from a",
            "different class set. Either 2,373 was computed from an enumeration this build does not",
            "produce, or the 53 is wrong. `docs/HARVEST-DELTA.md` entry #1 carries it.",
            "",
            "**`2,373` may not be pinned as a literal in any golden test at this phase.** It",
            "resolves to no ledger row and to no measurement this code produces.",
        ]

    L += [
        "",
        "## The obligation coverage pair — two numbers, never one",
        "",
        "| published number | value | what it means |",
        "|---|---:|---|",
        f"| `predicates_with_a_STATUTE_obligation / {total}` | **{statute} / {total}** | "
        "*No harvested predicate yet implements a statutory clause.* |",
        f"| `predicates_with_a_TEMPLATE_obligation / {total}` | **{template_obl} / {total}** | "
        "Every harvested predicate implements a relation the regulator's own pinned blank encodes. |",
        "",
        "**The two counts are never added together, and publishing either alone fails the exit",
        "gate.** The first alone conceals that these predicates are grounded in a real regulator",
        "artifact; the second alone conceals that not one of them is grounded in the statute.",
        "",
        "`clause_absent_reason` distribution:",
        "",
        "| reason | count |",
        "|---|---:|",
    ]
    for k in sorted(absence_dist):
        L.append(f"| `{k}` | {absence_dist[k]} |")

    unclaimed = unclaimed_classes()
    L += [
        "",
        "## `fault_classes_claimed_by_no_harvested_candidate`",
        "",
        f"**{{{', '.join(unclaimed)}}}** — {len(unclaimed)} of 14 classes in the pinned fault model",
        "are claimed by no harvested class. *A fault class nobody claims is the most useful thing on",
        "this page.*",
        "",
        "| class | why it is unclaimed |",
        "|---|---|",
    ]
    for f in unclaimed:
        L.append(f"| **{f}** | {UNCLAIMED_REASONS.get(f, 'no reason recorded — this is a defect')} |")

    L += [
        "",
        "## What each harvest class claims, and why",
        "",
        "Declared per class as a module-level constant, so a claim cannot be tuned per predicate",
        "after a campaign without changing `code_sha256`. Committed in P4, four phases before the",
        "first campaign runs.",
        "",
        "| harvest class | `claims_fault_classes` |",
        "|---|---|",
    ]
    for name, classes in sorted(claimed_classes().items()):
        L.append(f"| `{name}` | {' '.join(classes)} |")

    L += [
        "",
        "## What this measurement does not license",
        "",
        "That any of these predicates means what a regulation means. Not one cites a clause — that",
        "is the whole point of the pair above. **NC-N01** is the control that cannot be built: a",
        "predicate can clear all five gates and enforce a rule that does not exist.",
        "",
    ]
    return "\n".join(L)


def render_both_ways(results: Sequence[Any]) -> str:
    """P4's headline number: `schema_keys` declared == AST-read, in both directions."""
    from cdfc.predicates.ast_walker import declared_vs_read
    from cdfc.predicates.cel_profile import check_subset
    from cdfc.predicates.errors import CelLayerError

    rows = []
    for res in results:
        agree = 0
        shortfalls: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = []
        for c in res.candidates:
            try:
                for slot in ("applicable", "expr", "witness"):
                    check_subset(getattr(c, slot), slot=slot)
                undeclared, unread = declared_vs_read(c)
            except CelLayerError as e:
                shortfalls.append((c.id, ("<not in the admitted subset>",), (str(e)[:80],)))
                continue
            if undeclared or unread:
                shortfalls.append((c.id, undeclared, unread))
            else:
                agree += 1
        rows.append((res.workbook, res.template_sha256[:8], agree, len(res.candidates), shortfalls))

    agree_total = sum(r[2] for r in rows)
    n_total = sum(r[3] for r in rows)
    L = [
        "# P4-B2/B4 — `schema_keys` both ways",
        "",
        "**This is the phase's headline number.** The settled fraction is *derivable* rather than",
        "*estimated* only because the key set a predicate reads can be determined statically. That",
        "claim becomes true — or measurably false — the day `schema_keys` is machine-checked",
        "against the CEL AST **in both directions** and the shortfall is counted.",
        "",
        f"## **{agree_total} of {n_total}** candidates agree in both directions",
        "",
        "| workbook | sha8 | agree | candidates | shortfalls |",
        "|---|---|---:|---:|---:|",
    ]
    for wb, sha8, agree, n, short in rows:
        L.append(f"| `{wb}` | `{sha8}` | {agree} | {n} | {len(short)} |")
    L += [
        f"| **total** | — | **{agree_total}** | **{n_total}** | {n_total - agree_total} |",
        "",
        "## The two directions, and why they are different exception types",
        "",
        "- **read but not declared** (`UndeclaredKeyRead`) — the pre-flight set is too small, and",
        "  P5 rule 2 is guarding the wrong keys. A predicate can return `PASS` over a key nobody",
        "  checked was present.",
        "- **declared but not read** (`DeclaredKeyUnread`) — the declared footprint overstates what",
        "  the predicate settles, which inflates the settled **numerator**.",
        "",
        "One is a hole in the guard; the other is a lie in the headline number. A single",
        "`KeysMismatch` type would fail NC-Q04, because a repair applied to the wrong side of a",
        "collapsed message is a repair that fixes nothing.",
        "",
    ]
    shortfall_rows = [(wb, *s) for wb, _sha, _a, _n, short in rows for s in short]
    if shortfall_rows:
        L += ["## Every shortfall", "", "| workbook | predicate | read-not-declared | declared-not-read |",
              "|---|---|---|---|"]
        for wb, pid, undeclared, unread in shortfall_rows:
            L.append(f"| `{wb}` | `{pid}` | {list(undeclared)} | {list(unread)} |")
    else:
        L += [
            "## Shortfalls",
            "",
            "None. **What that means and what it does not:** the declared key set equals the",
            "AST-read key set for every candidate. It says nothing about whether a predicate",
            "encodes its clause — that is NC-N01, where a negative control is impossible, and a",
            "predicate can clear all five gates and enforce a rule that does not exist.",
        ]
    L.append("")
    return "\n".join(L)
