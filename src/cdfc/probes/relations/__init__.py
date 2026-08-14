"""The relation layer — L6.

**`ScopeKind` keeps its import path.** It was declared at `cdfc.probes.relations` from P5, when
`cdfc.verdict` first needed to read it, because *a field one document writes and another ignores
is not a repair* (arbitration C3). P9 turns the module into a package rather than moving the type:
`from cdfc.probes.relations import ScopeKind` means today what it meant at P5, and the readers in
`verdict/states.py`, `verdict/closure.py` and `evaluate/rollup.py` did not have to be touched to
add a registry beside it.
"""

from cdfc.probes.relations.scope import LEAVES_IN_SCOPE, SCOPE_KINDS, ScopeKind

__all__ = ["LEAVES_IN_SCOPE", "SCOPE_KINDS", "ScopeKind"]
