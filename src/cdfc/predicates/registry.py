"""The predicate registry — append-only, Merkle-rooted, and it refuses an unsigned batch.

**P0 through P6 this module refused UNCONDITIONALLY (R5), and that was not a stub**: the
qualification pipeline did not exist, so there was no record to check and a loader that accepted
anything would have been the vacuous pass at the registry boundary. Its catalogue entry was marked
PROVISIONAL for four phases *because a green entry with no information in it must not be counted as
evidence* — its admission-side twin was impossible.

**P7-B4 gives it the other branch, so NC-Q02 stops being provisional.** `load()` now has two
outcomes and both are reachable: a predicate with a qualification record loads, and one without
raises. **This is BARRIER 3 and it is a RUNTIME INVARIANT, not a lint.**

**R5 append-only.** Supersession is a NEW ROW, never an update. The old row stays byte-unchanged,
so a narrowing of `claims_fault_classes` after a campaign is visible as a supersession with a
reason rather than as a better score on the same id.

**R7 — admission requires a human.** The gate is mechanical; shipping a check that will be applied
to a regulated filing is not. `admit()` raises `UnsignedAdmissionError` without a detached
signature over the batch manifest. **If no signer exists the batch may still be admitted with
`signer: "UNSIGNED"` — and every surface renders the admitted set with the literal string
`UNSIGNED BATCH` beside its count.** Ships, visibly weaker; it does not ship silently.

**DOMAIN SEPARATION IS NOT DECORATION.** `leaf = sha256(0x00 ‖ h)`, `internal = sha256(0x01 ‖ l ‖ r)`.
Without the prefixes an internal node and a leaf are the same construction, so two different
admitted sets can be made to share a root and `registryRoot` stops identifying what ran (NC-Q38).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from cdfc.qualify.errors import UnqualifiedPredicateError, UnsignedAdmissionError

PHASE: Final[str] = "P7"
UNSIGNED: Final[str] = "UNSIGNED"
UNSIGNED_BADGE: Final[str] = "UNSIGNED BATCH"

LEAF_PREFIX: Final[bytes] = b"\x00"
INTERNAL_PREFIX: Final[bytes] = b"\x01"


class UnqualifiedPredicate(UnqualifiedPredicateError):
    """Kept as an alias: P0's name, P7's meaning. Nothing that caught the old one breaks."""


@dataclass(frozen=True, slots=True)
class AdmittedPredicate:
    predicate_id: str
    version: int
    code_sha256: str
    obligation_id: str
    state: str
    severity_tier: str
    admitted_at: str
    signer: str
    batch_manifest_sha256: str
    qualification: Any

    @property
    def signed(self) -> bool:
        return self.signer != UNSIGNED

    def badge(self) -> str:
        """What a surface must render beside this predicate's count."""
        return "" if self.signed else UNSIGNED_BADGE


