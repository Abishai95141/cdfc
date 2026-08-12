#!/usr/bin/env python
"""Regenerate `src/cdfc/predicates/schema/predicate.schema.json` from the record.

The committed file is compared against this output by
`tests/contract/test_contract__predicate_schema.py`, so changing the dataclass without running
this fails the build rather than leaving two declarations of one shape.

    make predicate-schema        # or: python tools/gen_predicate_schema.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from cdfc.predicates.schema_build import build_schema  # noqa: E402

OUT = REPO / "src" / "cdfc" / "predicates" / "schema" / "predicate.schema.json"


def rendered() -> str:
    return json.dumps(build_schema(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = rendered()
    changed = not OUT.is_file() or OUT.read_text(encoding="utf-8") != text
    OUT.write_text(text, encoding="utf-8")
    print(f"{'wrote' if changed else 'unchanged'} {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
