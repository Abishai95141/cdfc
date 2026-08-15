"""P12 — the settling experiment. **THIS PACKAGE IS OFFLINE ONLY.**

Nothing here is reachable from a verdict. `cdfc.experiment.client` is the only module in the
package that may import a model client, and it is imported by `cdfc.experiment.run` and by
nothing else — `tests/negative/test_nc_model.py::test_nc__M13a_qualify_import_closure_has_no_model_client`
asserts the qualification path's import closure does not reach it, and its positive control
asserts that `run.py` *may*, because a guard that bans the wrong thing is not a guard.

**What this package is for.** P12 produces one number — *of `N` model-proposed regulatory checks,
`k` survived a five-gate admission test specified before the model ran* — and the epistemic content
of the phase is not the number but the ordering: the criterion was written, hashed and committed
**before** the first API call. Everything here exists to make that ordering a property of the
repository rather than a claim in a document.

**The seam is `experiments/E6/DECISION.md`.** `ci/barrier5.sh` fails the build if
`src/cdfc/model/propose.py` exists without it. A phase cannot gate itself, so the phase that runs
the model and the phase that builds on the result are two phases, and the file between them is the
only thing they share.
"""

from __future__ import annotations

from typing import Final

# The assertion this package makes about itself, quoted by `docs/measurements/P12-entry.md` and
# by the negative controls. It is a string rather than a comment because a test reads it.
OFFLINE_ONLY: Final[str] = (
    "cdfc.experiment is OFFLINE ONLY. No module in this package is reachable from any verdict "
    "root, and only cdfc.experiment.client may import a model client."
)

# The verdict roots this package must never appear in. Duplicated from nothing: P13-B0 will own
# the canonical list, and until it exists this is the set the P12 controls assert against.
VERDICT_ROOTS: Final[tuple[str, ...]] = (
    "cdfc.evaluate", "cdfc.verdict", "cdfc.probes", "cdfc.selfcheck", "cdfc.attest",
    "cdfc.qualify", "cdfc.surface",
)
