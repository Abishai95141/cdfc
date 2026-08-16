"""The G-CORPUS trichotomy, in `src/` where a rule belongs. **The middle branch has a name.**

This was `_gcorpus()` inside `tools/measure/p8_ffr.py`. It decides whether any predicate class may
carry a false-failure digit, and a decision of that weight living in a measurement script means
every other surface that needs it either re-implements it or quotes a remembered string.

## Why the middle branch exists at all

The gate as first written had two branches. The `RESTRICTED` case — `n >= 30` filings but
`n_non_synthetic == 0` — fell through the unnamed fallback into PASS, so **shipping a restricted
corpus looked exactly like shipping a qualified one.** Naming it is the repair, and the literal
string `G-CORPUS: RESTRICTED` renders on every surface that carries an FFR-bearing number.

The census is read from `fixtures/corpus_manifest.json`, which the corpus build commits. The corpus
itself is 110 MB of streamed filings and is deliberately not in the repository; the manifest is the
part a gate reads, and a gate whose data is absent must refuse rather than default.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

CORPUS_MANIFEST: Final[Path] = Path("fixtures/corpus_manifest.json")

# 30 filings. `tools/measure/p8_ffr.py` derives the severity thresholds from Wilson bounds; this is
# the corpus-size floor below which no class is licensed at all.
FLOOR: Final[int] = 30

Outcome = Literal["PASS", "RESTRICTED", "FAIL"]

RESTRICTED_LITERAL: Final[str] = "G-CORPUS: RESTRICTED"


class CorpusManifestAbsent(FileNotFoundError):
    """No census. **Not defaulted to FAIL, and certainly not to PASS.**

    FAIL is a measured verdict about a corpus that exists and is too small. An absent manifest is
    not a verdict about anything, and rendering it as one would put a gate's name on a
    determination nobody made.
    """


@dataclass(frozen=True, slots=True)
class Gcorpus:
    outcome: Outcome
    detail: str
    census: dict[str, int]
    provenance: str
    derived_by: str

    @property
    def digits_licensed(self) -> bool:
        """`FAIL` renders **no digit anywhere**. That is the whole point of the trichotomy."""
        return self.outcome != "FAIL"


def decide(n: int, n_non_synthetic: int, *, provenance: str = "", derived_by: str = "") -> Gcorpus:
    census = {"n": n, "n_non_synthetic": n_non_synthetic}
    if n_non_synthetic >= FLOOR:
        return Gcorpus(
            "PASS",
            "Every predicate class may be admitted and `BLOCKING` is reachable.",
            census, provenance, derived_by,
        )
    if n >= FLOOR:
        return Gcorpus(
            "RESTRICTED",
            f"`n = {n}` but `n_non_synthetic = {n_non_synthetic}`: the corpus is "
            "`TEMPLATE-COMPUTED`. Only the classes it licenses under P8-B2's mapping table are "
            "admissible — all classes, because `derived_by=FOREIGN_ENGINE` makes the oracle "
            "independent of this evaluator — and every severity tier is capped at `ADVISORY`. "
            "A restricted pass rendered as a pass is the failure this gate exists to prevent.",
            census, provenance, derived_by,
        )
    return Gcorpus(
        "FAIL",
        f"`n = {n}` is below the floor of {FLOOR}. No predicate is admitted and every "
        "false-failure rate renders `uninformative` — **with no digit anywhere.**",
        census, provenance, derived_by,
    )


def load(manifest: Path = CORPUS_MANIFEST) -> Gcorpus:
    if not manifest.is_file():
        raise CorpusManifestAbsent(
            f"{manifest} is not on disk, so the corpus census is unknown. The G-CORPUS outcome is "
            "not defaulted: an unmeasured corpus and a failed one are different facts."
        )
    m = json.loads(manifest.read_text(encoding="utf-8"))
    return decide(
        int(m["n"]), int(m["n_non_synthetic"]),
        provenance=str(m.get("provenance", "")), derived_by=str(m.get("derived_by", "")),
    )
