"""The container guard — a refusal that happens BEFORE any XML is parsed.

Order is the whole point. A guard that runs after the parser is not a guard: the zip bomb
has already been expanded and the entity has already been resolved by the time it speaks.
NC-P05a proves the order by spying on `cdfc.ingest.xmlsafe.fromstring` and asserting it
was never called on a tripped filing.

Every limit reports the LIMIT and the OBSERVED VALUE. A guard that says only "rejected"
cannot be triaged, and an operator who cannot triage a rejection will switch the guard
off.

A trip is a run-level `invalid.container_guard_tripped`, never a per-cell reason code and
never a FAIL. *A filing we could not safely open is not a filing that failed a check.*
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from cdfc.verdict.invalid import InvalidCause


@dataclass(frozen=True)
class GuardLimits:
    # Observed maxima across the nine prescribed workbooks are in the comments. The
    # headroom is deliberate and it is measured, not guessed: a limit tuned to the
    # observed maximum rejects the tenth workbook.
    max_entries: int = 1024  # observed max: 85
    max_entry_uncompressed_bytes: int = 16_777_216  # observed max: 3,551,232
    max_total_uncompressed_bytes: int = 67_108_864  # observed max: 4,495,901
    max_total_ratio: float = 100.0  # observed max: 6.2 — a ratio is not money, so a float is fine here
    required_parts: tuple[str, ...] = (
        "[Content_Types].xml",
        "xl/workbook.xml",
        "xl/_rels/workbook.xml.rels",
    )
    allowed_entry_suffixes: frozenset[str] = frozenset(
        {".xml", ".rels", ".bin", ".data", ".png", ".jpeg", ".jpg", ".emf", ".vml"}
    )


@dataclass(frozen=True)
class GuardReport:
    entries: int
    total_uncompressed: int
    total_compressed: int
    max_entry: int
    max_entry_name: str
    ratio: float
    missing_required: tuple[str, ...] = ()
    disallowed_suffixes: tuple[str, ...] = ()

    def as_canonical_obj(self) -> dict[str, object]:
        # `ratio` is excluded from the hashed projection: it is a float, and a float in a
        # hashed payload is a reproducibility bug. Its integer inputs are both here.
        return {
            "entries": self.entries,
            "total_uncompressed": self.total_uncompressed,
            "total_compressed": self.total_compressed,
            "max_entry": self.max_entry,
            "max_entry_name": self.max_entry_name,
            "missing_required": list(self.missing_required),
            "disallowed_suffixes": list(self.disallowed_suffixes),
        }


class GuardTrip(Exception):
    def __init__(self, detail: str, report: GuardReport | None = None) -> None:
        super().__init__(detail)
        self.cause = InvalidCause.CONTAINER_GUARD_TRIPPED
        self.detail = detail
        self.report = report


def guard(blob_path: Path, limits: GuardLimits = GuardLimits()) -> GuardReport:
    """Inspect the container from its central directory only. Parses no XML."""
    try:
        zf = zipfile.ZipFile(blob_path)
    except zipfile.BadZipFile as e:
        raise GuardTrip(f"not a readable zip container: {e}") from e

    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]

        n = len(infos)
        if n > limits.max_entries:
            raise GuardTrip(f"entry count {n} exceeds limit {limits.max_entries}")

        total_unc = 0
        total_cmp = 0
        max_entry = 0
        max_name = ""
        disallowed: list[str] = []
        for i in infos:
            total_unc += i.file_size
            total_cmp += i.compress_size
            if i.file_size > max_entry:
                max_entry, max_name = i.file_size, i.filename
            suffix = Path(i.filename).suffix.lower()
            if suffix and suffix not in limits.allowed_entry_suffixes:
                disallowed.append(i.filename)

            if i.file_size > limits.max_entry_uncompressed_bytes:
                raise GuardTrip(
                    f"entry {i.filename!r} uncompressed size {i.file_size} exceeds limit "
                    f"{limits.max_entry_uncompressed_bytes}"
                )

        if total_unc > limits.max_total_uncompressed_bytes:
            raise GuardTrip(
                f"total uncompressed size {total_unc} exceeds limit "
                f"{limits.max_total_uncompressed_bytes}"
            )

        ratio = (total_unc / total_cmp) if total_cmp else 0.0
        if ratio > limits.max_total_ratio:
            raise GuardTrip(
                f"compression ratio {ratio:.1f} exceeds limit {limits.max_total_ratio:.1f} "
                f"({total_unc} uncompressed / {total_cmp} compressed)"
            )

        names = {i.filename for i in infos}
        missing = tuple(p for p in limits.required_parts if p not in names)
        if missing:
            raise GuardTrip(f"missing required part(s) {list(missing)}; limit requires all of "
                            f"{list(limits.required_parts)}")

        if disallowed:
            raise GuardTrip(
                f"disallowed entry suffix in {disallowed[:3]}; allowed suffixes are "
                f"{sorted(limits.allowed_entry_suffixes)}"
            )

        return GuardReport(
            entries=n,
            total_uncompressed=total_unc,
            total_compressed=total_cmp,
            max_entry=max_entry,
            max_entry_name=max_name,
            ratio=ratio,
        )
