"""P12-B1 — the lock. **Append-only, ordered, and checked by git ancestry rather than by mtime.**

This is the artifact the whole experiment's epistemic value rests on: not the number `k`, but the
fact that the criterion producing it was written, hashed and committed **before the model ran**.
Everything here exists to make that ordering a property of the repository.

## Four refusals, and each one closes a way the ordering could be faked

| Refusal | Raised by | What it stops |
|---|---|---|
| `h0` can never move | `lock()` | the criterion edited after the result — NC-M02 |
| a field cannot be changed or removed | `append()` | the same, one field at a time — NC-M02 |
| `draw_sha256` cannot arrive before the pool hashes | `append()` | a draw over a pool that can still be re-curated — **NC-M34** |
| every lock commit must be a git-ANCESTOR of the first runlog row | `assert_precedes_first_call()` | the whole file written after the run and back-dated — NC-M01 |

## Why git ancestry and not timestamps

A timestamp is a number the writer chooses. `git merge-base --is-ancestor` asks the object graph,
and the object graph is not writable after the fact without rewriting every descendant commit.
This is the same technique `test_corpus__brief_predates_any_filled_workbook` and
`g2_kill._assert_claim_predates` already use, and it is imported in spirit rather than re-argued.

**And an unverifiable ancestry is NOT a verified one.** `ancestry_state()` returns
`UNVERIFIABLE (no git history)` in a tree with no commits and never `VERIFIED` by default — the
rule `g2_kill.ancestry_state` established, applied here. A check that cannot run has not passed.

## What `PoolNotYetFixed` is actually protecting

Three things decide which obligations the model is asked about: the named chapters, the canonical
ordering, and the disputed-region exclusion set. The first two were always locked. **The third was
not** — and it is the one produced by an instrument we wrote, over a document we chose, under a
normalisation we defined. If the exclusion set can move after the draw, or the extractors can be
reconfigured until the pool looks tractable, then `k of 20` measures **our curation** and reports
it as a property of the model. Those two results are indistinguishable in the published number,
which is why the ordering is enforced in code rather than described in the pre-registration.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from cdfc.canon import canonical_json, sha256_hex

PREREGISTRATION_PATH: Final[Path] = Path("experiments/E6/PREREGISTRATION.md")
LOCK_PATH: Final[Path] = Path("experiments/E6/preregistration.lock.json")
RUNLOG_PATH: Final[Path] = Path("experiments/E6/runlog.jsonl")

# The lock's field set is CLOSED. An unknown key raises, because a lock that accepts anything is a
# note. `h0` and `committed_at` are written by `lock()`; the rest arrive by `append()`.
BASE_FIELDS: Final[tuple[str, ...]] = ("h0", "committed_at", "git_commit", "published_in")

# APPENDABLE FIELDS IN THEIR REQUIRED ORDER. This tuple *is* the ordering rule — `append()` reads
# it rather than carrying a hand-written sequence of `if` statements that could disagree with it.
APPENDABLE: Final[tuple[str, ...]] = (
    "textsource_sha256",        # the pinned instrument text
    "exclusion_rule_sha256",    # the disputed-region rule and both extractor configurations
    "draw_sha256",              # the realised draw — AFTER the two above (NC-M34)
    "strata_sha256",            # the human stratum assignment
    "baselines_sha256",         # B0 ∪ B1 ∪ B2, frozen BEFORE the first API call
)

ALL_FIELDS: Final[frozenset[str]] = frozenset(BASE_FIELDS) | frozenset(APPENDABLE)


class LockIsAppendOnly(RuntimeError):
    """A field was changed or removed. The lock grows; it does not move."""


class PoolNotYetFixed(RuntimeError):
    """`draw_sha256` arrived while a pool hash was still absent (NC-M34)."""


class PreregistrationMissing(FileNotFoundError):
    """There is no lock. **The experiment does not run without one.**"""


class PreregistrationMismatch(RuntimeError):
    """`h0` does not match the pre-registration on disk — the criterion moved."""


class UnknownLockField(KeyError):
    """A key outside the closed set."""


class OrderingNotEstablished(RuntimeError):
    """A commit that must precede another does not, by git ancestry."""


@dataclass(frozen=True, slots=True)
class Lock:
    """The lock's contents. Read-only; `append()` returns a new one."""

    fields: Mapping[str, str]

    def __getitem__(self, key: str) -> str:
        return self.fields[key]

    def get(self, key: str) -> str | None:
        return self.fields.get(key)

    @property
    def h0(self) -> str:
        return self.fields["h0"]

    def has_run_prerequisites(self) -> tuple[bool, tuple[str, ...]]:
        """`(ready, missing)` — every appendable field the run requires before its first call."""
        missing = tuple(f for f in APPENDABLE if f not in self.fields)
        return (not missing), missing

    def as_json(self) -> bytes:
        return canonical_json(dict(self.fields))


