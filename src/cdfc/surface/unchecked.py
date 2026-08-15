"""P14-B2 — the Unchecked panel. **This is the product.**

It sits above the fold, it is not an appendix, and it is the only place in this market where a
reader is told what a tool did **not** do. Every other coverage product renders the checks it ran.
This renders the 1,849 cells nobody checked, grouped by reason, each group carrying a specific
statement of *what would make this checkable*.

## `MissingRemedy` raises. There is no fallback string.

A generic remedy — *"see documentation"*, *"contact support"* — turns a panel of reasons into a
panel of one sentence repeated, and a reader stops reading it on the second row. Worse, it is
**indistinguishable from a panel that has thought about each group**, which makes it the flattering
failure: the page looks complete and says nothing.

So a reason code that can reach a cell either has a `Remedy` written for it, or is listed in
`remedies.yaml`'s `deliberately_unremediable` block **with a written argument**. There is no third
state and no default.

## `applies_to: "*"` does not load

A wildcard selector is a generic remedy wearing a specific one's clothes: it satisfies "every group
has a remedy" while saying nothing about any group. The loader refuses it, and
`test_unchecked__wildcard_remedy_does_not_load` is the guard.

## `exhibits=None` is NOT `exhibits=()` — the absent ≠ empty rule, applied to our own panel

- **`None`** renders *"residue not yet measured"*. It is a statement about **us**.
- **`()`** renders *"the residue procedure ran and returned no survivors"*. It is a statement about
  **the check set**, and per NC-C02 it would itself be a finding worth investigating rather than
  good news — a residue of exactly zero means either the check set is complete or the fault model
  is too narrow to construct a survivor, and the second is far more likely.

**They must not look alike**, and the `None` rendering contains no digit at all so it cannot be
misread as a count.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

REMEDIES_PATH: Final[Path] = Path(__file__).resolve().parent / "remedies.yaml"

# A selector that matches everything is a remedy about nothing.
FORBIDDEN_SELECTOR: Final[str] = "*"

# A remedy shorter than this is a label, not an instrument. Measured against the shipped set: the
# shortest real one is well over 100 characters, because naming what would make a judgment
# checkable takes a sentence.
MIN_REMEDY_CHARS: Final[int] = 60


class MissingRemedy(KeyError):
    """A rendered group has no remedy. **A build error, never a placeholder.**"""


class GenericRemedy(ValueError):
    """A remedy that would apply to anything, and therefore says nothing about this."""


@dataclass(frozen=True, slots=True)
class Remedy:
    id: str
    reason_code: str
    applies_to: str            # a selector over stable keys / obligation ids; "*" is FORBIDDEN
    text: str                  # the instrument that would move this across the line
    source: str | None         # a citation, where one exists
    specific: bool             # asserted by the loader; a generic remedy does not load

    def __post_init__(self) -> None:
        if self.applies_to.strip() == FORBIDDEN_SELECTOR:
            raise GenericRemedy(
                f"{self.id}: applies_to is '*'. A wildcard selector satisfies 'every group has a "
                "remedy' while saying nothing about any group — a generic remedy wearing a "
                "specific one's clothes."
            )
        if not self.applies_to.strip():
            raise GenericRemedy(f"{self.id}: applies_to is empty")
        if len(self.text.strip()) < MIN_REMEDY_CHARS:
            raise GenericRemedy(
                f"{self.id}: the remedy is {len(self.text.strip())} characters. Naming the "
                "instrument that would make an obligation checkable takes a sentence; anything "
                "shorter is a label, and a panel of labels is a panel a reader stops reading."
            )
        if not self.specific:
            raise GenericRemedy(f"{self.id}: specific is False; a generic remedy does not load")


@dataclass(frozen=True, slots=True)
class UncheckedEntry:
    stable_key: str
    reason_code: str


@dataclass(frozen=True, slots=True)
class UncheckedGroup:
    reason_code: str
    count: int
    entries: tuple[UncheckedEntry, ...]
    remedy: Remedy

    def __post_init__(self) -> None:
        if self.count != len(self.entries):
            raise ValueError(
                f"{self.reason_code}: the group says {self.count} and carries "
                f"{len(self.entries)} entries. A count that is not the length of what it counts is "
                "the defect this whole project is named for."
            )


@dataclass(frozen=True, slots=True)
class ResidueExhibit:
    """A DEMONSTRATED survivor: a constructed falsehood no admitted check rejects.

    Exhibits sit **beneath** the reasons and are labelled as exhibits, not as reasons. A reason is
    *why we did not check*; an exhibit is *a thing we checked and still missed*. Presenting the
    second among the first would let a reader count it twice.
    """

    mutant_id: str
    what_was_changed: str
    why_nothing_caught_it: str


@dataclass(frozen=True, slots=True)
class UncheckedPanel:
    groups: tuple[UncheckedGroup, ...]
    total: int
    exhibits: tuple[ResidueExhibit, ...] | None   # None == not yet measured. NEVER ()

    def __post_init__(self) -> None:
        s = sum(g.count for g in self.groups)
        if s != self.total:
            raise ValueError(
                f"the groups sum to {s} and the panel says {self.total}. The panel PARTITIONS the "
                "unsettled set: every unchecked cell appears in exactly one group, and the total is "
                "the hero's second line."
            )
        keys = [e.stable_key for g in self.groups for e in g.entries]
        if len(keys) != len(set(keys)):
            raise ValueError("a cell appears in two groups; the panel is not a partition")

    @property
    def residue_state(self) -> str:
        """The two states, kept apart in the rendering as well as in the type."""
        if self.exhibits is None:
            return "residue not yet measured — the procedure has not been run against this predicate set"
        if not self.exhibits:
            return (
                "the residue procedure ran and returned no survivors. That is not good news on its "
                "own: a residue of zero means either the check set is complete or the fault model "
                "is too narrow to construct a survivor, and the second is more likely"
            )
        return f"{len(self.exhibits)} demonstrated survivors"


def load_remedies(path: Path = REMEDIES_PATH) -> tuple[dict[str, Remedy], dict[str, str]]:
    """`({reason_code: Remedy}, {reason_code: argument})`. **Raises on a generic remedy.**"""
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    remedies: dict[str, Remedy] = {}
    for r in raw.get("remedies") or ():
        rem = Remedy(
            id=r["id"], reason_code=r["reason_code"], applies_to=r["applies_to"],
            text=r["text"].strip(), source=r.get("source"), specific=bool(r.get("specific", False)),
        )
        remedies[rem.reason_code] = rem
    unremediable = {
        k: str(v).strip() for k, v in (raw.get("deliberately_unremediable") or {}).items()
    }
    for code, argument in unremediable.items():
        if len(argument) < MIN_REMEDY_CHARS:
            raise GenericRemedy(
                f"{code} is listed as deliberately unremediable with a {len(argument)}-character "
                "argument. Declining to name a remedy requires saying why, at length — otherwise "
                "the block is a way of moving a reason code out of the panel."
            )
    return remedies, unremediable


def build_unchecked_panel(
    run: Any, residue: Any | None = None, *, path: Path = REMEDIES_PATH
) -> UncheckedPanel:
    """Group every unsettled cell by reason code. **Raises `MissingRemedy` rather than defaulting.**"""
    from cdfc.verdict.reasons import ReasonCode

    remedies, unremediable = load_remedies(path)

    settled = {"PASS", "FAIL"}
    buckets: dict[str, list[UncheckedEntry]] = {}
    for cell in run.cells:
        state = str(getattr(cell.state, "value", cell.state)).upper()
        if state in settled or cell.reason is None:
            continue
        code = str(getattr(cell.reason, "value", cell.reason))
        buckets.setdefault(code, []).append(UncheckedEntry(cell.stable_key, code))

    groups: list[UncheckedGroup] = []
    for code in sorted(buckets):
        if code not in remedies:
            if code in unremediable:
                # Listed with an argument — it still renders, carrying the argument as its remedy.
                rem = Remedy(id=f"unremediable::{code}", reason_code=code, applies_to=code,
                             text=unremediable[code], source=None, specific=True)
            else:
                raise MissingRemedy(
                    f"{code} reached {len(buckets[code])} cells and has no remedy. Write one in "
                    "remedies.yaml, or list it under `deliberately_unremediable` with an argument. "
                    "There is no fallback string: a generic remedy makes a panel of reasons into "
                    "one sentence repeated, and it looks exactly like a panel that thought about "
                    "each group."
                )
        else:
            rem = remedies[code]
        entries = tuple(buckets[code])
        groups.append(UncheckedGroup(code, len(entries), entries, rem))

    known = {m.value for m in ReasonCode}
    unknown = sorted(set(buckets) - known)
    if unknown:
        raise ValueError(
            f"{unknown} are not in the closed thirty-code vocabulary. A reason outside the "
            "vocabulary is a reason nobody wrote a remedy for and nobody can count."
        )

    return UncheckedPanel(
        groups=tuple(groups),
        total=sum(g.count for g in groups),
        # None, not (). The residue procedure has not been run against this predicate set.
        exhibits=_exhibits(residue),
    )


def _exhibits(residue: Any | None) -> tuple[ResidueExhibit, ...] | None:
    """`None` when unmeasured. **Never `()` for an unmeasured residue.**"""
    if residue is None:
        return None
    rows = getattr(residue, "survivors", None)
    if rows is None:
        return None
    return tuple(
        ResidueExhibit(
            mutant_id=str(getattr(r, "mutant_id", "?")),
            what_was_changed=str(getattr(r, "what_was_changed", "")),
            why_nothing_caught_it=str(getattr(r, "why", "")),
        )
        for r in rows
    )
