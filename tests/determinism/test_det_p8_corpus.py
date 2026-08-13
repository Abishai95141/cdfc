"""P8 — the clean corpus and the Wilson strings reproduce byte-identically.

Engine drift is a **failing test** rather than a silently different corpus, and the 6-dp interval
strings are what P11's attestation re-derives.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

WILSON_PROBE = """
import sys
sys.path.insert(0, "src")
from cdfc.qualify.wilson import wilson, n_for_upper_bound
from decimal import Decimal
print("|".join(str(x) for k, n in ((0,4),(2,96),(0,340),(1,7)) for x in wilson(k,n)),
      n_for_upper_bound(Decimal("0.02")), n_for_upper_bound(Decimal("0.10")))
"""

CORPUS_PROBE = """
import sys, tempfile, pathlib
sys.path.insert(0, "src")
from cdfc.qualify.corpus.template_computed import DerivedBy, synthesise, corpus_digest
FME = pathlib.Path("fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
with tempfile.TemporaryDirectory() as t:
    made = synthesise(FME, pathlib.Path(t), seed=99, n=2, derived_by=DerivedBy.FOREIGN_ENGINE)
    print(corpus_digest(made), made[0].sha256, len(made[0].computed_cells))
"""

ENVS = (
    {"TZ": "UTC", "LC_ALL": "C", "PYTHONHASHSEED": "0"},
    {"TZ": "Pacific/Kiritimati", "LC_ALL": "tr_TR.UTF-8", "PYTHONHASHSEED": "12345"},
    {"TZ": "America/Adak", "LC_ALL": "en_US.UTF-8", "PYTHONHASHSEED": "99991"},
)


def _run(probe: str) -> set[str]:
    out = set()
    for extra in ENVS:
        r = subprocess.run([sys.executable, "-c", probe], cwd=REPO, capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), **extra})
        assert r.returncode == 0, r.stderr
        out.add(r.stdout.strip())
    return out


def test_det__wilson_is_byte_identical():
    """The 6-dp strings are identical across TZ, locale and hash seed. **Guards G-REPRO**: this
    value lands in a byte-identical attestation, and a `float` bound would make two machines
    produce two of them."""
    assert len(_run(WILSON_PROBE)) == 1


def test_det__foreign_engine_corpus_is_pinned():
    """The corpus is content-addressed and reproduces from `{seed, template, engine}` alone.

    **The corpus is not committed** — 40 filings of this workbook are 146 MB — so the digest in
    `fixtures/corpus_manifest.json` is what makes it reproducible rather than merely regenerable.
    """
    outs = _run(CORPUS_PROBE)
    assert len(outs) == 1, f"the corpus moved with the environment: {outs}"
    digest, first, computed = next(iter(outs)).split()
    assert len(digest) == 64 and len(first) == 64
    assert int(computed) == 505, "every FME formula cell must carry an engine-computed value"


def test_det__the_committed_manifest_matches_a_regeneration():
    """A stale manifest is a corpus nobody regenerated. This asserts the SHAPE and the pinned
    engine, not the 40 digests — regenerating those costs a minute of LibreOffice and belongs to
    `make ffr`, which the phase-closing ritual runs."""
    import json

    sys.path.insert(0, str(REPO / "src"))
    from cdfc.qualify.corpus.template_computed import engine_digest
    doc = json.loads((REPO / "fixtures/corpus_manifest.json").read_text(encoding="utf-8"))
    assert doc["derived_by"] == "FOREIGN_ENGINE"
    assert doc["n"] == len(doc["filings_sha256"]) == 40
    assert doc["n_non_synthetic"] == 0
    assert doc["derived_engine_digest"] == engine_digest(), (
        "the pinned engine moved; regenerate with `make ffr` and republish the rate, because a "
        "rate drawn from one engine is not a rate drawn from another"
    )
    assert not any(m.startswith("cdfc.calc") for m in doc["generator_import_closure"])
