"""P12-B3 — the Batch driver. **OFFLINE. Never in a request path. And it refuses more than it runs.**

`propose()` has four refusals before it can reach a network, and each one closes a way the
experiment could produce a number that looks the same and means something else:

| Refusal | When | What it stops |
|---|---|---|
| `PreregistrationMissing` | no `preregistration.lock.json` | a run whose criterion was never fixed |
| `PreregistrationMismatch` | `h0` ≠ the file on disk | a criterion edited between locking and running |
| `ArtefactHashesMissing` | draw / strata / baselines hashes absent | a run over a pool, a stratification or a bar that can still move |
| `ModelClientUnavailable` | no SDK, no credential | a run silently replaced by a stub |

**On today's tree the third fires**, and it fires for a structural reason rather than a
configuration one: there is no statutory instrument in this repository
(`docs/decisions/D-P7-01-no-statutory-instrument.md`), so there is no pool, so there is no draw,
so `draw_sha256` is not in the lock and `prereg.append()` would refuse it anyway under
`PoolNotYetFixed`. The refusal chain terminates exactly where the missing artifact is.

## NEVER RETRIES

There is no `attempt` parameter and the client is built with `max_retries = 0`. A malformed
candidate is a **discard row** — the discard pile is data, it is stage 0 of the funnel, and a
silent re-prompt would understate it while the funnel printed the planned count.

## `model_identity_reported` is recorded, and it is `null` rather than the alias when absent

Risk R19 is realised, not hypothetical: a failure cell moved from 96.6% to 100% on the same prompt
and harness **under the same alias, with no version bump**. So the driver records what the API
echoed back, separately from what was requested. Writing the requested alias into that field when
the API says nothing would manufacture agreement — the field would always match, and the check
that alias drift is visible would be a check on our own defaulting. `NC-M12`.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from cdfc.experiment.client import MODEL_ID, ClientConfig
from cdfc.experiment.draw import Draw
from cdfc.experiment.marginal import CANDIDATES_PER_OBLIGATION_PER_REGIME
from cdfc.experiment.parse import DISCARD_REASONS
from cdfc.experiment.prereg import APPENDABLE, Lock

Regime = Literal["correctness", "completeness"]

REGIMES: Final[tuple[Regime, ...]] = ("correctness", "completeness")
PROMPTS_DIR: Final[Path] = Path(__file__).resolve().parent / "prompts"
CANDIDATES_DIR: Final[Path] = Path("experiments/E6/candidates")
RUNLOG: Final[Path] = Path("experiments/E6/runlog.jsonl")


class ArtefactHashesMissing(RuntimeError):
    """The lock does not yet carry every hash the run requires.

    **The run does not proceed on a partial lock.** Each missing hash is an artifact that could
    still change after the model had been asked — and a pool, a stratification or a baseline that
    can move after the candidates are seen turns `k of 20` into a measurement of the thing that
    moved.
    """


@dataclass(frozen=True, slots=True)
class CandidateRecord:
    """One call. **Written BEFORE and after**, so a crash mid-batch leaves a row, not a gap."""

    candidate_sha256: str
    obligation_ordinal: int
    regime: Regime
    draw_index: int                       # 0..k-1 within the regime
    model_id: str
    model_identity_reported: str | None   # what the API echoed back — R19, alias drift
    prompt_sha256: str
    api_batch_id: str
    requested_at: str
    envelope: Any | None                  # None == malformed
    discard_reason: str | None

    def __post_init__(self) -> None:
        if (self.envelope is None) != (self.discard_reason is not None):
            raise ValueError(
                "a record carries an envelope XOR a discard reason. A malformed candidate with no "
                "reason is a call that left no row, and an envelope with a discard reason is a "
                "candidate that is both admitted and rejected."
            )
        if self.discard_reason is not None and self.discard_reason not in DISCARD_REASONS:
            raise ValueError(f"{self.discard_reason!r} is not one of {DISCARD_REASONS}")
        if self.model_identity_reported == "":
            raise ValueError(
                "model_identity_reported is null when the API supplies nothing — never the empty "
                "string and never the requested alias. An echoed identity that we filled in "
                "ourselves would always match, and NC-M12 would be checking our own defaulting."
            )

    def as_obj(self) -> dict[str, Any]:
        return {
            "candidate_sha256": self.candidate_sha256,
            "obligation_ordinal": self.obligation_ordinal,
            "regime": self.regime, "draw_index": self.draw_index,
            "model_id": self.model_id,
            "model_identity_reported": self.model_identity_reported,
            "prompt_sha256": self.prompt_sha256, "api_batch_id": self.api_batch_id,
            "requested_at": self.requested_at,
            "discard_reason": self.discard_reason,
        }


def prompt_sha256(regime: Regime) -> str:
    """The prompt's hash. **The prompt is a file, verbatim and hashed**, never a f-string.

    A prompt assembled at call time from fragments is a prompt nobody can quote in the
    pre-registration, and `PREREGISTRATION.md` carries both regimes verbatim with their hashes.
    """
    from cdfc.canon import sha256_hex

    path = PROMPTS_DIR / f"{regime}.md"
    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist; the prompt is part of the criterion")
    return sha256_hex(path.read_bytes())


def assert_ready(lock: Lock) -> None:
    """Every refusal that precedes the first call, in order. **Raises or returns None.**"""
    ready, missing = lock.has_run_prerequisites()
    if not ready:
        raise ArtefactHashesMissing(
            f"the lock is missing {list(missing)} of the required {list(APPENDABLE)}. Each is an "
            "artifact that could still change after the model had been asked. The run does not "
            "proceed on a partial lock: a baseline computed after seeing the candidates is not a "
            "baseline, and a pool re-curated after the draw makes `k of 20` a measurement of the "
            "curation."
        )


def planned_calls(draw: Draw, *, k: int = CANDIDATES_PER_OBLIGATION_PER_REGIME,
                  regimes: Sequence[Regime] = REGIMES) -> int:
    """`|Stratum A| × |regimes| × k`, plus the generated Stratum-B cap. **The funnel's stage 0.**"""
    obligations = len(draw.stratum_a) + len(draw.stratum_b_generated)
    return obligations * len(regimes) * k


