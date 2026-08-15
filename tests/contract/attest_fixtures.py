"""A statement fixture the contract tests share, built WITHOUT running the pipeline.

The contract tests are about the SHAPE of a statement, not about any particular filing, and
building one from a live run would make them slow and would couple a schema assertion to a
workbook. `tests/e2e/` runs the real thing.

Every value below is a plausible instance of its type, and every number is an integer — the
`no_json_float` test reads this fixture, so a float here would be a float in the payload.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from cdfc.attest.statement import Statement, Subject  # noqa: E402

TIME_VERIFIED = "2026-08-14T00:00:00Z"

MANIFEST: dict[str, Any] = {
    "template_sha256": "7d9a1960085785eefbe166fb5e04e94689780c490235fe55d8f3e8b620ceea39",
    "filing_sha256": "aeedbfe18c8030612e6d1b3a4f8e5c9d0a1b2c3d4e5f60718293a4b5c6d7e8f9",
    "registry_root": "root-p5-pre-gate-fixture",
    "register_snapshot_sha256": None,
    "code_git_sha": "0" * 40,
    "evaluator_version": "cdfc.calc P3 + celpy 0.5.0",
    "fault_model_version": "v3",
    "tool_versions": {
        "python": "3.12", "lxml": "5.2.1", "openpyxl": "3.1.5",
        "celpy": "0.5.0", "z3": "4.13.0",
    },
    "probe_seed": 0,
    "timeVerified": TIME_VERIFIED,
}

LIVENESS: dict[str, Any] = {
    "rowsTotal": 34, "canariesRun": 33, "canariesPassed": 33,
    "antiCanariesRun": 33, "antiCanariesPassed": 33,
    "canariesInapplicable": 0, "canariesIndeterminate": 0, "canariesUnresolved": 0,
    "antiCanariesFired": 0, "antiCanariesNotPass": 0,
    "selfTestSilent": True, "maxWitnesses": 3,
}

RESIDUE: dict[str, Any] = {
    "residue": 517, "wrongTotal": 517, "innocuousTotal": 44, "unadjudicableTotal": 21,
    "registryRoot": "6e340b9cffb37a98" + "0" * 48,
    "nAdmittedPredicates": 0, "nAdmittedRelations": 0,
    "faultModelVersion": "v3",
    "adjudicationRecordSha256": "e" * 64,
    "rejectorSet": "ADMITTED",
    "label": "CEILING — computed against an EMPTY admitted set.",
}


def sample_statement(*, invalid: bool = False) -> Statement:
    """A VALID statement, or an INVALID one carrying `null` in both fields (F24)."""
    return Statement(
        subjects=(
            Subject(name="filing.xlsx", sha256=MANIFEST["filing_sha256"]),
            Subject(name="template.xlsx", sha256=MANIFEST["template_sha256"]),
        ),
        scope={
            "fieldSurface": 3747, "inScope": 3747, "outOfScope": 0,
            "outOfScopeRetained": 0, "runId": "3f9a2c1d5e7b8a04",
        },
        run_state="INVALID" if invalid else "VALID",
        invalid_causes=("invalid.canary_silent",) if invalid else (),
        settled_fraction=None if invalid else {
            "settled": 1898, "inScope": 3747, "cellsTotal": 3747,
            "denominatorWarning": "the denominator is the field surface computed from styles.xml, "
                                  "not the set of cells any predicate happens to bind",
            "admissibilityCaveat": "",
        },
        verdict=None if invalid else {"state": "SETTLEMENT_DECLARED"},
        liveness_proof=LIVENESS,
        residue=RESIDUE,
        counter_evidence=(),
        false_failure_rate=None,
        corpus_provenance="SELF-AUTHORED",
        assessor={"id": "cdfc", "thirdParty": False},
        manifest=MANIFEST,
        time_verified=TIME_VERIFIED,
        open_items=(
            {
                "id": "C21",
                "what": "legal review of the signing arrangement has not returned; the demo signs "
                        "a synthetic filing with a published demo key",
                "openedAt": "2026-08-11",
                "ageDays": 3,
            },
        ),
    )
