"""P7-B1 — `emit()` is byte-identical across environment. Its digest enters `qualified_against`."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PROBE = """
import sys
sys.path.insert(0, "src")
from pathlib import Path
from cdfc.qualify.template_instrument import emit
from cdfc.predicates.harvest import harvest
from cdfc.predicates.obligations import generate_template_obligations
p = Path("fixtures/prescribed/Reporting_Format_for_Fund_Management_Entities_02012026_20260102_0255.xlsx")
it = emit(p)
tbl = generate_template_obligations(harvest(p), it)
import hashlib
spans = hashlib.sha256(
    "".join(f"{k}:{o.span[0]}-{o.span[1]}" for k, o in sorted(tbl.rows.items())).encode()
).hexdigest()
print(it.sha256, spans, len(it.text), len(tbl))
"""

ENVS = (
    {"TZ": "UTC", "LC_ALL": "C", "PYTHONHASHSEED": "0"},
    {"TZ": "Pacific/Kiritimati", "LC_ALL": "tr_TR.UTF-8", "PYTHONHASHSEED": "12345"},
    {"TZ": "America/Adak", "LC_ALL": "en_US.UTF-8", "PYTHONHASHSEED": "99991"},
)


def test_det__template_instrument_reproduces():
    outs = set()
    for extra in ENVS:
        r = subprocess.run(
            [sys.executable, "-c", PROBE], cwd=REPO, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), **extra},
        )
        assert r.returncode == 0, r.stderr
        outs.add(r.stdout.strip())
    assert len(outs) == 1, (
        f"the instrument text or an obligation span moved with the environment: {outs}. "
        "Its digest enters qualified_against, so a predicate would change identity by being "
        "qualified on a different machine."
    )


def test_det__obligation_spans_reproduce_from_a_different_cwd(tmp_path):
    """The `cwd` half of the same property: the instrument is a function of the file's BYTES."""
    r = subprocess.run(
        [sys.executable, "-c", PROBE.replace('sys.path.insert(0, "src")',
                                             f'sys.path.insert(0, "{REPO}/src")')
                                    .replace('Path("fixtures', f'Path("{REPO}/fixtures')],
        cwd=tmp_path, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
    )
    assert r.returncode == 0, r.stderr
    here = subprocess.run([sys.executable, "-c", PROBE], cwd=REPO, capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home())})
    assert r.stdout.strip() == here.stdout.strip()
