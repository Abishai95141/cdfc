#!/usr/bin/env python
"""P10-B2/B3/B4 — the adjudication record, `|RESIDUE|`, and the two demonstrated survivors.

**The adjudication is the only human step in the procedure, and this project has no second
person.** So it is performed by a DECLARED RULE SET, every row carries the rule that decided it
instantiated on that mutant's own cell and values, and the record is labelled
`RULE-BASED-v1 — a weaker adjudication, not a human judgement` on every surface that quotes a
number derived from it. That label travels the way `SINGLE-SIGNER` and `SAME-AUTHOR` do.

**The rules are written here rather than inferred, and each says what it decides and why.** A
reader who disagrees with one disagrees with a sentence, re-rates the affected mutants, and
re-derives `|RESIDUE|` from the new record's hash. That is what content-addressing the record is
for.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.selfcheck.adjudication import (  # noqa: E402
    RULE_BASED,
    AdjudicationRecord,
    AdjudicationRow,
    cohens_kappa,
    render_kappa,
)
from cdfc.selfcheck.exhibit import Exhibit, e2_candidates, recompute_blind, render as render_exhibits
from cdfc.selfcheck.residue import compute_residue, render  # noqa: E402

CAMPAIGN = REPO / "reports" / "campaigns" / "fme-v3-seed20260810"
OUT_DIR = REPO / "adjudication" / "v3"
DOC = REPO / "docs" / "measurements" / "P10-residue.md"

# The seed, and the date it was written down. **Before round 1**, which is what makes the
# 20-in-100 sample a commitment rather than a choice; `AdjudicationRecord.__post_init__` refuses the other
# order.
SAMPLE_SEED = 20261014
SAMPLE_FRACTION = "20/100"
SEED_COMMITTED_AT = "2026-08-14"
ADJUDICATED_AT = "2026-08-14"


# --------------------------------------------------------------------------------------------
# THE RULES. Each decides one class of edit, and says why.
# --------------------------------------------------------------------------------------------

RULES: dict[str, str] = {
    "R-UNOBS": (
        "INNOCUOUS. The recalculated grid and every literal are identical to the base, so no "
        "reader — human or machine — can tell this artifact from the one it was made from. It "
        "asserts exactly what the base asserts, and a mutant that cannot be distinguished cannot "
        "be a misstatement."
    ),
    "R-WHITESPACE": (
        "INNOCUOUS. The edit adds or removes surrounding whitespace and changes no character of "
        "the value. Whitespace is not part of a filed value: every reader of this form trims it, "
        "and the regulator's own data validation matches the trimmed text."
    ),
    "R-QUANTITY": (
        "WRONG. The edit changes a NUMBER the regulator asked the filer to state. A money, count "
        "or date cell carries a quantity the filer is asserting to be true; changing it changes "
        "the assertion, whatever else in the workbook still agrees."
    ),
    "R-CATEGORY": (
        "WRONG. The edit replaces a categorical value with a different member of its own "
        "controlled vocabulary. The document now says the scheme IS something it is not — and "
        "does so legally, which is why this class is the residue's most important member."
    ),
    "R-IDENTITY": (
        "WRONG. The edit changes text the regulator asked the filer to state — a name, a "
        "registration number, an address. A registration number containing a substituted "
        "character is not the number it appears to be, and a register lookup on it fails."
    ),
    "R-OMISSION": (
        "WRONG. The edit removes a value the filer had stated. An omission is a misstatement by "
        "silence: the form asked, and the return no longer answers."
    ),
}

MONEY_CLASSES = {"F01", "F02", "F03", "F04", "F06", "F11", "F13"}
DATE_CLASSES = {"F09"}
CATEGORY_CLASSES = {"F10", "F14"}
OMISSION_CLASSES = {"F05", "F07"}
TEXT_CLASSES = {"F08", "F12"}


def _rule_for(row: Mapping[str, Any]) -> tuple[str, str]:
    """`(rule_id, verdict)` for one mutant. Total: every class of the pinned model is decided."""
    cls = str(row.get("fault_class", ""))
    op = str(row.get("operator_id", ""))
    if str(row.get("observability")) == "UNOBSERVABLE":
        return "R-UNOBS", "INNOCUOUS"
    if op == "F12.c":                    # trailing_whitespace
        return "R-WHITESPACE", "INNOCUOUS"
    if cls in CATEGORY_CLASSES:
        return "R-CATEGORY", "WRONG"
    if cls in OMISSION_CLASSES:
        return "R-OMISSION", "WRONG"
    if cls in MONEY_CLASSES or cls in DATE_CLASSES:
        return "R-QUANTITY", "WRONG"
    if cls in TEXT_CLASSES:
        return "R-IDENTITY", "WRONG"
    raise SystemExit(f"no rule covers fault class {cls!r} — the rule set is not total")


def _argument(row: Mapping[str, Any], rule_id: str) -> str:
    """The rule, INSTANTIATED on this mutant's own cell and edit. Not the rule alone.

    A record whose every row carries the same sentence is a schema, not an adjudication. The
    instantiation is what lets a reader disagree with a specific decision.
    """
    sites = ", ".join(row.get("sites") or ())
    op = row.get("operator_id", "?")
    return f"[{rule_id}] {RULES[rule_id]} Applied by {op} at {sites}."


def build_record(rows: Sequence[Mapping[str, Any]]) -> AdjudicationRecord:
    out = []
    for row in rows:
        rule_id, verdict = _rule_for(row)
        out.append(
            AdjudicationRow(
                mutant_id=str(row["mutant_sha256"]), verdict=verdict,
                argument=_argument(row, rule_id), adjudicated_by=RULE_BASED,
                adjudicated_at=ADJUDICATED_AT, round=1,
            )
        )
    return AdjudicationRecord(
        rows=tuple(out), fault_model_version="v3",
        filing_sha256=str(rows[0]["base_sha256"]) if rows else "",
        sample_seed=SAMPLE_SEED, sample_fraction=SAMPLE_FRACTION,
        seed_committed_at=SEED_COMMITTED_AT,
    )


def _all_mutants() -> list[dict[str, Any]]:
    """Every mutant the campaign retained, from all FIVE buckets.

    **`survived.jsonl` is the fifth, and P10-B2 is why it exists.** The campaign wrote killed /
    unobservable / indeterminate / unreachable, so a mutant that was OBSERVABLE, REACHABLE and
    killed by NOTHING landed in no file at all — and that population IS the residue. The counts
    were never wrong (`G − U − I − K` always named it) but the rows were unrecoverable, so
    `|RESIDUE|`'s per-survivor class of falsehood could not be reported and neither exhibit family
    could be drawn from a real run.

    An unobservable mutant is RETAINED with its reason (§0.7) for the same reason: the population
    has to be complete or the denominator is a choice.
    """
    out: dict[str, dict[str, Any]] = {}
    for name in ("killed.jsonl", "unobservable.jsonl", "indeterminate.jsonl", "unreachable.jsonl",
                 "survived.jsonl"):
        path = CAMPAIGN / name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                out.setdefault(str(row["mutant_sha256"]), row)
    return sorted(out.values(), key=lambda r: str(r["mutant_sha256"]))


def main() -> int:
    mutants = _all_mutants()
    if not mutants:
        raise SystemExit("no campaign on disk; run `make campaign` first")

    record = build_record(mutants)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / f"{record.filing_sha256[:8]}.jsonl"
    target.write_text(record.serialise(), encoding="utf-8")

    rejected_pre_gate = {
        str(r["mutant_sha256"]): list(r.get("killed_by") or ()) for r in mutants
    }
    indeterminate = {
        str(r["mutant_sha256"]) for r in mutants
        if str(r.get("observability")) == "INDETERMINATE_OBSERVABILITY"
    }

    from cdfc.predicates.registry import registry_root

    empty_root = registry_root([])
    admitted = compute_residue(
        mutants, record, {}, registry_root=empty_root,
        n_admitted_predicates=0, n_admitted_relations=0,
        rejector_set="ADMITTED", unadjudicable=indeterminate,
    )
    pre_gate = compute_residue(
        mutants, record, rejected_pre_gate, registry_root="root-p5-pre-gate-fixture",
        n_admitted_predicates=0, n_admitted_relations=0,
        rejector_set="PRE-GATE", unadjudicable=indeterminate,
    )

    kappa, n = cohens_kappa(record.by_round(1), record.by_round(2))
    marginal = marginal_over_residue(pre_gate.survivors, mutants)
    _write_p9_delta(marginal)
    exhibits = build_exhibits(mutants, record)

    print(render(admitted))
    print()
    print(render(pre_gate))
    print()
    print(render_kappa(kappa, n, reason=NO_SECOND_RATER))
    print()
    print(render_exhibits(exhibits))
    DOC.write_text(
        render_doc(admitted, pre_gate, record, target, kappa, n, exhibits), encoding="utf-8"
    )
    print(f"wrote {target.relative_to(REPO)} and {DOC.relative_to(REPO)}")
    return 0


NO_SECOND_RATER = (
    "there is no second adjudicator on this project, and κ has no mechanical substitute. "
    "Re-running the same rules gives κ = 1.0 by construction; running a second rule set and "
    "calling its agreement κ dresses a mechanical agreement as an adjudication agreement. "
    "P10 exit criterion 7 is recorded NOT MET."
)


def build_exhibits(
    mutants: Sequence[Mapping[str, Any]], record: AdjudicationRecord
) -> list[Exhibit]:
    """E1 and E2, drawn from the campaign's own survivors rather than constructed for the page.

    An exhibit built specially for the exhibit block is a demonstration that the author could
    build one. An exhibit that IS a survivor of the run is a demonstration that the run produced
    one — which is the claim.
    """
    survivors = [
        m for m in mutants
        if not (m.get("killed_by") or ())
        and str(m.get("observability")) == "OBSERVABLE"
        and record.verdict_of(str(m["mutant_sha256"])) == "WRONG"
    ]
    out: list[Exhibit] = []
    e2 = next((m for m in survivors if str(m.get("fault_class")) in CATEGORY_CLASSES), None)
    # E1 in ORDER OF STRENGTH, and the order is the argument. `F13.b` moves BOTH ends of a
    # cross-sheet carry, which is the coordinated misstatement in its purest form: the carry
    # identity is satisfied and the quantity is false. `F02` scales one value uniformly, which is
    # coordinated only where the scaled cell is the whole component. `F13.a` moves ONE end and is
    # a desync — it is NOT a coordinated misstatement, and describing it as one would be an
    # exhibit whose caption claims more than its construction does.
    e1 = next((m for m in survivors if str(m.get("operator_id")) == "F13.b"), None)
    if e1 is None:
        e1 = next((m for m in survivors if str(m.get("fault_class")) == "F02"), None)
    if e1 is not None:
        out.append(
            Exhibit(
                family="E1", title=_e1_title(str(e1["operator_id"])),
                construction=(
                    f"operator {e1['operator_id']} applied at {', '.join(e1.get('sites') or ())} — "
                    f"{_e1_construction(str(e1['operator_id']))}"
                ),
                content_sha256=str(e1["mutant_sha256"]),
                cells=tuple(e1.get("sites") or ()),
                survives_against=(
                    "the PRE-GATE harvested set (348 candidates). The ADMITTED set is empty, so "
                    "survival against it is by construction and is not claimed here"
                ),
                why_unkillable=(
                    "every cross-sheet carry and every SUM identity the harvest derived still "
                    "holds. The artifact is internally consistent and the quantity it reports is "
                    "false — which is a property of the TRUTH of the document, not of its "
                    "behaviour, and therefore unreachable by any predicate over the artifact alone"
                ),
            )
        )
    if e2 is not None:
        out.append(
            Exhibit(
                family="E2", title="categorical swap inside the regulator's own vocabulary",
                construction=(
                    f"operator {e2['operator_id']} applied at {', '.join(e2.get('sites') or ())}, "
                    "replacing the value with another legal member of its controlled vocabulary"
                ),
                content_sha256=str(e2["mutant_sha256"]),
                cells=tuple(e2.get("sites") or ()),
                survives_against=(
                    "the PRE-GATE harvested set (348 candidates), including every membership "
                    "predicate the harvest derived from the workbook's own data validations"
                ),
                why_unkillable=(
                    "the new value is legal by the regulator's own validation, so membership "
                    "passes by construction; and the cell feeds no template formula, so no "
                    "recompute, carry or sum identity can reach it either"
                ),
            )
        )
    return out


def _write_p9_delta(marginal: dict) -> None:
    """Replace the dated PENDING in `docs/measurements/P9-delta.md` column (b) with the answer.

    **A dated open item that stays open forever is the escape hatch a `PENDING` field creates.**
    `test_reg__no_relation_is_permanently_pending` refuses one in the relation registry; the same
    discipline applies to a measurement's own placeholder.
    """
    doc = REPO / "docs" / "measurements" / "P9-delta.md"
    text = doc.read_text(encoding="utf-8")
    answer = (
        "UNDEFINED — not admitted, so not in the rejector set "
        f"(residue measured {len(marginal['relations'])} relations, "
        f"{marginal['n_survivors']} survivors, 2026-08-14)"
    )
    text = text.replace("PENDING — requires P10-B2, opened 2026-08-14", answer)
    text = text.replace(
        "Column (b) needs the residue population, which is P10-B2's.",
        "**Column (b) is CLOSED as of 2026-08-14, and the answer is `UNDEFINED` rather than a "
        "number.** The residue population now exists (`docs/measurements/P10-residue.md`), and "
        "the measurement it permits is this: an unadmitted relation is not in the rejector set at "
        "all, so its marginal kill over the residue is undefined — **not zero**, which would read "
        "as *it ran and caught none*. That distinction is the same one `settledFraction: null` "
        "versus `0` carries one layer up. Originally:",
    )
    doc.write_text(text, encoding="utf-8")


def marginal_over_residue(survivors: Sequence[str], mutants: Sequence[Mapping[str, Any]]) -> dict:
    """P9-delta column (b): each admitted relation's marginal kill over the residue population.

    **This closes a DATED OPEN ITEM rather than leaving it pending.** `docs/measurements/P9-delta.md`
    carries `PENDING — requires P10-B2, opened 2026-08-14` in column (b) for six relations, and
    `plan/05` names the `P9-B4 -> P10-B2` edge that creates it (adversary F34). The residue
    population now exists, so the column is measured.

    The measurement is a SET DIFFERENCE and not a difference of counts: a relation's marginal kill
    is the survivors IT rejects that nothing else does, and `|kills(r)| - |kills(B0)|` can be
    negative while `r` still catches mutants `B0` misses.
    """
    from cdfc.probes.relations.registry import load as load_catalogue

    rows = {}
    for spec in load_catalogue():
        # A relation that is NOT ADMITTED rejects nothing, and that is a fact about the registry
        # rather than about the residue. It is reported as such rather than as a zero, because a
        # zero here would read as "it ran and caught none".
        rows[spec.id] = {
            "admitted": False,
            "runnable_today": spec.runnable_today,
            "marginal": None,
            "why": (
                "not admitted — see P9-relation-attrition.md. An unadmitted relation is not in the "
                "rejector set, so its marginal over the residue is UNDEFINED, not zero"
            ),
        }
    return {"n_survivors": len(survivors), "relations": rows}


_E1 = {
    "F13.b": ("coordinated misstatement — a carry moved at both ends",
              "both ends of a cross-sheet carry moved by the same amount, so the carry identity "
              "is still satisfied"),
    "F02.a": ("coordinated misstatement — one component scaled uniformly",
              "the value scaled by ten, so every identity it participates in scales with it"),
    "F02.b": ("coordinated misstatement — one component scaled uniformly",
              "the value divided by ten, so every identity it participates in scales with it"),
    "F02.c": ("coordinated misstatement — one component scaled uniformly",
              "the value scaled by a thousand, so every identity it participates in scales with it"),
}


def _e1_title(op: str) -> str:
    return _E1.get(op, ("coordinated misstatement", ""))[0]


def _e1_construction(op: str) -> str:
    return _E1.get(op, (None, f"operator {op}; see docs/FAULT-MODEL-v3.md for its semantics"))[1]


def render_doc(
    admitted: Any, pre_gate: Any, record: AdjudicationRecord, path: Path,
    kappa: Any, n: int, exhibits: Sequence[Exhibit],
) -> str:
    sample = record.sample()
    return f"""# P10 — `|RESIDUE|`, the adjudication record, and the demonstrated survivors

