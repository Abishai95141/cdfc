"""P12-B3 — **the ONLY module under `src/cdfc/` that may import a model client.**

Everything about this file is a boundary. It exists so that the rule *"no model on the verdict
path"* is a statement about **one import site** rather than about a convention people remember.

## The guard bans the PACKAGE, not the vendor

`tests/negative/test_nc_model.py::test_nc__M13a_qualify_import_closure_has_no_model_client`
asserts that no verdict root's AST import closure reaches `cdfc.experiment.client`. It does not
enumerate `anthropic`, `openai`, `httpx`, … — enumerating vendors means the guard is one new SDK
behind forever. Its positive control, `test_nc__M13c_run_module_may_import_the_client`, asserts
that `cdfc.experiment.run` **can**: a guard that bans the wrong thing is not a guard, and a
reject-everything import rule would pass every negative control while forbidding the build.

## The import is deferred, and that is not laziness

`anthropic` is **not in `requirements.lock`** and is not installed here. A module-level import
would make `cdfc.experiment` unimportable, which would take `power`, `draw`, `prereg`, `decide`
and `funnel` down with it — every model-free part of the phase — and the negative controls that
prove the package is offline would fail to collect. So the client is constructed inside
`build_client()`, and the absence of the SDK is reported as the named, catchable condition it is.

## `max_retries = 0`, and there is no `attempt` parameter anywhere

**Retry is impossible here, not merely banned.** A silent retry understates the discard rate, and
the discard pile is stage 0 of the funnel — so a retried batch produces a funnel that starts from
a curated set while printing the planned count. `NC-M10` is the control and
`test_propose__has_no_attempt_parameter` introspects the signature, because a constant somebody
can pass a different value to is a default, not a rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

# The model the pre-registration names. A literal, hashed into `PREREGISTRATION.md`, so that a
# run under a different model is a diff rather than a footnote.
MODEL_ID: Final[str] = "claude-opus-5"

# **There is no retry.** Not a default that can be overridden — the client is constructed with it
# and no call site takes an attempt count.
MAX_RETRIES: Final[int] = 0

# Generation is offline and batched. Batch is not an optimisation here: it is what makes ~600 calls
# a single reviewable artifact with one id in the runlog.
USE_BATCH_API: Final[bool] = True

# Temperature is pre-registered. It is a property of the experiment, not a knob.
TEMPERATURE: Final[float] = 1.0


class ModelClientUnavailable(RuntimeError):
    """No model SDK, or no credential. **Named, so the run's refusal is legible.**

    This is not an error condition to be worked around. `experiments/E6/DECISION.md` records the
    run as not taken and says why; a run that could not be made and a run that produced nothing
    are different facts, and this exception is what keeps them apart.
    """


@dataclass(frozen=True, slots=True)
class ClientConfig:
    """Everything about the call that is pre-registered, in one hashable object."""

    model_id: str = MODEL_ID
    max_retries: int = MAX_RETRIES
    batch: bool = USE_BATCH_API
    temperature: float = TEMPERATURE

    def __post_init__(self) -> None:
        if self.max_retries != 0:
            raise ValueError(
                f"max_retries = {self.max_retries}. Retry is impossible here, not configurable: a "
                "silent re-prompt understates the discard rate, and the discard pile is the "
                "funnel's stage 0. NC-M10."
            )


def build_client(config: ClientConfig | None = None) -> Any:
    """Construct the vendor client. **Raises `ModelClientUnavailable` rather than degrading.**

    There is no offline stub and no cached-response mode. A driver that fell back to a stub would
    produce a runlog indistinguishable from a real one, and the runlog is what the git-ancestry
    check anchors on.
    """
    cfg = config or ClientConfig()
    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise ModelClientUnavailable(
            "no model SDK is installed. `anthropic` is deliberately absent from "
            "requirements.lock: nothing in the verdict path may import it, and P12's run is a "
            "human-initiated, money-spending step rather than something a test can trigger. "
            "Installing it is part of taking the run, not part of building the harness."
        ) from exc
    return anthropic.Anthropic(max_retries=cfg.max_retries)
