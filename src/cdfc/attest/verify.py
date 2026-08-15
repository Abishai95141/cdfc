"""P11-B2 — `verify`. **The programme's acceptance test, as a command.**

*If it does not reproduce, it does not ship.*

## The two facts, and why they must never merge

A third party does **not** have the filer's private key, so `verify` proves two different things
and reports them separately:

| claim | how | reported as |
|---|---|---|
| the **payload** re-derives byte-identically | re-run the pipeline from the manifest's pins and compare | `reproduced` with **named diffs** |
| the **signature** is valid over that payload | Ed25519 against the public key carried in the envelope | `signature_valid: true / false / null` |

**`verify` NEVER RE-SIGNS.** A tool that re-signed to compare signatures would report a mismatch
whenever the key differed and a match whenever it did not — and neither answer is about the report.
`test_v__verify_never_calls_sign` asserts it by AST over this module, because a comment saying so
is not the same as it being so.

**`signature_valid: None` is not `False`.** *We checked and it does not match* and *there is nothing
here to check against* are different facts about the world, and reporting the first for the second
is the collapse this project is named for.

## What it re-derives, and the one pin that is weaker than it looks

The pipeline is re-run against the manifest's **eight** pins — `template_sha256`, `filing_sha256`,
`registry_root`, `register_snapshot_sha256`, `code_git_sha`, `evaluator_version`,
`fault_model_version`, `tool_versions` — plus the two run-level **inputs** the probe and attestation
layers added: `probe_seed` and `timeVerified`. Both are recorded, never read at run time.

**`libreoffice` is deliberately absent from that list because it is not on the verdict path**, and
`test_no_libreoffice_online` asserts it.

**`code_git_sha` pins the COMMIT and not the working tree**, and that is a real gap rather than a
technicality: a dirty tree re-derives under a `code_git_sha` that does not describe the code that
ran. `verify` therefore reports `tree_clean` alongside the two claims. A `reproduced: true` from a
dirty tree is a weaker statement than the same value from a clean one, and the caller is told which
it has rather than being left to assume.

## Diffs are NAMED, never a boolean

`(artifact, byte_offset, expected, actual)`. A reproduction check that answers only *no* tells the
reader that something moved and nothing about what, and the first thing anyone does with that answer
is stop believing it.
"""

from __future__ import annotations

import base64
import json
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from cdfc.attest import dsse
from cdfc.attest.statement import MANIFEST_PINS, MANIFEST_RUN_INPUTS

# How much of a differing region to quote. Enough to see the change, short enough to read.
WINDOW: Final[int] = 48


class BlobMissing(FileNotFoundError):
    """A blob the manifest names is not in the store. **Never substituted for a similar one.**"""


@dataclass(frozen=True, slots=True)
class Diff:
    artifact: str
    byte_offset: int
    expected: str
    actual: str

    def render(self) -> str:
        return (
            f"{self.artifact} @ byte {self.byte_offset}\n"
            f"      expected  {self.expected!r}\n"
            f"      actual    {self.actual!r}"
        )


@dataclass(frozen=True, slots=True)
class VerifyResult:
    reproduced: bool
    diffs: tuple[Diff, ...]
    signature_valid: bool | None
    manifest_pins_checked: tuple[str, ...]
    tree_clean: bool = True
    detail: str = ""

    def as_row(self) -> dict[str, Any]:
        return {
            "reproduced": self.reproduced,
            "signature_valid": self.signature_valid,
            "manifest_pins_checked": list(self.manifest_pins_checked),
            "tree_clean": self.tree_clean,
            "diffs": [
                {"artifact": d.artifact, "byte_offset": d.byte_offset,
                 "expected": d.expected, "actual": d.actual}
                for d in self.diffs
            ],
            "detail": self.detail,
        }


@dataclass
class BlobStore:
    """`sha256 -> path`, built by scanning directories. **Content-addressed, never name-addressed.**

    A store keyed on filename would resolve `filing.xlsx` to whichever file currently has that
    name, which is exactly the substitution `verify` exists to detect.
    """

    roots: Sequence[Path]
    _index: dict[str, Path] = field(default_factory=dict, repr=False)

    def index(self) -> dict[str, Path]:
        if not self._index:
            import hashlib

            for root in self.roots:
                for p in sorted(Path(root).rglob("*")):
                    if p.is_file() and p.suffix in (".xlsx", ".xlsm"):
                        self._index[hashlib.sha256(p.read_bytes()).hexdigest()] = p
        return self._index

    def get(self, sha256: str) -> Path:
        path = self.index().get(sha256)
        if path is None:
            raise BlobMissing(
                f"no blob with digest {sha256[:16]}… in {[str(r) for r in self.roots]}. It is not "
                "resolved by name instead: a store keyed on filename returns whichever file "
                "currently has that name, which is the substitution verify exists to detect."
            )
        return path


def tree_is_clean(repo: Path) -> bool:
    """`code_git_sha` pins the commit; a dirty tree means it does not describe the code that ran."""
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=False
    )
    return out.returncode == 0 and not out.stdout.strip()


