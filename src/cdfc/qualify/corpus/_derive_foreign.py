"""P8-B2 — the FOREIGN_ENGINE derivation. **This module imports nothing from `cdfc.calc`.**

That absence is not stylistic: `g4_ffr.independent()`'s second conjunct is
`generator_import_closure & evaluation_import_closure(cand) == frozenset()`, and the closure is
computed BY AST over THIS module. A dispatcher that imported both derivation paths would put
`cdfc.calc` in the closure of a corpus `cdfc.calc` never touched, and the independence claim would
be false in the direction that flatters us — which is F2 again, one level up.

The engine EXPORTS A VALUE TABLE and never re-serialises the workbook.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from cdfc.qualify.corpus._writer import formula_values

MODULE = "cdfc.qualify.corpus._derive_foreign"


class ForeignEngineUnavailable(RuntimeError):
    """The pinned engine cannot be run offline and deterministically.

    **Pre-decided branch:** `derived_by=FOREIGN_ENGINE` is then unavailable, the arithmetic classes
    have NO admissible corpus until the blind fill lands, and the funnel reports `NOT ADMITTED` for
    want of a corpus — a measurement, not a stall. What is NOT permitted is the previous behaviour:
    arithmetic predicates drawing a zero FFR from cells our own evaluator wrote.
    """


def value_table(soffice: Path, path: Path) -> dict[tuple[str, str], object]:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [str(soffice), "--headless", "--norestore", "--convert-to",
             "xlsx:Calc MS Excel 2007 XML", "--outdir", tmp, str(path)],
            capture_output=True, text=True, timeout=900,
        )
        produced = Path(tmp) / (path.stem + ".xlsx")
        if not produced.is_file():
            raise ForeignEngineUnavailable(
                f"the pinned engine produced nothing for {path.name}: {proc.stdout}\n{proc.stderr}"
            )
        return formula_values(produced)
