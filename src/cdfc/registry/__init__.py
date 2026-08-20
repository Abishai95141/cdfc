"""The ARTEFACT REGISTRY — content-addressed storage for uploads.

`D-A3-01` closed by mandating this and `D-A3-01a` found it had never been built, which is what
actually blocks *"upload rules today, financial exports next week, ask for a filing the week
after"*. There was nowhere to put the first two uploads.

Nothing here stores a graph. The graph stays a re-derived projection, for the reason `D-A3-01`
gives and this does not disturb: an accumulating graph is state outside `run_id_for`'s digest.
"""

from cdfc.registry.store import (
    Artefact,
    ArtefactKind,
    DigestMismatch,
    Registry,
    RegistryError,
    RunInputs,
)

__all__ = [
    "Artefact", "ArtefactKind", "DigestMismatch", "Registry", "RegistryError", "RunInputs",
]
