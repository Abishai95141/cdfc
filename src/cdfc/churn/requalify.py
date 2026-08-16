"""V4 — the PROVISIONAL sweep. **The settled fraction falls, and it falls for the right reason.**

Criterion A8 is *the number goes down when the template changes*. That is easy to satisfy wrongly
and the wrong way is nearly invisible on a chart:

* **Right:** the affected predicates keep running, keep reporting findings, and stop *settling*.
  The filer still sees every finding; the coverage number stops claiming those cells were decided.
* **Wrong:** the affected predicates stop running. The number falls by the same amount, the chart
  looks identical, and detection has silently been lost.

`ChurnReport` makes the two distinguishable by construction: `moved_to_provisional`,
`still_running` and `numbers_hidden` are asserted EQUAL AS SETS. Under the wrong implementation
`still_running` is empty while the other two are not, and the assertion fires.

## Which predicates move — two signals, and the first one is the one that matters

**(a) A vocabulary it declares changed.** A membership predicate carries a `template.vocab.<slug>`
key, and the vocabulary behind that key is resolved from the pinned blank. On the FY2029-30 fixture
exactly one vocabulary moves — `n_1_introduction_d3`, from four financial years to five — and every
predicate declaring it was qualified against a set that no longer describes the template. It would
report a **failure on a valid filing**, which is the definition of a false failure, which is
exactly why it must stop settling.

**(b) A sheet it reads changed.** Coarser, and it is the catch-all for template edits that are not
vocabulary edits.

Cell-level granularity was tried first and is WRONG here, in the silent direction. The FY2029-30
edit adds `Dropdown!E7`, and *no predicate reads E7* — at harvest time it did not exist. A
cell-level sweep reports **nothing changed** precisely in the case the rule exists for. The first
build of this module did that and moved zero predicates, which is how it was found.

`ChurnReport.granularity` states the rule on the wire. A sweep that is coarse and says so can be
narrowed later; a sweep that is precise and wrong cannot be detected at all.
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

GRANULARITY: Final[str] = (
    "VOCABULARY, then SHEET. A predicate moves when a template vocabulary it declares changed, or "
    "when a sheet it reads differs between the two workbooks. Not cell-level: the FY2029-30 bump "
    "adds a cell no predicate reads, and every predicate carrying the old year vocabulary is "
    "nonetheless wrong about a valid filing."
)

_REL_RE: Final[re.Pattern[str]] = re.compile(r'Id="(rId\d+)"[^>]*Target="([^"]+)"')
_SHEET_RE: Final[re.Pattern[str]] = re.compile(r'<sheet[^>]*name="([^"]+)"[^>]*r:id="(rId\d+)"')


class ChurnArithmeticError(AssertionError):
    """The three sets disagree, or the numerator rose. Either is a sweep that lost detection."""


def _part_to_sheet(path: Path) -> dict[str, str]:
    """`xl/worksheets/sheetN.xml` -> the sheet's display name, via the workbook relationships."""
    with zipfile.ZipFile(path) as z:
        rels = dict(_REL_RE.findall(z.read("xl/_rels/workbook.xml.rels").decode("utf-8")))
        book = z.read("xl/workbook.xml").decode("utf-8")
    out: dict[str, str] = {}
    for name, rid in _SHEET_RE.findall(book):
        target = rels.get(rid, "")
        if target:
            out["xl/" + target.lstrip("/")] = name
    return out


def changed_sheets(old: Path, new: Path) -> frozenset[str]:
    """The DISPLAY NAMES of sheets whose XML differs. **A part with no sheet name is not dropped.**

    An unmapped part — a changed `sharedStrings.xml`, a changed data model — cannot be attributed
    to a sheet, and silently ignoring it would let a whole class of template change sweep nothing.
    Those parts surface as the sentinel `*` which matches every predicate, because a change nobody
    can localise is a change that might touch anything.
    """
    from cdfc.qualify.surgery import differing_parts

    mapping = _part_to_sheet(new)
    out: set[str] = set()
    for part in differing_parts(old, new):
        name = mapping.get(part)
        if name is not None:
            out.add(name)
        elif part.startswith("xl/") and not part.endswith(".rels"):
            out.add("*")
    return frozenset(out)