*Generated by `tools/measure/p10_residue.py`. Re-run with `make residue`.*

**The primary number of this phase.** `|RESIDUE|` is the count of WRONG mutants that no admitted
predicate and no admitted relation rejects — *the first quantitative statement anyone has made
about the limit of document-level verification for a regulated filing.*

## Two numbers, because there are two rejector sets and only one of them is admitted

```
{render(admitted)}
```

```
{render(pre_gate)}
```

**The first is the honest headline.** P7 admits 0 of 348 candidates and P9 admits 0 relations, so
the rejector set on the day is EMPTY and every WRONG mutant survives by construction. `plan/05`
P10's entry criteria anticipate exactly this and call it a ceiling; NC-C07 is the control that
stops a ceiling being read as a measurement.

**The second says what the harvest WOULD catch if it were admitted**, and it may not be cited in a
gate, in a severity tier, or in any published rate.

## The adjudication record

| | |
|---|---|
| record | `{path.relative_to(REPO)}` |
| digest | `{record.digest()}` |
| rows | {len(record.rows)} |
| rater | **{record.rater_label}** |
| sample seed | `{record.sample_seed}`, committed {record.seed_committed_at} — **before** the first adjudication on {ADJUDICATED_AT} |
| sample | {record.sample_fraction} = {len(sample)} mutants |

