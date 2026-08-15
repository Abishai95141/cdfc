"""P12-B1 — the lock. **Append-only, ordered, and never `VERIFIED` by default.**

The experiment's whole epistemic content is an ordering: the criterion was written, hashed and
committed *before* the model ran. Every refusal here closes one way that ordering could be faked,
and the admission-side control is as load-bearing as the refusals — a lock that refused everything
would pass every negative test and forbid the experiment.
"""

from __future__ import annotations

import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from cdfc.experiment import prereg  # noqa: E402
from cdfc.experiment.prereg import (  # noqa: E402
    APPENDABLE,
    LockIsAppendOnly,
    PoolNotYetFixed,
    PreregistrationMismatch,
    ancestry_state,
    h0_of,
    lock_summary,
)

PREREG = REPO / "experiments" / "E6" / "PREREGISTRATION.md"
LOCK = REPO / "experiments" / "E6" / "preregistration.lock.json"


def _locked(tmp_path: Path) -> tuple[Path, Path]:
    """A copy of the committed pre-registration, locked inside `tmp_path`.

    **The real `experiments/E6/` is never written to.** `lock()` and `append()` both write, and a
    test that wrote there would clobber the committed lock — which is the one artifact in this
    build that cannot be regenerated, because `h0` may never move.
    """
    doc = tmp_path / "PREREGISTRATION.md"
    doc.write_text(PREREG.read_text(encoding="utf-8"), encoding="utf-8")
    lock_path = tmp_path / "preregistration.lock.json"
    prereg.lock(doc, lock_path, committed_at="2026-08-15")
    return doc, lock_path


