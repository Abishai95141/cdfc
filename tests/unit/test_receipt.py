"""L0 receipt — the hash is over the exact bytes, and a refusal leaves no trace."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.ingest.receipt import RefusedAtReceipt, blob_path_for, receive  # noqa: E402

FME = REPO / "fixtures" / "prescribed" / (
    "Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx"
)
AT = "2026-08-11T09:00:00Z"


def test_receive__hash_is_over_exact_bytes(tmp_path: Path) -> None:
    """No normalisation, no re-encoding. A trailing byte changes the digest."""
    data = FME.read_bytes()
    r1 = receive(data, media_type="application/vnd.ms-excel", cap_bytes=10_000_000,
                 blob_root=tmp_path, received_at=AT)
    assert r1.filing_sha256 == hashlib.sha256(data).hexdigest()
    assert r1.filing_sha256.startswith("7d9a1960")
    assert r1.n_bytes == 3_663_391


def test_receive__over_cap_raises_413_and_writes_nothing(tmp_path: Path) -> None:
    with pytest.raises(RefusedAtReceipt) as ei:
        receive(FME.read_bytes(), media_type="x", cap_bytes=1000, blob_root=tmp_path,
                received_at=AT)
    assert ei.value.http_status == 413
    assert not list(tmp_path.rglob("*")), "a refused receipt wrote a blob"


def test_receive__non_zip_raises_415(tmp_path: Path) -> None:
    with pytest.raises(RefusedAtReceipt) as ei:
        receive(b"not a zip at all", media_type="x", cap_bytes=10_000, blob_root=tmp_path,
                received_at=AT)
    assert ei.value.http_status == 415
    assert not list(tmp_path.rglob("*"))


def test_receive__rejects_a_non_rfc3339_timestamp(tmp_path: Path) -> None:
    """`received_at` is an argument, and an argument can be wrong."""
    with pytest.raises(RefusedAtReceipt):
        receive(FME.read_bytes(), media_type="x", cap_bytes=10_000_000, blob_root=tmp_path,
                received_at="11 Aug 2026")


def test_receive__blob_is_written_read_only(tmp_path: Path) -> None:
    r = receive(FME.read_bytes(), media_type="x", cap_bytes=10_000_000, blob_root=tmp_path,
                received_at=AT)
    assert r.blob_path.exists()
    assert (r.blob_path.stat().st_mode & 0o222) == 0, "the blob is writable"
    assert r.blob_path == blob_path_for(r.filing_sha256, tmp_path)


def test_receive__part_digests_cover_every_entry(tmp_path: Path) -> None:
    """A re-derivation must be able to say WHICH sheet changed; a part map makes that a
    lookup rather than a diff."""
    import zipfile

    r = receive(FME.read_bytes(), media_type="x", cap_bytes=10_000_000, blob_root=tmp_path,
                received_at=AT)
    with zipfile.ZipFile(FME) as z:
        entries = {i.filename for i in z.infolist() if not i.is_dir()}
    assert set(r.part_sha256) == entries
    assert len(r.part_sha256) == 42, f"expected 42 entries, got {len(r.part_sha256)}"
    assert "xl/worksheets/sheet10.xml" in r.part_sha256


def test_receive__is_idempotent_and_never_rewrites_a_blob(tmp_path: Path) -> None:
    data = FME.read_bytes()
    r1 = receive(data, media_type="x", cap_bytes=10_000_000, blob_root=tmp_path, received_at=AT)
    mtime1 = r1.blob_path.stat().st_mtime_ns
    r2 = receive(data, media_type="x", cap_bytes=10_000_000, blob_root=tmp_path, received_at=AT)
    assert r1.filing_sha256 == r2.filing_sha256
    assert r2.blob_path.stat().st_mtime_ns == mtime1, "an existing blob was rewritten"
