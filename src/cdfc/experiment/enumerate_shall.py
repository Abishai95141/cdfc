"""P12-B1 — the pool enumerator. **The `shall` sentences of the named chapters, and nothing else.**

`enumerate_shall` is the experiment's *pool*, not G0's text: G0 asks *does this quote locate?*,
and this asks *what is there to ask about?*. It runs over an `InstrumentText` — the P7-B0 artifact
— and therefore inherits its dual-extraction discipline for free.

## Three things decide which obligations the model is asked about, and all three are locked

The **named chapters**, the **canonical ordering**, and the **disputed-region exclusion set**. If
any of them can move after the draw, `k of 20` measures the pool's construction and reports it as
a property of the model. So:

- **A chapter title that does not match exactly RAISES.** There is no fuzzy chapter match. A
  silently-missed chapter is a silently-shrunk denominator, and this project has committed that
  defect four times in other places — every one of them looked like a smaller number that nobody
  questioned because nothing said a number was missing.
- **The ordering is arithmetic, not lexical.** `(reg_no, sub_clause, span)` with `sub_clause`
  parsed into components, so regulation 9 sorts before regulation 51 and sub-clause `(10)` sorts
  after `(9)`. Lexical ordering would put `51` before `9` and `(10)` before `(9)`, and the
  permutation is keyed on the ordinal, so a wrong order is a **different draw** wearing the same
  seed.
- **A `shall` inside a disputed region is EXCLUDED and COUNTED**, never dropped. The extractions
  have no authoritative reading there, so an obligation quoted out of it is a quote into
  something we cannot stand behind.

## `shall` is matched on word boundaries, and the boundary rule is stated

`marshalling`, `shallow` and `Marshall` all contain the token. The match requires that the
characters either side are not alphanumeric — asserted by
`test_enumerate__shall_inside_a_longer_word_is_not_an_obligation`, whose fixture is `marshalling`
because that word appears in financial regulation and would not have been caught by a fixture
somebody invented.

## `str.find`, not a regular expression

Sentence splitting here is a hand-written scan on `. ` / `; ` / newline with an abbreviation guard,
not a regex. The project bans regex over CEL and over XML for the same underlying reason and the
reason applies again: a regex that is subtly wrong over prose fails by returning **fewer**
sentences, which shrinks the pool silently and in the flattering direction.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from cdfc.experiment.draw import (
    OBLIGATION_TOKEN,
    ChapterNotFound,
    ExcludedObligation,
    Obligation,
    Pool,
)

# A sentence ends at one of these when the next character is whitespace or the text ends. Stated
# as data so the rule is inspectable and so a change to it is a diff.
TERMINATORS: Final[tuple[str, ...]] = (".", ";", "\n")

# Abbreviations whose trailing full stop does NOT end a sentence. Deliberately short and closed:
# a long guessed list is a curation of the instrument by another name, and every entry here is one
# the FME reporting instruments actually use.
NON_TERMINAL: Final[frozenset[str]] = frozenset({
    "no", "nos", "reg", "regs", "cl", "sub", "para", "sec", "art", "sch", "rs", "vs", "viz",
    "i.e", "e.g", "etc", "ltd", "pvt", "co", "inc", "mr", "ms", "dr",
})

# A unit whose text begins with one of these is a STRUCTURAL HEADING and closes the chapter above
# it. The set is data, and `enumerate_shall` **refuses** a heading that is not in the declared
# heading list rather than absorbing it — see `UndeclaredHeading`.
HEADING_PREFIXES: Final[tuple[str, ...]] = (
    "Chapter ", "CHAPTER ", "Part ", "PART ", "Schedule ", "SCHEDULE ", "Annexure ", "ANNEXURE ",
)


class UndeclaredHeading(LookupError):
    """A unit reads as a chapter heading and is not in the declared heading list.

    **This is fail-closed, and the direction matters.** A named chapter runs to the next heading.
    If a heading the pre-registration never declared is not recognised as one, the chapter above it
    swallows everything below — so obligations from chapters that were **deliberately not sampled**
    enter the pool, `|drawn|` inflates, and the model is asked about clauses outside the
    pre-registered scope. That is denominator inflation, and it is the mirror image of the
    truncation NC-M03 guards.

    So the enumerator refuses and names the heading rather than guessing whether it is one. The
    remedy is to declare it in `all_headings` — an edit to the pre-registered pool construction,
    which is hashed, which is exactly where that decision belongs.
    """


class NotAStatute(ValueError):
    """The instrument handed in is not a statutory instrument.

    Raised rather than returning an empty pool, because an empty pool and *"you handed me a
    spreadsheet"* are different facts with different remedies, and this project's whole thesis is
    that collapsing those two is the defect. See `docs/decisions/D-P7-01-no-statutory-instrument.md`:
    **no statutory instrument is pinned in this repository**, so on today's corpus this is the
    exception `tools/e6/enumerate_shall.py` reports.
    """


def is_obligation_token_at(text: str, i: int) -> bool:
    """`shall` at `i`, on word boundaries. `marshalling` is not an obligation."""
    if not text.startswith(OBLIGATION_TOKEN, i):
        return False
    before = text[i - 1] if i > 0 else " "
    after_i = i + len(OBLIGATION_TOKEN)
    after = text[after_i] if after_i < len(text) else " "
    return not (before.isalnum() or before == "_") and not (after.isalnum() or after == "_")


def sentences(text: str, offset: int = 0) -> tuple[tuple[int, int], ...]:
    """Sentence spans, absolute into the instrument. Hand-written, with the abbreviation guard."""
    out: list[tuple[int, int]] = []
    start = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in TERMINATORS:
            nxt = text[i + 1] if i + 1 < n else " "
            if ch == "\n" or nxt.isspace() or i + 1 == n:
                head = text[start:i].rstrip()
                token = head.rsplit(" ", 1)[-1].lower().rstrip(".") if head else ""
                # A FULL STOP AFTER A LEADING NUMERAL IS A CLAUSE NUMBER, NOT A SENTENCE END.
                # `51. (1) The FME shall …` split here in the first version, so `parse_citation`
                # saw ` (1) The FME shall …` and every obligation parsed to reg_no 0 — and the
                # canonical ordering, which is keyed on the ordinal, silently became insertion
                # order. The rule is narrow on purpose: the numeral must be the WHOLE sentence so
                # far, so `… in 2025. The FME shall …` still splits, because there `2025` is not
                # the first token.
                clause_numeral = ch == "." and head.strip().isdigit()
                if not (ch == "." and (token in NON_TERMINAL or clause_numeral)):
                    # Leading whitespace is trimmed OUT OF THE SPAN, not just out of the string.
                    # A quote whose span includes the space before it still locates under
                    # `source.find`, so the defect would be invisible to G0 and visible only as a
                    # verbatim quote nobody could paste back — the shape of every off-by-one that
                    # survives review.
                    lead = len(head) - len(head.lstrip())
                    if head.strip():
                        out.append((offset + start + lead, offset + start + len(head)))
                    start = i + 1
        i += 1
    tail = text[start:].strip()
    if tail:
        lead = len(text[start:]) - len(text[start:].lstrip())
        out.append((offset + start + lead, offset + start + lead + len(tail)))
    return tuple(out)


def parse_citation(quote: str) -> tuple[int, tuple[int | str, ...]]:
    """`(reg_no, sub_clause)` from a leading citation, or `(0, ())` when there is none.

    **Parsed, so that ordering is arithmetic.** `"51. (1)(a) The FME shall …"` becomes
    `(51, ("1", "a"))`. A quote with no citation sorts first with `reg_no = 0`, which is stable
    and, more importantly, *visible*: an instrument whose obligations all parse to 0 has not been
    understood by this function and the golden's value assertion says so.
    """
    s = quote.lstrip()
    num = ""
    i = 0
    while i < len(s) and s[i].isdigit():
        num += s[i]
        i += 1
    if not num:
        return 0, ()
    reg = int(num)
    parts: list[int | str] = []
    while i < len(s):
        # The separator between a regulation number and its first sub-clause is `.` followed by a
        # space — `51. (1)(a)` — and between sub-clauses there is nothing. The first version
        # consumed the `.` and then met the space, broke, and returned `(52, ())` for
        # `52. (2)(a) …`: every sub-clause silently absent, so `(51)(10)` and `(51)(9)` compared
        # EQUAL and the canonical ordering degenerated to span order within a regulation.
        if s[i] in ". \t":
            i += 1
            continue
        if s[i] != "(":
            break
        j = s.find(")", i)
        if j == -1:
            break
        body = s[i + 1:j].strip()
        if not body or len(body) > 4:
            break
        parts.append(body)
        i = j + 1
    return reg, tuple(parts)


def _sub_clause_key(parts: Sequence[int | str]) -> tuple[tuple[int, int, str], ...]:
    """Sub-clause components ordered ARITHMETICALLY: `(10)` after `(9)`, `(a)` after any number."""
    key: list[tuple[int, int, str]] = []
    for p in parts:
        s = str(p)
        if s.isdigit():
            key.append((0, int(s), ""))
        else:
            key.append((1, 0, s))
    return tuple(key)


def enumerate_shall(
    source: object, *, chapters: frozenset[str], all_headings: frozenset[str] | None = None
) -> Pool:
    """Every `shall` sentence in the named chapters, in canonical order, with the exclusions.

    `source` is an `InstrumentText` (P7-B0). It is typed `object` and duck-checked so this module
    does not import the qualification package — `cdfc.experiment` must stay out of the verdict
    path's import closure in **both** directions, and a type annotation is enough to create an
    import that `test_nc__M13a` would then have to carve an exception for.
    """
    for attr in ("text", "units", "disputed", "sha256"):
        if not hasattr(source, attr):
            raise NotAStatute(
                f"the instrument handed in has no `{attr}`; this is not an InstrumentText. "
                "The pool is enumerated over a pinned STATUTORY instrument read by two "
                "independent extractors — see docs/decisions/D-P7-01-no-statutory-instrument.md."
            )
    kind = getattr(source, "kind", None)
    if kind is not None and str(kind).upper() != "STATUTE":
        raise NotAStatute(
            f"instrument kind is {kind!r}, not STATUTE. Enumerating `shall` over a TEMPLATE "
            "workbook would produce a pool of spreadsheet labels and call it a regulation."
        )

    text: str = source.text                               # type: ignore[attr-defined]
    units = tuple(source.units)                           # type: ignore[attr-defined]
    if not units:
        raise NotAStatute(
            "the instrument has no addressable units. An empty pool and an absent instrument are "
            "different facts; this is the second."
        )

    headings = chapters if all_headings is None else all_headings
    if not chapters <= headings:
        raise UndeclaredHeading(
            f"chapters {sorted(chapters - headings)} are sampled but are not in the declared "
            "heading list. The sampled set must be a subset of the instrument's headings."
        )
    named = _chapter_spans(text, units, chapters, headings)

    found: list[Obligation] = []
    excluded: list[ExcludedObligation] = []
    for _title, (lo, hi), page in named:
        for span in sentences(text[lo:hi], offset=lo):
            quote = text[span[0]:span[1]]
            if not any(is_obligation_token_at(quote.lower(), i) for i in range(len(quote))):
                continue
            if source.is_disputed(span):                  # type: ignore[attr-defined]
                excluded.append(ExcludedObligation(
                    quote=quote, char_span=span, page=page,
                    reason="the extractions disagree here, so no party's reading is authoritative",
                ))
                continue
            reg, sub = parse_citation(quote)
            found.append(Obligation(
                ordinal=-1, reg_no=reg, sub_clause=sub, quote=quote, char_span=span,
                source_sha256=source.sha256,               # type: ignore[attr-defined]
            ))

    # THE CANONICAL ORDERING: (reg_no, sub_clause, span[0]) — arithmetic, never lexical.
    found.sort(key=lambda o: (o.reg_no, _sub_clause_key(o.sub_clause), o.char_span[0]))
    ordered = tuple(
        Obligation(ordinal=n, reg_no=o.reg_no, sub_clause=o.sub_clause, quote=o.quote,
                   char_span=o.char_span, source_sha256=o.source_sha256)
        for n, o in enumerate(found)
    )
    return Pool(
        obligations=ordered, excluded=tuple(excluded),
        source_sha256=source.sha256,                       # type: ignore[attr-defined]
        chapters=tuple(sorted(chapters)),
    )


def _chapter_spans(
    text: str, units: Sequence[object], chapters: frozenset[str], headings: frozenset[str]
) -> tuple[tuple[str, tuple[int, int], int], ...]:
    """`(title, span, page)` per named chapter. **Every named chapter must match exactly.**

    The title is read **from the instrument text at the unit's span**, never from the unit's `key`.
    A `ResolvedUnit`'s key is an addressing handle chosen by the extractor — for a workbook it is
    `(sheet, kind, ref)` — and matching a pre-registered chapter list against it would compare the
    regulation's chapter titles to our own indexing scheme and find nothing, which raises here and
    would otherwise have looked exactly like a regulation with no chapters.
    """
    opens: list[tuple[str, int, int, int]] = []       # title, unit index, span start, page
    boundaries: list[int] = []                        # span starts of EVERY declared heading
    undeclared: list[str] = []
    for i, u in enumerate(units):
        lo, hi = u.span                                           # type: ignore[attr-defined]
        title = text[lo:hi].strip()
        if title in headings:
            boundaries.append(lo)
            if title in chapters:
                opens.append((title, i, lo, u.page))              # type: ignore[attr-defined]
        elif title.startswith(HEADING_PREFIXES):
            undeclared.append(title)

    if undeclared:
        raise UndeclaredHeading(
            f"{len(undeclared)} unit(s) read as structural headings and are not declared: "
            f"{undeclared[:5]}. A named chapter runs to the NEXT HEADING, so an unrecognised one "
            "is absorbed into the chapter above it — and every obligation below it enters a pool "
            "the pre-registration says it is outside. Declare it in `all_headings`, which is part "
            "of the hashed pool construction, or fix the extraction."
        )

    matched = {t for t, _i, _s, _p in opens}
    missing = sorted(chapters - matched)
    if missing:
        raise ChapterNotFound(
            f"{len(missing)} of {len(chapters)} named chapters did not match EXACTLY: {missing}. "
            "There is no fuzzy chapter match here: a chapter matched loosely is a different "
            "denominator, and a chapter missed silently is a smaller one. Fix the pre-registered "
            "chapter list or fix the extraction — do not relax the comparison."
        )

    # A chapter runs to the NEXT CHAPTER HEADING, not to the next unit — a chapter that stopped at
    # its own heading would enumerate nothing and report a pool of zero as a property of the
    # instrument. `opens` is in unit order because `units` was walked in order.
    out: list[tuple[str, tuple[int, int], int]] = []
    end_of_text = units[-1].span[1]                                              # type: ignore[attr-defined]
    for title, _i, start, page in opens:
        later = [b for b in boundaries if b > start]
        out.append((title, (start, min(later) if later else end_of_text), page))
    return tuple(out)