def h0_of(path: Path = PREREGISTRATION_PATH) -> str:
    """The pre-registration's content hash. **Over the bytes, so whitespace is part of it.**"""
    if not path.is_file():
        raise PreregistrationMissing(
            f"{path} does not exist. The criterion is the experiment; there is nothing to lock."
        )
    return sha256_hex(path.read_bytes())


def lock(
    path: Path = PREREGISTRATION_PATH,
    lock_path: Path = LOCK_PATH,
    *,
    committed_at: str,
    git_commit: str = "",
    published_in: str = "",
) -> Lock:
    """Write the lock with `h0`. **Refuses if a lock exists and `h0` differs.**

    `committed_at` is a PARAMETER and not a clock read. Nothing under `src/cdfc/` reads the wall
    clock (`ci/no-clock-in-core.sh`), and this module is not the place to start: a lock whose
    timestamp came from the machine that wrote it is a lock that can be re-written on a machine
    whose clock was set differently.

    **This function refuses to lock a criterion `decide()` cannot consume.** The check runs
    *before* anything is written, so a prose threshold does not reach the file and the experiment
    therefore does not run — F30's repair, in the only place it can be structural.
    """
    from cdfc.experiment.criterion import assert_machine_evaluable

    h0 = h0_of(path)
    assert_machine_evaluable(path)

    if lock_path.is_file():
        existing = _read(lock_path)
        if existing.h0 != h0:
            raise PreregistrationMismatch(
                f"the lock records h0 = {existing.h0[:16]}… and {path} now hashes to {h0[:16]}…. "
                "h0 CANNOT MOVE. If the criterion was genuinely wrong, that is a new experiment "
                "with a new pre-registration and a stated argument that the old threshold was "
                "wrong — dated, and never discovered by finding the old one could not be met."
            )
        return existing

    fields = {"h0": h0, "committed_at": committed_at}
    if git_commit:
        fields["git_commit"] = git_commit
    if published_in:
        fields["published_in"] = published_in
    out = Lock(fields=fields)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_bytes(out.as_json() + b"\n")
    return out


def append(lock_path: Path = LOCK_PATH, **artefact_hashes: str) -> Lock:
    """APPEND-ONLY, and ORDERED. Adding is permitted; changing or removing raises."""
    current = _read(lock_path)
    merged = dict(current.fields)

    for key, value in artefact_hashes.items():
        if key not in ALL_FIELDS:
            raise UnknownLockField(
                f"{key!r} is not a lock field. The set is closed: {sorted(ALL_FIELDS)}. A lock "
                "that accepts an unknown key is a lock that can be extended to say anything."
            )
        if key in merged and merged[key] != value:
            raise LockIsAppendOnly(
                f"{key} is already {merged[key][:16]}… and would become {value[:16]}…. The lock is "
                "APPEND-ONLY: a field that can be rewritten is a field that will be rewritten on "
                "the day the result is unwelcome."
            )
        merged[key] = value

    # THE ORDERING RULE (NC-M34). `draw_sha256` may not arrive while any hash that fixes the pool
    # is still absent. Read off APPENDABLE rather than hard-coded, so the tuple is the single
    # statement of the order.
    draw_index = APPENDABLE.index("draw_sha256")
    if "draw_sha256" in merged:
        unfixed = [f for f in APPENDABLE[:draw_index] if f not in merged]
        if unfixed:
            raise PoolNotYetFixed(
                f"draw_sha256 was appended while {unfixed} are still absent. A draw over a pool "
                "that can still be re-curated is a draw over a curation: the exclusion set and "
                "the extractor configurations are OURS, and if they can move after the draw then "
                "`k of 20` measures our reading of the instrument and reports it as a property of "
                "the model. Those two results are indistinguishable in the published number."
            )

    for key in current.fields:
        if key not in merged:
            raise LockIsAppendOnly(f"{key} would be removed; the lock is append-only")

    out = Lock(fields=merged)
    lock_path.write_bytes(out.as_json() + b"\n")
    return out


def _read(lock_path: Path) -> Lock:
    if not lock_path.is_file():
        raise PreregistrationMissing(
            f"{lock_path} does not exist. `propose()` refuses without it, and that refusal is the "
            "experiment's only guarantee that the criterion predates the result."
        )
    raw = json.loads(lock_path.read_text(encoding="utf-8"))
    unknown = sorted(set(raw) - ALL_FIELDS)
    if unknown:
        raise UnknownLockField(f"the lock on disk carries unknown fields {unknown}")
    return Lock(fields=raw)


# --- git ancestry ------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False,
    )