def test_lock__h0_cannot_move(tmp_path: Path) -> None:
    """NC-M02. The criterion edited after the result is the defect the whole lock exists for.

    Re-locking an unchanged document is idempotent and returns the same `h0` — otherwise the check
    would be a check on whether anyone ran `lock()` twice. Re-locking a document that moved by a
    single trailing byte raises, because `h0` is over the **bytes**: whitespace is part of the
    criterion, and a criterion that can be reformatted can be reformatted into a different one.
    """
    doc, lock_path = _locked(tmp_path)
    first = json.loads(lock_path.read_text(encoding="utf-8"))
    assert first["h0"] == h0_of(doc)
    assert prereg.lock(doc, lock_path, committed_at="2026-08-15").h0 == first["h0"]

    doc.write_text(doc.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(PreregistrationMismatch) as e:
        prereg.lock(doc, lock_path, committed_at="2026-08-15")
    assert "h0 CANNOT MOVE" in str(e.value)
    assert "never discovered by finding the old one could not be met" in str(e.value), (
        "the refusal must say what a legitimate revision looks like, or the only reading left is "
        "that the threshold is unrevisable — and that is the reading people route around"
    )
    assert json.loads(lock_path.read_text(encoding="utf-8")) == first, (
        "the lock changed under a refused re-lock"
    )


def test_append__removing_a_field_raises(tmp_path: Path) -> None:
    """The lock GROWS; it does not move. Blanking `h0` is how a removal is expressible here.

    A field that can be rewritten is a field that will be rewritten on the day the result is
    unwelcome — and the empty string is the rewrite that reads, in a JSON file, as *there was never
    a value here*.
    """
    _doc, lock_path = _locked(tmp_path)
    before = lock_path.read_bytes()

    with pytest.raises(LockIsAppendOnly) as e:
        prereg.append(lock_path, h0="")
    assert "APPEND-ONLY" in str(e.value)

    with pytest.raises(LockIsAppendOnly):
        prereg.append(lock_path, committed_at="2026-08-16")

    assert lock_path.read_bytes() == before, "a refused append still wrote"


def test_append__draw_hash_before_the_pool_hashes_raises(tmp_path: Path) -> None:
    """**NC-M34.** A draw over a pool that can still be re-curated is a draw over a curation.

    The chapter set, the normalisation and the disputed-region exclusion set are all ours. If they
    can move after the draw, `k of 20` measures *our reading of the instrument* and reports it as a
    property of the model — and those two results are indistinguishable in the published number,
    which is why this is enforced in code rather than described in the document.
    """
    _doc, lock_path = _locked(tmp_path)
    before = lock_path.read_bytes()

    with pytest.raises(PoolNotYetFixed) as e:
        prereg.append(lock_path, draw_sha256="d" * 64)
    msg = str(e.value)
    assert "textsource_sha256" in msg and "exclusion_rule_sha256" in msg, (
        "the refusal must name WHICH pool hashes are still absent"
    )
    assert "indistinguishable in the published number" in msg
    assert lock_path.read_bytes() == before, "the draw hash landed despite the refusal"

    # One of the two present is still not enough — the guard is over the whole prefix, not the
    # most recent field.
    prereg.append(lock_path, textsource_sha256="a" * 64)
    with pytest.raises(PoolNotYetFixed):
        prereg.append(lock_path, draw_sha256="d" * 64)


def test_append__a_correctly_ordered_pair_is_accepted(tmp_path: Path) -> None:
    """**THE ADMISSION-SIDE CONTROL. The lock is append-only, not frozen.**

    Without it every refusal above is satisfied by an `append()` that raises unconditionally: a
    reject-everything lock passes every negative test in this file and makes the experiment
    unrunnable. This is the test that says the intended sequence actually works — and that the
    prerequisites the run checks are still reported as incomplete, since two hashes remain.
    """
    _doc, lock_path = _locked(tmp_path)

    prereg.append(lock_path, textsource_sha256="a" * 64)
    prereg.append(lock_path, exclusion_rule_sha256="b" * 64)
    after = prereg.append(lock_path, draw_sha256="d" * 64)

    assert after["draw_sha256"] == "d" * 64
    assert json.loads(lock_path.read_text(encoding="utf-8"))["draw_sha256"] == "d" * 64, (
        "the accepted append did not reach the file"
    )

    ready, missing = after.has_run_prerequisites()
    assert ready is False and missing == ("strata_sha256", "baselines_sha256"), (
        "a partial lock must report itself partial; the run refuses on exactly this tuple"
    )

    # Re-appending the SAME value is not a change, so it is not a violation — the rule is
    # append-only, not write-once-per-process.
    assert prereg.append(lock_path, draw_sha256="d" * 64)["draw_sha256"] == "d" * 64

    final = prereg.append(lock_path, strata_sha256="s" * 64, baselines_sha256="c" * 64)
    assert final.has_run_prerequisites() == (True, ())
    assert set(APPENDABLE) <= set(final.fields)


def test_ancestry__is_never_verified_by_default(tmp_path: Path) -> None:
    """**A check that cannot run has not passed.**

    `UNVERIFIABLE` and `VIOLATED` are kept apart because their remedies differ: a violation is a
    finding about the experiment, an unverifiable ancestry is a finding about the *environment* — a
    tarball with no `.git`, a shallow clone. Reporting the second as the first is exactly the
    collapse this project is named for, and defaulting to `VERIFIED` is how it happens.
    """
    assert ancestry_state(tmp_path).startswith("UNVERIFIABLE")
    assert ancestry_state(tmp_path) != "VERIFIED"

    # And on the real tree, where git history DOES exist: still unverifiable, because no model call
    # has been made and there is therefore nothing for the lock to precede.
    on_repo = ancestry_state(REPO)
    assert on_repo.startswith("UNVERIFIABLE"), on_repo
    assert "no runlog" in on_repo, (
        "the state must say WHICH precondition is absent; `UNVERIFIABLE` with no cause is a shrug"
    )

    # Not vacuous: the function can say VERIFIED, so the assertions above are about behaviour and
    # not about a branch that was deleted.
    source = Path(prereg.__file__).read_text(encoding="utf-8")
    assert '"VERIFIED"' in source and "VIOLATED" in source


def test_lock_summary__carries_the_command_that_recomputes_the_hash() -> None:
    """DoD line J1. **A hash a reviewer can recompute is evidence; a hash pasted into a description
    is a claim.**

    So the command is not merely present — it is RUN here, against the committed document, and its
    output must be the `h0` the lock records. A `recompute` string that names the wrong file, or the
    wrong algorithm, would read exactly as convincingly and reproduce nothing.
    """
    summary = lock_summary(LOCK)
    assert summary["h0"] == h0_of(PREREG)
    assert summary["run_may_proceed"] is False
    assert summary["fields_missing"] == list(APPENDABLE), (
        "on today's tree no artefact hash is in the lock — there is no statutory instrument, so "
        "there is no pool and no draw. The summary must say so rather than report readiness."
    )

    command = summary["recompute"]
    assert "PREREGISTRATION.md" in command

    if shutil.which(shlex.split(command)[0]) is not None:
        out = subprocess.run(
            shlex.split(command), cwd=REPO, capture_output=True, text=True, check=True,
        )
        assert out.stdout.split()[0] == summary["h0"], (
            f"the published recompute command produced {out.stdout.split()[0]!r}, not the h0 the "
            "lock records. The command is the evidence; a command that does not reproduce the "
            "hash is a longer way of asserting it."
        )
    else:  # pragma: no cover - shasum is present on every machine this repo is built on
        assert hashlib.sha256(PREREG.read_bytes()).hexdigest() == summary["h0"]
