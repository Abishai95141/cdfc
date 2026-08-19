"""M-CEIL — the FILING-CHECKABLE ceiling for prose statutory rules.

An earlier estimate said roughly 176 of 531 `shall` clauses carry testable content, counted by
looking for a quantity, a comparator or a temporal marker in the clause. Then regulation 8(1) was
read properly. It is INSIDE that 176 by pattern -- it has a comparator -- and it is still not
checkable against this filing, for two independent reasons:

    the threshold is not in the clause   "as specified in Second Schedule ... or such other
                                          amount as may be specified by the Authority"
    the field is not a figure            the only net-worth cell in the whole return is
                                          `8. Compliance Status!C6`, a yes/no attestation

So the pattern count is an OVER-estimate and the size of the over-count is unknown. This measures
it, over the pinned instrument and the pinned return, with the two subtractions applied
separately so each one can be argued with.

    STAGE 1   every `shall` clause -> one of six classes, closed
    STAGE 2   every labelled field -> FACT or ATTESTATION
    CEILING   clauses that survive BOTH subtractions

THE CLASSIFIER IS CRUDE AND THE OUTPUT SAYS SO. Its miss modes are published beside the number,
and the negative control is that each class must be non-empty -- a classifier that puts everything
in one bucket produces a clean-looking number and has measured nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTRUMENT = ROOT / "corpus/instruments/statute-fm-regulations-2025.text.json"

# --- STAGE 1 vocabulary. Closed, and ordered: the FIRST match wins, most-disqualifying first. ---
#
# `DELEGATED` before `QUANTIFIED` is the whole point. A clause that says "not less than the amount
# specified in the Schedule" contains a comparator AND a pointer somewhere else. Counting it as
# quantified is exactly the over-count regulation 8(1) exposed.
DELEGATION = re.compile(
    r"(as (?:may be )?specified (?:in|by)|as prescribed|in accordance with|"
    r"Schedule|as (?:may be )?determined by|such other|as the Authority may)", re.I)
# EVERY alternative is word-bounded, and the reason is a defect this classifier had on its first
# run: `Rs\.?` under re.I matches the "rs" inside "forms", "advertisers" and "matters", which put
# 228 clauses in the quantified bucket including a pure definition of "advertisement". A currency
# abbreviation that matches inside ordinary words is a classifier that measures nothing.
QUANTITY = re.compile(
    r"(\bUSD\b|\bINR\b|\bRs\b|\bper cent\b|\bpercent\b|%|\bnot less than\b|\bat least\b|"
    r"\bnot exceed\b|\bexceed(?:s|ing)?\b|\bminimum\b|\bmaximum\b|\bnot more than\b|"
    r"\bmillion\b|\bcrore\b|\blakh\b)", re.I)
TEMPORAL = re.compile(
    r"(within (?:a period of )?\w+ (?:day|days|month|months|year|years)|"
    r"\bevery (?:quarter|month|year)\b|\bannually\b|\bquarterly\b|"
    r"\bprior to\b|\bbefore the\b|\bno later than\b)", re.I)
PROVISO = re.compile(r"Provided that", re.I)
# A DEFINITION carries quantities and is not an obligation. `"control" shall include the right to
# appoint a majority ... twenty-six per cent` trips every quantity pattern and there is nothing in
# any filing to test it against -- it defines a term other clauses then use. Second over-count
# found by reading the classifier's own examples rather than its totals.
DEFINITION = re.compile(r"^\s*\(?[a-z0-9]{1,3}\)?\s*[\u201c\"][^\u201d\"]{2,60}[\u201d\"]\s+shall\s+(mean|include)", re.I)

CLASSES = ("QUANTIFIED_IN_CLAUSE", "DELEGATED_ELSEWHERE", "TEMPORAL_ONLY",
           "DEFINITION", "PROVISO_ONLY", "NO_TESTABLE_CONTENT")


def classify_clause(text: str) -> str:
    if DEFINITION.search(text):
        return "DEFINITION"
    has_q, has_t = bool(QUANTITY.search(text)), bool(TEMPORAL.search(text))
    if DELEGATION.search(text) and (has_q or has_t):
        return "DELEGATED_ELSEWHERE"
    if has_q:
        return "QUANTIFIED_IN_CLAUSE"
    if has_t:
        return "TEMPORAL_ONLY"
    if PROVISO.search(text):
        return "PROVISO_ONLY"
    return "NO_TESTABLE_CONTENT"


# --- STAGE 2. An ATTESTATION field asks the filer to CERTIFY, not to REPORT. ------------------
#
# The earlier classifier keyed on a couple of phrases and mislabelled at least one cell that reads
# as an attestation. This one keys on the grammatical shape a certification takes, and it is still
# crude: it is a regex over a label, and it is published as a FLOOR for that reason.
ATTEST = re.compile(
    r"(has been complied|is in compliance|are in compliance|has complied|"
    r"\bhas the necessary\b|\bhas put in place\b|\bconfirm(?:ed|s|ation)?\b|"
    r"\bcertif(?:y|ied|ication)\b|\bundertak(?:e|ing)\b|\bdeclare[sd]?\b|"
    r"\bwhether\b|\bhas been (?:done|carried out|maintained|adhered)|"
    r"\byes\s*/\s*no\b|\bcomplied with\b|\bin place\b)", re.I)
# Anything asking for a number, a name or a date is a FACT even if it also trips the above.
FACTUAL = re.compile(
    r"(\bnumber\b|\bamount\b|\bvalue\b|\btotal\b|\bname\b|\bdate\b|\bAUM\b|"
    r"\bNAV\b|\bcount\b|\bISIN\b|\bLEI\b|\baddress\b|\bemail\b|\bPAN\b)", re.I)


def classify_field(label: str) -> str:
    if FACTUAL.search(label):
        return "FACT"
    return "ATTESTATION" if ATTEST.search(label) else "FACT"


def shall_clauses(doc: dict) -> list[tuple[str, str]]:
    text = doc["text"]
    out = []
    for u in doc["units"]:
        a, b = u["span"]
        seg = text[a:b]
        if re.search(r"\bshall\b", seg):
            out.append((u["key"], seg))
    return out



# --- STAGE 2 — the return's own fields, read from the workbook ------------------------------
FME = ROOT / "fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"


def labelled_fields() -> list[tuple[str, str]]:
    """(A1 ref, label) over THE REPO'S OWN FIELD SURFACE, not a second reader.

    `surface_for` is the same 3,747-cell denominator every run is scored over. Re-deriving the
    unlocked set here with a private rule would be a second list, and the one that drifts is the
    one nobody is reading. The label is the nearest non-empty text cell to the LEFT on the same
    row; a field with no such neighbour is SKIPPED rather than guessed.
    """
    sys.path.insert(0, str(ROOT / "src"))
    from openpyxl import load_workbook

    from cdfc.measure.p5_run import surface_for

    total, refs = surface_for(FME)[0], surface_for(FME)[1]
    want: dict[str, set[str]] = {}
    for r in refs:
        sheet, cell = r.rsplit("!", 1)
        want.setdefault(sheet, set()).add(cell)

    wb = load_workbook(FME, data_only=True)          # READER ONLY -- never saved (NC-P04)
    out: list[tuple[str, str]] = []
    adjacent: list[tuple[str, str]] = []
    for ws in wb.worksheets:
        if ws.title not in want:
            continue
        for row in ws.iter_rows():
            texts = {c.column: c.value.strip() for c in row
                     if isinstance(c.value, str) and c.value.strip()}
            for c in row:
                if c.coordinate not in want[ws.title]:
                    continue
                left = [col for col in texts if col < c.column]
                if left:
                    out.append((f"{ws.title}!{c.coordinate}", texts[max(left)]))
                    if c.column - 1 in texts:
                        adjacent.append((f"{ws.title}!{c.coordinate}", texts[c.column - 1]))

    # THE LABELLED POPULATION IS A PROPERTY OF THE RULE, NOT OF THE RETURN, AND THE RULE WAS
    # NEVER PINNED. Three readings of "this field has a label" give three different denominators
    # over the same 3,747 cells, and the DISTINCT-label count is what gives the loose rule away:
    # it labels ROWS, reusing one row header across every column in the row. A count that moves
    # sixfold with an unwritten convention is the count-vs-contents defect again, on the
    # denominator of the semantic half.
    print(f"  field surface (the run's own denominator)   {total}")
    print(f"  RULE A  nearest text anywhere to the left   {len(out)} of {total}"
          f"   distinct labels {len(set(l for _, l in out))}")
    print(f"  RULE B  immediately adjacent cell is text   {len(adjacent)} of {total}"
          f"   distinct labels {len(set(l for _, l in adjacent))}")
    print("  RULE C  the spike's unrecorded rule         724 of 3747   NOT REPRODUCIBLE")
    print("     -- `docs/spike/README.md` publishes 724 labelled fields and 702/22 FACT vs")
    print("        ATTESTATION over them. Neither rule here yields 724, and the spike did not")
    print("        record which rule it used. The split is therefore reported below over RULE B,")
    print("        which labels FIELDS; RULE A labels rows and must not be used as a denominator.")
    return adjacent


def stage2() -> tuple[int, int, list[tuple[str, str]]]:
    print("\n=== M-CEIL STAGE 2 — the return's own fields ===")
    fields = labelled_fields()
    fact = [f for f in fields if classify_field(f[1]) == "FACT"]
    att = [f for f in fields if classify_field(f[1]) == "ATTESTATION"]
    print(f"    FACT-shaped                     {len(fact)} of {len(fields)}")
    print(f"    ATTESTATION-shaped              {len(att)} of {len(fields)}   <- a FLOOR, see below")
    by_sheet = {}
    for ref, _ in att:
        by_sheet[ref.split("!")[0]] = by_sheet.get(ref.split("!")[0], 0) + 1
    print(f"    attestations by sheet           {dict(sorted(by_sheet.items()))}")
    print("\n  five attestation labels, verbatim, so the classifier can be argued with:")
    for ref, lab in att[:5]:
        print(f"    {ref:34} {lab[:78]}")
    return len(fact), len(att), att


def stage0(doc: dict, clauses: list) -> None:
    """Reproductions of three numbers this repository has published. Two do not reproduce."""
    text = doc["text"]
    provisos = [seg for _k, seg in clauses if re.search(r"Provided that", seg, re.I)]
    occurrences = len(re.findall(r"Provided that", text, re.I))
    print("=== M-CEIL STAGE 0 — reproducing three published numbers ===")
    print(f"  characters in the pinned text                      {len(text)}")
    naive = re.findall(r"(?m)^\s*(\d{1,3})\.\s", text)
    print(f"  REPRODUCES  naive line-anchored regulation numbers  {len(naive)} distinct "
          f"{len(set(naive))}   (published: 3)")
    print(f"  CORRECTS    `Provided that` occurrences in the text {occurrences}   "
          f"(docs/EXPERIMENT-PROGRAMME says 93)")
    print(f"  CORRECTS    shall-units carrying a proviso          {len(provisos)} of {len(clauses)}"
          f"   (docs/spike/README says 106 of 531)")
    print("     -- the published 106 is not reproducible from the pinned text by any reading of")
    print("        `clause` this script can construct. The count over `shall`-bearing units is")
    print("        the one below; the count over ALL units is a different, larger population.")



def main() -> int:
    doc = json.loads(INSTRUMENT.read_text(encoding="utf-8"))
    clauses = shall_clauses(doc)
    stage0(doc, clauses)

    counts = dict.fromkeys(CLASSES, 0)
    examples: dict[str, tuple[str, str]] = {}
    for key, seg in clauses:
        c = classify_clause(seg)
        counts[c] += 1
        examples.setdefault(c, (key, re.sub(r"\s+", " ", seg)[:150]))

    print("=== M-CEIL STAGE 1 — every `shall` clause in the pinned instrument ===")
    print(f"  pinned units {len(doc['units'])}   units containing `shall` {len(clauses)}")
    for c in CLASSES:
        print(f"    {c:24} {counts[c]:5} of {len(clauses)}")

    # NEGATIVE CONTROL. A classifier that returns one class for everything scores a clean number
    # and has measured nothing. Every class must be reachable ON THIS CORPUS.
    empty = [c for c in CLASSES if counts[c] == 0]
    print("\n  negative control — every class reachable on this corpus:",
          "PASS" if not empty else f"FAIL, unreachable: {empty}")
    print("\n  one real clause per class, so the buckets can be argued with:")
    for c in CLASSES:
        if c in examples:
            k, t = examples[c]
            print(f"    {c:24} {k}  {t}")

    survivors = counts["QUANTIFIED_IN_CLAUSE"] + counts["TEMPORAL_ONLY"]
    print(f"\n  SUBTRACTION 1 — the threshold must be IN the clause.")
    print(f"    pattern-testable (quantity or temporal, ignoring delegation) "
          f"{survivors + counts['DELEGATED_ELSEWHERE']} of {len(clauses)}")
    print(f"    of which the value lives ELSEWHERE  {counts['DELEGATED_ELSEWHERE']} of {len(clauses)}")
    print(f"    SURVIVING subtraction 1             {survivors} of {len(clauses)}")

    n_fact, n_att, _ = stage2()

    print("\n=== THE CEILING, AND WHAT IT IS NOT ===")
    print(f"  clauses whose threshold is IN the clause          {survivors} of {len(clauses)}")
    print(f"  return fields that ask for a FACT                 {n_fact} of {n_fact + n_att}")
    print("  The ceiling is the INTERSECTION and it is NOT the product of these two. Binding a")
    print("  surviving clause to a FACT field is the rule->field binding problem, and this")
    print("  measurement does not perform it -- it bounds the ceiling from above, twice:")
    print(f"    upper bound from the instrument side             {survivors} of {len(clauses)}")
    print("    the earlier pattern-only estimate was 176 of 531, counted without subtracting")
    print("    delegation or definitions. THAT is the number this corrects.")
    print("\n  MISS MODES, published with the number:")
    print("    1. the pinned units are PAGE-SENTENCES, not provisions. A clause split across two")
    print("       units is classified twice, on fragments -- `p0143.s0018` opens mid-sentence at")
    print("       a bare parenthesised voting-rights threshold. The segmenter fixes this, and")
    print("       lands every count here is over a fragment population.")
    print("    2. DELEGATED_ELSEWHERE is detected by phrase. A clause pointing at a Schedule")
    print("       without one of those phrases is scored as quantified.")
    print("    3. STAGE 2 reads the label to the LEFT. A field labelled above its column is")
    print("       skipped rather than guessed, so the labelled population is a floor.")
    return 0 if not empty else 1


if __name__ == "__main__":
    sys.exit(main())