def _introducing_commit(repo: Path, path: Path, *, needle: str) -> str | None:
    """The EARLIEST commit whose version of `path` contains `needle`.

    Walked oldest-first, because the field's *introduction* is what must precede the run — the
    most recent commit that touched the file would let a field be introduced late and then merely
    re-touched early-looking.
    """
    log = _git(repo, "log", "--reverse", "--format=%H", "--", str(path))
    if log.returncode != 0 or not log.stdout.strip():
        return None
    for commit in log.stdout.split():
        show = _git(repo, "show", f"{commit}:{path}")
        if show.returncode == 0 and needle in show.stdout:
            return commit
    return None


def _first_commit_of(repo: Path, path: Path) -> str | None:
    log = _git(repo, "log", "--reverse", "--format=%H", "--", str(path))
    if log.returncode != 0 or not log.stdout.strip():
        return None
    return log.stdout.split()[0]


def is_ancestor(repo: Path, earlier: str, later: str) -> bool:
    return _git(repo, "merge-base", "--is-ancestor", earlier, later).returncode == 0


def ancestry_state(
    repo: Path = Path("."),
    lock_path: Path = LOCK_PATH,
    runlog: Path = RUNLOG_PATH,
) -> str:
    """`VERIFIED` / `UNVERIFIABLE (…)` / `VIOLATED (…)`. **Never `VERIFIED` by default.**

    The three states are kept apart because their remedies differ: a violation is a finding about
    the experiment, and an unverifiable ancestry is a finding about the *environment* — a tarball
    with no `.git`, a shallow clone. Reporting the second as the first is exactly the collapse this
    project is named for.
    """
    if _git(repo, "rev-parse", "--git-dir").returncode != 0:
        return "UNVERIFIABLE (no git history)"
    if not (repo / runlog).is_file():
        return "UNVERIFIABLE (no runlog — no model call has been made)"
    try:
        assert_precedes_first_call(repo, lock_path, runlog)
    except OrderingNotEstablished as exc:
        return f"VIOLATED ({exc.args[0].splitlines()[0]})"
    except PreregistrationMissing:
        return "UNVERIFIABLE (no lock)"
    return "VERIFIED"


def assert_precedes_first_call(
    repo: Path = Path("."),
    lock_path: Path = LOCK_PATH,
    runlog: Path = RUNLOG_PATH,
) -> None:
    """Every lock field's introducing commit is an ancestor of the first runlog commit.

    **And the two pool hashes must additionally precede the draw hash** — the NC-M34 edge, checked
    on the object graph exactly as `h0` is, because an ordering rule that is enforced only inside
    `append()` is enforced only for people who use `append()`.
    """
    current = _read(repo / lock_path)
    first_run = _first_commit_of(repo, runlog)
    if first_run is None:
        raise OrderingNotEstablished(
            f"{runlog} has no commit. There is nothing for the lock to precede — which is the "
            "state before the first API call, and is not a failure."
        )

    for field, value in sorted(current.fields.items()):
        if field in ("committed_at", "published_in"):
            continue
        commit = _introducing_commit(repo, lock_path, needle=value)
        if commit is None:
            raise OrderingNotEstablished(
                f"{field} is in the lock on disk but appears in no commit of {lock_path}. An "
                "uncommitted lock field is a field that was never fixed."
            )
        if not is_ancestor(repo, commit, first_run):
            raise OrderingNotEstablished(
                f"{field} was introduced in {commit[:12]}, which is NOT an ancestor of the first "
                f"runlog commit {first_run[:12]}. The criterion did not precede the run: it could "
                "have been written to fit the result, and nothing in the published number would "
                "show the difference."
            )

    draw_hash = current.get("draw_sha256")
    if draw_hash is not None:
        draw_commit = _introducing_commit(repo, lock_path, needle=draw_hash)
        for field in APPENDABLE[:APPENDABLE.index("draw_sha256")]:
            value = current.get(field)
            if value is None:
                raise OrderingNotEstablished(f"{field} is absent while draw_sha256 is present")
            pool_commit = _introducing_commit(repo, lock_path, needle=value)
            if pool_commit is None or draw_commit is None:
                raise OrderingNotEstablished(f"{field} or draw_sha256 appears in no commit")
            if not is_ancestor(repo, pool_commit, draw_commit):
                raise OrderingNotEstablished(
                    f"{field} ({pool_commit[:12]}) is not an ancestor of draw_sha256 "
                    f"({draw_commit[:12]}). The pool was still movable when the draw was taken."
                )


def lock_summary(lock_path: Path = LOCK_PATH) -> dict[str, Any]:
    """What a DoD line J1 must show: the hash, and **the command that recomputes it**.

    A hash a reviewer can recompute is evidence; a hash pasted into a description is a claim.
    """
    current = _read(lock_path)
    ready, missing = current.has_run_prerequisites()
    return {
        "h0": current.h0,
        "recompute": f"shasum -a 256 {PREREGISTRATION_PATH}",
        "fields_present": sorted(current.fields),
        "fields_missing": list(missing),
        "run_may_proceed": ready,
    }
