"""P11-B3 — the declared-lossy projections.

**Every projection carries a mandatory flag naming itself lossy and naming the URI of the
normative artifact — in the file, not in a README.** Any party reading only the projection sees a
smaller, cleaner report than the truth, and that is exactly why the file has to say so itself: the
reader who most needs the warning is the one who never saw the attestation.

Both projections join `report.html`, `attestation.json` and `run.jsonl` in `make determinism`'s
comparison set. **A lossy projection that is also non-deterministic is a second artifact a consumer
could diff and mis-read**, so every identifier in them is derived from content and nothing is
generated.
"""

from cdfc.attest.projections.oscal import NotRepresentable, project_oscal
from cdfc.attest.projections.rocrate import project_rocrate

__all__ = ["NotRepresentable", "project_oscal", "project_rocrate"]