def changed_vocabularies(old: Path, new: Path) -> frozenset[str]:
    """The `template.vocab.<slug>` names whose MEMBER SET differs between two blanks.

    Order-insensitive: a vocabulary listing the same four years in a different order is the same
    vocabulary, and moving predicates for a reordering would make every sweep after a cosmetic edit
    look like a real one.
    """
    from cdfc.facts.build import template_tree

    a = template_tree(old)["vocab"]
    b = template_tree(new)["vocab"]
    return frozenset(
        k for k in set(a) | set(b)
        if sorted(a.get(k, [])) != sorted(b.get(k, []))
    )


@dataclass(frozen=True, slots=True)
class ChurnReport:
    """`moved_to_provisional == still_running == numbers_hidden`, asserted rather than intended."""

    old_template_sha256: str
    new_template_sha256: str
    changed_sheets: tuple[str, ...]
    changed_vocabularies: tuple[str, ...]
    moved_to_provisional: tuple[str, ...]
    # WHICH SIGNAL MOVED EACH ONE. The two are not equally strong and collapsing them would hide
    # that: a vocabulary change is a demonstrated false-failure risk on a valid filing, and a sheet
    # change is a conservative *we cannot rule it out*. A reader deciding whether to re-qualify
    # nine predicates needs to know which of the two they are looking at.
    moved_reason: dict[str, str]
    still_running: tuple[str, ...]
    numbers_hidden: tuple[str, ...]
    numerator_delta: int
    old_settled: int
    new_settled: int
    field_surface: int
    granularity: str = GRANULARITY

    def __post_init__(self) -> None:
        a, b, c = (set(self.moved_to_provisional), set(self.still_running),
                   set(self.numbers_hidden))
        if not (a == b == c):
            raise ChurnArithmeticError(
                f"moved={sorted(a)}, still_running={sorted(b)}, hidden={sorted(c)}. A PROVISIONAL "
                "predicate STILL RUNS: detection is not lost, only the claim to have settled the "
                "cell is. A sweep where these three differ has either kept a number it should have "
                "hidden or stopped running a check it should have kept."
            )
        if self.numerator_delta > 0:
            raise ChurnArithmeticError(
                f"numerator_delta={self.numerator_delta}. A template bump can only remove cells "
                "from the settled numerator. A rise means the sweep re-admitted something, and "
                "nothing re-admits automatically."
            )
        if self.new_settled != self.old_settled + self.numerator_delta:
            raise ChurnArithmeticError(
                f"{self.old_settled} + ({self.numerator_delta}) != {self.new_settled}"
            )

    @property
    def cause(self) -> str:
        """The history point's `cause`. **A step-down without one does not render.**"""
        what = ", ".join(self.changed_vocabularies) or ", ".join(self.changed_sheets) \
            or "(nothing localised)"
        return (
            f"template {self.old_template_sha256[:12]} → {self.new_template_sha256[:12]}: "
            f"{what} changed, {len(self.moved_to_provisional)} predicates moved to PROVISIONAL "
            "and stopped settling. They still run and still report findings."
        )


