"""L0 receipt — a hash over the EXACT received bytes, and a refusal that leaves no trace.

Three properties this file exists to hold:

1. **The hash is over the bytes as received.** No normalisation, no re-encoding, no
   "cleanup". The moment a filing is re-serialised on the way in, the thing we hashed is
   not the thing the filer sent, and a re-derivation proves nothing about their document.
2. **A refusal creates NO run row.** An over-cap or non-zip submission is refused before
   anything is written. A half-created run is a run whose absence of findings means
   nothing.
3. **`received_at` is an ARGUMENT, never a clock read** (R3). A core module that reads a
   clock cannot be re-derived, and `ci/no-clock-in-core.sh` fails the build if one tries.

Per-part digests are not decoration: a re-derivation must be able to say WHICH sheet
changed, and a part map makes that a lookup rather than a diff.
"""

from __future__ import annotations

import hashlib
import os
import re
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
ZIP_MAGIC = b"PK\x03\x04"


class RefusedAtReceipt(Exception):
    """Refused before any run exists. NO RUN ROW IS CREATED."""

    def __init__(self, http_status: int, reason: str) -> None:
        super().__init__(f"{http_status}: {reason}")
        self.http_status = http_status
        self.reason = reason


@dataclass(frozen=True)
class Receipt:
    filing_sha256: str
    n_bytes: int
    media_type: str
    received_at: str
    blob_path: Path
    part_sha256: Mapping[str, str]

    def as_canonical_obj(self) -> dict[str, object]:
        """The hashable projection. Note `blob_path` is EXCLUDED — it is a local
        filesystem fact, not a property of the filing, and including it would make the
        digest machine-dependent."""
        return {
            "filing_sha256": self.filing_sha256,
            "n_bytes": self.n_bytes,
            "media_type": self.media_type,
            "received_at": self.received_at,
            "part_sha256": dict(self.part_sha256),
        }


def blob_path_for(digest_hex: str, blob_root: Path) -> Path:
    """blobs/sha256/<aa>/<remaining 62>."""
    return blob_root / "sha256" / digest_hex[:2] / digest_hex[2:]


def receive(
    data: bytes,
    *,
    media_type: str,
    cap_bytes: int,
    blob_root: Path,
    received_at: str,
) -> Receipt:
    if not RFC3339.match(received_at):
        raise RefusedAtReceipt(400, f"received_at is not RFC 3339: {received_at!r}")

    if len(data) > cap_bytes:
        raise RefusedAtReceipt(413, f"{len(data)} bytes exceeds cap {cap_bytes}")

    if not data.startswith(ZIP_MAGIC):
        raise RefusedAtReceipt(415, "not a zip container (no PK\\x03\\x04 magic)")

    digest_hex = hashlib.sha256(data).hexdigest()

    # Per-part digests. We read the central directory only — no XML is parsed here, and
    # nothing is parsed at all before the container guard runs.
    parts: dict[str, str] = {}
    try:
        import io

        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                parts[info.filename] = hashlib.sha256(z.read(info.filename)).hexdigest()
    except zipfile.BadZipFile as e:
        raise RefusedAtReceipt(415, f"unreadable zip container: {e}") from e

    path = blob_path_for(digest_hex, blob_root)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".partial")
        tmp.write_bytes(data)
        os.chmod(tmp, 0o444)
        tmp.rename(path)
    # A blob is written once and never rewritten. If it exists its bytes are already ours
    # by construction — the path IS the digest.

    return Receipt(
        filing_sha256=digest_hex,
        n_bytes=len(data),
        media_type=media_type,
        received_at=received_at,
        blob_path=path,
        part_sha256=parts,
    )
