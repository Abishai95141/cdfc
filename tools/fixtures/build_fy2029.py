#!/usr/bin/env python
"""P15-B2's churn fixture — the FME workbook with FY2029-30 added to the year vocabulary.

    make fixture-fy2029

**`Dropdown!$E$3:$E$6 = {2025-26, 2026-27, 2027-28, 2028-29}`. The workbook cannot express
FY2029-30.** That is a version event already on the calendar rather than an invented one, which is
what makes it the honest churn fixture: every membership predicate carrying that vocabulary would
FAIL a valid FY2029-30 filing, and a predicate that fails valid filings must stop settling.

## TWO parts, not one. The plan said one, and the workbook says otherwise

`plan/07` specifies *"rewrite exactly one worksheet XML (the `Dropdown` sheet)"* and a test
asserting `len(differing) == 1`. **That is not enough to express FY2029-30 in this workbook, and
the one-part fixture is a fixture that changes nothing.** Measured here:

* the year vocabulary lives in `xl/worksheets/sheet10.xml` as `Dropdown!E3:E6`;
* the validation that *uses* it lives in `xl/worksheets/sheet1.xml`, as an `x14:dataValidation`
  whose `<xm:f>` is the literal range `Dropdown!$E$3:$E$6`, applying to `sqref D3`.

Writing `2029-30` into `E7` alone leaves the referenced range at `$E$3:$E$6`, so the induced
vocabulary is **unchanged**, no predicate's binding moves, and the churn sweep correctly reports
that nothing happened. The first build of this fixture did exactly that and the sweep moved zero
predicates — which is how the discrepancy was found, rather than by re-reading the plan.

So the surgery rewrites two parts and the test asserts **exactly two**, both named:

| part | edit |
|---|---|
| `xl/worksheets/sheet10.xml` | add `E7 = 2029-30`, as an INLINE string |
| `xl/worksheets/sheet1.xml`  | extend that one `x14` range to `Dropdown!$E$3:$E$7` |

The inline string still matters: a shared-string index would drag `xl/sharedStrings.xml` in as a
third part, and every part in the diff is a part somebody has to argue is intentional.

## Raw-zip surgery

Every other entry is copied byte-for-byte. **An openpyxl round-trip is forbidden** (NC-P04) and
here it would also be catastrophic: 96.9% of this archive is `xl/model/item.data`, the embedded
data model, which a round-trip collapses from 3.55 MB to 66 KB.
"""

from __future__ import annotations

import pathlib
import shutil
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

BASE = REPO / ("fixtures/prescribed/"
               "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
OUT = REPO / "fixtures/synthetic/template-bumped__fy2029-30.xlsx"

VOCAB_PART = "xl/worksheets/sheet10.xml"    # the `Dropdown` sheet, per xl/_rels/workbook.xml.rels
RANGE_PART = "xl/worksheets/sheet1.xml"     # `1. Introduction`, where the x14 validation lives
PARTS = frozenset({VOCAB_PART, RANGE_PART})
NEW_VALUE = "2029-30"

# Each edit is anchored on a byte string that appears EXACTLY ONCE, asserted below. A replace with
# `count=1` on an anchor that appears twice edits an arbitrary one of them.
VOCAB_ANCHOR = b'<row r="7" spans="4:18" x14ac:dyDescent="0.35"><c r="F7"'
VOCAB_INSERT = (b'<row r="7" spans="4:18" x14ac:dyDescent="0.35">'
                b'<c r="E7" t="inlineStr"><is><t>2029-30</t></is></c><c r="F7"')

RANGE_ANCHOR = b"<xm:f>Dropdown!$E$3:$E$6</xm:f>"
RANGE_INSERT = b"<xm:f>Dropdown!$E$3:$E$7</xm:f>"

# The validation census, asserted across the surgery. Extending a range must not drop one.
X14_TAG = b"<x14:dataValidation"


def _patch(blob: bytes, anchor: bytes, insert: bytes, part: str) -> bytes:
    n = blob.count(anchor)
    if n != 1:
        raise SystemExit(
            f"{part}: the anchor appears {n} times, not once. The pinned blank has moved and this "
            "surgery must not guess which occurrence to edit."
        )
    return blob.replace(anchor, insert, 1)


def main() -> int:
    if not BASE.is_file():
        print(f"{BASE} is absent", file=sys.stderr)
        return 1
    with zipfile.ZipFile(BASE) as z:
        vocab, ranges = z.read(VOCAB_PART), z.read(RANGE_PART)
        if b"2029-30" in vocab:
            print(f"{VOCAB_PART} already carries {NEW_VALUE}", file=sys.stderr)
            return 1
        before = ranges.count(X14_TAG)
        patched = {
            VOCAB_PART: _patch(vocab, VOCAB_ANCHOR, VOCAB_INSERT, VOCAB_PART),
            RANGE_PART: _patch(ranges, RANGE_ANCHOR, RANGE_INSERT, RANGE_PART),
        }
        after = patched[RANGE_PART].count(X14_TAG)
        if before != after:
            print(f"  REFUSED: x14 validations went {before} -> {after}", file=sys.stderr)
            return 1

        OUT.parent.mkdir(parents=True, exist_ok=True)
        tmp = OUT.with_suffix(".tmp")
        # Compression, timestamp and attributes are carried per entry from the source, so the only
        # difference between the two archives is the bytes of two parts rather than the metadata of
        # all of them.
        with zipfile.ZipFile(tmp, "w") as out:
            for info in z.infolist():
                keep = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                keep.compress_type = info.compress_type
                keep.external_attr = info.external_attr
                keep.internal_attr = info.internal_attr
                keep.create_system = info.create_system
                out.writestr(keep, patched.get(info.filename) or z.read(info.filename))
        shutil.move(str(tmp), str(OUT))

    from cdfc.qualify.surgery import differing_parts

    diff = differing_parts(BASE, OUT)
    print(f"wrote {OUT.relative_to(REPO)}  ({OUT.stat().st_size:,} bytes)")
    print(f"  differing parts: {sorted(diff)}")
    print(f"  x14 validations preserved: {before}")
    if diff != PARTS:
        print(f"  REFUSED: expected exactly {sorted(PARTS)}", file=sys.stderr)
        OUT.unlink(missing_ok=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
