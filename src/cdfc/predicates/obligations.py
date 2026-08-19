"""P7-B1 — the obligations table, and the `source` discriminator that keeps the funnel honest.

**ARBITRATION C2.** A harvested predicate implements a relation the REGULATOR'S TEMPLATE encodes;
a hand-authored one implements a clause the STATUTE states. **Both are real obligations.** They are
not the same kind of thing, and collapsing them is what made F9 irreconcilable — so `source` is a
required, closed discriminator with no default and no `None`, and it is a DIFFERENT field from
`ingest_source`, which records how the row got here rather than what it is.

**F9 — a harvested candidate gets a template-derived obligation and G0 runs over it for real.**
Its `obligation_id` is `OBL-TEMPLATE-<F|V>-<sheet>-<ref>`, its `instrument_id` is the pinned blank's
`template-<sha8>`, its `quote` is the verbatim construct the harvester read, and its `span` is that
construct's exact offset into `template_instrument.emit()`. `instrument_text.find(quote)` is then a
real, failable question: *is the relation this predicate claims to implement present in the pinned
blank, at the offset recorded?* The rejected alternative — skipping G0 for clause-less candidates —
made stage one of the funnel read `N → N`, a constant wearing the shape of a measurement.

**THE PUBLISHED FIGURE IS TWO NUMBERS, NEVER ONE.** `coverage_pair()` returns both counts or
raises; there is no accessor that returns one. `0/572` alone is wrong by 572 under F9's ruling, and
`572/572` alone conceals that nothing here is grounded in a statute. The sentence that ships beside
them survives verbatim: **no harvested predicate yet implements a statutory clause.**
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, Literal

from cdfc.qualify.instruments import InstrumentNotFound, InstrumentStore
from cdfc.qualify.textsource import InstrumentText

OBLIGATIONS_YAML: Final[Path] = Path("obligations.yaml")

NO_STATUTORY_PREDICATE: Final[str] = "no harvested predicate yet implements a statutory clause"


class ObligationError(ValueError):
    """A row that is not admissible as an obligation. Never repaired, never defaulted."""


class UnpairedObligationCount(RuntimeError):
    """One of the two obligation-coverage counts was rendered without the other (C2)."""


class ObligationSource(StrEnum):
    STATUTE = "STATUTE"  # a `shall` in an instrument the Authority issued
    TEMPLATE = "TEMPLATE"  # a relation the regulator's own PINNED BLANK encodes (F9)


IngestSource = Literal["hand", "l1b", "harvest"]
INGEST_SOURCES: Final[frozenset[str]] = frozenset({"hand", "l1b", "harvest"})


@dataclass(frozen=True, slots=True)
class Obligation:
    obligation_id: str
    source: ObligationSource
    instrument_id: str
    frbr_uri: str | None
    eId: str | None
    quote: str
    span: tuple[int, int]
    ingest_source: IngestSource

    def __post_init__(self) -> None:
        if not self.obligation_id:
            raise ObligationError("an obligation with no id cannot be cited")
        if not isinstance(self.source, ObligationSource):
            raise ObligationError(
                f"{self.obligation_id}: source must be an ObligationSource, not "
                f"{type(self.source).__name__}. There is no default and no None (C2)."
            )
        if self.ingest_source not in INGEST_SOURCES:
            raise ObligationError(
                f"{self.obligation_id}: ingest_source must be one of {sorted(INGEST_SOURCES)}. "
                "It records HOW THE ROW GOT HERE and is a different question from `source`, "
                "which records what it IS — neither is derived from the other."
            )
        if not self.quote:
            raise ObligationError(f"{self.obligation_id}: an obligation with no quote is a citation")
        lo, hi = self.span
        if not (isinstance(lo, int) and isinstance(hi, int)) or lo < 0 or hi < lo:
            raise ObligationError(f"{self.obligation_id}: span {self.span!r} is not a span")
        if self.source is ObligationSource.TEMPLATE:
            if self.frbr_uri is not None:
                raise ObligationError(
                    f"{self.obligation_id}: a TEMPLATE obligation has no FRBR URI — there is no "
                    "statutory work to name."
                )
            if not self.instrument_id.startswith("template-"):
                raise ObligationError(
                    f"{self.obligation_id}: a TEMPLATE obligation resolves against a pinned "
                    f"blank, and {self.instrument_id!r} is not one."
                )
        elif self.instrument_id.startswith("template-"):
            raise ObligationError(
                f"{self.obligation_id}: a STATUTE obligation cites an instrument the Authority "
                f"issued, and {self.instrument_id!r} is a pinned blank. Labelling a template "
                "relation as statutory is the one direction C2 exists to prevent."
            )


@dataclass(frozen=True, slots=True)
class ObligationTable:
    """The rows, plus the two counts that may only be published together."""

    rows: Mapping[str, Obligation]

    def __getitem__(self, obligation_id: str) -> Obligation:
        try:
            return self.rows[obligation_id]
        except KeyError:
            raise ObligationError(
                f"{obligation_id!r} is not in the obligations table. A candidate whose obligation "
                "is missing does not take a skip at G0 — a gate stage that cannot fail is this "
                "product's own failure mode wearing a gate's clothes."
            ) from None

    def __contains__(self, obligation_id: object) -> bool:
        return obligation_id in self.rows

    def __len__(self) -> int:
        return len(self.rows)

    def coverage_pair(self, candidates: Sequence[object]) -> tuple[int, int, int]:
        """`(statute, template, total)` — THREE integers, in one call, always.

        There is deliberately no `statute_count()` and no `template_count()`. A surface can only
        render one of these numbers alone by discarding the others it was handed, which is a
        visible act rather than an omission.
        """
        statute = template = 0
        for c in candidates:
            oid = getattr(c, "obligation_id", None)
            if oid is None:
                raise ObligationError(f"{c!r} carries no obligation_id; C2 requires one of every candidate")
            row = self[oid]
            if row.source is ObligationSource.STATUTE:
                statute += 1
            else:
                template += 1
        return statute, template, statute + template

    def render_coverage_pair(self, candidates: Sequence[object]) -> str:
        """Both counts, on adjacent lines, from one call — and the sentence when it is true."""
        s, t, n = self.coverage_pair(candidates)
        out = [
            f"predicates_with_a_STATUTE_obligation  = {s} / {n}",
            f"predicates_with_a_TEMPLATE_obligation = {t} / {n}",
        ]
        if s == 0:
            out.append(f"{NO_STATUTORY_PREDICATE.capitalize()}.")
        return "\n".join(out)


def assert_pair_rendered(text: str) -> None:
    """C2's rendering rule, checkable on any surface.

    Raises `UnpairedObligationCount` when a surface carries one of the two counts without the
    other. Called by `test_p7__both_obligation_counts_render_or_neither_does` over every published
    surface, so *one number alone* fails the build in either direction.
    """
    has_s = "predicates_with_a_STATUTE_obligation" in text
    has_t = "predicates_with_a_TEMPLATE_obligation" in text
    if has_s != has_t:
        missing = "TEMPLATE" if has_s else "STATUTE"
        raise UnpairedObligationCount(
            f"a surface renders one obligation-coverage count without the other; "
            f"predicates_with_a_{missing}_obligation is absent. `0/N` alone is wrong by N under "
            "F9's ruling, and `N/N` alone conceals that nothing here is grounded in a statute."
        )


# --- the TEMPLATE side: generated from the harvest and the pinned blank --------------------


def _render_construct(kind: str, parts: Sequence[str]) -> str:
    from cdfc.qualify.template_instrument import SEP, formula_unit_text, validation_unit_text

    if kind == "formula":
        return formula_unit_text("s", "A1", parts[0]).split(SEP, 1)[1]
    if kind == "validation":
        t, op, f1 = parts
        return validation_unit_text("s", "A1", t, op, f1).split(SEP, 1)[1]
    raise ObligationError(f"unknown construct kind {kind!r}")


def generate_template_obligations(result: object, instrument: InstrumentText) -> ObligationTable:
    """One TEMPLATE obligation per harvested obligation id, located in the pinned blank.

    **What is falsifiable here, because the tautological reading is the one to avoid.** Taking the
    quote out of the instrument and then asserting it is in the instrument proves nothing. The two
    checks that can fail are:

    1. **The construct must EXIST as a unit** at the `(kind, sheet, ref)` the harvest recorded. A
       harvest run against a different template version fails here — which is
       `g0.quote_not_located` caught one step earlier, at generation.
    2. **The harvest's own recording must MATCH the instrument's corroborated text.** The harvest
       and party A read through the same code, so a mismatch on an AGREED unit means the two
       parties diverged and the instrument carries the sentinel instead — and that case is not an
       error, it is `g0.quote_in_disputed_region`, so the obligation is emitted pointing at the
       disputed span and the gate refuses it. Any OTHER mismatch is a defect in this repository
       and raises.
    """
    from cdfc.qualify.template_instrument import SEP, _norm_ref

    index: dict[tuple[str, str, str], object] = {}
    for u in instrument.units:
        _sheet_idx, _row, _col, kind, addr = u.key.split("|", 4)
        sheet, _, ref = addr.rpartition("!")
        index[(kind, sheet, ref)] = u

    rows: dict[str, Obligation] = {}
    for oid, (construct_kind, parts, sheet, ref) in sorted(result.constructs.items()):  # type: ignore[attr-defined]
        k = "F" if construct_kind == "formula" else "V"
        unit = index.get((k, sheet, _norm_ref(ref)))
        if unit is None:
            raise ObligationError(
                f"{oid}: the pinned blank {instrument.instrument_id} carries no {construct_kind} "
                f"at {sheet}!{ref}. The harvest read a construct this instrument does not have, "
                "which means the two were taken from different template versions."
            )
        rendered = instrument.text[unit.span[0] : unit.span[1]]
        expected = _render_construct(construct_kind, parts)
        if SEP in rendered:
            quote = rendered.split(SEP, 1)[1]
            offset = unit.span[0] + len(rendered.split(SEP, 1)[0]) + len(SEP)
            span = (offset, unit.span[1])
        else:
            # A disputed unit is rendered as the sentinel and has no address prefix to strip.
            quote, span = expected, unit.span
        if quote != expected and not instrument.is_disputed(unit.span):
            raise ObligationError(
                f"{oid}: the harvest recorded {expected!r} and the instrument carries {quote!r} "
                f"at {sheet}!{ref}, and the unit is not disputed. Two code paths in this "
                "repository read one construct differently."
            )
        if instrument.is_disputed(unit.span):
            quote, span = expected, unit.span
        rows[oid] = Obligation(
            obligation_id=oid,
            source=ObligationSource.TEMPLATE,
            instrument_id=instrument.instrument_id,
            frbr_uri=None,
            eId=None,
            quote=quote,
            span=span,
            ingest_source="harvest",
        )
    return ObligationTable(rows)


# --- the STATUTE side: hand-maintained, and empty (D-P7-01) --------------------------------


def load(path: Path = OBLIGATIONS_YAML, *, store: InstrumentStore | None = None) -> ObligationTable:
    """Load `obligations.yaml`, refusing any row whose instrument is not pinned.

    **A row is validated against its OWN instrument, not against a default.** An obligation naming
    an instrument that is absent from the corpus does not resolve against an empty string — it does
    not resolve at all, and it raises. That is what keeps `source: STATUTE` unreachable while the
    statutory corpus is empty (D-P7-01) instead of quietly resolving to nothing and passing G0.
    """
    import yaml

    store = store or InstrumentStore()
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows: dict[str, Obligation] = {}
    for raw in doc.get("obligations") or ():
        try:
            source = ObligationSource(raw["source"])
        except (KeyError, ValueError) as e:
            raise ObligationError(
                f"{raw.get('obligation_id', '<no id>')}: `source` is required and closed to "
                f"{[s.value for s in ObligationSource]} (C2)"
            ) from e
        o = Obligation(
            obligation_id=raw["obligation_id"],
            source=source,
            instrument_id=raw["instrument_id"],
            frbr_uri=raw.get("frbr_uri"),
            eId=raw.get("eId"),
            quote=raw["quote"],
            span=(int(raw["span"][0]), int(raw["span"][1])),
            ingest_source=raw.get("ingest_source", "hand"),
        )
        if o.obligation_id in rows:
            raise ObligationError(f"{o.obligation_id}: duplicate row")
        try:
            it = store.get(o.instrument_id)
        except InstrumentNotFound as e:
            raise ObligationError(
                f"{o.obligation_id}: names instrument {o.instrument_id!r}, which is not pinned in "
                f"{store.root}. While the statutory corpus is empty (D-P7-01) this is how a "
                "STATUTE obligation is kept out of the funnel rather than resolving against "
                "nothing."
            ) from e
        lo, hi = o.span
        if hi > len(it.text):
            raise ObligationError(
                f"{o.obligation_id}: span {o.span} runs past the end of {o.instrument_id} "
                f"({len(it.text)} characters)"
            )
        if it.text[lo:hi] != o.quote and not it.is_disputed(o.span):
            raise ObligationError(
                f"{o.obligation_id}: the span and the quote disagree; one of them is a lie. "
                f"instrument[{lo}:{hi}] is {it.text[lo:hi][:60]!r} and the row quotes "
                f"{o.quote[:60]!r}. (A span inside a DISPUTED region is admitted here and refused "
                "at G0 with `g0.quote_in_disputed_region`, because those are different findings.)"
            )
        rows[o.obligation_id] = o
    return ObligationTable(rows)
