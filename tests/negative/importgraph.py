"""Re-export of the AST import-closure walker, which moved to `src/cdfc/importgraph.py` at P8.

It moved because `g4_ffr.independent()` computes an import closure at RUNTIME, and a shipped module
importing from `tests/` is a product that does not ship. **This file is a re-export and not a second
implementation** — the whole reason the walker is one function is that two would drift, and the one
that drifts is the one nobody is reading.
"""

from cdfc.importgraph import import_closure, reaches  # noqa: F401
