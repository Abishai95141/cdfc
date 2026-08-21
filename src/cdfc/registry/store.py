"""Content-addressed storage for uploads, and the run inputs that name them.

## The shape, and the prior art it is assembled from

This is a **Merkle-rooted content-addressed store** — the Git object model, applied to regulatory
uploads. Bytes go in, a `sha256` comes back, and the digest IS the identity. A filename is
metadata, never an address: two custodians who send the same trial balance under two names upload
one artefact, and a filer who renames a file has not created one.

Three properties follow, and each one is a thing this product already needed:

* **Idempotent.** Uploading the same bytes twice is one artefact. Re-running a filing after a
  re-upload is the same run.
* **Immutable.** There is no `update`. `D-A3-01`'s hazard — *"two runs over an identical filing,
  template and registry would return different coverage while sharing one run id"* — cannot arise,
  because nothing an artefact digest names can change under it.
* **Nameable in a manifest.** A run records the digests it used, so `cdfc verify` re-derives from
  the same inputs. This is what makes the cross-upload flow reproducible rather than merely
  possible.

## Why not a graph database, or a document store

`D-A3-01a` re-measured it: assembling 424,000 nodes costs 0.136 s and the scaling term is the
PARSE, not the fold. What was missing was never a query engine — it was somewhere to put the
bytes. A store that also indexed would be a cache nobody can prove correct, built before it is
needed; `D-A3-01a` sets its trigger at ~50 documents per ENTITY and it is not this module.

## What travels with an artefact, and what deliberately does not

`kind` is DECLARED by the uploader, not sniffed. A sniffer that guesses a trial balance from a
custodian feed has made a decision nobody recorded, and the two are checked against different
things. An upload whose kind is wrong is a user error with a name; an upload whose kind was
inferred wrongly is a silent one.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from cdfc.canon import canonical_json, digest as canon_digest

# Two hex characters of fan-out, as Git does it. A flat directory of 100,000 files is slow to list
# on every filesystem this will meet, and the fan-out costs nothing.
FANOUT: Final[int] = 2
MANIFEST_NAME: Final[str] = "MANIFEST.json"


class RegistryError(RuntimeError):
    """The registry cannot do what was asked. Never repaired, never defaulted."""


class DigestMismatch(RegistryError):
    """Stored bytes do not hash to the name they are stored under.

    This is the one failure that must never be recoverable: every run that named this digest was
    reading something else, and a coverage declaration over it is a statement about a document
    nobody can produce.
    """


class ArtefactKind(StrEnum):
    """What an upload IS. DECLARED by the uploader; never sniffed from the bytes.

    The kinds are what this system does different things with, not a taxonomy of file formats:
    a rules corpus is executed, a template induces a field surface, a source is observed for
    evidence, a filing is checked.
    """

    RULES = "rules"            # a regulator's published validation rules
    TEMPLATE = "template"      # a blank return; induces the field surface
    SOURCE = "source"          # a custodian feed, trial balance, cap table, valuation pack
    FILING = "filing"          # a completed return, to be checked
    INSTRUMENT = "instrument"  # a statute, circular or other prose rulebook


@dataclass(frozen=True, slots=True)
class Artefact:
    """One uploaded thing. `digest` is the identity; everything else is metadata."""

    digest: str
    kind: ArtefactKind
    size: int
    filename: str          # as uploaded. NOT an address, and two artefacts may share one.
    media_type: str

    def as_canonical_obj(self) -> dict[str, object]:
        return {
            "digest": self.digest, "kind": self.kind.value, "size": self.size,
            "filename": self.filename, "media_type": self.media_type,
        }


@dataclass(frozen=True, slots=True)
class RunInputs:
    """The artefacts one run used, and the Merkle root over them.

    **The root is over THIS RUN'S inputs, not over the whole registry.** A run that names three
    artefacts must produce the same root next year, on a registry that has since grown by
    thousands — a root over everything present would change under every unrelated upload, and the
    run id would stop being a function of its inputs.
    """

    digests: tuple[str, ...]
    merkle_root: str

    def __post_init__(self) -> None:
        if len(set(self.digests)) != len(self.digests):
            raise RegistryError(
                "a run names the same artefact twice; inputs are a SET and a duplicate means the "
                "caller believes it used two things when it used one."
            )
        if tuple(sorted(self.digests)) != self.digests:
            raise RegistryError(
                "run inputs are stored sorted, so that a run's identity does not depend on the "
                "order a user happened to upload in."
            )


def merkle_root_of(digests: Iterable[str]) -> str:
    """A root over a SET of artefact digests. Order-independent by construction.

    Sorted-then-folded rather than a pairwise tree: the set is small (a run names a handful of
    artefacts), and a sorted fold has no second-preimage subtlety to get wrong. It is computed
    through `cdfc.canon` so it obeys the same canonicalisation as every other digest here.
    """
    return canon_digest({"artefacts": sorted(set(digests))})


@dataclass(frozen=True, slots=True)
class Registry:
    """Content-addressed storage rooted at a directory. Immutable; no update, no delete."""

    root: Path

    # --- writing -------------------------------------------------------------------------

    def put(
        self, data: bytes, *, kind: ArtefactKind, filename: str, media_type: str = ""
    ) -> Artefact:
        """Store `data` under its own digest. Idempotent; re-putting identical bytes is a no-op.

        **Re-putting DIFFERENT bytes under a colliding digest is impossible and re-putting the
        same digest with different metadata does not overwrite.** The first upload's filename is
        kept, because a later caller renaming an artefact must not rewrite the provenance of runs
        that already named it.
        """
        if not filename.strip():
            raise RegistryError(
                "an artefact is stored under its digest, but it is RECORDED with the name a human "
                "uploaded it as; a nameless upload cannot be reported back to the person who sent "
                "it."
            )
        d = hashlib.sha256(data).hexdigest()
        blob = self._blob_path(d)
        art = Artefact(digest=d, kind=kind, size=len(data), filename=filename.strip(),
                       media_type=media_type)
        if blob.exists():
            existing = self._read_meta(d)
            if existing is not None:
                return existing
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_bytes(data)
        self._meta_path(d).write_bytes(canonical_json(art.as_canonical_obj()))
        return art

    def put_file(self, path: Path, *, kind: ArtefactKind, media_type: str = "") -> Artefact:
        return self.put(path.read_bytes(), kind=kind, filename=path.name, media_type=media_type)

    # --- reading -------------------------------------------------------------------------

    def has(self, digest: str) -> bool:
        return self._blob_path(digest).is_file()

    def get(self, digest: str) -> bytes:
        """The bytes stored under `digest`, RE-HASHED before they are returned.

        The re-hash is not paranoia about disks; it is the same rule `deserialise` applies to a
        pinned instrument. A store that hands back whatever is at a path has made its addresses
        into filenames.
        """
        p = self._blob_path(digest)
        if not p.is_file():
            raise RegistryError(
                f"artefact {digest[:12]}… is not in this registry. A run naming it cannot be "
                "re-derived, and that is a missing input rather than an empty one."
            )
        data = p.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            raise DigestMismatch(
                f"artefact {digest[:12]}… hashes to {actual[:12]}…. Every run that named this "
                "digest was reading different bytes, and any coverage declared over it describes "
                "a document nobody can produce."
            )
        return data

    def path(self, digest: str) -> Path:
        """The blob's own path on disk. **For readers that need a FILE, never for a writer.**

        `openpyxl` and every workbook reader want a path, and the registry holds bytes. Copying
        each blob to a temporary file to satisfy that would give the reader a path whose name is
        not the artefact's identity, and a refusal message naming `/tmp/tmp8f2a.xlsx` tells a
        filer nothing about what they uploaded. The store is immutable — there is no update and no
        delete — so handing out a read path cannot be used to change what a digest addresses.
        """
        p = self._blob_path(digest)
        if not p.is_file():
            raise RegistryError(f"{digest[:12]}… is not in this registry")
        return p

    def meta(self, digest: str) -> Artefact:
        m = self._read_meta(digest)
        if m is None:
            raise RegistryError(f"artefact {digest[:12]}… has no metadata record in this registry.")
        return m

    def list(self, kind: ArtefactKind | None = None) -> tuple[Artefact, ...]:
        out: list[Artefact] = []
        meta_root = self.root / "meta"
        if meta_root.is_dir():
            for p in sorted(meta_root.rglob("*.json")):
                a = self._parse_meta(p.read_bytes())
                if kind is None or a.kind is kind:
                    out.append(a)
        return tuple(sorted(out, key=lambda a: a.digest))

    def counts(self) -> dict[str, int]:
        by_kind: dict[str, int] = {}
        total = 0
        for a in self.list():
            by_kind[a.kind.value] = by_kind.get(a.kind.value, 0) + 1
            total += a.size
        return {"artefacts": sum(by_kind.values()), "bytes": total,
                **{f"kind_{k}": v for k, v in sorted(by_kind.items())}}

    # --- naming inputs -------------------------------------------------------------------

    def inputs(self, digests: Sequence[str]) -> RunInputs:
        """The `RunInputs` for a run, REFUSING any digest this registry cannot produce.

        A run may not name an artefact that is absent: the whole point of naming inputs is that
        `cdfc verify` can re-derive from them later, and a name that resolves to nothing is a
        promise the manifest cannot keep.
        """
        missing = sorted({d for d in digests if not self.has(d)})
        if missing:
            raise RegistryError(
                f"{len(missing)} named artefact(s) are not in this registry, e.g. "
                f"{[m[:12] + '…' for m in missing[:3]]}. A run cannot name an input it cannot "
                "re-read."
            )
        uniq = tuple(sorted(set(digests)))
        return RunInputs(digests=uniq, merkle_root=merkle_root_of(uniq))

    # --- paths ---------------------------------------------------------------------------

    def _blob_path(self, digest: str) -> Path:
        self._check(digest)
        return self.root / "blobs" / digest[:FANOUT] / digest

    def _meta_path(self, digest: str) -> Path:
        self._check(digest)
        p = self.root / "meta" / digest[:FANOUT] / f"{digest}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def _check(digest: str) -> None:
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise RegistryError(
                f"{digest!r} is not a sha256 hex digest. An address that is not a digest is a "
                "filename, and a filename is not an identity."
            )

    def _read_meta(self, digest: str) -> Artefact | None:
        p = self.root / "meta" / digest[:FANOUT] / f"{digest}.json"
        return self._parse_meta(p.read_bytes()) if p.is_file() else None

    @staticmethod
    def _parse_meta(raw: bytes) -> Artefact:
        o: Mapping[str, object] = json.loads(raw.decode("utf-8"))
        return Artefact(
            digest=str(o["digest"]), kind=ArtefactKind(str(o["kind"])), size=int(o["size"]),  # type: ignore[arg-type]
            filename=str(o["filename"]), media_type=str(o["media_type"]),
        )
