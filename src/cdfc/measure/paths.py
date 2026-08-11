"""Measurement-file path constants.

Other modules import these instead of re-typing a filename. A measurement written to a
path one module spells differently from another is a measurement nobody reads — and this
project's measurement ledger is its own coverage declaration applied to itself.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[3]

MEASUREMENTS_DIR: Path = REPO_ROOT / "docs" / "measurements"
REPORTS_DIR: Path = REPO_ROOT / "reports"
PERF_DIR: Path = REPORTS_DIR / "perf"  # timings live HERE, outside every hashed payload (R3)
FIXTURES_DIR: Path = REPO_ROOT / "fixtures"

# --- per-phase measurement files -------------------------------------------------
P0_GATE_LIVENESS: Path = MEASUREMENTS_DIR / "p0-gate-liveness.json"
P1_READER_AGREEMENT: Path = MEASUREMENTS_DIR / "p1-reader-agreement.json"
P2_FIELD_SURFACE: Path = MEASUREMENTS_DIR / "p2-field-surface.json"
P3_EVALUATOR: Path = MEASUREMENTS_DIR / "p3-evaluator.json"
P4_HARVEST_DISTRIBUTION: Path = MEASUREMENTS_DIR / "p4-harvest-distribution.json"
P5_VERDICT_CLOSURE: Path = MEASUREMENTS_DIR / "p5-verdict-closure.json"
P6_FAULT_CAMPAIGN: Path = MEASUREMENTS_DIR / "p6-fault-campaign.json"
P7_ATTRITION_FUNNEL: Path = MEASUREMENTS_DIR / "p7-attrition-funnel.json"
P8_FFR: Path = MEASUREMENTS_DIR / "p8-ffr.json"

# --- the artifact corpus ---------------------------------------------------------
INGEST_MANIFEST: Path = FIXTURES_DIR / "MANIFEST.json"