def propose(
    draw: Draw,
    *,
    lock: Lock,
    k: int = CANDIDATES_PER_OBLIGATION_PER_REGIME,
    regimes: Sequence[Regime] = REGIMES,
    model_id: str = MODEL_ID,
    config: ClientConfig | None = None,
    runlog: Path = RUNLOG,
) -> tuple[CandidateRecord, ...]:
    """Ask the model. **Every refusal above fires before anything reaches a network.**

    There is no `attempt` parameter, and there will not be one: `test_propose__has_no_attempt_parameter`
    introspects this signature. `max_retries == 0` on the constructed client is asserted by the
    same test, because the two together are what make retry *impossible* rather than *discouraged*.
    """
    from cdfc.experiment.client import build_client

    assert_ready(lock)
    if lock["draw_sha256"] != draw.sha256:
        raise ArtefactHashesMissing(
            f"the lock pins draw {lock['draw_sha256'][:16]}… and the draw handed in hashes to "
            f"{draw.sha256[:16]}…. Running against a draw the lock does not name is running "
            "against a pool nobody fixed."
        )
    for regime in regimes:
        prompt_sha256(regime)              # raises if a prompt is missing, before any call

    client = build_client(config)          # raises ModelClientUnavailable when there is no SDK
    _ = client, k, model_id, runlog
    raise NotImplementedError(
        "the batch submission is the money-spending, human-initiated half of P12-B3 and is not "
        "reachable in this build: every refusal above fires first on this tree. See "
        "docs/measurements/P12-entry.md for which artifact is missing and why, and "
        "experiments/E6/DECISION.md for the published status of the run."
    )


def read_runlog(path: Path = RUNLOG) -> tuple[dict[str, Any], ...]:
    """The runlog, as rows. **Its first commit is what the git-ancestry check anchors on.**"""
    if not path.is_file():
        return ()
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


def alias_splits(records: Sequence[CandidateRecord]) -> dict[str, int]:
    """`{reported identity: count}`, with `null` counted under its own key. **NC-M12.**

    An alias that resolved to two different underlying models mid-batch produces two keys here, and
    a batch whose identities are not all equal is reported as split rather than pooled — a pooled
    `k of 20` across two models is a number about neither.
    """
    out: dict[str, int] = {}
    for r in records:
        key = r.model_identity_reported or "null (the API reported no identity)"
        out[key] = out.get(key, 0) + 1
    return out
