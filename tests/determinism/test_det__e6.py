"""P12 — the draw and the power tables are byte-identical across environments.

Both artifacts are things a reader is invited to **recompute**. The draw is a sha256-keyed sort
precisely so that anyone with a hash function can re-derive it in any language, and the power tables
are exact rational arithmetic so that no figure depends on a rounding mode. Neither claim survives
if the bytes move with the machine's timezone, its hash seed, its locale or the directory the
process happens to be started in.

**The pattern is `tools/measure/p11_byte_identity.py`'s**: one subprocess per environment, four
variations that one machine can actually make, and the real bytes compared rather than a summary of
them. The variations are not decorative — each is a published source of non-determinism in Python:
the clock's zone, the hash seed that orders sets and dicts, the locale that orders strings, and the
working directory that resolves relative paths.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"

# `(label, env)`. Identical in spirit to P11's table, so a difference found here is comparable to a
# difference found there rather than to a different experiment.
ENVIRONMENTS: tuple[tuple[str, dict[str, str]], ...] = (
    ("baseline", {"TZ": "UTC", "PYTHONHASHSEED": "0", "LC_ALL": "C"}),
    ("antipodal clock", {"TZ": "Pacific/Kiritimati", "PYTHONHASHSEED": "0", "LC_ALL": "C"}),
    ("different hash seed", {"TZ": "UTC", "PYTHONHASHSEED": "1", "LC_ALL": "C"}),
    ("different locale", {"TZ": "UTC", "PYTHONHASHSEED": "0", "LC_ALL": "en_IN.UTF-8"}),
)

DRAW_SCRIPT = """
import sys
sys.path.insert(0, {src!r})
from cdfc.experiment.draw import Obligation, Pool, TableOracle, draw

N = 60
obligations = tuple(
    Obligation(
        ordinal=i, reg_no=(i // 4) + 1, sub_clause=(str((i % 4) + 1),),
        quote="A fund management entity shall do the thing numbered %d." % i,
        char_span=(i * 100, i * 100 + 55), source_sha256="a" * 64,
    )
    for i in range(N)
)
pool = Pool(
    obligations=obligations, excluded=(), source_sha256="a" * 64,
    chapters=("Chapter III — Registration and Obligations of Fund Management Entities",),
)
oracle = TableOracle(
    assignment={{i: ("A" if i % 3 else "B") for i in range(N)}},
    assigner={{i: "R. Assigner" for i in range(N)}},
)
sys.stdout.buffer.write(draw(pool, seed=20260815, strata=oracle).as_json())
"""

POWER_SCRIPT = """
import sys
sys.path.insert(0, {src!r})
from cdfc.experiment.power import power_table
sys.stdout.buffer.write(power_table().as_markdown().encode("utf-8"))
"""


def _bytes_under(script: str, env: dict[str, str], cwd: Path) -> bytes:
    proc = subprocess.run(
        [sys.executable, "-c", script.format(src=str(SRC))],
        cwd=cwd, capture_output=True, check=False,
        env={**os.environ, **env, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")[-2000:]
    return proc.stdout


def _assert_identical(script: str, tmp_path: Path, what: str) -> bytes:
    baseline = _bytes_under(script, dict(ENVIRONMENTS[0][1]), REPO)
    assert baseline, f"{what} produced no bytes at all — this test would compare nothing"

    for label, env in ENVIRONMENTS:
        got = _bytes_under(script, env, REPO)
        assert got == baseline, f"{what} changed under `{label}` ({env})"

    # The fourth variation, and the one the environment dict cannot express: a different working
    # directory. It catches dependence on a relative path, which is the form of non-determinism a
    # fresh clone at the same commit is meant to find and a same-directory re-run never will.
    elsewhere = _bytes_under(script, dict(ENVIRONMENTS[0][1]), tmp_path)
    assert elsewhere == baseline, f"{what} changed when the process was started elsewhere"
    return baseline


def test_det__draw_bytes_identical(tmp_path: Path) -> None:
    """`draw.as_json()` is the same bytes everywhere, or the seed does not pin the draw.

    The permutation is `sorted(range(n), key=sha256(pool ‖ seed ‖ index))` rather than
    `random.Random(seed).shuffle`, and this is the test that cashes the argument for it: a keyed
    sort has no interpreter state, so the order cannot depend on anything the environment supplies.
    A draw that moved with `PYTHONHASHSEED` would still look like a draw — a reader re-deriving it
    would simply get different obligations and no way to tell which run was the real one.
    """
    payload = _assert_identical(DRAW_SCRIPT, tmp_path, "draw.as_json()")

    import json

    obj = json.loads(payload)
    assert len(obj["stratum_a"]) == 20, (
        "the draw did not run to |A| = 20; the fixture is not a draw"
    )
    assert len(obj["drawn"]) == len(obj["stratum_a"]) + len(obj["stratum_b_all"]), (
        "the drawn set is not its two strata — NC-M03, a truncated denominator"
    )
    assert len(obj["stratum_b_generated"]) <= 10


def test_det__power_table_bytes_identical(tmp_path: Path) -> None:
    """The pre-registration's §6 is the same bytes everywhere.

    It is rendered into a document whose sha256 **is** `h0`, so a figure that moved with the
    locale would move `h0` — and `h0` may never move. A byte difference here would not present as a
    rounding disagreement; it would present as a pre-registration mismatch, i.e. as the accusation
    that somebody edited the criterion.
    """
    payload = _assert_identical(POWER_SCRIPT, tmp_path, "power_table().as_markdown()")

    text = payload.decode("utf-8")
    separators = [line for line in text.splitlines() if line.startswith("|---")]
    assert len(separators) == 4, f"{len(separators)} tables were rendered, not four"
    assert "| 0.30 | 0.416 | 0.035 |" in text, (
        "the corrected P(X <= 2 | n = 20, p = 0.30) is not in the rendered table"
    )

    # And the rendered bytes are what the committed document carries — so this test and the
    # round-trip contract test are pinned to the same artifact rather than to two of them.
    doc = (REPO / "experiments" / "E6" / "PREREGISTRATION.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("| 0."):
            assert line in doc, f"a generated row is absent from the pre-registration: {line}"
