#!/usr/bin/env python
"""Re-render `docs/measurements/P6-fault-model-v3.md` from a campaign's stored manifest.

The campaign is 773 mutants and ~25 minutes; the document is prose over its numbers. Re-rendering
reads the manifest the campaign wrote, so the document can never quote a number no campaign
produced.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools" / "measure"))

from cdfc.qualify.campaign import Campaign, ClassTally  # noqa: E402

from p6_campaign import DOC, render_doc  # noqa: E402


def main() -> int:
    target = sorted((REPO / "reports" / "campaigns").glob("*/manifest.json"))
    if not target:
        print("no campaign manifest; run `make campaign` first", file=sys.stderr)
        return 1
    m = json.loads(target[0].read_text(encoding="utf-8"))
    campaign = Campaign(
        campaign_id=m["campaign_id"],
        by_fault_class={k: ClassTally(**v) for k, v in m["by_fault_class"].items()},
        fault_model_version=m["fault_model_version"],
        fault_model_digest=m["fault_model_digest"],
        harness_version=m["harness_version"],
        site_set_digest=m["site_set_digest"],
        evaluator_version=m["evaluator_version"],
        base_sha256=m["base_sha256"],
        sampling_rule=m["sampling_rule"],
    )
    DOC.write_text(render_doc(campaign, target[0].parent, 4252), encoding="utf-8")
    print(f"re-rendered {DOC.relative_to(REPO)} from {target[0].relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