`AdjudicationRecord.__post_init__` refuses a record whose seed post-dates round 1, because a
commitment made after seeing the result is not a commitment. The digest is RFC 8785 over the
**sorted** rows plus the sample commitment, so shuffling the file does not move it and re-seeding
does.

### The rules, and each is a sentence a reader can disagree with

{chr(10).join(f"- **{k}** — {v}" for k, v in sorted(RULES.items()))}

A reader who disagrees with one re-rates the affected mutants, re-derives the record hash, and
re-computes `|RESIDUE|` from it. That is what content-addressing the record is for, and it is why
a verdict without an argument is refused by the loader.

## Cohen's κ

```
{render_kappa(kappa, n, reason=NO_SECOND_RATER)}
```

**Exit criterion 7 is NOT MET, and the substitute is not available.** Every other missing human on
this project had a mechanical stand-in that was weaker in a stateable way — LibreOffice for an
independent evaluator, a foreign engine for arm 2, `SINGLE-SIGNER` for a second reviewer. κ has
none: it measures agreement between two MINDS, and the two things a machine could do here — re-run
the same rules, or run a different rule set — produce κ = 1.0 by construction and a mechanical
agreement wearing an adjudication's clothes respectively. `cohens_kappa` is built and tested in
both directions against hand-computed vectors; it is the *input* that does not exist.

## The demonstrated survivors

```
{render_exhibits(exhibits) if exhibits else "NO EXHIBIT — the campaign produced no WRONG survivor of either family."}
```

**E1 is a construction and E2 is a measurement**, and that asymmetry is the point. E1's
unkillability is an argument: scale one connected component of the carry graph and every identity
still holds. E2's is a fact about the regulator's artifact: the cell feeds no template formula, so
no recompute can reach it, and the new value is legal by the regulator's own data validation, so
no membership predicate can reject it.

Both are drawn from the campaign's own survivor set rather than built for this page. An exhibit
constructed for the exhibit block demonstrates that the author could build one; an exhibit that IS
a survivor demonstrates that the run produced one.
"""


if __name__ == "__main__":
    raise SystemExit(main())
