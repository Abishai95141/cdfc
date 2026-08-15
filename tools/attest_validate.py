#!/usr/bin/env python
"""Validate a statement against `attestation.schema.json`.

**This lives in `tools/` and not in `src/cdfc/`**, and `test_diff__jsonschema_is_not_in_the_runtime_closure`
is why: `jsonschema` is a TEST dependency, and putting a validator in the runtime tree would make
the deterministic core depend on one. A check on the SHAPE of an artifact belongs beside the tests,
not inside the thing being shaped.

Raises — a statement that does not validate is not written, because a malformed attestation is
worse than none: it looks like evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

SCHEMA = REPO / "src" / "cdfc" / "attest" / "schema" / "attestation.schema.json"


def schema() -> dict[str, Any]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validate(statement: Any) -> None:
    """`statement` is a `cdfc.attest.statement.Statement` or an already-built object."""
    import jsonschema

    obj = statement.as_obj() if hasattr(statement, "as_obj") else statement
    jsonschema.validate(instance=obj, schema=schema())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: attest_validate.py <statement.json>", file=sys.stderr)
        return 2
    validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print(f"{sys.argv[1]}: validates against {SCHEMA.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