def first_diffs(name: str, expected: bytes, actual: bytes, limit: int = 3) -> tuple[Diff, ...]:
    """Named diffs at the byte level. Reports the first `limit` differing REGIONS, not bytes.

    Byte-by-byte would emit thousands of rows for one moved field and name none of them usefully;
    a region is what a reader can act on.
    """
    out: list[Diff] = []
    i, n = 0, max(len(expected), len(actual))
    while i < n and len(out) < limit:
        if i < len(expected) and i < len(actual) and expected[i] == actual[i]:
            i += 1
            continue
        out.append(
            Diff(
                artifact=name,
                byte_offset=i,
                expected=expected[i : i + WINDOW].decode("utf-8", "replace"),
                actual=actual[i : i + WINDOW].decode("utf-8", "replace"),
            )
        )
        i += WINDOW
    if not out and len(expected) != len(actual):
        out.append(
            Diff(
                artifact=name, byte_offset=min(len(expected), len(actual)),
                expected=f"<{len(expected)} bytes>", actual=f"<{len(actual)} bytes>",
            )
        )
    return tuple(out)


def envelope_of(artifact: Path) -> dict[str, Any]:
    return json.loads(artifact.read_text(encoding="utf-8"))


def payload_of(envelope: Mapping[str, Any]) -> bytes:
    return base64.b64decode(envelope["payload"])


def verify(artifact: Path, blobs: BlobStore, *, repo: Path | None = None) -> VerifyResult:
    """Re-derive the statement from the manifest's pins and compare it byte for byte.

    The signature is checked against the **stored** bytes and the re-derivation against the
    **re-run** bytes, and the two answers are returned separately. A caller that wants one number
    is asking a question this tool refuses to answer.
    """
    from cdfc.measure.p11_attest import statement_for
    from cdfc.measure.p10_run import run_filing

    repo = repo or Path(__file__).resolve().parents[3]
    envelope = envelope_of(artifact)

    # --- CLAIM 2 FIRST, and against the STORED bytes ---------------------------------------
    # Taken before anything is re-run, so a re-derivation failure cannot change the answer. The
    # signature is a fact about the file on disk.
    signature_valid = dsse.verify(envelope)

    stored = payload_of(envelope)
    obj = json.loads(stored)
    manifest = obj["predicate"]["manifest"]
    checked = tuple(p for p in (*MANIFEST_PINS, *MANIFEST_RUN_INPUTS) if p in manifest)
    missing = tuple(p for p in (*MANIFEST_PINS, *MANIFEST_RUN_INPUTS) if p not in manifest)
    if missing:
        return VerifyResult(
            reproduced=False, diffs=(), signature_valid=signature_valid,
            manifest_pins_checked=checked, tree_clean=tree_is_clean(repo),
            detail=(
                f"the manifest is missing {list(missing)}, so the pipeline cannot be pinned to it. "
                "A re-derivation against an incomplete manifest would be a re-run, not a check."
            ),
        )

    # **A MISSING BLOB IS A NAMED ANSWER, NOT A CRASH.** This is what a tampered filing looks
    # like from here: the attestation is about a document with a particular digest, and the store
    # does not contain it. Raising would make `cdfc verify` exit with a traceback, and a reader
    # would learn that the tool broke rather than that the artifact did.
    #
    # Resolved ONE AT A TIME so the result can name which one is missing. The first version wrapped
    # both in a single `try` and inferred the answer from the exception's text — and the text
    # truncates the digest to sixteen characters, so the substring test never matched and every
    # missing filing was reported as a missing template. A diagnosis inferred from a message is a
    # diagnosis about the message.
    missing_blob: tuple[str, str] | None = None
    filing = template = None
    for which in ("filing", "template"):
        try:
            resolved = blobs.get(manifest[f"{which}_sha256"])
        except BlobMissing:
            missing_blob = (which, manifest[f"{which}_sha256"])
            break
        if which == "filing":
            filing = resolved
        else:
            template = resolved
    if missing_blob is not None:
        which, digest = missing_blob
        return VerifyResult(
            reproduced=False,
            diffs=(
                Diff(
                    artifact=f"{which} blob",
                    byte_offset=0,
                    expected=f"sha256:{digest}",
                    actual="ABSENT from the blob store",
                ),
            ),
            signature_valid=signature_valid,
            manifest_pins_checked=checked,
            tree_clean=tree_is_clean(repo),
            detail=(
                f"the {which} this attestation is about is not in the store. Its digest is "
                f"{digest[:16]}…, and no file with that digest was found — so either the document "
                "changed after it was attested, or a different document was supplied under the "
                "same name. Both are the same fact from here: this is not the artifact that was "
                "checked."
            ),
        )

    # --- CLAIM 1: re-run, and rebuild the statement from the RECORDED inputs -----------------
    result = run_filing(filing)
    rebuilt = statement_for(
        result,
        filing=filing,
        template=template,
        # `timeVerified` is an INPUT read back from the manifest, never a clock read here. This is
        # the line that makes `expires` re-derive, and it is the whole reason `expires` is a
        # function of it.
        time_verified=manifest["timeVerified"],
        residue=obj["predicate"]["residue"],
        counter_evidence=obj["predicate"]["counterEvidence"],
    )
    actual = rebuilt.canonical()
    diffs = first_diffs("attestation payload", stored, actual)
    return VerifyResult(
        reproduced=not diffs,
        diffs=diffs,
        signature_valid=signature_valid,
        manifest_pins_checked=checked,
        tree_clean=tree_is_clean(repo),
        detail="" if not diffs else (
            f"{len(diffs)} differing region(s); the first is at byte {diffs[0].byte_offset}"
        ),
    )
