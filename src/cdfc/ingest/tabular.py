"""A delimited export read into an ADDRESSABLE text, by two independent parsers.

## Why a CSV needs two readers at all

Every span this system cites has to re-verify byte-exact, and `textsource.build` refuses a single
extraction outright: *"an instrument built from one reading is that reading's opinion, and a span
into it is unfalsifiable."* That rule was written for PDFs and it is not weaker for a CSV — a
custodian feed with an unquoted comma inside a field is misread silently by a naive splitter, and
nothing downstream can tell.

So two parsers, and they disagree exactly where the file is ambiguous:

* **`csv.reader`** — the stdlib dialect machine. Handles quoting, embedded delimiters, embedded
  newlines.
* **`naive_split`** — `line.split(delimiter)`. Deliberately dumb.

A row they agree on is `AGREED`. A row they do not is `DISPUTED`, excluded from the addressable
text, and **that is the correct outcome**: it is precisely the row whose field boundaries depend on
which parser you believed, and a value read out of it would be one parser's guess wearing a span.

**Both parsers are ours, so the agreement is `SAME_AUTHOR`, not `EXTERNAL`.** `InstrumentText.
agreement()` already reports those as two vectors and never averages them. This is weaker evidence
than the statutory instrument's pdfplumber-versus-pypdfium2 pair and the surface says so.

## What this is not

It is not a schema reader and it does not type anything. Column shape is
`cdfc.correspond.schema.SourceColumn.shape()`'s job, from the values; this produces the addressable
text and the spans, which is what evidence needs.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from typing import Final

from cdfc.qualify.textsource import Extraction, InstrumentText, Unit, build

# A row is rendered as its fields joined by this, so a span into the text lands on a field
# boundary a human can see. It is NOT the source delimiter: the source's own delimiter may appear
# inside a quoted field, and rendering with it would make the addressable text ambiguous in
# exactly the way the two parsers exist to detect.
FIELD_SEP: Final[str] = " | "

MAX_ROWS: Final[int] = 200_000


class TabularError(RuntimeError):
    """The export cannot be read. Never repaired, never defaulted."""


def _rows_csv(text: str, delimiter: str) -> list[list[str]]:
    return [r for r in csv.reader(io.StringIO(text), delimiter=delimiter)]


def _rows_naive(text: str, delimiter: str) -> list[list[str]]:
    return [line.split(delimiter) for line in text.splitlines()]


def _units(rows: Sequence[Sequence[str]]) -> tuple[Unit, ...]:
    out: list[Unit] = []
    for i, row in enumerate(rows[:MAX_ROWS]):
        body = FIELD_SEP.join(str(c).strip() for c in row)
        if body:
            out.append(Unit(key=f"r{i:06d}", text=body, page=1))
    return tuple(out)


def read_delimited(
    data: bytes, *, instrument_id: str, delimiter: str = ",", encoding: str = "utf-8"
) -> InstrumentText:
    """Read `data` into an addressable text. Rows the two parsers disagree on become DISPUTED."""
    try:
        text = data.decode(encoding)
    except UnicodeDecodeError as exc:
        raise TabularError(
            f"{instrument_id}: not decodable as {encoding}. An export whose encoding we guessed "
            "would give spans into characters nobody can reproduce."
        ) from exc
    if not text.strip():
        raise TabularError(f"{instrument_id}: the export is empty, which is not the same as "
                           "an export with no rows and is not silently either.")

    arms = []
    for name, rows in (("csv_reader", _rows_csv(text, delimiter)),
                       ("naive_split", _rows_naive(text, delimiter))):
        arms.append(Extraction(
            extractor=name, version="1", external=False, units=_units(rows), blind_to={},
        ))
    # Neither parser can be blind to a row the other produced — both see every line — so an
    # absence here would be a real MISS and `build` is left to refuse it.
    tables = {e.extractor: {u.key for u in e.units} for e in arms}
    universe = set().union(*tables.values())
    arms = [
        Extraction(
            extractor=e.extractor, version=e.version, external=False, units=e.units,
            blind_to={
                k: (f"{e.extractor} produced no unit at this row: the two parsers segmented the "
                    "export into a different number of non-empty rows, which happens when one of "
                    "them reads an embedded newline as a row break")
                for k in sorted(universe - tables[e.extractor])
            },
        )
        for e in arms
    ]
    return build(instrument_id, arms)


def header_and_rows(
    data: bytes, *, delimiter: str = ",", encoding: str = "utf-8"
) -> tuple[list[str], list[list[str]]]:
    """`(header, rows)` for `correspond.schema.columns_from_rows`. The QUOTED reading, deliberately.

    The column structure comes from `csv.reader` because that is the parser that is right about
    quoting; the naive arm exists to DISPUTE the addressable text, not to define columns. If the
    two disagree on a row, the value bound from it will fail `A5`'s re-verification anyway — which
    is the check that is supposed to catch it.
    """
    rows = _rows_csv(data.decode(encoding), delimiter)
    if not rows:
        raise TabularError("the export has no rows, so it declares no columns.")
    return [str(c).strip() for c in rows[0]], [[str(c).strip() for c in r] for r in rows[1:]]
