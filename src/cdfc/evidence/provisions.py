"""LAYER 1a — the rules corpus becomes addressable `Provision` nodes. Deterministic, no model.

**The eId kind is carried in the data, and it is the honest part of this module.** The pinned
corpus is FLAT TEXT: a line-anchored pattern recovers 3 regulation numbers from its 197,767
characters, because the extraction dropped the list markers that carry them
(`docs/measurements/M-CEIL-results.md`). So today every provision is addressed by COORDINATE --
`p0143.s0008`, page 143 sentence 8 -- and a rule stored against one moves if the instrument is
re-extracted. `PROVISION` eIds (`reg_8__subreg_1`) come from Docling's `ListItem.marker` and
arrive with the re-pinning measured as `N1`; `from_markers` is the seam they land in.

Neither kind is guessed. A source that cannot supply real markers returns COORDINATE and says so
on every node, so a reader can tell a durable citation from a fragile one without reading this
docstring.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from cdfc.evidence.vocabulary import EIdKind
from cdfc.qualify.textsource import InstrumentText


@dataclass(frozen=True, slots=True)
class Provision:
    eid: str
    eid_kind: EIdKind
    span: tuple[int, int]
    text: str
    page: int | None = None
    disputed: bool = False

    @property
    def durable(self) -> bool:
        """Does a rule citing this survive a re-extraction of the instrument?"""
        return self.eid_kind is EIdKind.PROVISION


@dataclass(frozen=True, slots=True)
class ProvisionSet:
    instrument_id: str
    instrument_sha256: str
    provisions: tuple[Provision, ...]
    eid_kind: EIdKind
    # Markers the instrument declared and that could not be addressed: `(eid, why)`. A DECLARED
    # ABSENCE, because `absent != empty` -- a durable set of 612 where the instrument named 617 is
    # a different fact from a durable set of 612 where it named 612.
    refused_markers: tuple[tuple[str, str], ...] = ()

    def by_eid(self) -> Mapping[str, Provision]:
        return {p.eid: p for p in self.provisions}

    def get(self, eid: str) -> Provision | None:
        return self.by_eid().get(eid)

    def __len__(self) -> int:
        return len(self.provisions)

    @property
    def durable_count(self) -> int:
        return sum(1 for p in self.provisions if p.durable)


def from_divisions(it: InstrumentText, *, only_with: str | None = None) -> ProvisionSet:
    """C2 — the instrument's OWN DIVISIONS become PROVISION-addressed provisions.

    ## Why this had to exist

    `cdfc evidence` published **`durably addressable 0 of 1218`** on every run. Every provision was
    `p0146.s0013` — page 146, sentence 13 — which is a COORDINATE: it moves when the instrument is
    re-extracted, when the layout shifts, or when an amendment inserts a page. A rule stored against
    one has a shorter lifetime than a reader will assume.

    The durable addresses already existed. `cdfc.qualify.provisions` recovers the instrument's own
    numbering — `div1_0002__sub_0002` — and the pinned instrument CARRIES that map: 617 divisions
    with spans, serialised beside the text. `from_markers` already accepted exactly
    `(eid, lo, hi)`. **Nothing needed inventing; the two halves were never joined.**

    This is also the sharpest form of what `N6` measured. A page-and-sentence address is precisely
    the incidental axis that measurement warned about — on `rfc2616` a page-number sequence scored a
    perfect 176-of-176 chain — and citing a statute by page number is citing the rendering rather
    than the law.

    Falls back to nothing: an instrument with no divisions RAISES, because silently returning
    coordinate-addressed provisions from a function whose name promises durable ones is how a
    fragile citation comes to look permanent.
    """
    dm = getattr(it, "divisions", None)
    divisions = tuple(getattr(dm, "divisions", ()) or ()) if dm is not None else ()
    if not divisions:
        raise ValueError(
            f"instrument {it.instrument_id!r} carries no division map, so it has no durable "
            "addresses. Pin it with the division recovery first; returning coordinate addresses "
            "here would report a fragile citation as a permanent one."
        )
    # A MALFORMED SPAN IS REFUSED AND COUNTED, never dropped and never passed on.
    #
    # Measured 20 Aug 2026 on the pinned IFSCA instrument: **5 of 617 divisions are INVERTED**
    # (`lo > hi`), all of them sub-divisions of `div1_0148`, and every one carries the same
    # `hi = 166169`. That is the parent's clipped end: `_clip_previous_run` in
    # `cdfc.qualify.provisions` bounded the parent and did not bound its children, so each child
    # kept a start that now runs past its own end. `div1_0148` is the same division that once
    # swallowed 182 units.
    #
    # `from_markers` already refuses these — correctly, with the message *"the markers were built
    # against different bytes than these"* — but it refuses by raising, which takes the whole run
    # down for 5 rows in 617. Refusing them HERE, with a reason and a count, keeps the other 612
    # addressable and keeps the defect visible instead of turning it into a crash nobody can act
    # on. The recovery bug is recorded in `docs/AUDIT-TRAIL.md`; this is not its fix.
    markers: list[tuple[str, int, int]] = []
    refused: list[tuple[str, str]] = []
    n = len(it.text)
    for d in divisions:
        lo, hi = d.span
        if not (0 <= lo <= hi <= n):
            refused.append((
                d.eid,
                f"span {(lo, hi)} is malformed against a {n}-character instrument"
                + (f" (INVERTED: lo exceeds hi by {lo - hi})" if lo > hi else " (out of range)"),
            ))
            continue
        if only_with is not None and only_with not in it.text[lo:hi]:
            continue
        markers.append((d.eid, lo, hi))
    if not markers:
        raise ValueError(
            f"instrument {it.instrument_id!r} yielded no usable division marker: "
            f"{len(refused)} malformed, {len(divisions)} total. An empty durable set would report "
            "'nothing matched' where the truth is 'every address was broken'."
        )
    ps = from_markers(it, markers)
    return ProvisionSet(
        instrument_id=ps.instrument_id, instrument_sha256=ps.instrument_sha256,
        provisions=ps.provisions, eid_kind=ps.eid_kind, refused_markers=tuple(refused),
    )


def from_instrument(it: InstrumentText, *, only_with: str | None = None) -> ProvisionSet:
    """Every pinned unit becomes a COORDINATE-addressed provision.

    `only_with` filters to units containing a substring -- `"shall"` gives the obligation-bearing
    subset. The filter is applied to the unit's own text and the count of what it removed is
    recoverable by calling twice, so a narrowed population is never mistaken for the whole one.

    A unit overlapping a DISPUTED region is KEPT and flagged, not dropped. `G-QUOTE` needs to tell
    *"the quote is nowhere"* from *"the quote is in a region the extractors disagreed about"* --
    two reasons with two different remedies -- and dropping here collapses them into one.
    """
    out: list[Provision] = []
    for u in it.units:
        lo, hi = u.span
        seg = it.text[lo:hi]
        if only_with is not None and only_with not in seg:
            continue
        out.append(Provision(
            eid=u.key,
            eid_kind=EIdKind.COORDINATE,
            span=u.span,
            text=seg,
            page=u.page,
            disputed=it.is_disputed(u.span),
        ))
    return ProvisionSet(
        instrument_id=it.instrument_id,
        instrument_sha256=it.sha256,
        provisions=tuple(out),
        eid_kind=EIdKind.COORDINATE,
    )


def from_markers(
    it: InstrumentText,
    markers: Sequence[tuple[str, int, int]],
) -> ProvisionSet:
    """PROVISION-addressed nodes from `(eid, start, end)` triples a layout-preserving reader found.

    The seam for the re-pinning. It takes markers rather than producing them, because recovering
    them needs a reader that keeps list markers and NOTHING in `src/` is allowed that dependency:
    the marker recovery is a build-time step whose output is pinned, exactly as the instrument
    text itself is.

    Every span is checked against the instrument it claims to address. A marker set built against
    different bytes would otherwise silently produce provisions whose text is somebody else's.
    """
    out: list[Provision] = []
    for eid, lo, hi in markers:
        if not (0 <= lo <= hi <= len(it.text)):
            raise ValueError(
                f"marker {eid!r} spans {(lo, hi)}, outside the instrument's {len(it.text)} "
                "characters. The markers were built against different bytes than these."
            )
        out.append(Provision(
            eid=eid,
            eid_kind=EIdKind.PROVISION,
            span=(lo, hi),
            text=it.text[lo:hi],
            page=(u.page if (u := it.unit_at((lo, hi))) else None),
            disputed=it.is_disputed((lo, hi)),
        ))
    return ProvisionSet(
        instrument_id=it.instrument_id,
        instrument_sha256=it.sha256,
        provisions=tuple(out),
        eid_kind=EIdKind.PROVISION,
    )


def cited_eids(text: str, known: Iterable[str]) -> tuple[str, ...]:
    """The eIds a provision's own text refers to, restricted to ones that EXIST.

    Deliberately conservative and deliberately not a parser: it reports which known eIds appear
    verbatim. Resolving *"as specified in regulation 51"* to a target needs regulation 51 to be a
    node, which is the COORDINATE/PROVISION question above -- so under coordinate addressing this
    finds little, and that is a true report of the corpus rather than a limit of the search.
    """
    return tuple(sorted({e for e in known if e in text}))
