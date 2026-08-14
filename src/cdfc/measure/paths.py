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
#
# **THIS MODULE CONTAINED THE DEFECT IT EXISTS TO PREVENT.** `P1_READER_AGREEMENT` spelled the P1
# file `p1-reader-agreement.json` while the file the build actually produces — from
# `tools/measure/agreement_matrix.py` — is `p1-agreement.json`. Three further constants named
# files no phase ever wrote, and seven of the nine were imported by nothing, so nothing noticed.
# A constant that names a file which does not exist is worse than a re-typed filename: it reads
# as a canonical answer.
#
# Every path below is now asserted to EXIST by `test_contract__every_measurement_path_resolves`,
# and a phase that has not produced its file declares that here rather than pointing at nothing.
P0_GATE_LIVENESS: Path = MEASUREMENTS_DIR / "p0-gate-liveness.json"
P1_READER_AGREEMENT: Path = MEASUREMENTS_DIR / "p1-agreement.json"
P2_FIELD_SURFACE: Path = MEASUREMENTS_DIR / "p2-field-surface.json"
P3_EVALUATOR: Path = MEASUREMENTS_DIR / "p3-evaluator.json"
P4_HARVEST_DISTRIBUTION: Path = MEASUREMENTS_DIR / "p4-harvest-distribution.json"
P5_VERDICT_CLOSURE: Path = MEASUREMENTS_DIR / "p5-verdict-closure.json"
P9_CEILING: Path = MEASUREMENTS_DIR / "p9-template-diff-ceiling.json"
P9_RELATION_ATTRITION: Path = MEASUREMENTS_DIR / "p9-relation-attrition.json"
P9_RELATION_RUNNABILITY: Path = MEASUREMENTS_DIR / "p9-relation-runnability.json"

# P6, P7 and P8 publish their measurements as MARKDOWN plus a live report under `reports/`, not as
# a per-phase JSON. `P6_FAULT_CAMPAIGN`, `P7_ATTRITION_FUNNEL` and `P8_FFR` named JSON files that
# no phase ever wrote; they are replaced by the paths that exist, so a reader following a constant
# arrives at a file.
P6_CAMPAIGN_DIR: Path = REPORTS_DIR / "campaigns"
P7_ATTRITION: Path = MEASUREMENTS_DIR / "P7-attrition.md"
P8_FFR: Path = MEASUREMENTS_DIR / "P8-ffr.md"

# --- the artifact corpus ---------------------------------------------------------
# `INGEST_MANIFEST` pointed at `fixtures/MANIFEST.json`, which has never existed: each fixture
# FAMILY carries its own, because they are pinned for different reasons and by different tools.
# Naming the three is the honest form; naming a fourth that nobody writes is not.
PRESCRIBED_MANIFEST: Path = FIXTURES_DIR / "prescribed" / "MANIFEST.json"
SYNTHETIC_MANIFEST: Path = FIXTURES_DIR / "synthetic" / "MANIFEST.json"
ADVERSARIAL_MANIFEST: Path = FIXTURES_DIR / "adversarial" / "MANIFEST.json"
CORPUS_MANIFEST: Path = FIXTURES_DIR / "corpus_manifest.json"
