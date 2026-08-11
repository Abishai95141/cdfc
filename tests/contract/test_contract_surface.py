"""The green-tick exemption must stay exactly one file."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def test_contract__green_tick_exemption_is_one_file() -> None:
    """Excluding a file from a gate is how gates get defeated. The exemption is the
    vocabulary's own definition site and nothing else."""
    src = (REPO / "ci" / "no-green-tick.sh").read_text()
    m = re.search(r"EXEMPT = \{([^}]*)\}", src)
    assert m, "the gate no longer declares an EXEMPT set"
    paths = [p.strip().strip('"').strip("'") for p in m.group(1).split(",") if p.strip()]
    assert paths == ["src/cdfc/surface/labels.py"], f"exemption list grew to {paths}"
