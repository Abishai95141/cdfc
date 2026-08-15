"""P11 — the reference attestation: one assembler, so nothing builds a statement twice.

`cdfc attest <filing>` calls this. It takes a run that has already been through the canary loop —
**there is nothing to sign until the canaries run** — and produces the DSSE envelope and the
statement's canonical bytes.

**Every value in the manifest is an INPUT.** `timeVerified` and `probe_seed` are arguments, not
values read at run time; `code_git_sha` is read from the repository, not from a clock; `expires` is
derived. Nothing in this module reads a clock, and `test_det__no_clock_in_verdict` asserts it over
the import closure.

## The demo signs a synthetic filing with a published key, and says so on its face

`plan/05` P11-B1: *"Until the open legal review returns (spec §III.7 C21), the demo signs a
synthetic filing with a demo key and the report says so on its face"* — rendered **with its age**,
not as silence. `OPEN_ITEMS` below carries it, `openItems` is a required field of the schema, and
its `ageDays` is computed from `timeVerified` and the date the item was opened, so the number grows
on its own without anybody remembering to update it.
"""

from __future__ import annotations

import datetime as _dt
import json
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from cdfc.attest import dsse
from cdfc.attest.statement import Statement, from_run
from cdfc.canon import canonical_json
from cdfc.measure.p5_run import FME
from cdfc.probes.driver import DEFAULT_SEED

REPO: Final[Path] = Path(__file__).resolve().parents[3]

# The open items the report carries on its face, with the date each was opened. `ageDays` is
# DERIVED from `timeVerified`, so it grows without anybody maintaining it — an open item whose age
# has to be updated by hand is an open item that reads as three days old for ever.
OPEN_ITEMS: Final[tuple[Mapping[str, str], ...]] = (
    {
        "id": "C21",
        "what": (
            "The legal review of the signing arrangement has not returned. The demo signs a "
            "SYNTHETIC filing with a PUBLISHED demo key, and the Ed25519 implementation is the "
            "RFC 8032 reference — not constant-time, and refused for any key but the demo key."
        ),
        "openedAt": "2026-08-11",
    },
    {
        "id": "G-CORPUS",
        "what": (
            "No independently-authored clean corpus exists, so falseFailureRate is null and "
            "corpusProvenance is SELF-AUTHORED. A rate of zero here would be a claim; null is the "
            "absence of one."
        ),
        "openedAt": "2026-08-13",
    },
    {
        "id": "P10-kappa",
        "what": (
            "There is no second adjudicator, so Cohen's kappa on the residue's adjudication record "
            "is UNMEASURED. It is the input that does not exist, not the instrument."
        ),
        "openedAt": "2026-08-14",
    },
)


def code_git_sha() -> str:
    """The commit the run was produced by. **Read from git, never from a clock.**"""
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=False
    )
    sha = out.stdout.strip()
    if len(sha) != 40:
        raise RuntimeError(
            "code_git_sha could not be read. It pins the code the attestation was produced by, and "
            "an attestation that cannot say which code produced it cannot be re-derived."
        )
    return sha


def tool_versions() -> dict[str, str]:
    """The five pinned tools. **`libreoffice` is deliberately absent: it is not on the verdict
    path**, and pinning it would imply it was."""
    import sys
    from importlib.metadata import PackageNotFoundError, version

    def _v(name: str) -> str:
        try:
            return version(name)
        except PackageNotFoundError:
            return "absent"

    return {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "lxml": _v("lxml"),
        "openpyxl": _v("openpyxl"),
        "celpy": _v("cel-python"),
        "z3": _v("z3-solver"),
    }


def _age_days(opened_at: str, time_verified: str) -> int:
    a = _dt.date.fromisoformat(opened_at)
    b = _dt.datetime.fromisoformat(time_verified.replace("Z", "+00:00")).date()
    return max(0, (b - a).days)


def open_items(time_verified: str) -> tuple[dict[str, Any], ...]:
    return tuple(
        {**dict(item), "ageDays": _age_days(item["openedAt"], time_verified)}
        for item in OPEN_ITEMS
    )


def manifest_for(
    result: Any, *, template_sha256: str, time_verified: str, probe_seed: int = DEFAULT_SEED
) -> dict[str, Any]:
    """The eight pins plus the two run-level inputs. `verify` re-runs the pipeline against these."""
    return {
        "template_sha256": template_sha256,
        "filing_sha256": result.filing_sha256,
        "registry_root": getattr(getattr(result, "selection", None), "registry_root", "")
        or "root-p5-pre-gate-fixture",
        # NC-X01: nothing in `src/` reaches the network, and no register snapshot is bound to a
        # verdict in this build. `null` is `we make no claim`, which is the true statement.
        "register_snapshot_sha256": None,
        "code_git_sha": code_git_sha(),
        "evaluator_version": "cdfc.calc P3 + celpy 0.5.0",
        "fault_model_version": "v3",
        "tool_versions": tool_versions(),
        "probe_seed": probe_seed,
        "timeVerified": time_verified,
    }


def statement_for(
    result: Any,
    *,
    filing: Path,
    template: Path = FME,
    time_verified: str,
    residue: Mapping[str, Any] | None = None,
    counter_evidence: Sequence[Mapping[str, Any]] = (),
) -> Statement:
    import hashlib

    template_sha = hashlib.sha256(template.read_bytes()).hexdigest()
    return from_run(
        result,
        template_sha256=template_sha,
        template_name=template.name,
        filing_name=filing.name,
        manifest=manifest_for(result, template_sha256=template_sha, time_verified=time_verified),
        time_verified=time_verified,
        residue=residue,
        counter_evidence=counter_evidence,
        open_items=open_items(time_verified),
    )


def attest(statement: Statement) -> tuple[bytes, dict[str, Any]]:
    """`(canonical payload, DSSE envelope)`. The vendor signs nothing; the filer's key signs."""
    payload = statement.canonical()
    return payload, dsse.sign(payload).as_obj()


def write(statement: Statement, out_dir: Path) -> Path:
    """`runs/<run_id>/attestation.json`, beside `run.jsonl` and `manifest.json`.

    Written with `canonical_json` rather than `json.dump`, because the file on disk IS the artifact
    `verify` compares byte for byte — a pretty-printer between the payload and the file would make
    the comparison about the printer.
    """
    payload, envelope = attest(statement)
    target = out_dir / statement.as_predicate()["scope"]["runId"]
    target.mkdir(parents=True, exist_ok=True)
    path = target / "attestation.json"
    path.write_bytes(canonical_json(envelope) + b"\n")
    (target / "statement.json").write_bytes(payload + b"\n")
    return path


# **`validate()` IS NOT HERE, and `test_diff__jsonschema_is_not_in_the_runtime_closure` is why.**
# `jsonschema` is a TEST dependency: putting it in the runtime tree — even behind a lazy import —
# would make the deterministic core depend on a validator, and the differential test that walks the
# runtime closure caught it immediately. Schema validation lives in `tools/attest_validate.py` and
# in the contract tests, which is where a check on the SHAPE of an artifact belongs.
#
# What stays here is the refusal that does not need a validator: `Statement.__post_init__` already
# refuses a statement the schema would reject on the one rule that matters most (F24's PRESENT-and-
# null), so the builder and the schema cannot disagree about it.