def _sha256_of(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sheet_of(stable_key: str) -> str:
    return stable_key.split("!", 1)[0] if "!" in stable_key else ""


def declared_vocabularies(candidates: Any) -> dict[str, frozenset[str]]:
    """predicate id -> the `template.vocab.<slug>` names it declares in `schema_keys`.

    Read from the DECLARED keys rather than from the run. A run's `stable_key` is a filing cell, so
    a vocabulary dependency is invisible in it — which is the exact blindness that made the first
    version of this sweep move nothing.
    """
    out: dict[str, frozenset[str]] = {}
    for c in candidates:
        names = {
            k.split("template.vocab.", 1)[1]
            for k in getattr(c, "schema_keys", ())
            if k.startswith("template.vocab.")
        }
        if names:
            out[c.id] = frozenset(names)
    return out


def on_template_change(
    old: Path | str,
    new: Path | str,
    *,
    run_dir: Path,
    candidates: Any = None,
    read_sheets: dict[str, frozenset[str]] | None = None,
) -> ChurnReport:
    """Sweep one run against a template bump.

    `candidates` supplies the DECLARED vocabulary dependencies — signal (a), and the one that
    actually fires on a version bump. When it is omitted the sweep falls back to signal (b) alone
    and **says so** by leaving `changed_vocabularies` empty; it does not silently report that a
    vocabulary bump moved nobody.

    `read_sheets` maps predicate id -> the sheets it reads. When not supplied it is derived from the
    run itself — the `stable_key` of every cell the predicate evaluated.
    """
    old_p, new_p = Path(old), Path(new)
    sheets = changed_sheets(old_p, new_p)
    vocabs = changed_vocabularies(old_p, new_p) if candidates is not None else frozenset()

    records = [
        json.loads(line)
        for line in (run_dir / "run.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    closure = manifest["closure"]

    observed: dict[str, set[str]] = {}
    for r in records:
        pid = r.get("predicate_id")
        if pid:
            observed.setdefault(str(pid), set()).add(_sheet_of(str(r.get("stable_key", ""))))
    reads = read_sheets or {k: frozenset(v) for k, v in observed.items()}
    declared = declared_vocabularies(candidates) if candidates is not None else {}

    # Only predicates the run actually exercised can lose a settled cell, so the moved set is
    # intersected with what ran. A predicate that moved but settled nothing changes no number and
    # would inflate the reported count without moving the chart.
    ran = set(observed)
    why: dict[str, str] = {}
    for pid in sorted(ran):
        hit = declared.get(pid, frozenset()) & vocabs
        if hit:
            why[pid] = (
                f"VOCABULARY {', '.join(sorted(hit))} changed. This predicate was qualified "
                "against a member set the template no longer has, so it would report a FAILURE on "
                "a valid filing."
            )
        elif "*" in sheets:
            why[pid] = (
                "a changed part could not be attributed to a sheet, so no predicate can be ruled "
                "out. Conservative: this is not a demonstrated defect."
            )
        elif reads.get(pid, frozenset()) & sheets:
            why[pid] = (
                f"SHEET {', '.join(sorted(reads[pid] & sheets))} changed. Conservative: the change "
                "may not touch anything this predicate reads, and it has not been shown to."
            )
    moved = tuple(sorted(why))

    # The cells that STOP SETTLING. Counted over DISTINCT stable keys, and only where no predicate
    # that stayed ACTIVE also settles the same cell -- a cell settled by two predicates, one of
    # which moved, is still settled. Counting the evaluations instead of the cells would
    # over-report the fall, which is the flattering direction for a product whose pitch is that its
    # number can go down.
    settled_by_moved: set[str] = set()
    settled_by_kept: set[str] = set()
    for r in records:
        if not r.get("settles"):
            continue
        key = str(r.get("stable_key", ""))
        (settled_by_moved if str(r.get("predicate_id")) in set(moved) else settled_by_kept).add(key)
    lost = settled_by_moved - settled_by_kept

    old_settled = int(closure["settled"])
    delta = -len(lost)
    return ChurnReport(
        old_template_sha256=_sha256_of(old_p),
        new_template_sha256=_sha256_of(new_p),
        changed_sheets=tuple(sorted(sheets)),
        changed_vocabularies=tuple(sorted(vocabs)),
        moved_to_provisional=moved,
        moved_reason=why,
        # V3: the SAME predicates. They keep running; only their claim to settle is withdrawn.
        still_running=moved,
        numbers_hidden=moved,
        numerator_delta=delta,
        old_settled=old_settled,
        new_settled=old_settled + delta,
        field_surface=int(closure["cellsTotal"]),
    )


def provisional_states(report: ChurnReport, current: dict[str, str]) -> dict[str, str]:
    """Apply the sweep to a state map. **There is no branch here that writes `ACTIVE`.**

    `test_quarantine__nothing_re_admits_automatically` asserts that structurally, by walking the
    AST of this package for an assignment of the literal — so the absence is checked rather than
    promised. Clearing a state is a human act.
    """
    out = dict(current)
    for pid in report.moved_to_provisional:
        out[pid] = "PROVISIONAL"
    return out