class Registry:
    """An append-only store. In memory here; `migrations/001_qualification.sql` is its schema."""

    def __init__(self) -> None:
        self._rows: list[AdmittedPredicate] = []
        self._qualifications: dict[str, Any] = {}

    # -- admission -------------------------------------------------------------------------

    def admit(
        self,
        cand: Any,
        q: Any,
        *,
        signer: str,
        signature: bytes,
        batch_manifest_sha256: str,
        admitted_at: str,
        severity_tier: str = "ADVISORY",
        state: str = "PROVISIONAL",
    ) -> AdmittedPredicate:
        from cdfc.predicates.canonical import code_sha256

        if signer != UNSIGNED and not signature:
            raise UnsignedAdmissionError(
                f"{cand.id}: signer {signer!r} with no detached signature over the batch manifest "
                f"{batch_manifest_sha256[:8]}. R7 exists because the gate is mechanical and "
                "shipping a check that will be applied to a regulated filing is not."
            )
        if signer == UNSIGNED and signature:
            raise UnsignedAdmissionError(
                f"{cand.id}: a signature was supplied under the literal signer {UNSIGNED!r}. "
                "The unsigned path is a DECLARED weakening, not a place to hide a signature."
            )
        if q is None:
            raise UnqualifiedPredicate(
                f"{cand.id}: admitted with no qualification record. Barrier 3."
            )
        digest = code_sha256(cand)
        row = AdmittedPredicate(
            predicate_id=cand.id, version=cand.version, code_sha256=digest,
            obligation_id=cand.obligation_id, state=state, severity_tier=severity_tier,
            admitted_at=admitted_at, signer=signer,
            batch_manifest_sha256=batch_manifest_sha256, qualification=q,
        )
        # APPEND. A supersession is a new row; nothing is mutated.
        self._rows.append(row)
        self._qualifications[digest] = q
        return row

    def load(self, predicate_id: str, version: int) -> AdmittedPredicate:
        """BARRIER 3, as a runtime invariant. Two outcomes, both reachable."""
        for row in reversed(self._rows):  # the latest row wins; the older ones stay
            if row.predicate_id == predicate_id and row.version == version:
                if self._qualifications.get(row.code_sha256) is None:
                    raise UnqualifiedPredicate(
                        f"{predicate_id} v{version}: no qualification row. A predicate whose "
                        "error rate is unknown is not admitted — which is what makes the "
                        "settled-fraction claim true by construction rather than by discipline."
                    )
                return row
        raise UnqualifiedPredicate(
            f"{predicate_id} v{version} is not in the registry, so it carries no qualification "
            "record. It does not load."
        )

    def rows(self) -> tuple[AdmittedPredicate, ...]:
        return tuple(self._rows)

    def unsigned_count(self) -> int:
        return sum(1 for r in self._rows if not r.signed)

    def root(self) -> str:
        return registry_root([r.code_sha256 for r in self._rows])


def load_or_refuse(envelope: Mapping[str, object]) -> Any:
    """The P0 entry point, kept. It still refuses — an envelope carrying no qualification block
    is exactly what it always refused — and its admission-side twin now exists at `Registry.load`,
    which is what lets NC-Q02 stop being provisional."""
    if not envelope.get("qualification"):
        raise UnqualifiedPredicate(
            f"predicate {envelope.get('id', '<no id>')!r} not loaded: no qualification record. "
            "A predicate whose error rate is unknown is not admitted."
        )
    from cdfc.predicates.loader import load_predicate

    return load_predicate(envelope)


# --- the Merkle root ------------------------------------------------------------------------


def registry_root(code_sha256s: Sequence[str]) -> str:
    """Merkle over SORTED digests, with domain separation. An odd node is PROMOTED, not duplicated.

    Duplicating an odd node is the CVE-2012-2459 construction: two different leaf multisets produce
    one root. Promotion does not.
    """
    leaves = [hashlib.sha256(LEAF_PREFIX + bytes.fromhex(h)).digest() for h in sorted(code_sha256s)]
    if not leaves:
        # An empty registry has a root, and it is NOT the hash of nothing-in-particular: it is the
        # leaf prefix over the empty string, so "no predicates admitted" is a stateable fact.
        return hashlib.sha256(LEAF_PREFIX).hexdigest()
    level = leaves
    while len(level) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(hashlib.sha256(INTERNAL_PREFIX + level[i] + level[i + 1]).digest())
        if len(level) % 2:
            nxt.append(level[-1])  # PROMOTED, never duplicated
        level = nxt
    return level[0].hex()


def batch_manifest_sha256(code_sha256s: Sequence[str], *, campaign_id: str, qualified_at: str) -> str:
    """What a human signs. The digests, the campaign they were qualified against, and the date."""
    from cdfc.canon import digest

    return digest({
        "code_sha256": sorted(code_sha256s),
        "campaign_id": campaign_id,
        "qualified_at": qualified_at,
    })
