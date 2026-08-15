"""P11-B3 — the RO-Crate evidence crate. **Self-contained, or it fails.**

An evidence crate that references a blob it does not carry is a bibliography. The whole value of
the form is that a recipient can open it and find everything the claim rests on, so
`project_rocrate` **raises** when a referenced blob is absent rather than emitting an entry
pointing at nothing.

Like the OSCAL projection it declares its own lossiness in the file. Unlike it, an RO-Crate CAN
represent an `INVALID` run — a crate is a container for evidence rather than an assurance document,
and evidence that the instrument could not be demonstrated is still evidence. **The two projections
differ here on purpose**, and `docs/PROJECTION-LOSS.md` states the difference: the OSCAL refusal is
about a form whose vocabulary cannot say *we did not look*, not about `INVALID` being unmentionable.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from cdfc.attest.projections.oscal import LOSSY_NOTICE, NORMATIVE_URI

CONTEXT: Final[str] = "https://w3id.org/ro/crate/1.1/context"


class BlobNotCarried(ValueError):
    """The crate references a blob it does not contain. An evidence crate is self-contained."""


def project_rocrate(
    statement: Any, blobs: Mapping[str, Path], *, extra: Sequence[Mapping[str, Any]] = ()
) -> dict[str, Any]:
    """`blobs` maps the crate-relative name to a file that must EXIST."""
    pred = statement.as_predicate() if hasattr(statement, "as_predicate") else statement["predicate"]
    subjects = (
        statement.as_obj()["subject"] if hasattr(statement, "as_obj") else statement["subject"]
    )

    entities: list[dict[str, Any]] = []
    for name, path in sorted(blobs.items()):
        if not Path(path).is_file():
            raise BlobNotCarried(
                f"the crate references {name!r} at {path}, which does not exist. An evidence crate "
                "that names a blob it does not carry is a bibliography: the recipient cannot open "
                "the thing the claim rests on, which is the entire value of the form."
            )
        raw = Path(path).read_bytes()
        entities.append(
            {
                "@id": name,
                "@type": "File",
                "contentSize": str(len(raw)),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )

    return {
        "@context": CONTEXT,
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
                "about": {"@id": "./"},
            },
            {
                "@id": "./",
                "@type": "Dataset",
                "name": "Filing settlement evidence crate",
                # The lossy flag, IN THE FILE.
                "description": LOSSY_NOTICE,
                "identifier": pred["scope"]["runId"],
                "isBasedOn": {"@id": NORMATIVE_URI},
                "runState": pred["runState"],
                "subjectOf": [s["digest"]["sha256"] for s in subjects],
                "hasPart": [{"@id": e["@id"]} for e in entities],
            },
            *entities,
            *[dict(e) for e in extra],
        ],
    }
