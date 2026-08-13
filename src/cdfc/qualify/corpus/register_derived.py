r"""P8-B2 — the REGISTER-DERIVED oracle, and the exhibit that explains why the FFR column exists.

**The warrant, stated narrowly because a narrow warrant stated broadly is the error:**

> **Every entity in the register is validly registered, so a predicate asserting MEMBERSHIP cannot
> have a true positive there.**

It licenses an FFR for the **membership / identity** classes and for nothing else. It is not an
oracle about amounts, dates or arithmetic, and it never becomes one.

## The measurement, taken first-hand

Snapshot `fixtures/register/fme-register__<sha8>.json`, 229 live FMEs, **229 of 229** carrying a
non-empty `RegistrationNumber`. So the predicate is *satisfiable*. And then:

| checker | fires on | what that is |
|---|---:|---|
| the obvious **format regex** `^IFSCA/FME/(I\|II\|III)/\d{4}-\d{2}/\d+$` | **87 of 229** | a FALSE FAILURE on every one — the entity is validly registered |
| **set membership** under the declared normalisation | **0 of 229** | the admitted predicate |

**Two incompatible identifier schemes are live in the same register on the same day** — 142 legacy
and 84 in the newer `FDM<YYYY><AAA><NNNN>` form — and three match neither. The three are the whole
exercise, and each is verified at codepoint level by `test_golden__the_three_stragglers`:

1. `IFSCA/FME/IV/2023-24/033` — Roman numeral **IV**, where the FME categories are I, II and III.
2. `IFSCA/FME/III/2022‑23/037` — the hyphen is **`U+2011 NON-BREAKING HYPHEN`**, not `U+002D`.
   **This is a homoglyph in a LIVE registration number**, and it is why
   `textsource.REFUSED_TRANSFORMATIONS` refuses to unify dashes: a normaliser that folded them
   would make the gate that catches this unfailable.
3. `100` — a bare integer.

**Nothing here reaches the network.** A host function resolves against the snapshot and never live
(NC-X01): a verdict that depends on what a remote server said at verdict time is a verdict nobody
can re-derive.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

SNAPSHOT_DIR: Final[Path] = Path("fixtures/register")

# The obvious regex any competent engineer would write, and the reason this module exists.
FORMAT_REGEX: Final[re.Pattern[str]] = re.compile(r"^IFSCA/FME/(I|II|III)/\d{4}-\d{2}/\d+$")
NEW_SCHEME_REGEX: Final[re.Pattern[str]] = re.compile(r"^FDM\d{4}[A-Z]{3}\d{4}$")

# The dash family, folded to U+002D at the membership boundary. NFKC alone does NOT do this: it
# maps U+2011 to U+2010, and both are still not U+002D.
DASHES: Final[tuple[str, ...]] = ("\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212")

# THE DECLARED NORMALISATION, and every element of it is load-bearing on this data.
NORMALISATION: Final[tuple[tuple[str, str], ...]] = (
    ("nfkc", "compatibility forms fold; a full-width digit is a digit"),
    ("dashes_to_u002d", "a LIVE registration number carries U+2011 NON-BREAKING HYPHEN, and the "
                        "whole dash family folds to U+002D here. **AFTER NFKC, and the order is a "
                        "defect this module's own golden test caught**: NFKC maps U+2011 to U+2010 "
                        "(HYPHEN), not to U+002D, so a `replace(U+2011, U+002D)` written before "
                        "NFKC silently stopped matching the one number it existed for. Folding is "
                        "done HERE, at the membership boundary, and NOT in the instrument text — "
                        "`textsource.REFUSED_TRANSFORMATIONS` keeps them distinct so a homoglyph "
                        "planted in a QUOTE is still catchable"),
    ("strip", "leading and trailing whitespace is a transport artefact"),
    ("casefold", "the register is not case-consistent across its two identifier schemes"),
)


class SnapshotMissing(FileNotFoundError):
    """No pinned register snapshot. A membership check does not fall back to a format guess."""


@dataclass(frozen=True, slots=True)
class RegisterSnapshot:
    sha256: str
    source: str
    records: tuple[Mapping[str, object], ...]

    @property
    def n(self) -> int:
        return len(self.records)

    def numbers(self) -> tuple[str, ...]:
        return tuple(str(r.get("RegistrationNumber") or "") for r in self.records)

    def membership_set(self) -> frozenset[str]:
        return frozenset(normalise(n) for n in self.numbers() if n)

    def n_resolving(self) -> int:
        """**229 of 229.** The predicate is SATISFIABLE — which is what makes the 87 a finding
        about the checker rather than about the register."""
        return sum(1 for n in self.numbers() if n)


def normalise(value: str) -> str:
    """The declared normalisation. Applied at the MEMBERSHIP boundary and nowhere else."""
    s = unicodedata.normalize("NFKC", value)
    for dash in DASHES:
        s = s.replace(dash, "-")
    return s.strip().casefold()


def load(directory: Path = SNAPSHOT_DIR) -> RegisterSnapshot:
    files = sorted(directory.glob("fme-register__*.json"))
    if not files:
        raise SnapshotMissing(
            f"no pinned register snapshot in {directory}. A membership check resolves against a "
            "SNAPSHOT and never live (NC-X01); it does not degrade to a format guess, because a "
            "format guess is the 87-of-229 false-failure rate this module exists to publish."
        )
    doc = json.loads(files[-1].read_text(encoding="utf-8"))
    return RegisterSnapshot(sha256=files[-1].stem.split("__")[-1], source=doc["source"],
                            records=tuple(doc["records"]))


# --- the two checkers, and the gap between them is the exhibit ---------------------------


def format_regex_fires(snapshot: RegisterSnapshot) -> tuple[str, ...]:
    """Every registration number the OBVIOUS regex rejects. **Each one is a false failure.**"""
    return tuple(n for n in snapshot.numbers() if not FORMAT_REGEX.match(n or ""))


def membership_fires(snapshot: RegisterSnapshot, values: Sequence[str] | None = None) -> tuple[str, ...]:
    """Every value absent from the register under the declared normalisation.

    Against the register's own numbers this is EMPTY by construction — and that is the point: the
    admitted predicate cannot have a true positive here, so anything it fires on is a false one.
    """
    members = snapshot.membership_set()
    return tuple(v for v in (values if values is not None else snapshot.numbers())
                 if normalise(v) not in members)


def stragglers(snapshot: RegisterSnapshot) -> tuple[tuple[str, str], ...]:
    """`(registration number, entity)` for every number matching NEITHER live scheme."""
    return tuple(
        (str(r.get("RegistrationNumber") or ""), str(r.get("list_title") or ""))
        for r in snapshot.records
        if not FORMAT_REGEX.match(str(r.get("RegistrationNumber") or ""))
        and not NEW_SCHEME_REGEX.match(str(r.get("RegistrationNumber") or ""))
    )
