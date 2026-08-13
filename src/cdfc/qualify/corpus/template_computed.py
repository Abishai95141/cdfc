"""P8-B2 — the TEMPLATE-COMPUTED corpus, with `derived_by` recorded (F2).

**F2, and it is the repair this build exists for.** The corpus generator originally filled the
inputs and *"let the workbook's own 505 formula cells compute the rest via `src/cdfc/calc/`"*, and
the predicates that check those formulas are checked against **the same function**. Three
load-bearing acceptance conditions were therefore tautologies, and at G4 it meant
`synthesise(..., n=189)` — one command, one afternoon, deterministic from a seed — **bought a
`BLOCKING` severity tier from a corpus the product generated about itself.**

The expected FFR of an arithmetic predicate on such a corpus is zero *regardless of the predicate's
quality*, which is this plan's own definition of an uninformative rate and the exact condition
under which `SELF-AUTHORED` is refused a number.

**So what fills the DERIVED cells is now an explicit, recorded choice:**

| `derived_by` | who computes the derived cells | licenses an FFR for |
|---|---|---|
| `CALC` | **us** — `src/cdfc/calc/` | ONLY predicates whose read set is disjoint from `computed_cells`: membership, bounds, `conditional_required`. **Never `sum_identity`, `cross_sheet_equality`, `tally_identity`** |
| `FOREIGN_ENGINE` | a pinned offline engine sharing no module with `src/cdfc/` | **all classes, arithmetic included** — the oracle is independent — labelled `foreign-engine:<digest>` wherever the rate renders |
| `NONE` | nobody | nothing; an execution substrate for G1 and G3ᵉ, which is all §0.3 ever needed |

**`synthesise` no longer takes a `FormulaEvaluator` argument.** The generator selects its
derivation engine from `derived_by`, so handing it our evaluator is not something a caller can do
by habit.

**The foreign engine EXPORTS A VALUE TABLE and never re-serialises the workbook.** Its output is
read for numbers only; the workbook is written by `qualify/surgery.py`'s raw-zip path, for the same
measured reason openpyxl is banned — a round-trip drops 24 parts and all 19 `x14` validations, and
a fixture that differs from the pinned blank in ways nobody intended is not a control.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from cdfc.importgraph import import_closure
from cdfc.qualify.corpus._derive_foreign import ForeignEngineUnavailable
from cdfc.qualify.corpus.provenance import CorpusProvenance

# The pinned offline engine. It is named by PATH and by VERSION DIGEST, and a corpus generated with
# a different digest is a different corpus — `test_det__foreign_engine_corpus_is_pinned` makes
# engine drift a failing test rather than a silently different corpus.
SOFFICE: Final[Path] = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")

M: Final[str] = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

# **THE CLOSURE IS COMPUTED OVER THE MODULE THAT DERIVED THE VALUES, NOT OVER THIS DISPATCHER.**
# The AST walker sees every import, including one inside a function body, so a dispatcher that
# reached both derivation paths would put `cdfc.calc` in the closure of a corpus `cdfc.calc` never
# touched — the independence claim false in the direction that flatters us, which is F2 one level
# up. So each derivation lives in its own module and the closure is taken over that one.
DERIVATION_MODULE: Final[Mapping[str, str]] = {
    "CALC": "cdfc.qualify.corpus._derive_calc",
    "FOREIGN_ENGINE": "cdfc.qualify.corpus._derive_foreign",
    "NONE": "cdfc.qualify.corpus._writer",
}


class DerivedBy(StrEnum):
    CALC = "CALC"  # src/cdfc/calc/ computed the derived cells — OUR CODE
    FOREIGN_ENGINE = "FOREIGN_ENGINE"  # a digest-pinned engine, in a subprocess, sharing no module
    NONE = "NONE"  # inputs only; derived cells carry no value


@dataclass(frozen=True, slots=True)
class CleanFiling:
    path: Path
    sha256: str
    provenance: CorpusProvenance
    derived_by: DerivedBy
    derived_engine_digest: str | None  # required iff derived_by == FOREIGN_ENGINE
    computed_cells: frozenset[str]  # "Sheet!REF" — THE CELLS A PROGRAM DERIVED
    generator_import_closure: frozenset[str]  # module names, COMPUTED, never declared
    seed: int

    def __post_init__(self) -> None:
        if self.derived_by is DerivedBy.FOREIGN_ENGINE and not self.derived_engine_digest:
            raise ValueError(
                f"{self.path.name}: derived_by=FOREIGN_ENGINE with no engine digest. The digest is "
                "what makes 'a program independent of ours computed this' a checkable claim rather "
                "than a sentence."
            )
        if self.derived_by is not DerivedBy.FOREIGN_ENGINE and self.derived_engine_digest:
            raise ValueError(
                f"{self.path.name}: an engine digest under derived_by={self.derived_by}. The field "
                "records WHICH foreign engine ran; annotating it otherwise makes it unreadable."
            )
        if self.derived_by is DerivedBy.NONE and self.computed_cells:
            raise ValueError(
                f"{self.path.name}: derived_by=NONE with {len(self.computed_cells)} computed "
                "cell(s). NONE means nobody derived anything."
            )
        if self.derived_by is not DerivedBy.NONE and not self.computed_cells:
            raise ValueError(
                f"{self.path.name}: derived_by={self.derived_by} and computed_cells is EMPTY. An "
                "empty computed set makes `independent()`'s first conjunct vacuously true, which "
                "is F2 with the evidence removed instead of the check."
            )

    @property
    def label(self) -> str:
        """What renders wherever a rate drawn from this filing renders."""
        if self.derived_by is DerivedBy.FOREIGN_ENGINE:
            return f"{self.provenance.value} · foreign-engine:{(self.derived_engine_digest or '')[:12]}"
        return f"{self.provenance.value} · derived_by={self.derived_by.value}"


def engine_digest() -> str:
    """The pinned engine's identity. Raises rather than defaulting: an unnamed engine is not a
    foreign engine, it is an assumption."""
    if not SOFFICE.is_file():
        raise ForeignEngineUnavailable(
            f"the pinned offline engine is not at {SOFFICE}. derived_by=FOREIGN_ENGINE is "
            "unavailable, so the arithmetic classes have no admissible corpus until the blind "
            "fill lands — which the funnel reports as NOT ADMITTED for want of a corpus."
        )
    try:
        r = subprocess.run([str(SOFFICE), "--version"], capture_output=True, text=True, timeout=120)
        version = r.stdout.strip() or r.stderr.strip()
    except (OSError, subprocess.SubprocessError) as e:
        raise ForeignEngineUnavailable(f"the pinned engine did not report a version: {e}") from e
    if not version:
        raise ForeignEngineUnavailable("the pinned engine reported no version")
    return hashlib.sha256(version.encode("utf-8")).hexdigest()


def generator_closure(derived_by: DerivedBy) -> frozenset[str]:
    """The DERIVATION's first-party import closure, BY AST, never declared.

    Under `FOREIGN_ENGINE` the derived values come out of a subprocess, so `cdfc.calc` is not in
    the closure of the code that produced them. Under `CALC` it is — and that is the POSITIVE
    CONTROL: a check that cannot detect the case it exists for is not a check.
    """
    module = DERIVATION_MODULE[derived_by.value]
    return frozenset(set(import_closure(module)) | {module})


# --- generation ------------------------------------------------------------------------------


def _lawful_inputs(ctx, rng) -> dict[tuple[str, str], object]:
    """A lawful value for every field-surface cell that is not a formula, VARIED BY SEED.

    Lawful means JOINTLY lawful, not merely cell-wise lawful. With 100 in every input a ten-row
    `SUM` produced 1,000 in a total cell the template bounds to `[0, 100]`, and the bound predicate
    FAILED on the "clean" filing — correctly: the filing was unlawful in a way no single cell
    showed. The declared distribution is therefore **small integers in `[1, 5]`**, which keeps every
    derived total inside the bounds this workbook declares while still varying between filings.
    """
    from cdfc.predicates.harvest import expand, resolve_vocabulary

    formula_refs = {(s, f.ref) for s, fs in ctx.formulas_by_sheet.items() for f in fs}
    values: dict[tuple[str, str], object] = {}

    for sheet, records in sorted(ctx.validations_by_sheet.items()):
        for dv in records:
            if not dv.sqref.split():
                continue
            refs = [c for part in dv.sqref.split() for c in expand(part.replace("$", ""))]
            if dv.type == "list":
                vocab, _ = resolve_vocabulary(ctx, sheet, dv.formula1)
                chosen: object | None = vocab[rng.randrange(len(vocab))] if vocab else None
            elif dv.type in ("whole", "decimal", "date"):
                chosen = _inside(dv.formula1, dv.formula2, dv.operator, rng)
            else:
                chosen = None
            if chosen is None:
                continue
            for ref in refs:
                if (sheet, ref) in formula_refs or (sheet, ref) not in ctx.key_of:
                    continue
                values[(sheet, ref)] = chosen

    for sheet, ref in sorted(ctx.wb.unlocked_cells):
        if (sheet, ref) in formula_refs or (sheet, ref) in values:
            continue
        if (sheet, ref) in ctx.key_of:
            values[(sheet, ref)] = rng.randint(1, 5)
    return values


def _inside(f1: str | None, f2: str | None, operator: str, rng) -> object | None:
    def num(x: str | None) -> float | None:
        try:
            return float(str(x).strip())
        except (TypeError, ValueError):
            return None

    lo, hi = num(f1), num(f2)
    if lo is None:
        return None
    if hi is not None and hi >= lo:
        span = min(int(hi - lo), 4)
        return _fit(lo + (rng.randint(0, span) if span > 0 else 0))
    op = operator or ">="
    if op in (">=", "=="):
        return _fit(lo + (rng.randint(0, 4) if op == ">=" else 0))
    if op == ">":
        return _fit(lo + 1 + rng.randint(0, 4))
    if op in ("<=", "<"):
        return _fit(lo - (0 if op == "<=" else 1) - rng.randint(0, 4))
    return _fit(lo)


def _fit(x: float) -> object:
    """Inside int64, and an integer when it can be. A float in a filing is a value nobody can
    re-derive; R4 makes money an integer count."""
    if abs(x) > 9.2e18:
        return 0
    return int(x) if float(x).is_integer() else round(x, 3)


def synthesise(
    blank: Path,
    out_dir: Path,
    *,
    seed: int,
    n: int,
    derived_by: DerivedBy,
) -> tuple[CleanFiling, ...]:
    """Fill only the INPUT cells; what fills the DERIVED cells is `derived_by`'s choice.

    Every output carries `CDFC_SYNTHETIC=true`, `CDFC_PROVENANCE=TEMPLATE-COMPUTED`,
    `CDFC_DERIVED_BY` and, for `FOREIGN_ENGINE`, the engine digest — in a `.prov.json` sidecar
    whose `may_be_quoted_as` is a SENTENCE rather than a token, because a fixture whose licence you
    cannot read off its own record is a fixture somebody will reuse in the wrong gate.
    """
    import json
    import random

    from cdfc.predicates.harvest import _load_context

    if n <= 0:
        raise ValueError("a corpus of no filings is not a corpus")
    digest = engine_digest() if derived_by is DerivedBy.FOREIGN_ENGINE else None
    ctx = _load_context(blank)
    closure = generator_closure(derived_by)
    out_dir.mkdir(parents=True, exist_ok=True)

    made: list[CleanFiling] = []
    for i in range(n):
        rng = random.Random(f"{seed}:{i}")
        inputs = _lawful_inputs(ctx, rng)
        stem = f"clean__template-computed-{derived_by.value.lower()}__fme-{i:03d}"
        target = out_dir / f"{stem}.xlsx"
        computed = _derive(blank, target, inputs, derived_by=derived_by)
        sha = hashlib.sha256(target.read_bytes()).hexdigest()
        final = out_dir / f"{stem}__{sha[:8]}.xlsx"
        if final != target:
            target.replace(final)
        filing = CleanFiling(
            path=final, sha256=sha, provenance=CorpusProvenance.TEMPLATE_COMPUTED,
            derived_by=derived_by, derived_engine_digest=digest,
            computed_cells=computed, generator_import_closure=closure, seed=seed * 10_000 + i,
        )
        (final.with_suffix(".prov.json")).write_text(json.dumps({
            "CDFC_SYNTHETIC": True,
            "CDFC_PROVENANCE": CorpusProvenance.TEMPLATE_COMPUTED.value,
            "CDFC_DERIVED_BY": derived_by.value,
            "CDFC_DERIVED_ENGINE_DIGEST": digest,
            "sha256": sha,
            "seed": filing.seed,
            "computed_cells": sorted(computed),
            "generator_import_closure": sorted(closure),
            "may_be_quoted_as": _quotable(derived_by, digest),
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        made.append(filing)
    return tuple(made)


def _quotable(derived_by: DerivedBy, digest: str | None) -> str:
    if derived_by is DerivedBy.CALC:
        return (
            "A TEMPLATE-COMPUTED filing whose derived cells THIS PROJECT'S OWN evaluator computed. "
            "It licenses a false-failure rate ONLY for predicates whose read set is disjoint from "
            "computed_cells; for any arithmetic predicate the rate is zero by construction and "
            "g4_ffr.check() raises UninformativeCorpusError. It can never reach BLOCKING."
        )
    if derived_by is DerivedBy.FOREIGN_ENGINE:
        return (
            "A TEMPLATE-COMPUTED filing whose derived cells were computed by a pinned offline "
            f"engine (foreign-engine:{(digest or '')[:12]}) sharing no module with src/cdfc/. It "
            "licenses a false-failure rate for ALL predicate classes, arithmetic included, and the "
            "engine digest renders wherever the rate renders. It is still SYNTHETIC and can never "
            "reach BLOCKING."
        )
    return (
        "A TEMPLATE-COMPUTED filing with NO derived values: an execution substrate for G1 and the "
        "empirical arm of G3. It licenses no false-failure rate at all."
    )


def _derive(
    blank: Path, target: Path, inputs: Mapping[tuple[str, str], object], *, derived_by: DerivedBy
) -> frozenset[str]:
    """Write the filing and return **the cells a program actually derived a value into**.

    The set is DIFFED against the input set rather than trusted from the caller
    (`test_tc__computed_cells_are_recorded_and_exact`): a `computed_cells` the caller declares is a
    string in a record, and `independent()`'s first conjunct is only a check if that set is what
    actually happened.
    """
    from cdfc.qualify.corpus._writer import strip_and_write, write_values

    strip_and_write(blank, target, inputs)
    if derived_by is DerivedBy.NONE:
        return frozenset()

    if derived_by is DerivedBy.CALC:
        from cdfc.qualify.corpus._derive_calc import value_table

        table = value_table(target)
    else:
        from cdfc.qualify.corpus._derive_foreign import value_table as foreign_table

        table = foreign_table(SOFFICE, target)

    # A derived value written into a cell the FILER filled would mean the engine overwrote an
    # input, and `computed_cells` would then claim a cell the filer owns.
    overlap = sorted(set(table) & set(inputs))
    if overlap:
        raise ValueError(
            f"{target.name}: the derivation wrote {len(overlap)} cell(s) the filer filled, e.g. "
            f"{overlap[:3]}. `computed_cells` would then claim a cell nobody computed."
        )
    write_values(blank, target, table)
    return frozenset(f"{s}!{r}" for (s, r) in table)


def corpus_digest(filings: Sequence[CleanFiling]) -> str:
    """One digest over the whole corpus, so engine drift is a FAILING TEST rather than a silently
    different corpus."""
    from cdfc.canon import digest

    return digest([[f.path.name, f.sha256, f.derived_by.value, f.derived_engine_digest or ""]
                   for f in sorted(filings, key=lambda x: x.path.name)])
